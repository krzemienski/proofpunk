---
name: root-cause-debugging
description: >-
  Find and fix the real cause of bugs, never the symptom — disciplined reproduce-minimize-hypothesize-instrument loops for hard bugs and performance regressions, backward call-stack tracing to the original trigger, test-pollution bisection with a find-polluter script, expert investigation protocols (evidence gathering, hypothesis testing, verification patterns), and competing-hypothesis tracing lanes. Use when a bug's cause is unclear, errors surface far from their origin, fixes keep not sticking, tests pollute each other, or you're tempted to patch a symptom or add a retry. The Iron Rule for debugging — no fix without reproduction, no claim without evidence.
---

# Root-Cause Debugging

The Iron Rule's other half: fixing the real system requires finding the real
cause. A patch applied to a symptom — a retry, a `sleep()`, a swallowed
exception, a widened timeout — is a mock of a fix and is forbidden here.

## Non-Negotiables

1. **Reproduce first.** No reproduction, no fix. If you cannot make it fail on
   demand, your job is building the reproducer, not editing the code.
2. **One hypothesis at a time, tested.** From
   `references/debug-like-expert.md`: state the hypothesis, predict what
   evidence confirms/refutes it, gather THAT evidence, then update.
3. **Trace backward from the crash to the trigger** —
   `references/root-cause-tracing.md`: the line that throws is almost never
   the line that's wrong. Follow invalid data back to its origin.
4. **Evidence over vibes.** Instrument, log, bisect. Every "I think it's X"
   gets a measurement. Cite what you SEEN, per
   `../../references/evidence-contract.md`.
5. **Verify the fix against the original reproduction**, then re-run the
   surrounding suite — a fix that breaks neighbors is a new bug, and its
   blast radius must be re-validated (see the `functional-validation` skill).

## Reference Routing

| Situation | Read |
|---|---|
| Hard bug or performance regression, no obvious cause | `references/diagnose.md` (+ `scripts/hitl-loop.template.sh`) |
| Error deep in a call chain / invalid data of unknown origin | `references/root-cause-tracing.md` (+ `scripts/find-polluter.sh` for test pollution bisection) |
| Full expert investigation protocol | `references/debug-like-expert.md` + `references/expert-*.md` (mindset, techniques, hypothesis testing, verification, when to research) |
| Competing explanations, want them raced against each other | `references/trace-competing-hypotheses.md` |

## Workflow

1. **Stabilize the repro** — deterministic input, environment, steps.
2. **Minimize** — cut the repro to the smallest case that still fails.
3. **Hypothesize + instrument** — one hypothesis, one measurement, iterate.
4. **Trace to origin** — backward through the call chain to where bad state
   was born, not where it exploded.
5. **Fix the origin**, delete any symptomatic hacks the bug had attracted.
6. **Prove it** — original repro now passes, full suite re-run, evidence
   sealed via the `evidence-gates` skill.

## Anti-Patterns

- "Fixed it" without a reproducer that flipped red→green → UNVERIFIED.
- Adding `sleep`/retry/try-except around the symptom → symptomatic hack.
- Testing three hypotheses in one edit → you learn nothing from the result.
- Fixing where the error is raised instead of where the data went bad.

## Related Skills (this plugin)

- `stack-testing` — turn the reproducer into a permanent regression test
- `functional-validation` — re-validate the blast radius after the fix
- `plan-hardening` — adversarial review before large fixes
- `evidence-gates` — fresh-evidence discipline for every claim
