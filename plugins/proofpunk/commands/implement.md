---
description: Implement a goal end to end with the Proofpunk orchestrator
argument-hint: "<goal> [--parallel] [--auto] [--mine] [--fast]"
---

Activate the `implement` skill and run it against:

$ARGUMENTS

Follow the skill's execution loop exactly: distill TRUE success criteria (get explicit approval if they are not self-evident), decompose into tasks, execute each task to completion, and validate only through end-user testing that produces proof. Report the criteria-proof table when done.

## Examples

**1. Minimal — positional goal only**

```
/proofpunk:implement "team workspaces with invite flow"
```
Distills TRUE criteria (asks for approval if not self-evident), then runs all stages 0-7 interactively.

**2. With flags — control the execution mode**

```
/proofpunk:implement "migrate billing to Stripe" --mine --parallel --auto
```
Mines past sessions first, fans scouts/plan-stages/build-lanes out with executable lane contracts, and never stops until every criterion is proven.

**3. Composed — chained with other commands**

```
/proofpunk:forge-prompt "billing migration build" --out .prompts/billing.prompt.md
/proofpunk:implement .prompts/billing.prompt.md
```
Forge the build prompt first, review it, then implement from the approved prompt with tests-first per task.

**4. Full command — every option selected**

```
/proofpunk:implement "add Stripe billing webhooks with signature verification" --parallel --auto --mine
```
Mines past sessions first, fans out scouts, forges the prompt, decomposes
with proof obligations, runs independent lanes in parallel with executable
lane contracts, tests before code per task, and never stops until every
criterion is proven. The write path never creates test files — validation is the completed user job.
