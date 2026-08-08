---
name: prompt-forge
description: >
  Prompt engineering, rating, and pipeline design in one skill: author
  high-quality prompts (system prompts, task prompts, structured-output
  prompts), RATE any prompt against a quantitative evaluation rubric with
  test cases and metrics, optimize weak prompts against real failure
  evidence, and build multi-stage meta-prompt pipelines (.prompts/
  directories with dependency-aware Do/Plan/Research/Refine stages, each
  with a SUMMARY.md). Use whenever asked to write, review, score, rate,
  improve, or debug a prompt; design a system prompt; force structured
  output; manage long context; create prompt pipelines or meta-prompts; or
  when a model's output is unreliable and the prompt is the suspect.
---

# Prompt Forge

Design it, rate it, fix it, chain it. Prompt work backed by patterns,
rubrics, and evidence — not vibes.

## Mode Routing

| Request | Mode | Start at |
|---------|------|----------|
| "Write a prompt that..." | AUTHOR | Section 1 |
| "Rate / review / score this prompt" | RATE | Section 2 |
| "This prompt's output is bad / unreliable" | OPTIMIZE | Section 3 |
| "Create a multi-stage prompt pipeline" | PIPELINE | Section 4 |

## Section 1 — AUTHOR

### Input-type handling

| Input type | Signal | Treatment |
|------------|--------|-----------|
| Voice transcript / ramble | run-on sentences, filler | extract intent, discard filler |
| File path | starts with a path | read/infer the review-or-improve task |
| Partial idea | incomplete thought | infer scope, add structure |
| Single word | "refactor", "fix" | ask for scope or apply stated defaults |
| Multi-part | several distinct tasks | decompose into pipeline stages (Section 4) |

### Intake

Before writing, pin down the intake (5-7 questions, never skip):

1. **Task** — what exactly should the output do or be?
2. **Audience/model** — which model consumes it, and what does it know already?
3. **Format** — XML-tagged (Claude-style), markdown, JSON-schema-driven, or chat-template?
4. **Depth** — Core (single clear instruction set) or Advanced (examples, edge cases, fallbacks)?
5. **Inputs/outputs** — concrete sample input and the exact expected output shape
6. **Constraints** — tone, length, forbidden behaviors, domain rules
7. **Failure modes** — what wrong output has been seen or is feared?

### Capability inventory (for prompts that drive agentic work)

Inventory what the executing agent can use, and name it in the prompt:
available skills, MCP servers/tools (`<skills_to_activate>`, `<mcp_tools>`
sections in XML formats). A prompt that never mentions the tools produces
generic output that ignores them.

### Model tone

Match the target model's guidance: measured language for frontier models
("prefer", "aim to" — aggressive MUST/CRITICAL/ALWAYS stacking causes
over-engineering), explicit parallel-tool-call and proactivity directives
for the faster tiers. For coding tasks, inject the no-mocks rule — the
prompt must never ask for unit-test substitutes (see gate 8 below).

Then author using the bundled references (load on demand):

- `references/prompt-patterns.md` — proven structures (persona, CoT, few-shot, ReAct, guardrails)
- `references/system-prompts.md` — system-prompt architecture and layering
- `references/structured-outputs.md` — JSON schema, XML tags, delimiter strategies
- `references/context-management.md` — context budgeting, ordering, and compression

### Authoring quality gates (all seven must pass)

1. **Structure** — valid skeleton for the target format (XML tags balanced / schema valid)
2. **Completeness** — task, context, constraints, output contract all present
3. **Token count** — within the model's practical budget; no dead weight
4. **No placeholders** — zero `[TODO]`, `[insert X]`, `{???}` left in the prompt
5. **Actionable workflow** — an executor could act without asking clarifying questions
6. **Best practices** — patterns from the references applied deliberately
7. **Examples present** — at least one concrete input/output pair (Advanced mode: few-shot set)

For any prompt that drives system-touching work, add gate 8:
8. **End-user validation clause** — the prompt instructs the executing AI to
   validate by actually operating MCP/automation tools as the end user
   (click, submit, navigate), and forbids reporting success without actual
   execution. Per `../../references/end-user-actor.md`.

Output the PROMPT ONLY (no surrounding essay) unless the user asks for rationale.

## Section 2 — RATE

Score any prompt against the rubric in
`references/evaluation-frameworks.md`. Produce:

```
## Prompt Rating — <name>
Overall: <score>/100 — <grade: production-ready | needs-work | rewrite>
| Dimension        | Score | Notes |
|------------------|-------|-------|
| Clarity          | /20   | ...   |
| Specificity      | /15   | ...   |
| Structure        | /15   | ...   |
| Output contract  | /15   | ...   |
| Edge-case cover  | /15   | ...   |
| Testability      | /10   | ...   |
| Token efficiency | /10   | ...   |
## Failure modes predicted: <list>
## Test cases: <3-5 concrete inputs with expected outputs>
## Top 3 fixes, ordered by impact
```

Rules:
- Score against concrete test cases, not impressions — run or dry-run them
- A prompt that cannot define its own success metric scores 0 on Testability
- Cite the exact line/section behind every deduction

## Section 3 — OPTIMIZE

1. Collect REAL failure evidence: actual bad outputs, not hypothetical ones
2. Classify each failure: instruction ambiguity | missing context | format
   drift | reasoning gap | context overflow
3. Apply the targeted fix from `references/prompt-optimization.md`
4. Re-run the SAME test cases that failed
5. Report before/after scores — optimization without re-measurement is guessing

Never "improve" a prompt in the abstract. No failure evidence -> ask for a
real bad output first.

## Section 4 — PIPELINE (meta-prompts)

Build multi-stage prompt pipelines under `.prompts/`:

```
.prompts/
├── 01-<topic>-research/
│   ├── PROMPT.md      # the stage prompt
│   └── SUMMARY.md     # filled after execution: what it produced, key outputs
├── 02-<topic>-plan/
└── 03-<topic>-do/
```

- **Purpose routing**: each stage is one of Research (gather), Plan (decide),
  Do (execute), Refine (improve) — never a blend
- **Dependency-aware**: stage N's prompt declares which earlier SUMMARY.md
  files it consumes; execution order follows dependencies
- **Every stage gets a SUMMARY.md** — the contract that lets later stages
  trust earlier outputs
- Stages that produce system-touching work carry validation gates per
  `../../references/evidence-contract.md`

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Rating a prompt without test cases | Build 3-5 concrete cases first |
| Optimizing without a captured bad output | Demand real failure evidence |
| One mega-prompt doing research+plan+execute | Split into pipeline stages |
| Placeholders shipped in a "final" prompt | Gate 4 — zero placeholders |
| "Make it better" edits with no re-test | Same test cases, before/after scores |
| Marking validation complete without the AI actually invoking MCP/automation tools and acting as the end user | Execute the tools yourself; unexecuted = UNVERIFIED |
| Skipping or faking QA/verification steps under any circumstance | Run them or report them UNVERIFIED — no exceptions |

## Related Skills

- `plan-hardening` — inject validation gates into a finished prompt
- `validation-plan` — pipeline stages that produce plans should follow its hierarchy
