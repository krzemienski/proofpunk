**Deliverable:** one combined document. **Part I** is the complete product specification (screens, wireframes, behaviors, rationale, SDK grounding). **Part II** is the executable build prompt with validation checkpoints, parallel lanes, and orchestration. Feed Part II (with Part I attached as its authority) to the build agent.

**Repository:** `krzemienski/proofpunk-agent` (new, standalone)
**Consumes (unmodified, read-only):** `krzemienski/proofpunk` plugin v2.0.1
**Wraps:** `claude-agent-sdk` (Python; version pinned at Phase 0 verification -- target the version exposing `include_partial_messages`, streaming control, and subagent forwarding; every symbol below marked ✅ verified / ⚠ pending Phase 0 source verification)
**UI framework:** Textual (pinned stable)
**Python:** 3.10+
**License:** MIT

---

# PART I -- FINAL PRODUCT SPECIFICATION v1.0

## 1. Product Purpose

### 1.1 What it is
Proofpunk Agent is a terminal-native mission-control interface for Claude Agent SDK sessions. It runs one or more Claude agent sessions -- with the Proofpunk plugin loaded -- and renders everything the SDK exposes, live: the orchestrator/subagent tree, per-agent current activity, streaming tokens, tool calls and results, hook events, permission prompts, cost and context consumption, MCP server health, checkpoints, and errors.

### 1.2 Why it exists
Three gaps motivate the product:

1. **Opacity gap** -- SDK-driven agent runs are black boxes: nested subagents, tool calls, and hook firings leave no unified real-time trace. Operators cannot answer what is it doing right now and why.
2. **Evidence gap** -- Proofpunk's doctrine demands fresh, sealed, three-facet evidence (screen/disk/logs), but producing it today is manual shell work. The TUI embeds the evidence lifecycle into the product itself.
3. **Control gap** -- Interrupts, permission-mode changes, checkpoint/rewind, and budget monitoring require bespoke scripts. The TUI makes them first-class keystrokes.

### 1.3 Non-goals (v1.0)

* Not a chat client replacement for Claude Code's own TUI.
* Not a multi-user or remote collaboration tool.
* Not a prompt IDE (Proofpunk's `prompt-forge` covers prompt authoring).
* No modification of the Proofpunk plugin -- ever. Consumed read-only.
* No hidden chain-of-thought rendering -- only what the SDK stream actually exposes.

## 2. Governing Doctrine (binding on all implementation)

1. **Done means proven by end-user testing.** Unexecuted work is `UNVERIFIED`, never `PASS`.
2. **No mocks, stubs, test doubles, fake endpoints, or test-mode bypasses in the product.** Developer inner-loop tests (Textual `Pilot`, snapshot tests) may exist as contributor tooling under `tests_dev/` but are never cited as completion evidence and are never imported by product code.
3. **Completion evidence** = fresh `e2e-evidence/run-*` directory produced via Proofpunk's actual `scripts/fresh_evidence.py` subprocess (init-run → next-step artifacts → seal → validate), containing screen captures, disk-state assertions, and logs, secret-scanned before sealing.
4. **Real PTY only for E2E claims** -- `script -qfc` sub-PTY driving; observe-before-act; never pipe a TTY-guarded app; never burst-input; screenshots for visual claims.
5. **The harness lives in the repository** under `validation/` and is driven against the real installed product.
6. **Verdicts are explicit:** `PASS` / `FAIL` / `BLOCKED` / `UNVERIFIED` with full-path citations.

## 3. Validation Research Synthesis (informs §6, §9)

### 3.1 The seven-category TUI testing framework (adopted as validation architecture)

|Category|Question answered|Key tools/patterns|
|---|---|---|
|1. Functional/unit|Does this widget render/behave correctly in isolation?|Textual `run_test()` + `Pilot`; Ratatouille; tui-testing (Rust)|
|2. E2E/integration|Does the full app work from a real terminal?|`script -qfc` sub-PTY driving; tmux control mode; pyte terminal emulation; expect-style pattern matching|
|3. Snapshot/regression|Did the visual output change unexpectedly?|pytest-textual-snapshot (SVG capture); tui-snapshot; golden-file diff with review workflow|
|4. Fuzz/property|Does it break under random input?|Input storms; hypothesis; arbitrary keystroke injection with invariant checks|
|5. Accessibility|Is it usable via keyboard/screen-reader semantics?|Keyboard-only navigation audits; focus-order verification; contrast checks adapted to terminal palettes|
|6. Performance|Is it fast and lean under load?|Frame budget ≤16ms at 60fps; streaming-token throughput benchmarks; memory profiling over long sessions; p50/p95/p99 event→paint latency|
|7. Integration/ecosystem|Does it work across terminals and environments?|Terminal matrix (iTerm2, Alacritty, kitty, GNOME Terminal, Windows Terminal); TERM/color-capability matrix; SSH vs local|

### 3.2 Findings that shape this spec

* **Proofpunk's own `tui-testing` skill is the canonical doctrine layer**; this framework extends it. Proofpunk mandates real sub-PTY (`script -qfc`), observe-before-act, screenshots over text hashes, three proof facets. The seven categories map cleanly onto that doctrine.
* **Textual's first-party testing stack** (`run_test`, `Pilot`, `pytest-textual-snapshot`) covers categories 1 and 3 but runs headless -- under Proofpunk doctrine it is developer-inner-loop tooling, NOT completion evidence. Completion evidence requires category 2 (real PTY) + category 6 (real load).
* **Performance benchmarking for streaming TUIs** must measure: tokens/sec render throughput, event→paint latency p95 under concurrent subagent bursts, memory growth over a 30-minute session, and startup-to-first-paint time. These become §6 Screen 5's binding Performance Budget.
* **Fuzz input** is load-bearing for a chat-driven TUI: paste bombs, rapid key repeats during streaming, resize storms during active tool calls.
* **The terminal matrix** informs compatibility requirements: Textual handles capability detection, but evidence must show the neon-tokyo theme degrading gracefully on 256-color and 16-color terminals.

## 4. The Four-Plane Agent Model (normative)

The word agent appears in four distinct planes; every screen and subsystem must respect the separation:

|Plane|Definition|Source of truth|Rendered as|
|---|---|---|---|
|P1 -- Runtime agent|An orchestrator or subagent instance inside the SDK session|SDK stream: `SystemMessage` init, tool-use attribution (`parent_tool_use_id` ⚠, hook payloads ⚠), `AgentDefinition` configs|Agent Tree nodes|
|P2 -- Plugin agent|Proofpunk's declarative agents (`implement`, `scout`, `end-user-validate`)|`plugins/proofpunk/agents/*.md` (read at startup, never mutated)|Badges on P1 nodes when SDK reports matching agent type|
|P3 -- TUI node|The tree widget's visual state object|Internal state store fed by the event reducer|The tree itself|
|P4 -- Validation actor|A real end-user-testing execution driving this TUI|Proofpunk `end-user-testing` skill + `validation/` harness|External; invisible to the product except via Evidence panel output|

**Attribution rule (binding):** P3 state is built from SDK primitives in this strict preference order -- (1) hook-provided `agent_id`/`agent_type` ⚠, (2) `parent_agent_id` on session/message records ⚠, (3) `parent_tool_use_id` linkage ✅ (confirmed pattern in Anthropic research-agent demo), (4) orchestrator fallback with node labeled `(unattributed)`. Timing-based and string-matching attribution is prohibited except as the labeled-degraded fallback in (4).

## 5. Visual Identity System

### 5.1 Base theme: `neon-tokyo` (default)

Canonical palette (from Proofpunk `themes/palettes.json`, consumed read-only):

|Token|Hex|Usage|
|---|---|---|
|accent|`#FF2D95`|active agent, primary focus ring, HUD labels|
|accent2|`#00E5FF`|streaming tokens, links, secondary highlights|
|info|`#00BFFF`|informational events, hook notices|
|success|`#39FF88`|passed validation, completed agents, sealed evidence|
|error|`#FF3B5C`|errors, failed tools, blocked verdicts|
|warning|`#FFD600`|budget warnings, permission prompts, unattributed nodes|
|text|`#EDEDF2`|primary content|
|muted|`#8A8FA3`|timestamps, secondary metadata|
|dim|`#4A4660`|borders, inactive agents, scrollbars|
|panel|`#0B0B14`|background|
|panel2|`#12121E`|raised panels, cards|

### 5.2 Theme system

* All 20 Proofpunk palettes are supported, loaded from the local Proofpunk checkout's `themes/palettes.json` at startup; failure to locate falls back to embedded `neon-tokyo` with a warning in the Status HUD.
* `t` cycles themes live without restart; theme changes apply to every mounted widget within one render frame.
* Flat black mandate: no gradient backgrounds; depth conveyed solely through `panel`/`panel2` layering and border color intensity.
* Terminal degradation: on 256-color terminals, hex colors quantize to nearest xterm-256; on 16-color, map to canonical ANSI roles (accent→magenta, accent2→cyan, success→green, error→red, warning→yellow). Evidence must include one capture per tier.

### 5.3 Typography and glyph language

* Tree glyphs: `▸` collapsed, `▾` expanded, `●` running, `◐` waiting/permission-pending, `○` idle, `✔` complete, `✖` errored.
* Spinner: braille pattern for streaming activity; static `◐` when paused.
* All status communicated by glyph + color + text label (accessibility: never color alone).

## 6. Application Shell and Navigation

### 6.1 Layout anatomy (all screens share this chrome)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ ◆ PROOFPUNK AGENT  v1.0.0   session: 7f3a…c2   model: opus-4.8   ⏱ 04:12│  ← Header bar (panel2)
├──────────────┬─────────────────────────────────────────────┬─────────────┤
│              │                                             │             │
│   AGENT      │              MAIN VIEW                      │  INSPECTOR  │
│   TREE       │          (screen content area)              │  (context)  │
│   (left)     │                                             │  (right)    │
│              │                                             │             │
├──────────────┴─────────────────────────────────────────────┴─────────────┤
│ HUD: $0.4231 │ ctx 41% │ tok 2.1k/s │ tools 17 │ hooks 4 │ MCP 3/3 │ ⏸  │  ← Status HUD (panel2)
└──────────────────────────────────────────────────────────────────────────┘
```

* **Header bar:** product name/version, session id (truncated), model, elapsed wall time, current permission mode badge.
* **Agent Tree (left, 28 cols, collapsible to 0):** the P3 hierarchy.
* **Main view (center, fluid):** active screen content; screens switch without remount cost (Textual `ContentSwitcher`).
* **Inspector (right, 36 cols, collapsible):** contextual detail for whatever is selected/focused -- raw JSON payloads, tool I/O, hook payloads, evidence manifest entries.
* **Status HUD (bottom, 1-2 rows):** cost, context %, token throughput, tool count, hook count, MCP health, checkpoint indicator, scroll-pause state.

### 6.2 Global keybindings (work on every screen)

|Key|Action|Why|
|---|---|---|
|`Tab` / `Shift+Tab`|cycle focus: tree → main → inspector|keyboard-first doctrine|
|`1-5`|jump to screen (Session, Tools, Hooks, Evidence, Performance)|single-keystroke navigation|
|`[` / `]`|collapse/expand side panels|maximize content on narrow terminals|
|`Space`|pause/resume auto-scroll of streaming views|reading long tool output|
|`i`|interrupt current SDK turn (async, non-blocking)|control gap remedy|
|`m`|cycle permission mode (prompt→acceptEdits→bypassPermissions) ⚠ surfaced as modal confirm for bypass|safety on irreversible mode|
|`c`|create checkpoint ⚠|rewind safety net|
|`r`|rewind to selected checkpoint (confirmation modal; labeled destructive)|recovery|
|`t`|cycle theme|operator preference|
|`e`|seal current evidence run|doctrine integration|
|`?`|help overlay (all bindings + current screen's bindings)|discoverability|
|`q`|quit (confirm if session active)|prevent accidental loss|
|`n` / `w`|(v1.1, disabled with tooltip in v1.0) new/close session tab|roadmap honesty|

### 6.3 Terminal requirements

* Minimum 100×28 cells; below minimum, a blocking resize notice renders (never a broken layout).
* Truecolor preferred; graceful 256/16-color degradation per §5.2.
* Verified matrix (evidence required): iTerm2, Alacritty, kitty, GNOME Terminal, Windows Terminal; local and SSH.

## 7. Screen Specifications

> Each screen: purpose (why), wireframe, functional spec (what, numbered), data sources (SDK symbols with verification status), validation obligations.

---

### Screen 1 -- SESSION VIEW (`1`) -- default

**Why:** This is the home screen -- the operator's primary answer to what is happening right now. It fuses the live transcript with per-agent attribution so nested orchestration is legible in real time.

```
┌─ AGENT TREE ────────┬─ SESSION STREAM ────────────────────────┬─ INSPECTOR ─────────┐
│ ▾ ● orchestrator    │ 12:01:04 ▸ orchestrator                 │ Selected:           │
│   ▾ ● implement-1   │   I'll start by scouting the codebase…  │ ToolUseBlock #42    │
│   │ ◐ scout-2       │   ▍streaming…                           │ ─────────────────── │
│   │ ○ validate-3    │                                         │ name: Read          │
│   ✔ scout-1 (done)  │ 12:01:06 ▸ implement-1 → tool: Read     │ input:              │
│                     │   src/auth/session.py (2,341 lines)     │  {file_path: …}     │
│ Active: 3           │   ✔ result (1.2s, 214KB)                │                     │
│ Depth: 2            │                                         │ result: 200 OK      │
│                     │ 12:01:09 ▸ scout-2                      │ duration: 1.214s    │
│                     │   Found 3 auth flows. Report:           │ tokens: 8,412       │
│                     │   ▍                                     │                     │
│                     │ ── paused (Space to resume) ──          │ [copy] [follow]     │
├─ COMPOSER ──────────┴─────────────────────────────────────────┴─────────────────────┤
│ > type a message to the orchestrator… (Enter send, Shift+Enter newline)             │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Functional spec:**

1. **Agent Tree** renders P3 hierarchy: root orchestrator always node 0; children attach by attribution rule (§4); each node shows glyph-state, name, and current tool (if any) in muted text.
2. **Node states:** `running` (● accent, animated), `permission-pending` (◐ warning), `idle` (○ dim), `complete` (✔ success, collapses by default after 5s), `errored` (✖ error, stays expanded).
3. **Active count and depth** computed from tree state; displayed under tree; depth warning badge appears if nesting exceeds 2 (⚠ pending SDK nesting-depth verification).
4. **Session Stream** is a chronologically ordered, agent-attributed transcript: text blocks (streaming, `include_partial_messages=True` ⚠ → `StreamEvent` ✅), tool calls as inline cards (collapsed one-liner: name, key arg, duration, status), expandable to full I/O.
5. **Streaming rendering:** token deltas append to the open block; throughput meter in HUD updates ≥2Hz; auto-scroll follows unless paused (`Space`) -- paused state shows a visible banner and a `jump to live` affordance.
6. **Composer** sends user messages to the orchestrator via `ClaudeSDKClient.query()` ✅; disabled with reason-label while a turn is mid-flight if SDK forbids concurrent query (⚠ verify concurrency semantics); supports multiline.
7. **Interrupt:** `i` issues `client.interrupt()` ✅; UI shows `interrupting…` then honors terminal reason (`ResultMessage.terminal_reason` ⚠) to distinguish completed vs interrupted.
8. **Inspector (context = Session):** shows full JSON of selected message/block with syntax highlighting; `[copy]` copies to clipboard; `[follow]` pins inspector to latest event of the selected agent.
9. **Permission prompts:** when `can_use_tool` ⚠ fires, a modal overlays center screen with tool name, input summary, risk badge, and Allow/Deny/Always keys (`a`/`d`/`A`); HUD shows ◐ while pending; unattended timeout never auto-allows.
10. **Empty state:** before first query, stream area shows session metadata (model, cwd, plugin status, setting sources) and a hint bar -- never a blank void.

**Data sources:** `ClaudeSDKClient` ✅, `receive_response()`/`receive_messages()` ✅, `StreamEvent` ✅, `ToolUseBlock` ✅, `ToolResultBlock` ✅, `SystemMessage` (init: plugins, agents, setting_sources) ✅, `ResultMessage` ✅ (+`terminal_reason` ⚠), `AgentDefinition` ⚠ (field list per Phase 0), hook events ⚠ (`include_hook_events`), `forward_subagent_text=True` ⚠ for nested text.

**Validation obligations:** real session with ≥1 subagent spawn; evidence shows tree nesting, live token streaming in a screenshot mid-delta, a tool card expanded, an interrupt round-trip, and a permission modal interaction -- all in one sealed run.

---

### Screen 2 -- TOOLS VIEW (`2`)

**Why:** The session stream interleaves tools with prose; operators hunting which tool did what, with what args, and what did it cost in time need a dense, filterable tabular ledger.

```
┌─ TOOLS LEDGER ──────────────────────────────────────────────────── filter: [all ▾] ⌕___ ┐
│ #  │ time     │ agent       │ tool      │ key arg            │ dur    │ status │ cost │
│ 41 │ 12:01:04 │ implement-1 │ Read      │ src/auth/session.… │ 1.21s  │ ✔      │  --   │
│ 42 │ 12:01:06 │ scout-2     │ Grep      │ OAuthState       │ 0.34s  │ ✔      │  --   │
│ 43 │ 12:01:11 │ implement-1 │ Bash      │ pytest -x          │ 22.7s  │ ✖ 1    │  --   │
│ 44 │ 12:01:35 │ orchestr.   │ Agent     │ spawn: validate-3  │  --     │ ◐ perm │  --   │
│ …  │          │             │           │                    │        │        │      │
├─ INSPECTOR: tool #43 ──────────────────────────────────────────────────────────────────┤
│ input:  {command: pytest -x, timeout: 120000}                                        │
│ result: exit 1 -- FAILED tests/test_session.py::test_refresh_race                       │
│ stderr: (412 lines) [view]                              [copy all] [re-run in shell]   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Functional spec:**

1. Row-per-tool-call ledger, newest at bottom, virtualized scrolling (≥10k rows without jank).
2. Columns: seq#, timestamp, attributed agent (or `(unattributed)` warning-styled), tool name, extracted key arg (file path / command / pattern), duration, status glyph, cost (if SDK exposes per-tool cost ⚠; else `--`).
3. Live filters: agent dropdown, tool-name dropdown, status filter, free-text search over args/results (debounced 150ms).
4. Selecting a row populates Inspector with full input JSON, result payload, stderr, duration, token cost if available; `[view]` opens a scrollable full-text modal for long outputs.
5. Failed tools (✖) render error-colored rows and auto-expand a one-line error summary; `f` jumps to next failure.
6. Permission-pending tools appear in ledger as ◐ with the same modal interaction as Screen 1 (single source of truth -- the modal is a global widget).
7. Ledger export: `x` writes the current filtered view as JSONL to the evidence run directory (doctrine: disk facet).

**Data sources:** `ToolUseBlock`/`ToolResultBlock` ✅, hook `PreToolUse`/`PostToolUse` payloads ⚠ (in-band visibility of plugin shell hooks pending verification -- if invisible, ledger derives solely from message stream and marks the hook column `n/a`).

**Validation obligations:** a run containing ≥5 distinct tools including one failure; evidence shows filter interaction, failure jump, full-output modal, and exported JSONL existing on disk with matching row count.

---

### Screen 3 -- HOOKS & EVENTS VIEW (`3`)

**Why:** Proofpunk's behavior is largely hook-driven (evidence-guard, stop-guard, no-test-files, post-write-walkthrough). Operators must see hooks fire, block, and warn -- or the plugin is indistinguishable from magic.

```
┌─ HOOK EVENTS ─────────────────────────────────────────── group: [by hook ▾]  ⚠ source ┐
│ 12:01:02  SessionStart      session-start.sh          ✔ ok      12ms                  │
│ 12:01:06  PreToolUse        evidence-guard.sh         ✔ allow    8ms                  │
│ 12:01:34  PostToolUse       post-write-walkthrough.sh ⚠ warn    31ms  artifact…    │
│ 12:02:11  Stop              stop-guard.sh             ✖ block   15ms  no sealed run│
├─ SYSTEM EVENTS ────────────────────────────────────────────────────────────────────────┤
│ 12:00:58  init    plugins: [proofpunk ✔]  agents: [implement, scout, end-user-validate]│
│ 12:00:59  mcp     3/3 servers healthy (fresh-evidence ✔, …)                            │
│ 12:02:11  block   stop-guard → session continuation requested                          │
├─ INSPECTOR: hook payload ──────────────────────────────────────────────────────────────┤
│ {hook_event: Stop, decision: block, reason: no sealed evidence run,              │
│  raw_transcript_excerpt: …}                                   [copy]                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Functional spec:**

1. Two stacked lanes: **Hook Events** (chronological, groupable by hook script or event type) and **System Events** (init, plugin load, MCP health changes, checkpoint ops, conversation resets ⚠).
2. Each hook row: timestamp, event type, script/matcher name, decision glyph (✔ allow/ok, ⚠ warn/modify, ✖ block), duration, one-line reason.
3. **Honest-source badge:** the header shows whether hook visibility is in-band (`include_hook_events` ⚠ verified working) or log-derived (fallback: tail plugin hook stderr/log files, marked `source: logs`). The product never fabricates in-band hook events.
4. Block decisions (✖) are error-colored and pinned to the top of the lane until acknowledged (any keypress on the row).
5. Inspector shows the full hook payload JSON (in-band) or the captured log excerpt (fallback), with provenance label.
6. System lane records MCP server state transitions with health glyphs; a degradation (e.g., 3/3 → 2/3) flashes warning until acknowledged.
7. Conversation-reset events ⚠ render as a full-width divider in this lane and Screen 1's stream (never silently dropped).

**Data sources:** `HookEventMessage` ⚠, `SystemMessage` init data ✅, MCP status from init + periodic probe ⚠ (SDK method TBD at Phase 0), plugin `hooks.json` (read for matcher inventory at startup).

**Validation obligations:** run with the Proofpunk plugin loaded; evidence captures at least one block decision rendered, provenance badge state, and an MCP health transition (or a documented stable 3/3 with probe logs).

---

### Screen 4 -- EVIDENCE VIEW (`4`)

**Why:** The doctrine's evidence lifecycle (init-run → artifacts → seal → validate) is currently manual shell work. Embedding it turns compliance into a panel the operator watches and drives.

```
┌─ EVIDENCE RUN ─────────────────────────────────────────────────────────────────────────┐
│ run: e2e-evidence/run-20260823-120114-streaming-session          state: ● collecting   │
│ steps: 07 captured │ last: 0007-tool-ledger-export.jsonl (2s ago)                      │
├─ ARTIFACTS ────────────────────────────────────────────────────────────────────────────┤
│ 0001-session-init.json            ✔ disk ✔ scanned                                     │
│ 0002-tree-nested.png              ✔ disk ✔ scanned                                     │
│ 0003-streaming-mid-delta.png      ✔ disk ✔ scanned                                     │
│ 0004-permission-modal.png         ✔ disk ✔ scanned                                     │
│ 0005-interrupt-roundtrip.log      ✔ disk ✔ scanned                                     │
│ 0006-hook-block.png               ✔ disk ✔ scanned                                     │
│ 0007-tool-ledger-export.jsonl     ✔ disk ✔ scanned                                     │
├─ VERDICT BOARD ────────────────────────────────────────────────────────────────────────┤
│ S1 streaming renders live          PASS     0003                                       │
│ S2 tree attribution correct        PASS     0002, 0003                                 │
│ S3 permission modal gates tool     PASS     0004                                       │
│ S4 interrupt honored               PASS     0005                                       │
│ S5 hook block visible              PASS     0006                                       │
│ S6 ledger export on disk           PASS     0007                                       │
├─ ACTIONS ──────────────────────────────────────────────────────────────────────────────┤
│ [e] seal run    [v] validate    [o] open run dir    [s] secret scan (auto pre-seal)    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Functional spec:**

1. On app start with evidence enabled, the product shells out to the real `python3 scripts/fresh_evidence.py init-run <slug>` (from the configured Proofpunk checkout) -- never reimplements the lifecycle.
2. Artifact list mirrors the run directory (watched via filesystem polling ≤1s granularity); each entry shows seq#, name, disk-existence check, secret-scan status.
3. Key product actions auto-capture artifacts: screen captures (Textual SVG/PNG export) on demand via `g` (grab), ledger exports, and interrupt/hook events snapshot their own logs into the run.
4. **Verdict Board:** a user-editable checklist (defined per validation session in `validation/plans/*.md`) mapping success criteria → artifact citations; verdicts restricted to PASS/FAIL/BLOCKED/UNVERIFIED; selecting a verdict row jumps Inspector to the cited artifact.
5. `[e] seal` runs `fresh_evidence.py seal` via subprocess and streams its stdout/stderr into a modal; `[v] validate` runs `validate` and renders its report; failures keep state at `collecting` and mark the board row.
6. Secret scan runs automatically before seal; findings list file:line with redaction hints; seal is blocked until clean or explicitly overridden (override itself is recorded as an artifact -- no silent bypass).
7. If Proofpunk checkout is absent (`--no-plugin` or path invalid), the entire screen shows a disabled state explaining the dependency -- no degraded fake-evidence mode exists.

**Data sources:** Proofpunk `scripts/fresh_evidence.py` CLI ✅, filesystem watch on run dir, Textual screen export API ✅ (`export_screenshot`/SVG), `validation/plans/` files (repo-local).

**Validation obligations:** the evidence run validating the product must itself be produced through this screen's actions (self-hosting proof): evidence shows init via UI, ≥3 `g` captures, a blocked seal on an injected secret (then cleaned), a successful seal, and `validate` output rendered in-app.

---

### Screen 5 -- PERFORMANCE VIEW (`5`)

**Why:** Streaming multi-agent sessions are the worst-case load for a TUI: token bursts, concurrent tool cards, tree mutations. Operators and CI need numeric proof the interface keeps up -- this is the in-product half of the performance-benchmark research.

```
┌─ PERFORMANCE ──────────────────────────────────────────────────────────────────────────┐
│ frame time      p50 3.1ms  p95 9.8ms  p99 14.2ms   budget ≤16ms  ✔                    │
│ event→paint     p50 21ms   p95 88ms   p99 140ms    budget p95≤120ms ✔                 │
│ token render    2,140 tok/s sustained   burst 6,800 tok/s   no dropped events ✔        │
│ memory          184MB RSS   Δ +2.1MB/10min (leak gate: ≤10MB/30min) ✔                  │
│ startup→paint   812ms (cold)            budget ≤2,000ms ✔                              │
├─ LIVE GRAPHS ──────────────────────────────────────────────────────────────────────────┤
│ frame ms  ▁▂▂▃▂▁▁▂▄▃▂▂▁▁▂▂▃▅▃▂▂▁▁▁▂▂▂▁▁▁▂▃▂▁                                          │
│ tok/s     ▃▅█▅▃▂▁▁▂▃▅▇█▆▄▃▃▂▂▁▁▁▂▃▅▄▃▂▁▁▁                                          │
├─ LOAD PROFILE ─────────────────────────────────────────────────────────────────────────┤
│ events processed 14,203 │ reducer queue depth 0 (max 212) │ dropped 0                  │
│ agents seen 7 │ tools 41 │ hooks 12 │ messages 1,884                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Functional spec:**

1. **Performance Budget (binding gates, v1.0):** frame p95 ≤ 16ms; event→paint p95 ≤ 120ms under a 3-concurrent-agent token burst; sustained render ≥ 1,500 tok/s with zero dropped stream events; RSS growth ≤ 10MB over a 30-minute active session; cold startup→first-paint ≤ 2,000ms on a mid-range laptop.
2. All five metrics compute live from in-process instrumentation (monotonic timestamps at SDK-event receipt, reducer enqueue/dequeue, and paint completion); histograms are reservoir-sampled to bound memory.
3. Sparkline graphs update at 2Hz; budget breaches flash the metric error-colored and log a `BUDGET_BREACH` event to the system lane (Screen 3) and to the evidence run.
4. `b` exports the current metrics snapshot as JSON into the evidence run (disk facet for benchmark claims).
5. The external benchmark harness (`validation/perf/`) drives scripted load from real sessions; recorded SDK event replays are prohibited as completion evidence (replays allowed only in contributor inner-loop tooling).
6. Startup timer starts at process entry and stops at first full paint of Screen 1; both cold (fresh venv) and warm numbers recorded.

**Data sources:** internal instrumentation only (no SDK dependency); Textual render hooks; `resource`/`psutil` for RSS.

**Validation obligations:** a 30-minute real-session evidence run with metrics exported at 5-minute intervals; budget table showing all ✔; at least one induced burst (parallel subagent fan-out) with p95 within gate.

---

### 7.6 Overlays and modals (global)

|Overlay|Trigger|Spec|
|---|---|---|
|Help (`?`)|any screen|binding table + screen-specific section; dismiss any key|
|Permission modal|`can_use_tool` ⚠|tool, input summary, risk badge, `a`/`d`/`A`; focus-trapped; never auto-resolves|
|Rewind confirm|`r`|lists checkpoints ⚠, requires typing checkpoint id prefix; labeled destructive|
|Quit confirm|`q` with active session|warns unsealed evidence if run state = collecting|
|Theme picker|`T` (shift-t)|full 20-theme list with live preview under cursor|

## 8. System Architecture

### 8.1 Process topology

```
┌──────────────────────────── proofpunk-agent (one process) ───────────────────────────┐
│  Textual App (asyncio)                                                               │
│   ├─ UI layer: screens 1-5, overlays, widgets                                        │
│   ├─ State store: immutable event log + reducers (tree, ledger, hooks, metrics)      │
│   ├─ SDK bridge: ClaudeSDKClient wrapper (single owner task; queue-based I/O)        │
│   ├─ Evidence bridge: subprocess runner for fresh_evidence.py + fs watcher           │
│   └─ Theme loader: Proofpunk palettes.json reader                                    │
│                                                                                      │
│  External: claude-agent-sdk → bundled Claude Code CLI (child process, SDK-managed)   │
│  External: proofpunk checkout (read-only: plugin, hooks, themes, scripts)            │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Data flow (unidirectional)

1. **SDK bridge** owns the only `ClaudeSDKClient` ✅ instance; a single consumer task iterates `receive_messages()` ✅ and normalizes every message into typed internal events appended to the **event log** (the sole source of truth).
2. **Reducers** subscribe to the log and maintain derived state: agent tree (P3), tool ledger, hook lanes, metrics reservoirs, evidence state. Reducers are pure functions -- replayable, testable, and the foundation for v1.1 session replay.
3. **UI widgets** render from derived state; they never read SDK objects directly. User input flows back as commands (`SendMessage`, `Interrupt`, `SetPermissionMode`, `Checkpoint`, `Rewind`) into the bridge's command queue.
4. **Backpressure:** if reducer queue depth exceeds threshold (HUD shows depth), the bridge applies coalescing to token-delta events (never drops tool/hook/system events) and surfaces a warning -- silent loss is a doctrine violation.
5. **Graceful degradation matrix:**

|SDK capability|If absent/unverified at Phase 0|
|---|---|
|`include_hook_events` ⚠|Hooks screen falls back to log-tail source with provenance badge|
|`forward_subagent_text` ⚠|Subagent text shows as collapsed ran N tools summary nodes|
|`terminal_reason` ⚠|Interrupt outcome inferred from `ResultMessage` subtype with `(inferred)` label|
|hook-level attribution ⚠|Tree uses `parent_tool_use_id` ✅ then `(unattributed)` labels|
|checkpoint/rewind API ⚠|`c`/`r` keys disabled with tooltip; screen section hidden|

### 8.3 Configuration and CLI

```
proofpunk-agent [PROMPT] [--project PATH] [--model MODEL]
                [--effort low|medium|high|max] [--max-budget USD]
                [--resume SESSION_ID] [--theme NAME]
                [--proofpunk-path DIR] [--no-plugin]
                [--evidence-slug SLUG] [--version]
```

* `--proofpunk-path` defaults to auto-discovery: `~/.claude/plugins/proofpunk`, then `$PROOFPUNK_HOME`, then sibling checkout. Discovery result shown in Screen 3 init lane.
* SDK options wired: `plugins=[{type:local,path:…}]` (⚠ exact config shape verified at Phase 0 -- dict vs `SdkPluginConfig`), `setting_sources` per Phase 0 findings, `include_partial_messages=True` ✅, plus all capability flags per §8.2 matrix.
* Permission mode surfaced in header at all times; `bypassPermissions` requires the modal confirm.

### 8.4 Error architecture

* Structured SDK errors (`ResultError` ⚠ structured fields, `ProcessError`, `CLIConnectionError`, `CLIJSONDecodeError` ✅) map to a dedicated error banner widget with: human summary, error class, recovery action (retry/resume/restart), and a `view raw` Inspector jump.
* Bridge death (CLI crash) freezes the tree with current state, marks all running nodes ✖, and offers resume-with-same-session-id.
* Every error event lands in the system lane and the evidence run automatically.

## 9. Security and Trust Boundaries

1. **Project confinement:** SDK `cwd` fixed to `--project` root; the TUI displays the root in the header; no UI affordance can widen it mid-session.
2. **Plugin trust:** the Proofpunk checkout is treated as trusted code (its hooks execute); the path is shown at startup and in Screen 3; inventory of loaded plugin files logged to evidence.
3. **Subprocess policy:** exactly two subprocess families -- the SDK-managed CLI and `fresh_evidence.py`; both launched with explicit argv (no shell strings), recorded to the event log.
4. **Credential hygiene:** evidence auto-scan pre-seal; the composer never echoes secrets flagged by the scanner pattern set; API keys enter only via environment (never CLI args, never rendered).
5. **Irreversible actions:** rewind and bypass-permission mode are the only two; both require confirmation modals and emit audit events.

## 10. Validation Architecture (product-level)

### 10.1 Seven-category mapping

|Category|Implementation in this repo|Completion-evidence eligible?|
|---|---|---|
|1 Functional|contributor tooling only (Textual `Pilot`)|No|
|2 E2E|`validation/e2e/` harness: `script -qfc` sub-PTY driving the installed app|**Yes -- primary**|
|3 Snapshot|contributor tooling (pytest-textual-snapshot)|No (inner loop)|
|4 Fuzz/property|`validation/e2e/fuzz_*.py`: paste bombs, rapid keys during streaming, resize storms -- run under real PTY|**Yes**|
|5 Accessibility|keyboard-only scripted traversal; focus-order assertions; contrast checks per theme tier|**Yes**|
|6 Performance|in-product Screen 5 + `validation/perf/` 30-min real-session benchmark|**Yes**|
|7 Terminal matrix|evidence captured on ≥3 terminal emulators incl. one 256-color and one SSH session|**Yes**|

### 10.2 Harness rules (from Proofpunk tui-testing doctrine, binding)

Real sub-PTY via `script -qfc`; never pipe; observe-before-act with explicit waits; screenshots for visual claims; screen+disk+logs per scenario; secrets scanned; harness lives in-repo; no mutation of a running driver; no double-driving a target.

### 10.3 Release gate (v1.0)

All five Screen-level validation obligation sets (§7) PASS + Performance Budget all ✔ + terminal matrix evidence + one full self-hosted evidence run sealed and validated through Screen 4 itself. Any `UNVERIFIED` or `BLOCKED` item blocks release.

## 11. Roadmap

|Version|Scope|
|---|---|
|v1.0 (this spec)|Single session, five screens, evidence integration, performance instrumentation, neon-tokyo + 20 themes|
|v1.1|Session tabs (`n`/`w`), session replay from event log, checkpoint timeline visualization|
|v1.2|Remote/shared session stores, team evidence review workflow, plugin marketplace browser|

## 12. Phase 0 Verification Register (must resolve before build)

|#|Symbol/claim|Status|Resolution method|
|---|---|---|---|
|1|`AgentDefinition` exact fields|⚠ contradiction in prior notes|read installed `types.py`|
|2|`SdkPluginConfig` dataclass vs dict|⚠|read `types.py` + `client.py`|
|3|`include_hook_events`, `HookEventMessage`|⚠ changelog-only|source + runtime smoke session|
|4|`forward_subagent_text`|⚠ changelog-only|source + runtime smoke session|
|5|`get_context_usage`, `list_subagents`, `get_subagent_messages`|⚠|source read|
|6|`TaskUpdatedMessage`, `terminal_reason`|⚠|source read|
|7|`resume_session_at`, `resume_drops_turn`|⚠|source read|
|8|Plugin shell hooks → in-band visibility|⚠ likely invisible|runtime smoke session with Proofpunk loaded|
|9|Subagent nesting depth ceiling|⚠|runtime experiment (orchestrator→sub→sub)|
|10|`skills=all` validity|⚠|source read|
|11|`skills`/`memory`/`mcpServers`/`maxTurns` on `AgentDefinition`|⚠ contradicts four fields note|source read; reconcile by version|
|12|Checkpoint/rewind API names|⚠|source read|

---

# PART II -- MASTER BUILD PROMPT (proofpunk-agent v1.0)

<!-- Authored by prompt-forge AUTHOR --depth advanced. Combined document per the
     deliverable definition above: Part I (preceding section) is the complete product
     specification and binding authority; Part II (this section, on the canonical XML
     skeleton) is the executable build prompt with validation checkpoints, parallel
     lanes, and orchestration. Feed this single file to the build agent. On any
     conflict, Part I wins — report the conflict, never resolve it silently. -->

<task>
Build the complete proofpunk-agent product — the standalone repository `krzemienski/proofpunk-agent`, v1.0, per the Part I specification above — as one phased end-to-end delivery (phase gates in `<sequential_thinking>` step 3): scaffold the Python 3.10+ repo; resolve the Phase 0 verification register (Part I §12, all twelve rows) against the installed `claude-agent-sdk` source before writing any SDK-touching code; implement the application shell, the five screens, the SDK bridge, the evidence bridge, and the theme loader exactly as Part I §5–§8 prescribe; then prove the product through sealed evidence runs produced by the real validation harness (Part I §10) — driving the installed TUI in a real PTY as its end user. Done means every per-screen validation obligation (Part I §7) and every §10.3 release-gate item shows PASS with full-path artifact citations; anything you did not personally execute stays UNVERIFIED and blocks release.
</task>

<context>
You are a build executor with the Proofpunk plugin (v2.0.1) loaded. Part I (the section above) is the authority; its section numbers are the citation language used in PHASE0.md, evidence manifests, and RELEASE.md. What you know and must not re-derive:

- The product is a Textual TUI (pinned stable) wrapping `claude-agent-sdk` (Python). One process; topology per §8.1; unidirectional data flow per §8.2 (event log is the sole source of truth; reducers are pure; widgets never read SDK objects).
- The Proofpunk plugin is consumed read-only from a discovered checkout (§8.3 discovery order: `~/.claude/plugins/proofpunk`, then `$PROOFPUNK_HOME`, then sibling). Its `themes/palettes.json` feeds the theme system (§5.2); its `scripts/fresh_evidence.py` IS the evidence lifecycle (§2 rule 3, §7 Screen 4); its `tui-testing` doctrine governs E2E (§10.2).
- The Four-Plane agent model (§4) is normative: P1 runtime agents, P2 plugin agents, P3 TUI tree nodes, P4 validation actors. Tree attribution follows the strict preference order in §4 — hook-provided ids, then `parent_agent_id`, then `parent_tool_use_id`, then labeled `(unattributed)` fallback. Timing-based and string-matching attribution are prohibited outside the labeled fallback.
- Every `⚠` in Part I means "verify at Phase 0, never assume." §12 is the register; §8.2's degradation matrix is the decision table for every negative verdict. The SDK version is pinned by what Phase 0 actually inspects (target the installed version exposing `include_partial_messages`, streaming control, subagent forwarding).
- Doctrine (§2) binds the whole build: no mocks/stubs/test-doubles in product code; `tests_dev/` is contributor inner-loop only and never cited as completion evidence; completion evidence = fresh sealed `e2e-evidence/run-*` dirs from the real `fresh_evidence.py` subprocess; real PTY (`script -qfc`) only for E2E claims; verdicts restricted to PASS/FAIL/BLOCKED/UNVERIFIED.
</context>

<skills_to_activate>
- `tui-testing` — canonical E2E doctrine layer: sub-PTY driving, observe-before-act, screenshots for visual claims, three proof facets (screen/disk/logs). Fire it before writing any `validation/e2e/` scenario.
- `end-user-testing` — the Actor Mandate: you drive the installed TUI yourself for every validation claim; unexecuted = UNVERIFIED. Fire it at every checkpoint with a validation obligation.
- `full-functional-audit` — app-wide interaction sweep for the final §10.3 release-gate pass. Fire it once all five screens have landed; per-screen gates stay with `end-user-testing`.
If plugin path discovery fails, stop and report — do not improvise a substitute doctrine.
</skills_to_activate>

<mcp_tools>
None are mandatory. Real-system driving happens through the shell: `script -qfc` for the sub-PTY, the resolved `<plugin-root>/skills/end-user-testing/scripts/fresh_evidence.py` for the evidence lifecycle (resolution contract in `<sequential_thinking>` step 6), git/pip in the project venv, and Textual's own SVG/PNG screen export for captures. If a terminal-automation MCP tool is available in the harness, prefer it for PTY capture per the Actor Mandate's tool-path priority — but never use any tool to bypass the doctrine (no piping the TTY-guarded app, no double-driving a target).
</mcp_tools>

<sequential_thinking>
1. Phase 0 first, always. Read the installed SDK source (`types.py`, `client.py`, changelog) and run one real smoke session with Proofpunk loaded. Write `PHASE0.md` resolving all twelve register rows (§12) with per-row verdict, evidence (file:line or smoke-log excerpt), and the pinned version string. No SDK-touching code exists before PHASE0.md does. Phase cost: 1 file. Gate: verification + operator approval.
2. Freeze the capability contract. For every ⚠ that resolved negative, engage the matching §8.2 degradation-matrix row (hooks → log-tail source with provenance badge; no subagent forwarding → collapsed summary nodes; no `terminal_reason` → inferred label; no hook attribution → `parent_tool_use_id` then `(unattributed)`; no checkpoint API → `c`/`r` disabled with tooltip). Record each decision in PHASE0.md. No new files; approval to proceed closes Phase 0.
3. Execution discipline (binding, from the operator's standing rules): all remaining work runs as numbered PHASES — each phase touches ≤5 files, ends with its own verification evidence, and waits for explicit operator approval before the next phase starts (a one-word `go` advances). Parallelism lives inside a phase: independent lane slices (each ≤5 files, disjoint file sets) run as parallel sub-agents and merge only at that phase's verification step. Never open a new phase in the same response as the previous one. Evidence freshness is per-phase: each phase's Verify step opens its own evidence run and cites only artifacts from that run — prior-run artifacts are regression context, never the phase's PASS citation. Each phase gate also re-runs the previous phase's verification as a regression rail (cheap: the harness is in-repo); a prior-phase regression failure blocks advancement until fixed.
4. Phase 1 — scaffold (5 files): `pyproject.toml` (MIT, py≥3.10, pinned textual + the Phase-0-pinned SDK), `proofpunk_agent/__init__.py`, `__main__.py` (full §8.3 CLI surface), `app.py` (§6.1 chrome, ContentSwitcher, §6.2 global bindings, inline Screen 1 empty state), `theme.py` (`palettes.json` loader, embedded neon-tokyo fallback, §5.2 degradation ladder, live `t` cycling). Verify in a real PTY: chrome renders, empty state shows, `t` cycles, blocking resize notice fires below 100×28.
5. Phase 2 — state core (4 files): `state/events.py` (typed events, immutable log), `state/reducers/__init__.py`, `reducers/tree.py` (§4 attribution order), `reducers/ledger.py`. Verify: replay-determinism regression rail in tests_dev.
6. Phase 3 — bridges (2 files): `bridge/sdk.py` (single-owner client, command queue, §8.2 rule 4 backpressure, §8.4 error mapping), `bridge/evidence.py` (`fresh_evidence.py` subprocess runner + ≤1s fs watcher). Two facts from the real codebase govern this bridge: (a) the script's actual location is `<plugin-root>/skills/end-user-testing/scripts/fresh_evidence.py` — NOT the `scripts/fresh_evidence.py` path Part I §7 Screen 4 names from the checkout — and plugin roots vary by install (dev checkout `<checkout>/plugins/proofpunk/`, cache `~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/<version>/`, marketplace `~/.claude/plugins/marketplaces/proofpunk-marketplace/plugins/proofpunk/`); Part I's `~/.claude/plugins/proofpunk` default matches none of them on a real machine. Resolution contract (recorded in PHASE0.md): treat a candidate as the plugin root iff it contains both `skills/` and `themes/`; resolve the script by globbing `**/end-user-testing/scripts/fresh_evidence.py` under that root; verify it executes (`--help` exit 0) before first use. (b) The script operates on `./e2e-evidence/` relative to its CWD and targets the most-recently-modified run — so the runner pins cwd to the product repo root or an unpinned cwd silently lands runs in the wrong tree. Verify: one smoke session streams events into the log; init-run via the bridge creates the run dir inside the product repo.
7. Phase 4 — remaining reducers (2 files): `reducers/hooks.py` (two lanes, provenance-badge state), `reducers/metrics.py` (reservoir sampling, the five Screen 5 metrics). Verify with the replay rail.
8. Phase 5 — Screen 1 (2 files): `screens/session.py`, `validation/e2e/scenario_session.py`. Verify: §7 Screen 1 obligations — subagent spawn, mid-delta streaming capture, expanded tool card, interrupt round-trip, permission modal.
9. Phase 6 — Screens 2 and 3 as parallel lane slices (4 files): slice A `screens/tools.py` + `validation/e2e/scenario_tools.py`; slice B `screens/hooks.py` + `validation/e2e/scenario_hooks.py`. They share only the global permission modal landed in Phase 5. Verify both screens' §7 obligation sets at the phase gate.
10. Phase 7 — Screen 4 (3 files): `screens/evidence.py`, `validation/plans/session.md`, `validation/e2e/scenario_evidence.py`. Verify self-hosting obligations: init via UI, ≥3 `g` captures, a blocked seal on an injected secret then a clean seal, `validate` rendered in-app.
11. Phase 8 — Screen 5 (2 files): `screens/performance.py`, `validation/perf/driver.py`. Verify: the five budget metrics live, `b` snapshot export lands in the run dir.
12. Phase 9 — fuzz and keyboard traversal (≤5 files): `fuzz_paste.py`, `fuzz_keys.py`, `fuzz_resize.py`, and a keyboard-only traversal script under `validation/e2e/`. Verify: invariants hold under real-PTY input storms (§10.1 categories 4–5).
13. Phase 10 — evidence program (execution-heavy; new files only under `validation/plans/`, ≤5 per sub-phase): per-screen obligation runs, the 30-minute Performance Budget run, the terminal matrix (≥3 emulators incl. one 256-color and one SSH), self-hosted run last — each sealed through Screen 4.
14. Phase 11 — docs and release (3 files): `LICENSE` (full MIT text, copyright holder per repo owner), `README.md` (install, CLI reference, keybinding table §6.2, doctrine note), `RELEASE.md` (verdict table mapping every §7 obligation and §10.3 gate to a verdict and a full-path artifact citation). Any UNVERIFIED or BLOCKED → stop and report honestly; never pad a gate.
Branch rule: a Phase 0 verdict that invalidates a design assumption returns to step 2, re-freezes, and re-slices the affected phases before any further lane work. Never code around an unresolved ⚠.
</sequential_thinking>

<todos>
The build maintains exactly these tracked items; each closes only with cited evidence, and every item lands inside a numbered phase (≤5 files) that advances only on verification evidence plus operator approval:
- PHASE0.md: all 12 register rows resolved, SDK version pinned
- Repo scaffold: pyproject + CLI + shell chrome boots to Screen 1 empty state
- Theme loader: 20 palettes cycle live, fallback warning, degradation ladder
- SDK bridge + event log + reducers with backpressure honored
- Screen 1 Session: tree, streaming, composer, interrupt, permission modal
- Screen 4 Evidence: init-run, artifact watch, seal, validate, self-hosting
- Screen 2 Tools: ledger, filters, failure jump, JSONL export
- Screen 3 Hooks: two lanes, provenance badge, degradation fallback
- Screen 5 Performance: five budget metrics live, snapshot export
- validation/ harness: PTY + fuzz scenarios per §10.2 rules
- Evidence runs: all five screen obligation sets sealed
- Performance budget run: 30-minute session, all gates ✔
- Terminal matrix: ≥3 terminals incl. 256-color and SSH captures
- Self-hosted evidence run produced through Screen 4 itself
- Docs and release: LICENSE + README.md + RELEASE.md verdict table, no UNVERIFIED rows
</todos>

<authorization>
Without asking, you may: create every file in the new repo; create a venv and install the pinned dependencies; run real SDK sessions within the default `--max-budget`; invoke `fresh_evidence.py`; drive sub-PTYs; git init/commit locally.
Explicit consent required first: pushing to any remote; publishing anything; exceeding the budget cap; deleting any evidence run.
Forbidden outright, and consent cannot override: modifying the Proofpunk checkout in any way (read-only; report violations instead); mocks/stubs/test-doubles in product code; citing `tests_dev/` as completion evidence; auto-allowing a permission prompt; overriding a failed secret scan silently (an override is itself a recorded artifact — §7 Screen 4 rule 6).
</authorization>

<constraints>
- Doctrine §2 verbatim and non-negotiable: done means proven by end-user testing; evidence = fresh sealed run dirs from the real `fresh_evidence.py` subprocess; real PTY only for E2E claims; verdicts only PASS/FAIL/BLOCKED/UNVERIFIED with full-path citations.
- Part I is the authority. Do not restate it in code comments — cite §-numbers. Do not exceed v1.0 scope (§11): `n`/`w` ship disabled with tooltip; no replay, no tabs, no remote stores.
- Attribution follows §4's strict order; never timing- or string-matching attribution outside the labeled `(unattributed)` fallback.
- Never fabricate in-band hook events; the honest-source badge (§7 Screen 3 rule 3) is mandatory in both modes.
- Flat black mandate (§5.2): no gradients; status = glyph + color + text, never color alone.
- Terminal floor 100×28 renders the blocking resize notice, never a broken layout; degradation evidence covers truecolor, 256, and 16 tiers.
- Measured implementation tone: prefer/aim-to phrasing for design guidance; absolute language only where doctrine or safety demands it. Human-readable code; no filler comments.
- Every error path lands in the system lane and the evidence run (§8.4); bridge death freezes the tree and offers resume — no silent state loss.
- Phased execution is binding: each phase touches ≤5 files, ends with verification evidence, and waits for explicit operator approval before the next phase begins (one-word `go` advances). Parallelism lives inside a phase as sub-agent lane slices with disjoint ≤5-file sets, merged at the phase verification step. Never start the next phase in the same response.
</constraints>

<output_contract>
Deliver the repository `krzemienski/proofpunk-agent` in exactly this shape (generated dirs appear as runs occur):

```
krzemienski/proofpunk-agent/
├── pyproject.toml                # MIT, py>=3.10, pinned textual + claude-agent-sdk (Phase 0 pin)
├── LICENSE                       # full MIT text (Part I front-matter: MIT)
├── README.md                     # install, CLI reference, keybinding table (§6.2), doctrine note
├── PHASE0.md                     # register table + pinned version + degradation decisions
├── RELEASE.md                    # §10.3 verdict table (final deliverable)
├── proofpunk_agent/
│   ├── __init__.py
│   ├── __main__.py               # CLI entry, full §8.3 flag surface
│   ├── app.py                    # Textual App: chrome, ContentSwitcher, global bindings
│   ├── theme.py                  # palettes.json loader + fallback + degradation ladder
│   ├── bridge/
│   │   ├── sdk.py                # single-owner SDK wrapper, command queue, backpressure
│   │   └── evidence.py           # fresh_evidence.py subprocess runner + fs watcher
│   ├── state/
│   │   ├── events.py             # typed internal events, immutable log
│   │   └── reducers/             # tree, ledger, hooks, metrics (pure functions)
│   └── screens/
│       ├── session.py            # Screen 1
│       ├── tools.py              # Screen 2
│       ├── hooks.py              # Screen 3
│       ├── evidence.py           # Screen 4
│       └── performance.py        # Screen 5
├── validation/
│   ├── plans/                    # per-session criteria checklists (§7 obligations)
│   ├── e2e/                      # PTY scenarios + fuzz_*.py
│   └── perf/                     # 30-minute benchmark driver
├── tests_dev/                    # contributor inner-loop only; never evidence
└── e2e-evidence/run-*/           # sealed evidence runs (generated, never hand-made)
```

RELEASE.md row format: `| obligation (§ref) | verdict | artifact (full path) |`. Every cited artifact must be non-empty (>0 bytes) and belong to a sealed run; a verdict citing a missing or empty file is a FAIL of the release gate itself, not a formatting issue.
Final chat report: the file tree, the RELEASE.md verdict table verbatim, and a blocker list (empty iff shipping).
</output_contract>
<validation>
The Actor Mandate applies to every claim: you personally drive the installed TUI in a real PTY (`script -qfc`) — launch it, press every binding you claim works, watch streaming mid-delta, answer a permission modal yourself, trigger and survive an interrupt, seal a run through Screen 4's own `[e]` action. Observe-before-act: wait for the expected state before the next keystroke; screenshots for visual claims, personally read after capture. Performance numbers are claimed only after reading the exported metrics JSON from disk (asserted non-empty) — the live Screen 5 display is a dashboard, not evidence; numbers come from the 30-minute real session, never synthetic replays (replays are contributor tooling, §7 Screen 5 rule 5). Terminal-matrix claims require captures from the actual emulators. A green `tests_dev/` suite is the regression rail only — labeled REGRESSION, never VALIDATION. Any behavior you did not personally drive is reported UNVERIFIED — and any UNVERIFIED row blocks the release gate.
</validation>

<example>
Example 1 — Phase 0 register resolution (input → expected PHASE0.md row):
Input: row 3 — "`include_hook_events`, `HookEventMessage` ⚠ (changelog-only)".
Positive output: `| 3 | include_hook_events ✅ types.py:L212, client kwarg; HookEventMessage ✅ types.py:L447 | smoke log: run-…/0001-session-init.json | none — in-band hooks lane |`.
Negative output engages §8.2 row 1: hooks screen falls back to log-tail source, provenance badge reads `source: logs`, and PHASE0.md records that decision. Either verdict is acceptable; an assumed one is not.

Example 2 — validation scenario for a Screen 1 obligation:
Input: criterion "S1 streaming renders live" (§7 Screen 1).
Drive: `script -qfc "proofpunk-agent 'scout this repo'"` → observe tree node `● orchestrator` appears (wait, don't guess) → press `g` mid-delta to capture → assert HUD tok/s meter > 0 in the capture → artifact lands as `0003-streaming-mid-delta.png` in the open run dir.
Expected verdict row: `| S1 streaming renders live | PASS | e2e-evidence/run-<id>/0003-streaming-mid-delta.png |`.

Example 3 — degradation fallback (advanced; edge case rehearsal):
Input: Phase 0 row 8 resolves negative — plugin shell hooks are invisible in-band.
Behavior: Screen 3 header badge shows `source: logs`; the hook lane tails the plugin's hook stderr/log files; no `HookEventMessage` is ever synthesized; PHASE0.md records the fallback; one evidence capture shows the badge. The same honesty pattern governs every ⚠: negative verdict + engaged fallback + recorded decision = shippable; silent downgrade or fabricated in-band data = doctrine violation.
</example>
