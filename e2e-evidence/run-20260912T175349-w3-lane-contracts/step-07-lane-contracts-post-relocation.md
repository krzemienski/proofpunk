# Lane contracts — negative mutations re-run AFTER relocation

The mutation suite in step-04 ran while the contracts lived in
.planning/lane-contracts/. They now live in
plugins/proofpunk/lane-contracts/ because .planning is gitignored.
A relocated checker with a changed default path is a different
program until it is re-driven, so the whole suite is repeated here.

## Happy path, new location
```
$ python3 tools/verify-lane-contracts.py   # default dir now plugins/proofpunk/lane-contracts
  PASS  lane-01-hooks.contract.yml
  PASS  lane-02-evidence.contract.yml

LANE CONTRACTS: 2 checked, 0 error(s)
  files under lane ownership: 12
unpiped rc=0
```

## Negative mutations, re-run against the relocated tree
  M1 dangling acquire_digest                           rc=1  correctly FAILS
        ERROR: lane-01-hooks.contract.yml: acquire_digest does not resolve: .planning/nope.md
  M2 invented validation_runbook                       rc=1  correctly FAILS
        ERROR: lane-01-hooks.contract.yml: validation_runbook does not resolve: plugins/proofpunk/references/fake-validation.md
  M3 owns matching nothing                             rc=1  correctly FAILS
        ERROR: lane-01-hooks.contract.yml: owns `plugins/proofpunk/ghost/*.sh` matches no file in the tree
  M4 binding field deleted                             rc=1  correctly FAILS
        ERROR: lane-02-evidence.contract.yml: missing binding field `acquire_digest`
  M5 overlapping ownership                             rc=1  correctly FAILS
        ERROR: lane-02-evidence.contract.yml: lane `evidence` and lane `hooks` both claim plugins/proofpunk/hooks/stop-guard.sh — overlapping ownership
  M6 empty contract directory                          rc=1  correctly FAILS
      no *.contract.yml files in /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.rUaH7H8v6f/none

## Fallback parser parity (PyYAML absent)
The checker prefers PyYAML and falls back to a dependency-free reader so
it can run in the bare containers the gates run in. Both paths must
agree, or the checker's verdict depends on what happens to be installed.
```
$ docker run --rm -v $(pwd):/w -w /w python:3.12-slim python3 -c 'import yaml' ; echo pyyaml present?
PyYAML ABSENT — fallback parser will be used

$ docker run --rm ... python3 tools/verify-lane-contracts.py
  PASS  lane-01-hooks.contract.yml
  PASS  lane-02-evidence.contract.yml

LANE CONTRACTS: 2 checked, 0 error(s)
  files under lane ownership: 12
unpiped rc=0
```

## Installed-layout check
Lane contracts are NOT copied by the installer — they are orchestrator
inputs consumed from a repo checkout, not per-skill runtime files.
Confirmed against a real install:
  installer rc=0
  lane-contract files in the installed tree: 0  (expected 0)
