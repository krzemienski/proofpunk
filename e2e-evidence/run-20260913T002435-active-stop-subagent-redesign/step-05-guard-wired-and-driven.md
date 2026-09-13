# Step 5 - The guard wired, and the ordering bug it exposed

## What was driven
The REAL hooks/stop-guard.sh, invoked as Claude Code invokes it: hook
JSON on stdin, decision JSON on stdout. Real tracker files, real
transcripts, isolated temp cwds. No mocks.

## The bug my first wiring shipped
I placed the liveness check inside the else branch, after the
claim/proof/scout gates. Driving it exposed the flaw immediately:

  AC1 live child, Stop     -> BLOCKED, reason 'claimed without evidence'
  AC1 live child, no claim -> BLOCKED, reason 'subagents still running'

Same live child, two different reasons. With a completion claim the
claim gate fired first and the liveness check was NEVER REACHED. The
session was held for the wrong reason and the running child was never
mentioned -- exactly the case the user reported.

A block is not a pass. Both arms blocked; only one blocked correctly.
Asserting on rc alone would have hidden this.

## The fix
Liveness now runs BEFORE the claim gates (stop-guard.sh:250-287,
claim gate at 289). It asks a question that does not depend on whether
the model said 'done', so it cannot sit behind a gate that does.

## Result after the move: GUARD FAILS: 0

  AC1 live child + claim        BLOCK  'background subagents are still running'
  AC1 live child, no claim      BLOCK  'background subagents are still running'
  nested grandchild live        BLOCK  'background subagents are still running'
  AC2 all completed             not blocked on subagent grounds
  AC3 leaked 257h child         not blocked on subagent grounds
  no tracker at all             not blocked on subagent grounds
  AC4 SubagentStop + live sibling  NOT held for subagents

## Why SubagentStop is exempt, and proof the exemption is real
SubagentStop fires when a CHILD stops. Holding that child because its
siblings are busy would deadlock the very work the session waits for.

Mutation-tested rather than asserted: removing the bypass
(event != 'SubagentStop') drives GUARD FAILS: 1, with the SubagentStop
case blocking on 'subagents are still running' -- the deadlock. Restoring
it returns 0.

## Regression
Full harness after wiring: HOOK TEST FAILS: 0.
