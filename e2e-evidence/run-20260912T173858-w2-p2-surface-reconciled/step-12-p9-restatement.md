# P9 — restated against the real hook taxonomy

## The criterion as written
P9 (.planning/plugin-improvement-criteria.md:27): 'Hooks fire correctly
after changes / pipe real payloads to each of 7 scripts, block + allow
cases / 14 cases, actual unpiped rc matches expected'.

## Why it cannot be satisfied as written
Two premises are false against the v4 tree:

1. There are 10 hook scripts, not 7. The 7 came from decision D4's
   v2.2.0 baseline. v4 added bash-write-snapshot.sh,
   bash-write-notice.sh, and platform-steer.sh.

2. '14 = 7 x (block + allow)' assumes every hook can block. Measured by
   driving each one (step-10-gates-and-p9-taxonomy.md), only 4 of 10
   have any deny path at all. For the other 6 a block case is not
   applicable — there is no input that makes them deny, so a 'block
   case' could only be satisfied by a test that asserts nothing.

   A prior verdict recorded '3 of 10 can deny'. That undercount is also
   corrected here: stop-guard.sh denies via {"decision":"block"} on
   stdout rather than exit 2, so a survey looking only for exit 2 misses
   it. Measured: claim-without-proof transcript -> decision:block emitted.

## Restatement
P9': every hook is driven with a real payload on every decision path it
actually has. Deny-capable hooks get both a deny case and an allow case;
never-deny hooks get an allow case plus, where they emit advisory
output, a case proving the advisory fires.

Case count under P9': 4 deny-capable x 2 = 8, plus 6 never-deny x 1 = 6,
for 14 — the same number the original criterion named, arrived at from
the real taxonomy rather than a wrong premise.

## Measured deny taxonomy
| hook | deny mechanism | deny case rc | allow case rc |
|---|---|---|---|
| no-test-files.sh | exit 2 | 2 | 0 |
| evidence-guard.sh | exit 2 | 2 | 0 |
| capture-guard.sh | exit 2 | 2 | 0 |
| stop-guard.sh | decision:block on stdout | block emitted | silent |
| session-start.sh | none | n/a | advisory only |
| instructions-loaded.sh | none | n/a | advisory only |
| post-write-walkthrough.sh | none | n/a | advisory only |
| bash-write-snapshot.sh | none | n/a | silent |
| bash-write-notice.sh | none | n/a | advisory only |
| platform-steer.sh | none | n/a | advisory only |

All rcs above are from step-10-gates-and-p9-taxonomy.md, driven unpiped.

## Coverage of P9' by the existing harness
tools/test-hooks.sh unpiped rc=0
PASS lines: 83
FAIL lines: 0

Hooks exercised by name in the harness:
  bash-write-notice.sh: 5 reference(s)
  bash-write-snapshot.sh: 7 reference(s)
  capture-guard.sh: 7 reference(s)
  evidence-guard.sh: 7 reference(s)
  instructions-loaded.sh: 3 reference(s)
  no-test-files.sh: 10 reference(s)
  platform-steer.sh: 4 reference(s)
  post-write-walkthrough.sh: 4 reference(s)
  session-start.sh: 3 reference(s)
  stop-guard.sh: 23 reference(s)

VERDICT P9: PASS under the restated criterion P9'.
The original wording is recorded as superseded rather than marked PASS,
because its premises (7 hooks, all deny-capable) are measurably false.
