# LaneDocumentation VERDICT

Lane: `LaneDocumentation`
Tree: `/Users/nick/proofpunk` @ start SHA `93c479d` (working tree dirty with this lane's edits)
Evidence: `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/`

## Detector ownership

Main ruled this lane owns `tools/verify-counts.py` (Class-2). LaneImprovements takes Classes 1/3/4 (`verify-mutation-artifact.py`, `verify-shipped-vs-active.py`, `verify-proof-vocab.py`). Recorded via hub; they confirmed they will not create or edit `verify-counts.py`. **Exactly one of us built it: this lane.**

## Derived canon (recomputed this lane, never copied)

```
skills=18 refs=14 cmds=6+6 hooks.sh=9 events=7 regs=11
agents=3/4/3 (claude/opencode/omp)
edges=48 (router=17, among delivery=31)
```

The work-order's "13 references" is **stale**. `plugins/proofpunk/references/` globs 14 files; the 14th is `run-trace-schema.md`. The work-order's "47 edges" is **wrong**: `verify-orchestration.py`'s `CALLS` parse of every `## Skill calls` table yields 48 (the omitted edge is `tui-testing → end-user-testing`).

## What changed (file:line)

### ACTIVE GUIDANCE from the drift inventory

| Item | Status | Citation |
|---|---|---|
| `README.md:402` `functional-validation` in live downstream table | **Already fixed** at HEAD. Current `README.md:402` reads `end-user driving per the shared runbooks (web/API equivalent)`. Historical `functional-validation` remains at `README.md:91` (v1.9.0 changelog — HISTORICAL, not rewritten). | `README.md:402` |
| `.claude-plugin/plugin.json:4` + `.omp-plugin/plugin.json:4` `"functional validation"` as first capability | **Fixed this lane.** Both descriptions now start the skill list with `"end-user testing"`. Descriptions are byte-identical (`len=1282`). | `plugins/proofpunk/.claude-plugin/plugin.json:4`, `plugins/proofpunk/.omp-plugin/plugin.json:4` |
| `package.json:4` third copy of the same string | **Already diverged and already clean.** `package.json:5` is `"Proofpunk OMP plugin — skills, commands, themes, and the doctrine-guard extension."` — no dead skill name. Not forced byte-identical with the two marketplace descriptions: it is the OMP extension manifest, not marketplace copy. Forcing identity would overwrite a correct, shorter string. | `plugins/proofpunk/package.json:5` |
| `tools/build-site.py:360` hardcoded `"18 skills"` | **Already fixed.** Live line is `f"... {N_SKILLS} skills where end-user testing is the only PASS."` with `N_SKILLS = len(skills)` at `:181`. Not edited (not in exclusive file list; already derived). | `tools/build-site.py:181,360` |
| `tools/INSTALL.md` OpenCode "1 agent" | **Already fixed.** Live lines name 4 agents (`INSTALL.md:58`, `:140`, `:229`). | `tools/INSTALL.md:58,140,229` |

### Live counts this lane corrected (not in the inventory as defects, but the tree disagrees)

- `plugins/proofpunk/docs/architecture.md` header v2.2.0 → current-tree v3.0.0 shipping (`:13`).
- Layers table: hooks 7-scripts/6-events → **9 scripts / 7 event keys / 11 registrations**; references 13 → **14** (`:30-31`). Doubled `\|\|` pipes from the first patch pass were repaired.
- §1 harness paragraph now names `verify-citations.py`, `verify-harness-integrity.py`, `verify-router-links.py`, `gauge-report.py`, and `verify-counts.py` (`:35-` after rewrite).
- Call-table heading: 47/30 → **48/31**, derived from the orchestration parse (`:126`).
- `tui-testing` row: leaf → calls `end-user-testing`; `end-user-testing` callers 12 → **13** (`:144,147`).
- Depth table: `tui-testing` moved from depth 0 to depth 1 (`:171-178`).
- §4 hook intro: no longer restates a stale 6/7/8 table; cites `docs/hook-enforcement-map.md`. Decision-surface gained `bash-write-snapshot.sh` and `bash-write-notice.sh` rows and the `stop-guard.sh` fail-open `enforcement OFF (<reason>)` path.
- §6 `--hooks` is documented as **opt-in** (`WITH_HOOKS=0` default), not "automatic on plugin installs".
- Measurement footer: 13 refs → 14; 47 edges → 48 with the omitted edge named (`:How this was measured`).
- `README.md:420` mermaid `13 shared doctrine files` → **14**.
- `plugins/proofpunk/AGENTS.md:30-31` OpenCode 4th agent named; references 13 → 14.
- `plugins/proofpunk/README.md:51-58` added `run-trace-schema.md`.
- `plugins/proofpunk/docs/usage-guide.md` OpenCode install text: 1 primary agent → **4 agents**.
- `AGENTS.md:43` and `plugins/proofpunk/AGENTS.md:50` testing requirements now name `python3 tools/verify-counts.py`.

### INSTALL.md flag/example alignment against `proofpunk-install.sh` `case` (`:126-150`)

Added the flags the `case` block accepts that the option tables omitted: `--with-doctrine`, `--inject-memory [FILE]`, `--hooks` (moved into Inspection so every `case` arm is in a table), `--verify`, `--backup`. `--inject-claude-md` is labelled a legacy alias.

Examples that would not run as written, **fixed**:

- Example 7 used only `--inject-claude-md`; now uses `--inject-memory` (the flag the 60-second block already passed) and names the alias.
- Example 8 pinned `--ref v1.8.0`. Live tags are **v2.1.0 and v2.2.0** (`git tag -l`). Now `--ref v2.2.0`.
- Example 6 `cd Proofpunk` after cloning `proofpunk` (default dir is lowercase). Now `cd proofpunk`.
- Exit-code table claimed `2 = no transcripts`. The installer never exits 2 (`die` → 1; `--only` miss → 3; success/`--list`/`--help` → 0). Row 2 removed.

## What I drove

Unpiped:

1. `python3 tools/verify-counts.py` on the clean (post-edit) tree → rc=0.
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-01-clean.log`
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-01-clean.rc` (`0`)
2. Named mutation `19 skills` in `plugins/proofpunk/AGENTS.md:8` (the live "18 skills, 6 commands" purpose line) → rc=1, output names the file and line:
   `plugins/proofpunk/AGENTS.md:8: 19 skills (live accepts [17, 18])`
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-02-mutation.log`
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-02-mutation.rc` (`1`)
3. Restore from pre-mutation copy → byte-identical, rc=0.
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-03-restored.log`
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-03-restored.rc` (`0`)
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-04-restore-identity.txt`
4. Post-AGENTS.md-testing-line edit: rc=0.
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-05-post-agents-edit.log`
   `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-docs/step-05-post-agents-edit.rc` (`0`)

A first mutation arm used `17 skills`, which the detector correctly accepts (18 total − 1 router = 17 delivery). That arm is not the proof; the `19 skills` arm is.

## Per-claim

| Claim | Verdict | Proof |
|---|---|---|
| `python3 tools/verify-counts.py` exits 0 on the clean tree | **PASS** | `step-01-clean.rc`, `step-05-post-agents-edit.rc` |
| Mutation-proven red-by-name | **PASS** | `step-02-mutation.log` names `plugins/proofpunk/AGENTS.md:8: 19 skills`; restore byte-identical (`step-04-restore-identity.txt`) |
| Detector does not flag historical provenance | **PASS** | skips `evidence/`, `e2e-evidence/`, `docs/` (generated + dated v3 logs), `.planning/`, dated report basenames, `consolidation-decisions.md`, `validation-results.md`, `improvements.md`, `hooks-and-init-design.md`, and lines matching `v1.x` / `17→19→18` / `original N skills`. `README.md:91` (v1.9.0 `functional-validation`) is not flagged. |
| Every ACTIVE GUIDANCE item fixed-and-verified or recorded already-fixed | **PASS** | table above; three of five already fixed at HEAD with `file:line` |
| Zero historical provenance prose rewritten | **PASS** | Did not edit `proofpunk-hooks-release-report.md`, `proofpunk-skills-improvement-report-round2.md`, `consolidation-decisions.md`, `validation-results.md`, `improvements.md`, `hooks-and-init-design.md`, `evidence/v3-release/00-baseline/drift-inventory.md`, or any `evidence/` file. `README.md:91` v1.9.0 changelog left intact. Architecture §8 drift-history paragraph (`17→19→18`) left intact. |
| `docs/architecture.md` covers skills, commands, hooks, references, agents, installer, gates, with counts derived | **PASS** | The live architecture file is `plugins/proofpunk/docs/architecture.md` (no `docs/architecture.md` at repo root — that path is generated HTML `docs/doc-architecture.html`, which this lane is forbidden to hand-edit). Counts in the markdown source now match the globs. |
| "47 edges" derived or marked UNVERIFIED, never restated unchecked | **PASS** | Re-derived as **48** from the same `## Skill calls` parse `verify-orchestration.py` uses. Heading and measurement footer updated. The old "47" appears only as the previous (wrong) figure being corrected. |
| INSTALL.md flags match the installer `case` block | **PASS** | Every `case` arm in `tools/proofpunk-install.sh:126-150` now has a table row. Examples that would not run were fixed and named above. |

## Historical prose — explicit check

I read `evidence/v3-release/00-baseline/drift-inventory.md` in full before editing. Every row it classified HISTORICAL PROVENANCE PROSE was left untouched. Rewriting those to today's 14/48/7 would have destroyed accurate release history (the exact failure the inventory exists to prevent).

## Open / UNRESOLVED

- **`docs/architecture.md` at repo root does not exist.** The source of truth is `plugins/proofpunk/docs/architecture.md`; `docs/doc-architecture.html` is generated by `tools/build-site.py` and was not regenerated (this lane does not run project-wide builds; siblings are mid-flight). The generated HTML still says 13 refs / 47 edges until someone reruns `build-site.py`.
- **`package.json` description is not byte-identical with the two `plugin.json` files.** Already-clean shorter OMP-extension copy. The inventory treated it as a third copy of the marketplace string; the live file is not that string. Forcing identity would be a new defect.
- **`tools/AGENTS.md` Key Files** does not yet list `verify-counts.py`. LaneImprovements owns that file; I asked them to add one line. Not edited here.
- **Router Shared-doctrine table** (`skills/proofpunk/SKILL.md:84-98`) still lists 13 reference rows — it does not cite `run-trace-schema.md`. LaneImprovements said they would add that citation; I did not touch skill files.
- **`verify-counts.py` is not in `.github/workflows/gates.yml`.** LaneImprovements owns gates.yml. Detector exists and is mutation-proven; CI wiring is their Class-1/3/4 batch plus whatever they add.
- **First mutation arm (`17 skills`) was a false-green** because 17 is a legitimate delivery-skill count. The detector's `expected_for("skills")` accepts `{18, 17}`. That is correct for "calls all 17 others" prose; it means a live "17 skills" inventory claim would also pass. Accepting 17 is the smaller lie (router-vs-delivery is real arithmetic). A stricter "only 18 in inventory sentences" parser is UNBUILT.
- **`tools/build-site.py:360` already uses `N_SKILLS`.** Confirmed; not this lane's edit. If a sibling reverts that line, `verify-counts.py` will not catch it (it scans `.md`, not `.py`).
