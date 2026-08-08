---
name: cook
description: >
  Structured feature implementation with mandatory planning and verification
  gates: scout the codebase first, pin exact requirements, plan before code,
  implement following existing patterns, then PROVE the result — code review
  against acceptance criteria, full test pass, no regressions in touchpoints,
  no broken public contracts, and an end-user drive of the finished feature
  via MCP/automation tools. Modes: interactive (default, human approval at
  each gate), fast (skip research), auto (auto-approve low-risk only),
  parallel (batched execution), no-test (downgrades testing to a warning the
  user must accept), tdd (tests-first per phase). Use to implement features,
  execute plans, or build fixes once scope is known — "implement X", "build
  X", "execute this plan", "cook this feature".
---

# Cook — Structured Implementation

End-to-end implementation with gates that catch unexamined assumptions and
silent regressions. **Principles: YAGNI, KISS, DRY.**

## HARD GATES

### GATE 1 — No code before a reviewed plan

Do NOT write implementation code until a plan exists and has been reviewed.
"Simple" tasks hide the most unexamined complexity. Exception: the user
explicitly says "just code it" / "skip planning" — respect that, and note
the skipped gate in the final report.

### GATE 2 — Scout first

Before planning or asking questions, scan the codebase:

1. Project type, language(s), framework(s)
2. Existing modules relevant to the task
3. Patterns/conventions for similar features (implementation must match them)
4. Existing docs and in-flight plans covering this area
5. Public APIs, schemas, contracts the task could affect

State a 3-6 bullet context summary before proceeding. Skip only when the
input is already a plan file (the plan encodes scout output).

### GATE 3 — Exact requirements

Before producing the plan, answer in one concrete sentence each:

1. **Expected output** — concrete artifact(s): files, behaviors, screens,
   endpoint + payload, CLI + flags
2. **Acceptance criteria** — specific behaviors / inputs -> outputs / edge
   cases that MUST work
3. **Scope boundary** — explicitly OUT this round
4. **Non-negotiable constraints** — stack, locations, naming, compatibility
5. **Touchpoints** — files/modules modified; contracts that must stay stable

Ground every question in scout findings. Never proceed on vague intent.

### GATE 4 — No side effects

Implementation is NOT done until proven side-effect-free:

1. New behavior matches EVERY acceptance criterion
2. All tests pass — including modules sharing files/contracts with the change
3. No regression: walk each touchpoint and every caller of changed functions
4. No new lint/type/build errors anywhere in the repo
5. Public contracts unchanged (signatures, types, API responses, schemas,
   env vars, config keys) unless intentional and called out

If review reveals a side effect: STOP. Present what broke, the 1-line cause,
and 2-4 concrete options (revert and re-plan / update dependents / add a
compatibility shim / accept the regression with reason). The user decides —
never silently patch around regressions.

With `--no-test`, item 2 becomes a warning the user must explicitly accept;
items 1, 3, 4, 5 remain enforceable.

## Modes

| Mode | Research | Testing | Review gates | Progression |
|------|----------|---------|--------------|-------------|
| interactive (default) | yes | yes | human approval each step | one at a time |
| fast | no | yes | human approval each step | one at a time |
| auto | yes | yes | auto only for low-risk; high-risk stops | continuous low-risk |
| parallel | optional | yes | human approval each step | batched groups |
| no-test | yes | skipped (warning) | human approval each step | one at a time |
| plan-path input | no | yes | human approval each step | per plan |

`--tdd` composes with any mode: write tests for current behavior before
refactoring, verify they still pass after.

## Workflow (authoritative)

```
Intent detection -> [plan path? load it] -> Scout -> Summarize
  -> [exact requirements? no -> loop] -> Research -> Plan
  -> REVIEW GATE -> Implement -> [simplify signal? simplify]
  -> REVIEW GATE -> Test -> REVIEW GATE -> Finalize -> Report
```

Blocking gates in non-auto modes: post-research, post-plan,
post-implementation, post-testing (100% pass + approval before finalize).

Always enforced (all modes):

- **Testing**: 100% pass unless no-test mode
- **Code review**: check (a) every acceptance criterion met, (b) no
  regression in touchpoints/blast radius, (c) no breaking contract changes
  unless called out, (d) follows scout-found patterns, (e) no new
  lint/type/build errors
- **End-user verification**: per `../../references/end-user-actor.md`, drive
  the finished feature as an end user via MCP/automation tools — click,
  submit, navigate — capturing fresh evidence per
  `../../references/evidence-contract.md`. "The code looks right" and "tests
  pass" are not proof the feature works for a user. This step is never
  skipped, faked, or marked done without actual execution — if no tool path
  exists, the finalize report says UNVERIFIED with the reason.
- **Finalize**: update plan status across ALL phase files, update docs if
  warranted, offer to commit, write the report — citing the driven end-user
  evidence (tools used, actions performed, evidence paths) for every
  acceptance criterion

## Step Output Format

```
✓ Step [N]: [brief status] — [key metrics]
```

## Anti-Rationalization

| Thought | Reality |
|---------|---------|
| "Too simple to plan" | Simple tasks hide complexity. Plan takes 30 seconds |
| "I already know how" | Knowing != planning. Write it down |
| "Let me just start coding" | Undisciplined action wastes tokens |
| "The user wants speed" | Fastest path = plan -> implement -> done |
| "I'll plan as I go" | That's hoping, not planning |
| Marking validation complete without the AI actually invoking MCP/automation tools and acting as the end user | Execute the tools yourself; unexecuted = UNVERIFIED |
| Skipping or faking QA/verification steps under any circumstance | Run them or report them UNVERIFIED — no exceptions |
## Related Skills

- `brainstorm` — decide the approach before cooking
- `validation-plan` — authors the plans this skill executes
- `functional-validation` — the end-user verification protocol for Gate 4
- `evidence-gates` — evidence standard for the final verification
