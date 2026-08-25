# 03-gap-register — deduplicated, ranked (corrected)

From 32 raw findings (4 lenses; verbatim in 02-red-team-findings.md): 7 CRITICAL / 24 HIGH / 1 MEDIUM.
Dedup: SEC-1 + FM-5 merged into G-01 (same plugin-root trust defect; two lenses; merged item stays CRITICAL). **31 unique = 7 CRITICAL + 23 HIGH + 1 MEDIUM.**
Correction note: an earlier draft fabricated row ER-7B, mislabeled FM-6 as FM-9, and downgraded ER-2 — all fixed in 02 before this regeneration.

## CRITICAL (7)

| id | lens(es) / raw | where | gap → remediation |
|---|---|---|---|
| G-01 | SEC-1 + FM-5 (merged) | P3 plugin-root resolution | Root-iff-skills/+themes/ + glob + `--help`-only lets a planted/stub tree win and become trusted supplier; multiple legit installs unranked. → Resolution precedence: `--proofpunk-path` > `$PROOFPUNK_HOME` > dev checkout `plugins/proofpunk/` > versioned cache (highest version) > marketplace. Root valid iff `skills/` + `themes/` + `.claude-plugin/plugin.json` naming `proofpunk`. Resolved path + content hash recorded in PHASE0.md, shown at startup, re-verified (hash) before every evidence invocation; mismatch → stop, never guess. |
| G-02 | SEC-2 | PTY driver + run-dir trust | `script -qfc` shell-string under storms; SSH hop; no CSI/OSC filtering; no run-dir confinement. → Watcher confined to `<repo>/e2e-evidence/run-*/` (realpath, reject symlinks/outside); artifact names sanitized; captured PTY output rendered escape-filtered everywhere incl. Inspector; fuzz corpus banned from wrapper-killing signals (SIGINT/exit) and modal-Approve sequences. |
| G-03 | SC-01 | `<scope>` block | Normalization dropped the binding v1.0 ceiling. → Ceiling restored as forbidden: no session tabs (`n`/`w` disabled+tooltip), no product session replay, no remote/shared stores; touch = per-phase file lists, not blanket repo write. |
| G-04 | ER-1 | all phase Verify lines | Gates are behavioral one-liners; sealed-run lifecycle absent from PASS predicate. → Every gate = one sealed run (init-run → next-step per obligation → seal → validate); PASS row cites run-id + artifact paths; gate template baked into 05-gated.md. |
| G-05 | ER-2 | P8 Verify | On-screen widgets could PASS the perf gate. → PASS predicate = exported metrics JSON read from disk, parsed, all five budget values asserted from file; live display never cited. |
| G-06 | FM-1 | stop_conditions + every Verify | No wall-clock/connect/wait bounds → gates can hang forever. → Timeout ladder binding: per-observe ≤30s; per-phase ≤60min; P10 sub-phases ≤90min; SDK connect ≤60s. Expiry = BLOCKED verdict with partial artifacts sealed, never a hang. |
| G-07 | FM-2 | P3 bridge/sdk.py | Single-owner loop could starve Textual; crash path incomplete. → Receive loop its own asyncio task; crash = backoff 1s/2s/4s max 3 → frozen + resume-session surfaced; orphan CLI reaped via SDK teardown; queued commands survive in log with explicit replay/drop decision event. |

## HIGH (23)

| id | raw | where | gap → remediation |
|---|---|---|---|
| G-08 | SEC-3 | watcher + Screen 4 ingestion | Planted path/payload ingested and displayed. → Covered by G-02 confinement + sanitize + escape-filter; Screen 4 renders artifact metadata only, never raw untrusted bytes. |
| G-09 | SEC-4 | permission modal vs fuzz | Fuzz could Approve. → Product invariant: no automated input path resolves a permission prompt; P9 asserts modal stays pending under storm; resolution only on explicit human keystroke. |
| G-10 | SEC-5 | evidence subprocess | Glob at invoke, inherited env. → Explicit argv array; absolute pinned script path resolved once at startup; env allowlist (PATH, HOME, LANG); invocation recorded in event log. |
| G-11 | SEC-6 | secret-scan coverage | Typescripts/screenshots/SSH unscanned; leaks committed. → Scanner covers ALL sealed-run artifact types; pre-seal failure blocks seal; committed finding = release-gate FAIL. |
| G-12 | SEC-7 | budget enforcement | Cap unspecified, not hard-enforced. → Default recorded in PHASE0.md; HUD live aggregate incl. subagents; 90% suspend / 100% halt (BLOCKED); consent to raise. |
| G-13 | SEC-8 | SDK project confinement | SDK sessions not project-rooted. → Every SDK session cwd = repo root, `--project` = same root; header displays root; never widened. |
| G-14 | SC-02 | P2/P4 replay wording | "Replay rail" invites product replay (v1.1). → Renamed "event-log replay harness in tests_dev (contributor rail)"; explicitly not product surface. |
| G-15 | SC-03 | P10 sub-phases | Unnamed, uncapped. → Enumerated: (a) S1–S5 obligation runs, (b) 30-min perf run, (c) terminal matrix, (d) self-hosted; each ≤5 files; total new files ≤10; beyond = new phase + approval. |
| G-16 | SC-04 | re-freeze rule dropped | Silent rescope on negative verdict. → Restored verbatim: re-freeze, re-slice, delta approval before resuming. |
| G-17 | SC-05 | unowned deliverables | Overlays/inspector/checkpoint-keys/tests_dev unowned. → Ownership map: global modals+inspector → P5; help stub + n/w tooltip → P1; checkpoint/rewind keys → P6 (tooltip-disabled if row 12 negative); tests_dev/ → created P2, extended per phase. |
| G-18 | SC-06 | P5 Verify breadth | P5 gate spanned later-phase surface. → Split: modal + interrupt round-trip + mid-delta + tool-card = P5; subagent-spawn/tree-nesting evidence = P6 gate. |
| G-19 | SC-07 | SSH cell vs no_touch | Remote work under v1.0 label. → SSH cell = operator-provided target rendering the LOCAL product over SSH client; consent prompt before connecting; no remote deployment/stores. |
| G-20 | ER-3 | regression artifact | No proof of prior-phase re-check. → Regression re-run emits `regression-prior-phase` artifact in the CURRENT run; absence blocks PASS. |
| G-21 | ER-4 | RELEASE.md freshness | Stale P5–P9 captures could fill table. → RELEASE.md cites only P10/P11-run artifacts; P10 re-captures per obligation. |
| G-22 | ER-5 | P7 disk proof | In-app-only judging. → Two distinct sealed runs read back from disk (blocked-seal + clean); validator report rendered from clean run's validate output file. |
| G-23 | ER-6 | artifact integrity | >0 bytes too weak. → Non-empty + type-consistent (PNG magic / JSON parses / log ≥128 bytes) + fresh_evidence validate output cited. |
| G-24 | ER-7 | P0 gate verdict format | "approval" ≠ verdict row. → P0 emits the standard verdict row like every gate. |
| G-25 | ER-8 | unique runs per unit | Capture reuse across lanes/cells. → One sealed run per gate unit (P6 per lane; P10 per matrix cell); reuse = gate FAIL. |
| G-26 | FM-3 | backpressure numerics | No depth cap/overflow policy. → Queue cap 10k events; coalesce deltas to cap, then drop-oldest deltas + `BACKPRESSURE_DROP` event + HUD warning; gate asserts zero dropped CONTROL events. |
| G-27 | FM-4 | 30-min run flake | One flake re-runs everything. → ≤2 infra-flake re-runs (fresh sealed run each); budget/permission stall = BLOCKED not retried; >20% inter-run variance investigated before PASS. |
| G-28 | FM-6 | interrupt vs modal | Focus/sequencing undefined. → Modal owns focus; `i` queues behind modal resolution; keystrokes never leak layers; Verify drives one path at a time. |
| G-29 | FM-7 | watcher split-brain | Screen 4 live over dead bridge. → Bridge heartbeat; death pauses Screen 4 (`bridge-down` badge), disables seal/next-step; resume reconciles dir vs log before re-enabling. |
| G-30 | FM-8 | driver portability | Timeouts/resync/BSD-Linux missing; P6 collision. → Per-command driver timeout; SIGWINCH resync; BSD/Linux `script` flag map in validation/e2e/README; P6 lanes drive separate app instances; matrix cells serial. |

## MEDIUM (1)

| id | raw | where | gap → remediation |
|---|---|---|---|
| G-31 | SC-08 | Screen 1 dual ownership (P1/P5) | P1 ships chrome + empty-state placeholder only; P5 replaces it with the real session screen; handoff documented in P5 file list. |

Counts: 7 + 23 + 1 = 31 unique (from 32 raw; 1 two-lens merge). Audit: raw IDs SEC-1..8, SC-01..08, ER-1..8, FM-1..8 each consumed exactly once.
