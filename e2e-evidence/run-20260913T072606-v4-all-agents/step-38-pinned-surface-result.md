# step-38 — the pinned surface, and what it is NOT

## The run

    PP_CMDSURFACE_OUT_DIR=.../p6-surface-pinned
    surface model (all arms): cc/claude-opus-5
    550s, rc=1
    full_chain=4/6 plugin_pass=4/6 control_fail=6/6 honest_max=4/6
    HARNESS ERRORS (1): [('install','plugin')]

Per-arm provenance, read from the 15 arm artifacts:

    14 arms  model=cc/claude-opus-5  model_pin_honoured=True
     1 arm   UNPARSED (harness error, no init, no model)

## What this closes

P6's uncontrolled variable. Every arm that ran is attributable to one named
model, recorded in its own artifact. A rerun now measures behaviour rather
than behaviour-and-model at once. That was the audit's opening finding and
it is closed at the mechanism level.

## What this does NOT close

rc=1 is a RUN-level failure, not a P6 verdict. full_chain is 4/6, exactly
where the gauge already had it. Nothing was promoted. The criterion needs
6/6 and this run did not deliver it.

I want to be precise about the arithmetic: the surface was 4/6 before
pinning and is 4/6 after. Pinning did not improve the score and was never
expected to — it removes a confounder so the remaining failures can be
attributed. The two non-full-chain commands are install (harness error this
run) and truth-audit.

## The defect this run found in MY enforcement

The install plugin arm died at "Fatal error in message reader" BEFORE any
session started — no init, therefore no model, therefore no
model_pin_honoured. My check labelled that a PIN failure.

Wrong, and the wrong kind of wrong: it replaced a real pre-existing crash
(the same ProcessError shape sits in the v3 evidence) with a symptom of my
own instrumentation. An operator reading that line would have investigated
model pinning instead of the crash.

Fixed: an arm with harness_error and no model is left untouched. It already
fails correctly through its own path — classify returns FAIL ("plugin arm
recorded a harness error ... init-level fields are not execution proof"),
promotion refuses it, and it can never reach level c or d. Verified by
running classify and promote on that exact shape.

## Fixture defect, same review

My stub returned rc=0 for the crash shape. The real arm writes rc=2 (read
from cmd_slash_install.plugin.rc). A stub asserting a SOFTER contract than
production meets is a test that cannot catch the regression it exists for.
Corrected, and the hardcoded assertion total — which stayed at 15 while I
added four checks — is now derived: 20.

## Four shapes, proven by execution

    honoured          rc 0  controlled
    wrong model       rc 2  INVALIDATED, promotion blocked
    missing field     rc 2  INVALIDATED
    pre-session crash rc 2  own harness_error, never full-chain

No exceptions raised on any path.

## Status
P6 UNVERIFIED at 4/6. Controlled now, but not passing. The remaining work is
the install arm's crash and truth-audit's level — both real behaviour
questions, which is the point of removing the confounder.

VERDICT: surface controlled, score unchanged, one self-inflicted
misattribution found and fixed.
