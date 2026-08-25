# Flag-drift defect — live command proof

Two command surfaces documented flags the real script rejects.

## Executed proof

Script: `plugins/proofpunk/skills/codebase-truth-audit/scripts/init_audit_workspace.py`

```
--since 2026-01-01                   -> rc=2  error: unrecognized arguments: --since
--start 2026-01-01 --end 2026-08-13  -> rc=0
```

Captured in `old.log` and `new.log`. Every documented invocation using
`--since/--until` failed for anyone who copied it.

## Fixed

- `plugins/proofpunk/commands/truth-audit.md` (Claude surface)
- `plugins/proofpunk/opencode/commands/proofpunk-truth-audit.md` (OpenCode surface)

The OpenCode surface was missed in the first pass — same defect, second platform.

## Second defect fixed in the same pass

`tools/build-site.py:311` hardcoded `/proofpunk:cook`, a command removed at
v2.0.0, and omitted the real `/proofpunk:install`. Because the string lived in
the *generator*, every regeneration reproduced it. Replaced with the real
command; confirmed by regenerating: zero files name `cook`, `index.html` now
names `install`.

## Incidental: the guard fired on the operator

While cleaning up a probe artifact, a recursive-delete command was blocked by
proofpunk's own PreToolUse destructive-command guard — then blocked a second
time when the same pattern appeared merely as *quoted text* inside a heredoc.

Two observations, both real:
1. The guard fires on live operator commands, not just model-authored ones.
2. It matches the raw command string, so a documented example of a dangerous
   pattern is blocked as if it were an execution. That is a false positive, and
   is recorded here rather than fixed — changing guard semantics is a behavior
   change that needs operator sign-off.
