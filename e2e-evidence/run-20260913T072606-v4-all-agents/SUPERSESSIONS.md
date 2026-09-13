# Superseded claims in this run

A sealed step is never edited. When a later measurement refutes an earlier
claim, the earlier step stays exactly as sealed and is listed here.

| Step | Claim | Superseded by | What actually holds |
|---|---|---|---|
| `step-19-count-guard-hardening.md` | "I8 moves ... to individually proven" | `step-20-i8-claim-retracted.md` | FALSE. `HISTORICAL_PREFIXES` excludes `plugins/proofpunk/skills/`, so every SKILL.md is skipped by verify-counts. Re-running the mutation gives caught=False. |

step-19 is superseded only on that one conclusion. Its other content stands
and was independently re-verified: the CLAIM_RE widening is real, and the
four stale counts it exposed in `plugins/proofpunk/docs/architecture.md`
are in a file that IS scanned, so those fixes are genuinely guarded.

P8 therefore reads: individually proven I1, I5 (2 of 15). Unguarded: I8, I9.
