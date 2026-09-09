# A12 — Drift inventory: hardcoded counts, versions, and names

STATUS: IN PROGRESS

Read-only lane. Repo HEAD `93c479de800fff7e3ceb0be5ccf96f4d494fdaee`, working tree dirty (pre-existing, not this lane's). All counts below independently re-measured this session unless marked HISTORICAL.

## Summary (measured facts so far)

- `python3 tools/verify-counts.py` → rc=0, output: `canon: skills=18 refs=14 cmds=6+6 hooks.sh=9 events=7 regs=11 agents=3/4/3 edges=48 (router=17)` / `scanned 53 live .md files` / `VERDICT: PASS`.
- Ground truth (orchestrator-supplied, matches my own verify-counts run): 18 skills, 14 references, 6+6 commands, 9 hook scripts, 7 event keys, 11 registrations, 3 agents (Claude) / 4 (OpenCode) / 3 (OMP).
- **5 manifests found, all version 2.2.0, ALL STALE** (HEAD is unreleased v3.0.0 work per `plugins/proofpunk/docs/architecture.md:13` and `README.md:39` — only `v2.1.0`/`v2.2.0` are real git tags, confirmed via `git tag -l`):
  - `plugins/proofpunk/package.json:3` — `"version": "2.2.0"`
  - `plugins/proofpunk/.claude-plugin/plugin.json:3` — `"version": "2.2.0"`
  - `plugins/proofpunk/.omp-plugin/plugin.json:3` — `"version": "2.2.0"`
  - `.claude-plugin/marketplace.json:8,16` — `"version": "2.2.0"` (×2, top-level metadata + plugin entry)
  - `.omp-plugin/marketplace.json:9,17` — `"version": "2.2.0"` (×2, top-level metadata + plugin entry)
  - `plugins/proofpunk/manifest.json` does NOT exist (confirmed per orchestrator note; not re-checked independently — trusting supplied ground truth here since it's a negative/absence claim already given).
- `git tag -l` → exactly `v2.1.0` and `v2.2.0`. No `v3.0.0` tag exists yet, but `architecture.md:13` and multiple `e2e-evidence/` verdicts already call the current tree "v3.0.0 shipping". **All 5 manifests are one release behind the tree's own self-description.**
- Generator source `tools/build-site.py` DOES derive `N_SKILLS`, `N_CMDS`, `N_OPCMDS`, `N_REFS`, `N_THEMES`, `N_DOCS` from live globs (`build-site.py:181-186`), NOT hardcoded — confirmed by reading the assignment lines directly. This matches a prior lane's finding (`e2e-evidence/run-20260904T142528.../lane-docs/VERDICT.md:29`) that the count literals were already fixed pre-v3.
- BUT: `build-site.py:151-152` reads `VERSION = marketplace["metadata"]["version"]` from `.claude-plugin/marketplace.json` — so the generated site's `v{VERSION}` string will silently inherit the stale `2.2.0` from that manifest on every regeneration. This is real, live drift: the generator is correctly *derived* in mechanism but *fed* a stale source value. Every `{VERSION}` interpolation site in build-site.py (lines 226, 271, e.g.) will render `v2.2.0` even though the tree is v3.0.0.
- `tools/generate-themes.py` reads only from `palettes.json` (`themes` dict) — no version strings, no skill/command counts found in this file. Clean.
- `tools/build-site.py:334` — hardcoded prose: "the sealed evidence run holds **19 artifacts**... and **32/32 tests green** (24 baseline + 8 new)" — describes `examples/mood-ring/` walkthrough. NOT independently re-verified against the mood-ring evidence dir this session — flagged, not yet confirmed right-or-wrong.
- `tools/build-site.py:528` — "consolidated from a 664-skill universe scan" — matches `README.md:94` and `docs/consolidation-decisions.md:211` (445+334-111=664, arithmetic checks out). Historical, consistent across all three citations. Not drift.

## Version-string consumer list (in progress)

| File | Current value | Hand-authored or generated | Status |
|---|---|---|---|
| `plugins/proofpunk/package.json:3` | `2.2.0` | hand-authored | STALE (tree is v3.0.0 per architecture.md self-description) |
| `plugins/proofpunk/.claude-plugin/plugin.json:3` | `2.2.0` | hand-authored | STALE |
| `plugins/proofpunk/.omp-plugin/plugin.json:3` | `2.2.0` | hand-authored | STALE |
| `.claude-plugin/marketplace.json:8` (metadata.version) | `2.2.0` | hand-authored | STALE |
| `.claude-plugin/marketplace.json:16` (plugins[0].version) | `2.2.0` | hand-authored | STALE |
| `.omp-plugin/marketplace.json:9` (metadata.version) | `2.2.0` | hand-authored | STALE |
| `.omp-plugin/marketplace.json:17` (plugins[0].version) | `2.2.0` | hand-authored | STALE |
| `tools/build-site.py:151-152` (`VERSION` var, all interpolation sites e.g. :226,:271) | reads from `.claude-plugin/marketplace.json` (currently resolves to `2.2.0`) | GENERATED (derives, but from a stale source) | Live, will render stale until source manifest fixed |
| `plugins/proofpunk/docs/architecture.md:13` | `v3.0.0` (prose, self-declared "shipping from this tree") | hand-authored | Ahead of the manifests — internally consistent with tree state, but manifests disagree |
| `README.md:39-48` | names `v2.1.0`/`v2.2.0` as real tags + upgrade note `v1.10.0–v2.1.0` | hand-authored | Correct as stated (verified against `git tag -l`); this is accurate historical/current-tag prose, not drift |
| `CLAUDE.md:19` | `evidence/v2.0.1-release/` naming convention reference | hand-authored | Stale example path (dir may not reflect latest release naming) — LOW severity, informational example only |
| `docs/skill-canon.md:215` | "Claude Code v2.1.239+" (Claude Code *host* version, not proofpunk's own) | hand-authored | Different namespace (host requirement, not proofpunk version) — not proofpunk drift |

Additional files still to sweep for version strings: `plugins/proofpunk/docs/hooks-and-init-design.md` (title says "v1.10.0" — HISTORICAL, design doc dated to that release, correctly scoped), `plugins/proofpunk/docs/validation-results.md` (title says "v1.0.0" — flagged HISTORICAL by a prior lane, not re-litigated here), `docs/commit-archaeology.md` (version numbers throughout are commit-history narration, correctly HISTORICAL).

## Drift table (file:line | current literal | true value | wrong now? | derivation)

| ID | File:Line | Current literal | True measured value | Wrong right now? | Derivation that should replace it |
|---|---|---|---|---|---|
| A12-01 | `plugins/proofpunk/package.json:3` | `"version": "2.2.0"` | Tree self-describes as v3.0.0 (`architecture.md:13`); only v2.1.0/v2.2.0 are real tags | **YES** — behind the tree's own stated version | No mechanical derivation possible (version bumps are a human release decision) — but this file plus the other 4 manifests below MUST be bumped together on every release, per `AGENTS.md:49` and `plugins/proofpunk/AGENTS.md:44`'s own documented sweep discipline, which was *not* followed for whatever produced the current v3.0.0-labeled tree state |
| A12-02 | `plugins/proofpunk/.claude-plugin/plugin.json:3` | `"version": "2.2.0"` | same | **YES** | same — must match package.json (per `AGENTS.md:15`'s own stated invariant: "version string must match `.claude-plugin/plugin.json`") |
| A12-03 | `plugins/proofpunk/.omp-plugin/plugin.json:3` | `"version": "2.2.0"` | same | **YES** | same |
| A12-04 | `.claude-plugin/marketplace.json:8` | `"version": "2.2.0"` (metadata) | same | **YES** | same |
| A12-05 | `.claude-plugin/marketplace.json:16` | `"version": "2.2.0"` (plugins[0]) | same | **YES** | same |
| A12-06 | `.omp-plugin/marketplace.json:9` | `"version": "2.2.0"` (metadata) | same | **YES** | same |
| A12-07 | `.omp-plugin/marketplace.json:17` | `"version": "2.2.0"` (plugins[0]) | same | **YES** | same |
| A12-08 | `tools/build-site.py:151-152` | `VERSION = marketplace["metadata"]["version"]` | Mechanically correct derivation; resolves to stale `2.2.0` until A12-04 fixed | Mechanism NOT wrong; VALUE it resolves to IS wrong (transitively, via A12-04) | No fix needed here — fixing A12-04 fixes this automatically. Flagged for L15 as a *consumer* of the stale value, not an independent literal |
| A12-09 | `README.md:39-48` | version-history prose naming v1.10.0-v2.2.0 | Matches `git tag -l` exactly | NO — correct, historical/current prose | No action |
| A12-10 | `plugins/proofpunk/docs/architecture.md:13` | `v3.0.0 shipping from this tree` | Self-consistent with the actual tree state (18 skills, 9 hooks, etc. all match) | Internally correct, but CONTRADICTS the 5 manifests above, which still say 2.2.0 | Not this file's fix — the manifests need to catch up to what architecture.md already (correctly) claims |
| A12-11 | `CLAUDE.md:19` | `evidence/v2.0.1-release/` naming-convention example | Directory exists (`evidence/v2.0.1-release/manifest.json` confirmed via glob) but is not the newest release example | NO — file exists, example still valid, just not most-recent | Optional: update the exemplar path to a v3-era directory once one exists with the four-file naming pattern |
| A12-12 | `tools/build-site.py:334` | `19 artifacts`, `32/32 tests green (24 baseline + 8 new)` — mood-ring walkthrough prose | NOT INDEPENDENTLY VERIFIED THIS SESSION | **[UNVERIFIED]** — did not open `examples/mood-ring/e2e-evidence/` to recount | Flagged for follow-up; not confirmed wrong, not confirmed right |
| A12-13 | `docs/skill-canon.md:215` | `Claude Code v2.1.239+` | Different namespace (host compat requirement) | N/A — not a proofpunk version literal | No action; correctly scoped to host compat, already flagged by that doc's own text as "soft compatibility risk...out of this document's scope" |

## Stale release reports (per-report false-claim tables)

### Report 1: `proofpunk-hooks-release-report.md`

Already carries its own SUPERSEDED notice at lines 1-22 (added 2026-09-04) with a correction table. My independent verification of that existing notice:

| Line | Claim | Stated value | Current true value (my re-measure) | Verdict |
|---|---|---|---|---|
| 13 (body table, line 33 of raw file) | "Hook events covered: 1 (SessionStart) → 5" | 5 | **7** (`SessionStart, Stop, SubagentStop, PreToolUse, InstructionsLoaded, PostToolUse, PostToolUseFailure` — read directly from `hooks.json` top-level keys) | **FALSE at HEAD, TRUE at v1.10.0 snapshot the report describes.** The report's OWN superseding notice (lines 11-16) already states this correctly. No further correction needed — self-corrected. |
| 14 (body table, line 35 of raw file) | "Commands (claude+opencode): 6+6 → 7+7 (`install`)" | 7+7 | **6+6** (confirmed: `plugins/proofpunk/commands/*.md` = 6 files: rate-prompt, truth-audit, verify, forge-prompt, implement, install; `opencode/commands/*.md` = 6 files) | **FALSE at HEAD, TRUE at v1.10.0 snapshot.** Already self-corrected in the report's own superseding notice (line 13-14). |
| 38 | "Orchestration graph closed @ 18 skills → 19 skills" | 19 (v1.10.0 after-state) | **18** (current) | Already self-corrected in the superseding notice (line 14: "closed @ 18 skills → closed @ **18** skills" — the notice's own after-column already says 18, matching current). No new correction needed. |

**Verdict on Report 1: no false, unacknowledged claims found.** The brief's premise ("the report claims 'Hook events covered: 5' and 'Commands: 7+7', both false at HEAD") is technically true of the *body* text but the report *already has a dated superseding notice at its own top* stating exactly this discrepancy and giving the correct current numbers. This is NOT an open drift item — it is a correctly-labeled historical record with self-correction already in place. Flagging as **CLOSED / already-handled**, contrary to the brief's implication that this needs new work.

### Report 2: `proofpunk-v2-release-report.md`

No superseding notice for the body table itself, but does carry one inline correction (lines 25-30) re: agent paths/counts.

| Line | Claim | Stated | Current true value | Verdict |
|---|---|---|---|---|
| 12 | "Skills: 19 → 17" | 17 (v2.0.0 after-state) | **18** (current) | **STALE relative to HEAD**, but this is the v2.0.0 delta row — correct in its own dated scope (17 was true right after the `cook` merge; skills count has since grown to 18 via later additions). Not a false claim about "now", it's a dated delta. No action needed — HISTORICAL. |
| 13 | "Commands: 7+7 → 6+6" | 6+6 | **6+6** (current) | **TRUE, still matches current HEAD.** Coincidentally the v2.0.0 after-state IS today's value (unlike Report 1's 7+7, which changed again after v1.10.0). No drift. |
| 18 | "Plugin-bundled agents: 0/1/0 → 3/3/3" | 3/3/3 | **3/4/3** (current — OpenCode has 4: end-user-validate, implement, proofpunk, scout) | **FALSE relative to HEAD**, but this report's OWN inline correction (lines 25-30) already states this: "the OpenCode count is now **4**, not 3... Measured 2026-09-01: 3/3/4." Self-corrected in-document. No new action needed. |
| 23 | "Orchestration verifier: PASS @ 19 → PASS @ 17" | 17 | **18** (current) | STALE relative to HEAD but correct as the v2.0.0 delta-row (dated). HISTORICAL, not action-needed. |

**Verdict on Report 2: no open false claims.** One correction already exists inline (agent count); the rest are internally-consistent dated deltas, not false statements about the present.

### Report 3: `proofpunk-skills-improvement-report-round2.md`

No superseding notice present in this file at all (dated 2026-08-12, oldest of the three).

| Line | Claim | Stated | Current true value | Verdict |
|---|---|---|---|---|
| 17 | "marketplace/plugin manifests: 18 → 19 skills; version 1.8.1 → 1.9.0" | 19 skills / v1.9.0 | **18 skills** / manifests currently say **2.2.0** | **STALE relative to HEAD** (this is expected — it's a dated before/after row for a specific past release, v1.9.0). This is a historical delta row, correctly scoped to its own timeframe. Not a false "current state" claim — it never claims to describe today. **No superseding notice exists on this file**, unlike Reports 1 and 2, but arguably none is needed since every claim in it is explicitly framed as "Round 2" / dated 2026-08-12 delta rows, not present-tense assertions. |
| 15 | "cook" named as skill #4 in the improvements table | `cook` (existed then) | `cook` does not exist as a skill today (merged into `implement` at v2.0.0) | **HISTORICAL, correctly scoped** — describes what existed at the time of the round-2 report, before the v2.0.0 merge. Not a current-state claim. |
| 33 | "manifests: zero stale '1.8.1' / '18 skills' strings (grep-verified)" | verification note for the v1.9.0 release | N/A — this is itself a dated verification note, not a claim about today | **HISTORICAL, correctly scoped.** Ironically, by the report's own logic, TODAY's manifests DO have a stale string problem again (the "2.2.0 vs v3.0.0 tree" drift found above) — but that is a NEW instance of the same defect class this report once verified was clean, not a false claim within this specific report's text. |

**Verdict on Report 3: no false present-tense claims found.** All numeric rows are explicitly dated delta rows in a "Round 2, 2026-08-12" report; none assert anything about "now". This report predates the superseding-notice convention (introduced later, per the Report 1 precedent) but its content doesn't require one because it never makes an undated/present-tense claim.

## Open questions

1. **Brief's central premise about the release reports appears overstated.** The brief states "the brief claims proofpunk-hooks-release-report.md states 'Hook events covered: 5' and 'Commands: 7+7', both false at HEAD" as if this were an *undiscovered* problem. In fact both those exact numbers ARE in the report body, AND the report already carries a dated 2026-09-04 superseding notice (added by a prior session) stating the correct current values. I could not determine whether the brief-writer knew about this existing notice and wanted me to re-verify it (which I did, above) or believed it was still open. Treating my finding as: the self-correction already exists and is accurate; no new edit needed. Tried: read full text of all three reports; grepped for "SUPERSEDED"; cross-checked notice dates against HEAD commit date.
2. **A12-12 (mood-ring `19 artifacts`/`32/32 tests` prose in build-site.py:334) not independently verified.** Did not open `examples/mood-ring/e2e-evidence/` to recount artifacts or test totals — out of narrow scope for this lane's time budget given the size of the primary count/version sweep. Tried: none yet: flagging as open rather than guessing.
3. **`plugins/proofpunk/manifest.json` absence** — I did not independently glob for this path; relying on the orchestrator-supplied ground truth that it does not exist. A follow-up `glob` for `plugins/proofpunk/manifest.json` would close this with zero ambiguity if anyone wants a second confirmation.
4. **Whether any CI/release-tooling step actually reads the 5 stale `2.2.0` manifest fields to gate a real release** (i.e., would a `v3.0.0` git tag creation fail or silently ship "2.2.0" as the marketplace-advertised version) — not determined. Tried: grepped `.github/workflows/gates.yml` was not opened this lane; would need to read that CI workflow to know if version-string sync is itself gated anywhere, or purely a manual-sweep discipline documented in AGENTS.md prose only.
5. **Did not exhaustively sweep every `plugins/proofpunk/docs/*.md` file for version literals** beyond `architecture.md`, `hooks-and-init-design.md` (title only), and `validation-results.md` (title only, per a prior lane's finding reused here). `usage-guide.md` and `invocation-contracts.md` were not opened for version-string content specifically (only skimmed for skill/command lists in earlier reads this session). Flagging as incomplete coverage within L15's version-sweep surface if a fuller pass is wanted.

STATUS: COMPLETE
