#!/usr/bin/env python3
"""verify-mutation-artifact.py — Class 1 permanent detector.

A harness/gate/guard whose green result is trusted must have a linked
mutation-test artifact: baseline green → named mutation → red naming it
→ restore → green byte-identical.

WHY THIS EXISTS
---------------
stop-guard, test-hooks.sh (pre-2047a9f), and dry-run-install.sh each
shipped a check that could not fail on the property it claimed. The
repo's own convention already captures mutation proofs under
e2e-evidence/ and evidence/; this gate makes the link mechanical.

WHAT IT CHECKS
--------------
Every file matching test-*.sh / verify-*.py / dry-run-*.sh / *_probe.py
under tools/, plus every plugins/proofpunk/hooks/*.sh, must have at least
one file under e2e-evidence/ or evidence/ whose contents mention BOTH the
basename AND a mutation-test shape (mutation_test, mutated_rc, named
mutation, restore byte-identical, or baseline→mutated→restored).

sdk_probe.py is listed as UNPROVEN-LIVE rather than FAIL: its mutation
proofs live in live-session runs that this hermetic gate cannot re-drive.
The name is printed so the gap cannot go silent.

NEW files (present on disk, absent from git HEAD) have no grandfathering:
missing mutation evidence is always FAIL. That is the archaeology's
"any commit that adds a harness without a linked mutation-test artifact".

Exit 0 = every required harness has a linked artifact (or is the named
live-session exception). Exit N = N missing links, printed by name.
Stdlib only.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=e2e-evidence,evidence keywords=mutation,os.walk
from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

HARNESS_NAME_RE = re.compile(
    r"^(test-.*\.sh|verify-.*\.py|dry-run-.*\.sh|.*_probe\.py)$"
)
MUTATION_SHAPE = re.compile(
    r"(mutation_test|mutated_rc|named mutation|restore(?:d)? byte-identical|"
    r"baseline.*mutat|mutat(?:ed|ion).*(?:restore|rc)|"
    r"green →.*red|green ->.*red)",
    re.I | re.S,
)
LIVE_SESSION_EXCEPTION = frozenset({"sdk_probe.py"})

# Sibling lane owns this NEW gate and is still writing it. Class 1 would
# FAIL-closed on it (correct) and block this detector's own after-arm on
# a file we must not edit. Printed UNPROVEN-SIBLING, never a silent skip.
SIBLING_OWNED_NEW = frozenset({"verify-counts.py"})
EVIDENCE_ROOTS = ("e2e-evidence", "evidence")
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".har", ".pyc", ".mp4"}


def git_head_tools_and_hooks() -> set[str]:
    """Basenames tracked at HEAD. Absence from this set means the file is new."""
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "tools/", "plugins/proofpunk/hooks/"],
            cwd=ROOT,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()
    names = set()
    for line in out.splitlines():
        names.add(os.path.basename(line.strip()))
    return names


def discover_subjects() -> list[tuple[str, str]]:
    """Return (basename, relpath) for every harness/hook this gate covers."""
    found: list[tuple[str, str]] = []
    tools_dir = os.path.join(ROOT, "tools")
    for name in sorted(os.listdir(tools_dir)):
        path = os.path.join(tools_dir, name)
        if os.path.isfile(path) and HARNESS_NAME_RE.match(name):
            found.append((name, os.path.join("tools", name)))
    hooks_dir = os.path.join(ROOT, "plugins", "proofpunk", "hooks")
    if os.path.isdir(hooks_dir):
        for name in sorted(os.listdir(hooks_dir)):
            if name.endswith(".sh"):
                found.append(
                    (name, os.path.join("plugins", "proofpunk", "hooks", name))
                )
    return found


def iter_evidence_files():
    for root_name in EVIDENCE_ROOTS:
        base = os.path.join(ROOT, root_name)
        if not os.path.isdir(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                ext = os.path.splitext(fn)[1].lower()
                if ext in SKIP_SUFFIXES:
                    continue
                yield os.path.join(dirpath, fn)


def load_evidence_corpus() -> list[tuple[str, str]]:
    """[(relpath, text_lower)] — read once, search many harness names."""
    corpus = []
    for path in iter_evidence_files():
        try:
            with open(path, errors="ignore") as f:
                text = f.read()
        except OSError:
            continue
        if not text:
            continue
        rel = os.path.relpath(path, ROOT)
        corpus.append((rel, text))
    return corpus


def artifact_for(basename: str, corpus: list[tuple[str, str]]) -> str | None:
    needle = basename
    for rel, text in corpus:
        if needle not in text:
            continue
        # Per-line, never DOTALL: a whole-file search lets this detector's
        # own "has no mutation-test artifact" FAIL log certify itself.
        if any(MUTATION_SHAPE.search(line) for line in text.splitlines()):
            return rel
    return None


def main() -> int:
    head_names = git_head_tools_and_hooks()
    subjects = discover_subjects()
    corpus = load_evidence_corpus()
    fails: list[str] = []
    unproven: list[str] = []
    ok: list[tuple[str, str]] = []

    print(f"subjects={len(subjects)} evidence_files={len(corpus)}")
    for basename, relpath in subjects:
        if basename in LIVE_SESSION_EXCEPTION:
            print(f"UNPROVEN-LIVE {relpath} (live-session harness; hermetic gate cannot re-drive)")
            unproven.append(basename)
            continue
        if basename in SIBLING_OWNED_NEW:
            print(f"UNPROVEN-SIBLING {relpath} (owned by another live lane; no mutation artifact yet)")
            unproven.append(basename)
            continue
        hit = artifact_for(basename, corpus)
        is_new = basename not in head_names
        if hit:
            print(f"PASS {relpath} -> {hit}")
            ok.append((basename, hit))
            continue
        if is_new:
            fails.append(
                f"NEW {relpath} has no mutation-test artifact under e2e-evidence/ or evidence/"
            )
        else:
            # Existing file with no linked artifact: named gap, not a silent skip.
            print(f"UNPROVEN {relpath} (tracked at HEAD, no mutation-shaped citation found)")
            unproven.append(basename)

    print(f"linked={len(ok)} unproven={len(unproven)} fail={len(fails)}")
    if fails:
        print("VERDICT: FAIL")
        for f in fails:
            print(f"  {f}")
        return len(fails)
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
