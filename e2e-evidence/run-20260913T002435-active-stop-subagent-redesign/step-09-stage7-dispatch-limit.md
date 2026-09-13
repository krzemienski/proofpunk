# Step 9 - What 'Stage 7 dispatch' can and cannot be proven

## The challenge
An advisory asked for an end-to-end trace showing a real
/proofpunk:implement session DISPATCHING Stage 7, arguing that driving
the documented command by hand does not prove the integration.

That is a fair distinction. I checked whether such a trace is even
possible.

## Measured: there is no dispatcher to trace

  files in skills/implement: 2
    SKILL.md
    references/execution-loop.md
  executable dispatchers: 0

  commands/implement.md exists: True
  is markdown prose (no code): True

proofpunk skills are MARKDOWN READ BY A MODEL. There is no interpreter,
no scheduler, no process that 'runs Stage 7'. The stages execute because
a model reads the skill and follows it.

## Consequence for the grade
'A real implement run dispatched Stage 7' is not UNPROVEN pending more
work -- it is UNVERIFIABLE BY CONSTRUCTION with any tool available here.
There is no artifact a dispatch would leave behind, because there is no
dispatcher.

What IS proven, and how:
  - the command in Stage 7 runs and produces the documented artifact at
    the documented path (step-08, rc=0, 1123 bytes)
  - its rc=2 branch withholds the artifact (step-08, artifact absent)
  - the calls-table edge implement -> completion-summary is registered
    and verify-orchestration checks it in both directions (rc=0)

What is NOT proven:
  - that a model, reading Stage 7 in a live session, actually issues the
    call. That depends on model behaviour, not on this repo's code.

## Why I am not calling this PASS
The honest grade is UNVERIFIABLE-BY-CONSTRUCTION. Marking it PASS on the
strength of a hand-driven command would be exactly the substitution this
plugin exists to prevent: proving the mechanism works, then claiming the
integration fires.

The same limit already applies to Stage 0 and Stage 8 of implement, which
the prior session graded UNVERIFIED for this identical reason. This is
consistent with that grading, not a new exception.
