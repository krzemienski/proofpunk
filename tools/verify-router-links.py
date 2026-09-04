#!/usr/bin/env python3
"""verify-router-links.py — derived (never restated) router-head closure.

Globs plugins/proofpunk/skills/*/SKILL.md for the true skill set, parses the
router head's own '## Skill calls' table, and asserts:

  (a) every non-head skill is routed to — the expected count is glob_N - 1,
      never a literal 17
  (b) zero orphans (routed names that do not exist as skill directories)
  (c) every reference in the router's '## Shared doctrine' table resolves
      as a real file relative to the citing SKILL.md

Exit 0 on a clean tree. Exit 1 on any failure, naming the offender on
stdout. Stdlib only. Deterministic.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=SKILL.md keywords=Skill calls,Shared doctrine
from __future__ import annotations

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
SKILLS_ROOT = os.path.join(ROOT, "plugins", "proofpunk", "skills")
HEAD_NAME = "proofpunk"
HEAD_PATH = os.path.join(SKILLS_ROOT, HEAD_NAME, "SKILL.md")

CALLS_HEADING = "## Skill calls"
DOCTRINE_HEADING = "## Shared doctrine"


def fail(offenders: list[str]) -> int:
    print("VERDICT: FAIL")
    for o in offenders:
        print(f"OFFENDER: {o}")
    return 1


def skill_set() -> list[str]:
    """True skill set from disk. Order is the glob sort of parent dirs."""
    paths = glob.glob(os.path.join(SKILLS_ROOT, "*", "SKILL.md"))
    names = sorted(os.path.basename(os.path.dirname(p)) for p in paths)
    return names


def section_after(body: str, heading: str) -> str | None:
    """Return the markdown section starting at `heading` up to the next H2.

    The heading argument is a prefix of the H2 line so a title like
    '## Shared doctrine — what every skill defers to' still matches
    '## Shared doctrine'. The match is line-anchored.
    """
    m = re.search(
        rf"^{re.escape(heading)}[^\n]*\n(.*?)(?=\n## |\Z)",
        body,
        re.S | re.M,
    )
    return m.group(1) if m else None


def parse_skill_calls(sec: str) -> list[str]:
    """Parse the Calls column of the router's skill-call table.

    Matches the same row shape used by tools/verify-orchestration.py:
    a pipe-table row whose first cell is a backtick-wrapped skill name.
    """
    return re.findall(r"^\| `([a-z0-9-]+)` \|", sec, re.M)


def parse_doctrine_refs(sec: str) -> list[str]:
    """Parse backtick-wrapped relative paths from the Shared doctrine table."""
    return re.findall(r"^\| `([^`]+)` \|", sec, re.M)


def main() -> int:
    offenders: list[str] = []

    if not os.path.isfile(HEAD_PATH):
        return fail([f"router head missing: {HEAD_PATH}"])

    names = skill_set()
    n = len(names)
    expected_routed = n - 1  # derived: never a restated literal

    if HEAD_NAME not in names:
        offenders.append(
            f"head '{HEAD_NAME}' is not in the globbed skill set {names}"
        )

    non_head = [s for s in names if s != HEAD_NAME]

    with open(HEAD_PATH, encoding="utf-8") as fh:
        head_text = fh.read()

    calls_sec = section_after(head_text, CALLS_HEADING)
    if calls_sec is None:
        offenders.append(
            f"{HEAD_PATH}: missing '{CALLS_HEADING}' section"
        )
        routed: list[str] = []
    else:
        routed = parse_skill_calls(calls_sec)
        if not routed:
            offenders.append(
                f"{HEAD_PATH}: '{CALLS_HEADING}' table parsed 0 rows"
            )

    routed_set = set(routed)
    non_head_set = set(non_head)

    missing = sorted(non_head_set - routed_set)
    orphans = sorted(routed_set - non_head_set)
    # A self-route is also an orphan against the non-head set, but name it
    # distinctly so a mutation that points the table at the head is obvious.
    if HEAD_NAME in routed_set:
        offenders.append(
            f"self-route: router table lists '{HEAD_NAME}'"
        )

    if missing:
        offenders.append(
            "unrouted skill(s) "
            f"(expected {expected_routed} non-head from glob of {n}; "
            f"table has {len(routed_set)} unique): {missing}"
        )
    if orphans:
        offenders.append(
            f"orphan route(s) (name does not exist as a skill dir): {orphans}"
        )

    # Duplicate rows in the table: still a defect (the count would otherwise
    # look like coverage while a name is listed twice and another is missing).
    dupes = sorted({r for r in routed if routed.count(r) > 1})
    if dupes:
        offenders.append(f"duplicate route(s) in skill-call table: {dupes}")

    doctrine_sec = section_after(head_text, DOCTRINE_HEADING)
    if doctrine_sec is None:
        offenders.append(
            f"{HEAD_PATH}: missing '{DOCTRINE_HEADING}' section"
        )
        refs: list[str] = []
    else:
        refs = parse_doctrine_refs(doctrine_sec)
        if not refs:
            offenders.append(
                f"{HEAD_PATH}: '{DOCTRINE_HEADING}' table parsed 0 refs"
            )

    citing_dir = os.path.dirname(HEAD_PATH)
    broken_refs = []
    for ref in refs:
        resolved = os.path.normpath(os.path.join(citing_dir, ref))
        if not os.path.isfile(resolved):
            broken_refs.append(f"{ref} -> {resolved}")
    if broken_refs:
        offenders.append(
            "doctrine reference(s) do not resolve relative to "
            f"{HEAD_PATH}: {broken_refs}"
        )

    if offenders:
        return fail(offenders)

    print("VERDICT: PASS")
    print(f"skills_globbed={n}")
    print(f"non_head_expected={expected_routed}")
    print(f"routed={len(routed)} unique={len(routed_set)}")
    print(f"doctrine_refs={len(refs)} all_resolved=true")
    print(f"head={HEAD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
