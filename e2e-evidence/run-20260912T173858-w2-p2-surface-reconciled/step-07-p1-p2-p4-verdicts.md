# P1 / P2 / P4 — verdicts from this run

| Criterion | Verdict | Evidence |
|---|---|---|
| P1 installer defects w/ reproduction | PASS (no BLOCKERs found) | step-06-p1-installer-blocker-hunt.md |
| P2 complete surface on clean HOME | PASS | step-01-p2-count-reconciliation.md |
| P4 installer idempotent | PASS | step-04-p4-idempotency-recaptured.md |

## P1 detail
8 hostile conditions driven against the real installer. All 8 fail
closed with a correct unpiped rc; none produced a partial install or a
silent success. No BLOCKER was found, so P1's 'every BLOCKER has a
verbatim command + rc + file:line' is satisfied over an empty set —
stated plainly rather than presented as if defects had been hunted and
cleared.

Observation (not a blocker): C2 (unwritable HOME) and C4 (.claude is a
regular file) surface the raw 'mkdir: ... Permission denied' / 'Not a
directory' from the shell rather than the installer's own die() 'ERROR:'
format used by C5/C6/C8. The rc is correct (1) and the message names the
real cause, so this is a consistency nit, not a defect. Recorded rather
than fixed: changing it would mean wrapping every mkdir in the script.

## P2 detail
The criterion's 6 commands / 3 agents / 7 hooks come from decision D4's
v2.2.0 baseline. v4 ships 7 / 4 / 10. Treating those as a floor, every
baseline item is present and the extras are accounted for by name.
The load-bearing check is not the count but the set comparison: all 10
hook scripts are on disk AND all 10 are registered in settings.json,
0 missing and 0 extra in both directions. 'Placed but unwired' is the
v1.10.0 defect class this check exists to catch.

## P4 detail
Two installs into one HOME. settings.json is byte-identical afterwards
(diff rc=0, matching sha256 recorded), 12 registered commands both
times, 18/18 skills skipped by collision protection on the second run,
and exactly one settings.json.bak (overwritten in place, not one per
run).
