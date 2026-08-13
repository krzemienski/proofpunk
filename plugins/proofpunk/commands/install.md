---
description: Install proofpunk project memory — CLAUDE.md (≤200 lines, merged never clobbered) plus scoped .claude/rules/ with the proof contract
argument-hint: "[--clobber] [--no-rules]"
---

# /proofpunk:install — project memory installer

Sets up the memory layer that makes the doctrine stick in THIS project:
a tight `CLAUDE.md` and scoped `.claude/rules/*.md`. Every step verifies
itself and reports real file paths and line counts.

## Acceptance criteria (all must hold — report each)

- `CLAUDE.md` exists and is **≤ 200 lines** (adherence degrades past that).
- Doctrine lives inside `<!-- proofpunk:begin -->` … `<!-- proofpunk:end -->`
  markers; nothing outside the markers was edited.
- `.claude/rules/proof-obligations.md` and `.claude/rules/evidence-contract.md`
  exist with valid frontmatter.
- The verification block at the end was actually run, and its output is in
  the final report.

## Step 1 — Detect (report findings, don't ask)

Read: `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` (stack +
test/build commands), the root directory name (project name), existing
`CLAUDE.md` and `.claude/rules/` (presence, sizes), and whether the project
is a TUI (ink/textual/ratatui in dependencies).

## Step 2 — Write or merge CLAUDE.md

Template: `assets/claude-md-template.md` in this plugin (read it). Substitute
`{{PROJECT_NAME}}`, `{{TEST_COMMAND}}`, `{{BUILD_COMMAND}}` with the detected
values (omit lines whose value was not detected — never write "unknown").

- **No existing CLAUDE.md** → create it from the template.
- **Existing CLAUDE.md** → merge: if a `<!-- proofpunk:begin -->` section
  exists, replace ONLY that section; otherwise append the section. Never edit
  a single line outside the markers.
- **`--clobber`** → replace the whole file (user opted in explicitly).
- After writing: count lines. If the file exceeds 200, compress the
  proofpunk section (never truncate the user's own content outside markers).

## Step 3 — Write scoped rules

From `assets/rules/` in this plugin (read each):

- `.claude/rules/proof-obligations.md` — global (no `paths:` scoping).
- `.claude/rules/evidence-contract.md` — scoped to evidence dirs.
- `.claude/rules/tui-driving.md` — write ONLY if Step 1 detected a TUI project.

Do not overwrite a rule file that already exists and differs — report the
conflict and write to `<name>.proofpunk.md` instead (unless `--clobber`).

## Step 4 — Verify (run this, paste real output)

```bash
wc -l CLAUDE.md .claude/rules/*.md
grep -c "proofpunk:begin" CLAUDE.md
head -3 .claude/rules/proof-obligations.md
tail -n 3 ~/.claude/proofpunk-loads.jsonl 2>/dev/null || echo "no load log yet (fires next session start)"
```

## Report

Table: file | action (created/merged/skipped/conflict) | lines. Then the
acceptance criteria checklist with PASS/FAIL per row. If anything failed,
say so — a partial install is reported UNVERIFIED, never "done".
