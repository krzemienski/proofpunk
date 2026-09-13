# step-33 — a comment is not a gate

## The gap I "documented"

Step-32 added `verification_block_run`, kept it out of INSTALL_EFFECT_CHECKS,
and wrote a comment saying the fourth criterion stays UNVERIFIED. I called
that honest. It was honest PROSE and a live overclaim.

Two consumers decide "fully proven" by reading the LEVEL STRING alone:

    verify-command-surface.py   if verdict["level"] in ("c", "d")
    gauge-report.py             c.get("reached_level") in ("c", "d")

Neither reads `effect_partial`. So a row could carry effect_partial=True and
still be counted in gauge #4's full-chain total — an install missing its
fourth acceptance criterion raising the very number that gates the release.
Adding a sibling flag changed nothing, because nothing consumed it.

## Fixed at the source, not the consumers

A partial promotion now returns level "d-partial" with effect_proven=False.
Both predicates exclude it because "d-partial" is not in their tuples. No
consumer had to change — it fails closed everywhere by construction.

Measured across all three states:

    ABSENT -> d-partial  effect_proven=False  counted=False
    FALSE  -> d-partial  effect_proven=False  counted=False
    TRUE   -> d          effect_proven=True   counted=True

Verify path unaffected (level d, never partial).

## Regression
tools/test-promotion-partial.py, 20 assertions: the three states, each of
the 6 gated checks blocking promotion independently, the verify path, and a
CONSUMER-CONTRACT guard that reads both consumers' source and fails if
either predicate drifts or if "d-partial" is ever added to a full-chain
tuple. That guard is the part that keeps this fix from silently rotting.

## The pattern, fifth occurrence

Each time the mechanism was right and the CLAIM about it was wrong:

    step-29  claimed a safety boundary, shipped a basename regex
    step-30  five wrong paths credited
    step-32  hardened one branch, left its twin unguarded
    step-32  claimed a documented gap was contained
    step-33  the gap was reachable by the release gate

The correction each time came from executing the claim, never from
re-reading it.

## Suite
verify-counts, verify-orchestration, test-write-assertion 67,
test-promotion-partial 20, test-hooks, test-integrations 36/36,
dry-run-install, test-installer — all PASS.

VERDICT: the fourth criterion can no longer be silently skipped. P6 stays
UNVERIFIED at 4/6; the unpinned, unrecorded model is still untouched.
