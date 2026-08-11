# Task File Format (validation-plan)

Structured per-task files with acceptance criteria, adapted from
`code-task-generator` — with the Proofpunk end-user validation policy
applied: every acceptance criterion must be verifiable by the AI actually
executing MCP/automation tools as the end user, never by assumption.

## When to Use

Generate `.code-task.md` files when breaking a phase or feature into
implementable tasks, or converting a plan into executor-ready units.

## Format

```markdown
# Task: [Descriptive Title]

## Context
- Current state: [what exists now]
- Goal: [what should exist after]
- Files involved: [specific paths]

## Requirements
1. [Specific, measurable requirement]

## Acceptance Criteria
- [ ] Given [precondition], When the AI [end-user action executed via
  MCP/automation tool], Then [observable result + evidence to capture]

## Dependencies
- [Task IDs this depends on]

## Validation
Execute each acceptance criterion by actually performing the action as the
end user (click, submit, call, run). Capture fresh run-scoped evidence per
the evidence contract. A criterion not executed is UNVERIFIED — never
checked off.
```

## Rules

- **One concern per task** — unrelated changes split; link with dependencies
- **Context is mandatory** — executor needs file paths, current behavior, and
  why the change is needed
- **Acceptance criteria are executable end-user actions** — not "code
  handles X" but "agent submits the form with empty email and sees the
  inline error". Given-When-Then where When is a driven action
- **No assumable criteria** — if a criterion cannot be executed against the
  real system, rewrite it until it can, or mark the task blocked
- **Process one step at a time** for multi-step plans — adapt later steps
  based on earlier results

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Tasks without acceptance criteria | "Done" becomes subjective | Every task carries executable Given-When-Then criteria |
| Bundling unrelated changes | Blocks parallel work; hard to review | One concern per task |
| Criteria the AI can't execute as the end user | Invites assumed/faked validation | Rewrite as a driven action with an observable result |
| Marking criteria done without executing them | Validation theater | Unexecuted = UNVERIFIED, per `../../../references/end-user-actor.md` |
