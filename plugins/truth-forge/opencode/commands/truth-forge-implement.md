---
description: Implement a goal end to end with the truth-forge orchestrator
argument-hint: "<goal> [--parallel] [--auto] [--mine] [--fast] [--no-test] [--tdd]"
---

Activate the `implement` skill and run it against:

$ARGUMENTS

Follow the skill's execution loop exactly: distill TRUE success criteria (get explicit approval if they are not self-evident), decompose into tasks, execute each task to completion, and validate only through end-user testing that produces proof. Report the criteria-proof table when done.
