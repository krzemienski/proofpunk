# Step 3 - A runtime tracker already exists, and it lies

## Correction to my step-2 conclusion
In step 2 I concluded the mechanism should be transcript spawn/result
pairing. A scout found something better and I verified it directly:
the runtime ALREADY maintains a subagent tracker.

  .omc/state/sessions/<session-id>/subagent-tracking-state.json

Measured shape (3 real files on disk):
  keys: agents, total_spawned, total_completed, total_failed, last_updated
  agents[] entries carry: status, agent_type, completed_at
  status values seen: 'running', 'completed'

So the query the redesign needs is literally:
  count(a for a in agents if a.status == 'running')

That is strictly better than my transcript-pairing plan: no full-file
scan, no 3547-record parse inside a 10s hook timeout.

## The hazard that would have shipped a wedged session
I checked whether those 'running' agents are actually alive.

  running agent age: 257.5 h   type=worker
  running agent age: 257.5 h   type=worker
  running agent age: 266.2 h   type=worker

  running agents: 3    older than 1 hour: 3

All three are leaked. No process has been alive for 11 days.

Worse, the counters do not reconcile with the list:
  session bf6d2762: agents=3  total_spawned=4  total_completed=19

total_completed (19) exceeds total_spawned (4) by 15. The counters
cannot be used as the source of truth either.

## Consequence for the design (this is the important part)
The naive implementation of the user's request --
  'do not stop while any subagent is running'
-- would read status=='running', find 3 leaked entries, and block the
stop FOREVER. Every session in this repo would wedge immediately.

Any correct design MUST:
  1. bound staleness: an entry older than a cutoff counts as finished;
  2. not trust total_* counters (measured incoherent);
  3. fail OPEN on a missing/unparsable tracker -- a stop guard that
     cannot read state must never trap the session.

## Observability verdict (final)
OBSERVABILITY: PROVEN-AVAILABLE via .omc subagent-tracking-state.json
  (status field), with transcript spawn/result pairing as a fallback.
The shipped stop-guard reads neither: 0 references to the tracker,
and a 40-line transcript window that missed 13/13 spawns.
