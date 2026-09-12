# Stage 2 scout: both surfaces, measured against real source

Operator said 'do both'. Before editing either guard I re-derived the
runtime facts from the tree and the installed SDKs, because 5 of 10
scout claims I inherited this session were refuted on contact.

## OpenCode: measured, and my notebook's version was wrong
Notebook said 'session.idle is observe-only (SDK v1.15.13)'. The SDK
actually installed here is @opencode-ai/plugin 1.4.7. The cited
version is not present, so that claim was inherited, not measured.

Measured instead: I read the whole Hooks interface in
~/.config/opencode/node_modules/@opencode-ai/plugin/dist/index.d.ts
lines 170-313. Seventeen hooks. There is NO stop hook, NO idle hook
and NO completion hook of any kind. Every hook returns Promise<void>.
session.idle is not a hook at all -- it is an Event type reachable only
through the generic 'event' handler, which also returns Promise<void>
and therefore cannot block.

The conclusion my notebook asserted is CORRECT, but it was correct by
luck: the version it cited does not exist on this machine.

Only blocking seam in 1.4.7: throw from tool.execute.before. That
enforces at the TOOL boundary, which is a different instant from stop.

## OpenCode plugin as it stands
plugins/proofpunk/opencode/plugin/proofpunk.ts registers
tool.execute.before (destructive commands, secret reads, test-file
writes) and an event handler that logs on session.created. There is no
stop guard of any kind -- not an inert one, simply absent.

## OMP: the claim CANNOT be verified here
extensions/proofpunk.ts:79 does read:
    (_ctx as { session?: unknown }).session ?? {}
confirmed by reading the file, not from memory.

But @oh-my-pi/pi-coding-agent is NOT INSTALLED anywhere reachable:
  ~/.omp/node_modules     absent
  ./node_modules          absent
  package.json deps       none declared

So the ExtensionContext claim -- that .session is absent from the type
-- cannot be checked against real types on this machine. It remains
exactly what it was: an unverified scout claim. The cast compiles
because nothing type-checks this file; tsc has never run on it.

## What this means for 'do both'
OpenCode is actionable: the seam is known and the SDK is present.
OMP is NOT symmetrically actionable. Editing line 79 on the strength
of an unverifiable claim would be the same mistake I have made five
times this session -- writing from memory of a contract instead of
from the artifact that encodes it. The artifact is missing.

## Harness coverage
tools/test-hooks.sh mentions neither file. Zero coverage on both
surfaces; every gate that has passed this session tested the shell
hook only.
