# The ledger applies its own standard unevenly, and cannot self-correct

## What happened
After auditing run provenance I marked the three W3 items BLOCKED:
driven and measured, but their evidence lives in a run whose history is
disclosed as mutated, so closing them would assert clean sealed proof I
do not have.

The same is true of six items I had ALREADY closed before running that
audit:
  Contracts / fix fresh_evidence run-targeting race   -> w3-lane-contracts (MUTATED)
  Contracts / emit executable lane contracts           -> w3-lane-contracts (MUTATED)
  Contracts / prove lane contract conformance          -> w3-lane-contracts (MUTATED)
  W2 / P1 installer BLOCKER hunt                       -> w2-p2-surface-reconciled (MUTATED)
  W2 / P2 temp HOME install + inventory                -> w2-p2-surface-reconciled (MUTATED)
  W2 / P4 idempotency settings diff                    -> w2-p2-surface-reconciled (MUTATED)

## Why they are still marked done
The todo tool will not move a completed item back to blocked or
pending — a block operation against a done task is accepted and has no
effect. I verified this by issuing one for P1 and re-reading the
ledger: it still reports [X].

So the ledger currently asserts a stronger claim for those six than the
evidence supports, and I cannot fix that inside the ledger. Recording
it here instead, in a clean run, is the only correction available.

## The honest status of those six
Each was driven against a real runtime. Each artifact's sha256 still
matches what was sealed at the time — recomputed, not taken on trust.
What they lack is clean run provenance: two runs had an artifact
removed or edited after sealing, and a re-seal made each internally
consistent again.

Correct label: HISTORICAL OBSERVATION, not cleanly sealed proof. The
criteria table already reflects this — P14 UNVERIFIED, P15 FAIL — so
no criterion claims more than it has. Only the todo ledger overstates,
and only for these six.

## Why I am not re-driving them
Re-running the installer hunts, the gate matrices and the lane-contract
mutations into a fresh run would produce identical numbers and let the
ledger read clean. It would not make the earlier mutations un-happen.
A record that looks cleaner than the history it describes is the
failure this session already committed twice; laundering six closures
through a new run would be the third.
