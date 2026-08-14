---
description: Author a new high-quality prompt on the canonical XML skeleton
argument-hint: "<goal> [--out PATH] [--depth core|advanced]"
---

Activate the `prompt-forge` skill and run its AUTHOR workflow for:

$ARGUMENTS

Produce the .prompt.md file on the canonical skeleton (task, context, sequential_thinking, todos, authorization, constraints, output_contract, validation, example).

**5. Full command — every option selected**

```
/proofpunk-forge-prompt author "migration plan for Postgres 15 → 17 across 3 services" --out .planning/pg17.prompt.md --depth advanced
```
AUTHOR mode, advanced depth (full evaluation + remediation guidance),
written to a named file — ready for `rate-prompt` and then `cook`.
