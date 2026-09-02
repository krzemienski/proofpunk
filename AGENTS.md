<!-- Generated: 2026-08-23 | Updated: 2026-08-23 -->

# proofpunk

## Purpose

Execution-first delivery plugin for Claude Code, oh-my-pi (OMP), and OpenCode: 17 skills that make "done" mean *proven by end-user testing*. The AI drives the real system as an end user, and any claim it did not actually execute is reported UNVERIFIED, never PASS. No mocks, no stubs, no test-mode bypasses.

## Key Files

| File | Description |
|------|-------------|
| `CLAUDE.md` | Process-memory rules for agents working on this repo (generated artifacts, deliberate `../../references/X` layout, verification commands) |
| `README.md` | Full project documentation: install paths per platform, skill table, command reference — the authoritative overview |
| `plugins/proofpunk/package.json` | Plugin manifest; version string must match `.claude-plugin/plugin.json` and marketplace metadata on every release |
| `.claude-plugin/marketplace.json` | Claude Code marketplace catalog |
| `.omp-plugin/marketplace.json` | OMP marketplace catalog |
| `proofpunk-v2-release-report.md` | v2 release evidence summary |
| `proofpunk-hooks-release-report.md` | Hooks release evidence summary |
| `proofpunk-skills-improvement-report-round2.md` | Round-2 skills improvement findings |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `tools/` | Installer, verification scripts, site/theme generators (see `tools/AGENTS.md`) |
| `evidence/` | Per-release verification output captures (see `evidence/AGENTS.md`) |
| `examples/` | mood-ring Flask demo — proofpunk's dogfooding target with live evidence runs (see `examples/AGENTS.md`) |
| `plugins/proofpunk/` | The shippable plugin: skills, commands, hooks, agents, themes, doctrine (see `plugins/proofpunk/AGENTS.md`) |
| `docs/` | Generated GitHub Pages site — built by `tools/build-site.py`, never hand-edited |
| `banks/` | Mnemopi memory runtime database — generated, never edited |

## For AI Agents

### Working In This Directory

- `CLAUDE.md` at this root is the ruling process contract; follow it before editing anything.
- Generated outputs (`docs/*.html`, `plugins/proofpunk/themes/{omp,opencode,hyper}/`, `banks/`) are never hand-edited; change sources and regenerate.
- Do not localize the `../../references/X` citation layout in `plugins/proofpunk/skills/` — the installer rewrites those paths at install time.

### Testing Requirements

- Skills/hooks/installer changes: `bash tools/test-hooks.sh`, `bash tools/dry-run-install.sh`, `python3 tools/verify-orchestration.py`, capture under `evidence/<release>/`.
- Theme changes: `python3 tools/generate-themes.py` then confirm deterministic output.

### Common Patterns

- One canonical source per generated artifact family (e.g. `themes/palettes.json` → three rendered formats).
- Version strings and skill/command counts recur in `package.json`, `README.md`, `tools/INSTALL.md`, and `tools/build-site.py` page sources — sweep all of them together on release.

## Dependencies

### Internal

- `tools/` generates `docs/` and `plugins/proofpunk/themes/` rendered formats.
- `plugins/proofpunk/` is the unit the marketplaces and installer ship.

### External

- No runtime dependencies — the installed plugin is markdown, JSON, and shell. Build-time tooling needs Bash, Python 3, and PyYAML (`build-site.py` frontmatter parsing); optional `mmdc` (mermaid-cli) for diagram pre-rendering.
<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->

<!-- proofpunk:begin -->
## Proof contract (proofpunk)

- Done means proven by end-user testing: drive the real system as the end
  user, capture run-scoped evidence, cite it by full path. Unexecuted =
  UNVERIFIED, never PASS.
- No mocks, stubs, or placeholder implementations. Malformed input fails
  clearly and safely. Secrets never enter evidence directories.
- Load proofpunk doctrine (`plugins/proofpunk/references/`) on demand with
  the read tool — do not preload it here.

## Commands

- Test: `bash tools/test-hooks.sh`, `bash tools/dry-run-install.sh`,
  `python3 tools/verify-orchestration.py`
- Build: `python3 tools/build-site.py` (docs), `python3 tools/generate-themes.py` (themes)
- Proof runs: `/proofpunk:verify` before any completion claim;
  `/proofpunk:implement "<goal>"` for multi-step work.

## Project

- proofpunk — read README.md for overview.
<!-- proofpunk:end -->

