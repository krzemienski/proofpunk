---
name: red-team-eval
description: >
  Attack your own plans, prompts, and outputs before reality does — 4-lens
  hostile review (security, scope-creep, evidence-rigor, failure-modes)
  against plans/prompts/artifacts, formal eval-driven development (EDD)
  scoring agent sessions against rubrics, QA cycling loops (test, verify
  fix, repeat until goal met), and agent evaluation with scoring rubrics and
  benchmarks. Use when a plan or prompt needs adversarial stress beyond a
  friendly review, when you want measurable quality scores for agent output
  across runs, when a fix-verify loop must not stop at 'looks done', or when
  regression-testing prompt changes against real failure cases. Not for
  finding a bug's root cause (use root-cause-debugging) or pre-execution
  plan strengthening (use plan-hardening).
---

# Red Team + Eval

## Run checklist

Copy this checklist and track your progress:

- [ ] Select the attack mode (4-lens review / EDD / QA cycle / agent eval)
- [ ] Run every lens or rubric against the artifact; log findings with severity
- [ ] Score against the rubric; compare to threshold or baseline
- [ ] Produce validation-gated fix prompts for every finding
- [ ] Re-run after fixes until the goal is met

Friendly review finds what you expect to be wrong. This skill is for finding
what you DON'T expect: hostile lenses against your artifacts, and measured
scores instead of impressions. Findings carry severities per
`../../references/severity-model.md` and unexecuted evals are UNVERIFIED per
`../../references/end-user-actor.md`.

## Reference Routing

| Situation | Read |
|---|---|
| Adversarial review of a plan / prompt / XML artifact / run output | `references/red-team.md` (4 hostile lenses; `assets/` has trigger/eval definitions) |
| Score agent sessions formally; eval-driven development | `references/eval-harness.md` |
| Relentless test→verify→fix loop until goal is met | `references/ultraqa.md` |
| Benchmark prompt/agent quality with rubrics (external Strands SDK) | `references/agent-eval-strands.md` |

## Workflow

1. **Choose the target and the attack.** Plans and prompts get the 4-lens
   red team; implementations get QA cycling; quality regressions get evals.
2. **Red team**: each lens (security, scope-creep, evidence-rigor
   failure-modes) reviews independently — findings are merged and
   severity-tagged, and every HIGH/CRITICAL is dispositioned (fixed or
   explicitly accepted with rationale) before the artifact proceeds.
3. **Eval**: define scoring rubrics and test cases BEFORE running, execute
   against real outputs, record scores, and re-measure after changes —
   a before/after pair, never a single number from memory.
4. **QA cycle**: run → verify against the goal → fix the delta → repeat.
   The loop ends on measured goal attainment, not on iteration count.

## Anti-Patterns

- Red-teaming your own work and grading it leniently → the lenses are
  hostile by design; let them be.
- Tuning a prompt until the eval passes, without re-running on held-out
  cases → overfitting; keep failure cases held out.
- Declaring "quality improved" from two cherry-picked outputs → rubric +
  full case set + recorded scores.
- Stopping a QA cycle because "the remaining issues are minor" → minor is a
  severity verdict with evidence, not a feeling.


## Bundled resources

- `assets/evals.json` — scoring rubrics and benchmark eval definitions; load when building or running an EDD eval.
- `assets/trigger-eval.json` — trigger-routing eval cases; load when regression-testing description changes.

## Example

**Input:** User: 'Attack this launch plan.'

**Output:** 4-lens review returns 9 findings (2 security, 3 scope-creep, 4 failure-mode), each with severity and a validation-gated fix prompt; re-run after fixes shows 0 blockers.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `end-user-testing` | QA cycling loops | evidence standard for test-verify-fix iterations |

Called by: `plan-hardening`, `proofpunk`.
