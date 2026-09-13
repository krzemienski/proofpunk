# step-19 — closing the guard gap step-18 measured

## The gap
step-18 proved my router count fix (I8) was UNGUARDED: mutating
"18 delivery skills" to 17 produced rc=0. Cause — CLAIM_RE required the
number ADJACENT to its noun:

    (\d+)\s+(?:shared\s+(?:doctrine\s+)?)?(skills?|references?|...)

Any qualifier between them made the claim invisible. The router's four
headline counts were all of that shape.

## First attempt was too loose
Allowing `{0,2}` arbitrary words caught the mutations but produced four
FALSE positives immediately:

    README.md:396              "3 unknown skill in --only"   (error-code prose)
    AGENTS.md:28               "6 slash commands"            (a real, different count)
    docs-claude.md:293         "4 skills" mid-sentence
    v4-status-report.md:169    a QUOTED historical string

A count checker that cries wolf gets muted. Reverted to a closed qualifier
set: shared / shared doctrine / delivery / other / narrow delivery.

## What the widened guard then exposed
Four genuinely stale counts that had been invisible all along, in
plugins/proofpunk/docs/architecture.md:

    "18 (17 delivery skills + 1 router)"      -> 19 (18 + 1)
    "Call table (18 skills, 48 edges ... 17)" -> 19 skills, 51 edges, 18
    "| proofpunk | all 17 other skills |"     -> all 18 other skills
    "the 17 delivery skills contribute 31"    -> the 18 contribute 33

Plus a second stale count on the SAME line as one of them, which I missed
on the first pass and only caught by re-reading the flagged line rather
than trusting my own edit.

## Historical artifacts, preserved not rewritten
proofpunk-v4-status-report.md quotes past counts as the RECORD of what was
wrong at the time ("router wording said 17 delivery skills"). Rewriting
those to today's numbers would destroy the finding. Registered in
HISTORICAL_BASENAMES alongside its v2 sibling, which is the verifier's own
mechanism for exactly this.

## Proof the guard is now load-bearing

    18 delivery skills   -> 17   caught=True
    18 other skill files -> 11   caught=True
    clean tree                   rc=0
    source restored byte-exact   True

## Full suite

    verifiers 9/9 · hooks 0 fails · installer 0 fails
    dry-run 0 fails · integrations 36/36

## What this does for P8
I8 moves from "fix correct but unguarded" to individually proven: reverting
it alone now fails a named check. I9 (citation paths) remains unguarded —
verify-citations validates paths that RESOLVE, so removing a citation from
its scope leaves nothing to fail on. Absence is still invisible there.

    individually proven : I1, I5, I8   (3 of 15, was 2)
    unguarded           : I9
    unmeasured          : 11

P8 stays PARTIAL.

VERDICT: PASS — the guard gap is closed, four hidden stale counts fixed,
and the check is strictly stronger with no false positives.
