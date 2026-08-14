---
description: Install proofpunk project memory — CLAUDE.md or AGENTS.md (platform-correct, ≤200 lines, merged never clobbered) plus scoped rules
argument-hint: "[--platform claude-code|opencode|agents|omp] [--clobber] [--no-rules]"
---

# /proofpunk:install — project memory installer

Sets up the memory layer that makes the doctrine stick in THIS project,
using the conventions of the platform you're running on. Platform defaults
(verified against vendor docs, 2026-08-13):

| Platform | Memory file | Scoped rules |
|---|---|---|
| claude-code (default) | `CLAUDE.md` | `.claude/rules/*.md` with `paths:` frontmatter |
| omp | `CLAUDE.md` (Claude-compatible chain) | `.claude/rules/` |
| opencode | `AGENTS.md` (CLAUDE.md is only a fallback when no AGENTS.md exists) | `.opencode/rules/*.md` (opencode-rules plugin layout) |
| agents | `AGENTS.md` | none — rules inline in AGENTS.md |

Also know the asymmetries: Claude Code auto-loads `@path` references from
CLAUDE.md; OpenCode does NOT — the AGENTS.md template therefore instructs
explicit on-demand reads instead of `@` imports.

## Acceptance criteria (all must hold — report each)

- The platform's memory file exists, is ≤ 200 lines, and uses the correct
  name for the platform (table above).
- Doctrine lives inside `<!-- proofpunk:begin -->` … `<!-- proofpunk:end -->`
  markers; nothing outside the markers was edited.
- Scoped rule files exist in the platform's rules directory with valid
  frontmatter (skipped cleanly with `--no-rules`).
- The verification block at the end was actually run, output in the report.

## Step 1 — Detect (report findings, don't ask)

Platform: `--platform` if given; otherwise infer from the agent you are
(Claude Code → claude-code; OpenCode → opencode; OMP → omp; else agents).
Project: stack manifests (package.json/pyproject/go.mod/Cargo.toml), the
root directory name, existing memory files (`CLAUDE.md` AND `AGENTS.md` —
note both, they interact per the table), existing rules dirs, and whether
the project is a TUI (ink/textual/ratatui in dependencies).

## Step 2 — Write or merge the memory file

Template: `assets/claude-md-template.md` (claude-code/omp) or
`assets/agents-md-template.md` (opencode/agents) in this plugin — read the
right one. Substitute `{{PROJECT_NAME}}`, `{{TEST_COMMAND}}`,
`{{BUILD_COMMAND}}` with detected values (omit lines with no detected
value — never write "unknown").

- **No existing file** → create from the template.
- **Existing file** → merge: replace an existing marked section in place,
  otherwise append it. Never edit outside the markers.
- **Both CLAUDE.md and AGENTS.md exist on opencode** → warn that AGENTS.md
  wins and CLAUDE.md is ignored by OpenCode; merge into AGENTS.md only.
- **`--clobber`** → replace the whole file (explicit opt-in).
- After writing: count lines; if >200, compress the proofpunk section
  (never the user's own content outside markers).

## Step 3 — Write scoped rules (skip with `--no-rules`)

From `assets/rules/` in this plugin:

- claude-code/omp: write into `.claude/rules/` — `proof-obligations.md`
  (global), `evidence-contract.md` (paths: evidence dirs), `tui-driving.md`
  (only when Step 1 detected a TUI).
- opencode: same three files into `.opencode/rules/` (the opencode-rules
  plugin convention); if that plugin isn't installed, say so and note that
  unscoped rules still apply via AGENTS.md.
- agents: no rules directory convention — fold the proof-obligations rule
  into the AGENTS.md marked section instead.

Never overwrite a differing existing rule file — report the conflict and
write `<name>.proofpunk.md` instead (unless `--clobber`).

## Step 4 — Verify (run this, paste real output)

```bash
wc -l CLAUDE.md AGENTS.md 2>/dev/null
wc -l .claude/rules/*.md .opencode/rules/*.md 2>/dev/null
grep -c "proofpunk:begin" CLAUDE.md AGENTS.md 2>/dev/null
head -3 .claude/rules/proof-obligations.md .opencode/rules/proof-obligations.md 2>/dev/null
tail -n 3 ~/.claude/proofpunk-loads.jsonl 2>/dev/null || echo "no load log yet (fires next session)"
```

## Report

Table: file | action (created/merged/skipped/conflict) | lines. Then the
acceptance checklist with PASS/FAIL per row. A partial install is reported
UNVERIFIED, never "done".

## Examples

```bash
/proofpunk:install                                        # detect platform, merge, rules, verify
/proofpunk:install --platform opencode                    # AGENTS.md + .opencode/rules/
/proofpunk:install --platform agents --no-rules           # AGENTS.md only, rules folded in
/proofpunk:install --clobber                              # replace the memory file wholesale
/proofpunk:install --platform claude-code --no-rules --clobber   # every option selected
```
