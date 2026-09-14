<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-08-23 | Updated: 2026-08-23 -->

# evidence

## Purpose

Per-release verification captures: the actual stdout of the three release-verification commands (`test-hooks.sh`, `dry-run-install.sh`, `verify-orchestration.py`) plus full-install output, one directory per release. This is the proof that a release claim ("hooks 19/19, dry-run 0 fails, verifier PASS") was executed, not asserted.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `v2.0.1-release/` | v2.0.1: test-hooks 19/19, dry-run 0 fails, verifier PASS, full-install output |
| `v2-release/` | v2.0.0: dry-run, test-hooks, verify-orchestration outputs |
| `hooks-release/` | v1.10.x hooks release: the same trio |

## For AI Agents

### Working In This Directory

- Read-only evidence: never edit, backfill, or "clean up" captures — a modified capture is a fabricated claim.
- **Never `git add` a run directory until that run is finished and sealed.** Committing a run's steps or its `evidence-inventory.txt` mid-run makes every later addition to that run a rewrite of a committed capture, which `tools/verify-evidence-immutability.py` correctly refuses. Measured 2026-09-14: this single workflow mistake produced three separate immutability failures in one session (`REWRITTEN 744B -> 864B`, `222B -> 332B`, `9046B -> 9407B`). Restoring the inventory alone does not fix it — a manifest that omits files the run now contains is a *false* manifest.
- Corollary: if a finding must be recorded after a run is committed, open a **new** run directory (`fresh_evidence.py init-run <slug>`) and carry the correction there with an explicit supersession header naming the superseded step. A committed capture is never edited to agree with a later finding; the record shows both what was believed and what replaced it.
- New release → new `<release>-release/` directory; copy the four-file naming pattern from `v2.0.1-release/`.
- Secrets must never appear in evidence (enforced by `evidence-guard.sh`); if one leaks, rotate the secret, do not just delete the file.

### Testing Requirements

- A release is not claimed done until this directory holds fresh, non-empty captures for every verification command run.

## Dependencies

### Internal

- Produced by `tools/test-hooks.sh`, `tools/dry-run-install.sh`, `tools/verify-orchestration.py`, and full installer runs.

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
