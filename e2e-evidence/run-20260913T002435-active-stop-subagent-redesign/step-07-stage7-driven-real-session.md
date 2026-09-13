# Step 7 - Stage 7 driven against this repo's real tracker

## What was driven
The command documented in implement/SKILL.md Stage 7, run VERBATIM, in
this session, against the real .omc tracker on disk. Not a fixture.

  python3 plugins/proofpunk/skills/end-user-testing/scripts/completion_gate.py \
      --session $SESSION_ID --cwd $PWD --out ...

## Result

  session: 8a9e4029-b77a-40a6-9e95-f23b76312761  (resolved from disk)
  GATE: ALL_COMPLETE - 0 live, 1 stale(>10m, treated finished), 1 terminal
  rc=0
  artifact: 1123 bytes written

The artifact is copied beside this step as artifact-stage7-summary.md.

## What the artifact proves
  - it resolved the REAL tracker path for this repo, not a temp fixture
  - it counted 2 agents FROM THE LIST, and says so in the artifact
  - it names the leaked 257h worker as 'stale(>10m, treated finished)'
    rather than reporting it completed
  - it refuses to quote total_* and states why in the artifact body

## The integration that now exists
implement/SKILL.md Stage 7 carries the exact invocation, not prose:
  rc=0 -> every child terminal, summary written, report may proceed
  rc=2 -> a child is live, NO summary written, report must not be produced

Both calls-table edges are registered and verify-orchestration passes:
  implement -> completion-summary
  completion-summary -> end-user-testing

## Permanent coverage (C1-C3)
Three harness cases now guard the gate itself:
  C1 live child     exit 2 AND no artifact written
  C2 all terminal   exit 0, artifact names each agent, never 'successfully'
  C3 no tracker     exit 0, artifact states it 'confirms NOTHING'

Proven load-bearing by mutation: disabling the live-child guard drives
HOOK TEST FAILS: 1 (C1 fails, rc=0 where 2 was required). Restoring
returns 0.

## Gate state
9/9 verifiers rc=0. HOOK TEST FAILS: 0.
