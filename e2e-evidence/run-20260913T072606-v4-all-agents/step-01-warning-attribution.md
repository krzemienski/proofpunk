# step-01 — the reported warning is NOT proofpunk's

## The reported defect
    claude-code-harness: hooks.json: unknown key 'if'
    in hooks.PermissionRequest[1] ignored

## Owner, proven by exhaustive scan of every installed plugin
Scanned every hooks.json under ~/.claude/plugins via pathlib.
Exactly ONE plugin has a PermissionRequest entry carrying a top-level `if`:

    ~/.claude/plugins/cache/claude-code-harness-marketplace/claude-code-harness/4.16.3/hooks/hooks.json
        PermissionRequest entries : 2
        'if' at top-level index   : [1]

The warning text names `claude-code-harness` itself, and the index [1] matches.

### The offending entry verbatim
{
    "matcher": "Bash",
    "if": "Bash(git status*)|Bash(git diff*)|Bash(git log*)|Bash(git branch*)|Bash(git rev-parse*)|Bash(git show*)|Bash(git ls-files*)|Bash(npm test*)|Bash(npm run test*)|Bash(npm run lint*)|Bash(npm run typecheck*)|Bash(npm run build*)|Bash(npm run validate*)|Bash(npm lint*)|Bash(npm typecheck*)|Bash(npm build*)|Bash(pnpm test*)|Bash(pnpm run test*)|Bash(pnpm run lint*)|Bash(pnpm run typecheck*)|Bash(pnpm run build*)|Bash(pnpm run validate*)|Bash(pnpm lint*)|Bash(pnpm typecheck*)|Bash(pnpm build*)|Bash(yarn test*)|Bash(yarn run test*)|Bash(yarn run lint*)|Bash(yarn ru

## proofpunk does NOT declare PermissionRequest anywhere
    source plugins/proofpunk/hooks/hooks.json events : ['InstructionsLoaded', 'PostToolUse', 'PostToolUseFailure', 'PreToolUse', 'SessionStart', 'Stop', 'SubagentStop']
    PermissionRequest present                        : False
    installed 3.0.0 declares PermissionRequest       : False
    installed 2.2.0 declares PermissionRequest       : False

17 other plugins declare PermissionRequest; none has an `if` key.

## What I SEE
The warning belongs to a third-party plugin, claude-code-harness 4.16.3.
proofpunk cannot emit it: it declares no PermissionRequest event in source
or in either installed copy. Editing proofpunk's hooks.json would change
nothing about this message.

## Real proofpunk finding surfaced by the same scan
    installed  ~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/3.0.0/
    manifests  plugins/proofpunk/package.json = 4.0.0
    => the running Claude Code loads proofpunk 3.0.0, not 4.0.0. VERSION DRIFT.

VERDICT: warning ownership = claude-code-harness (NOT proofpunk). PASS on attribution.
