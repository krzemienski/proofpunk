# Design — proofpunk v1.10.0: deterministic hook enforcement + `/proofpunk:install`

**Status**: implemented in this release. Sources cited per section.

## 0. Research basis (all external, verified 2026-08-13)

| Source | What it contributed |
|---|---|
| Claude Code Hooks reference (code.claude.com/docs/en/hooks) | 30 lifecycle events; decision-control matrix (`decision:"block"`, `hookSpecificOutput.permissionDecision`, `additionalContext`); matcher grammar; `${CLAUDE_PLUGIN_ROOT}`; prompt-hook response schema |
| anthropics/claude-code `plugin-dev/skills/hook-development` | Canonical Stop/SubagentStop completeness-check pattern (block feeds `reason` back to Claude to continue); PreToolUse JSON output shape |
| claude-mem hooks architecture doc | Performance discipline: hooks sub-100ms, always-exit-0 on Setup, version-marker pattern, suppressOutput where appropriate |
| CLAUDE.md current best practices (Anthropic memory docs + luongnv89/claude-howto + community) | ≤200 lines (adherence degrades past it); imperative voice; high-priority rules in first 40 lines; NO verification reminders (Opus-5-era over-verification); `.claude/rules/*.md` with `paths:` frontmatter for scoped loading; never clobber — marked-section merge |

Design decisions traceable to the table:
- **Stop guard is a command hook, not a prompt hook.** The official canonical
  example for Stop is prompt-based (Haiku judges completeness). We use a
  deterministic command hook instead: (a) it is locally testable end-to-end
  (a prompt hook's judgment can't be measured without an LLM in the loop —
  and this release must be *measured*); (b) zero latency/cost per stop;
  (c) the heuristic is narrow and documented, blocking only on a strong
  unproven-claim signal, defaulting to non-blocking additionalContext.
- **PreToolUse guards are command hooks** (fast, deterministic, JSON deny) —
  prompt hooks for path checks would be waste; the docs' own `.env` example
  is a command hook for exactly this class.
- **CLAUDE.md ≤ 200 lines** is a hard acceptance criterion of `/proofpunk:install`.

## 1. Hook set (hooks/hooks.json)

| Event | Matcher | Type | Script | Behavior |
|---|---|---|---|---|
| SessionStart | `startup\|resume\|clear` | command | `session-start.sh` (existing, tightened) | doctrine `additionalContext`; <20ms; exit 0 |
| **Stop** | (none) | command | `stop-guard.sh` | transcript scan (see §2): strong unproven-claim → `{"decision":"block","reason":…}` (reason is fed back to Claude and the turn continues); otherwise `additionalContext` soft reminder; <50ms |
| **SubagentStop** | (none) | command | `stop-guard.sh` | same check, subagent transcript |
| **PreToolUse** | `Write\|Edit` | command | `evidence-guard.sh` | deny (exit 2 + stderr) when the write targets an evidence dir **and** payload matches secret patterns; else allow (exit 0) |
| **InstructionsLoaded** | (none) | command | `instructions-loaded.sh` | append `{ts, filePath, loadReason, cwd}` to `~/.claude/proofpunk-loads.jsonl`; always exit 0 (the measurement tap for `/proofpunk:install`) |

## 2. stop-guard.sh — the unproven-completion detector

Inputs (stdin JSON): `session_id`, `transcript_path`, `cwd`, `hook_event_name`.

Algorithm (deterministic, documented heuristic):
1. Read the last 40 lines of `transcript_path` (JSONL). No file → exit 0.
2. Claim signal: an assistant text line containing a completion marker
   (`\b(done|complete|completed|finished|shipped|all tests pass|works now)\b`
   case-insensitive).
3. Proof signal: any line in the same window referencing a proof artifact
   (`e2e-evidence/`, `evidence-inventory`, `step-\d+`, `screenshot`,
   `curl .*200`, `verdict`).
4. Block iff claim-signal AND NOT proof-signal:
   `{"decision":"block","reason":"Proofpunk: completion was claimed without a cited end-user test artifact. Run the end-user test (drive the real system), capture run-scoped evidence, cite it by full path — or downgrade the claim to UNVERIFIED."}`
5. Else: `{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"proofpunk: done = proven by end-user testing."}}` — soft, non-blocking.

False-positive posture: the block reason tells Claude exactly how to satisfy
the guard (produce evidence or downgrade), so a mistaken block costs one
turn of clarification, not a halt. This mirrors the official pattern where
the reason is the next instruction.

## 3. evidence-guard.sh — secrets never enter evidence

Inputs: `tool_name`, `tool_input.file_path` (Write/Edit).

1. If `file_path` matches `*(e2e-evidence|evidence)/*`:
   scan `tool_input.content` for secret patterns
   (`sk-[A-Za-z0-9_-]{16,}`, `ghp_[A-Za-z0-9]{20,}`, `AKIA[0-9A-Z]{16}`,
   `BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY`, `api[_-]?key`).
   Match → exit 2, stderr: "Proofpunk: refusing to write probable secret material into an evidence directory (see evidence-contract: redact, never commit)."
2. Else exit 0.

## 4. `/proofpunk:install` — project memory installer (7th command)

Command doc: `commands/install.md`. The agent executes four steps with
explicit verification after each:

1. **Detect** — stack manifests (package.json/pyproject/go.mod/Cargo.toml),
   test/build commands, existing `CLAUDE.md`, existing `.claude/rules/`,
   project name from the root directory.
2. **CLAUDE.md** — write or merge:
   - Template (`assets/claude-md-template.md`): ≤40 lines of proofpunk
     doctrine + detected commands. Total file MUST stay ≤200 lines.
   - Existing file → merge into `<!-- proofpunk:begin -->` …
     `<!-- proofpunk:end -->` section (replace section if present, append if
     absent). Never edit outside the markers. Report the diff.
3. **Scoped rules** — `.claude/rules/`:
   - `proof-obligations.md` (no `paths:` — global): task-level proof rule.
   - `evidence-contract.md` (`paths: ["e2e-evidence/**", "evidence/**"]`):
     redact + freshness rules, loads only when evidence files are touched.
   - `tui-driving.md` (`paths: ["**/*.tsx", "**/ink*"]`, only when the project
     is a TUI): the tui-testing discipline pointer.
4. **Verify** — read the files back (line counts), print the
   InstructionsLoaded log line proving the last load event
   (`~/.claude/proofpunk-loads.jsonl` tail), and state the acceptance
   criteria: CLAUDE.md ≤200 lines, markers present, rules parse.

opencode variant: `opencode/commands/proofpunk-install.md` (same playbook).

## 5. Measurement plan (before → after, all executed, none claimed)

| Metric | v1.9.0 | v1.10.0 | Instrument |
|---|---|---|---|
| Hook events covered | 1 | 5 | hooks.json diff |
| Deterministic doctrine enforcement | 0 blocking hooks | 3 decision points (Stop, SubagentStop, PreToolUse) | `tools/test-hooks.sh` run |
| Commands (claude + opencode) | 6+6 | 7+7 | file count |
| Project-memory scaffolding | none | CLAUDE.md + 3 scoped rules via one command | dry-run in `/tmp/pp-init-fixture` |
| Hook-script correctness | untested | bash -n + 8 JSON-stdin behavior cases green | test output committed |
| Orchestration graph | closed | closed (verifier exit 0) | verify-orchestration.py |
| Site | v1.9.0 pages | v1.10.0 + install command row + hooks section | regenerated |

Acceptance: every row measured by a script whose output is committed to
`evidence/hooks-release/`.
