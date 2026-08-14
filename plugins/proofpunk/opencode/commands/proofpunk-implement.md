---
description: Implement a goal end to end with the Proofpunk orchestrator
argument-hint: "<goal> [--parallel] [--auto] [--mine] [--fast]"
---

Activate the `implement` skill and run it against:

$ARGUMENTS

Follow the skill's execution loop exactly: distill TRUE success criteria (get explicit approval if they are not self-evident), decompose into tasks, execute each task to completion, and validate only through end-user testing that produces proof. Report the criteria-proof table when done.

**4. Full command — every option selected**

```
/proofpunk-implement "add Stripe billing webhooks with signature verification" --parallel --auto --mine
```
Mines past sessions first, fans out scouts, forges the prompt, decomposes
with proof obligations, runs independent lanes in parallel with executable
lane contracts, tests before code per task, and never stops until every
criterion is proven. The write path never creates test files.
