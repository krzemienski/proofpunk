# LaneImprovements VERDICT

HEAD at start: `93c479de800fff7e3ceb0be5ccf96f4d494fdaee`.
Evidence: `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-improvements/`.
Ledger: `/Users/nick/proofpunk/docs/improvement-ledger.md`.

## What changed

| File | What |
|---|---|
| `tools/verify-mutation-artifact.py` NEW sha256=`631ad2589922dc15c2c7ba94a1b3244294de77eb5de2d8e70781739fce1641be` | Class 1 detector |
| `tools/verify-shipped-vs-active.py` NEW sha256=`6f2b22136fd3c61f61cc6a24a36b8c9fb4e29ac174d0d1f6b80c9bc2814a5099` | Class 3 detector |
| `tools/verify-proof-vocab.py` NEW sha256=`18cc78f7a65b2361a90e5f5e47c94eb982171ae7de8b144cd65841375576cf4a` | Class 4 detector |
| `.github/workflows/gates.yml:84-97` | CI steps for router-links, Class 1/3/4, and sibling Class 2 |
| `plugins/proofpunk/skills/proofpunk/SKILL.md:99` | doctrine-table row for `run-trace-schema.md` |
| `plugins/proofpunk/skills/end-user-testing/SKILL.md:133-135` | executing skill loads `run-trace-schema.md` |
| `tools/AGENTS.md:20-23` | Key Files rows for the four class detectors |
| `.planning/plugin-improvements.md:92-123` | `93c479d` re-measurement table |
| `docs/improvement-ledger.md` NEW | 18-item status + measured-success table |

Not edited: `tools/sdk_probe.py`, `tools/verify-command-surface.py`, `tools/gauge-report.py`, `tools/INSTALL.md`, `docs/architecture.md`, `plugins/proofpunk/hooks/*`, `tools/test-hooks.sh`, `tools/verify-counts.py`, plugin manifests.

## What was driven

`python3 tools/verify-{mutation-artifact,shipped-vs-active,proof-vocab,router-links}.py` — clean + named mutations + restores. Exit codes in sibling `.rc` files, never piped.

## Per-claim

| Claim | Verdict | Citation |
|---|---|---|
| All 18 backlog items re-measured at `93c479d` with no inherited labels | **PASS** (script-level) | `docs/improvement-ledger.md` table; `.planning/plugin-improvements.md:92-123` |
| Item 18 VOID premise holds | **PASS** (script-level) | `evidence/AGENTS.md:22` is capture-immutability; `:24` is secrets |
| ≥10 improvements implemented | **PASS** (script-level) | ledger "Proved vs attempted": proved **10**, attempted **12** |
| Class 1 mutation-proven | **PASS** (script-level) | `step-14-mutation-artifact-after-tighten.rc`=0 → `step-19-class1-mutated-new-harness.rc`=1 names `verify-dummy-mutation.py` → `step-20-class1-restored.rc`=0 |
| Class 3 mutation-proven | **PASS** (script-level) | `step-10-shipped-vs-active-after.rc`=0 → `step-21-class3-mutated-uncited-ref.rc`=1 names `_mutation-uncited.md` → `step-22-class3-restored-after-dummy.rc`=0 |
| Class 4 mutation-proven | **PASS** (script-level) | `step-11-proof-vocab-after.rc`=0 → `step-17-class4-mutated-bare-DONE.rc`=1 names `STATUS: DONE` → `step-18-class4-restored.rc`=0 |
| Router doctrine table still green | **PASS** (script-level) | `step-29-router-links-final2.log` `doctrine_refs=14 all_resolved=true` rc=0 |
| Final after-arms green | **PASS** (script-level) | `step-26`/`step-27`/`step-28`/`step-29` all rc=0 |

## Open / UNRESOLVED

See `docs/improvement-ledger.md` §Open. Headline: #3 PARTIAL by design; `sdk_probe.py` UNPROVEN-LIVE; `verify-counts.py` UNPROVEN-SIBLING; dead `"functional validation"` string is LaneDocumentation; I7 in_evidence identity is not mutation-proven against a diverge; this lane is script-level only.
