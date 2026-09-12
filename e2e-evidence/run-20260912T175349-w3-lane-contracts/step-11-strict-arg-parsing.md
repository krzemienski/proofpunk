# Strict argument parsing for fresh_evidence.py

The first --run implementation removed only the FIRST occurrence and
ignored surplus positionals, so 'seal junk' ran as 'seal' and
'--run a --run b' silently used a. Tolerating junk in the tool whose
whole job is refusing things is the same defect class as a silent
fail-open.

## Malformed invocations must all refuse
```
  seal junk                              rc=2  seal takes 0 positional argument(s), got 1: ['junk']
  validate junk                          rc=2  validate takes 0 positional argument(s), got 1: ['junk']
  validate --run a --run b               rc=2  --run given more than once
  validate --bogus                       rc=2  unknown option: --bogus
  validate --run (no value)              rc=2  --run requires a run directory
  next-step (no slug)                    rc=2  next-step takes 1 positional argument(s), got 0: []
  next-step a b                          rc=2  next-step takes 1 positional argument(s), got 2: ['a', 'b']
  init-run --run <dir>                   rc=2  init-run creates a run; --run does not apply
  validate --run <nonexistent>           rc=2  no such run directory: e2e-evidence/nope
```

## Valid invocations must still work
```
  validate --run <dir>                 rc=0  (expect 0)
  validate (bare, single run)          rc=0  (expect 0)
  next-step <slug> --run <dir>         rc=0  -> step-02-probe
  next-step --run <dir> <slug>         rc=0  -> step-02-probe
  both orderings identical:            YES
  seal --run <dir>                     rc=0  (expect 0)
  --help                               rc=0  (expect 0)
```
