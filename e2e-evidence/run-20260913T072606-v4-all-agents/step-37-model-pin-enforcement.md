# step-37 — a warning is not a gate, again

## What I shipped first

Threaded one model through all 15 arms, then added a per-arm check that
PRINTED when the pin was not honoured. Committed it as "per-arm assertion".

It asserted nothing. The print changed no rc, no parsed verdict, no count.
An arm that ignored the pin still reached promotion and still counted toward
the full-chain total. The run would have LOOKED controlled while one arm
floated — strictly worse than not pinning, because the artifact would now
carry a false claim of control.

This is the second time this session I mistook a recorded observation for an
enforced one. Step-33 was the first (a comment documenting a gap the gate
could still walk through).

## Fail-closed now

    model_pin_honoured False   -> SDK resolved a different model
    model_pin_honoured missing -> arm never reported; control UNPROVEN

Both INVALIDATE the arm: parsed=None, rc=2, reason appended to the arm's own
log so the artifact carries it and not just stdout. Downstream a None json
is an unusable arm — promotion refuses it ("effect probe produced no
parseable result") and it can never reach level c or d, so it drops out of
full-chain counts.

Rejecting `None` is the important half. Absence of a reading is not a
passing reading — the same error class as the truncation reading, the 0/6
replay, and "no model in the artifact". Third and fourth occurrences were
this session; this is the fifth place it could have bitten.

## Proven by execution, not inspection

tools/test-model-pin.py stubs the probe and runs real arms:

    honoured    -> arm usable, rc 0
    wrong model -> INVALIDATED, rc 2, promotion blocked
    unreported  -> INVALIDATED
    no pin      -> enforcement does not fire; arm still attributable via
                   its recorded `model` field

Plus structural guards: `model` must be REQUIRED (not defaulted) on both
run_probe and run_arm_with_retry, because a default lets a missed call site
silently unpin; all four call sites must pass it; DEFAULT_SURFACE_MODEL must
name an explicit model. 15 assertions.

## Why required-positional matters

I made `model` positional deliberately. With a keyword default, forgetting
one of the four call sites produces a silently unpinned arm. Required means
TypeError at the first call — loud, immediate, unmissable.

## Status
The pinned 15-arm surface is running now. P6's uncontrolled variable is
closed at the mechanism level; whether the criterion passes is a separate
question that run will answer.

VERDICT: enforcement fails closed and is regression-tested. P6 still
UNVERIFIED pending the surface result.
