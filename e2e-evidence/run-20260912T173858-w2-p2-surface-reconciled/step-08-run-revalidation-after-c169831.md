# Re-validation of every run in this session under the stricter rule

Commit c169831 made validate refuse artifacts <= 1024 bytes. Any
'validate OK' printed BEFORE that commit was produced by the weaker
tool and cannot support a verdict. Both runs are therefore re-validated
by the current tool, unpiped.

## run-20260912T172922-w2-installer-p1p2p4 (the W1 hook-fix run)
```
$ python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py validate
THIN: e2e-evidence/run-20260912T172922-w2-installer-p1p2p4/step-05-p4-idempotency-verdict.md (903 bytes, needs > 1024) — too small to carry a claim; re-capture with its command, rc, and surrounding state (evidence-contract.md rule 3)
THIN: e2e-evidence/run-20260912T172922-w2-installer-p1p2p4/step-10-case5b-mutation-proof.log (996 bytes, needs > 1024) — too small to carry a claim; re-capture with its command, rc, and surrounding state (evidence-contract.md rule 3)
validate FAIL: 2 issues
unpiped rc=2
```
Status: INVALID under the current rule. Two artifacts are below the
threshold. Its four load-bearing artifacts (step-06 defect, step-07 fix
proof, step-08/11 gates, step-09 Linux parity) are all above the
threshold and remain readable, but the RUN as a whole no longer
validates, so verdicts are not cited from it.

## run-20260912T173858-w2-p2-surface-reconciled (the current run)
```
$ python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py validate
validate OK: e2e-evidence/run-20260912T173858-w2-p2-surface-reconciled
unpiped rc=0
```
Status: VALID. Carries the re-captured P4 verdict (step-04) and the
re-captured mutation proof (step-05), which is precisely why they were
re-captured rather than left behind in the invalidated run.

## Consequence for the criteria table
P1, P2, P4 are cited from this run only. The hook-fix defect and fix
proof live in the older run; they are re-driven into this run before
any P8 verdict is claimed, rather than cited across an invalid seal.
