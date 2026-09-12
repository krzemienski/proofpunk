# Intent Verification (shared)

The stop guards ask *"was a completion claimed without evidence?"*. That
catches an unproven claim. It does not catch the more expensive failure: a
session that produced real evidence for **work nobody asked for**, or for a
fraction of what was asked.

This contract adds the second question — *did this session accomplish what the
original request set out to do?* — and bounds what happens when the answer is
no.

## The split that makes it checkable

**A hook cannot judge whether intent was met.** That is a natural-language
comparison between a request and everything that followed. A regex attempting
it would be a guard faking comprehension, which is the defect class this
plugin exists to prevent.

So responsibility divides:

| Who | Does what | How it is checked |
|---|---|---|
| The **model** | Reads the whole session, compares outcome to original intent, records a verdict | The verdict file exists and states MET or UNMET |
| The **stop guard** | Refuses to let the session end without a verdict, or with an UNMET one | Mechanical: file present? verdict string? attempt count? |

Neither half pretends to do the other's job. The hook never reads intent; the
model never enforces the stop.

## The verdict file

One JSON file per session, written by the model, read by every stop surface:

```
~/.proofpunk/intent/<sha256(session_id:cwd)[:32]>.json
```

Same namespace convention as `~/.proofpunk/bash-baselines/` used by
`bash-write-snapshot.sh:147`, so all three runtimes reach it identically — it
is a home-relative path, not a platform API.

```json
{
  "session_id": "abc123",
  "cwd": "/repo",
  "original_intent": "verbatim first user request, never summarized",
  "verdict": "MET" | "UNMET" | "PARTIAL",
  "unmet": ["specific thing asked for that did not happen"],
  "attempt": 1,
  "next_prompt": ".prompts/fix-<slug>.prompt.md",
  "recorded": "2026-09-12T18:00:00Z"
}
```

`original_intent` is **verbatim**. A summary is the model's paraphrase of the
request, and grading against a paraphrase grades the paraphrase.

## The verification pass

Runs before a session claiming completion may stop.

1. **Recover the original intent.** The first `user` record in the session
   transcript, verbatim. On Claude Code that is `transcript_path` from the Stop
   payload — the complete JSONL, not a tail. Measured: every transcript under
   `~/.claude/projects/` carries typed `user` records with the first request
   intact.
2. **Read the whole session.** Not a window. The gap between what was asked and
   what happened is frequently visible only at the start — a request with four
   clauses where the session addressed the first.
3. **Use sequential thinking.** Required, not advisory. Reviewing a long
   session for intent satisfaction is exactly where skipping ahead produces a
   summary instead of a review.
4. **Judge each clause of the request separately.** "Do X and also Y" is two
   obligations. A session that nails X and never mentions Y is UNMET, not
   PARTIAL-in-spirit.
5. **Record the verdict** at the path above.
6. **If UNMET** — write the next-session fix prompt naming precisely what was
   not done, and increment `attempt`.

## The bound

**Three attempts, then escalate.** Operator-approved 2026-09-12.

| `attempt` | On UNMET |
|---|---|
| 1, 2 | Write the fix prompt, restart `implement` |
| 3 | Write the fix prompt, **stop**, escalate with a blocker report |

An unbounded retry loop on an unachievable goal burns the budget and surfaces
as exhaustion rather than as a diagnosis. The cap converts that into a
structured hand-back naming the unmet intent and what was tried.

The counter lives in the verdict file, so it survives a restart — the thing a
loop bound must survive to mean anything.

## What each stop surface enforces

| Surface | Mechanism |
|---|---|
| `hooks/stop-guard.sh` | `{"decision":"block","reason":...}` |
| `extensions/proofpunk.ts` | `{continue: true, reason}` from `session_stop` |
| `opencode/plugin/proofpunk.ts` | per the OpenCode plugin API |

All three apply one rule: **a completion claim with no intent verdict, or with
an UNMET verdict below the cap, does not end the session.** At the cap they
allow the stop and require the escalation report instead — because refusing to
stop at that point would be the unbounded loop the cap exists to prevent.

## Failure modes this is designed against

- **Evidence for the wrong work.** Real artifacts, real drives, real PASS
  verdicts — for something other than what was asked. Every existing gate goes
  green.
- **Partial satisfaction reported as done.** A four-clause request where one
  clause was implemented well.
- **Intent drift across restarts.** Each restart re-reads the *original*
  request, never the previous attempt's restatement of it. Otherwise the goal
  degrades toward whatever the last session found convenient.
