# 'do both': OMP and OpenCode intent gates, measured

## The OMP guard was inert. Proven, not argued.
Installing @oh-my-pi/pi-coding-agent 18.1.18 settled the question my
notebook could only assert. ExtensionContext (types.d.ts:297-389) has
ui, mode, cwd, sessionManager, model, isIdle() -- and NO session.
Run through the guard's own logic:
```
  ctx.session          = undefined
  text the guard sees  = "{}"
  CLAIM matches?       = false
  => would ever block? = false
```
It had never blocked anything. So fixing it is a bug fix on dead code
-- not the behavior change I had been treating as needing approval.

Session data is on the EVENT: SessionStopEvent carries messages,
session_id, stop_hook_active (shared-events.d.ts:83-93). Same logic
reading event.messages blocks correctly.

## OpenCode: 17 hooks, none of them stop
Read the whole Hooks interface in the installed SDK 1.4.7
(dist/index.d.ts:170-313). No stop, idle, or completion hook; every
hook returns Promise<void>. session.idle is an Event, not a hook.
Operator chose both seams: announce at idle, block at tool boundary.

My notebook cited SDK v1.15.13 and pi v17.3.4. Neither version exists
here. The conclusions happened to be right; the citations were not.

## Four defects the advisories caught in my own code
1. Unconditional intent gate -- would have forced a continuation on
   every ordinary clean stop. Scoped to the claim path.
2. No stop_hook_active check -- a continue:true would re-enter itself
   forever. The flag exists on the event; now honored.
3. Inverted fail policy -- my comment said 'only exit 0 authorizes'
   while the code returned allow on spawn failure. Now tagged
   outcomes: allow / unmet / missing-interpreter / unrunnable.
4. Silent fail-open in OpenCode while OMP announced. Same product,
   opposite policies. Both now announce.

## A measurement that reversed my design
I keyed the fail-open case on ENOENT. Measured on Node 22:
```
  "python3-missing-xyz"   code=EACCES  err.path="python3-missing-xyz"
  "/nonexistent/python3"  code=ENOENT  err.path="/nonexistent/python3"
  "python3" (PATH empty)  code=ENOENT  err.path="python3"
```
An errno test BLOCKS the real 'no interpreter' case (EACCES) and
ALLOWS a typo'd path (ENOENT) -- exactly backwards. err.path echoes
the command verbatim in every case, so the gate now compares against
the exact interpreter string it executed.

## Driven: six branches, real helper, isolated HOME
```
  no session id          block=true   fails closed
  MET verdict            block=false  allow
  UNMET verdict          block=true   unmet
  no verdict recorded    block=true   unmet
  bogus interp path      block=true   unrunnable:ENOENT
  python3 absent         block=false  enforcement-OFF-announced
```
An earlier run of this matrix reported no-session-id on four rows
including MET: env vars never reached the node child, so those arms
tested nothing. Fifth bad fixture this session. Re-driven with ids as
argv.

## Gates
  OpenCode tsc (SDK 1.4.7)   exit=0
  OMP tsc (SDK 18.1.18)      exit=0
  counts/citations/orchestration/lane-contracts  rc=0
  test-hooks.sh              88 PASS / 0 FAIL

## Scope, stated plainly
This is branch-level proof of the gate logic plus type-conformance
against both real SDKs. Neither guard has been driven INSIDE its
runtime -- no OMP session has fired session_stop here, no OpenCode
session has hit tool.execute.before. That needs the runtimes
themselves, and the harness still has zero coverage of either file.
