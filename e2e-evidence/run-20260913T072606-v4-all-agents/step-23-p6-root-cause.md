# step-23 — P6: the flake has a cause, and raising the budget is not the fix

## The flake is not random
Three runs of the truth-audit probe alone, at the shipped budget:

    run 1  pass=False  failed=[text_matches, no_harness_error]
    run 2  pass=True   failed=[]
    run 3  pass=False  failed=[text_matches, no_harness_error]

Every failure carried the SAME harness error:

    ResultError: Reached maximum number of turns (8)

One signature, not nondeterministic behaviour. `text_matches` co-fails
because the run is cut off before the model finishes quoting the flags.

## A budget raise that was TRIED and REVERTED
_SLASH_SKILL_TOOLS sets max_turns=8 for every slash probe. Raising this one
probe to 14:

    run 1  pass=False  failed=[tool_invoked, tool_arg_matches, tool_succeeded]
    run 2  exceeded the 900s wall clock
    run 3  exceeded the 900s wall clock

Only ONE of the three produced a verdict — the other two were killed by the
timeout, so this is a single trial, not a three-run result.

It did not fix the probe. It MOVED the failure: the extra turns were spent
NOT calling the Skill tool, and longer runs then blew the wall clock. So the
turn budget was one cause and never the only one.

Reverted to 8. Eight fails fast with a legible signature; fourteen fails
slowly with a worse one; neither passes reliably. A budget large enough to
pass would be a retry wearing a different hat.

## What is now known, and what is not

    KNOWN    the failure signature is singular and reproducible
    KNOWN    max_turns=8 is a real contributing cause
    KNOWN    raising it alone makes things worse, measurably
    UNKNOWN  why the model sometimes never calls the Skill tool at all

The next step is diagnosing the skipped Skill call, not buying more turns.

## Status
P6 stays UNVERIFIED. This is progress — the flake now has a named,
reproducible cause instead of being an unexplained 1-in-3 — but a cause is
not a pass, and I will not average retries into one.

VERDICT: P6 UNVERIFIED, root cause partially isolated, budget change
reverted with its measurements recorded.
