#!/usr/bin/env python3
"""verify-evidence-immutability.py — committed captures are read-only.

`evidence/AGENTS.md` states the rule plainly: "never edit, backfill, or
'clean up' captures — a modified capture is a fabricated claim." Until this
gate existed, nothing enforced it.

Measured 2026-09-14 at HEAD 63727e1: 15 committed captures under
`evidence/v3-release/l16-commands/` were modified in the working tree by an
unscoped `verify-command-surface.py` run.
`cmd_slash_implement.plugin.log` shrank 13706B -> 477B — a green capture
replaced by a crash log — and `cmd_slash_implement.plugin.rc` flipped 0 -> 2.
Thirteen gates ran green across that state. None of them looks at whether a
committed capture still matches the blob that was committed, so the one
defect class the evidence tree exists to prevent was the one class no gate
could see.

WHAT THIS GATE CAN OBSERVE
  Content drift of tracked files under the capture roots, measured against
  the committed blob via `git diff`. Modification, truncation, and deletion
  all surface, because all three make the working tree disagree with HEAD.

WHAT THIS GATE CANNOT OBSERVE
  - Anything about UNTRACKED files. A new capture is how evidence is
    supposed to arrive; this gate is silent on it by design.
  - Anything about a NEWLY STAGED capture. `git diff HEAD` reports a staged
    addition as a change, but a path absent from HEAD was never committed,
    so it cannot have been mutated. Measured 2026-09-14: staging a fresh
    103-file run directory turned this gate red with 103 "MODIFIED COMMITTED
    CAPTURES", every one of which was absent from HEAD. That is the same
    false-alarm shape the gate exists to prevent, pointed at itself — and a
    gate that cries wolf on the normal path of adding evidence gets muted,
    which would silence the real check.
  - A mutation that is committed. Once a bad edit is in a commit, HEAD and
    the worktree agree again and this gate goes quiet. It guards the window
    between mutation and commit, which is exactly where the measured
    incident lived. Catching a committed mutation needs history analysis
    against the capture's original commit, which this gate does not do.
  - Whether a capture's CONTENT is truthful. Byte-identical to HEAD is the
    whole claim.
  - Mutations in a detached/ref-less state where `git diff` cannot resolve
    HEAD — reported as an error, never as a pass.

Stdlib Python 3 only. Never pipes. Never writes evidence/.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=evidence,e2e-evidence keywords=git diff,subprocess
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Capture roots. Both hold sealed run artifacts that a later run must never
# rewrite in place.
CAPTURE_ROOTS = ("evidence", "e2e-evidence")

# Authored documentation that LIVES inside a capture root but is not a capture.
# `evidence/AGENTS.md` is this repository's evidence doctrine: the very file the
# deny message below cites. Treating it as a sealed capture made the doctrine
# permanently uneditable, and the gate's own remedy ("write new artifacts to a
# fresh run-scoped directory") is incoherent for a directory-level AGENTS.md.
#
# Measured 2026-09-14: adding a rule to evidence/AGENTS.md — to stop the very
# workflow mistake that had tripped this gate three times — was itself refused
# with `REWRITTEN 1551B -> 2487B`.
#
# `capture-guard.sh` already draws this line at runtime and has since it was
# written: `.md` and `.json` are authored sidecars, always allowed; only raw
# capture extensions (.txt .log .out .err .jsonl .png .har .csv) are protected.
# This gate disagreed with that hook about the same rule. It now agrees.
#
# Scoped by PATH, not by extension, and not by basename alone.
#
# NOT by extension: capture-guard.sh exempts all `.md`/`.json` because it guards
# a different thing (a live tool call writing a raw capture). Copying that rule
# here would gut this gate — every step-NN.md and every evidence-inventory.txt
# this session protected is `.md`. They must stay protected.
#
# NOT by basename alone: a README.md written INSIDE a run directory is part of
# that run's record and is a capture. One exists today:
# e2e-evidence/run-20260827T162405-ref-differential-pristine/README.md.
#
# So: exempt only an authored doc sitting at the TOP LEVEL of a capture root,
# outside any run-* or <release>-release subdirectory.
AUTHORED_BASENAMES = {"AGENTS.md", "README.md", "CLAUDE.md"}


def is_authored_doc(path: str) -> bool:
    """True for top-level authored docs like evidence/AGENTS.md.

    `evidence/AGENTS.md` -> parts ('evidence', 'AGENTS.md') -> depth 2 -> exempt.
    `evidence/v3-release/.../README.md` -> deeper -> a capture, still protected.
    """
    parts = path.split("/")
    return len(parts) == 2 and parts[1] in AUTHORED_BASENAMES


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    )


def main() -> int:
    head = git("rev-parse", "--short", "HEAD")
    if head.returncode != 0:
        print("ERROR: cannot resolve HEAD; refusing to report a pass")
        print(head.stderr.strip())
        return 2
    print(f"== committed-capture immutability at HEAD {head.stdout.strip()}")

    existing = [r for r in CAPTURE_ROOTS if os.path.isdir(os.path.join(ROOT, r))]
    if not existing:
        print("ERROR: no capture root found; refusing to report a vacuous pass")
        return 2

    fails: list[str] = []
    total_tracked = 0

    for root in existing:
        # Tracked files only. `git diff --name-only HEAD -- <root>` reports
        # every tracked path under the root whose worktree content differs
        # from the committed blob, including deletions.
        ls = git("ls-files", "--", root)
        if ls.returncode != 0:
            print(f"ERROR: git ls-files failed for {root}")
            print(ls.stderr.strip())
            return 2
        tracked = [p for p in ls.stdout.splitlines() if p.strip()]
        total_tracked += len(tracked)

        diff = git("diff", "--name-only", "HEAD", "--", root)
        if diff.returncode != 0:
            print(f"ERROR: git diff failed for {root}")
            print(diff.stderr.strip())
            return 2
        candidates = [p for p in diff.stdout.splitlines() if p.strip()]

        # A path `git diff HEAD` reports but which does not exist in HEAD is
        # a newly added (staged) capture, not a mutated one. Only a file that
        # HAS a committed blob can have drifted from it.
        changed = []
        authored = 0
        for p in candidates:
            if is_authored_doc(p):
                authored += 1
                continue
            if git("cat-file", "-e", f"HEAD:{p}").returncode == 0:
                changed.append(p)
        added = len(candidates) - len(changed) - authored

        print(
            f"   {root}: tracked={len(tracked)} modified={len(changed)}"
            + (f" (+{added} newly added, not in HEAD — out of scope)" if added else "")
            + (f" (+{authored} authored doc(s) — not captures)" if authored else "")
        )
        for path in changed:
            # Report the size delta, since truncation is the shape that
            # destroys a green capture most quietly.
            blob = subprocess.run(
                ["git", "show", f"HEAD:{path}"],
                cwd=ROOT, capture_output=True,
            )
            sealed_n = len(blob.stdout) if blob.returncode == 0 else -1
            abs_p = os.path.join(ROOT, path)
            live_n = os.path.getsize(abs_p) if os.path.exists(abs_p) else -1
            if live_n < 0:
                shape = "DELETED"
            elif sealed_n >= 0 and live_n < sealed_n:
                shape = f"TRUNCATED {sealed_n}B -> {live_n}B"
            elif sealed_n >= 0:
                shape = f"REWRITTEN {sealed_n}B -> {live_n}B"
            else:
                shape = "MODIFIED"
            fails.append(f"{path}: {shape}")

    if total_tracked == 0:
        print("ERROR: zero tracked captures found; refusing to report a pass")
        return 2

    if fails:
        print(f"\nMODIFIED COMMITTED CAPTURES ({len(fails)}):")
        for f in fails:
            print(f"   {f}")
        print(
            "\nevidence/AGENTS.md: a modified capture is a fabricated claim.\n"
            "Restore with `git checkout -- <path>` and write new artifacts to a\n"
            "fresh run-scoped directory instead of rewriting a sealed one."
        )
        print("VERDICT: FAIL")
        return 1

    print(f"\nPASS evidence-immutability: {total_tracked} committed captures "
          "byte-identical to HEAD")
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
