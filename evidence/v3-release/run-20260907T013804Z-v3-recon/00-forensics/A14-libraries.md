STATUS: COMPLETE

# A14 — Library/approach evaluation + A15 prior-art scout

## Hard constraint (verified against source)

Proofpunk ships with NO runtime dependencies. Build-time tooling is Bash + Python 3 stdlib, **plus PyYAML**, which `tools/build-site.py` already imports:
- `tools/build-site.py:9` — "PyYAML (`import yaml`), used by fm_parse() to read skill frontmatter."
- `tools/build-site.py:16` — `import yaml  # noqa: F401` inside `_preflight()`, guarded by an ImportError check that names the missing dep and gives `pip install pyyaml`.
- `tools/build-site.py:40` — `import yaml` inside `fm_parse()` itself.
- `tools/AGENTS.md:55` — "Python 3 stdlib (`colorsys`, `json`, `html`, `re`) plus **PyYAML** (`import yaml` in `build-site.py` `fm_parse` — external, not stdlib); optional `mmdc` (mermaid-cli) for diagram pre-rendering."

Real dependency floor for this repo: Python 3 stdlib + PyYAML (build-time doc tooling only, not shipped in the plugin tree) + Bash + optional external binaries invoked via subprocess (`pandoc`, `mmdc`). Any new pip/npm package for a runtime capability is disqualified. Format-borrowing (copying a JSON shape without importing the client library that defines it) is explicitly permitted and used below for capability 2.

## Existing local substrate (all four capabilities must be evaluated against this, not a blank slate)

- `tools/trace.py` (25.5KB) — already implements an L2 run-trace: schema-versioned (`SCHEMA_VERSION = "1.0"`), hash-chained JSONL event log (`tools/trace.py:38-40`). Fixed 12-key record shape (`tools/trace.py:54-57`): `schema_version, run_id, ts, event, stage, skill, agent_id, parent_id, decision, artifact, cost, hash`. `cost` is a nested object with exactly `COST_KEYS = ["tokens", "wall_ms", "tool_calls"]` (`tools/trace.py:58`), all three nullable. Hash chain formula (`tools/trace.py:90-105`): `hash = sha256(prev_hash + "\n" + canonical_json(record_without_hash))`, `canonical_json` sorts keys with no whitespace, genesis is 64 `"0"` chars. CLI subcommands: `emit`, `read`, `validate`, `reconcile`.
- `plugins/proofpunk/references/run-trace-schema.md` — the doctrine doc for the above, with real worked examples pulled from an actual build run (not hand-typed). Explicitly states the trace is machine-facing and does NOT replace `.planning/execution-ledger.json` (human-facing, mutable state); `reconcile` walks the ledger read-only as a comparison target and reports MATCHED/MISMATCHED/UNTRACED, never resolving disagreement silently.
- `tools/verify-counts.py` (11.1KB, self-described "Class-2 detector") — regex-based live-tree-vs-prose count verifier, stdlib-only (`tools/verify-counts.py:23-29`, only `glob, json, os, re, sys`). Has `canon()` (derives every count from the live tree; docstring: "Never a literal" — `tools/verify-counts.py:117-118`), a `NOUNS` tuple of count nouns it owns, `HISTORICAL_BASENAMES`/`HISTORICAL_PREFIXES`/`HISTORICAL_LINE` regex to skip provenance/historical prose, `CLAIM_RE`/`PLUS_RE`/`SLASH_AGENTS_RE` to extract numeric claims from markdown, `expected_for()` to compute acceptable values per noun, `check_file()` per-file diff logic, `main()` driver. Exit 0 clean / exit 1 with file:line mismatches (docstring `tools/verify-counts.py:19`).
- 8 other verify-* Class-N detectors exist as siblings, all stdlib-only, all narrow single-purpose checks over the live tree (`verify-orchestration.py`, `verify-shipped-vs-active.py`, `verify-proof-vocab.py`, `verify-mutation-artifact.py`, `verify-harness-integrity.py`, `verify-router-links.py`, `verify-citations.py`, `verify-command-surface.py`). No generic linter, schema registry, or generated-manifest+verifier pair beyond this family exists in the repo.
- `docs/architecture.md` documents a **derive-don't-restate** convention as a named, repeat-enforced repo doctrine (`docs/architecture.md:493-499`): "The mitigation this repo has converged on, and the standard this document itself follows, is: derive, don't restate." — this is direct evidence the repo already prefers extending an existing detector over inventing a parallel mechanism, cited against the count-drift regression it fixed (`docs/architecture.md:471-476`).

---

## Capability 1 — Run-telemetry format

**Candidates evaluated:** OpenTelemetry log-record JSON, Chrome Trace Event format, JSON Lines with a versioned schema, SQLite.

| Candidate | Verdict | Reason | Disqualified for dependency? |
|---|---|---|---|
| **JSON Lines w/ versioned schema** | **WINNER** | Already implemented and shipping as `tools/trace.py` + `run-trace-schema.md`. Zero new dependency: stdlib `json`, `hashlib`, `re`, `argparse`. Append-only, one line = one event, trivially diffable/greppable, tool-agnostic (no client library needed to emit or consume). Matches the repo's existing hash-chain integrity model directly. | No — pure stdlib |
| OpenTelemetry log-record JSON | Loser | The OTel *format itself* (structured log record schema) is a defensible shape to borrow, but the practical way anyone actually emits/consumes it is via an OTel SDK/exporter client library — that is a pip dependency (`opentelemetry-sdk`, `opentelemetry-exporter-*`). Hand-rolling raw OTel JSON with no SDK is possible but buys nothing `trace.py`'s existing shape doesn't already give, while adding a second incompatible envelope schema alongside the live one. | **Yes**, if implemented as the SDK typically ships it — the OTel *client library* requires pip; a hand-written raw-JSON-only imitation is not disqualified but is strictly worse than reusing trace.py |
| Chrome Trace Event format | Loser | Designed for visualization in `chrome://tracing` / Perfetto — a nanosecond-timestamped, phase-tagged (`"ph": "B"/"E"/"X"`) event stream optimized for a flame-graph UI, not for hash-chained tamper-evidence or human-readable audit review. No native viewer dependency in this repo (no Perfetto UI shipped), so adopting this format buys a visualization capability proofpunk doesn't currently use, at the cost of a schema mismatch with the existing `run-trace-schema.md` 12-key shape. | No — format itself is just JSON, but functionally mismatched to the repo's actual need (audit trail, not flame-graph) |
| SQLite | Loser | `sqlite3` is stdlib, so not disqualified on dependency grounds — but it fails the "already exists" test harder than any other candidate: adopting it means abandoning the append-only JSONL log `trace.py` already implements, hash-chains, and validates, in favor of a binary file format that is harder to `git diff`, harder to grep, and requires a schema migration story `trace.py` doesn't need (JSONL tolerates additive fields; a SQL schema needs `ALTER TABLE` or a version-forked DB file). Every other proofpunk artifact (ledger, findings, evidence) is plaintext/JSON for the same git-diffability reason. | No — stdlib, but architecturally wrong fit |

**Bias check (task specified: "bias toward JSON Lines. Verify that bias rather than assuming it."):** Bias confirmed correct — and stronger than the task assumed, because this capability is not "build JSON Lines from scratch," it is "recognize `tools/trace.py` already IS this, fully implemented, hash-chained, and documented." The actual open question this recon surfaces is whether "add run-telemetry capability" in the v3 scope means (a) extend `trace.py`'s existing 12-key shape/9 event types, or (b) build a second, competing telemetry mechanism. Recommend (a); building (b) would violate the repo's own derive-don't-restate doctrine (`docs/architecture.md:493-499`) the same way the historical skill-count drift did.

---

## Capability 2 — Evidence integrity / attestation

**Candidates evaluated:** git object hashing, `sha256sum` (CLI), Python `hashlib`, in-toto/SLSA statement shapes, Sigstore.

| Candidate | Verdict | Reason | Disqualified for dependency? |
|---|---|---|---|
| **Python `hashlib` + in-toto-SHAPED JSON statement** | **WINNER** | `hashlib.sha256` is already the repo's hashing primitive (`tools/trace.py:105`, `compute_hash()`). The in-toto **Statement** envelope (see verified shape below) is a small, stable, dependency-free JSON structure — it can be hand-emitted with `json.dumps` + `hashlib`, borrowing the field names/semantics without importing `in-toto`'s Python attestation library (`in-toto` PyPI package) or its verification tooling. | No — `hashlib` is stdlib; the in-toto *shape* is borrowed as plain JSON, not the in-toto *library* |
| git object hashing | Loser | Git's own SHA-1 (or SHA-256 in newer repos) object hashing is real integrity, but it hashes *committed* blobs, not evidence artifacts at capture time — evidence directories in this repo (`evidence/`, `e2e-evidence/`) are explicitly pre-commit working state per `evidence-contract.md`, so relying on git object IDs alone can't attest to an artifact before it's committed, and ties attestation to git's commit cadence rather than to the moment of capture. | No — git itself is a repo prerequisite, not a new dependency, but semantically wrong fit for pre-commit evidence |
| `sha256sum` (CLI) | Loser | Fine for a one-off manual check, but shelling out to an external binary from Python (`subprocess.run(["sha256sum", ...])`) is strictly worse than calling `hashlib.sha256` directly — no dependency win, adds subprocess overhead and platform variance (macOS ships `shasum -a 256`, not `sha256sum`, without coreutils) — proofpunk already runs on macOS (see workstation) where this genuinely breaks without `brew install coreutils`. | No — but breaks cross-platform (macOS default has no `sha256sum`), which is a real functional disqualifier, not just a style preference |
| in-toto / SLSA statement shapes (as a **library**, not a borrowed format) | Loser (as a library; winner as a **format**, see above) | The `in-toto-attestation` Python package and SLSA verification tooling are pip dependencies. Using them AS LIBRARIES is disqualified. Using their JSON *shape* by hand, with stdlib `json`+`hashlib`, is the winning approach above. | **Yes**, if the actual library/SDK is imported; **No** if only the JSON shape is borrowed |
| Sigstore | Loser | Sigstore (`cosign`, `rekor`, `fulcio`) provides keyless signing and a public transparency log — real cryptographic non-repudiation beyond a hash. But it requires either a pip/npm client (`sigstore-python`) or a separately-installed `cosign` binary plus network access to Sigstore's public infrastructure (Fulcio CA, Rekor log) at attestation time. Proofpunk's threat model (per `evidence-contract.md`, redact-don't-commit-secrets) does not currently require third-party non-repudiation of evidence authorship — hash-chain tamper-evidence (already shipped) is a lower-cost fit for the stated need. | **Yes** — requires an external client (pip or a separately-managed binary) and live network dependency at attestation time |

**In-toto Statement shape (fetched from primary source, not paraphrased):**

Fetched `https://raw.githubusercontent.com/in-toto/attestation/main/spec/v1/statement.md` directly. Exact schema block as published:

```jsonc
{
  "_type": "https://in-toto.io/Statement/v1",
  "subject": [
    {
      "name": "<NAME>",
      "digest": {"<ALGORITHM>": "<HEX_VALUE>"}
    },
    ...
  ],
  "predicateType": "<URI>",
  "predicate": { ... }
}
```

Field semantics as published (quoted, not paraphrased):
- `_type` *string (TypeURI), required* — "Identifier for the schema of the Statement. Always `https://in-toto.io/Statement/v1` for this version of the spec."
- `subject` *array of ResourceDescriptor objects, required* — "Set of software artifacts that the attestation applies to. Each element represents a single software artifact. Each element MUST have `digest` set."
- `predicateType` *string (TypeURI), required* — "URI identifying the type of the Predicate."
- `predicate` *object, optional* — "Additional parameters of the Predicate. Unset is treated the same as set-but-empty. MAY be omitted if `predicateType` fully describes the predicate."

Also fetched the referenced `ResourceDescriptor` shape (`https://raw.githubusercontent.com/in-toto/attestation/main/spec/v1/resource_descriptor.md`), since `subject[].digest` uses it — a `DigestSet` is a literal `{"<ALGORITHM>": "<HEX VALUE>", ...}` map, e.g. `{"sha256": "7f4714fd..."}` — this is exactly the shape `tools/trace.py`'s own `hash` field already produces (a hex sha256 digest), so the borrow is a near-zero-friction fit: proofpunk's existing `sha256(...)` hex outputs slot directly into an in-toto-shaped `digest: {"sha256": "<hex>"}` field with no format translation needed.

**Recommendation:** a hand-rolled `{"_type": "https://in-toto.io/Statement/v1", "subject": [{"name": "<artifact path>", "digest": {"sha256": "<hex from hashlib>"}}], "predicateType": "https://proofpunk.dev/evidence-attestation/v1" (proofpunk-owned URI, not a real in-toto predicate type — this is the honesty boundary of "format borrowed, no dependency added"), "predicate": {...}}` JSON sidecar per evidence artifact, emitted by stdlib `json`+`hashlib`, with zero in-toto library import. This is exactly the shape the task's bias instruction predicted; the field names above are now grounded in the primary spec text, not invented.

---

## Capability 3 — Cost/time budgeting: what's actually observable from a hook, per platform

### Claude Code (verified against primary doc: `code.claude.com/docs/en/hooks`, fetched and read in full for the relevant sections)

- **Common input fields present on (almost) every hook:** `session_id`, `prompt_id`, `transcript_path`, `cwd`, `permission_mode`, `effort` — **no token/cost field in this common set.**
- **`PostToolUse` / `PostToolUseFailure`:** carries `duration_ms` — quoted: "Optional. Tool execution time in milliseconds. Excludes time spent in permission prompts and PreToolUse hooks." → **wall-clock: YES**, at individual tool-call granularity, documented and directly readable from hook stdin JSON.
- **`Stop` / `SubagentStop`:** carries `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons` — **no token/cost field.**
- **Subagent (`Agent`/Task tool) dispatch, foreground completion:** quoted from the fetched doc — "When a foreground Agent call completes, your PostToolUse hook receives the subagent's final text and run telemetry in `tool_response`... for token and cost rollups across subagents, use the token and cost counters... filtered to `query_source` `"subagent"`, since `totalTokens` and `usage` cover the final request only." Fields present in `tool_response`: `totalTokens` (input+output+cache combined, **final API request only, not the whole run**), `totalDurationMs` (subagent wall-clock), `totalToolUseCount` (subagent tool-call count), `usage` (object: `input_tokens`, `output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`).
- **Background subagents:** `tool_response` at launch/backgrounding time carries **no** usage fields (`status: "async_launched"` only, resolves later).
- **`SessionEnd`:** field list not confirmed from the same primary fetch pass as the above (only PreToolUse/PostToolUse/PostToolUseFailure/Stop/SubagentStop/StopFailure/Agent-tool sections were fetched in full). Secondary sources (community docs, not code.claude.com itself) report `session_id`, `cwd`, `hook_event_name`, `reason`, `transcript_path` — **no total_cost_usd/duration_ms/num_turns field is claimed anywhere**, and a live upstream GitHub feature request (`anthropics/claude-code#4318`) explicitly asks for session cost data in SessionEnd, implying it does not currently exist. **[UNVERIFIED against the primary doc directly — secondary-sourced, flagged.]**

**Conclusion — Claude Code:** tool-call-level **wall-clock is directly hook-observable** (`duration_ms` on every `PostToolUse`). **Token counts are hook-observable only for subagent (`Agent` tool) dispatches**, via a documented `tool_response.usage`/`totalTokens` field — not for the main session's own per-turn token usage. Tool-call *counts* are observable indirectly by counting `PostToolUse` firings in a session (each fire = one tool call), and directly for subagents via `totalToolUseCount`.

### OpenCode (primary doc fetched: `opencode.ai/docs/plugins/`; payload-field claims are secondary-sourced)

- Official event catalogue confirmed from the primary fetch: Tool Events are **only** `tool.execute.before` and `tool.execute.after` (no per-event field-level schema table was present on this page — it documents plugin structure and event names, not payload shapes). Session Events: `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated`.
- Secondary-sourced (not confirmed against opencode.ai's own schema reference) claim for `tool.execute.after` payload fields: `tool`, `sessionID`, `callID`, `messageID`, `args`, `result` (with `result.output`). **[UNVERIFIED against primary source.]**
- Independently corroborated (multiple sources, including a linked community `TokenScope` plugin repo): OpenCode logs message-level records including model identifiers and per-turn input/output token usage locally at `~/.local/share/opencode/storage/message/` — this is **filesystem-observable, not hook-payload-observable**. Community cost-tracking tools (`ccusage`, `opencode-tokenscope`) read these on-disk files rather than reading a hook input field.
- No `duration_ms`-equivalent field was found documented for OpenCode tool events in either the primary doc or secondary sources.

**Conclusion — OpenCode:** No officially-documented hook-payload field for tokens or wall-clock was confirmed in the primary doc. Token/cost data is technically available, but only via post-hoc filesystem reads of `~/.local/share/opencode/storage/message/`, not a hook-native field — meaningfully weaker observability than Claude Code's `duration_ms`/subagent-`usage` fields. A proofpunk hook targeting OpenCode would need to shell out to read that storage directory rather than parse hook stdin.

### OMP / 9router

- **[UNVERIFIED, weak sourcing]** — no first-party OMP or 9router documentation site was located via web search; only secondary aggregator content (community blog posts, a SourceForge mirror listing, GitHub issue references, Reddit) surfaced, and it is not reliable enough to cite as a source for a hook-payload schema claim. A claim that "OMP's OpenTelemetry integration tracks `gen_ai.client.token.usage` and cost deltas per model" appeared in search results but traces back to a betterstack.com community guide and a GitHub issue link, neither of which is OMP's own documentation.
- This session is itself running on OMP (workstation `Model: 9router/cc/claude-sonnet-5`), so a more reliable route to answer this sub-question would be to inspect OMP's own documentation surface directly (accessible via `omp://` inside this harness) rather than public web search — **not done in this pass**, since this is a repo-local, read-only recon lane scoped to `proofpunk`, and OMP's own internals are outside that scope. **Flagged as an explicit open question for the orchestrator** if OMP-hook parity genuinely blocks capability-3 design; recommend routing that specific sub-question to whichever lane has `omp://` access, rather than treating this pass's web-search result as authoritative.

**Overall capability-3 conclusion:** observability is uneven across the three platforms — Claude Code gives real wall-clock (`duration_ms`) and partial token data (subagent-only, via `usage`/`totalTokens`); OpenCode gives neither natively in a hook payload, only via filesystem reads; OMP is unverified pending a primary-source check. Any cross-platform budgeting design must either (a) degrade gracefully to "best-effort where available, null elsewhere" — which is exactly what `tools/trace.py`'s existing `cost` object already does (all three `COST_KEYS` are documented nullable, `tools/trace.py:58` + `run-trace-schema.md` field table) — or (b) scope the capability to Claude Code only, where the fields genuinely exist. Recommend (a): the existing trace schema's nullable-cost design already anticipates this exact cross-platform gap.

---

## Capability 4 — Drift detection

**Candidates evaluated:** extend `tools/verify-counts.py`, add a generic linter, a schema registry, a generated-manifest + verifier pair.

| Candidate | Verdict | Reason | Disqualified for dependency? |
|---|---|---|---|
| **Extend `tools/verify-counts.py`** | **WINNER** | Already exists, already stdlib-only, already implements the exact "derive canon from live tree, flag prose that disagrees" pattern the repo's own architecture doc names as its converged mitigation for drift (`docs/architecture.md:493-499`, quoted above). Extension means adding new `NOUNS` entries / new `canon()` fields / new `expected_for()` cases for whatever new count-class needs tracking — a bounded, low-risk change to a file whose contract (`docstring`, `tools/verify-counts.py:1-22`) already documents the historical-vs-active classification rules a new check would need anyway. | No — pure stdlib extension of existing code |
| Add a generic linter (e.g. a rule-engine wrapper) | Loser | Would duplicate `verify-counts.py`'s classification logic (`HISTORICAL_BASENAMES`/`HISTORICAL_PREFIXES`/`HISTORICAL_LINE`) in a second, more abstract engine, for no capability `verify-counts.py` doesn't already have. A "generic" linter framework (even a stdlib one) adds an abstraction layer over a single-file 325-line script that the repo's own doctrine explicitly warns against (see `docs/architecture.md`'s repeated caution about typed-in-one-place numbers "describing a fact that lived somewhere else"). | No (could stay stdlib) but architecturally redundant |
| Schema registry | Loser | A schema registry implies a persistent, queryable store of "what shape should X look like" that other tools consult centrally — genuinely useful for cross-service contract validation, but proofpunk has no services; it has markdown files and a handful of stdlib scripts each already scoped to one narrow class of drift (Class 1 through Class 4, per `tools/AGENTS.md`'s own naming). A registry is infrastructure for a scale of drift-surface this repo does not have. | No dependency required in principle (could be a JSON file), but solves a problem this repo doesn't have |
| Generated-manifest + verifier pair | Loser | This is architecturally close to what `verify-counts.py` already does (`canon()` IS a generated manifest, computed fresh every run rather than cached to disk) — the only difference is persisting the manifest as a separate artifact vs. recomputing it in-process each run. Recomputing in-process (current design) is strictly safer against manifest/reality skew, since a cached manifest file is itself one more thing that can drift from the tree it describes — exactly the failure class this capability exists to prevent. | No dependency required, but reintroduces the exact staleness risk the capability is meant to eliminate |

**Bias check (task specified: "bias toward extending the existing verifier. Justify or refute."):** Bias confirmed and justified — extending `verify-counts.py` is not merely the path of least resistance, it is the only candidate that doesn't reintroduce a form of the drift problem itself (a persisted manifest or an external registry both create a second surface that can go stale relative to the tree, which is precisely what `verify-counts.py`'s "derive, never a literal" design principle exists to prevent).

---

## A15 — Prior-art scout

### 1. Parallel lane model: orchestrator-worker vs blackboard vs actor-supervision

**Chosen: orchestrator-worker.** This is not a hypothetical choice — it is the pattern this very recon task is running under: `Main` decomposed the v3 recon into 12 independent lanes (A1–A14 per this task's own framing), each lane executes a scoped subtask with no direct lane-to-lane communication, and results synthesize back to `Main`. This matches the orchestrator-worker definition precisely: centralized decomposition, stateless/isolated workers, no inter-worker communication, single point of synthesis.

**Rejected — blackboard:** one-line reason: requires a shared read/write memory all agents poll and a control unit to arbitrate contributions and resolve conflicting posts — proofpunk's lanes have no need to build on each other's partial results mid-flight (each lane's task is fully independent), so the coordination overhead blackboard architectures pay for emergent, incremental collaboration buys nothing here.

**Rejected — actor-supervision tree:** one-line reason: its main advantage over orchestrator-worker is automatic failure recovery (a supervisor restarts a crashed child actor) and deep hierarchical nesting — proofpunk's lane model is one level deep (orchestrator → 12 flat lanes, no lane spawns its own children in this task), so the supervision-tree's extra structure for multi-level fault isolation is unused complexity for a flat fan-out.

### 2. Execution ledger: write-ahead-log vs event-sourcing

**Chosen: event-sourcing (specifically, the append-only immutable-event variant already shipped as `tools/trace.py`).** The existing `run-trace-schema.md` explicitly frames the trace as "an append-only sequence of timestamped facts about what happened, in the order it happened" — this is event-sourcing's defining property (the sequence of events *is* the source of truth), not WAL's (WAL exists to durably recover a *separate* current-state store after a crash, then gets truncated at checkpoints).

**Rejected — write-ahead-log:** one-line reason: WAL is a database-internal durability primitive (log-before-write, truncated at checkpoints) that you get for free from choosing a transactional database engine, not something proofpunk would hand-implement for an evidence trail — and its records are transient (truncated), which is the opposite of the "long-term, permanent, the history is the value" property proofpunk's `run-trace-schema.md` and hash-chain integrity model both require.

*(Note: `.planning/execution-ledger.json`, the OTHER half of proofpunk's existing two-document model, is explicitly NOT event-sourced — it's described in `run-trace-schema.md` as human-facing, mutable, revisable state, which is the opposite of event-sourcing's immutability. This is intentional: proofpunk already runs a hybrid — event-sourced trace + mutable ledger, reconciled by `trace.py reconcile` — matching the well-known CQRS pattern of separating a write-side event log from a read-side current-state projection.)*

### 3. Stuck protocol: plan-execute-reflect vs ReAct vs Tree-of-Thought

**Chosen: plan-execute-reflect.** Matches proofpunk's existing `implement/SKILL.md` execution-ledger loop structure (per the earlier grep hit on `implement/SKILL.md`, which names an explicit "Stage 5 — EXECUTE the loop" / task ledger / DONE-when-artifact-proven cycle) — plan-execute-reflect's explicit Planner→Executor→Reflector separation, with bounded re-plan/step limits to prevent infinite re-planning, maps directly onto a task-ledger-driven loop that already tracks DONE/pending/verdict state per task.

**Rejected — ReAct:** one-line reason: its single interleaved thought-action-observation loop with no explicit plan or reflection phase is documented as "brittle on long horizons" and prone to context-window-driven forgetting on multi-step work — proofpunk's stuck-protocol need is specifically for LONG, multi-phase orchestration runs, which is ReAct's known weak point.

**Rejected — Tree-of-Thought:** one-line reason: its strength is parallel exploration of multiple candidate solution paths with backtracking for problems with no single obvious answer (combinatorial search, creative ideation) — proofpunk's stuck cases are typically "this specific task's verdict didn't resolve," a single-path debugging problem, not a branching-search problem, so ToT's higher token cost for parallel path exploration buys nothing here.

### 4. Lane contracts: contract testing vs schema registry

**Chosen: contract testing (consumer-driven contract pattern, applied as a lightweight convention rather than a tooling framework).** Each lane in this very recon (A1–A14) received an explicit output contract in its task brief (a named file path, a required section structure: Summary/Findings-table/Open-questions, an ID-prefix convention) — this IS contract testing's core idea: the consumer (`Main`, synthesizing 12 lane reports) defines the contract each producer (lane) must satisfy, verified at consumption time by checking the artifact matches the expected shape. No shared registry process is needed because the number of "services" (lanes) is small, short-lived (one task run), and the contract is stated once per dispatch rather than needing central discovery.

**Rejected — schema registry:** one-line reason: schema registries earn their cost when many long-lived producers/consumers need to discover and negotiate compatible schema versions over time (e.g., Kafka topics with evolving message schemas across dozens of services) — proofpunk's lane contracts are ephemeral (one recon run), small in count (12 lanes), and fully specified up front by the orchestrator in each task brief, so there is no schema-discovery or versioning problem for a registry to solve.

---

## Open questions

1. OMP's own hook-payload schema for token/cost/wall-clock observability could not be verified from a reliable primary source in this pass — web search surfaced only aggregator/community content, no first-party OMP docs URL. Tried: 2 targeted web searches ("oh my pi" OR "9router" hook cost tokens observable; OMP harness hooks PreToolUse PostToolUse). If capability-3 design genuinely depends on OMP parity, recommend routing this specific sub-question to a lane with `omp://` documentation access.
2. Claude Code `SessionEnd` hook's exact field list was not directly confirmed from the primary `code.claude.com/docs/en/hooks` fetch in this pass (only PreToolUse/PostToolUse/PostToolUseFailure/Stop/SubagentStop/StopFailure/Agent-tool sections were fetched and read in full — the doc is 3780 lines and only a subset was pulled). The SessionEnd fields cited above (`session_id`, `cwd`, `hook_event_name`, `reason`, `transcript_path`) come from secondary community sources and are marked UNVERIFIED; a follow-up fetch of the SessionEnd-specific section (`https://code.claude.com/docs/en/hooks.md`, searching for `### SessionEnd`) would close this gap if it matters to a downstream design decision.
3. OpenCode's `tool.execute.after` payload field list (`tool`, `sessionID`, `callID`, `messageID`, `args`, `result`) is secondary-sourced only — the primary `opencode.ai/docs/plugins/` page documents event *names* but not per-event payload *schemas*. A dedicated OpenCode SDK/types reference (likely a separate docs page or the `@opencode-ai/plugin` TypeScript type definitions themselves) would be the authoritative source if this field list needs to be load-bearing for capability-3 design.
