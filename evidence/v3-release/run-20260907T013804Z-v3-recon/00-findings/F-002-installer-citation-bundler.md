# F-002 — installer citation bundler mis-resolves run-trace-schema.md

Recorded: 2026-09-07T01:49:06Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee

## Symptom

`bash tools/test-installer.sh` exits 7 on the working tree. Installer output:

```
✗ end-user-testing: BROKEN refs after auto-fix: [('run-trace-schema.md', 'references/severity-model.md')]
```

The auto-fix resolves `run-trace-schema.md` to the WRONG target (`severity-model.md`),
then reports the result broken. The file it should resolve to exists and is tracked:
`plugins/proofpunk/references/run-trace-schema.md` (15082 bytes, tracked at HEAD).

## Three-arm isolation (single variable)

| arm | tree | rc | evidence |
|---|---|---|---|
| A | clean HEAD (detached worktree) | **0** | `f002-installer-arms/arm-A-clean-HEAD.log` |
| B | clean HEAD + ONLY `end-user-testing/SKILL.md` from working tree | **5** | `f002-installer-arms/arm-B-head-plus-eut-edit.log` |
| C | full working tree | **7** | `f002-installer-arms/arm-C-full-working-tree.log` |

## Attribution

- NOT pre-existing at HEAD (arm A = 0).
- NOT caused by F-001 (arm A already has all 18 skills).
- **Caused by uncommitted in-flight work.** Arm B isolates it to ONE added citation.

## The trigger

Working tree adds to `plugins/proofpunk/skills/end-user-testing/SKILL.md` (+3 lines, ~:133):

> validate against `../../references/run-trace-schema.md`

At HEAD, zero skills cite `run-trace-schema.md`. In the working tree, two do
(`end-user-testing` and the `proofpunk` router head). The reference shipped as a file
and got a docs page, but no skill cited it until now — so the installer bundler path
for this reference was never exercised.

## Class

Defect class 3 from the repo taxonomy: **a component shipped but never registered/exercised.**
Identical in shape to `99c72fb` (evidence-guard.sh shipped on disk, never registered).

## Blast radius (arm B, 5 failures from one line)

- clean install rc=1
- collision default rc=1
- --override rc=1
- canonical hooks.json parity FAIL
- F-D5-2 fresh_evidence.py missing after install

Because install aborts before completing, downstream groups fail for a reason
unrelated to their own subject — a cascade that masks their true state.

## Fix (NOT applied — Phase 5, needs an adopted proposal)

Root-cause the bundler resolution in `tools/proofpunk-install.sh`. The auto-fix maps an
unresolved citation onto the wrong reference rather than failing with the real name.
Do not fix by deleting the citation — that hides the bundler defect.
