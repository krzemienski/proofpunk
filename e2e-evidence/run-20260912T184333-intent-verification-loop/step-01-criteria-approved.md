# TRUE success criteria — intent-verification loop

Source: dictated request, 2026-09-12. Two ambiguities were escalated
before any code, and the operator answered both.

## Resolved ambiguity 1 — which surfaces
The request named 'barcode and LMP'. Measured: zero occurrences of
either string anywhere in the repo (grep, case-insensitive, whole
tree). They are voice-transcription artifacts. Rather than guess, the
operator was asked and chose ALL THREE stop surfaces:
  plugins/proofpunk/hooks/stop-guard.sh          Claude Code Stop/SubagentStop
  plugins/proofpunk/extensions/proofpunk.ts      OMP session_stop
  plugins/proofpunk/opencode/plugin/proofpunk.ts OpenCode (has NO stop guard today)

## Resolved ambiguity 2 — loop bound
The request said 'keep working so it finally implements'. Taken
literally that is an unbounded self-restarting agent, which on an
unachievable goal burns the budget and surfaces as exhaustion rather
than a diagnosis. Operator chose: HARD CAP 3, then escalate with a
blocker report naming the unmet intent.

## The criteria (observable, end-user provable, measurable)

| ID | Criterion | End-user validation | Threshold |
|----|-----------|--------------------|-----------|
| C1 | implement records the session's original intent at start | run implement, inspect the artifact | intent file exists, contains the verbatim request |
| C2 | A verification pass judges intent-vs-outcome, not just evidence | drive a session whose evidence is present but intent unmet | pass returns UNMET with the specific gap named |
| C3 | The pass reads the whole session, not a tail window | feed a transcript where the intent gap is only visible early | gap is still found |
| C4 | All 3 stop surfaces block an unmet-intent stop | pipe real payloads to each | each emits block/continue with the intent reason |
| C5 | An unmet verdict writes a next-session fix prompt | trigger UNMET, inspect output | prompt file exists and names the unmet intent |
| C6 | The loop is bounded at 3 and escalates | drive 4 consecutive unmet cycles | attempts 1-3 restart; 4th escalates, never restarts |
| C7 | Sequential thinking is required in the pass | read the shipped instruction | the pass mandates it explicitly |
| C8 | No regression in the existing 7 gates | run the matrix from an archive of HEAD | 7/7 rc=0 |

## The architectural decision I own
A hook cannot judge whether intent was MET — that is a model judgment
over natural language. A regex that tried would be a guard faking
semantic understanding, which is the defect class this plugin exists
to prevent.

So the split is:
  hooks enforce the PROCEDURE — did an intent-verification pass run?
  the model performs the JUDGMENT — was the original intent met?
A stop with no recorded pass is blocked. A stop with a recorded UNMET
verdict is blocked. A stop with a recorded MET verdict is allowed.
That is checkable mechanically without any hook pretending to read.
