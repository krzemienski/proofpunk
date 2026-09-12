# proofpunk v4 — P1-P15 measured verdicts

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| P1 | Installer defects w/ reproduction | UNVERIFIED | no installer BLOCKER hunt run this session |
| P2 | Complete surface on clean HOME | PARTIAL | e2e-evidence/run-20260912T005052-v4-forge-prompt/step-18-linux-platform-gates.txt (dry-run only, not real temp-HOME inventory) |
| P3 | ../../references/ citations resolve | PASS | tools/verify-citations.py rc=0; 0 broken across 18 skills |
| P4 | Installer idempotent | UNVERIFIED | never run twice into same HOME this session |
| P5 | Router links all 17 | PASS | 17/17 measured in plugins/proofpunk/skills/proofpunk/SKILL.md |
| P6 | Router routes correctly live | UNVERIFIED | needs live session probes; verify-command-surface.py never completed |
| P7 | >=10 improvements ranked+implemented | FAIL | 5 shipped this session (acquire cmd, implement refactor, 2 fixture fixes, hook fail-open) |
| P8 | Each improvement individually proven | PARTIAL | hook fail-open proven 3 envs; acquire/refactor proven by gates only |
| P9 | Hooks fire correctly, block+allow | PASS | 124 assertions / 10 scripts, rc=0 macOS + Linux root + non-root |
| P10 | Doctrine rules enforced or gap stated | UNVERIFIED | no interaction/precedence map produced |
| P11 | Docs explain architecture | PARTIAL | architecture.md current, but no skill read for correctness |
| P12 | Counts/versions accurate | PASS | tools/verify-counts.py rc=0; docs v3->v4 drift fixed |
| P13 | Existing harnesses pass | PASS | test-hooks/dry-run-install/verify-orchestration rc=0 both platforms |
| P14 | Evidence sealed via fresh_evidence.py | FAIL | validate rc=2 'no .run-meta' — 31 artifacts hand-written, never init-run/seal |
| P15 | Success measured not asserted | PARTIAL | this table is the first one produced |

PASS=5 PARTIAL=4 FAIL=2 UNVERIFIED=4 of 15

P14 is the doctrine violation: this session produced 31 artifacts by hand
instead of driving fresh_evidence.py init-run/next-step/seal/validate.
