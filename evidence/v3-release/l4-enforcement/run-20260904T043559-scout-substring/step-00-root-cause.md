# stop-guard false-PASS: scout keyword matches inside cited evidence path

Date: 2026-09-04T04:31:20Z
Tree: HEAD=9963648bd6be74c4738c65be8730b910cde9a3f9 DIRTY=yes (18 files)

## Differential arms (only the evidence DIRNAME differs)
ARM a: cited path e2e-evidence/run-2026-scout/step-05.png  -> silent (no block)
ARM b: cited path e2e-evidence/run-2026-plain/step-05.png  -> BLOCKS on missing scout

Prose is byte-identical in both arms. The guard credits a scout record
because the substring 'scout' appears in the FILENAME, not the prose.

## Mechanism
stop-guard.sh:63  SCOUT_KEYWORD = re.compile(r'(scout|context summary|...)', re.I)
  -> no word boundary, no exclusion of PROOF_PATH tokens.
stop-guard.sh:71  PATH_SHAPED now requires an extension, so the real
  scout prose line ('touchpoints in the checkout module') correctly fails
  the conjunction. The CITATION line then supplies 'scout' by itself.

## Consequence
Any run whose evidence directory is named *scout* self-certifies its own
scout record. This is a FALSE-PASS in the proof-of-work guard (gauge #2).
Detected by tools/test-hooks.sh case 23 -> HOOK TEST FAILS: 1
