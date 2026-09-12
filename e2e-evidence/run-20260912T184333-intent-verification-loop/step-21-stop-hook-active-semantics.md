# stop_hook_active: verified against the runtime, with a residual risk

## Why this was challenged
My guard returns early when event.stop_hook_active is true. An
advisory asked whether that flag really marks an already-authorized
continuation, or merely 'a hook is active' -- in which case the escape
would let an UNMET session settle unchecked.

I had asserted the semantics from the field NAME and my own comment.
The SDK type carries no doc comment on it (shared-events.d.ts:90), so
that was inference, not evidence.

## Traced to the runtime
agent-session.ts, the only writes to the backing field:
```
  807   #sessionStopHookActive = false            initial
  4073  #sessionStopHookActive = false            reset with continuation state
  4148  #sessionStopContinuationCount++
  4149  #sessionStopHookActive = true             set AFTER a continuation
  4128  stop_hook_active: this.#sessionStopHookActive   emitted on the event
```
Line 4149 fires only on the path that has just decided to force a
continuation (4148 increments the counter immediately before). It is
reset at 4073 whenever that state clears.

So the flag means: THIS settle pass follows a continuation that was
already forced. The early return is correct -- without it, a
continue:true would re-enter its own handler.

## The residual risk the advisory correctly identified
Because the re-fired pass is not re-gated, an UNMET session can settle
on the turn AFTER a forced continuation. The gate fires once per
continuation, not until intent is met.

This is a deliberate trade, and worth naming rather than hiding:
  - re-gate every pass  -> the guard fights the runtime until
    SESSION_STOP_CONTINUATION_CAP (agent-session.ts:4140) stops it,
    burning 8 forced turns to reach the same place
  - escape once         -> one forced continuation carrying the reason,
    then the session may settle

The runtime already bounds this: line 4140 caps continuations and logs
'session_stop continuation cap reached'. Fighting it would produce a
worse failure mode than the one being prevented.

The honest statement is therefore NOT 'an unmet session cannot stop on
OMP'. It is: an unmet session is interrupted once, with the unmet
clauses named, and must act on that before it settles. Enforcement is
one forced turn, not an indefinite block.
