# Run-Trace Schema (shared)

Canonical record shape and event-type catalogue for the L2 run-trace
substrate: a schema-versioned, hash-chained JSONL event log of what
actually happened during an orchestration run. Implemented by
`tools/trace.py`. Every worked example below is a real, unmodified
record emitted by that tool during its own build (`evidence/v3-release/l2-trace/proof-run.jsonl`,
`run_id=run-20260904T054443-l2-trace-proof`) — not hand-typed fiction.

## What this is, and what it is not

The trace is **machine-facing history**: an append-only sequence of
timestamped facts about what happened, in the order it happened,
tamper-evident via a hash chain. It answers "what occurred, and when,
and in what order" after the fact.

**`.planning/execution-ledger.json` remains human-facing state.** The
ledger answers "what does this session currently believe is true right
now" — criteria verdicts, gate results, corrections made, root cause.
It is read by humans, written by hand or by an agent narrating its own
progress, and it is mutable (a criterion's verdict can be revised as new
evidence arrives).

The trace does not replace the ledger's job and never writes to it.
`tools/trace.py reconcile` reads the ledger read-only, purely as a
comparison target: does the ledger's claimed state agree with what the
trace independently observed? Disagreement is reported, never silently
resolved in either document's favor.

| | Trace (`tools/trace.py`) | Ledger (`.planning/execution-ledger.json`) |
|---|---|---|
| Nature | append-only event log | current-state document |
| Mutability | never edited in place; only appended | edited as understanding changes |
| Granularity | one record per discrete event | one entry per criterion/gate/correction |
| Integrity | hash-chained, tamper-evident | none (plain JSON, hand-editable) |
| Consumed by | `read`, `validate`, `reconcile` | any skill/human reading current state |
| Written by | `tools/trace.py emit` | `implement`'s Stage 5/7, or by hand |

## Record shape

Every record is exactly one line of JSON (JSONL) with **exactly these
12 keys**, no more, no fewer — `validate` reports both `MISSING FIELD(S)`
and `UNEXPECTED FIELD(S)` as separate defect classes:

| Field | Type | Nullable | Meaning |
|-------|------|----------|---------|
| `schema_version` | string | no | Must be a version this `trace.py` build supports (currently `"1.0"`). A trace and its reader/validator can drift apart across `tools/` upgrades; this field is how `validate` catches that instead of silently misreading an old or newer shape. |
| `run_id` | string | no | Identifies one orchestration run. One trace **file** holds exactly one `run_id` — `validate` flags a second `run_id` appearing mid-file as a defect, and `emit` refuses to append a record whose `--run-id` disagrees with the file's established one. |
| `ts` | string | no | ISO-8601 UTC, millisecond precision, `Z` suffix (`2026-09-04T06:15:57.730Z`). `emit` stamps this automatically (`--ts` overrides for reconstructing historical events). |
| `event` | string | no | One of the 9 event types below. |
| `stage` | string | yes | The orchestration stage/phase name this event belongs to (e.g. `Phase5-L2Trace`, or a ledger-style dotted path like `gates.test-hooks` for `verdict` events — see `reconcile` conventions below). Null when the event has no stage context (rare). |
| `skill` | string | yes | The skill, hook script, or tool name most directly responsible for this event (e.g. `evidence-guard.sh`, `end-user-testing`, `bash`). Null when not applicable. |
| `agent_id` | string | yes | The subagent/session identifier this event belongs to. Required non-null for `spawn` and `return`. |
| `parent_id` | string | yes | The parent agent/session identifier (who spawned `agent_id`, or who this `return` reports back to). |
| `decision` | string \| object \| null | yes | The event's payload. Shape depends on `event` — see the per-event-type table below. |
| `artifact` | string | yes | A path (repo-relative) to a produced or consulted artifact. Required non-null for `evidence_capture`. |
| `cost` | object | no | **Always** an object with exactly the keys `tokens`, `wall_ms`, `tool_calls` — each an individual `int \| float \| null`. Never omit the object itself; individual metrics may be `null` when not tracked for that event. |
| `hash` | string | no | 64-char lowercase hex sha256 digest — see Hash chain below. Computed by `emit`, never hand-supplied. |

## Event types (all 9, each with a real worked example)

### `stage_enter` — entering an orchestration stage or phase

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.730Z",
  "event": "stage_enter",
  "stage": "Phase5-L2Trace",
  "skill": "proofpunk",
  "agent_id": null,
  "parent_id": null,
  "decision": null,
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 0, "tool_calls": 0},
  "hash": "1a70b62de10d7d65f2242b052eb44fa4a2834268397663d8ee2cba0aafdd3765"
}
```

Required non-null: `stage`.

### `stage_exit` — leaving an orchestration stage or phase

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:58.092Z",
  "event": "stage_exit",
  "stage": "Phase5-L2Trace",
  "skill": "proofpunk",
  "agent_id": null,
  "parent_id": null,
  "decision": null,
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 0, "tool_calls": 0},
  "hash": "010e534289a3645a08e4d95971e9729a3b07f10e1338afbdbff6466ef24b824f"
}
```

Required non-null: `stage`.

### `spawn` — a subagent is dispatched

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.760Z",
  "event": "spawn",
  "stage": "Phase5-L2Trace",
  "skill": "task",
  "agent_id": "TraceSubstrate",
  "parent_id": "Main",
  "decision": null,
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 0, "tool_calls": 1},
  "hash": "a87cc40192cad53baa7084d82345c26edbb79c8b75a7ab5c184ebe0943a6d3d7"
}
```

Required non-null: `agent_id` (the id being spawned). `parent_id` is who
spawned it — record it whenever known, though the schema does not force
it, since a top-level session has no parent to name.

### `return` — a subagent reports back to its caller

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:58.064Z",
  "event": "return",
  "stage": "Phase5-L2Trace",
  "skill": "task",
  "agent_id": "TraceSubstrate",
  "parent_id": "Main",
  "decision": null,
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 0, "tool_calls": 0},
  "hash": "0948d290cde2e938bc7b63deac40a361ccd2540b411bd1fac43367a1f1ebf955"
}
```

Required non-null: `agent_id`.

### `skill_invoke` — a skill's doctrine is loaded/invoked

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.789Z",
  "event": "skill_invoke",
  "stage": "Phase5-L2Trace",
  "skill": "end-user-testing",
  "agent_id": "TraceSubstrate",
  "parent_id": "Main",
  "decision": null,
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 0, "tool_calls": 0},
  "hash": "be6edaec42274b0c3b35baef19deb89bc8c8f1a1f3d2f6d91fa51cb219366050"
}
```

Required non-null: `skill`.

### `hook_decision` — a hook's outcome, **including silent passes**

A hook's silence is itself a decision — a hook can only enforce anything
if its non-firing is as recordable as its firing. `decision` for this
event type is either the bare string `"allow" | "block" | "silent"`, or
an object with an `"outcome"` key holding one of those three values plus
whatever extra context the emitter wants to carry (`rc`, `reason`, …).
`validate` accepts both shapes but requires the outcome to be one of the
three values in either form.

**Silent pass** (evidence-guard.sh allowed a clean write — this is a
*decision*, not an absence of one):

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.844Z",
  "event": "hook_decision",
  "stage": "Phase5-L2Trace",
  "skill": "evidence-guard.sh",
  "agent_id": "TraceSubstrate",
  "parent_id": null,
  "decision": {"outcome": "silent", "rc": 0, "reason": "clean content into evidence dir"},
  "artifact": "evidence/v3-release/l2-trace/proof-run.jsonl",
  "cost": {"tokens": 0, "wall_ms": 42, "tool_calls": 1},
  "hash": "98adfefdbeebb1121f59402b1865b32a0426b218dca4beca05cc41995183b9da"
}
```

**Block** (evidence-guard.sh denied a `ghp_`-shaped secret targeting an
evidence directory, `rc=2`):

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.871Z",
  "event": "hook_decision",
  "stage": "Phase5-L2Trace",
  "skill": "evidence-guard.sh",
  "agent_id": "TraceSubstrate",
  "parent_id": null,
  "decision": {"outcome": "block", "rc": 2, "reason": "probable secret material (ghp_ pattern) targeting an evidence directory"},
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 38, "tool_calls": 1},
  "hash": "21411d1a7c3b1ebb365e120d194620794d8a6fd9606bed9bcaeb1b7bafa9fb48"
}
```

Required non-null: `decision`.

### `tool_call` — a tool-call class this session executed

`decision` here is a free-form object describing the call class and
enough of the invocation to be useful without duplicating full tool
transcripts (that belongs in the session transcript, not the trace).

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.817Z",
  "event": "tool_call",
  "stage": "Phase5-L2Trace",
  "skill": "bash",
  "agent_id": "TraceSubstrate",
  "parent_id": null,
  "decision": {"class": "read", "cmd": "git log --oneline -15"},
  "artifact": null,
  "cost": {"tokens": 0, "wall_ms": 120, "tool_calls": 1},
  "hash": "309aba052fcd59a9b043a174c92d115f5b3e00bdd0909a07d2d9b86867592521"
}
```

### `evidence_capture` — an artifact was produced or consulted

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:58.009Z",
  "event": "evidence_capture",
  "stage": "Phase5-L2Trace",
  "skill": "trace.py",
  "agent_id": "TraceSubstrate",
  "parent_id": null,
  "decision": null,
  "artifact": "evidence/v3-release/l2-trace/proof-run.jsonl",
  "cost": {"tokens": 0, "wall_ms": 5, "tool_calls": 1},
  "hash": "e903fabc56b85481eeb0e6974b050fb4dc9a93ad625eb4fd7077f89706629ae7"
}
```

Required non-null: `artifact`.

### `verdict` — a criterion, gate, or checkpoint verdict

`decision` for this event type is a bare string, one of `PASS`, `FAIL`,
`BLOCKED`, `UNVERIFIED` — the same four-state vocabulary the rest of
Proofpunk uses (`severity-model.md`). `stage` conventionally
carries the dotted path matching how the ledger names the same claim
(`gates.<name>` for release gates, `criteria.<ID>` for numbered
criteria) — `reconcile` depends on this convention to match trace
verdicts against ledger claims; see below.

```json
{
  "schema_version": "1.0",
  "run_id": "run-20260904T054443-l2-trace-proof",
  "ts": "2026-09-04T06:15:57.899Z",
  "event": "verdict",
  "stage": "gates.test-hooks",
  "skill": "test-hooks.sh",
  "agent_id": "TraceSubstrate",
  "parent_id": null,
  "decision": "PASS",
  "artifact": "evidence/v3-release/00-baseline/gates-20260904T051258/test-hooks.sh.log",
  "cost": {"tokens": 0, "wall_ms": 0, "tool_calls": 0},
  "hash": "e1e2054754a64a746b4583a6724ac296dd8f9f5701d79e90f675a48bdd923fd7"
}
```

Required non-null: `decision`.

## Hash chain (tamper-evidence)

`hash = sha256(prev_hash + "\n" + canonical_json(record_without_hash))`,
where `canonical_json` sorts keys and uses no whitespace. `prev_hash`
for a run's first record is the genesis value `"0"` × 64. Every
subsequent record chains from the previous record's own `hash`.

This is why corrupting *any* line cascades: `validate` reports the
corrupted line's own defect **and** a `HASH CHAIN BROKEN` finding on
every line after it, because each downstream hash was computed assuming
the previous line's content was exactly what it now is not. This was
observed directly during mutation-proof testing — see
`evidence/v3-release/l2-trace/VERDICT.md`, arms 2 and 3.

`emit` also refuses to append to a trace whose current tail already
fails its own hash check (`rc=2`, "refusing to append") — extending a
known-corrupt chain would compound the exact defect `validate` exists
to catch, rather than surface it.

## `reconcile` conventions

`tools/trace.py reconcile --trace <file> <ledger>` walks the ledger JSON
recursively and extracts two claim classes:

1. **Verdict claims** — any object carrying a `"verdict"` key (the
   `criteria.*` shape), plus the special-cased `gates` block (whose
   values are bare `0`/`1` ints or `{"rc": N}` objects — the *one*
   ledger shape this function hardcodes, because a bare int has no
   other way to express PASS/FAIL). Each claim's dotted path (e.g.
   `gates.test-hooks`, `criteria.C1_router_as_head_keep_18`) is looked
   up against every `verdict` event in the trace whose `stage` field
   matches that same path.
2. **Evidence citations** — any `"evidence"` or `"artifact"` string
   value anywhere in the ledger, checked against every `artifact` value
   this trace recorded via `evidence_capture` or `verdict` events.

Each claim class resolves to exactly one of three buckets:

- **MATCHED** — the trace independently recorded the same verdict (or
  captured the same evidence path) the ledger claims.
- **MISMATCHED** — the trace recorded a *different* verdict for the same
  stage the ledger claims a verdict for. This is the interesting,
  attention-worthy case: `reconcile` exits 1 (not 2 — a policy
  disagreement is not a schema violation).
- **UNTRACED** — the ledger makes a claim this trace never independently
  observed at all. This is **expected and honest**, not a defect: a
  trace only records what actually happened during the run it covers,
  and a ledger legitimately carries claims from other sessions or
  criteria this run never touched. `reconcile` still exits 0 when
  every checked claim is either MATCHED or UNTRACED — only a genuine
  MISMATCH is a failure.

`reconcile` exits 2 if either input file is missing or malformed
(mirrors `validate`'s exit-code contract), 1 on any MISMATCH, 0
otherwise.

## Exit codes (both `validate` and `reconcile`)

| rc | Meaning |
|----|---------|
| 0 | Clean — file valid (or reconcile found 0 mismatches) |
| 1 | `reconcile` only: ≥1 verdict MISMATCH between trace and ledger |
| 2 | Missing file, empty file, malformed JSON on any line, unknown event type, missing required field, wrong `schema_version`, hash-chain break, or (ledger-side) malformed ledger JSON |

`validate` never exits with anything other than 0 or 2 — there is no
"warn but pass" state for a schema violation; see
`evidence/v3-release/l2-trace/VERDICT.md` for the three named
corruption classes proven to trigger rc=2, each restored to a
byte-identical clean state afterward.
