# Proofpunk v2.0.0 — One Write Path — Measured Report (Round 4, 2026-08-13)

Contract: the operator's Priority-HIGH spec (architecture + invocation
correctness) plus a research swarm's invocation contracts for Claude Code,
OpenCode, and OMP (all from official/vendor sources — see
`plugins/proofpunk/docs/invocation-contracts.md`).

## The collapse

| Metric | v1.10.1 | v2.0.0 | Evidence |
|---|---|---|---|
| Skills | 19 | **17** (`cook` merged into `implement`; `functional-validation` absorbed as implement's inline Stage 5) | `evidence/v2-release/verify-orchestration-output.txt` |
| Commands (claude + opencode) | 7+7 | **6+6** (`cook` gone from both surfaces) | `plugins/proofpunk/commands/`, `opencode/commands/` |
| Write paths | 2 (implement + cook, ~60% duplicated per the inventory diff) | **1** | `docs/consolidation-decisions.md` (v2.0.0 entry) |
| Validation invocation | standalone skill (skippable) | **inline phase of implement — cannot be skipped** | `skills/implement/SKILL.md` Stage 5 |
| Scouting before edits | advisory | **mandatory + enforced** (stop-guard blocks "done" without a scout record) | `evidence/v2-release/test-hooks-output.txt` cases 14-15 |
| Test-file creation | possible | **hard-blocked** (PreToolUse, all platforms) | same, cases 9-11 |
| Plugin-bundled agents | 0 (claude) / 1 (opencode) / 0 (omp) | **3 / 3 / 3** (implement, scout, end-user-validate) with skills baked in | `plugins/proofpunk/agents/`, `opencode/agents/`, `omp/agents/` |
| Hook decision points | 3 | **5** (+ no-test-files PreToolUse, + PostToolUse walkthrough) | `hooks/hooks.json` |
| Hook behavior cases | 13/13 | **19/19** | `evidence/v2-release/test-hooks-output.txt` |
| "test" in the write path | 17 occurrences (implement) | 0 outside blocking/prohibition context | language audit |
| Install dry-run | 0 fails | 0 fails (both targets) | `evidence/v2-release/dry-run-install-output.txt` |
| Orchestration verifier | PASS @ 19 | **PASS @ 17** | `evidence/v2-release/verify-orchestration-output.txt` |

> **Superseded (2026-09-01, historical record — not rewritten):** the plugin-bundled
> agents row is stale in two ways. The real paths are nested —
> `plugins/proofpunk/opencode/agents/` and `plugins/proofpunk/omp/agents/`, not
> top-level — and the OpenCode count is now **4**, not 3: `proofpunk.md` (the router
> agent) was added after this report shipped. Measured 2026-09-01: 3 / 3 / 4.
> This report is left intact as the v2.0.0 record.

## Invocation contract (researched, drives the design)

- **Claude Code**: skills auto-invoke by model judgment over name+description
  (1,536-char listing budget); plugin agents spawn via the Agent tool on
  description match and get full skill content via the `skills:` frontmatter
  preload; `hooks/hooks.json` merges on plugin enable; Stop/SubagentStop take
  no matchers (silently ignored).
- **OpenCode**: plugins are TS hook modules (`tool.execute.before` throws to
  block); agents are `agents/*.md` with `permission:` maps (tools: is
  deprecated); skills discovered across six roots incl. `~/.claude/skills`;
  AGENTS.md beats CLAUDE.md; no `@`-imports in AGENTS.md.
- **OMP**: first-class `task` subagents (`agents/*.md` with `autoloadSkills`);
  extensions subscribe to `tool_call` (can block) and `session_stop` (can
  force continuation, cap 8); native memory = `.omp/AGENTS.md` + sticky
  `RULES.md`; marketplace is Claude-registry-compatible.

## What the measurement loop caught

- My own cross-reference sweep stripped list commas in two hook scripts
  (Python adjacent-string fusion turned the patterns into garbage) — the
  harness failed loudly; both scripts rewritten and re-proven.
- The verifier caught stale Called-by lines in five skills the moment cook
  disappeared — the graph is machine-checked, so drift is impossible to miss.
