# step-17 — audit: does the OMP harness overclaim?

## The question
An audit of my own harness reported it "asserts something tracker/subagent
related" while simultaneously printing UNCOVERED for that lifecycle. If true,
the harness would be claiming parity it cannot have.

## Measured, line by line
Every line in tools/test-integrations.mjs mentioning tracker or subagent:

    251 [comment]  // subagent-lifecycle gap (references/subagent-aware-stop.md §10) stays
    372 [console]  console.log("  UNCOVERED  subagent lifecycle — ...")

    assertions about tracker/subagent parity: ZERO

One comment, one UNCOVERED notice. No `check(...)` call touches either.

## Why the audit said otherwise
My audit regex stripped `//` comments before testing, but not console.log
lines — so the UNCOVERED notice itself matched, and the notice exists
precisely to DISCLAIM the thing it was flagged for.

## What the harness actually asserts (all observable, all production code)

    tool_call      block decisions and allow-decisions        7 assertions
    session_start  returns no decision, notifies the operator 2
    session_stop   holds an unevidenced claim; does not
                   re-fire on continuation; ignores a
                   no-claim turn                              3
    registration   label, 3 subscriptions, 1 command          5

It never imports intentBlockReason or any private symbol — only the default
export, invoked through an ExtensionAPI recorder, which is how the runtime
invokes it.

## Third instrument false-positive in this session
1. A scan flagged four "terminal status" phrases as overclaims — all four
   were CONTRASTS with terminal status.
2. A completeness check reported step-13 missing a blocker — the phrase
   wrapped across a newline.
3. This one: an UNCOVERED disclaimer matched a search for the thing it
   disclaims.

Each time the artifact was correct and the instrument was wrong. Each time
the cheap move — edit the artifact until the check goes green — would have
made the evidence worse. None were edited.

VERDICT: PASS — the harness asserts only supported behaviour and explicitly
disclaims the child-lifecycle gap. No overclaim.
