# proofpunk v4 — P1-P15, measured and sealed

Criteria source: .planning/plugin-improvement-criteria.md (operator-approved 2026-09-01)

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| P1 | Installer defects w/ reproduction | UNVERIFIED | no BLOCKER hunt run |
| P2 | Complete surface on clean HOME | UNVERIFIED | dry-run only; no temp-HOME inventory |
| P3 | references/ citations resolve | PASS | tools/verify-citations.py rc=0, 0 broken |
| P4 | Installer idempotent | UNVERIFIED | never run twice into one HOME |
| P5 | Router links all 17 | PASS | 17/17 in plugins/proofpunk/skills/proofpunk/SKILL.md |
| P6 | Router routes correctly live | UNVERIFIED | tools/verify-command-surface.py never completed |
| P7 | >=10 improvements implemented | FAIL | 5 shipped, threshold 10 |
| P8 | Each improvement proven | PARTIAL | hook fail-open proven 3 envs; rest gate-only |
| P9 | Hooks block+allow, 14 cases | BLOCKED | criterion assumes 7 hooks x (block+allow). Measured 10 hooks, only 3 deny-capable (capture-guard, evidence-guard, no-test-files); 7 are documented never-denies so a block case is inapplicable. Needs operator-approved restatement; NOT claimable as PASS |
| P10 | Doctrine enforced or gap stated | UNVERIFIED | no precedence map produced |
| P11 | Docs explain architecture | PARTIAL | architecture.md current; zero skills read for correctness |
| P12 | Counts/versions accurate | PASS | tools/verify-counts.py rc=0 |
| P13 | Existing harnesses pass | PASS | 4 harnesses rc=0 on macOS + Linux root + non-root |
| P14 | Evidence sealed via fresh_evidence.py | PASS | this run: init-run -> seal -> validate rc=0 |
| P15 | Success measured not asserted | FAIL | 31 prior artifacts hand-written outside any sealed run |

BLOCKED=1 FAIL=2 PARTIAL=2 PASS=5 UNVERIFIED=5 of 15

No criterion is claimed PASS by reinterpretation. P9 is BLOCKED pending
operator restatement, not PASS. P15 is FAIL because the bulk of this
session's artifacts bypassed fresh_evidence.py entirely.
