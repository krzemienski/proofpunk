# step-15 — OMP extension driven, not just loaded

## What changed
The harness previously asserted only that the OMP module loads and exports a
function, printing UNCOVERED for behaviour. It now drives the real handlers:
17 behavioural assertions, 36 total across both integrations.

## Why this is production code, not a stub
The extension registers handlers against an ExtensionAPI. A recorder that
implements `setLabel`/`on`/`registerCommand` CAPTURES the real handler
functions; invoking one runs the shipped code exactly as the runtime invokes
it. Nothing is reimplemented.

## Payloads match the published contract
Fixtures were incomplete on the first pass (`{toolName, input}` only).
Corrected against pi-coding-agent 18.1.19's own typings:

    interface ToolCallEventBase { type: "tool_call"; toolCallId: string; }
    export interface BashToolCallEvent extends ToolCallEventBase {
        toolName: "bash"; input: BashToolInput; }

so every tool_call fixture now carries type + toolCallId + toolName + input,
and the session events carry their type tags and turn_id.

A grep for `toolName` in shared-events.d.ts returns ZERO, which briefly looked
like proof the field does not exist. It does — the discriminated union lives in
extensions/types.d.ts. Searching one file and concluding absence was my error.

## Mutation-proven: the assertions are load-bearing

    secret guard disabled        -> caught  (FAIL: denies reading a .env secret)
    destructive patterns emptied -> caught  (FAIL: rm -rf, force-push)
    test-file guard disabled     -> caught  (FAIL: denies writing a test file)

    source restored byte-exact: True

An earlier attempt reported the secret mutation as NOT caught. That mutation
was vacuous: it INSERTED an alternative (`__NEVERMATCH__|`) into the regex
instead of removing the matching ones, so `.env` still matched. The assertion
was fine; the mutation proved nothing. Replacing the whole pattern catches it.

## Full run
OpenCode plugin (opencode/plugin/proofpunk.ts)
  PASS  exports a Proofpunk factory
  PASS  registers tool.execute.before
  PASS  registers an event handler
  PASS  denies rm -rf against home
  PASS  denies writing a test file
  PASS  UNMET: denies an ordinary source write
  PASS  UNMET: denies an ordinary bash command
  PASS  UNMET: still allows a read-only tool (session can inspect)
  PASS  UNMET: still allows the resolver command (session can unwedge)
  PASS  UNMET: resolver exemption resists shell chaining
  PASS  MET: allows an ordinary source write
  PASS  MET: allows an ordinary bash command
  PASS  MET: still denies a destructive command
  PASS  MET: still denies writing a test file
  PASS  session.idle is observe-only (never throws)
  PASS  session.created is observe-only (never throws)
  PASS  session.created announced via client.app.log

OMP extension (extensions/proofpunk.ts)
  PASS  module loads under bun
  PASS  default export is the extension factory
  PASS  sets a label at load
  PASS  subscribes to session_start
  PASS  subscribes to tool_call
  PASS  subscribes to session_stop
  PASS  registers the proofpunk command
  PASS  tool_call denies rm -rf against home
  PASS  tool_call denies a force-push to main
  PASS  tool_call denies reading a .env secret
  PASS  tool_call denies writing a test file
  PASS  tool_call allows an ordinary bash command
  PASS  tool_call allows an ordinary source write
  PASS  tool_call allows reading an ordinary file
  PASS  session_start returns no decision
  PASS  session_start notifies the operator
  PASS  session_stop holds a completion claim carrying no evidence
  PASS  evidence guard does not re-fire on a continuation pass
  PASS  session_stop ignores a turn that claimed nothing
  UNCOVERED  subagent lifecycle — pi-coding-agent 18.1.19 emits no
             child-identity event, so there is nothing to fire

INTEGRATION TEST PASSES: 36
INTEGRATION TEST FAILS: 0


## Still UNCOVERED, by construction
Subagent lifecycle. pi-coding-agent 18.1.19 emits no event carrying a child
agent identity, so there is nothing to fire. The harness prints this rather
than omitting it.

VERDICT: PASS — the OMP extension is driven end to end for every event it
actually receives, with mutation proof that the guards are real.
