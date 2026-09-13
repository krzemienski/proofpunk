# Step 4 - The state helper, driven against 16 real tracker files

## What was driven
agent_state.py run as a SUBPROCESS against genuine tracker JSON written
into isolated temp cwds. No imports, no monkeypatching, no mocks.

## Result: 16/16 arms, MATRIX FAILS: 0

  BLOCK arms (a live child must hold the session):
    live child under cutoff        rc=0  LIVE 1: scout
    nested grandchild live         rc=0  LIVE 1: grandchild
    one live among stale           rc=0  LIVE 1: real

  ALLOW arms (nothing live -> never wedge):
    all completed                  rc=2  1 terminal
    stale running 257h             rc=2  1 stale(>10m, treated finished)
    failed child (terminal)        rc=2  1 terminal
    fresh session, empty agents    rc=2  0 live
    incoherent counters 19 vs 4    rc=2  computed from list, not counters
    running, NO started_at         rc=2  1 UNKNOWN-age(allowed, NOT proven finished)
    unparsable started_at          rc=2  1 UNKNOWN-age(allowed, NOT proven finished)
    malformed JSON                 rc=2  tracker unreadable; failing open
    agents not a list              rc=2  no agents list; failing open
    non-object entry               rc=2  1 unparsable
    unknown status                 rc=2  1 unparsable
    no tracker file at all         rc=2  no recorded children
    empty session id               rc=2  cannot resolve a tracker

## Correction made mid-build, on operator instruction
My first implementation folded unknown-age entries into 'stale' and
printed 'treated finished'. That states something untrue: a missing
started_at is not evidence of completion.

UNKNOWN is now a fourth bucket. It still does not block -- an entry
with no timestamp can never age out, so blocking on it would wedge the
session permanently with no recovery -- but it is reported as
'UNKNOWN-age(allowed, NOT proven finished)' and the summary prints an
explicit warning naming each broken record.

The two unknown arms now show that exact string, verified above.

## Scope correction (measured, not assumed)
I checked which runtimes actually WRITE the tracker:
  claude/omc   4 tracker artifacts (writer + live state)
  omp          0
  opencode     0

So this is an OMC/Claude-runtime integration. On OMP and OpenCode the
tracker is absent, the helper returns 'no tracker file', and those
surfaces keep their current stop behaviour. Stated as a limitation in
references/subagent-aware-stop.md section 5 -- it is not parity, and
reading that path there would be convention rather than evidence.
