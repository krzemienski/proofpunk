# Both guards driven through their REAL registered handlers

## What was driven
Imported each plugin module and invoked the handlers the runtime
registers -- not a reimplementation of their logic. The OpenCode plugin
was laid out as it installs (plugin at opencode/plugin/, helper
reachable via ../../skills) so the shipped relative path is what
resolved.

## tool.execute.before, real handler
```
  write + UNMET verdict     THREW, naming the unmet intent
  write + MET verdict       ALLOWED
  read  + UNMET             ALLOWED (read-only, changes nothing)
```

## event handler, real handler
```
  session.created           info log emitted
  session.idle x2 (UNMET)   warn logged ONCE -- dedup works
```

## The bypass an advisory would not let go of, and was right about
My first version exempted the whole bash tool, so an unmet session
could work indefinitely through it. Driving it confirmed the hole:
bash + UNMET was ALLOWED.

Fixed by gating bash per-COMMAND instead of per-tool. Only a command
that is actually resolving the verdict is exempt:
```
  bash: intent_verdict.py record    ALLOWED
  bash: fresh_evidence.py seal      ALLOWED
  bash: npm run build && deploy     BLOCKED
  write: mutation                   BLOCKED
```

## Then the decoy attack, also an advisory's catch
A bare substring test would exempt any command CONTAINING the token.
Anchored to the command head and rejected shell chaining. Driven:
```
  npm run deploy && echo intent_verdict.py   BLOCKED
  npm run deploy # intent_verdict.py         BLOCKED
  cat e2e-evidence/x | sh                    BLOCKED
  echo hi; python3 intent_verdict.py         BLOCKED
  $(intent_verdict.py) && npm publish        BLOCKED
  env X=1 python3 intent_verdict.py record   BLOCKED
  sudo python3 intent_verdict.py record      BLOCKED
  python3 .../intent_verdict.py record       ALLOWED
  python3 .../fresh_evidence.py seal         ALLOWED
```
Seven decoys blocked, two genuine resolvers allowed.

## Two fixture errors, disclosed not buried
1. First drive had the helper outside the plugin's ../../skills reach,
   so write+MET threw 'helper is missing'. That failure was my layout,
   not the product -- though it did prove the fail-closed path fires.
   Re-driven with the install layout: write+MET ALLOWED.
2. A decoy command contained a real destructive string, and
   proofpunk's OWN destructive-pattern guard blocked it before the
   intent gate could be reached. The product defended itself against
   my test. Decoys rewritten without destructive strings.

Sixth and seventh bad fixtures this session.

## Typechecks
  OpenCode plugin vs real SDK 1.4.7    tsc exit=0
  OMP extension vs real SDK 18.1.18    tsc exit=0

## Scope
The handlers are driven directly, which is stronger than the helper
matrix but still not a live runtime: no OMP process fired
session_stop, no OpenCode process called these hooks. The harness has
zero coverage of either file, so nothing re-checks this on the next
change.
