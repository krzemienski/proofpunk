# step-34 — a live arm, and the promotion I had to take back

Ran cmd_slash_install_effect against a real sandbox. 131s, 77KB artifact,
preserved at live-install-arm/cmd_slash_install_effect.live.json.

## What it proved

    write_attempted          True    <- the audit's original defect, fixed
    write_succeeded          True
    verification_block_run   True    <- 2 matching calls
    claude_md_exists         True
    markers_present          True
    within_200_lines         True
    template_substituted     True
    text_matches             True
    slash_registered         True
    slash_expanded           True
    local_plugin_loaded      True
    session_completed        True
    no_harness_error         FALSE

Three things established that replay could not:

1. The contract-aligned write check works on live data. The old
   "Write in tools" predicate reported False for this same behaviour.
   tools_used=['Bash'], write_tool_used=False, write_mechanism=['Bash'].

2. install.md's fourth criterion is OBSERVABLE. verification_block_run
   fired twice. Replay reported 0/6 purely because truncation severs the
   command before its grep.

3. Every tool input exceeded the 200-char cap — 206, 232, 206, 271, 686,
   524, 237 — all flagged input_truncated=True. The truncation defect is
   confirmed by measurement and is now visible in the artifact instead of
   silently looking like absence.

## The promotion I took back

Seeing verification_block_run=True, I added it to INSTALL_EFFECT_CHECKS.
Then re-read the result:

    result.is_error = True
    'Reached maximum number of turns (12)'
    no_harness_error = False

An errored session cannot certify a gate. Every check in it is a reading
taken from a run that did not complete, and promote_to_effect_proven
already refuses to promote on harness error — I would have been gating on
exactly the class of evidence that function exists to reject.

Reverted. Gate stays at 6. The reasoning now sits in source beside the
tuple with the evidence path, so the next session starts from the finding
rather than re-deriving it.

This is the sixth time this session the mechanism was right and my claim
about it was premature. The difference here is that the check itself is
sound — only the evidence backing its promotion was not.

## Model provenance
No model id anywhere in the 77KB artifact. Confirmed on live data, not
inferred from the older evidence. Still P6's gating problem.

## P6 status
The failure signature is unchanged in KIND (turn exhaustion) but the
content is different: at max_turns=12 every substantive check passed and
only the budget failed. That is a materially better failure than the
recorded 8-turn runs, where tool_invoked itself failed. Recorded, not
acted on — raising the budget was TRIED and REVERTED earlier this session
for regressing other arms, and one arm is not the surface.

VERDICT: three findings proven live; promotion correctly withheld; P6
remains UNVERIFIED at 4/6.
