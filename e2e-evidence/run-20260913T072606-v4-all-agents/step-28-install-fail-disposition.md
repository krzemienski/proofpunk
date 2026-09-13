# step-28 — disposition of the install FAIL

"Text-only by design" explained the probe's SHAPE, not why it FAILS. Pressed
on that. The answer changes the finding.

## The base arm is not a failure at all

    cmd_slash_install.plugin.log keys : ['harness_error', 'probe']
    harness_error : ProcessError: Command failed with exit code 1

No `pass` key, no `checks` — the session never produced a verdict. Also note
`expect_text=""`, an EMPTY string, so the text assertion is vacuous and
cannot be the failing check. This arm is UNVERIFIED (harness fault), not
FAIL (command fault). Reporting it as a command failure was wrong.

## The effect arm proves the install WORKED

    claude_md_exists     True
    markers_present      True
    within_200_lines     True     (18 lines)
    template_substituted True
    text_matches         True
    slash_registered     True
    slash_expanded       True
    session_completed    True

    write_attempted      False    <- the ONLY failing pair
    write_succeeded      False

The counterfactual is clean: claude_md_exists False, markers False,
substituted False. So the effect is real and attributable.

## Why write_attempted is False

    tools_used: ['Bash']

    probe logic:  checks["write_attempted"] = "Write" in tools

Six Bash calls. The last two `cd` into the sandbox and write the file via
shell. The file landed, correct and substituted — but through Bash, not the
Write tool, so a check that greps for the literal string "Write" in the tool
list reports False.

## Correct disposition

This is an ASSERTION-DEFINITION defect, not a missing implementation and not
prompt/model behaviour. The probe asks "was the memory file installed
correctly" but MEASURES "was the Write tool used". Those differ whenever the
agent shells out — which is a legitimate way to write a file.

The `why` text says the intent outright: "a real first-party Write/Edit
call, not an ambient MCP tool and not just narration". Bash IS first-party
and IS a real effect, not narration. It satisfies the stated intent while
failing the implemented check.

## What this does to 5/6
The advisory was right that 5/6 risked conflating causes. It does:

    base arm    UNVERIFIED (harness_error, no verdict) — not a FAIL
    effect arm  FAIL on a check that disagrees with its own stated intent

Neither is evidence that /proofpunk:install is broken. The command's
declared contract (commands/install.md: platform-correct memory file, <=200
lines) is MET on disk and confirmed by counterfactual.

## Revised next step
Ahead of the model-pinning rerun: fix write_attempted to accept a verified
on-disk effect from any first-party tool, or split it into
`first_party_write` vs `write_tool_used` so the distinction is recorded
rather than conflated. Otherwise the controlled rerun re-measures a check
that is asking the wrong question.

VERDICT: install is NOT a prompt defect, NOT a missing implementation, and
NOT expected failure. One arm is UNVERIFIED; the other fails an assertion
that contradicts its own documented intent.
