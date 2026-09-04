# L2 `tools/trace.py validate` — independent verification

Verified: 2026-09-04 (UTC) | HEAD `9963648` (working tree dirty)
Verifier: orchestrating session, re-running the tool directly rather than
accepting the building lane's `"mutation_proven": true` claim.

## Result: the validator discriminates across all five corruption classes

| Input | Expected | Measured rc |
|---|---|---:|
| valid trace (`proof-run.jsonl`, 15 real records) | 0 | **0** |
| appended malformed JSON line | 2 | **2** |
| required field `event` removed from record 1 | 2 | **2** |
| `schema_version` set to `99.0` | 2 | **2** |
| empty file | 2 | **2** |
| missing file | 2 | **2** |

The baseline arm returning **0** is what makes the other five meaningful. A
validator that returns non-zero on everything discriminates nothing.

## Method correction — recorded because it nearly produced a false PASS

My first run invoked `trace.py validate <path>` positionally and reported:

```
baseline rc=2 (expect 0)   <- and every corruption also rc=2
```

I was one step from recording "all corruptions caught." They were not caught —
the tool never ran. `validate` requires `--trace PATH`, and argparse rejects a
positional with **rc=2**, the same exit code this validator uses for a schema
violation. The two are indistinguishable by exit code alone.

The tell was the baseline: a *valid* trace also returned 2. Had I only run the
mutated arms — which is what "mutation-proving" naively looks like — every one
would have "passed" and the finding would have been fabricated.

**Rule this run now applies:** the baseline arm must return rc=0 on known-good
input before any non-zero result on mutated input may be attributed to
detection. If the baseline is also non-zero, the invocation is wrong, not the
subject.

This is the second occurrence in this session. The first was
`verify-harness-integrity.py --tools-dir` (real flag: `--root`), also rc=2,
also nearly recorded as detection. Both are logged in
`evidence/v3-release/l16-harness/INDEPENDENT-VERIFICATION.md` and here so the
pattern is visible rather than buried in two separate lanes.

## Scope — what this verification does and does not establish

**Establishes:** `validate` correctly rejects five distinct corruption classes
and accepts a real, schema-valid trace produced by actual events.

**Does not establish:** that `trace.py` is wired into anything. The building
lane states this plainly and it is worth repeating — `proof-run.jsonl` holds
15 records from that task's own execution, not a trace of the Phase 5 build.
No skill, hook, or command currently emits into a trace. Until emission is
wired into `implement`'s Stage 5 loop and the hook decision points, gauge #1
(stage-transition coverage) has **no** data source and must read UNMEASURED,
never 0% and never a projected value.

## Open

- Emission is unwired (above) — the substrate exists, the producers do not.
- `reconcile` hardcodes two ledger shapes; a ledger schema change needs a
  matching walker update. Named in both the reference doc and the source.
- `SCHEMA_VERSION` is pinned to `1.0` with no migration path. Deferred
  deliberately rather than speculatively abstracted.
