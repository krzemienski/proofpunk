# step-02 — OMP contract obtained; subagent lifecycle proven ABSENT

## What I drove
Operator said "unblock omp". I obtained the AUTHORITATIVE published type
contract instead of guessing, into an isolated temp dir. No mutation of
~/.omp, ~/.claude, or project dependencies.

    npm view @oh-my-pi/pi-coding-agent version  -> 18.1.19
    omp --version                               -> omp/18.1.19   (EXACT match)
    npm pack @oh-my-pi/pi-coding-agent@18.1.19  -> 3148 files, 1345 .d.ts

## The ExtensionAPI event surface (dist/types/extensibility/extensions/types.d.ts)
44 event literals are accepted by pi.on(), including:

    session_start session_stop session_shutdown before_agent_start
    agent_start agent_end turn_start turn_end tool_call tool_result
    tool_execution_start tool_execution_update tool_execution_end
    tool_approval_requested tool_approval_resolved ...

## Why the tracker still cannot be written (measured, not assumed)

1. agent_start / agent_end are MAIN-LOOP events, not subagent events.
   shared-events.d.ts declares them verbatim:

       export interface AgentStartEvent { type: "agent_start"; }

       export interface AgentEndEvent {
           type: "agent_end";
           messages: AgentMessage[];
           willContinue?: boolean;
       }

   AgentStartEvent carries ONE field: its own type tag. There is no agent id,
   no session id, no child identity. The doc comment says "Fired when an agent
   loop starts (once per user prompt)" — that is the main agent, not a child.

2. A tracker entry REQUIRES a stable agent_id (agent_state.py:98-116 keys
   liveness off per-entry status + started_at). No extension event supplies one
   for a child.

3. The only two child-adjacent strings in the whole extension typings:
     - `subagent` x1 — PROSE inside addAutocompleteProvider docs, listing
       headless modes ("print, RPC, ACP, subagents"). Not an event.
     - `parentSession` x2 — an OPTION to ExtensionCommandContext.newSession().
       A method for creating a session, not a notification that one ran.

## What I SEE
The contract is no longer unknown — it is known, and it says the feature does
not exist. OMP extensions cannot observe subagent spawn or completion, so a
tracker written from this surface could never represent child liveness. Writing
one would fabricate parity.

Contrast with the earlier block reason: that said "contract not on disk"
(unverifiable). This says "contract obtained, feature absent" (measured).

VERDICT: OMP subagent-tracker parity is ARCHITECTURALLY IMPOSSIBLE at
pi-coding-agent 18.1.19. Blocked with proof, not for want of information.
