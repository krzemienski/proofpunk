# step-16 — the installer could never install a new skill

## Found by driving a real install
A real install into an isolated HOME (never the operator's ~/.claude) reported:

    == summary: 18 installed, 0 replaced, 0 skipped, 0 missing ==
    skills installed  : 19        <- directories present
    source skills     : 19
    completion-summary: MISSING

19 directories on disk, 18 installed, and the one absent was
`completion-summary` — the skill shipped in v4.

## Root cause
tools/proofpunk-install.sh:46 declared a hardcoded list:

    ALL_SKILLS="brainstorm codebase-truth-audit end-user-testing ... visual-inspection"

18 names, written before completion-summary existed. `SELECTED="$ALL_SKILLS"`
drove the install, so a skill absent from the literal could never be
installed. `grep -c completion-summary tools/proofpunk-install.sh` -> 0.

Worse, the summary line counted the SAME stale list, so "18 installed"
agreed with itself and nothing disagreed. A self-consistent wrong answer.

This is why both installed Claude Code caches (2.2.0 and 3.0.0) lack the
skill — not a stale cache, a defect that ships.

## The fix
ALL_SKILLS is now DERIVED from the tree after SKILLS_SRC is known: any
directory holding a SKILL.md, sorted for determinism (glob order is
locale-dependent). Same definition verify-counts.py and
verify-router-links.py already use.

Ordering verified: derivation at :230-235, first consumption at :254.

## Proven by a real install, after

    == summary: 19 installed, 0 replaced, 0 skipped, 0 missing ==
    skills installed  : 19
    source skills     : 19
    completion-summary: PRESENT
    its SKILL.md      : YES

## The harness caught my change — by design
tools/test-installer.sh keeps its OWN hardcoded EXPECTED_SKILLS, with a
comment explaining why: sourcing the list from the installer would make the
harness absorb the installer's own bugs. It failed 3 assertions the moment
the installer started reporting 19.

That independence is exactly what should have caught the original omission,
and would have, had completion-summary been added to it when the skill
shipped. Added now, with the incident recorded in the comment so the next
person understands why the list is hand-maintained rather than derived.

## All harnesses after the fix

    INSTALLER TEST FAILS: 0
    INSTALL DRY-RUN FAILS: 0
    HOOK TEST FAILS: 0
    INTEGRATION TEST PASSES: 36
    verifiers: 9/9

VERDICT: PASS — a skill added to the tree now installs. Found by driving the
real installer, not by reading it.
