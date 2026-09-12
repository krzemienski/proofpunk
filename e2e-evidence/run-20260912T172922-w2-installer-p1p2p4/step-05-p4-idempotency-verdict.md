# P4 — installer idempotency, measured

HOME=/tmp/pp-p2-qW8jVh ; installer run TWICE with identical flags:
  bash tools/proofpunk-install.sh --target claude-code --source local --source-dir $(pwd) --hooks --themes --plugins

## rc
run1 rc=0 (step-02-install-run1-clean-home.log)
run2 rc=0 (step-04-install-run2-idempotency.log)

## settings.json after run1 vs after run2
```
(no differences — byte-identical)
```
diff exit=0 => NO duplicate hook registrations, NO JSON corruption

## registered hook command count, both runs
/tmp/pp-settings-run1.json: 12 registered commands
/tmp/pp-settings-run2.json: 12 registered commands

## second-run skill disposition (collision protection)
SKIP lines: 18
== summary: 0 installed, 0 replaced, 18 skipped (collision), 0 missing ==

## backup-file proliferation check (a second run must not litter)
skill .bak dirs: 0
settings .bak files: 1

VERDICT P4: PASS
