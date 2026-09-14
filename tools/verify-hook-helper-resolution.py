#!/usr/bin/env python3
"""Assert every helper a hook needs RESOLVES in the real installed layout.

Why this gate exists
--------------------
The repo layout and the installed layout are different shapes, and the hooks
were written against the repo one:

    repo      plugins/proofpunk/hooks/../skills/...      -> exists
    installed ~/.proofpunk/hooks/../skills/...           -> DOES NOT EXIST
              (proofpunk-install.sh puts hooks in ~/.proofpunk/hooks but
               skills in the platform dir, e.g. ~/.claude/skills)

stop-guard.sh's intent branch is FAIL-CLOSED. So on every `--hooks` install the
helper-missing branch fired and the guard blocked forever, while the helper sat
one directory away. A session hit exactly this in the field and concluded the
tool "does not exist in any installed version".

A static grep cannot catch this: the path is assembled at runtime from a
candidate list. The only honest check is to install into a throwaway HOME and
drive the hook, which is what this does.

Exit 0 = every hook resolved its helper in a real install. Exit 1 = a hook
would wedge a real user.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=proofpunk-install.sh,stop-guard.sh keywords=subprocess,tempfile
# SUBJECT is the INSTALLED layout: this harness really runs the installer with
#   --hooks into a throwaway HOME, then drives the installed stop-guard.sh.
# CAN OBSERVE: whether a hook installed to ~/.proofpunk/hooks can actually
#   resolve the helper it needs. The driven transcript satisfies the claim,
#   proof and scout branches first so the fail-closed intent branch is genuinely
#   reached, and a vacuity check fails the gate if an earlier branch
#   short-circuited instead.
# CANNOT OBSERVE: whether the HOST wires the hook to the Stop event at runtime,
#   whether a live model-driven session emits a claim at all, or whether the
#   omp/opencode/agents targets resolve — only claude-code is installed here.
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALLER = os.path.join(ROOT, "tools", "proofpunk-install.sh")

# The block text a hook emits when it cannot find its helper. Matching on this
# is deliberate: it is the user-visible symptom, not an internal detail.
MISSING_MARKER = "helper is missing"


def drive_stop_hook(home: str, hook: str, evidence: str) -> tuple[str, str]:
    """Drive a real Stop event that reaches the intent branch.

    The transcript must satisfy the claim, proof AND scout gates first --
    otherwise an earlier branch short-circuits and the intent branch is never
    exercised, which would make this gate vacuous.
    """
    transcript = os.path.join(home, "t.jsonl")
    with open(transcript, "w", encoding="utf-8") as fh:
        for msg in (
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "text", "text": "fix the hook and prove it"}]}},
            {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "text", "text":
                 "Scout context summary: mapped hooks/stop-guard.sh and its "
                 "touchpoints.\nVerified. Evidence: " + evidence +
                 "\nComplete and verified."}]}},
        ):
            fh.write(json.dumps(msg) + "\n")

    payload = json.dumps({
        "session_id": "gate-" + uuid.uuid4().hex[:8],
        "cwd": ROOT,
        "transcript_path": transcript,
        "hook_event_name": "Stop",
    })
    proc = subprocess.run(
        ["bash", hook], input=payload, capture_output=True, text=True,
        env=dict(os.environ, HOME=home),
    )
    lines = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith("{")]
    obj = json.loads(lines[-1]) if lines else {}
    return obj.get("decision", "(allow)"), obj.get("reason", "")


def main() -> int:
    evidence = os.path.join(ROOT, "e2e-evidence", "run-tooling-surface", "VERDICT.md")
    if not os.path.isfile(evidence):
        print("SKIP: no evidence artifact to cite; cannot reach the intent branch")
        return 0

    # Two layouts, because they fail for different reasons: the default one
    # (skills in the platform dir) and a custom --dir, which no fixed candidate
    # list can guess and which only the installer-recorded path can resolve.
    failures = 0
    for label, skills_dir in (
        ("default --dir (platform skills dir)", None),
        ("custom --dir (unguessable path)", "somewhere/else/skills"),
    ):
        home = tempfile.mkdtemp(prefix="pp-helper-gate-")
        try:
            target_dir = (os.path.join(home, skills_dir) if skills_dir
                          else os.path.join(home, ".claude", "skills"))
            if run_case(home, target_dir, evidence, label) != 0:
                failures += 1
        finally:
            shutil.rmtree(home, ignore_errors=True)
    return 1 if failures else 0


def run_case(home: str, target_dir: str, evidence: str, label: str) -> int:
    print("-- %s" % label)
    inst = subprocess.run(
        ["bash", INSTALLER, "--source-dir", ROOT, "--target", "claude-code",
         "--dir", target_dir, "--hooks"],
        cwd=ROOT, capture_output=True, text=True,
        env=dict(os.environ, HOME=home),
    )
    if inst.returncode != 0:
        print("FAIL: install into throwaway HOME failed")
        print((inst.stderr or inst.stdout)[-600:])
        return 1

    hook = os.path.join(home, ".proofpunk", "hooks", "stop-guard.sh")
    if not os.path.isfile(hook):
        print("FAIL: stop-guard.sh not installed to ~/.proofpunk/hooks")
        return 1

    decision, reason = drive_stop_hook(home, hook, evidence)

    if MISSING_MARKER in reason:
        print("FAIL: the installed hook cannot resolve its helper.")
        print("      Every --hooks user would be wedged by a fail-closed")
        print("      guard. Reason emitted:")
        for line in reason.splitlines():
            print("        " + line)
        return 1

    # Vacuity check: if we did not actually reach the intent branch, this
    # gate proved nothing and must not report success.
    if "intent verdict" not in reason:
        print("FAIL: the intent branch was never reached, so this gate is")
        print("      vacuous. An earlier branch short-circuited:")
        print("        decision=" + decision)
        for line in reason.splitlines()[:3]:
            print("        " + line)
        return 1

    print("OK: installed hook resolved its helper and reached the intent")
    print("    branch (decision=%s)." % decision)
    return 0


if __name__ == "__main__":
    sys.exit(main())
