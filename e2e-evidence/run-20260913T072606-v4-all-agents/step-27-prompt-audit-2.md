# step-27 — prompt-audit round 2: contracts, settings, provenance

Three follow-up questions, each answered by measurement.

## 1. Does every probe demand an OBSERVABLE action?

    cmd_slash_implement     require_tool + require_tool_arg + expect_text   OBSERVABLE
    cmd_slash_forge_prompt  require_tool + require_tool_arg + expect_text   OBSERVABLE
    cmd_slash_rate_prompt   require_tool + require_tool_arg + expect_text   OBSERVABLE
    cmd_slash_truth_audit   require_tool + require_tool_arg + expect_text
                            + forbid_text                                   OBSERVABLE
    cmd_slash_verify        expect_text only                                TEXT-ONLY
    cmd_slash_install       expect_text only                                TEXT-ONLY

Four of six require a real Skill call with matching arguments. Two are
text-only — and those two are exactly the commands with NO backing skill
(both documented `playbook-recognition`, honest max `d`). Their EFFECT arms
carry the observable half: `effect_kind` asserts CLAUDE.md exists on disk
with markers, under the line cap, placeholders substituted, plus a
counterfactual.

So the text-only base arms are not a gap — the observable contract lives in
the effect arm. Worth stating because a reader auditing only the base arm
would reasonably flag it.

## 2. Could ambient settings be rewriting the instructions?

    setting_sources   NOT SET   -> default is none; no CLAUDE.md loads
    system_prompt     absent everywhere in sdk_probe.py

No. The probe cannot be inheriting instructions from project or user config.
That hypothesis is closed.

## 3. Does the SDK expose the resolved model anywhere?

    init entries captured  : 1
    init keys              : kind, local_plugin, slash_proofpunk
    model strings in the ENTIRE raw log : NONE

The probe records a FILTERED init — three fields it chose to keep. Whatever
the SDK emitted about the model, if anything, was discarded at capture time.

This matters for the fix: pinning `model` is one change, but RECORDING it is
a separate and independently valuable one. Machine-readable provenance in
the artifact, not assistant narration — verify-command-surface.py:27 already
rules that "never the model's narration of having done so" is the standard,
and that rule applies to provenance too.

## Revised next step
Previously: "pin model, re-run, then blame wording."
Now: pin model AND widen the recorded init to include the resolved model id.
Without the second half, a pinned run still cannot prove what it ran on.

## Status
P6 UNVERIFIED at 5/6. Three hypotheses now closed by measurement rather than
argument: turn budget (regressed when changed), ambient MCP (regressed when
changed), ambient settings (not loaded at all). The open one — unrecorded,
unpinned model — is a property of the apparatus.

VERDICT: prompt wording is NOT implicated. The contracts are sound, the
settings surface is clean, and the measurement lacks provenance.
