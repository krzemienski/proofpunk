# --run targeting: the fix, driven

## The defect
fresh_evidence.py resolved its target as the most recently MODIFIED
run-* directory. With two runs on the same mtime that is a tie, broken
arbitrarily. My own verification loop hit it: touching three runs in
sequence put all three in the same second, so all three validations
targeted one directory and a genuinely failing run reported rc=0.

## Reproduction — tied mtimes, no --run
```
  alpha: one 1200-byte artifact  (must validate rc=0)
  beta:  one 50-byte artifact    (must validate rc=2)
  both directories touched to the same second:
    14:07:05 e2e-evidence/run-20260912T180705-alpha
    14:07:05 e2e-evidence/run-20260912T180705-beta
```

### Without --run (ambiguous):
  unpiped rc=0  <- whichever run won the tie, not a chosen one

### With --run (unambiguous):
  validate --run <alpha, good>  unpiped rc=0   (expect 0)
  validate --run <beta, thin>   unpiped rc=2   (expect 2)

## Refusals
  --run <nonexistent>        rc=2  no such run directory: e2e-evidence/does-not-exist
  --run <not named run-*>    rc=2  not a run directory (must be named run-*): e2e-evidence/not-a-run
  --run with no value        rc=2  --run requires a run directory
  init-run --run <dir>       rc=2  init-run creates a run; --run does not apply

## Flag position is not significant
  next-step <slug> --run <dir> -> e2e-evidence/run-20260912T180705-alpha/step-02-probe
  next-step --run <dir> <slug> -> e2e-evidence/run-20260912T180705-alpha/step-02-probe
  identical: YES

## Unchanged semantics without the flag
  newest run is gamma; bare next-step -> e2e-evidence/run-20260912T180705-gamma/step-01-later
  targets gamma: YES
