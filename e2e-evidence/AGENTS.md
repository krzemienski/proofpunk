<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-09-04 | Updated: 2026-09-04 -->

# e2e-evidence

## Purpose

Run-scoped end-to-end evidence: one directory per validation run, holding the
actual captured stdout/stderr, screenshots, and verdicts that back a
completion claim. Companion to `../evidence/` (per-release captures); this
directory holds per-run captures produced through the fresh-evidence
lifecycle (`end-user-testing` → `scripts/fresh_evidence.py`).

## Run directory naming

Canonical convention: `run-<ISO8601-compact>-<slug>/` — e.g.
`run-20260901T233102-doc-correction-final/`. The timestamp is UTC
`%Y%m%dT%H%M%S`, stamped by `fresh_evidence.py init-run <slug>`, so
lexicographic directory order equals chronological run order.

20 historical directories predate the convention and carry bare names
(`run-slug`: `run-p4/`, `run-docs18-b1/`, `run-final-parity/`,
`run-sdk-probes/`, `run-flag-drift/`, …). They are intentionally left
untouched — captures are immutable — so bare names cannot be chronologically
ordered without opening each verdict or checking mtimes. Do not rename them;
every new run takes the timestamped form.

## Run directory contents

Minimum a fresh (2026-09-01+) run must contain — enforced by
`fresh_evidence.py validate`:

| File | Role |
|------|------|
| `.run-meta` | `run_id=` and `started=<ISO Z>` lines; run-start timestamp that artifact freshness is measured against |
| `step-NN-<slug>.*` | ≥1 non-empty, sequentially numbered capture (`step-01-…`, `step-02-…`; prefix from `next-step`); mtime must be ≥ run start |
| `evidence-inventory.txt` | sealed by `seal`: v2 digest inventory (`name size sha256` per artifact plus a `sealed=… count=… total_bytes=` line); a run whose files changed after sealing is not citable |
| `VERDICT.md` | human-readable verdict/summary (conventional in current runs; not machine-enforced) |

Older eras differ and stay as captured: 2026-08-24 runs pair `step-*.txt`
(sometimes split `-stdout`/`-stderr`) with `summary.json`; 2026-08-27 runs
pair steps with `verdict.json` and often predate digest sealing. Loose
artifacts at this directory's root (`FIXES.md`, `mine-intent-matrix.json`)
follow the same immutability rule.

## For AI Agents

### Working In This Directory

- Read-only evidence: never edit, backfill, rename, or "clean up" captures —
  a modified capture is a fabricated claim.
- New run → from repo root run
  `python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py init-run <slug>`,
  then `next-step` per capture, `seal` when done, `validate` before citing.
- The "active run" is the most recently modified `run-*` subdirectory —
  finish or seal one run before starting another, or `next-step`/`seal`/
  `validate` will target the wrong directory.
- Secrets must never appear in evidence (enforced by `evidence-guard.sh`);
  if one leaks, rotate the secret, do not just delete the file.

### Testing Requirements

- A claim is not PASS until this directory holds a fresh, sealed, non-empty
  capture for every command or screenshot the claim cites, each citable by
  full path.

## Dependencies

### Internal

- Produced by `plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py`
  (init-run / next-step / seal / validate) and by the verification commands it
  captures (`tools/test-hooks.sh`, `tools/test-installer.sh`,
  `tools/dry-run-install.sh`, `tools/verify-orchestration.py`).

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
