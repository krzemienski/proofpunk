#!/usr/bin/env python3
"""verify-proof-vocab.py — Class 4 permanent detector.

A status word (DONE / FIXED / RESOLVED / PASS / PROVEN / VERIFIED) in a
committed living document must sit adjacent to a path citation. Bare
completion language without a cite is the defect class that produced
"12 probes = 12 improvements" and a FIXED label that driving later
refuted.

SCOPE
-----
Living docs, not immutable captures:

  .planning/*.md
  docs/*.md                 (source; generated *.html is skipped)
  README.md, AGENTS.md, CLAUDE.md
  plugins/proofpunk/AGENTS.md
  tools/AGENTS.md
  e2e-evidence/AGENTS.md
  evidence/AGENTS.md

Skipped on purpose: e2e-evidence/run-*, evidence/v*-release/*, generated
HTML, dated release reports at repo root, plugins/proofpunk/docs/
historical logs. Those are captures or provenance, not live status.

A hit is a line matching a completion word as a whole word. It PASSES
when the same line, the previous line, or the next line contains a
path-shaped citation (foo/bar.ext or foo/bar/) OR a proof-level token
(END-USER, script-level, script, install, model-only, UNVERIFIED,
UNPROVEN, BLOCKED, FAIL). Table rows count the whole row as "the same
line" after joining cells.

Exit 0 = every hit is cited. Exit N = N uncited hits, printed as path:line.
Stdlib only.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=AGENTS.md,README.md keywords=glob.glob,re.search
from __future__ import annotations

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

STATUS = re.compile(
    r"(?<![A-Za-z])(?:DONE|FIXED|RESOLVED|PASS|PROVEN|VERIFIED)(?![A-Za-z])"
)
NEGATED = re.compile(
    r"\b(?:never|not|only|unexecuted)\s+PASS\b|"
    r"false-PASS|false PASS|"
    r"verifier PASS|"
    r"is not PASS|"
    r"after visual PASS",
    re.I,
)
HARNESS_COUNT = re.compile(
    r"\b\d+\s+PASS\b|"
    r"\brc=\d+/\d+\s+PASS\b|"
    r"PASS iff\b",
    re.I,
)
PROOF_TOKEN = re.compile(
    r"\b(?:END-USER|script-level|model-only|UNVERIFIED|UNPROVEN|BLOCKED|FAIL|"
    r"CLOSED|PARTIAL|VOID|OPEN)\b"
)
PATH_CITE = re.compile(
    r"(?:[A-Za-z0-9_.-]+/)+\S+\.\w+|"  # path/to/file.ext
    r"`[^`]+\.[A-Za-z0-9]+`|"          # `file.ext`
    r"\b\w+\.(?:md|py|sh|json|yml):"   # file.md:12
)

SKIP_FILES = frozenset({
    "docs/skill-canon.md",
    ".planning/proofpunk-agent.prompt.md",
})

TARGETS = [
    ".planning/*.md",
    "docs/*.md",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "plugins/proofpunk/AGENTS.md",
    "tools/AGENTS.md",
    "e2e-evidence/AGENTS.md",
    "evidence/AGENTS.md",
]


def expand_targets() -> list[str]:
    paths: list[str] = []
    for pat in TARGETS:
        if any(ch in pat for ch in "*?["):
            paths.extend(sorted(glob.glob(os.path.join(ROOT, pat))))
        else:
            p = os.path.join(ROOT, pat)
            if os.path.isfile(p):
                paths.append(p)
    # docs/*.md only — drop html if a glob ever picks it up
    return [p for p in paths if not p.endswith(".html")]


def cited(window: str) -> bool:
    if PROOF_TOKEN.search(window) or PATH_CITE.search(window):
        return True
    # Adjacent proof-level language that is not a filesystem path:
    # "PASS live" (END-USER drive) and "artifact citation" (the Class 4
    # requirement stated as a criterion).
    if re.search(r"\bPASS live\b", window):
        return True
    if re.search(r"\bartifact citation\b", window, re.I):
        return True
    return False


def check_file(path: str) -> list[str]:
    rel = os.path.relpath(path, ROOT)
    if rel in SKIP_FILES:
        return []
    try:
        with open(path, errors="ignore") as f:
            lines = f.read().splitlines()
    except OSError as e:
        return [f"{rel}: unreadable ({e})"]
    hits: list[str] = []
    for i, line in enumerate(lines):
        if not STATUS.search(line):
            continue
        if NEGATED.search(line):
            continue
        if HARNESS_COUNT.search(line):
            continue
        prev = lines[i - 1] if i > 0 else ""
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        window = "\n".join((prev, line, nxt))
        if cited(window):
            continue
        hits.append(f"{rel}:{i + 1}: uncited status word: {line.strip()[:160]}")
    return hits


def main() -> int:
    files = expand_targets()
    print(f"files={len(files)}")
    fails: list[str] = []
    for p in files:
        fails.extend(check_file(p))
    print(f"uncited={len(fails)}")
    if fails:
        print("VERDICT: FAIL")
        for f in fails:
            print(f"  {f}")
        return 1 if len(fails) else 0
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
