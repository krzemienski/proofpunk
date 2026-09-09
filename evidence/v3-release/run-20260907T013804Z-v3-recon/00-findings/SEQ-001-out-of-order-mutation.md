# SEQ-001 — out-of-order mutation during read-only Phases 0-4

Recorded: 2026-09-07T01:41:47Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee

## What was done

`git checkout HEAD -- plugins/proofpunk/skills/implement/SKILL.md`

| | state | sha256 | skills on disk |
|---|---|---|---|
| before | absent (working-tree deletion) | n/a | 17 |
| after  | present, byte-identical to HEAD | 5ed7370e501388b8d29003fa50bcbba58be4a1c2d893138d8c5890c7250a3e40 | 18 |

## Why it is a violation

The work order makes Phases 0-4 read-only and requires the ordering be verifiable
from commit order, not narrative. A filesystem mutation occurred before Phase 0 was
recorded. That is a sequencing failure independent of the mutation being a revert.

## Why it is NOT a Phase-5 improvement

- Byte-identical to HEAD; introduces zero new content.
- Closes no adopted proposal (none exist yet; docs/proposals.md is ABSENT).
- Reverts unattributed pre-session tree damage, not authored work.

## Measured effect (why leaving it would have poisoned Phase 3)

| gate | rc before | rc after |
|---|---|---|
| verify-counts | 1 | 0 |
| verify-orchestration | 1 | 0 |
| verify-router-links | 1 | 0 |
| gauge-report | 1 | 1 |
| verify-harness-integrity | 3 | 3 |

Three of five red gates were reporting the deletion, not repo defects.

## Disposition

Retained. Baseline of record is `gates/` (pre-restore, tree-as-found);
`gates-after-F001/` is the corrected-tree baseline Phase 3 will use.
Both are kept. No claim is made that Phases 0-4 were mutation-free.
