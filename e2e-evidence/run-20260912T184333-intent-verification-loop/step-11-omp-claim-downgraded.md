# Downgrading my own OMP claim: contract-level UNVERIFIED, not proven

step-10 says the OMP guard 'has never blocked anything'. That overstates
what I measured, and the overstatement is exactly the kind this session
has caught four times already.

## What my probe actually proved
I reproduced the handler's extraction and ran it against two contexts I
constructed myself:
```
  ctx WITHOUT .session  -> text="{}"  claim=false  wouldContinue=false
  ctx WITH .session     -> claim=true             wouldContinue=true
```
That is a proof about the LOGIC, conditional on the context shape. It
is not a proof about the SHIPPED runtime, because I fabricated both
contexts. If OMP does attach an undocumented .session at runtime, the
guard works and my probe says nothing about it.

## Where the premise came from
ScoutRuntimes, citing installed sources I cannot execute here:
  - ExtensionContext has cwd/sessionManager/exec, no session
    (pi v17.3.4 runner.ts:956-978)
  - the session_stop EVENT carries messages[], turn_id,
    last_assistant_message, session_id, session_file, stop_hook_active,
    signal (shared-events.ts:96-107)
  - SESSION_STOP_CONTINUATION_CAP = 8 (agent-session.ts:347), enforced
    at :3418-3444

I verified none of those line references myself. The package is not
installed in this tree:
```
  ls: cannot access 'node_modules/@oh-my-pi': No such file or directory
  package.json dependencies: {}
```

## Corrected classification
  OMP guard behaviour: CONTRACT-LEVEL UNVERIFIED.
  The code casts to a property that a cited source says does not exist.
  Whether it is inert in production requires driving the real runtime or
  an official fixture, and I have neither.

## What IS independently verifiable from this repo
  1. The cast is real and unguarded (extensions/proofpunk.ts:78-80).
  2. `JSON.stringify(undefined ?? {})` is "{}" — language semantics,
     not a runtime claim.
  3. The harness has ZERO coverage of the OMP extension:
     extensions/proofpunk.ts references: 0
     session_stop references:           0
  So if it IS inert, nothing in this repo would ever report it.

That third point stands on its own and is the actionable finding:
a shipped guard with no test, reading a property whose existence is
disputed, is untrustworthy regardless of which way the dispute lands.
