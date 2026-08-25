<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-08-23 | Updated: 2026-08-23 -->

# tools

## Purpose

Build, install, and verification toolchain for proofpunk: the multi-platform installer, the three release-verification scripts, the installer usage docs, and the deterministic generators for the theme pack and the GitHub Pages site.

## Key Files

| File | Description |
|------|-------------|
| `proofpunk-install.sh` | Multi-platform installer: plain skills into `~/.claude/skills`, OMP, OpenCode, or `~/.agents/skills`; rewrites `../../references/X` citations to self-contained copies; optional themes/plugins/hooks/memory-injection; `--verify` pass auto-repairs broken refs |
| `test-hooks.sh` | Runs hook assertions and exits nonzero on failures; a successful run ends with `HOOK TEST FAILS: 0` — run before any hooks change |
| `dry-run-install.sh` | Installer dry-run harness (0 fails expected) — run before any installer change |
| `verify-orchestration.py` | Verifies skill orchestration graph (18 skills green, `proofpunk` router as sole root) — run before any skills change |
| `INSTALL.md` | Authoritative installer usage: every flag, what an install produces, why self-contained copies exist |
| `build-site.py` | Generates `docs/*.html` (reads markdown sources; pre-renders mermaid via mmdc when present). Edit page sources here, not the HTML |
| `generate-themes.py` | Renders `plugins/proofpunk/themes/palettes.json` → `themes/{omp,opencode,hyper}/`. Deterministic; hand-edits to rendered files are overwritten |

## For AI Agents

### Working In This Directory

- `build-site.py` hardcodes `ROOT = /tmp/build/proofpunk/proofpunk-main` — it expects a repo checkout at that path; adjust when running elsewhere.
- The installer is the only writer of user machines; treat any change to its copy/rewrite logic as release-grade (full verification trio below).
- `ALL_SKILLS` in `proofpunk-install.sh` must match the actual skill dirs in `plugins/proofpunk/skills/` — a ghost or missing entry is the exact v2.0.1 bug class.

### Testing Requirements

- Any change here: run `bash test-hooks.sh`, `bash dry-run-install.sh`, `python3 verify-orchestration.py` from this directory, all green, outputs captured under `evidence/<release>/`.
- Theme pipeline: `python3 generate-themes.py` twice → byte-identical output (determinism check).

### Common Patterns

- Shell scripts use `say`/`warn`/`die`/`run` helpers (see installer utils section) — follow them for new output paths.
- Generated-file discipline: every generator reads one canonical source and writes derived formats; never special-case a rendered artifact.

## Dependencies

### Internal

- Reads from `plugins/proofpunk/skills/`, `references/`, `themes/`, `opencode/`, `extensions/`.
- Writes the `docs/` site and the rendered theme formats.

### External

- Python 3 stdlib (`colorsys`, `json`, `html`, `re`) plus **PyYAML** (`import yaml` in `build-site.py` `fm_parse` — external, not stdlib); optional `mmdc` (mermaid-cli) for diagram pre-rendering.

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
