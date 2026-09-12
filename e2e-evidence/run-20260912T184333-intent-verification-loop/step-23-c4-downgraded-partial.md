# C4 said 'all three surfaces block'. That overclaims. Downgraded.

## The overclaim
I graded C4 PASS as 'all three surfaces block'. An advisory caught
that the wording implies STOP-TIME enforcement on all three. OpenCode
cannot do that -- it has no stop hook, which my own source comment says
in as many words. step-19 proves tool-boundary blocking, not stop
blocking.

Two different things were being graded under one label.

## What each surface actually enforces
```
  Claude Code   STOP time    blocks the stop itself
                             (Stop hook, decision:block)
  OMP           STOP time    forces a continuation at settle
                             (session_stop -> continue:true)
  OpenCode      TOOL time    throws on the next mutating tool call
                             (no stop hook exists in SDK 1.4.7)
```

## Corrected grade
C4 as written ('all three surfaces block' = at stop): PARTIAL.
  2 of 3 enforce at stop. The third enforces at the only seam its
  runtime provides.

The criterion that IS fully met is a different sentence:
  'every surface enforces the intent gate at its available seam' -- PASS.

I am not renaming the criterion to make it pass. The original wording
is what was approved, so it is graded as written and the achievable
version is stated beside it.

## Why this matters beyond bookkeeping
The two seams have genuinely different force. A stop-time block
prevents the session from ending. A tool-time block lets it end -- it
only interrupts the next action. An OpenCode session that claims
completion and simply stops is NOT caught.

That is a real coverage hole, not a labeling nuance, and it is the
honest reason C4 cannot be PASS as written.

## Unchanged
C1, C3, C5, C7 stay UNVERIFIED. Surface drives prove the guards fire;
they say nothing about whether an implement run invokes capture, does
a whole-session sequential review, or consumes a fix prompt.
