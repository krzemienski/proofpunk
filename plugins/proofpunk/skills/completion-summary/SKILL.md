---
name: completion-summary
description: >
  The end-of-process gate: confirms every background subagent has finished
  before a stop may be signalled, and writes the run summary that records
  what each agent did. Reads the runtime's subagent tracker, reports one of
  the five states, and exits non-zero while any child is still live. Use at
  the end of a multi-agent run, before claiming a session is complete, or
  when asked to "confirm all agents finished", "write the run summary", or
  "close out the run". Not a substitute for end-user testing — it proves
  agents terminated, never that their work was correct.
---

# Completion summary — the last gate before stop

A session that spawns background children can look finished while they are
still working. This skill answers the question the stop guard cannot answer
from a transcript: **did every agent actually finish, and what did each one
do?**

The state model it applies — the five states, the staleness rule, the
fail-open posture, and the edge cases — is defined in
`../../references/subagent-aware-stop.md`. Read it before changing any behaviour
here; this skill is its end-of-process consumer.

## Run checklist

- [ ] Resolve the session id and cwd (the pair that keys the tracker)
- [ ] Read the tracker; classify every agent
- [ ] If any child is live: STOP. Do not write a summary. Wait or explain.
- [ ] Write the summary artifact, naming every agent and its terminal status
- [ ] Report the state, including anything not *proven* finished

## The contract

```
input   session id + cwd
reads   .omc/state/sessions/<session-id>/subagent-tracking-state.json
writes  a summary artifact naming every agent and its terminal status
exit    0 = all children terminal, summary written
        2 = a live child remains; the stop must not be signalled
```

Run it **before** the stop, never after. A summary written once the session
has ended cannot influence whether it should have ended; the exit code is the
gate, not the prose.

## How to run it

```
python3 skills/end-user-testing/scripts/completion_gate.py \
    --session "$SESSION_ID" --cwd "$PWD" [--out PATH]
```

That single call IS the gate. It reads the tracker, and then either:

- **a child is live** — writes nothing, prints which agents are running, and
  exits **2**. A summary naming a running agent as finished would be false, so
  none is produced.
- **nothing is live** — writes the summary artifact atomically (default
  `run-completion-summary.md`, override with `--out`) and exits **0**.

The exit code is the gate; the artifact is the record. Both come from the same
call, so a summary can never exist for a run that was still working.

For the raw state without writing anything:

```
python3 skills/end-user-testing/scripts/agent_state.py live    --session ID --cwd DIR
python3 skills/end-user-testing/scripts/agent_state.py summary --session ID --cwd DIR
```

## What the summary must contain

- every agent: type, terminal status, `completed_at`
- counts computed from the agents list — **never** from `total_*`. One real
  session on disk reports `total_completed=19` against `total_spawned=4`;
  the aggregate counters are incoherent and must not be quoted.
- any entry aged out by the staleness cutoff, labelled as such, so a leaked
  worker appears in the record instead of being silently dropped
- the state the session ended in, verbatim from the helper

## The five states

| State | Meaning | Stop |
|---|---|---|
| `MAIN_IDLE_CHILDREN_LIVE` | at least one live child | **BLOCKED** |
| `ALL_COMPLETE` | every child terminal | allowed |
| `ALL_COMPLETE_DEGRADED` | nothing live, but something is not *proven* terminal | allowed |
| `MAIN_IDLE_NO_CHILDREN` | no children recorded | allowed |
| `MAIN_ACTIVE` | main thread still working | stop not yet asked |

`ALL_COMPLETE_DEGRADED` is not a rounding of `ALL_COMPLETE`. It means a record
had a missing or unparsable `started_at`, or could not be read at all. Report
it as degraded; writing "all complete" there asserts something unmeasured.

## Platform scope — measured, not assumed

| Runtime | Tracker | This skill |
|---|---|---|
| Claude Code (with OMC) | present | **supported** |
| OMP | absent (0 artifacts found) | reports no children; gate is a no-op |
| OpenCode | absent (0 artifacts found) | reports no children; gate is a no-op |

On a runtime with no tracker the helper returns `MAIN_IDLE_NO_CHILDREN` and
this skill can confirm nothing. Say so in the summary rather than implying a
clean run: absence of a tracker is absence of evidence.

## What this skill does NOT prove

It confirms **recorded** completion. It cannot prove a process exited — the
tracker carries `status`, `agent_type`, `started_at`, `completed_at`, and no
liveness field. A child that crashed without writing a terminal status stays
`running` until it ages out.

So: never write "all agents completed successfully" on the strength of this
skill. Write what was measured — which agents reached a terminal status, which
aged out, and which could not be read.

## Anti-patterns

| Pattern | Do instead |
|---|---|
| Writing the summary after the stop | Run it before; the exit code is the gate |
| Quoting `total_completed` | Count the agents list; the counters are incoherent |
| Calling a degraded state complete | Report `ALL_COMPLETE_DEGRADED` and name the record |
| "All agents finished successfully" | Name terminal statuses; success is not in the tracker |
| Blocking forever on a leaked child | The cutoff ages it out; that is by design |

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `end-user-testing` | after the gate passes | the proof standard for the run's own claims |

Called by: `proofpunk`.

Not yet called by `implement`. Wiring it into that skill's Stage 7 requires an
edge in its own calls table; claiming the caller here before that edge exists
would be an unbacked claim, and `verify-orchestration.py` checks exactly that
in both directions.
