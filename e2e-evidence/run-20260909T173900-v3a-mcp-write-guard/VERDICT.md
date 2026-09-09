# VERDICT — v3(a) D-A MCP write-guard fix: PASS (1 control arm UNVERIFIED)

Run: 2026-09-09T17:39Z, this session. HEAD at run time: 8537b3f + uncommitted D-A fix.

## The fix

- `plugins/proofpunk/hooks/hooks.json` — PreToolUse and PostToolUse matchers
  `Write|Edit` → `^(Write|Edit|mcp__[A-Za-z0-9_]+__(write|edit|move|create|rename|delete|remove)[A-Za-z0-9_]*)$`
  (JS-regex path per the documented matcher semantics; read-only MCP tools
  do not route — 8 match / 9 non-match vector check).
- 4 guard scripts (`no-test-files`, `evidence-guard`, `capture-guard`,
  `post-write-walkthrough`) — read `tool_input.path` in addition to
  `tool_input.file_path` (MCP filesystem payloads use `path`; pre-fix the
  scripts extracted an empty path and failed open even if routed).

## AC1 — live arms (tools/probe-mcp-write-guard.py, real claude_agent_sdk
sessions, real MCP filesystem server scoped to a canonical per-arm sandbox)

**Final artifacts** (harness v3: result capture, plugin-identity assertion,
block-is-goal denial prompts):

| Arm | Artifact | Result |
|---|---|---|
| denial_test_file | step-17-denial-testfile-v3.json | PASS — PreToolUse exit 2, guard identified in hook payload, tool result is_error, file absent, this checkout's plugin path proven in init |
| denial_secret | step-18-denial-secret-v3.json | PASS — same check set |
| control_write | step-15-control-write-v2.json | PASS — compliant MCP write landed, sha256(file) == sha256(successful call's content) |
| control_read | step-16-control-read-v2.json | PASS — MCP read unimpeded |
| control_no_plugin | — | **UNVERIFIED** — requires `setting_sources=[]` for a clean no-plugin arm, which breaks OAuth on this host (step-03). Attribution does not rest on this arm: the denying hook payload names the proofpunk guard and the init message proves this checkout loaded. |

Superseded (kept as harness-development record, not cited as proof):
step-02, step-05..step-11 (v1/v2 harness: `result` lost to a missing
`nonlocal`, no plugin-identity capture, sandbox spelling not canonical).
step-13 (v2 test-file arm) FAILED honestly: the model refused preemptively
citing an ambient host `block-test-files` rule — a model-level refusal,
not a guard signal; the block-is-goal prompt framing resolved it.

Earlier summary (superseded artifact numbers):

| Arm | Artifact | Result |
|---|---|---|
| denial_test_file | step-11-denial-testfile-canonical.json | PASS (v1 harness) |
| denial_secret | step-10-denial-secret-canonical.json | PASS (v1 harness) |
| control_write | step-07-control-write-canonical.json | PASS (v1 harness) |
| control_read | step-09-control-read-fixed.json | PASS (v1 harness) |
| control_no_plugin | — | **UNVERIFIED** — requires `setting_sources=[]` for a clean no-plugin arm, which breaks OAuth on this host ("OAuth session expired and could not be refreshed", step-03). The denial arms identify the denying guard by name in the hook payload, so attribution does not rest on this arm. |

## AC2 — mutation proof

step-12a baseline pass (rc=0) → step-12b mutated matcher `Write|Edit`:
rc=1, failure names the four unrouted MCP tools by name → step-12d
restored: rc=0, sha256 before == after (step-12-hooks-sha256-{before,after}.txt).

## Regression posture

- `tools/test-hooks.sh` rc=0 incl. 7 new D-A cases (M1 matcher-routing
  parsed from hooks.json itself; M2–M6 MCP `path`-key payloads).
- `tools/test-installer.sh`, `tools/dry-run-install.sh`,
  `tools/verify-orchestration.py` — all rc=0.
- First-party Write still enforced: step-04-sdk-firstparty-write.json —
  hook exit 2, file absent (probe's overall `pass:false` is its own
  text-fragile denial-string check; enforcement fields all correct).
- Retired false-block vectors (`cp -p`, `mv -f`, `touch -c`, `sed -i -e`)
  remain silent — no shell parsing was added.
