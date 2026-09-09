# v3 Gauge Deferrals — Operator Sign-off Tokens

Status: **approved by the operator, 2026-09-09** ("Sign-off tokens for all 8",
recorded verbatim in this run's execution ledger). Same token shape as Lane B's
`APPROVE BARRIER DELTA` / `REJECT BARRIER DELTA` / `STOP`.

Context: `.planning/v3-execution-ledger.json:59` records "9 of 17 specified
gauges implemented". The 9 implemented gauges are rows #1–#9 of
`docs/v3-gauges.md`. This document records the disposition of the remaining 8:
each is **deferred to v4 with its measured blocker stated**, per the operator's
decision. Deferral is a recorded decision, not a silent gap — v4's board owns
this list from day one.

## Named ungauged lanes (5)

| # | Lane | Measured blocker | Token |
|---|------|------------------|-------|
| 1 | L5 lint lane | `shellcheck` is absent on this host (finding F-T1, `docs/discovery-register.md`); the lane cannot run as written and no sealed artifact exists to cite | DEFER-TO-V4 (operator, 2026-09-09) |
| 2 | L6 `verify-runtime.py` | proves only the *declared* graph (`verify-orchestration.py`), never the graph that actually ran at runtime (`evidence/v3-release/00-discovery/d3-gate-inventory.md`); a gauge would require runtime-graph evidence that does not exist | DEFER-TO-V4 (operator, 2026-09-09) |
| 3 | L9 memory bus | D1/D2 remain agent interpretations, not evidence-resolved (`docs/discovery-register.md`); no measurable predicate exists | DEFER-TO-V4 (operator, 2026-09-09) |
| 4 | L18 forge-prompt fallback | same unresolved-interpretation blocker as L9 (`docs/discovery-register.md`) | DEFER-TO-V4 (operator, 2026-09-09) |
| 5 | Lane B (proofpunk-agent) | operator token `APPROVE BARRIER DELTA` was given 2026-09-01 (history.db row 2253), but Lane B is a separate sibling repo (`/Users/nick/proofpunk-agent`) with its own criteria (C0–C17); its gauge does not belong in this repo's board | DEFER-TO-V4 (operator, 2026-09-09) |

## Unrecoverable specifications (3)

The "17 specified gauges" count originates in the v3.0.0 work order (operator
dictation, session transcripts). `docs/v3-gauges.md:66-80` ("Rows explicitly
not yet gauged") names only the 5 lanes above; the remaining 3 of the 17 are
**not individually recoverable from any sealed source in this repo** — no file
enumerates them. Per the board's own rule, UNMEASURED beats a fabricated
number: rather than invent 3 gauge definitions to fill the count, the operator
defers the residual specification to v4, where the gauge set will be
re-derived from v4's architecture (v4-spec §7.1 decision: the board continues
as a regression rail).

| # | Lane | Blocker | Token |
|---|------|---------|-------|
| 6–8 | work-order gauge specs #10–#12 of the unimplemented set | not recoverable as named gauges from any sealed source; re-derive under v4 | DEFER-TO-V4 (operator, 2026-09-09) |

## Consequence for the release gate

`tools/gauge-report.py` exits 0 when every *wired, gateable* gauge is PASS
(UNMET/UNVERIFIED block; UNMEASURED is excluded by design). The 8 deferrals
above are recorded decisions outside the wired set and do not block the
v3.0.0 tag. v4 work item: revisit this file first — implement, re-specify,
or formally retire each row.
