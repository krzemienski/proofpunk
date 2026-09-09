# Live-session hook probes — orchestrator-driven after the session lock released

Driven 2026-09-04 by the orchestrator, after `LaneCommandSurface` released its
exclusive lock on `tools/sdk_probe.py`. `LaneHooksDoctrine` correctly recorded
all five of these as UNVERIFIED rather than upgrading them from a stale
`e2e-evidence/run-sdk-probes/` capture that predates its own `stop-guard.sh`
change.

## Results

| Probe | rc | Verdict | Artifact |
|---|---:|---|---|
| `stop_guard` | 0 | **PASS** | `step-04-live-stop_guard.log` |
| `instructions_loaded` | 0 | **PASS** | `step-04-live-instructions_loaded.log` |
| `blocks_test_file` | 1 | **UNVERIFIED** — probe could not run | `step-04-live-blocks_test_file.log`, retry `step-05-retry-blocks_test_file.log` |
| `allows_normal_file` | 1 | **UNVERIFIED** — probe could not run | `step-04-live-allows_normal_file.log`, retry `step-05-retry-allows_normal_file.log` |
| `doctrine` | 1 | **UNVERIFIED** | `step-04-live-doctrine.log` |

**Two hooks reach live-session proof. Three do not, for an environmental
reason that is not a proofpunk defect.**

## Why three probes could not run — diagnosed, not assumed

The failing signature was identical across runs:

```
checks: {'write_attempted': False, 'artifact_matches': True, 'denial_matches': False}
hooks:  []
```

`hooks: []` means **no hook fired at all** — so this cannot be read as "the
hook failed to block." Nothing reached the hook layer.

The model's own reply names the cause verbatim
(`step-05-retry-blocks_test_file.log`):

> "Cannot do it. This session has no Write tool — available tools are
> `ListAgents`, `SendMessage`, `Skill`, `TaskStop`, `Workflow` only."

The probe requests `allowed_tools=["Write"]`, but the session it was spawned
into did not grant a Write tool. With no Write attempt, `PreToolUse` on
`Write|Edit` is unreachable by construction.

### The probes behaved correctly by failing

`sdk_probe.py:92` sets `require_write_attempt=True` with the comment
"model must actually try, else vacuous." That guard did exactly its job: a
probe that cannot exercise its subject reports **failure**, not a green tick.
A harness that returned PASS here would be the false-pass defect this repo
corrects most often.

### What was ruled out before concluding

- **Stale artifact from a prior run** — checked `/tmp/proofpunk_probe/`: empty
  (0 files) before the first run. Cleared and re-driven anyway; identical result.
- **Transient failure** — re-driven a second time; byte-identical signature.
- **Hook regression** — refuted independently: the same guards pass 60/60 at
  script level (`bash tools/test-hooks.sh` rc=0), and `no-test-files.sh` is
  unchanged in this run.

## Correct scoping of the claim

| Hook | Script-level | Live-session |
|---|---|---|
| `stop-guard.sh` | PASS (60-case harness) | **PASS** (this run) |
| `instructions-loaded.sh` | PASS | **PASS** (this run) |
| `no-test-files.sh` | PASS | **UNVERIFIED** — probe environment lacks a Write tool |
| doctrine injection (`session-start.sh`) | PASS | **UNVERIFIED** |

`docs/hook-enforcement-map.md`'s live-session column must reflect exactly
this: two PASS, three UNVERIFIED. Nothing here licenses upgrading
`no-test-files.sh` to live-proven.

## Open / UNRESOLVED

- Whether `allowed_tools=["Write"]` is silently dropped when `sdk_probe.py`
  runs inside an already-nested agent session, versus a host-level policy
  denying Write to spawned sessions, is **not established**. Both are
  consistent with the observed output. Distinguishing them requires running
  the probe from a top-level session — not available from this orchestration
  context.
- `doctrine` (rc=1) was not diagnosed to the same depth as the two Write
  probes. It is recorded UNVERIFIED on its exit code alone; no claim is made
  about its cause.
