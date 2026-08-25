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

`tools/build-site.py:311` hardcoded `/proofpunk:cook`, a command removed at
v2.0.0, and omitted the real `/proofpunk:install`. Because the string lived in
the *generator*, every regeneration reproduced it. Replaced with the real
command.

**Browser-verified** (`commands-rendered.webp`, `index-rendered.webp`), with the
page identity asserted in the same evaluation so the capture cannot be of some
other tab:

```
url:   http://127.0.0.1:8901/commands.html
title: commands — 6+6 commands — proofpunk
names: forge-prompt, implement, install, rate-prompt, truth-audit, verify
cookVisible: false
```

That identity assertion earned its keep: an earlier capture in this same run
silently rendered an unrelated app because the relay tab had navigated away.

**Scope correction.** An earlier claim that "zero files name cook" was too
broad. Six generated files still contain the word *cook* in historical prose
(`doc-consolidation-decisions.html`, `doc-validation-results.html`, and others)
describing the v2.0.0 merge — those are correct records and were left alone.
What is true: **zero files name the command `/proofpunk:cook`**.

## Incidental: a guard fired — but NOT proofpunk's

While cleaning up a probe artifact, a recursive-delete command was blocked with
"Blocked by Proofpunk doctrine guard: destructive command pattern", then blocked
again when the same regex appeared merely as *quoted text* inside a heredoc.

**Initially misattributed to this plugin. That was wrong.** Checked:

- the message string appears nowhere under `plugins/proofpunk/hooks/`
- `hooks.json` registers PreToolUse on `Write|Edit` only — never `Bash`

So the blocking guard is an **ambient host-level guard whose source is not
attributed here**. It borrows proofpunk's name in its message, which is exactly
what made the misattribution easy.

What is observed, scoped honestly:
1. Some host guard blocks destructive Bash patterns from the operator.
2. It matches the raw command string, so *documenting* a dangerous pattern is
   blocked as if executing it — a false positive.

Not fixed here: the defect is not in this repository, so changing it would mean
editing host config outside the plugin.
