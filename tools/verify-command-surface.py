#!/usr/bin/env python3
"""Drive all six /proofpunk:* slash commands through sdk_probe.py.

Each command runs twice: plugin loaded, then --no-plugin (control arm).
The control MUST fail or the probe is vacuous.

Proof levels (from evidence/v3-release/00-baseline/command-surface-map.md):
  (a) script-level — backing script invoked directly (not this harness)
  (b) skill-load   — Skill tool by name, bypassing the command doc
  (c) full-chain   — slash typed → registered → mapped skill/script ran →
                     unique marker observed
  playbook-recognition — slash registered + unique command-doc marker,
                     but the command has no backing skill/script (install)
                     or no Activate-skill line (verify)

Only (c) counts toward the 6/6 full-chain gauge. install cannot reach (c):
it is an in-session agent playbook with no backing script, and SDK sessions
in this environment have no Write tool so the playbook cannot execute.

Writes ONE artifact:
  evidence/v3-release/l16-commands/command-surface-proof.json

Exit 0 only if every command's plugin arm passed its probe checks AND every
control arm failed. That is 6/6 at each command's honest maximum level, not
an inflated 6/6 full-chain. The artifact's full_chain field is the gauge
number.

Stdlib only. Never pipes a command whose exit code is recorded.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=sdk_probe.py keywords=--no-plugin,full_chain
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PROBE = os.path.join(HERE, "sdk_probe.py")
OUT_DIR = os.path.join(ROOT, "evidence", "v3-release", "l16-commands")
ARTIFACT = os.path.join(OUT_DIR, "command-surface-proof.json")

# Honest maximum per command. Derived from the command docs, not hoped.
# implement/forge-prompt/rate-prompt/truth-audit: "Activate the `X` skill"
# verify: playbook, no Activate-skill line, no flags, fresh_evidence.py is
#         internal to end-user-testing not exposed on the command
# install: in-session playbook, no skill, no script (distinct from
#          tools/proofpunk-install.sh)
COMMANDS = [
    dict(name="implement", probe="cmd_slash_implement",
         slash="/proofpunk:implement", skill="proofpunk:implement",
         max_level="c",
         note="command doc activates implement; flags --parallel --auto --mine --fast"),
    dict(name="forge-prompt", probe="cmd_slash_forge_prompt",
         slash="/proofpunk:forge-prompt", skill="proofpunk:prompt-forge",
         max_level="c",
         note="command doc activates prompt-forge AUTHOR; flag --depth"),
    dict(name="rate-prompt", probe="cmd_slash_rate_prompt",
         slash="/proofpunk:rate-prompt", skill="proofpunk:prompt-forge",
         max_level="c",
         note="command doc activates prompt-forge RATE; flag --ship-below-threshold"),
    dict(name="truth-audit", probe="cmd_slash_truth_audit",
         slash="/proofpunk:truth-audit", skill="proofpunk:codebase-truth-audit",
         max_level="c",
         note="command doc activates codebase-truth-audit; flags --start/--end"),
    dict(name="verify", probe="cmd_slash_verify",
         slash="/proofpunk:verify", skill=None,
         max_level="playbook-recognition",
         note="playbook: no Activate-skill line, no flags; marker UNVERIFIED"),
    dict(name="install", probe="cmd_slash_install",
         slash="/proofpunk:install", skill=None,
         max_level="playbook-recognition",
         note=("in-session playbook, NO backing skill or script — distinct "
               "from tools/proofpunk-install.sh; SDK has no Write tool so "
               "file-merge execution is unreachable; marker proofpunk:begin")),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_probe(probe, cwd, no_plugin, log_path, rc_path):
    """Run one sdk_probe arm. Capture stdout+stderr to log_path, rc to rc_path.

    Never pipes: Popen with files, wait, write rc from the process itself.
    """
    cmd = [sys.executable, PROBE, probe, "--cwd", cwd]
    if no_plugin:
        cmd.append("--no-plugin")
    with open(log_path, "w", encoding="utf-8") as out:
        proc = subprocess.Popen(
            cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
        rc = proc.wait()
    with open(rc_path, "w", encoding="utf-8") as fh:
        fh.write(str(rc))
    body = open(log_path, encoding="utf-8").read()
    parsed = None
    try:
        parsed = json.loads(body)
    except ValueError:
        # stdout may have a trailing warning; take the last JSON object
        start = body.rfind("{")
        if start >= 0:
            try:
                parsed = json.loads(body[start:])
            except ValueError:
                parsed = None
    return rc, parsed, body


def classify(cmd, plugin, control):
    """Name the proof level from observed checks. Never inflate."""
    p_ok = bool(plugin and plugin.get("pass"))
    c_fail = not bool(control and control.get("pass"))
    p_checks = (plugin or {}).get("checks") or {}
    if not p_ok or not c_fail:
        return dict(
            level="FAIL",
            plugin_pass=p_ok,
            control_failed=c_fail,
            reason="plugin arm did not pass or control arm did not fail",
        )
    slash_ok = bool(p_checks.get("slash_registered"))
    local_ok = bool(p_checks.get("local_plugin_loaded"))
    skill_ok = bool(p_checks.get("tool_succeeded")) if cmd["skill"] else None
    text_ok = bool(p_checks.get("text_matches"))
    if cmd["max_level"] == "c" and slash_ok and local_ok and skill_ok and text_ok:
        return dict(
            level="c",
            plugin_pass=True,
            control_failed=True,
            reason="slash registered, local plugin, Skill succeeded, marker observed",
        )
    if slash_ok and local_ok and text_ok:
        return dict(
            level="playbook-recognition",
            plugin_pass=True,
            control_failed=True,
            reason=("slash registered + local plugin + command-doc marker; "
                    "no backing skill/script executed"),
        )
    return dict(
        level="partial",
        plugin_pass=True,
        control_failed=True,
        reason="probe checks passed but required chain pieces missing",
        checks=p_checks,
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    work = tempfile.mkdtemp(prefix="pp-cmdsurface-")
    rows = []
    n_plugin_pass = 0
    n_control_fail = 0
    n_full_chain = 0
    n_honest_max = 0

    for i, cmd in enumerate(COMMANDS, 1):
        plug_log = os.path.join(OUT_DIR, f"{cmd['probe']}.plugin.log")
        plug_rc_p = os.path.join(OUT_DIR, f"{cmd['probe']}.plugin.rc")
        ctrl_log = os.path.join(OUT_DIR, f"{cmd['probe']}.control.log")
        ctrl_rc_p = os.path.join(OUT_DIR, f"{cmd['probe']}.control.rc")

        print(f"== {cmd['slash']} plugin arm", flush=True)
        p_rc, p_json, _ = run_probe(cmd["probe"], work, False, plug_log, plug_rc_p)
        print(f"== {cmd['slash']} --no-plugin control", flush=True)
        c_rc, c_json, _ = run_probe(cmd["probe"], work, True, ctrl_log, ctrl_rc_p)

        verdict = classify(cmd, p_json, c_json)
        if verdict["plugin_pass"]:
            n_plugin_pass += 1
        if verdict["control_failed"]:
            n_control_fail += 1
        if verdict["level"] == "c":
            n_full_chain += 1
        if verdict["level"] == cmd["max_level"]:
            n_honest_max += 1

        rows.append({
            "command": cmd["name"],
            "slash": cmd["slash"],
            "probe": cmd["probe"],
            "max_honest_level": cmd["max_level"],
            "reached_level": verdict["level"],
            "note": cmd["note"],
            "plugin": {
                "rc": p_rc,
                "pass": bool(p_json and p_json.get("pass")),
                "checks": (p_json or {}).get("checks"),
                "elapsed_s": (p_json or {}).get("elapsed_s"),
                "cost_usd": ((p_json or {}).get("result") or {}).get("cost_usd"),
                "reply": (p_json or {}).get("reply"),
                "init_slash_proofpunk": (p_json or {}).get("init_slash_proofpunk"),
                "local_plugin_loaded": (p_json or {}).get("local_plugin_loaded"),
                "tool_calls": (p_json or {}).get("tool_calls"),
                "transcript": (p_json or {}).get("transcript"),
                "log": os.path.relpath(plug_log, ROOT),
            },
            "control": {
                "rc": c_rc,
                "pass": bool(c_json and c_json.get("pass")),
                "checks": (c_json or {}).get("checks"),
                "elapsed_s": (c_json or {}).get("elapsed_s"),
                "cost_usd": ((c_json or {}).get("result") or {}).get("cost_usd"),
                "reply": (c_json or {}).get("reply"),
                "init_slash_proofpunk": (c_json or {}).get("init_slash_proofpunk"),
                "local_plugin_loaded": (c_json or {}).get("local_plugin_loaded"),
                "tool_calls": (c_json or {}).get("tool_calls"),
                "transcript": (c_json or {}).get("transcript"),
                "log": os.path.relpath(ctrl_log, ROOT),
            },
            "classify": verdict,
        })

    summary = {
        "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness": "tools/sdk_probe.py + tools/verify-command-surface.py",
        "levels": {
            "a": "script-level (not this harness)",
            "b": "skill-load via Skill tool by name (cmd_truth_audit_flags / cmd_rate_prompt_flag)",
            "c": "slash typed -> registered -> mapped skill ran -> marker observed",
            "playbook-recognition": "slash registered + command-doc marker; no skill/script",
        },
        "full_chain": f"{n_full_chain}/6",
        "plugin_pass": f"{n_plugin_pass}/6",
        "control_fail": f"{n_control_fail}/6",
        "honest_max_reached": f"{n_honest_max}/6",
        "install_cannot_reach_c": True,
        "install_reason": COMMANDS[-1]["note"],
        "commands": rows,
    }
    tmp = ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, ARTIFACT)
    digest = sha256_of(ARTIFACT)
    print(f"ARTIFACT {os.path.relpath(ARTIFACT, ROOT)} sha256:{digest}")
    print(f"full_chain={summary['full_chain']} "
          f"plugin_pass={summary['plugin_pass']} "
          f"control_fail={summary['control_fail']} "
          f"honest_max={summary['honest_max_reached']}")

    # 6/6 at honest maximum + every control failed. Not an inflated 6/6 (c).
    ok = (n_plugin_pass == 6 and n_control_fail == 6 and n_honest_max == 6)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
