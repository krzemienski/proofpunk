# step-24 — P6: second diagnosis, second measured regression

## A narrative I had to withdraw
step-23 said the open question was "why the model skips the Skill call".
Reading the actual failing transcript refutes that for the failures seen at
the shipped budget:

    tool_invoked      True
    tool_arg_matches  True
    tool_succeeded    True
    text_matches      FALSE   <- the only failure

The Skill call SUCCEEDS. The generalisation came from the max_turns=14 run,
which is a different configuration and a different failure.

## The real turn sink
Tool calls in a failing run: Monitor x2, Skill, Glob, and THREE
mcp__filesystem__* calls (list_directory, list_allowed_directories,
get_file_info) probing an empty sandbox.

3 of 7 calls are ambient MCP. Each costs one of 8 turns and none advances
the assertion, so the run is cut off before the model quotes `--start`.

`allowed_tools` governs FIRST-PARTY tools only; MCP tools are auto-approved
regardless. The effect probes already set `strict_mcp_config=True` for
exactly this reason.

## The fix, measured, and reverted
Adding `strict_mcp_config=True` to _SLASH_SKILL_TOOLS:

    run 1  pass=False  failed=[tool_invoked, tool_arg_matches, tool_succeeded]
    run 2  wall-clock timeout
    run 3  wall-clock timeout

The completed run REGRESSED — from "Skill called, text cut off" to "Skill
never called at all". Removing the ambient tools appears to change what the
model does first, not merely how many turns it has.

## Two attempts, two regressions

    max_turns 8 -> 14          one completed trial, regressed, 2 timeouts
    strict_mcp_config = True   one completed trial, regressed, 2 timeouts

Identical shape. Both diagnoses were evidence-backed and both fixes made the
signal worse. Reverted; only comments remain in sdk_probe.py, and the effect
probes' own strict_mcp_config is untouched.

## Status
P6 stays UNVERIFIED. What is established: the flake is not a turn budget
problem and not an ambient-MCP problem — the two obvious mechanical
explanations are both falsified by measurement. What it is remains unknown.

Recording two failures is worth more than a third guess. A change that
degrades the signal it is meant to improve does not ship because the
diagnosis behind it sounded right.

VERDICT: P6 UNVERIFIED. Two hypotheses falsified, no regression shipped.
