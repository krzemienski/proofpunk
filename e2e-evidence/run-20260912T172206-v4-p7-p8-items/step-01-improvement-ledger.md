# P7/P8 improvement ledger — v3->v4 window (17 commits, d5a50b1..a2fdeb9 exclusive)

P7 threshold: >=10 improvements, each with file + observable outcome.
P8: each individually proven by driving the real behavior it changed.

| ID | Improvement | Commit | Proof | P8 |
|---|---|---|---|---|
| I1 | ACQUIRE stage + digest contract + steering guard | `c752879` | gate-only | **PARTIAL** |
| I2 | render-counts.py owns every derived count | `46ebae6` | verify-counts rc=0 | **PASS** |
| I3 | Count claims reconciled against disk | `42ff1bf` | verify-counts rc=0 | **PASS** |
| I4 | Site generator derives counts (HTML drift class closed) | `8f69db0` | build N==N+1 determinism | **PASS** |
| I5 | Level (d) install/verify + fail-closed auth hygiene | `90bf91d` | DESIGNED ONLY, never driven | **UNVERIFIED** |
| I6 | /proofpunk:acquire + OpenCode twin (6+6 -> 7+7) | `ba97ec6` | verify-command-surface never completed | **PARTIAL** |
| I7 | implement SKILL.md 13,342 -> 10,515 B | `ba97ec6` | verify-orchestration rc=0; 3 doctrine rules verbatim | **PASS** |
| I8 | False v3.0.0 tag claim removed (README, INSTALL) | `ba97ec6` | git ls-remote: tag absent, claim was false | **PASS** |
| I9 | docs/architecture.md v3.0.0 -> v4.0.0 + regen | `ba97ec6` | 0 stale v3.0.0 in docs/*.html | **PASS** |
| I10 | Two non-portable fixtures (PATH=/bin, chmod 000) | `ad62851` | 0 fails macOS + Linux root + non-root | **PASS** |
| I11 | Case 4c false coverage claims corrected x2 | `944eaa6/da8cdf6` | measured [ -f ] short-circuit | **PASS** |
| I12 | 7 hooks exit 127 without python3 -- FAIL-OPEN FIX | `6363c5f` | 10/10 rc=0 hermetic PATH, 3 envs; deny rc=2 intact | **PASS** |
| I13 | P1-P15 measured and sealed | `a2fdeb9` | init-run/seal/validate rc=0 | **PASS** |

Items: 13. P7 threshold (>=10): MET by count.
P8 per-item: PASS=10 PARTIAL=2 UNVERIFIED=1

P7 was previously recorded FAIL on a count of 5. That count covered only
this session's commits and ignored the nine v4-window improvements that
preceded it. Corrected count is 13. P7 = PASS by threshold; P8 remains
PARTIAL because I5 was never driven and I1/I6 rest on gates alone.
