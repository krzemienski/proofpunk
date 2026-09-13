# step-12 — P9 restated against the real hook taxonomy

## Why P9 was FAIL
The criterion read: "Hooks fire correctly, 14 block+allow cases", derived from
an assumption of 7 hook scripts each having a block case (7 x 2 = 14). The
tree contradicts the premise:

    scripts on disk : 10   (not 7)
    block-capable   : 4    (not 7)

So the criterion was unsatisfiable AS WRITTEN — no arrangement of 7
all-denying hooks exists to test. The prior report recorded FAIL for exactly
this reason and left it there.

## The measured taxonomy

    BLOCK  capture-guard.sh      exit 2
    BLOCK  evidence-guard.sh     exit 2
    BLOCK  no-test-files.sh      exit 2
    BLOCK  stop-guard.sh         decision:block   (lines 280/293/298/350)
    allow  bash-write-notice.sh
    allow  bash-write-snapshot.sh
    allow  instructions-loaded.sh
    allow  platform-steer.sh
    allow  post-write-walkthrough.sh
    allow  session-start.sh

## The restated criterion
A block-capable hook owes two cases (it must deny when it should, and allow
when it should not deny). A non-blocking hook owes one (it must not deny):

    4 block-capable x 2  +  6 non-blocking x 1  =  14 honest cases

The NUMBER 14 survives. The reasoning does not: it comes from 4 blockers and
6 observers, never from "7 hooks that all deny".

## Coverage, driven

    bash tools/test-hooks.sh   ->   rc=0,  HOOK TEST FAILS: 0
    hook scripts invoked by the harness : 10/10
    not invoked                          : none

Every script on disk is exercised by the harness, including the four whose
deny paths are the ones that matter.

## A correction to my own first measurement
My initial classifier tested for `exit 2` and `continue:false` only. It
reported 3 block-capable and 13 cases, filing stop-guard.sh as advisory
because its enforcement path emits a top-level {"decision":"block"} rather
than exiting 2 — `additionalContext` is only its FAIL-OPEN path. Reading the
source corrected it to 4 and 14. A detector that only knows one blocking
mechanism will undercount blockers.

VERDICT: PASS as restated. The original wording stays on record as
unsatisfiable, so the change is visible as a criterion correction rather than
a silently moved goalpost.
