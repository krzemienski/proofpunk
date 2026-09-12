# Case 5b non-vacuity — mutation drive, re-captured with full context

Supersedes step-10 of run-20260912T172922-w2-installer-p1p2p4 (996 bytes,
refused by the stricter min-size rule). Same experiment, full output.

A regression test that cannot fail proves nothing. Case 5b is therefore
run against two trees: the fixed one, and a scratch copy with the fix
surgically reverted. It is load-bearing only if the first passes and the
second fails.

## Arm A — current tree (fix present)
```
$ bash tools/test-hooks.sh
unpiped rc=0
  PASS: no-test-files.sh announces enforcement loss without python3
  PASS: evidence-guard.sh announces enforcement loss without python3
  PASS: capture-guard.sh announces enforcement loss without python3
HOOK TEST FAILS: 0
```

## Arm B — scratch copy, notice line deleted from all three guards
mutation applied to 3 hooks — the stderr notice removed, bare 'exit 0' restored
verify the mutation is real:
  no-test-files.sh notice lines after mutation: 0
  evidence-guard.sh notice lines after mutation: 0
  capture-guard.sh notice lines after mutation: 0
```
$ (cd $MUT && bash tools/test-hooks.sh)
unpiped rc=3
  FAIL: no-test-files.sh fails open SILENTLY without python3 — lost enforcement is invisible
  FAIL: evidence-guard.sh fails open SILENTLY without python3 — lost enforcement is invisible
  FAIL: capture-guard.sh fails open SILENTLY without python3 — lost enforcement is invisible
HOOK TEST FAILS: 3
```

Arm A rc=0 with 3 PASS lines; Arm B rc=3 with 3 FAIL lines naming the
exact defect. Case 5b can fail, and fails for the right reason.

Each arm also self-checks its payload: the test first asserts the payload
denies (rc=2) with python3 present, so the python3-absent arm can never
pass on a payload that was never going to deny.
