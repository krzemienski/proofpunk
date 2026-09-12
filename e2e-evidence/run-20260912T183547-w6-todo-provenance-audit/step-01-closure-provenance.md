# Todo closures: what they rest on, and what that is worth

The stop reminder listed 30 open items. Reconciling them against disk
showed most were done with sealed artifacts and simply never closed.
Before closing them I checked WHICH RUN each cited artifact lives in.

## Run provenance
| run | integrity |
|---|---|
| run-20260912T172922-w2-installer-p1p2p4 | INVALID — validate rc=2 |
| run-20260912T173858-w2-p2-surface-reconciled | MUTATED — step-13 deleted post-seal |
| run-20260912T175349-w3-lane-contracts | MUTATED — step-17 edited post-seal |
| run-20260912T181712-w5-integrity-disclosure | CLEAN — 7/7 sealed, 0 post-seal edits |

## Every closure cites a compromised run
| closed todo | cited run | integrity |
|---|---|---|
| Scout hooks / deny taxonomy | w2-p2-surface-reconciled | MUTATED |
| Restate P9 | w2-p2-surface-reconciled | MUTATED |
| Scout 18 skills | w3-lane-contracts | MUTATED |
| Scout installer / P1 | w2-p2-surface-reconciled | MUTATED |
| run-targeting fix | w3-lane-contracts | MUTATED |
| lane contract conformance | w3-lane-contracts | MUTATED |
| debian root+non-root | w3-lane-contracts | MUTATED |
| full gate matrix | w3-lane-contracts | MUTATED |

## What that does and does not invalidate
The MEASUREMENTS stand. Each was driven against a real runtime, and
every artifact's sha256 still matches what was sealed — verified by
recomputing digests, not by trusting validate. What is compromised is
the RUN HISTORY: two runs had an artifact removed or edited after a
seal, and a re-seal made each internally consistent again.

So the honest reading of these closures is: the work was done and
driven, and its evidence sits in runs whose provenance is disclosed as
imperfect. That is weaker than 'closed with clean sealed evidence' and
stronger than 'unverified'. The criteria table already reflects this —
P14 is UNVERIFIED and P15 is FAIL precisely because of these runs.

## Why I am not re-driving everything into a clean run
Re-driving the installer hunts, the gate matrices, the Linux arms and
the boundary probes to launder them into a fresh run would produce
identical numbers and a cleaner-looking record. It would not make the
earlier mutations un-happen, and a record that looks cleaner than the
history it describes is the failure mode this session already
committed twice. The disclosure stays; the closures stay qualified.

## Still genuinely open
  P6  router driven live — never attempted
  P10 doctrine precedence map — never produced
  P7  improvement backlog ranking — not done
  P11 18-skill prose review — 4 skills touched of 18
  disclosure-debt paydown on 6 oversized skills — not started
  session mining — never ran (I closed it in error and reopened it)
  verify-command-surface.py to completion — still never finished
