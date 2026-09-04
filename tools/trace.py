#!/usr/bin/env python3
"""trace.py -- L2 run-trace substrate: a schema-versioned JSONL event log
for orchestration runs. Stdlib only (json, hashlib, argparse, re, os, sys,
datetime) -- no new runtime dependency.

Subcommands:
    emit       append one schema-valid event to a trace file
    read       read/filter events from a trace file
    validate   verify a trace file; exit 2 on ANY schema violation
    reconcile  cross-check a trace file against .planning/execution-ledger.json

Full record shape, field semantics, event-type table, exit-code taxonomy,
and the emit/reconcile conventions are documented in
plugins/proofpunk/references/run-trace-schema.md -- read that file before
changing this one; the two must stay in lockstep.

The trace is machine-facing HISTORY: an append-only, hash-chained JSONL
event log of what actually happened during an orchestration run. It is
NOT the ledger. `.planning/execution-ledger.json` remains human-facing
STATE (what a session currently believes is true). This tool never
writes to the ledger; `reconcile` only reads it, as a read-only
comparison target.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Schema constants -- keep these in lockstep with run-trace-schema.md.
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0"
SUPPORTED_SCHEMA_VERSIONS = {"1.0"}
GENESIS_HASH = "0" * 64  # sha256 hex digest is 64 hex chars; genesis is the all-zero digest

EVENT_TYPES = {
    "stage_enter", "stage_exit",       # stage entry/exit
    "spawn", "return",                 # subagent spawn/return
    "skill_invoke",                    # skill invocation
    "hook_decision",                   # hook decision, INCLUDING silent passes
    "tool_call",                       # tool-call class
    "evidence_capture",                # evidence capture
    "verdict",                         # verdict
}

# Fixed 12-key record shape (order is the canonical on-disk order). Every
# emitted record has EXACTLY these keys -- validate flags missing OR extra.
RECORD_KEYS = [
    "schema_version", "run_id", "ts", "event", "stage", "skill",
    "agent_id", "parent_id", "decision", "artifact", "cost", "hash",
]
COST_KEYS = ["tokens", "wall_ms", "tool_calls"]

HOOK_OUTCOMES = {"allow", "block", "silent"}
VERDICT_VALUES = {"PASS", "FAIL", "BLOCKED", "UNVERIFIED"}

# Event types that MUST carry a non-null value in the named field --
# documents + enforces the "silent is still a decision" requirement and a
# handful of other structurally-required fields per event type.
REQUIRES_NONNULL = {
    "hook_decision": ["decision"],
    "verdict": ["decision"],
    "spawn": ["agent_id"],
    "return": ["agent_id"],
    "skill_invoke": ["skill"],
    "stage_enter": ["stage"],
    "stage_exit": ["stage"],
    "evidence_capture": ["artifact"],
}

TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


class TraceError(Exception):
    """Raised for conditions that must FAIL LOUDLY -- never pass quietly."""


# ---------------------------------------------------------------------------
# Hashing -- the ONE formula both emit and validate use. If these two ever
# compute the hash differently, the chain becomes unverifiable by design.
# ---------------------------------------------------------------------------

def canonical_payload(record: dict) -> str:
    """Canonical JSON of every key except `hash`, sorted, no whitespace.
    Sorted (not insertion-order) so the hash is reproducible regardless of
    which key order a producer happened to serialize with."""
    payload = {k: v for k, v in record.items() if k != "hash"}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_hash(prev_hash: str, record_without_hash: dict) -> str:
    """hash = sha256(prev_hash + "\\n" + canonical_payload(record)).
    Chaining to prev_hash makes the LOG tamper-evident as a sequence: a
    per-record self-hash alone would catch a mutated field but not a
    deleted, reordered, or truncated line. GENESIS_HASH seeds the first
    record of each run_id (see run_id-scoping note in read_records)."""
    material = prev_hash + "\n" + canonical_payload(record_without_hash)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def iso_now() -> str:
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


# ---------------------------------------------------------------------------
# emit
# ---------------------------------------------------------------------------

def _parse_decision(raw: str | None):
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def _last_record_and_hash(trace_path: str) -> tuple[dict | None, str]:
    """Returns (last_valid_record_or_None, prev_hash_to_chain_from).
    Reading tolerates a NOT-YET-EXISTING file (fresh trace: genesis) but
    does NOT tolerate an existing-but-corrupt tail -- emit must refuse to
    extend a broken chain rather than silently keep appending past known
    corruption (that would compound the very defect validate exists to
    catch)."""
    if not os.path.exists(trace_path):
        return None, GENESIS_HASH
    with open(trace_path, "r", encoding="utf-8") as f:
        lines = [ln for ln in f.read().split("\n") if ln.strip()]
    if not lines:
        return None, GENESIS_HASH
    last_line = lines[-1]
    try:
        last = json.loads(last_line)
    except json.JSONDecodeError as exc:
        raise TraceError(
            f"refusing to append: trace tail (line {len(lines)}) is not valid JSON: {exc}"
        ) from exc
    if "hash" not in last or not isinstance(last["hash"], str):
        raise TraceError(
            f"refusing to append: trace tail (line {len(lines)}) has no usable 'hash' field"
        )
    expected = compute_hash(GENESIS_HASH if len(lines) == 1 else _hash_of_line(lines[-2]),
                             {k: v for k, v in last.items() if k != "hash"})
    if expected != last["hash"]:
        raise TraceError(
            f"refusing to append: trace tail (line {len(lines)}) fails its own hash check "
            f"(expected {expected}, got {last['hash']}) -- run `validate` before emitting further"
        )
    return last, last["hash"]


def _hash_of_line(line: str) -> str:
    rec = json.loads(line)
    return rec["hash"]


def cmd_emit(args: argparse.Namespace) -> int:
    last, prev_hash = _last_record_and_hash(args.trace)
    if last is not None and last.get("run_id") != args.run_id:
        raise TraceError(
            f"refusing to append: trace {args.trace!r} already holds run_id={last.get('run_id')!r}, "
            f"this emit asked for run_id={args.run_id!r} -- one trace file is one run "
            f"(reconcile and read assume a single run_id per file)"
        )
    if args.event not in EVENT_TYPES:
        raise TraceError(f"unknown event type {args.event!r}; must be one of {sorted(EVENT_TYPES)}")

    cost = {
        "tokens": args.tokens,
        "wall_ms": args.wall_ms,
        "tool_calls": args.tool_calls,
    }
    record = {
        "schema_version": SCHEMA_VERSION,
        "run_id": args.run_id,
        "ts": args.ts or iso_now(),
        "event": args.event,
        "stage": args.stage,
        "skill": args.skill,
        "agent_id": args.agent_id,
        "parent_id": args.parent_id,
        "decision": _parse_decision(args.decision),
        "artifact": args.artifact,
        "cost": cost,
    }

    missing_required = [f for f in REQUIRES_NONNULL.get(args.event, []) if record.get(f) is None]
    if missing_required:
        raise TraceError(
            f"event={args.event!r} requires non-null field(s) {missing_required} "
            f"(see run-trace-schema.md event-type table)"
        )

    record["hash"] = compute_hash(prev_hash, record)

    line = json.dumps(record, sort_keys=False, separators=(",", ":"))
    with open(args.trace, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)
    return 0


# ---------------------------------------------------------------------------
# read
# ---------------------------------------------------------------------------

def cmd_read(args: argparse.Namespace) -> int:
    if not os.path.exists(args.trace):
        sys.stderr.write(f"MISSING FILE: {args.trace} does not exist\n")
        return 2
    with open(args.trace, "r", encoding="utf-8") as f:
        raw_lines = [ln for ln in f.read().split("\n") if ln.strip()]

    matches: list[dict] = []
    for i, raw in enumerate(raw_lines, start=1):
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            sys.stderr.write(f"read: skipping malformed JSON at line {i} (use `validate` for a strict pass)\n")
            continue
        if args.run_id and rec.get("run_id") != args.run_id:
            continue
        if args.event and rec.get("event") != args.event:
            continue
        if args.stage and rec.get("stage") != args.stage:
            continue
        if args.skill and rec.get("skill") != args.skill:
            continue
        if args.agent_id and rec.get("agent_id") != args.agent_id:
            continue
        if args.since and str(rec.get("ts", "")) < args.since:
            continue
        if args.until and str(rec.get("ts", "")) > args.until:
            continue
        matches.append(rec)
        if args.limit and len(matches) >= args.limit:
            break

    if args.format == "count":
        print(len(matches))
    else:
        for rec in matches:
            print(json.dumps(rec, sort_keys=False, separators=(",", ":")))
    return 0


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def _validate_cost(cost, line_no: int, problems: list[str]) -> None:
    if not isinstance(cost, dict):
        problems.append(f"line {line_no}: 'cost' must be an object, got {type(cost).__name__}")
        return
    if set(cost.keys()) != set(COST_KEYS):
        problems.append(
            f"line {line_no}: 'cost' keys must be exactly {COST_KEYS}, got {sorted(cost.keys())}"
        )
        return
    for k in COST_KEYS:
        v = cost[k]
        if v is None:
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
            problems.append(f"line {line_no}: cost.{k} must be null or a non-negative number, got {v!r}")


def _validate_decision_shape(event: str, decision, line_no: int, problems: list[str]) -> None:
    if event == "hook_decision":
        if isinstance(decision, str):
            if decision not in HOOK_OUTCOMES:
                problems.append(
                    f"line {line_no}: hook_decision 'decision' string {decision!r} not in {sorted(HOOK_OUTCOMES)}"
                )
        elif isinstance(decision, dict):
            outcome = decision.get("outcome")
            if outcome not in HOOK_OUTCOMES:
                problems.append(
                    f"line {line_no}: hook_decision 'decision.outcome' {outcome!r} not in {sorted(HOOK_OUTCOMES)}"
                )
        else:
            problems.append(f"line {line_no}: hook_decision 'decision' must be a string or object, got {decision!r}")
    elif event == "verdict":
        if decision not in VERDICT_VALUES:
            problems.append(f"line {line_no}: verdict 'decision' {decision!r} not in {sorted(VERDICT_VALUES)}")


def cmd_validate(args: argparse.Namespace) -> int:
    if not os.path.exists(args.trace):
        print(f"MISSING FILE: {args.trace} does not exist", file=sys.stderr)
        return 2

    with open(args.trace, "r", encoding="utf-8") as f:
        raw = f.read()

    raw_lines = raw.split("\n")
    # A trailing newline produces one empty trailing element -- drop it,
    # but keep interior blank lines as real (malformed, empty-string) rows
    # so a stray blank line mid-file is a reportable defect, not silently
    # skipped.
    if raw_lines and raw_lines[-1] == "":
        raw_lines = raw_lines[:-1]

    if not raw_lines:
        # Deliberate distinct message: a trace with zero lines would
        # otherwise fall through every per-line check with nothing to
        # report and print a false "0 problems" pass -- the exact vacuous
        # loop-never-executes trap the fresh-evidence run-scoped-artifact
        # check (references/evidence-contract.md) exists to catch. Fail
        # loudly and specifically instead of vacuously.
        print(f"EMPTY TRACE: {args.trace} contains zero lines -- an empty trace cannot back any claim", file=sys.stderr)
        return 2

    problems: list[str] = []
    prev_hash = GENESIS_HASH
    file_run_id = None
    valid_event_count = 0

    for i, raw_line in enumerate(raw_lines, start=1):
        if raw_line.strip() == "":
            problems.append(f"line {i}: blank line inside trace body (not a trailing newline)")
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            problems.append(f"line {i}: MALFORMED JSON -- {exc} -- raw: {raw_line[:200]!r}")
            continue
        if not isinstance(record, dict):
            problems.append(f"line {i}: record must be a JSON object, got {type(record).__name__}")
            continue

        keys = set(record.keys())
        missing = [k for k in RECORD_KEYS if k not in keys]
        extra = sorted(keys - set(RECORD_KEYS))
        if missing:
            problems.append(f"line {i}: MISSING FIELD(S) {missing} (record has {sorted(keys)})")
        if extra:
            problems.append(f"line {i}: UNEXPECTED FIELD(S) {extra} not in the fixed 12-key schema")
        if missing:
            # Cannot safely evaluate the remaining structural checks
            # against a record with holes in its own shape -- record the
            # defect and move on rather than raising a KeyError that
            # would look like a harness crash, not a trace defect.
            continue

        sv = record["schema_version"]
        if sv not in SUPPORTED_SCHEMA_VERSIONS:
            problems.append(
                f"line {i}: WRONG SCHEMA_VERSION -- got {sv!r}, supported {sorted(SUPPORTED_SCHEMA_VERSIONS)}"
            )

        ev = record["event"]
        if ev not in EVENT_TYPES:
            problems.append(f"line {i}: UNKNOWN EVENT TYPE {ev!r} not in {sorted(EVENT_TYPES)}")

        if not isinstance(record["run_id"], str) or not record["run_id"]:
            problems.append(f"line {i}: 'run_id' must be a non-empty string, got {record['run_id']!r}")
        else:
            if file_run_id is None:
                file_run_id = record["run_id"]
            elif record["run_id"] != file_run_id:
                problems.append(
                    f"line {i}: RUN_ID MISMATCH -- file established run_id={file_run_id!r} at an earlier "
                    f"line, this line has run_id={record['run_id']!r} (one trace file is one run)"
                )

        if not isinstance(record["ts"], str) or not TS_RE.match(record["ts"]):
            problems.append(f"line {i}: 'ts' must be ISO-8601 UTC (…T…Z), got {record['ts']!r}")

        for f in ("agent_id", "parent_id", "stage", "skill", "artifact"):
            if record[f] is not None and not isinstance(record[f], str):
                problems.append(f"line {i}: '{f}' must be null or a string, got {record[f]!r}")

        _validate_cost(record["cost"], i, problems)

        if ev in EVENT_TYPES:
            if ev in REQUIRES_NONNULL:
                for f in REQUIRES_NONNULL[ev]:
                    if record.get(f) is None:
                        problems.append(f"line {i}: event={ev!r} requires non-null '{f}'")
            # Skip the shape check when 'decision' is null and already
            # reported above -- avoids reporting the same defect twice
            # under two different messages.
            if record.get("decision") is not None:
                _validate_decision_shape(ev, record.get("decision"), i, problems)

        if not isinstance(record["hash"], str) or not HASH_RE.match(record["hash"]):
            problems.append(f"line {i}: 'hash' must be a 64-char lowercase hex sha256 digest, got {record['hash']!r}")
        else:
            expected = compute_hash(prev_hash, {k: v for k, v in record.items() if k != "hash"})
            if expected != record["hash"]:
                problems.append(
                    f"line {i}: HASH CHAIN BROKEN -- expected {expected}, got {record['hash']} "
                    f"(this line's content or an earlier line was altered after being written)"
                )
            prev_hash = record["hash"]

        valid_event_count += 1

    if problems:
        print(f"INVALID: {args.trace} -- {len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 2

    print(f"VALID: {args.trace} -- {valid_event_count} event(s), run_id={file_run_id}, hash chain intact")
    return 0


# ---------------------------------------------------------------------------
# reconcile
# ---------------------------------------------------------------------------

def _walk_ledger_verdicts(node, path: str, out: list[dict]) -> None:
    """Generic recursive walk: any dict carrying a 'verdict' key is a
    verdict claim (criteria.* shape). Also special-cases the top-level
    'gates' block, whose values are bare ints or {"rc": N} -- the ONE
    ledger shape this function hardcodes, because a bare int has no other
    way to express PASS/FAIL. See run-trace-schema.md `reconcile`
    conventions for why these two shapes and not a generic schema."""
    if isinstance(node, dict):
        if "verdict" in node and isinstance(node["verdict"], str):
            out.append({"path": path, "verdict": node["verdict"], "evidence": node.get("evidence")})
        if path == "gates" or path.endswith(".gates"):
            for k, v in node.items():
                gate_path = f"{path}.{k}" if path else k
                if isinstance(v, bool):
                    continue
                if isinstance(v, int):
                    out.append({"path": gate_path, "verdict": "PASS" if v == 0 else "FAIL", "evidence": None})
                elif isinstance(v, dict) and "rc" in v and isinstance(v["rc"], int):
                    out.append({"path": gate_path, "verdict": "PASS" if v["rc"] == 0 else "FAIL", "evidence": None})
            return
        for k, v in node.items():
            child = f"{path}.{k}" if path else k
            _walk_ledger_verdicts(v, child, out)
    elif isinstance(node, list):
        for idx, v in enumerate(node):
            _walk_ledger_verdicts(v, f"{path}[{idx}]", out)


def _walk_ledger_evidence(node, path: str, out: list[dict]) -> None:
    if isinstance(node, dict):
        for key in ("evidence", "artifact"):
            v = node.get(key)
            if isinstance(v, str) and v:
                out.append({"path": f"{path}.{key}" if path else key, "value": v})
        for k, v in node.items():
            child = f"{path}.{k}" if path else k
            _walk_ledger_evidence(v, child, out)
    elif isinstance(node, list):
        for idx, v in enumerate(node):
            _walk_ledger_evidence(v, f"{path}[{idx}]", out)


def cmd_reconcile(args: argparse.Namespace) -> int:
    if not os.path.exists(args.trace):
        print(f"MISSING FILE: {args.trace} does not exist", file=sys.stderr)
        return 2
    if not os.path.exists(args.ledger):
        print(f"MISSING FILE: {args.ledger} does not exist", file=sys.stderr)
        return 2

    with open(args.trace, "r", encoding="utf-8") as f:
        trace_lines = [ln for ln in f.read().split("\n") if ln.strip()]
    trace_records = []
    for i, ln in enumerate(trace_lines, start=1):
        try:
            trace_records.append(json.loads(ln))
        except json.JSONDecodeError:
            print(f"MALFORMED TRACE: line {i} is not valid JSON -- run `validate` first", file=sys.stderr)
            return 2

    try:
        with open(args.ledger, "r", encoding="utf-8") as f:
            ledger = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"MALFORMED LEDGER: {args.ledger} -- {exc}", file=sys.stderr)
        return 2

    verdict_events = {}  # stage -> list[decision]
    evidence_artifacts = set()
    for rec in trace_records:
        if rec.get("event") == "verdict" and rec.get("stage"):
            verdict_events.setdefault(rec["stage"], []).append(rec.get("decision"))
        if rec.get("event") == "evidence_capture" and rec.get("artifact"):
            evidence_artifacts.add(rec["artifact"])

    ledger_verdicts: list[dict] = []
    _walk_ledger_verdicts(ledger, "", ledger_verdicts)
    ledger_evidence: list[dict] = []
    _walk_ledger_evidence(ledger, "", ledger_evidence)

    matched, mismatched, untraced_v = [], [], []
    for claim in ledger_verdicts:
        stage = claim["path"]
        if stage not in verdict_events:
            untraced_v.append(claim)
            continue
        observed = verdict_events[stage]
        if claim["verdict"] in observed:
            matched.append({**claim, "observed": observed})
        else:
            mismatched.append({**claim, "observed": observed})

    ev_matched, ev_untraced = [], []
    for claim in ledger_evidence:
        if claim["value"] in evidence_artifacts:
            ev_matched.append(claim)
        else:
            ev_untraced.append(claim)

    print(f"RECONCILE: trace={args.trace} ({len(trace_records)} events) vs ledger={args.ledger}")
    print(f"  verdict claims in ledger : {len(ledger_verdicts)}")
    print(f"    MATCHED   : {len(matched)}")
    for m in matched:
        print(f"      - {m['path']}: ledger={m['verdict']!r} trace={m['observed']}")
    print(f"    MISMATCHED: {len(mismatched)}")
    for m in mismatched:
        print(f"      - {m['path']}: ledger={m['verdict']!r} trace={m['observed']}")
    print(f"    UNTRACED  : {len(untraced_v)} (ledger claims a verdict this trace never independently recorded)")
    for u in untraced_v:
        print(f"      - {u['path']}: ledger={u['verdict']!r}")
    print(f"  evidence paths cited in ledger : {len(ledger_evidence)}")
    print(f"    MATCHED (captured in this trace)  : {len(ev_matched)}")
    for m in ev_matched:
        print(f"      - {m['path']} -> {m['value']}")
    print(f"    UNTRACED (not captured in this trace): {len(ev_untraced)}")
    for u in ev_untraced:
        print(f"      - {u['path']} -> {u['value']}")

    if mismatched:
        print(f"RECONCILE MISMATCH: {len(mismatched)} verdict(s) contradict the trace", file=sys.stderr)
        return 1
    print(f"RECONCILE OK: 0 mismatches ({len(matched)} matched, {len(untraced_v)} untraced -- untraced is expected "
          f"for ledger claims outside this trace's own observed scope)")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trace.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)

    pe = sub.add_parser("emit", help="append one schema-valid event")
    pe.add_argument("--trace", required=True)
    pe.add_argument("--run-id", required=True)
    pe.add_argument("--event", required=True, choices=sorted(EVENT_TYPES))
    pe.add_argument("--stage", default=None)
    pe.add_argument("--skill", default=None)
    pe.add_argument("--agent-id", default=None)
    pe.add_argument("--parent-id", default=None)
    pe.add_argument("--decision", default=None, help="string, or a JSON literal (e.g. '{\"outcome\":\"block\"}')")
    pe.add_argument("--artifact", default=None)
    pe.add_argument("--tokens", type=int, default=None)
    pe.add_argument("--wall-ms", type=int, default=None)
    pe.add_argument("--tool-calls", type=int, default=None)
    pe.add_argument("--ts", default=None, help="override timestamp; default now (UTC, ISO-8601)")

    pr = sub.add_parser("read", help="read/filter events")
    pr.add_argument("--trace", required=True)
    pr.add_argument("--run-id", default=None)
    pr.add_argument("--event", default=None, choices=sorted(EVENT_TYPES))
    pr.add_argument("--stage", default=None)
    pr.add_argument("--skill", default=None)
    pr.add_argument("--agent-id", default=None)
    pr.add_argument("--since", default=None)
    pr.add_argument("--until", default=None)
    pr.add_argument("--limit", type=int, default=None)
    pr.add_argument("--format", choices=["jsonl", "count"], default="jsonl")

    pv = sub.add_parser("validate", help="verify a trace file; exit 2 on any schema violation")
    pv.add_argument("--trace", required=True)

    pc = sub.add_parser("reconcile", help="cross-check trace against the execution ledger")
    pc.add_argument("--trace", required=True)
    pc.add_argument("ledger", help="path to .planning/execution-ledger.json (positional, per the assignment's `reconcile <ledger>` shape)")

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv[1:])
    try:
        if args.command == "emit":
            return cmd_emit(args)
        if args.command == "read":
            return cmd_read(args)
        if args.command == "validate":
            return cmd_validate(args)
        if args.command == "reconcile":
            return cmd_reconcile(args)
    except TraceError as exc:
        print(f"TRACE ERROR: {exc}", file=sys.stderr)
        return 2
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
