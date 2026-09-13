---
name: completion-summary
description: >
  The end-of-process gate: confirms no background subagent is RECORDED as
  still running before a stop may be signalled, and writes the run summary
  that records each agent's recorded status. Reads the runtime's subagent
  tracker,
  reports one of the four tracker-derived states, and exits non-zero while any child is
  recorded live. Use at the end of a multi-agent run, before claiming a
  session is complete, or when asked to "confirm all agents finished",
  "write the run summary", or "close out the run". Confirms RECORDED
  completion only: the tracker is a snapshot, never process liveness, and
  only Claude Code writes one. Not a substitute for end-user testing.
---

# Completion summary — the last gate before stop

A session that spawns background children can look finished while one is
still RECORDED as running. This skill answers the question the stop guard cannot answer
from a transcript: **is any child still recorded as running, and what did
each one do?**

The state model it applies — the state set, the staleness rule, the
fail-open posture, and the edge cases — is defined in
`../../references/subagent-aware-stop.md`. Read it before changing any behaviour
here; this skill is its end-of-process consumer.

## Run checklist

- [ ] Resolve the session id and cwd (the pair that keys the tracker)
- [ ] Read the tracker; classify every agent
- [ ] If any child is recorded running (and not aged out): STOP. Do not write
      a summary. Wait or explain.
- [ ] Write the summary artifact, naming every agent and its recorded status
      (a malformed or unknown entry renders as `?` / `-`, never as terminal)
- [ ] Report the state, including anything not *proven* finished

## The contract

```
input   session id + cwd
reads   .omc/state/sessions/<session-id>/subagent-tracking-state.json
writes  a summary artifact naming every agent with its recorded type, id,
        status and completed_at. Those four fields are all the tracker
        carries — the summary cannot say what an agent DID, only what was
        recorded about it. Unknown/malformed entries render `?` and `-`.
exit    0 = no child is recorded live, summary written. This covers three
            distinct states, not one: ALL_COMPLETE (every entry terminal),
            MAIN_IDLE_NO_CHILDREN (no tracker, or no entries — the case for
            every runtime except Claude Code), and ALL_COMPLETE_DEGRADED
            (nothing live, but at least one entry not PROVEN terminal). The
            summary names which one; the exit code alone does not.
        2 = a child is recorded live, OR the summary could not be written.
            Both mean the stop must not be signalled: an unwritten summary
            is not a passed gate.
```

Run it **before** the stop, never after. A summary written once the session
has ended cannot influence whether it should have ended; the exit code is the
gate, not the prose.

## How to run it

```
python3 plugins/proofpunk/skills/end-user-testing/scripts/completion_gate.py \
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
python3 plugins/proofpunk/skills/end-user-testing/scripts/agent_state.py live    --session ID --cwd DIR
python3 plugins/proofpunk/skills/end-user-testing/scripts/agent_state.py summary --session ID --cwd DIR
```

## What the summary must contain

- every agent: type, recorded status, `completed_at` (`?` and `-` when the
  record is unknown or malformed — never rendered as terminal)
- counts computed from the agents list — **never** from `total_*`. One real
  session on disk reports `total_completed=19` against `total_spawned=4`;
  the aggregate counters are incoherent and must not be quoted.
- any entry aged out by the staleness cutoff, labelled as such, so a leaked
  worker appears in the record instead of being silently dropped
- the state the session ended in, verbatim from the helper

## The states

| State | Meaning | Stop |
|---|---|---|
| `MAIN_IDLE_CHILDREN_LIVE` | at least one live child | **BLOCKED** |
| `ALL_COMPLETE` | no child recorded live; every entry terminal or aged out | allowed |
| `ALL_COMPLETE_DEGRADED` | nothing live, but something is not *proven* terminal | allowed |
| `MAIN_IDLE_NO_CHILDREN` | no children recorded | allowed |
| `MAIN_ACTIVE` | main thread still working | stop not yet asked |

The first four are **tracker-derived** and are the only values this skill can
report: `agent_state.py` defines exactly those four `STATE_*` constants.
`MAIN_ACTIVE` is stop-hook context, not a classification of the tracker —
there is no input from which this skill could derive it, because it only runs
once a stop has been asked for. It is listed to complete the state model
(`../../references/subagent-aware-stop.md` §2), never as an output.

`ALL_COMPLETE` means no child is recorded live and every entry is terminal
**or aged out past the staleness cutoff**. An aged-out entry is treated as
finished by age alone, not by a recorded terminal status — the summary labels
those explicitly so a leaked worker stays visible.

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

Called by: `implement` (Stage 7, before the report), `proofpunk`.
