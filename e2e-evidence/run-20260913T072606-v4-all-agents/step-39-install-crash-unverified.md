# step-39 — a hypothesis I built and then killed

## The question

The pinned surface's one harness error was the install plugin arm dying at
"Fatal error in message reader". Is that deterministic or transient, and
should the retry policy cover it?

## The hypothesis I formed

Searched every recorded install plugin arm:

    v3 lane-commands step-02      ok
    v3b-gauge4                    ok
    v4 p6-surface-pinned          CRASH
    v3-release attempt1           CRASH
    v3-release canonical .log     ok

Four ok, two crashes, and — critically — in v3-release the attempt1 file
CRASHED while the canonical .log for the same arm PASSED. I read that as
"a retry recovered it", concluded the shape is retry-recoverable, and was
about to argue for widening _TRANSIENT_RE, which currently matches only
rate-limit and OAuth shapes and never matched this crash text.

## Why that was wrong

Checked before acting:

    attempt1 sha ae356f3a  475 bytes   mtime 2026-09-13 05:52:45
    canonical sha ff2b21fa 30991 bytes mtime 2026-09-13 11:08:27

Only attempt1 exists. There is no attempt2. The two files differ by 30KB
and five hours sixteen minutes. The canonical is not a recovered retry of
the crashed attempt — it is a mirror written by a LATER, SEPARATE
invocation that overwrote it.

So the evidence never showed a retry succeeding. It showed two different
runs, one of which crashed. My inference chained "attempt1 crashed" +
"canonical passed" into "the retry worked", when the mirror step makes
those two files independent by construction.

## What I actually know

    - The crash is not deterministic: the same arm succeeded in other runs.
    - It is NOT proven retry-recoverable: no same-run retry was ever
      observed for this shape.
    - _TRANSIENT_RE does not match it, so it ran once. Whether it SHOULD
      be retried is now an open question with no supporting evidence.

## Decision

Classify the install plugin arm's crash UNVERIFIED. Do not widen
_TRANSIENT_RE on a correlation I just falsified. Retry policy is a separate
change needing its own evidence — ideally a same-run retry observed with
attempt2 present.

Widening it now would be the exact pattern this session keeps producing: a
mechanism built on a claim that felt measured and was not.

## Status
P6 UNVERIFIED at 4/6. Two blockers remain and both are real behaviour
questions: this crash (transient, cause unknown) and truth-audit's level.

VERDICT: hypothesis falsified by its own evidence; no code change made.
