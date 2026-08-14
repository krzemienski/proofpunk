---
description: Rate a prompt file against the 100-point rubric and apply remediations to file
argument-hint: "<prompt-file.md> [--in-place] [--report-only] [--out PATH]"
---

Activate the `prompt-forge` skill and run its RATE workflow on:

$ARGUMENTS

Write NAME.rating.md plus the remediated prompt file per the skill's file-output contract. Unexecuted suggestions are UNVERIFIED — remediate, do not merely advise.

**5. Full command — every option selected**

```
/proofpunk-rate-prompt .planning/pg17.prompt.md --report-only --out .planning/pg17.rating.md
```
Scores against the 7-dimension /100 rubric and writes the report to file
without touching the prompt. Note: `--in-place` and `--out` are exclusive
(same-file edit vs. separate output); `--report-only` composes with `--out`.
