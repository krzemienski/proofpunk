---
description: Execute an existing plan or goal under cook execution discipline
argument-hint: "<goal-or-plan-path> [--fast] [--no-test] [--tdd]"
---

Activate the `cook` skill and run it against:

$ARGUMENTS

Work the task list in order; every task ends in executed end-user proof, never asserted status.

**4. Full command — every option selected**

```
/proofpunk-cook .planning/ROADMAP.md --fast --tdd
```
Plan file, skip the research sub-step, tests written before each task's code.
Note: `--no-test` contradicts `--tdd` (one downgrades the rail, the other
strengthens it) — pick one; `--fast` composes with either.
