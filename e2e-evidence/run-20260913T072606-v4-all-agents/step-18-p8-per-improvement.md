# step-18 — P8: which improvements are INDIVIDUALLY proven

## Why P8 was downgraded
I had marked P8 PASS on the grounds that 15 improvements each cite an
evidence path. They do — but 15 improvements share only 8 artifacts, so a
citation proves the batch, not the member. Retracted to PARTIAL.

## Method: mutate the fix, see if anything fails
An improvement is INDIVIDUALLY proven when reverting it alone makes a named
check fail. Anything else is asserted.

## Results

    I1   CAUGHT      OpenCode filePath guard
                     (step-03: revert -> harness FAILs "MET: still denies
                      writing a test file"; restore -> 36/36)
    I5   CAUGHT      gauge #6 skill-count gate
                     (19 -> 18 inside g_skill_count -> gauge-report rc=1)
    I8   NOT CAUGHT  router delivery-skill counts
    I9   NOT CAUGHT  shared-runbook citation paths

Source restored byte-exact after every mutation.

## Why I8 escapes — a real guard gap
tools/verify-counts.py scans every .md (SKILL.md included), but its
CLAIM_RE requires the number ADJACENT to the noun:

    (\d+)\s+(?:shared\s+(?:doctrine\s+)?)?(skills?|references?|...)

So "18 delivery skills" and "18 other skill files" are structurally
invisible — an intervening word removes the claim from the checker's view.
Mutating those counts to 17 or 11 produces rc=0.

The router's four skill-count claims are therefore UNGUARDED. My fix to
them was correct (the tree has 18 delivery + 1 router), but nothing would
catch them regressing.

## Why I9 escapes — absence is invisible
verify-citations.py validates that `../../references/X.md` paths RESOLVE.
Rewriting one to a bare `references/*-validation.md` removes it from the
pattern's scope entirely, so there is no unresolved path left to fail on.
The checker sees fewer citations, not a broken one.

This is the same blind spot that let 8 broken citations ship in the first
place — and it is why I found them by reading, not by a gate.

## Honest P8 status

    individually proven : I1, I5      (2 of 15)
    unguarded           : I8, I9      (fixes correct, no check defends them)
    unmeasured          : the other 11

P8 stays PARTIAL. Closing it would require either a mutation proof per
improvement or a restatement accepting batch evidence — both are decisions,
not measurements, and neither is mine to make silently.

## Two guard gaps recorded for follow-up
1. CLAIM_RE cannot see a count separated from its noun by a modifier.
2. verify-citations cannot see a citation that was REMOVED from its scope.

VERDICT: P8 PARTIAL, with the proven/unproven split measured rather than
assumed.
