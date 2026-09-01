---
description: Rate a prompt file against the 100-point rubric and apply remediations to file
argument-hint: "<prompt-file.md> [--in-place] [--report-only] [--ship-below-threshold] [--out PATH]"
---

Activate the `prompt-forge` skill and run its RATE workflow on:

$ARGUMENTS

Write NAME.rating.md plus the remediated prompt file per the skill's file-output contract. Unexecuted suggestions are UNVERIFIED — remediate, do not merely advise.

**Example — redirected output, remediate and ship regardless of score**

```
/proofpunk-rate-prompt .planning/pg17.prompt.md --out .planning/pg17.remediated.md --ship-below-threshold
```
Scores against the 7-dimension /100 rubric, remediates, and writes the
remediated file to the given path. Note: `--in-place` and `--out` are
exclusive (same-file edit vs. separate output); `--report-only` and `--out`
are also exclusive (scorecard-only vs. writing a redirected deliverable) —
they conflict and fail fast if combined.
`--ship-below-threshold` finalizes even if the result grades needs-work/rewrite; omit it to require a passing score before shipping.
