# UNMET blocks the stop. My first drive said otherwise and was wrong.

## The false alarm
Driving stop-guard.sh at HEAD with real payloads, all three arms
returned rc=0 -- including the UNMET case that must block:
```
  UNMET session      rc=0 <- LEAKED
  MET session        rc=0 <- allowed (control)
  no verdict at all  rc=0 <- blocked
```
That reading was doubly wrong. The guard signals a block on STDOUT,
not via exit code, so rc=0 says nothing either way -- my own control
line called rc=0 'blocked' on one row and 'LEAKED' on another.

## Root cause: my payload, not the guard
The intent gate is reached only when a session CLAIMS completion. The
harness supplies a transcript carrying that claim (tools/test-hooks.sh
lines 760-773). My payload had no transcript_path at all, so the guard
returned before the gate was ever consulted. I measured a code path
that does not contain the feature.

tools/test-hooks.sh:756 warns about exactly this -- the proof path must
be a real file under an evidence dir or an earlier branch fires first.
I had read that line and still built the payload wrong.

## Re-drive with the claim present
```
  UNMET      BLOCKED, names the gap
  MET        allowed silently (control)
  no verdict BLOCKED
```
The UNMET arm surfaced its own reason text -- 'the OpenCode guard was
never written' -- so the block is tied to the recorded verdict rather
than to a generic refusal.

## Why this is recorded rather than dropped
A false alarm about my own feature costs the same disclosure as a real
defect. Had I trusted the first run I would have 'fixed' a guard that
was working, and the fix would have been to loosen it.

This is the third time this task that a bad fixture produced a
confident wrong reading: reused session ids leaking a spent cap, the
key-derivation mismatch, and now a payload missing the precondition.
The pattern is mine -- I build the fixture from memory of the contract
instead of from the driver that already encodes it.
