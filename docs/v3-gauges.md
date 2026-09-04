# Proofpunk v3 Gauge Board

Living scorecard. Every row's **Measured** column comes from a sealed
artifact under `evidence/v3-release/**`, cited by `path@sha256`, never from
scrollback or prose restated by hand. `tools/gauge-report.py` recomputes
every row on demand and is the authority when this file and a live run
disagree — re-run it and trust its output, not this document's cache.

Row status legend: **PASS** (meets target) · **UNMET** (measured, below
target) · **UNVERIFIED** (cited evidence does not resolve to a real sealed
file — never counted as passing) · **UNMEASURED** (no numeric target is
defined anywhere in the sealed sources; reported for trend tracking only,
does not gate release).

Regenerate: `python3 tools/gauge-report.py` — writes `gauge-report.md` and
`gauge-report.json` at repo root and exits non-zero until every gauge is
PASS.

| # | Lane | Gauge (unit) | Baseline | Target | Measured | Evidence |
|---|---|---|---|---|---|---|
| 1 | L12 | Skills passing spec basics — name matches dir, description ≤1024 chars, no unrecognized frontmatter fields (skills) | 18/18 | 18/18 | **18/18 — PASS** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 2 | L4 | stop-guard scout-substring false-PASS closed, mutation-proven (cases) | 47 -> 48 cases | mutation-proven (baseline = mutated+1, restore byte-identical) | **baseline=48 mutated=47 restored=48, byte_identical=True — PASS** | `evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring/VERDICT.md@sha256:43646ce82d6a4d2da30824812ac88cbf465833114b95167e2f70a6ccbb787aeb` (+3 step logs, see `gauge-report.json`) |
| 3 | L1 | Unresolved repo-tree citations, resolved relative to citing file (citations) | 30 -> 29 (top-level: 1 -> 0) | 0 | **29 unresolved (top-level: 0) — UNMET** | `evidence/v3-release/00-baseline/citation-integrity-finding.md@sha256:90969b64df5cc23d260e99b276822a09ff4e0123866730802d0004fa2ac04ec3` |
| 4 | L16 | Commands proven end-to-end at the real slash-command surface: typed -> flag mapping -> real execution -> observed result, single artifact (commands) | 0/6 | 6/6 | **0/6 — UNMET** | `evidence/v3-release/00-baseline/command-surface-map.md@sha256:9d76a58a16eb5246f48818666ba2b7d51a4242be64d8a824150d85636e0d3220` |
| 5 | L2/L3 | Release gates: all exit 0, exit codes captured separately from stdout (gates) | 4/4 rc=0 | 4/4 rc=0 (must be re-confirmed against current tree, not assumed from this cache) | **test-hooks.sh=0, test-installer.sh=0, dry-run-install.sh=0, verify-orchestration.py=0 — PASS** | `evidence/v3-release/00-baseline/gates-20260904T051258/exit-codes.txt@sha256:c6db6b3274cf4ee0b9a51a2b043d8234fb53e8f4a5d837f005a9aa19abc4a947` (+5 log files, see `gauge-report.json`) |
| 6 | L14 | Skill count, ground truth derived from `plugins/proofpunk/skills/*/SKILL.md`, never hand-restated (skills) | 18 | 18 | **18 — PASS** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 7 | L10 | Total description chars vs Claude Code's 1,536-char skill-listing budget (chars) | 13,949 (9.1x) | <=1,536 (1.0x) | **13,955 vs 1,536 (9.1x) — UNMET** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 8 | L10 | Median skill body size, context-economy proxy (bytes) | 6,266 | **UNMEASURED** — no numeric target defined in any sealed source (`description-budget-baseline.md`, `.planning/v3-criteria.md`); trend-tracking only, does not gate release | **6,186 bytes — UNMEASURED** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |

## Notes on rows with no defined target (UNMEASURED, not a silent pass)

- **#8 (median skill body size)** has a baseline measurement (6,266 bytes,
  `description-budget-baseline.md`) but **no target number appears anywhere
  in the sealed sources this tool can cite** — not in
  `description-budget-baseline.md`, not in `.planning/v3-criteria.md`, not
  in `docs/v3-reasoning-gate.md`. Inventing a threshold here would be a
  fabricated number; the row stays UNMEASURED against target and reports
  the real measured value for trend tracking only. It does not count toward
  the release-gate pass count.

## Rows explicitly not yet gauged

The following v3 lanes have discovery-level findings on disk but no
numeric gauge wired into `tools/gauge-report.py` yet — they are **not**
rows above, and their absence from this table is not a claim that they are
satisfied:

- **L5 lint lane** — `shellcheck` is absent on this host (finding F-T1,
  `docs/discovery-register.md`); the lane cannot run as written.
- **L6 `verify-runtime.py`** — proves only the *declared* graph
  (`verify-orchestration.py`), never the graph that actually ran at
  runtime (`evidence/v3-release/00-discovery/d3-gate-inventory.md`).
- **L9 memory bus / L18 forge-prompt fallback** — D1/D2 remain agent
  interpretations, not evidence-resolved (`docs/discovery-register.md`).
- **Lane B** — BLOCKED on an exact operator token
  (`APPROVE BARRIER DELTA` / `REJECT BARRIER DELTA` / `STOP`); never
  silently approved (`.planning/execution-ledger.json`).

Adding a gauge for any of these requires a sealed artifact under
`evidence/v3-release/**` to cite first — per this document's own rule,
UNMEASURED beats a fabricated number every time.

## Mutation proof of this tool

`tools/gauge-report.py` is mutation-proven: `evidence/v3-release/l-gauges/VERDICT.md`
records two independent mutations (missing-evidence-path, impossible-threshold),
each flipping exactly one named gauge from PASS to UNVERIFIED / UNMET
respectively, both reverted to byte-identical restores. See that directory
for the full three/five-arm capture and sha256 manifest.
