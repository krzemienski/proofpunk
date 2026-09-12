# Stage 0 needs a command that CANNOT hold a verdict

## The bug that forced this
Stage 0 runs at the start of every attempt, restarts included. Using
`record` there is unsafe however careful the merge rules are, because
record takes a --verdict and can therefore always overwrite the previous
attempt's judgment. Measured:
```
  after UNMET:  verdict=UNMET attempt=1 unmet=['clause Y missing'] next='.prompts/fix.md'
  Stage 0 re-record:
  after:        verdict=UNVERIFIABLE attempt=1 unmet=[] next=''
```
The restarted run was told to fix something and no longer knew what.

## capture: initialize-if-absent by construction
It cannot express a verdict, so it cannot destroy one. Driven:

```
1. fresh capture
   captured original intent for ev-15248-50378
    verdict=UNVERIFIABLE attempt=0 unmet=[] next='' intent='THE ORIGINAL ASK'
2. repeated capture with a PARAPHRASE -- must not win
   intent already captured for ev-15248-50378; unchanged
    verdict=UNVERIFIABLE attempt=0 unmet=[] next='' intent='THE ORIGINAL ASK'
3. record UNMET, then Stage 0 capture again
    verdict=UNMET attempt=1 unmet=['clause Y missing'] next='.prompts/fix.md' intent='THE ORIGINAL ASK'
   intent already captured for ev-15248-50378; unchanged
    verdict=UNMET attempt=1 unmet=['clause Y missing'] next='.prompts/fix.md' intent='THE ORIGINAL ASK'
   may-stop rc=2 (still blocks)
```

## Failure cases
```
  spent cap: attempt=3 -> after capture attempt=3   (capture cannot buy attempts)
  corrupt state: rc=1 -- refusing to capture over unreadable state at /Users/nick/.proo
                 file intact: not json{{{
  missing id:    rc=1 -- capture needs --session-id (or $PROOFPUNK_SESSION_ID): wit
```

The corrupt case matters: load() flattens an unparseable file to {},
so without an explicit existence check capture would treat it as absent
and overwrite it -- destroying a verdict, possibly one holding a spent
cap. It now refuses and says why.

## Attempt counting
Only UNMET increments. Stage 0's UNVERIFIABLE previously burned one, so
the cap tripped after TWO real failures. Fresh session, measured:
  stage0 attempt=0 rc=2 | f1 attempt=1 rc=2 | f2 attempt=2 rc=2 | f3 attempt=3 rc=0

## Gates
  verify-orchestration     rc=0
  verify-counts            rc=0
  verify-citations         rc=0
  verify-lane-contracts    rc=0
  test-hooks               rc=0

verify-orchestration passing matters here: Stage 8 was added to
implement/SKILL.md, and that gate requires literal '## Stage N'
headings in ascending order.
