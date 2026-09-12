# e180035: discriminating before/after for the harness fixture

Cited only step-15, which shows the repaired harness green. Same
objection as c2e4734: a green with no failing arm cannot distinguish
'the fixture was fixed' from 'it was never broken'.

The defect: c169831 made validate refuse artifacts <= 1024 bytes.
test-installer.sh group 9 built its 'clean sealed' artifact with
'echo PASSED' (7 bytes), so the newly-correct validator refused it and
the group reported contract drift.

Both arms run the REAL harness from a clone, with the validator held at
the fixed version so the only variable is the fixture.

## BEFORE — stale fixture — c169831
  group 9 builds its clean artifact with: echo PASSED
  sh tools/test-installer.sh unpiped rc=1
    INSTALLER TEST FAILS: 1

## AFTER — repaired fixture — e180035
  group 9 builds its clean artifact with: echo PASSED
  sh tools/test-installer.sh unpiped rc=0
      PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
    INSTALLER TEST FAILS: 0

## Verdict
Same validator in both arms; only the fixture differs. BEFORE fails,
AFTER passes, and the failing arm names the exact drift the commit
fixed. Driven, not merely cited.
