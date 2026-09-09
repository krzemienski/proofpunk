# /proofpunk:verify — end-to-end command-surface proof

## Proof level achieved: END-USER (full chain, one artifact)

Typed invocation → Skill load → dispatched worker execution → real bash
tool execution → observed output that matches independently-verified
ground truth, all captured in one streaming session transcript.

## Exact typed invocation

```
claude --model haiku -p '/proofpunk:verify "read tools/gauge-report.py and run one bash command that prints its first line and its byte size, nothing else"' \
  --output-format stream-json --forward-subagent-text --verbose \
  --max-budget-usd 3.00 --no-session-persistence --dangerously-skip-permissions
```

- Host: `claude` 2.1.260 (Claude Code CLI), headless/`-p` mode.
- Working directory at invocation: `/Users/nick/proofpunk/evidence/v3-release/l16-commands/scratch/realverify5` (a fresh scratch subdir inside this repo — never `/tmp`, per the macOS `/tmp` → `/private/tmp` symlink trap).
- `--forward-subagent-text` was required: this host runs Claude Code in
  "coordinator mode" (`CLAUDE_CODE_COORDINATOR_MODE=1` in
  `~/.claude/settings.json`), under which the TOP-LEVEL session has NO
  `Bash`/`Read` tool at all — every real-world action is delegated to a
  background worker `Agent`, and by default `--print` mode exits as soon
  as the top-level turn ends, before the async worker's own tool calls are
  visible in the parent's output stream. `--forward-subagent-text` plus
  `--output-format stream-json` forwards the worker's tool_use/tool_result
  events (tagged with `parent_tool_use_id`) into the same JSONL stream,
  which is what makes the full chain observable in ONE artifact instead of
  two disjoint ones.

## Raw artifact

Full unedited stream: `evidence/v3-release/l16-commands/scratch/realverify5/out.jsonl` (125 NDJSON events, 345,573 bytes; `err.log` empty, 0 bytes — stderr and stdout captured to separate files).

## Exit code (captured separately from stdout, never piped)

The invoking shell command was:
```
timeout 170 claude ... > out.jsonl 2>err.log
```
Job snapshot: `Wall time: 98.71 seconds` and no error text — the async
job harness reports **RC=0** (completed cleanly, well under the 170s
timeout; `timeout`'s own exit code of 124 would have meant a real hang,
and it did not fire).

## The chain, event by event (line numbers are 0-indexed NDJSON lines in out.jsonl)

| Step | Line | parent_tool_use_id | Event |
|---|---|---|---|
| 1. Typed skill invocation | 21 | (none, top-level) | `Skill` tool_use: `{"skill": "proofpunk:verify", "args": "read tools/gauge-report.py and run one bash command that prints its first line and its byte size, nothing else"}` |
| 2. Skill loads (doc → contract) | 23 | (none) | tool_result: `Loaded skill instructions (read-only): proofpunk:verify. Nothing was executed; delegate execution to a worker.` |
| 3. Coordinator tries directly, is refused | 26–29 | (none) | `Read` and `Bash` tool_use both error: `No such tool available … not available to you as the coordinator — run it from a worker via the Agent tool instead.` This is the platform enforcing exactly the flag-mapping-to-execution boundary the gauge asks to prove: the command doc's instruction cannot be short-circuited by the coordinator itself. |
| 4. Delegation to a real worker | 31–34 | (none) | `Agent` tool_use with `subagent_type: "proofpunk:end-user-validate"` (the skill's OWN backing agent, from `plugins/proofpunk/agents/end-user-validate.md`) and a prompt instructing it to execute the verification; tool_result confirms async launch, `agentId: a2cdf23b733c57005`. |
| 5. Worker reads the real file | 40, 43 | `toolu_01PSk351pi8qYLoRLTVJG4yN` | `Read` tool_use on `/Users/nick/proofpunk/tools/gauge-report.py`; tool_result returns the file's real first lines (`#!/usr/bin/env python3`, the actual header comment). |
| 6. Worker runs the real bash command | 49, 53 | `toolu_01PSk351pi8qYLoRLTVJG4yN` | `Bash` tool_use: `head -n1 /Users/nick/proofpunk/tools/gauge-report.py && wc -c < /Users/nick/proofpunk/tools/gauge-report.py`; tool_result: `#!/usr/bin/env python3` / `   29011`. |
| 7. Worker's own verdict | 60 | `toolu_01PSk351pi8qYLoRLTVJG4yN` | Worker's text block: `"Verdict: PASS … First line: `#!/usr/bin/env python3` …"` — a genuine executed, cited verdict per the command doc's contract ("Every claim in the final report must cite executed evidence"). |
| 8. Session termination | 95, 124 | (none) | Two `result` events (`subtype: success`, `is_error: false`), final cost `$1.00247985`. |

## Independent cross-check (this lane's own verification, not the worker's self-report)

```
wc -c /Users/nick/proofpunk/tools/gauge-report.py
```
→ `29011 /Users/nick/proofpunk/tools/gauge-report.py`

This matches the worker's captured output **exactly** (`29011`). The
worker's claim is not merely plausible text — its executed number is
independently reproducible against the live file at the time of this
lane's own measurement (`2026-09-04T15:xx:xx` per this session).

## Guard-against-false-pass checklist (per assignment)

- (a) Text matching: REJECTED as sufficient. The proof above requires the
  successful `ToolResult` at lines 43 and 53 (Read and Bash), not just the
  presence of the word "gauge-report.py" somewhere in output.
- (b) Namespaced invocation only: `/proofpunk:verify` was typed with the
  `proofpunk:` prefix throughout; no bare `/verify` was used (a bare
  `verify` skill DOES exist standalone on this host at
  `~/.claude/plugins/cache/.../verify` from an unrelated marketplace — see
  `bare-check-out.json` in scratch — and would NOT be attributable to this
  plugin).
- (c) Retried-failure-counted-as-success: the coordinator's own two direct
  `Read`/`Bash` attempts (lines 26–29) FAILED with a tool-unavailable
  error and are NOT counted as proof; only the delegated worker's
  successful execution (lines 40–53) is cited as the pass.
- (d) `/tmp` vs `/private/tmp`: all scratch and evidence files were written
  under `/Users/nick/proofpunk/evidence/v3-release/l16-commands/scratch/`,
  inside the repo, never under `/tmp`.

## Verdict

**PASS — end-user proof level.** Typed `/proofpunk:verify` invocation
correctly maps to the skill's documented protocol (Read the file, run ONE
bash command, cite executed evidence, emit a verdict); flags/positional
argument were correctly threaded through `Skill` → dispatched `Agent`
(`proofpunk:end-user-validate`, the skill's actual backing agent) → real
`Read` + `Bash` tool execution → an observed, independently-reproducible
result (`29011` bytes, matching ground truth) → a cited PASS/FAIL verdict.
