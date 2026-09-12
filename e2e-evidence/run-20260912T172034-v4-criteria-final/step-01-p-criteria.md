# proofpunk v4 — P1-P15, measured and sealed

Source of criteria: .planning/plugin-improvement-criteria.md

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| P1 | Installer defects w/ reproduction | UNVERIFIED | no BLOCKER hunt run |
| P2 | Complete surface on clean HOME | UNVERIFIED | dry-run only; no temp-HOME inventory |
| P3 | references/ citations resolve | PASS | verify-citations.py rc=0, 0 broken |
| P4 | Installer idempotent | UNVERIFIED | never run twice into one HOME |
| P5 | Router links all 17 | PASS | 17/17 in skills/proofpunk/SKILL.md |
| P6 | Router routes correctly live | UNVERIFIED | verify-command-surface.py never completed |
| P7 | >=10 improvements implemented | FAIL | 5 shipped, threshold is 10 |
| P8 | Each improvement proven | PARTIAL | hook fail-open proven 3 envs; rest gate-only |
| P9 | Hooks block+allow, 14 cases | PARTIAL | only 3/10 hooks can deny; 7 documented never-denies. Criterion assumes 7x(block+allow); needs restatement before PASS |
| P10 | Doctrine enforced or gap stated | UNVERIFIED | no precedence map produced |
| P11 | Docs explain architecture | PARTIAL | architecture.md current; no skill correctness review |
| P12 | Counts/versions accurate | PASS | verify-counts.py rc=0 |
| P13 | Existing harnesses pass | PASS | 4 harnesses rc=0, macOS + Linux root + non-root |
| P14 | Evidence sealed via fresh_evidence.py | PASS | this run: init-run -> seal -> validate rc=0 |
| P15 | Success measured not asserted | FAIL | prior 31 artifacts hand-written outside any sealed run |

PASS=5 PARTIAL=3 FAIL=2 UNVERIFIED=5 of 15

P15 is FAIL because this session produced 31 artifacts by hand instead of
driving fresh_evidence.py. P14 passes only for this run, created properly.
