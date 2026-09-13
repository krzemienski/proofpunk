# step-04 — P5 PASS, P9 restated, P6 measured FLAKY (not closed)

## P5 — router head links every non-head skill: PASS (re-driven, not inherited)

    python3 tools/verify-router-links.py   -> EXIT 0
    VERDICT: PASS
    skills_globbed=19  non_head_expected=18  routed=18 unique=18
    doctrine_refs=14 all_resolved=true

The criterion's own wording ("all 17 other skills") was stale: the router
links 18 non-head skills, because completion-summary landed in the previous
run. The measurement corrects the criterion, not the reverse.

## P9 — restated against the real hook taxonomy

The criterion assumed "7 hooks x (block + allow) = 14 cases". Measured from
plugins/proofpunk/hooks/*.sh:

    BLOCK   capture-guard.sh      exit 2
    BLOCK   evidence-guard.sh     exit 2
    BLOCK   no-test-files.sh      exit 2
    BLOCK   stop-guard.sh         decision:block  (lines 280/293/298/350)
    ADVISE  bash-write-notice.sh, platform-steer.sh,
            post-write-walkthrough.sh, session-start.sh   additionalContext
    OBSERVE bash-write-snapshot.sh, instructions-loaded.sh  no decision

    scripts=10  block-capable=4  non-blocking=6
    honest cases = 4x2 + 6 = 14

My FIRST classifier reported 3 block-capable and 13 cases: it tested for
`exit 2` and `continue:false` only, so it missed stop-guard.sh's top-level
{"decision":"block"} and misfiled it as ADVISE. Corrected by reading the
source. The honest total lands on 14 — the same number the criterion asserted,
but reached from the real taxonomy (4 blockers, not 7) instead of a wrong
premise.

## P6 — verify-command-surface.py: COMPLETES, but FLAKY. NOT closed.

It had never run to completion before. It now does, in ~5-8 minutes across
15 real sandboxed arms.

    run A: full_chain=5/6 plugin_pass=6/6 control_fail=6/6 honest_max=5/6
    run B: full_chain=4/6 plugin_pass=4/6 control_fail=6/6 honest_max=4/6

Two distinct causes, separated by measurement:

1. MY REGRESSION (reverted). I appended a shell-portability preamble to the
   install effect prompt to stop the model improvising `timeout 180 claude -p`
   (GNU timeout does not exist on this host: absent from zsh -lc, zsh -c, and
   as gtimeout; the step died exit=127 and burned every remaining turn).
   The preamble made it WORSE — write_attempted flipped to false and
   plugin_pass fell 6/6 -> 4/6. Prefixing prohibitions onto a slash command
   changed what the model did with the command itself, so the arm stopped
   testing the command doc. Reverted; the prompt is byte-identical to HEAD
   (git diff shows no prompt line changed).

2. GENUINE NONDETERMINISM, independent of my edit. truth-audit's PLUGIN arm
   failed on text_matches, which an install-only prompt change cannot touch.
   Re-running that single probe three times:

       run 1: pass=False  failed=['text_matches','no_harness_error']
       run 2: pass=True   failed=[]
       run 3: pass=False  failed=['no_harness_error']

       1/3 -> FLAKY

## What I SEE
P6 exercises live model sessions, so its verdict varies run to run. A
criterion whose outcome changes without any source change is not proven by a
single green run. I am NOT recording P6 as PASS, and NOT weakening the
verifier's harness-error gate to manufacture one — that gate correctly refuses
to score an exit=127 as success.

VERDICT: P5 PASS. P9 restated (14 honest cases from 4 block-capable hooks).
P6 UNVERIFIED — completes, but measured 1/3 flaky on truth-audit alone.
