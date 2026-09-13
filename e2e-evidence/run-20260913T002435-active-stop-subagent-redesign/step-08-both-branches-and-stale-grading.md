# Step 8 - Both gate branches driven; stale semantics graded

## Branch 1: the documented default path
Earlier I drove the gate to /tmp, not to the path Stage 7 documents.
Re-driven at the documented location:

  --out .planning/run-completion-summary.md
  GATE: ALL_COMPLETE - 0 live, 1 stale(>10m, treated finished), 1 terminal
  rc=0, 1123 bytes written at the documented path

## Branch 2: a LIVE child (the branch that had never been driven)

  GATE: live children remain (1): worker (LIVE)
  No summary written. Wait for them, or state why their output is not needed.
  rc=2
  artifact exists: False

The ABSENCE is the load-bearing property. A summary naming a running
agent as finished would be false, so the gate writes nothing at all.

## Stale semantics: graded, not assumed
A session whose only non-terminal entry is a leaked 257h worker reports
ALL_COMPLETE. I escalated whether that overstates certainty, since it is
the same shape as the unknown-age problem I had already fixed.

Operator decision: KEEP ALL_COMPLETE.

The distinction is epistemic, and it is the reason DEGRADED exists:

  stale    aged out by a DOCUMENTED RULE (>10m). A decision we made,
           with a fixed threshold, and the artifact names every aged-out
           entry explicitly so the detail is never hidden.
  DEGRADED something we COULD NOT MEASURE - missing or unparsable
           timestamp, or an unreadable record.

Merging them would have made nearly every real session in this repo read
DEGRADED, dulling the signal that flags genuinely broken records.

## Criterion status
  AC1 live child blocks the stop            PASS (step-05, step-08)
  AC2 all-completed allows                  PASS (step-05)
  AC3 leaked 257h does not wedge            PASS (step-04, step-05, step-08)
  AC4 SubagentStop not graded as main       PASS (step-05, mutation-proven)
  AC5 completion skill + summary artifact   PASS (step-06, step-07, step-08)
  AC6 no regression, counts in sync         PASS (9/9 gates, 0 harness fails)
  AC7 fail-open on unreadable tracker       PASS (step-04, 6 degenerate arms)
