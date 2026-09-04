# VERDICT — stop-guard scout-substring false-PASS (L4 / gauge #2)

Date: 2026-09-04T04:35:59Z
Repo HEAD: b4bd03ae32a62f486b40484b0ccf0e0933ab6f27 (working tree dirty — adopted as Phase 5 pre-work per operator)

## Defect
SCOUT_KEYWORD is substring-based and scanned the same text as PATH_SHAPED.
A cited evidence path whose run dir contains 'scout' supplied BOTH conjuncts
by itself, so any citation self-certified as its own scout record.

## Differential arms (only the evidence DIRNAME differs)
  run-2026-plain : blocks WITH and WITHOUT the fix  -> case 23 cannot see the defect
  run-2026-scout : blocks only WITH the fix         -> real false-PASS

## Fix
stop-guard.sh:178  scout_text = PROOF_PATH.sub(" ", text)
Cited evidence paths are masked out before the scout conjunction is tested.

## Mutation proof (harness discriminates)
  baseline  rc=0  PASS=48   (no FAIL)
  mutated   rc=1  PASS=47   FAIL: stop-guard accepted scout-named evidence dir as its own scout record
  restored  rc=0  PASS=48   byte-identical to baseline

## Regression posture
Case 24 added to tools/test-hooks.sh (48 cases). Control arm: genuine scout
prose naming real files is still CREDITED (guard stays silent) — verified.

## Note on provenance
tools/test-hooks.sh changed at 00:32:22, between this session's first
harness run (rc=1, fixture named run-2026-scout) and the fix (00:34).
The rename to run-2026-plain avoided the hazard instead of catching it;
case 24 restores discrimination. Not authored by this session.

PROOF LEVEL: script (harness-level). Not yet proven at a live session surface.
