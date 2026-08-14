---
description: Execute an existing plan or goal under cook execution discipline
argument-hint: "<goal-or-plan-path> [--fast] [--no-test] [--tdd]"
---

Activate the `cook` skill and run it against:

$ARGUMENTS

Work the task list in order; every task ends in executed end-user proof, never asserted status.

## Examples

**1. Minimal — positional goal only**

```
/proofpunk:cook "add an export button to the reports page"
```
Scouts, decomposes into proof-carrying tasks, executes each to end-user proof with a human checkpoint at every step.

**2. With flags — pick the mode**

```
/proofpunk:cook .planning/ROADMAP.md --tdd
```
Executes an existing plan file (scout output is encoded in the plan) with tests written before each task's implementation.

**3. Composed — plan upstream, cook downstream**

```
/proofpunk:forge-prompt "notification service plan" --out .planning/notifications.prompt.md
/proofpunk:cook .planning/notifications.prompt.md --fast
```
Plan/prompt first, then cook the approved artifact; `--fast` skips research because the plan already carries it.

**4. Full command — every option selected**

```
/proofpunk:cook .planning/ROADMAP.md --fast --tdd
```
Plan file, skip the research sub-step, tests written before each task's code.
Note: `--no-test` contradicts `--tdd` (one downgrades the rail, the other
strengthens it) — pick one; `--fast` composes with either.
