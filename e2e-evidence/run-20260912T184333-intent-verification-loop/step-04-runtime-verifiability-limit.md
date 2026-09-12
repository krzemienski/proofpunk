# What I can and cannot verify per runtime — measured

The design needs three adapters. Before writing any, I measured what is
actually checkable on this machine.

## SDKs are not installed
```
$ ls node_modules/@opencode-ai
  ls: cannot access 'node_modules/@opencode-ai': No such file or directory
  (absent)

$ ls node_modules/@oh-my-pi
  ls: cannot access 'node_modules/@oh-my-pi': No such file or directory
  (absent)

$ plugins/proofpunk/package.json dependencies
  dependencies: {}
  devDependencies: {}
  peerDependencies: {}
```

Both TypeScript surfaces import types that do not exist in this tree:
  extensions/proofpunk.ts:4        import type { ExtensionAPI } from '@oh-my-pi/pi-coding-agent'
  opencode/plugin/proofpunk.ts:4   import type { Plugin } from '@opencode-ai/plugin'

## Consequence for each surface

| Surface | Can I verify behaviour by execution? |
|---|---|
| hooks/stop-guard.sh | YES — it is /bin/sh reading stdin JSON. Drivable with real payloads, already done throughout this session. |
| extensions/proofpunk.ts | NO — cannot instantiate ExtensionAPI, cannot confirm what _ctx.session contains, cannot confirm that {continue:true} forces a turn. |
| opencode/plugin/proofpunk.ts | NO — cannot enumerate the event names the SDK exposes, so cannot confirm a session-stop event exists at all. |

## The claim in the OMP file I could NOT confirm
extensions/proofpunk.ts:75-76 says 'cap 8 forced continuations is the
runtime's own guard against loops'. That number appears nowhere in this
repo outside the comment:
  git grep -i continuation:
    docs/commit-archaeology.md:6:Commits are grouped by narrative arc, not strict chronological order, because several arcs 
    docs/doc-invocation-contracts.html:60:<td>extension <code>pi.on(...)</code>: <code>tool_call</code> can <code>{block, re
    evidence/v3-release/l16-harness/help-output.log:82:    1. Merge backslash line-continuations into one logical line (a
    evidence/v3-release/l16-harness/mutation-sandbox/tools/verify-harness-integrity.py:73:    1. Merge backslash line-contin
    evidence/v3-release/l16-harness/mutation-sandbox/tools/verify-harness-integrity.py:346:def merge_continuations(text):
    evidence/v3-release/l16-harness/mutation-sandbox/tools/verify-harness-integrity.py:347:    """Join backslash line-contin
    evidence/v3-release/l16-harness/mutation-sandbox/tools/verify-harness-integrity.py:426:        lines = non_comment_lines
    plugins/proofpunk/docs/invocation-contracts.md:12:| Hooks (hard guarantee) | `hooks/hooks.json` merges on enable; comman
    plugins/proofpunk/extensions/proofpunk.ts:76:  // continuations is the runtime's own guard against loops).
    plugins/proofpunk/skills/session-intent/references/scripts/analyze.sh:263:    # FIXED: Only add JSON continuation if Git
    plugins/proofpunk/skills/stack-testing/examples/condition_based_waiting.ts:57: *   // Wait for 2 AGENT_MESSAGE events (i
    proofpunk-v2-release-report.md:45:  force continuation, cap 8); native memory = `.omp/AGENTS.md` + sticky
    tools/verify-harness-integrity.py:73:    1. Merge backslash line-continuations into one logical line (a
    tools/verify-harness-integrity.py:346:def merge_continuations(text):
    tools/verify-harness-integrity.py:347:    """Join backslash line-continuations into single logical lines so a
    tools/verify-harness-integrity.py:426:        lines = non_comment_lines(merge_continuations(text))

It is an unverified assertion about someone else's runtime. I am not
building a bound on top of it.

## What this means for the build
The shell surface gets a real, driven implementation.

The two TypeScript surfaces get the adapter written against the
contract, and their status recorded as UNVERIFIED — not PASS — because
'the code looks right' is precisely the standard this plugin rejects.
Shipping them as proven would repeat the defect this session already
found twice: a claim pitched one standard above its evidence.

The honest split is stated up front rather than discovered at the
verdict table.
