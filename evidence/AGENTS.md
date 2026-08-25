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
- New release → new `<release>-release/` directory; copy the four-file naming pattern from `v2.0.1-release/`.
- Secrets must never appear in evidence (enforced by `evidence-guard.sh`); if one leaks, rotate the secret, do not just delete the file.

### Testing Requirements

- A release is not claimed done until this directory holds fresh, non-empty captures for every verification command run.

## Dependencies

### Internal

- Produced by `tools/test-hooks.sh`, `tools/dry-run-install.sh`, `tools/verify-orchestration.py`, and full installer runs.

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
