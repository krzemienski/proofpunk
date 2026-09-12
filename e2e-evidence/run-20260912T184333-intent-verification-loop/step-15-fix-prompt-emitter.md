# C5: the fix prompt is emitted from recorded state, not written by hand

## What was missing
Stage 8 step 6 said 'write the next-session fix prompt'. Nothing
generated it. The one artifact that carries the goal across a restart
was a freehand paraphrase by the same model that just failed to meet
the goal -- the exact drift the original-intent rule exists to stop.
The verdict file already had a next_prompt field, stored and carried
forward across restarts, pointing at a file nothing ever wrote.

## What now exists
intent_verdict.py fix-prompt composes from the verdict file: original
intent reproduced VERBATIM, gaps taken from the recorded unmet clauses,
attempt number and cap stated so the next session knows its budget.
With --out it writes the file and points next_prompt at it, so the
next session finds the prompt without being told where it is.

## Driven, isolated HOME
```
  UNMET with 2 gaps             rc=0  intent verbatim YES, both gaps YES
  next_prompt now points at it  YES
  MET refuses to emit           rc=2  (would invent work)
  no verdict at all             rc=2
  UNMET but no intent stored    rc=2  (cannot carry a goal it never had)
  UNVERIFIABLE, no gaps         rc=0  emits, says 're-derive from the
                                      original request' rather than
                                      fabricating gaps
```

## A defect an advisory caught
save() has always been atomic (mkstemp + os.replace). My --out write
was a plain write_text. A truncated fix prompt still PARSES as a fix
prompt, so an interrupted write would hand the next session a goal cut
off mid-sentence, silently. Now the same mkstemp + os.replace as save.
Re-driven: nested dir created, zero stray temp files, unwritable target
refused cleanly at rc=2.

## What this does NOT do
Stage 8 is PROSE. It instructs the model to call fix-prompt on UNMET,
to read the whole session, and to use sequential thinking. None of
those are enforced by anything -- no runner invokes the emitter, and no
hook can tell a real full-session review from a skim that recorded the
same verdict.

The stop guard enforces PROCEDURE (is there a verdict, what does it
say). It cannot enforce JUDGMENT QUALITY. So the honest scope is:
  - emitter behaviour: PROVEN, 6 cases
  - Stage 8 calls it:  INSTRUCTED, not enforced
C5 stays open until a run actually invokes it on UNMET and restarts
from the artifact it produced.

## Gates
88 PASS / 0 FAIL; counts, citations, orchestration, lane contracts all
rc=0 with the new command in tree.
