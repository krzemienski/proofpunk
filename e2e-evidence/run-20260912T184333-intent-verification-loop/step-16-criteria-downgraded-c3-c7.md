# I marked C3 and C7 PASS. They are not. Downgraded.

## The inconsistency
My final report graded C3 (whole-session read) and C7 (sequential
thinking) as PASS, while the same report said Stage 8 is 'instruction,
not enforcement' and that no runner invokes it. Both cannot be true.
An advisory caught it.

## Then I nearly defended the wrong grade
I ran a regex over stop-guard.sh for 'whole|entire|all lines|full
session' and it returned YES for 'verifies the WHOLE session was
read'. That was a false positive -- it matched incidental words, not a
whole-session check. Fourth bad fixture this task.

## What the guard actually does
stop-guard.sh:29, in its own header:
```
  Always <50ms, never reads more than the last 40 transcript lines.
```
It reads a WINDOW. Stage 8 requires the whole session precisely
because the gap is usually visible only at the start, where a
four-clause request met a one-clause response. The guard cannot see
there. This is not a bug in the guard -- a stop hook must stay under
50ms -- but it does mean C3 has no enforcement behind it.

For C7 the regex was honest: NO. Nothing checks sequential thinking.
Nothing could; it is a property of how the model reasoned, not an
artifact it leaves behind.

## Corrected grades
```
  C2 intent verified vs original request  PASS (contract-level)
     step-14: UNMET blocks and names its recorded gap. What is proven
     is that a verdict gates the stop -- not that the judgment behind
     that verdict was sound.
  C3 whole-session read       UNVERIFIED  guard reads last 40 lines
  C7 sequential thinking      UNVERIFIED  unobservable to any hook
```

## Why these cannot be closed by more work here
Both are judgment-quality properties. The guard enforces PROCEDURE --
is there a verdict, what does it say. No hook distinguishes a real
full-session review from a skim that recorded the same verdict.
Closing them needs an actual implement session whose transcript shows
the pass being performed, which needs the surfaces resolved first.

## Pattern worth naming
Four times this task a fixture I built produced a confident wrong
reading: reused session ids leaking a spent cap, the key-derivation
mismatch, the payload missing its precondition, and now a regex
matching incidental words. Each time I wrote the check from memory of
the contract instead of from the thing that already encodes it. The
answer was in the file's own header comment.
