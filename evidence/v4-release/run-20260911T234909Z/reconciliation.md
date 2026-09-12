# Proofpunk v4 release reconciliation

Run: `run-20260911T234909Z`

## Criteria

| Criterion | Status | Evidence | Note |
|---|---|---|---|
| AC1 ACQUIRE | BLOCKED | `ac1-ac6-live-flow-blocked.txt`; `../e2e-evidence/run-20260911T235357-v4-release/step-01-structural-and-blocked-receipts.txt` | No executable ACQUIRE command exists in the shipped plugin surface; live SDK probe timed out before producing a usable session. Fresh evidence inventory is sealed and validated. |
| AC2 live host/plugin mismatch and control | BLOCKED | `ac2-live-sdk-blocked.txt`; `../e2e-evidence/run-20260911T235357-v4-release/evidence-inventory.txt` | `claude_agent_sdk` is importable, but the live probe failed to load the local plugin and the environment has no usable `ANTHROPIC_API_KEY`; no PASS substituted. |
| AC3 count renderer | PASS | `render-counts.txt` | `python3 tools/render-counts.py --check` exited 0. |
| AC4 structural gates | PASS | `hooks-orchestration-integrity.txt`, `orchestration.txt`, `harness-integrity.txt` | All commands exited 0. |
| AC5 counts and descriptions | PASS | `counts.txt` | `python3 tools/verify-counts.py` exited 0. |
| AC6 scout + parallel lane contracts | BLOCKED | `ac1-ac6-live-flow-blocked.txt`; `../e2e-evidence/run-20260911T235357-v4-release/evidence-inventory.txt` | No executable command or generated lane-contract artifact is present in this repository; source procedure alone is not proof. |

## Inherited v3 rail

`evidence/v3-release/**`, `gauge-report.json`, and `gauge-report.md` remain isolated secondary-rail/user artifacts. They are not v4 evidence and are excluded from the release commit.

## Release decision

Not release-ready for a PASS claim: AC1, AC2, and AC6 are BLOCKED/UNVERIFIED. Structural and installer evidence is fresh, and the blocked receipts are now sealed in `../e2e-evidence/run-20260911T235357-v4-release/evidence-inventory.txt` (`validate OK`), but neither replaces the missing live criteria.
