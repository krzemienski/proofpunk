<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-08-23 | Updated: 2026-08-23 -->

# proofpunk (plugin)

## Purpose

The shippable plugin unit: 18 skills, 6 commands, 7 enforcement hooks, platform agents, the shared doctrine references, the 20-theme pack, and the OMP/OpenCode glue. This entire subtree is what the marketplaces (`source: ./plugins/proofpunk`) and `tools/proofpunk-install.sh` deliver to user machines.

## Key Files

| File | Description |
|------|-------------|
| `package.json` | OMP plugin manifest (`extensions/proofpunk.ts`); version must match `.claude-plugin/plugin.json` |
| `.claude-plugin/plugin.json` | Claude Code plugin manifest — name, version, description, keywords |
| `.omp-plugin/plugin.json` | OMP plugin catalog entry |
| `extensions/proofpunk.ts` | OMP doctrine-guard extension |
| `docs/usage-guide.md` | Hands-on invocation examples for every skill (`/skill-name <positional> --flag`) |
| `docs/architecture.md` | Skill DAG, ownership, depth model |
| `docs/invocation-contracts.md` | Exact invocation contract per skill |
| `docs/hooks-and-init-design.md` | Hook lifecycle and `/proofpunk:install` project-memory design |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `skills/` | 18 skill dirs, each with `SKILL.md`; `../../references/X` citations are deliberate — the installer rewrites them to self-contained copies. `proofpunk/` is the router head — it calls all 17 others and is called by none |
| `commands/` | 6 slash commands: verify, forge-prompt, implement, install, truth-audit, rate-prompt |
| `hooks/` | 7 enforcement hooks (stop-guard, evidence-guard, capture-guard, no-test-files, post-write-walkthrough, session-start, instructions-loaded) + `hooks.json` |
| `agents/` | Claude Code subagents: end-user-validate, implement, scout |
| `references/` | 13 shared doctrine files covering validation (api/cli/ios/web), CI gates, evidence contract, end-user actor rules, iOS HIG and WCAG checklists, platform routing, preflight checks, severity model, and defect patterns; cited as `../../references/X` and rewritten to self-contained copies at install time (scoped rule files live in `assets/rules/`) |
| `assets/` | `claude-md-template.md` + `agents-md-template.md` (used by `/proofpunk:install`) and `rules/` scoped rule files |
| `themes/` | `palettes.json` canonical source + rendered `omp/`, `opencode/`, `hyper/` formats (generated — never hand-edit) |
| `opencode/` | OpenCode commands, plugin glue, agents |
| `omp/agents/` | OMP agent definitions |

`capture-guard.sh` blocks modification of existing raw capture files (e.g. `.txt`, `.log`, `.png`) under `evidence/` or `e2e-evidence/`, while permitting new captures and authored `.md`/`.json` sidecars; it enforces `evidence/AGENTS.md:22` ("a modified capture is a fabricated claim").

## For AI Agents

### Working In This Directory

- Everything here ships to users: no scratch artifacts, no test scaffolding, no local-only files inside this subtree.
- Changing skill count or version → sweep `package.json`, `.claude-plugin/plugin.json`, both marketplace files at repo root, `README.md`, and `tools/INSTALL.md` together (recurring drift bug; see commits 2953547, 7958498).
- Skills cite doctrine as `../../references/X` on purpose; the installer's bundler widens and rewrites these. Localizing paths in-repo breaks the plugin tree.
- Rendered theme dirs are outputs of `tools/generate-themes.py`; edit `themes/palettes.json` only.

### Testing Requirements

- Full trio from repo root (`tools/test-hooks.sh`, `tools/dry-run-install.sh`, `tools/verify-orchestration.py`), captures under `evidence/<release>/`, before claiming any change here done.

### Common Patterns

- Doctrine lives in `references/` and skills defer to it; a skill never restates a ruling rule.
- Self-containment at install time is the design constraint that shapes citation layout — see `tools/INSTALL.md` "Why self-contained copies".
- No per-skill `AGENTS.md`: each skill dir's `SKILL.md` is its own documentation.

## Dependencies

### Internal

- Consumed by `tools/proofpunk-install.sh` (source of the skill/reference/theme copies) and both marketplace catalogs.

### External

- None at runtime — markdown, JSON, and shell; the OMP extension is TypeScript loaded by the host.

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
