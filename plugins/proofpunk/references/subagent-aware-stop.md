# Subagent-aware stop — the state model

A stop guard that reasons only about the main thread will release a session
whose children are still working. This reference defines the states, the
transitions, and the edge cases that a correct guard must survive.

Every fact below was measured in this repo. Citations are `path:line`.

## 1. Why the shipped guard gets this wrong

Three independent confirmations, all measured:

| Fact | Citation |
|---|---|
| One script is wired to **both** `Stop` and `SubagentStop` | `plugins/proofpunk/hooks/hooks.json:16-37` |
| That script extracts `hook_event_name` once and branches on it **never** | `plugins/proofpunk/hooks/stop-guard.sh:71` (1 reference, 0 conditionals) |
| The identical treatment is **documented as intended** | `plugins/proofpunk/docs/hooks-and-init-design.md:33` — "same check, subagent transcript" |

Consequence: a finishing subagent is graded by main-thread completion rules.
A subagent is not required to report completion to the main thread, so its
transcript legitimately lacks a proof citation — and the guard reads that
absence as an unproven claim.

Symmetrically, the main `Stop` event knows nothing about children: no matcher
in `hooks.json` matches the spawn tool, so a spawn is never observed.

## 2. The five states

```
MAIN_ACTIVE          main thread still working              -> stop not yet asked
MAIN_IDLE_NO_CHILDREN  main idle, zero live children        -> STOP ALLOWED
MAIN_IDLE_CHILDREN_LIVE main idle, >=1 live child           -> STOP BLOCKED
ALL_COMPLETE         main idle, every child terminal        -> STOP ALLOWED
ALL_COMPLETE_DEGRADED main idle, nothing live, but >=1 entry
                     not PROVEN terminal                    -> STOP ALLOWED
```

`MAIN_IDLE_CHILDREN_LIVE` is the state the shipped guard cannot represent, and
the only one that must block.

`ALL_COMPLETE_DEGRADED` exists because four states could not tell the truth. An
entry with a missing or unparsable `started_at`, or an unreadable record, is
not *proven* finished — reporting it as `ALL_COMPLETE` would assert something
unmeasured. The stop is still allowed (§3), but the state name says so.

## 3. What "live" means — and why age is part of the definition

A child is **live** iff:

```
status == "running"  AND  age(started_at) <= STALE_CUTOFF
```

The age clause is not defensive padding. It is forced by measurement:

```
running agent age: 257.5 h   type=worker
running agent age: 257.5 h   type=worker
running agent age: 266.2 h   type=worker

running agents: 3    older than 1 hour: 3
```

All three are leaked; no process has lived 11 days. A guard that blocks on
`status == "running"` alone would wedge **every** session in this repo on the
first stop, forever. Correctness here means bounding staleness, not trusting
the flag.

`STALE_CUTOFF` is **10 minutes** (operator-approved). The runtime's own
tracker uses 5 minutes (`STALE_THRESHOLD_MS = 5 * 60 * 1000`), so 10 is
deliberately the more conservative direction: it releases later, never
earlier, than the runtime would.

## 4. Counters are not the source of truth

```
session bf6d2762: agents=3  total_spawned=4  total_completed=19
```

`total_completed` (19) exceeds `total_spawned` (4) by 15. The aggregate
counters are incoherent, so the decision must be computed from the `agents`
list itself, never from `total_*`.

## 5. Where the state lives

The runtime already maintains the registry this design needs:

```
.omc/state/sessions/<session-id>/subagent-tracking-state.json
```

**Which runtimes actually write it — measured, not assumed.**

| Runtime | Tracker artifacts found | Consequence |
|---|---|---|
| Claude Code (with OMC installed) | 4 (writer + 3 live state files) | subagent-aware stop is **supported** |
| OMP | 0 | tracker absent; see below |
| OpenCode | 0 | tracker absent; see below |

So this mechanism is an **OMC/Claude-runtime integration**, not a universal
one. Reading the same path on OMP or OpenCode would be convention, not
evidence.

On a surface with no tracker the helper returns `MAIN_IDLE_NO_CHILDREN` with
the reason "no tracker file", i.e. **UNSUPPORTED collapses into fail-open**
(§6) — those surfaces keep exactly their current stop behaviour and gain
nothing. That is stated as a limitation; it is not parity.

If subagent-aware stop is ever required on OMP or OpenCode, it needs a writer
on that runtime first. Nothing in this design supplies one.

Measured shape (3 real files):

```
keys:   agents, total_spawned, total_completed, total_failed, last_updated
agents[]: status, agent_type, started_at, completed_at
status:   "running" | "completed"   (also "failed" per the writer)
```

It is written on `SubagentStart` (`status: running`) and flipped on
`SubagentStop` (`completed`/`failed`, plus `completed_at`).

Reading it costs one small JSON parse. The alternative — pairing
`tool_use(Agent)` ids against `tool_result.tool_use_id` in the transcript —
works but is strictly worse inside a 10s hook timeout: the sampled transcript
was 3547 records, and the guard's 40-line window contained **0 of 13** spawns
(all sat 546-3393 lines from EOF).

Transcript pairing therefore stays a documented fallback, not the mechanism.

## 6. Fail-open, and why it is not a loophole

If the tracker is missing, unreadable, or malformed, the guard **allows** the
stop and says so. A stop guard that cannot read state must never trap the
session: the failure mode of blocking-on-ignorance is an unrecoverable hang,
which is worse than the bug being fixed.

This is the same posture the existing guard already takes for a missing
interpreter — fail open, but *announced*, never silent.

## 7. Edge cases the design must survive

| Case | Required behaviour |
|---|---|
| Child spawns a grandchild | Grandchild appears in the same `agents` list; any live entry blocks. Depth is irrelevant. |
| Child fails | `status: failed` is terminal. Failure is not liveness; it must not block. |
| Child crashes without writing a terminal status | Entry stays `running` and ages out at the cutoff. This is exactly the leaked-worker case measured above. |
| Tracker written concurrently by two children | The runtime writer holds a lock (`staleLockMs`, `index.js:40`). The guard only ever **reads**, so it cannot corrupt state; a torn read fails open per §6. |
| `SubagentStop` fires for a child | Must not be graded by main-thread completion rules (the §1 defect). A child's own stop is not the session's stop. |
| No tracker at all (fresh session, no children) | Zero live children -> `MAIN_IDLE_NO_CHILDREN` -> allowed. |

## 8. What is deliberately *not* claimed

`status: running` is a **state snapshot, not process liveness**. Nothing in the
tracker proves a pid is alive; that is precisely why the age bound exists. A
design claiming true liveness would need a field the tracker does not carry
(measured fields: `status`, `agent_type`, `started_at`, `completed_at`).

OpenCode exposes no child state at all: `SessionStatus` is `idle | retry | busy`
and `session.idle` carries only `sessionID`
(`~/.config/opencode/node_modules/@opencode-ai/sdk/dist/gen/types.gen.d.ts:396-418`).
It can therefore only inherit the tracker file — it has no native signal to read.

## 9. The completion skill

The doc asks for a skill invoked at the end of a process that confirms every
agent finished and writes the run summary before stop is signalled.

**Contract**

```
input   session id + cwd  (the same pair that keys the tracker)
reads   .omc/state/sessions/<id>/subagent-tracking-state.json
writes  a summary artifact naming every agent and its terminal status
exit    0 = all children terminal, summary written
        2 = a live child remains; stop must not be signalled
```

**Why it is a skill and not more hook logic.** The hook answers a yes/no
question in under 10 seconds (`hooks.json` timeout). Reviewing the run and
writing a durable summary is model work: it reads the sequence, names what
each agent did, and records the outcome. Those belong on opposite sides of the
procedure/judgement line the intent gate already draws — the hook enforces
*that* a check happened; the skill performs it.

**Ordering.** The skill runs *before* the stop is signalled, not after. A
summary written after the session ends cannot influence whether it should
have ended. Its exit code is the gate.

**What the summary must contain**

- every agent: type, terminal status, `completed_at`
- the counts, computed from the list — never from `total_*` (§4)
- any entry aged out by the cutoff, labelled as such, so a leaked worker is
  visible in the record rather than silently dropped
- the state name (§2) the session ended in

**Honest limit.** The skill confirms *recorded* completion. It cannot prove a
process exited — that is the same snapshot-not-liveness limit as §8, and the
summary must not imply otherwise.
