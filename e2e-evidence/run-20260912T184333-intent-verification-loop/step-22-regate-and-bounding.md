# The one-turn escape was a real gap. Closed, with two bounding models.

## What an advisory caught
My OMP guard returned early whenever stop_hook_active was set. I called
it a recursion escape and a reasonable trade. Measured against the
actual request -- 'keep working so that it actually finally implements'
-- it was a functional gap: an UNMET session was interrupted ONCE and
could then settle on the very next pass.

That is not the requested behavior. Removed.

## Two guards, two questions, two policies
The evidence guard does NOT re-fire on a continuation pass: its
question ('is there a cited artifact?') is answered by the same
transcript, so re-asking loops on unchanged input.

The intent gate DOES re-fire: its question ('was the original request
met?') has a changing answer, because the continuation exists so the
session can go meet it.

## The hole that opened, which the same advisory predicted
error: command not found: record
Re-gating alone never terminates. Attempts advance on , not on
error: command not found: may-stop
, so a model that never re-records is held until OMP's own
continuation cap of 8 -- proofpunk's escalation at 3 is never reached.

Driven, and it was exactly that: 6 passes, all CONTINUE, attempt
pinned at 1.

error: command not found: may-stop
Fixed with an opt-in : a block spends an attempt.
```
  before          attempt=1 escalated=no
  pass 1  CONTINUE          attempt=2
  pass 2  CONTINUE          attempt=3
  pass 3  ALLOWED TO SETTLE  attempt=3 escalated=yes
  -> terminated at pass 3, inside the runtime cap of 8
```
Cap is not exceeded on repeat: calls 4-6 stay at attempt=3, rc=0.
error: command not found: may-stop
Plain  still mutates nothing, so the shell guard and status
checks are unaffected (3 calls, attempt stayed 1).

## OpenCode deliberately does NOT consume
An advisory pushed for --consume there too. It fires per TOOL CALL, not
per settle pass -- consuming would spend the whole cap on three
ordinary writes and release the session having never asked it to fix
anything.

Driven to check it is not a wedge instead:
```
  write #1..#5      BLOCKED, attempt stays 1  (cap never spent)
  record MET        write ALLOWED (session freed)
```
The exit is the action the block asks for. Bounded by the session's own
progress rather than by a counter.

## Stated limitation, not claimed parity
The two surfaces enforce at different instants with different bounds:
  OMP       per settle pass, bounded by attempts, escalates at 3
  OpenCode  per tool call, bounded by recording a verdict, no escalation
OpenCode cannot satisfy the bounded-retry contract without a
continuation-scoped consumption mechanism, which its SDK gives no seam
for. That is a known limitation.

## Twelfth bad fixture
The first re-gate drive showed pass 2 settling and I nearly concluded
the edit had failed. The driven copy was STALE -- hash 27c7dde5 against
the repo's e2627a66. I had measured the pre-edit file. Refreshed, the
same drive blocked every pass.

## Gates
  OpenCode tsc 1.4.7  exit=0    OMP tsc 18.1.18  exit=0
  counts/citations/orchestration/lane-contracts  rc=0
  test-hooks.sh  88 PASS / 0 FAIL
