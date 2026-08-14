---
description: Author a new high-quality prompt on the canonical XML skeleton
argument-hint: "<goal> [--out PATH] [--depth core|advanced]"
---

Activate the `prompt-forge` skill and run its AUTHOR workflow for:

$ARGUMENTS

Produce the .prompt.md file on the canonical skeleton (task, context, sequential_thinking, todos, authorization, constraints, output_contract, validation, example).

## Examples

**1. Minimal — positional goal only**

```
/proofpunk:forge-prompt "code review assistant for a Go monorepo"
```
Authors a complete .prompt.md on the canonical XML skeleton with the always-on workflow (thinking, todos, authorization, file-output).

**2. With flags — control output and depth**

```
/proofpunk:forge-prompt "incident triage runbook prompt" --out prompts/triage.prompt.md --depth advanced
```
Writes to an explicit path with the advanced tag set (edge cases, failure modes, output contract).

**3. Composed — forge, rate, iterate until it ships**

```
/proofpunk:forge-prompt "support-agent system prompt" --out prompts/support.prompt.md
/proofpunk:rate-prompt prompts/support.prompt.md --in-place
```
Forge v1, then RATE it against the 100-point rubric and remediate in place until the threshold is met.

**5. Full command — every option selected**

```
/proofpunk:forge-prompt author "migration plan for Postgres 15 → 17 across 3 services" --out .planning/pg17.prompt.md --depth advanced
```
AUTHOR mode, advanced depth (full evaluation + remediation guidance)
written to a named file — ready for `rate-prompt` and then `implement`.
