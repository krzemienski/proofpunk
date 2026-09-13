# step-25 — P6 full surface at the reverted configuration

Run launched at HEAD 9f58336, with both failed experiments reverted. The
only uncommitted change at launch was a comment, so the effective probe
config is identical to that SHA.

## All 15 arms ran — verified from the artifact, not the console tail

    implement      reached=c        arms=2
    forge-prompt   reached=c        arms=2
    rate-prompt    reached=c        arms=2
    truth-audit    reached=c        arms=2
    verify         reached=d        arms=3
    install        reached=FAIL     arms=4

    total arms executed: 15
    full_chain=5/6  plugin_pass=5/6  control_fail=6/6  honest_max=5/6
    harness_errors: 1  — install / plugin arm, rc=2

The console tail showed only the final counterfactual line, which reads like
an early abort. The artifact refutes that: six commands, fifteen arms, every
one recorded. Checked instead of assumed.

## What changed since the earlier 4/6

    earlier (my portability preamble)   full_chain=4/6  plugin_pass=4/6
    now (reverted)                      full_chain=5/6  plugin_pass=5/6

truth-audit reached level `c` in this run — the probe that was 1-in-3 flaky
passed here. That is consistent with a flake, not a fix: one passing run
proves no more than one failing run did.

## The remaining gap
`install` is the sole FAIL, on a harness error in its plugin arm (rc=2), not
on a behavioural check. Its log is
`evidence/v3-release/l16-commands/cmd_slash_install.plugin.log`.

## Status
P6 stays UNVERIFIED at 5/6. Two mechanical hypotheses are falsified
(step-23, step-24), the surface runs end-to-end, and one command fails on a
harness error that has not yet been diagnosed.

VERDICT: P6 UNVERIFIED — 5/6, all arms executed, install harness error open.
