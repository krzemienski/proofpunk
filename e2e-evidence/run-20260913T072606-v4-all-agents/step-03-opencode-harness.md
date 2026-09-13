# step-03 — OpenCode plugin driven; a real doctrine defect found and fixed

## What I drove
tools/test-integrations.mjs — a NEW harness that imports the actual plugin
module and calls its real exported factory. No mock of the code under test:
`Plugin` is a plain async function returning a hook table, so invoking it IS
the production path. The stub client supplies only `client.app.log`, which is
the sole dependency the plugin touches.

Before this file, coverage of both TS integrations was ZERO (measured across
tools/test-hooks.sh and 6 other harnesses).

## The defect the harness caught on its first honest run

    FAIL  MET: still denies writing a test file
          expected true   actual false

opencode/plugin/proofpunk.ts:227 read the write path as:

    output.args?.path ?? output.args?.file_path ?? ""

but OpenCode sends `filePath` — which the READ guard on line 216 already
assumed (`args.filePath ?? args.path`). So on every real write the test-path
regex was matched against the empty string, and the doctrine's hardest
promise — "the write path never creates test files" — silently never fired
on OpenCode.

It was invisible because the earlier deny case passed for the WRONG reason:
with no verdict recorded, the intent gate blocked the write first. Only
recording a MET verdict isolated the write guard and exposed it.

## The fix
Line 227 now reads `filePath` first, matching its sibling guard, with the
other spellings kept as tolerant fallbacks.

## Mutation proof (the test is load-bearing)

    WITHOUT fix : exit=1, FAIL "MET: still denies writing a test file"
    WITH fix    : exit=0, INTEGRATION TEST PASSES: 19
    source file restored byte-exact afterwards: True

A test that passes both before and after proves nothing. This one fails
precisely when the guard is weakened.

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
  UNCOVERED  event behavior — needs a live ExtensionAPI; a stub would test the stub

INTEGRATION TEST PASSES: 19
INTEGRATION TEST FAILS: 0


## What I SEE
19 assertions pass, 0 fail, exit 0. Both verdict states are exercised: UNMET
denies ordinary work while still allowing inspection and the resolver command
(so a session can unwedge itself), and MET allows ordinary work while still
denying destructive commands and test files.

## Stated limit, not papered over
The OMP extension is load-only here: its entry point needs a live ExtensionAPI
supplied by the running agent, and a fake one would test the fake. The harness
prints UNCOVERED for that and asserts only what is real — that the module
loads and its default export is the extension factory.

VERDICT: PASS for the OpenCode integration. OMP event behavior remains
UNCOVERED by construction.
