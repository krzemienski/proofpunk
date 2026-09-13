# step-26 — prompt-audit: P6 has an uncontrolled variable

Audited tools/sdk_probe.py against the claude_agent_sdk contract
(python/agent-sdk/README.md, ClaudeAgentOptions table).

## What the probe pins

    allowed_tools        pinned
    disallowed_tools     pinned
    max_turns            pinned (8)
    cwd                  fresh temp sandbox per arm
    plugins              pinned to the local checkout
    permission_mode      pinned
    setting_sources      pinned
    strict_mcp_config    set on effect probes only

## What it does NOT pin

    model                NEVER PASSED

`ClaudeAgentOptions.model` documents its default as "determined by the
CLI". Measured:

    "model" appears in sdk_probe.py as a parameter          : False
    "model" in verify-command-surface.py                    : prose only,
                                                              never a param
    model ID recorded anywhere in the run artifact           : NO

So every P6 arm runs on whatever model the CLI selects at that moment, and
the evidence cannot say which one. A probe measured at 1-in-3 has an
uncontrolled variable sitting directly upstream of the behaviour it tests.

## This is a CONFOUNDER, not a prompt defect
The prompts themselves look sound: each names its slash command, its flags,
and the marker text the check greps for. I am NOT claiming the wording is
the cause. I am claiming the experiment cannot currently distinguish
"wording is wrong" from "a different model answered", because the model is
free to vary and is never recorded.

That ordering matters. Two hypotheses were already falsified by changing a
knob and measuring the result:

    max_turns 8 -> 14          regressed
    strict_mcp_config = True   regressed

Changing prompt wording next, while the model still floats, would produce a
third uninterpretable result.

## The correct next step, not taken here
1. Determine which model the CLI actually selects, and how to override it.
2. Pin `model` in ClaudeAgentOptions and RECORD the id in the artifact.
3. Re-run all 15 arms under one pinned model.
4. Only then attribute any residual variance to prompt wording.

Step 2 is a harness change with real blast radius (it fixes what every arm
runs against), and steps 1-3 cost a full surface run each. Recorded rather
than started, so the next session begins from the finding instead of
rediscovering it.

## Status
P6 stays UNVERIFIED at 5/6. Third hypothesis identified and NOT yet tested;
unlike the first two, this one is about the measurement apparatus rather
than the thing measured.

VERDICT: P6 UNVERIFIED — model is an uncontrolled, unrecorded variable in
every arm.
