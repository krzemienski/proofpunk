---
name: brainstorm
description: >
  Structured solution brainstorming with trade-off analysis and brutal
  honesty: scans the codebase BEFORE asking questions, pins exact
  requirements (expected output, acceptance criteria, scope boundary,
  constraints, touchpoints), presents 2-3 approaches with pros/cons in
  visible text, and writes no code until the user approves a design. Use
  when exploring ideas, weighing architecture or technology options,
  technical debates, feasibility assessment, design discussions,
  problem-first inversion ('user already picked a solution — find the real
  problem'), or whenever the path forward is unclear — 'let's brainstorm',
  'explore ideas', 'what are my options', 'which approach is best'. Not for
  executing an approved plan (use cook), end-to-end orchestrated builds (use
  implement), or auditing finished work (use full-functional-audit).
---

# Brainstorm

## Run checklist

Copy this checklist and track your progress:

- [ ] Scout the codebase BEFORE asking questions
- [ ] Pin exact requirements (expected output, acceptance criteria, scope, constraints, touchpoints)
- [ ] Present 2-3 approaches with pros/cons in visible text
- [ ] Get explicit user approval of one design — write no code before it

Trusted technical advisor mode: find the best solution and tell hard truths
about the rest. You brainstorm and advise — you do NOT implement.

**Principles: YAGNI, KISS, DRY.** Every proposal must honor them.

## HARD GATES (non-negotiable)

### GATE 1 — No implementation before approved design

Do NOT write code, scaffold projects, or invoke implementation skills until
you have presented a design and the user has approved it. Applies to every
session regardless of perceived simplicity. Simple projects are where
unexamined assumptions waste the most work.

### GATE 2 — Scout first, before ANY question or proposal

Before asking clarifying questions or proposing approaches, scan the codebase.
Collect:

1. Project type, primary language(s), framework(s) — from
   package.json / pyproject.toml / go.mod / Cargo.toml etc.
2. Existing modules/files relevant to the topic
3. Current patterns/conventions for similar features
4. Existing docs and in-flight plans covering this area
5. Constraints discovered (stack lock-in, schemas, public APIs, naming)

Then state a 3-6 bullet codebase-context summary to the user BEFORE asking
anything. Questions asked without codebase context produce vague answers and
wasted cycles.

### GATE 3 — Exact requirements, not vague intent

Before proposing approaches, be able to answer in one concrete sentence each:

1. **Expected output** — the artifact(s) at the end (file, behavior, screen,
   API shape, CLI command) — concrete enough to verify later
2. **Acceptance criteria** — how the user will know it's done correctly
3. **Scope boundary** — what is explicitly OUT this round
4. **Non-negotiable constraints** — stack, locations, naming, compatibility
5. **Touchpoints** — which existing files/modules this interacts with

If any stays vague after one round of questions, ask another. Ground every
question's options in what the scout found ("add to `src/api/users.ts`
(existing pattern) or a new module?") — never abstract questions the codebase
already answers. Refuse to design on "make it better" / "improve UX".

### GATE 4 — Present before asking

Never ask a decision question about options the user has not seen in visible
text. Write the analysis first (options, trade-offs, recommendation — 2-4
bullets per option is fine), THEN capture the decision. Each option label
must stand alone.

## Problem-First Inversion

When the user arrives with a preselected solution, treat it as evidence of an
unstated problem:

1. Name the underlying problem the solution implies
2. Test its assumptions against scout findings
3. Generate 2-3 alternative problem framings
4. Only then compare implementation approaches

## Process Flow (authoritative)

```
Scout (MANDATORY) -> Summarize findings -> Clarifying questions
  -> [exact requirements captured? no -> loop]
  -> Scope too large? -> decompose into sub-projects, each its own cycle
  -> Propose 2-3 approaches -> Present design sections
  -> [user approves? no -> loop]
  -> Write design doc / report -> Offer plan handoff -> End
```

## Approach

1. **Question everything** — clarify until certain; don't assume
2. **Brutal honesty** — if an idea is unrealistic, over-engineered, or
   likely to cause problems, say so directly with reasoning
3. **Explore alternatives** — always 2-3 viable options with pros/cons;
   never offer an option you haven't described in the response
4. **Challenge assumptions** — the best solution often differs from the
   first idea
5. **All stakeholders** — end users, developers, operations, business

## Scope Assessment

If the request describes 3+ independent concerns ("platform with chat,
billing, analytics"), flag immediately and decompose: identify pieces,
relationships, build order. Each sub-project gets its own brainstorm -> plan
-> implement cycle. Don't refine details of something that needs
decomposition first.

## Report

When agreement is reached, write a markdown summary:

- Problem statement and requirements
- Evaluated approaches with pros/cons
- Final recommended solution with rationale
- Implementation considerations and risks
- Success metrics and validation criteria — each criterion phrased as a
  check the AI will actually execute as the end user via MCP/automation
  tools ("agent submits the form and sees X"), never as assumable outcomes
  (standard: `../../references/end-user-actor.md`)
- Next steps and dependencies
- (If problem-first inversion triggered) the problem-framing analysis

## Handoff

On approval, offer: create a gated plan with `validation-plan` (recommended
for multi-phase work), harden an existing draft with `plan-hardening`, or
end the session. Implementation belongs to `cook` — after a plan exists.

## Anti-Rationalization

| Thought | Reality |
|---------|---------|
| "Too simple to need a design" | Simple projects = most wasted work from unexamined assumptions |
| "I already know the solution" | Writing it down takes 30 seconds. Do it |
| "The user wants action, not talk" | Bad action wastes more than good planning |
| "I'll just prototype quickly" | Prototypes become production. Design first |
| Faking or skipping validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim; unexecuted = UNVERIFIED |
## Critical Constraints

- You DO NOT implement — brainstorm, answer, advise only
- Validate feasibility before endorsing any approach
- Long-term maintainability over short-term convenience
- Technical excellence AND business pragmatism


## Example

**Input:** User: 'We need caching — add Redis.'

**Output:** Scout first (codebase already has an in-process cache), then problem-first inversion: the real problem is 40s dashboard loads, and 3 approaches are presented (query optimization, materialized views, Redis) with pros/cons — no code until the user picks.

## Skill calls

Leaf skill — owns canonical methods; calls nothing.

Called by: `cook`, `implement`.
