# Proofpunk v1.10.0 — Hooks + `/proofpunk:install` — Measured Improvement Report (Round 3, 2026-08-13)

Basis: external research (Claude Code hooks reference, anthropics hook-development
skill, claude-mem hook architecture, current CLAUDE.md guidance), then design
(`plugins/proofpunk/docs/hooks-and-init-design.md`), then implementation, then
scripted measurement. Every row below is backed by a committed artifact.

## Before → after

| Metric | v1.9.0 | v1.10.0 | Evidence |
|---|---|---|---|
| Hook events covered | 1 (SessionStart) | 5 (+Stop, SubagentStop, PreToolUse, InstructionsLoaded) | `plugins/proofpunk/hooks/hooks.json` |
| Deterministic doctrine enforcement | 0 blocking hooks | 3 decision points (unproven-claim block ×2, secrets-in-evidence deny ×1) | `evidence/hooks-release/test-hooks-output.txt` |
| Commands (claude + opencode) | 6+6 | 7+7 (`install`) | `plugins/proofpunk/commands/install.md`, `opencode/commands/proofpunk-install.md` |
| Project-memory scaffolding | none | CLAUDE.md ≤200 lines (marker merge) + 3 scoped rules in one command | `evidence/hooks-release/dry-run-install-output.txt` |
| Hook-script correctness | untested | 13/13 behavior cases green (syntax ×4, decisions ×8, log tap ×1) | same as row 2 |
| Orchestration graph | closed @ 18 skills | closed @ 19 skills (verifier exit 0) | `evidence/hooks-release/verify-orchestration-output.txt` |

## Behavior cases proven (all in evidence/hooks-release/)

- stop-guard blocks a completion claim with no proof citation (`decision:"block"` + reason)
- stop-guard allows the same claim when an evidence path is cited
- stop-guard stays silent on non-claims and on missing transcripts
- evidence-guard denies `ghp_*` key material into `e2e-evidence/**` (exit 2 + stderr)
- evidence-guard allows clean evidence writes and ignores non-evidence paths
- instructions-loaded appends real JSONL load events to `~/.claude/proofpunk-loads.jsonl`
- install dry-run: CLAUDE.md merged (24 lines, user content preserved, markers present,
  zero placeholders left), 3 scoped rules written with `paths:` frontmatter

## Process defects caught by the measurement loop itself

- Harness `printf` ate inner-quote escapes and fed the guard invalid JSON — the
  "guard failure" was harness-generated; fixed with heredoc inputs (the guard was
  correct all along — a reminder that a red test can indict the test).
- Orchestration verifier caught tui-testing's called-by claims having no real
  edges (callers hadn't declared deferrals) and a stale canonical sink set —
  both fixed and re-verified.
