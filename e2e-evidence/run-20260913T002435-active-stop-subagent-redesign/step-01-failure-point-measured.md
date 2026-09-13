# Step 1 - The exact failure point, measured

## What the user reports
The main thread may stop while subagents are still running in the
background, because the stop hook lacks semantics to tell 'idle and
done' from 'idle while children work'.

## Root cause (PROVEN, three independent confirmations)

1. hooks.json wires ONE script to TWO different events:
     Stop         -> hooks/stop-guard.sh   (timeout 10)
     SubagentStop -> hooks/stop-guard.sh   (timeout 10)
   plugins/proofpunk/hooks/hooks.json:16-37

2. The script cannot tell them apart. It extracts hook_event_name at
   stop-guard.sh:71 and uses it in ZERO conditionals (measured: 1
   reference, 0 in a conditional). Both events take one code path.

3. This is DOCUMENTED AS INTENDED, not an oversight:
     docs/hooks-and-init-design.md:33
     | SubagentStop | (none) | stop-guard.sh | same check, subagent transcript |

## Why that produces the reported bug
A subagent finishing is graded by MAIN-THREAD completion rules. A
subagent is not required to report completion to the main thread, so
its transcript legitimately lacks a proof citation -- and the guard
treats that as an unproven claim.

Symmetrically, the Stop event knows nothing about children: no hook
matcher anywhere in hooks.json matches the Task tool (measured false),
so a subagent SPAWN is never observed.

## The missing state
There is no tracker. Searched all of plugins/proofpunk for any
agent-state/lock/running-agents file reference: 0 hits.

The guard's whole input is: last 40 lines of one transcript
(stop-guard.sh:134), plus session_id and cwd. Nothing in that input
can answer 'are children still running?'

## Consequence for the design
Distinguishing the four requested states requires information the stop
payload does not carry. Either a runtime field exposes child state
(unproven so far), or state must be tracked out of band. That
observability question is the gate on the whole redesign; a scout is
resolving it now.
