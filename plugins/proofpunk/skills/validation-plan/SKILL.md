---
name: validation-plan
description: >
  Authors multi-phase project plans where every phase carries blocking
  cumulative proof obligations — BRIEF, ROADMAP, per-phase PLAN, SUMMARY +
  VALIDATION with run-scoped evidence. Proofs are cumulative: phase N's
  validation re-verifies phases 1..N-1, so a regression in earlier work
  blocks advancement. Use when asked to plan a multi-phase build, create a
  validation plan, structure a project roadmap, break a feature into proven
  phases, write a BRIEF/ROADMAP, or when an autonomous runner needs phases
  it cannot advance past without proof. Not for executing the plan (use implement
  or implement) or hardening an existing draft (use plan-hardening).
---

# Validation Plan

## Run checklist

Copy this checklist and track your progress:

- [ ] Write the BRIEF (objective, criteria, constraints)
- [ ] Write the ROADMAP (phase breakdown)
- [ ] Write each phase PLAN with blocking proof obligations
- [ ] Define cumulative VALIDATION per phase (re-verifies all earlier phases)
- [ ] Confirm every gate has a run-scoped evidence requirement

Plans that cannot be marked done on vibes. Every phase ships with the
evidence it must produce, and later phases re-prove earlier ones.

**READ `../../references/evidence-contract.md` — proofs follow it.**

## Planning Hierarchy

```
.planning/
├── BRIEF.md                 # problem, constraints, success criteria
├── ROADMAP.md               # phase list with dependencies and proof summary
└── phases/
    └── NN-<slug>/
        ├── NN-MM-PLAN.md        # the work: tasks, contracts, proof block
        ├── NN-MM-SUMMARY.md     # what was actually done (written after)
        ├── NN-MM-VALIDATION.md  # the verdict with cited evidence
        └── evidence/            # run-scoped artifacts (or link to e2e-evidence/)
```

## Step 1 — BRIEF

Capture in one page:

- **Problem**: the observable pain or gap, with evidence it exists
- **Expected output**: concrete artifacts (files, behaviors, endpoints
  screens) verifiable later
- **Acceptance criteria**: specific inputs -> outputs and edge cases that
  must work
- **Scope boundary**: what is explicitly OUT this round
- **Non-negotiable constraints**: stack, file locations, naming, backward
  compatibility, deadlines
- **Touchpoints**: existing modules/contracts this will modify or must not break

If any item is vague ("make it better"), the BRIEF is not done.

## Step 2 — ROADMAP

Decompose into phases where each phase:

- Delivers a verifiable increment (not "work on X" but "X works end-to-end")
- Declares its dependencies (which phases must be green first)
- Declares its proof obligation (what end-user test proves it done)
- Is small enough that its end-user test runs in minutes, not hours

Order phases so foundations are proven before dependents start. Parallel
phases must not share mutable resources (see full-functional-audit mutex
table).

## Step 3 — Per-phase PLAN

Each PLAN.md contains:

1. **Objective** — one sentence, verifiable
2. **Tasks** — ordered, each with an owner surface (file/module)
3. **Contracts** — signatures, schemas, API shapes this phase must keep or change (changes called out explicitly)
4. **Validation proof block**:

```yaml
evidence:
  assertion: "<specific observable claim, e.g. 'POST /login returns 200 + JWT'>"
  type: screenshot | api-response | cli-output | log | test-run
  path_template: "e2e-evidence/run-<id>/step-NN-<action>.<ext>"
  min_size_bytes: 1024
  covers_phases: [all previous phase ids]   # cumulative proof
  actor: ai-end-user                        # the AI drives the actions via MCP/automation tools
```

Proof obligations must specify DRIVEN end-user actions ("agent clicks X
observes Y"), never passive checks ("screenshot exists"). See
`../../references/end-user-actor.md`.

When a task needs to be handed to a runner as a standalone file, author it
in the `references/task-file-format.md` format: acceptance criteria written
as executable end-user actions with an explicit "When is a driven action"
clause, so the runner cannot close the task with unexecuted validation.

A phase without a complete proof block is not provable — `end-user-testing`
refuses to validate it.

## Step 4 — Execution handoff

The runner (human, `implement`, or an autonomous loop) works the PLAN, then writes:

- **SUMMARY.md**: what was actually done, deviations from PLAN and why
- **VALIDATION.md**: the verdict from `end-user-testing` — PASS criteria cited
  to fresh run-scoped evidence paths, cumulative re-verification included
  and an explicit record of the end-user actions the AI actually executed
  (tools used + actions performed). Criteria whose validation was not
  executed are marked UNVERIFIED — never silently passed.

## The Cumulative Rule

Phase N's VALIDATION must re-run the proofs of phases 1..N-1 against the
current system. A green phase 3 that broke phase 1's behavior is a REGRESSION
and blocks advancement. Record regression re-runs explicitly:

```
Cumulative re-verification:
- [x] phase-01 proof — evidence: <new run path> — still PASS
- [x] phase-02 proof — evidence: <new run path> — still PASS
```

## Gate Discipline

- Gates are **blocking**: no advancement on FAIL or BLOCKED.
- Remediation happens in the current phase — never "fix it in a later phase".
- After any fix, re-run the phase proof AND the cumulative set.
- A plan amended mid-flight gets the amendment written into PLAN.md with the
  reason — no silent scope drift.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Phases defined as effort ("work on auth") | Phases defined as verifiable increments ("login flow works end-to-end") |
| Gates added after the work is done | Gate blocks authored with the PLAN, criteria defined before evidence |
| Phase proofs that only test the new work | Cumulative proofs re-proving all previous phases |
| "We'll validate at the end" | Every phase proofd; final phase is a regression sweep, not the first test |
| Silent scope changes mid-phase | Amend PLAN.md in writing with the reason |
| Faking or skipping validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim; unexecuted = UNVERIFIED |

## Example

**Input:** User: 'Plan the billing rebuild in phases I can't fake.'

**Output:** BRIEF -> ROADMAP (4 phases) -> per-phase PLANs each with blocking proof obligations; phase 3's validation re-proves phases 1-2, so a regression blocks advancement.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `end-user-testing` | every VALIDATION gate | run-scoped evidence the gates cite |

Called by: `implement`, `plan-hardening`.
