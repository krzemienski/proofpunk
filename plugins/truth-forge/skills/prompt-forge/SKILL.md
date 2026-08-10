---
name: prompt-forge
description: >
  Prompt engineering, rating, and pipeline design in one skill: author
  high-quality prompts (system prompts, task prompts, structured-output
  prompts) on the canonical XML tag skeleton, RATE any prompt against a
  quantitative evaluation rubric with test cases and metrics, optimize
  weak prompts against real failure evidence, and build multi-stage
  meta-prompt pipelines (.prompts/ directories with dependency-aware
  Do/Plan/Research/Refine stages, each with a SUMMARY.md). Every mode
  runs the always-on workflow: sequential thinking, todo tracking, an
  authorization engine, and a file-output contract — remediations from
  any rating are applied immediately and written to a file (a new file
  by default, the input file only with explicit consent), never left as
  chat-only suggestions. Use whenever asked to write, review, score,
  rate, improve, or debug a prompt; design a system prompt; force
  structured output; manage long context; create prompt pipelines or
  meta-prompts; or when output is unreliable and the prompt is suspect.
---

# Prompt Forge

Design it, rate it, fix it, chain it. Prompt work backed by patterns,
rubrics, and evidence — not vibes. Every engagement ends with a file on
disk, and every decision runs through the always-on workflow.

## Section 0 — Always-On Workflow (every mode, no exceptions)

These five disciplines run in EVERY mode, in this order. Skipping any of
them is a defect in the engagement, not a stylistic choice.

### 0.1 Sequential Thinking

Before writing or judging anything, reason in explicit numbered steps:

1. **Decompose** — break the request into its actual sub-problems
   (intent, audience, format, failure modes, file target)
2. **Analyze stepwise** — one numbered step per sub-problem; later steps
   MAY revise earlier ones, and when they do, say so ("revising step 2
   because step 4 showed the format assumption was wrong")
3. **Branch when it matters** — when two real alternatives exist (e.g.
   XML vs JSON-schema output, in-place edit vs new file), lay out both
   branches, then pick one with a one-line justification
4. **Verify the chain** — re-read the numbered steps; if any step is
   unsupported by the request or the evidence, fix it before acting

Only then act. A jump straight to output is the single most common
cause of prompt re-work.

### 0.2 Todo Discipline

Track multi-step prompt work as an explicit todo list:

- One todo per concrete action (intake, draft, gate-check, write file,
  re-rate) — never one mega-todo
- Exactly ONE todo in progress at a time
- Complete a todo the moment its action is done; add newly discovered
  follow-ups as new todos instead of silently absorbing them
- Before delivering, read the list back: anything still pending must be
  either finished or explicitly reported as not done

### 0.3 Authorization Engine

Every file-touching or shipping decision checks this table first:

| Action | Authorization needed? |
|--------|----------------------|
| Write a NEW file (remediated / optimized / authored copy) | No — this is the default action |
| Edit the input file IN PLACE | Yes — explicit user consent first |
| Ship a prompt graded `needs-work` or `rewrite` as final | Yes — explicit user sign-off after seeing the score |
| Overwrite or delete anything beyond the input file | Yes — explicit consent, always |
| Produce a report-only rating with NO file output | Yes — only when the user explicitly asks for report-only |

Default-safe posture: when authorization is ambiguous, write a new file,
leave the input untouched, and say what you did. Never block on consent
you don't need (new files), never act without consent you do need
(in-place edits, below-threshold shipping).

### 0.4 File-Output Contract

Every mode ends with at least one file on disk. Naming when the input
was a file `NAME.md`:

| Mode | Always writes | Also writes |
|------|---------------|-------------|
| AUTHOR | `NAME.prompt.md` (or the path the user gave) | — |
| RATE | `NAME.rating.md` (scorecard + test cases + fixes) | `NAME.remediated.md` — top fixes APPLIED |
| OPTIMIZE | `NAME.optimized.md` (failure fixes applied) | before/after scores inside the report |
| PIPELINE | `.prompts/<NN>-<stage>/PROMPT.md` per stage | `SUMMARY.md` per stage after execution |

Chat-only suggestions are a contract violation. If the user gave prose
instead of a file, treat their message as the input, still write
`remediated`/`optimized` output to a file, and offer the in-place edit
of the source file if one exists.

### 0.5 XML Tag Standard

Prompts authored here use the canonical skeleton; RATE checks for it;
OPTIMIZE preserves or repairs it:

```xml
<task>what to do, in one imperative paragraph</task>
<context>what the executor knows and must not assume</context>
<skills_to_activate>agentic prompts only</skills_to_activate>
<mcp_tools>agentic prompts only</mcp_tools>
<sequential_thinking>the numbered reasoning steps the executor must follow</sequential_thinking>
<todos>the tracked work items the executor must maintain</todos>
<authorization>what the executor may do without asking vs must get consent for</authorization>
<constraints>tone, length, forbidden behaviors, domain rules</constraints>
<output_contract>exact shape of the deliverable, including file paths</output_contract>
<validation>how the executor proves it worked, as the end user</validation>
<example>at least one concrete input/output pair</example>
```

| Tag | Required | Purpose |
|-----|----------|---------|
| `task` | always | the imperative core |
| `context` | always | grounding; kills assumption drift |
| `skills_to_activate`, `mcp_tools` | agentic prompts | names the capability inventory (see 1.3) |
| `sequential_thinking` | always | embeds the 0.1 discipline into the prompt itself |
| `todos` | multi-step work | embeds the 0.2 discipline |
| `authorization` | system-touching work | embeds the 0.3 consent boundaries |
| `constraints` | always | negative space: what not to do |
| `output_contract` | always | the deliverable's exact shape |
| `validation` | system-touching work | end-user proof per gate 8 |
| `example` | always | concreteness anchor |

Balanced tags, no orphans, no invented tags outside this table without
a stated reason.

## Mode Routing

| Request | Mode | Start at |
|---------|------|----------|
| "Write a prompt that..." | AUTHOR | Section 1 |
| "Rate / review / score this prompt" | RATE | Section 2 |
| "This prompt's output is bad / unreliable" | OPTIMIZE | Section 3 |
| "Create a multi-stage prompt pipeline" | PIPELINE | Section 4 |

Section 0 runs first in every mode.

## Section 1 — AUTHOR

### 1.1 Input-type handling

| Input type | Signal | Treatment |
|------------|--------|-----------|
| Voice transcript / ramble | run-on sentences, filler | extract intent, discard filler |
| File path | starts with a path | read/infer the review-or-improve task |
| Partial idea | incomplete thought | infer scope, add structure |
| Single word | "refactor", "fix" | ask for scope or apply stated defaults |
| Multi-part | several distinct tasks | decompose into pipeline stages (Section 4) |

### 1.2 Intake

Before writing, pin down the intake (5-7 questions, never skip):

1. **Task** — what exactly should the output do or be?
2. **Audience/model** — which model consumes it, and what does it know already?
3. **Format** — XML-tagged (default, per 0.5), markdown, JSON-schema-driven, or chat-template?
4. **Depth** — Core (single clear instruction set) or Advanced (examples, edge cases, fallbacks)?
5. **Inputs/outputs** — concrete sample input and the exact expected output shape
6. **Constraints** — tone, length, forbidden behaviors, domain rules
7. **Failure modes** — what wrong output has been seen or is feared?

### 1.3 Capability inventory (for prompts that drive agentic work)

Inventory what the executing agent can use, and name it in the prompt:
available skills, MCP servers/tools (`<skills_to_activate>`, `<mcp_tools>`
sections in XML formats). A prompt that never mentions the tools produces
generic output that ignores them.

### 1.4 Model tone

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

### 1.5 Authoring quality gates (all seven must pass)

1. **Structure** — valid skeleton for the target format (per 0.5 for XML:
   balanced tags, required tags present)
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

### 1.6 Output

Write the prompt to a file (0.4). In chat, output the PROMPT ONLY (no
surrounding essay) unless the user asks for rationale.

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
## Remediation: applied to <path> — re-scored <before>/100 -> <after>/100
```

Rules:
- Score against concrete test cases, not impressions — run or dry-run them
- A prompt that cannot define its own success metric scores 0 on Testability
- Cite the exact line/section behind every deduction
- Structure deductions reference the 0.5 tag table explicitly (missing
  `output_contract` is a Structure deduction AND an Output-contract deduction)

### 2.1 Remediation application (mandatory)

A rating that stops at the scorecard is unfinished. Immediately:

1. Apply the top fixes to the prompt — all of them that the evidence
   supports, ordered by impact
2. Write the remediated prompt to a file per 0.4 (default: new
   `NAME.remediated.md`; in-place edit of the input ONLY after explicit
   consent per 0.3)
3. Re-score the remediated version against the SAME test cases and
   report before/after
4. If the remediated version still grades below production-ready, the
   authorization engine (0.3) decides: ship only with explicit user
   sign-off, otherwise state what evidence is still missing

The rating report goes to `NAME.rating.md` (0.4). Chat carries the
scorecard summary plus the file paths, not the full artifacts.

## Section 3 — OPTIMIZE

1. Collect REAL failure evidence: actual bad outputs, not hypothetical ones
2. Classify each failure: instruction ambiguity | missing context | format
   drift | reasoning gap | context overflow
3. Apply the targeted fix from `references/prompt-optimization.md`
4. Write the optimized prompt to a file per 0.4 (default
   `NAME.optimized.md`; in-place only with consent per 0.3)
5. Re-run the SAME test cases that failed
6. Report before/after scores — optimization without re-measurement is guessing

Never "improve" a prompt in the abstract. No failure evidence -> ask for a
real bad output first. The sequential-thinking chain (0.1) is where the
failure classification lands — write the classification into the numbered
steps, not into chat as an aside.

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
- **Every stage prompt follows the 0.5 skeleton** — Research and Plan
  stages included; a pipeline stage is where XML discipline pays off most,
  because later stages parse earlier outputs
- **Every stage maps to a todo** (0.2) — pipeline execution is the
  canonical multi-todo workflow
- Stages that produce system-touching work carry validation gates per
  `../../references/evidence-contract.md`

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Rating a prompt without test cases | Build 3-5 concrete cases first |
| Rating that ends at the scorecard | Apply the fixes, write the remediated file, re-score (2.1) |
| Suggesting fixes in chat with no file written | File-output contract (0.4) — always a file |
| Editing the user's input file without asking | Authorization engine (0.3) — new file by default |
| Shipping a needs-work prompt as final | Explicit sign-off per 0.3, or state what's missing |
| Optimizing without a captured bad output | Demand real failure evidence |
| One mega-prompt doing research+plan+execute | Split into pipeline stages |
| Placeholders shipped in a "final" prompt | Gate 4 — zero placeholders |
| "Make it better" edits with no re-test | Same test cases, before/after scores |
| Jumping straight to output | Sequential thinking (0.1) — numbered steps first |
| Inventing ad-hoc XML tags | 0.5 tag table; new tags need a stated reason |
| Marking validation complete without the AI actually invoking MCP/automation tools and acting as the end user | Execute the tools yourself; unexecuted = UNVERIFIED |
| Skipping or faking QA/verification steps under any circumstance | Run them or report them UNVERIFIED — no exceptions |

## Related Skills

- `plan-hardening` — inject validation gates into a finished prompt
- `validation-plan` — pipeline stages that produce plans should follow its hierarchy
