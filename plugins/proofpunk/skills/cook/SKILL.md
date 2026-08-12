---
name: cook
description: >
  Structured feature implementation as an execution loop: scouts the
  codebase, pins exact requirements, decomposes into tasks each carrying a
  proof obligation, implements following existing patterns, and completes
  every task by proving it — end-user testing of the real feature,
  acceptance criteria asserted, touchpoints walked for regressions, no
  broken public contracts. Modes: interactive (default, human checkpoint at
  each step), fast, auto, parallel, no-test, tdd. Use when implementing a
  feature, executing an approved plan, or building a fix once scope is known
  — 'implement X', 'build X', 'execute this plan', 'cook this feature'. Not
  for open-ended ideation (use brainstorm), full orchestration with session
  mining and prompt forging (use implement), or writing plans (use
  validation-plan).
---

# Cook — Structured Implementation

## Run checklist

Copy this checklist and track your progress:

- [ ] Scout the codebase and pin exact requirements
- [ ] Decompose into tasks, each with a written proof obligation
- [ ] Implement one task following existing patterns
- [ ] Prove the task via its end-user test (not proven = not done; stuck protocol otherwise)
- [ ] Finalize: walk touchpoints for regressions, check public contracts
- [ ] Report from the execution ledger

End-to-end implementation as an execution loop: tasks, not gates.
**Principles: YAGNI, KISS, DRY.**

## THE EXECUTION CONTRACT

### Contract 1 — Tasks, not phases

Decompose the work into a task list before writing code. "Simple" tasks
hide the most unexamined complexity; the list is what exposes it. If the
user explicitly says "just code it" / "skip planning" — respect that: the
plan is a single task, and the final report notes the skipped
decomposition.

### Contract 2 — Scout first (readiness)

Before creating tasks or asking questions, scan the codebase:

1. Project type, language(s), framework(s)
2. Existing modules relevant to the task
3. Patterns/conventions for similar features (implementation must match them)
4. Existing docs and in-flight plans covering this area
5. Public APIs, schemas, contracts the task could affect

State a 3-6 bullet context summary before proceeding. Skip only when the
input is already a plan file (the plan encodes scout output).

The full scout-first rule — when to scout, what to extract, and its
anti-rationalization — is owned by `brainstorm` (GATE 2). This contract
applies it; it does not redefine it.

### Contract 3 — Every task gets a proof obligation

Before a task starts, write down:

1. **Expected output** — concrete artifact(s): files, behaviors, screens,
   endpoint + payload, CLI + flags
2. **Acceptance criteria** — specific behaviors / inputs -> outputs / edge
   cases that MUST work
3. **The end-user test** — how the finished task will be driven as the end
   user, and the assertion that proves it
4. **Scope boundary** — explicitly OUT this round
5. **Touchpoints** — files/modules modified; contracts that must stay stable

A task whose proof obligation cannot be written is not ready — shrink it
or escalate. Never proceed on vague intent.

The plan-level proof-obligation XML format (`<proof_obligation id="PO-N">`)
is owned by `validation-plan`; how the proof is executed and evidenced is
owned by `end-user-testing`. Cook consumes both — it does not redefine them.

### Contract 4 — Done means proven, with no side effects

A task completes only when:

1. Its end-user test drove the real feature and the assertion passed —
   fresh evidence captured per `../../references/evidence-contract.md`,
   per the actor protocol in `../../references/end-user-actor.md`
2. The regression rail passes — including modules sharing files/contracts
   with the change (with `--no-test`, this becomes a warning the user
   must explicitly accept; the end-user test is never downgraded)
3. No regression: walk each touchpoint and every caller of changed functions
4. No new lint/type/build errors anywhere in the repo
5. Public contracts unchanged (signatures, types, API responses, schemas,
   env vars, config keys) unless intentional and called out

If proof reveals a side effect: present what broke, the 1-line cause, and
2-4 concrete options (revert and re-plan / update dependents / add a
compatibility shim / accept the regression with reason). The user
decides — never silently patch around regressions.

## Modes

| Mode | Research | Regression rail | Checkpoints | Progression |
|------|----------|-----------------|-------------|-------------|
| interactive (default) | yes | yes | human confirmation each step | one task at a time |
| fast | no | yes | human confirmation each step | one task at a time |
| auto | yes | yes | auto-approve low-risk only | continuous |
| parallel | yes | yes | batch per wave | concurrent lanes |
| no-test | yes | warning | human confirmation each step | one task at a time |
| tdd | yes | rail first | human confirmation each step | one task at a time |

## The loop

```
Scout -> [requirements unclear? pin them -> loop] -> Research -> Decompose
-> per task: Implement -> [simplify signal? simplify] -> End-user test
-> [proven? next task : stuck protocol] -> Finalize -> Report
```

Human checkpoints in non-auto modes: post-research, post-decomposition,
post-implementation, post-testing (rail green + end-user proof before
finalize).

Always enforced (all modes):

- **Regression rail**: 100% pass unless no-test mode
- **Code review**: check (a) every acceptance criterion met, (b) no
  regression in touchpoints/blast radius, (c) no breaking contract changes
  unless called out, (d) follows scout-found patterns, (e) no new
  lint/type/build errors
- **End-user testing**: per `../../references/end-user-actor.md`, drive
  the finished feature as an end user via MCP/automation tools — click,
  submit, navigate — capturing fresh evidence per
  `../../references/evidence-contract.md`. "The code looks right" and
  "tests pass" are not proof the feature works for a user. This step is
  never skipped, faked, or marked done without actual execution — if no
  tool path exists, the finalize report says UNVERIFIED with the reason.
- **Stuck protocol on failure**: attempt the fix once; root-cause loop
  (max 3 hypotheses) via `root-cause-debugging`; split the task into
  smaller provable tasks; then escalate with a structured blocker report.
  A retry is never a fix.
- **Finalize**: update plan status across ALL phase files, update docs if
  warranted, offer to commit, write the report — citing the driven
  end-user evidence (tools used, actions performed, evidence paths) for
  every acceptance criterion

## Step Output Format

```
✓ Step [N]: [brief status] — [key metrics]
```

## Measured additions (2026-08-12, aperant-tui gate runs)

1. **Never mutate a running artifact.** Editing a gate/driver script while
   it executes corrupts the run mid-flight (shells read scripts
   incrementally); the evidence from such a run is splice-shaped and must
   be discarded. Edit, then re-launch. Measured basis: a mid-run edit
   killed a live gate with syntax errors at the edit point; the
   "successful" early steps and the post-edit steps never coexisted in one
   process.
2. **One driver per shared target.** Two gates launched against the same
   fixture/repo/user-data contaminate each other's disk assertions (a
   RESUME-on-disk check passed by reading the OTHER run's file). Before
   launching, list and kill prior drivers; after finishing, destroy the
   sessions you created. Concurrency belongs to the task graph, not to
   drivers of the same mutable target.
3. **Push before you optimize.** Volatile workbenches (tmpfs, ephemeral
   containers) erase unpushed work without warning; a lost tree costs a
   full reconstruction. The push point is immediately after every verified
   unit — the harness, the fixture builder, and the driver scripts belong
   in the repo (as `tools/`), so a wipe can never orphan them again.

## Anti-Rationalization

| Thought | Reality |
|---------|---------|
| "Too simple to plan" | Simple tasks hide complexity. Decomposing takes 30 seconds |
| "I already know how" | Knowing != planning. Write the proof obligation down |
| "Let me just start coding" | Undisciplined action wastes tokens |
| "The user wants speed" | Fastest path = task -> execute -> prove -> next |
| "I'll plan as I go" | That's hoping, not planning |
| Faking or skipping validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim; unexecuted = UNVERIFIED |


## Example

**Input:** User: 'cook this feature: export button on the reports page'

**Output:** Tasks T1-T3 decomposed, each with a proof obligation; T2's end-user test (click Export -> real .xlsx downloads with 42 rows) is captured as evidence before T2 is marked DONE.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `brainstorm` | before any task is created | scout-first (GATE 2) + exact requirements (GATE 3) |
| `validation-plan` | task decomposition | proof-obligation format (PO-N) |
| `end-user-testing` | Contract 4 — done means proven | the proof standard + verdict |
| `functional-validation` | executing the end-user test | how to drive the real runtime per platform |
| `root-cause-debugging` | stuck protocol | root cause when a task cannot be proven |
| `stack-testing` | regression rail | stack-specific test discipline |

Called by: `implement`.
