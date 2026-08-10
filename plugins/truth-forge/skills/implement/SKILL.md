---
name: implement
description: >
  Orchestrated implementation front door that composes every truth-forge
  skill into one run: mine past Claude Code sessions for previous
  implementations (session-intent), explore the codebase with parallel
  scout agents, forge the implementation prompt (prompt-forge on the
  canonical XML skeleton), harden the plan, execute under gate
  discipline (cook), debug root causes, and prove every success
  criterion as the end user. Flags: --parallel plans and implements in
  parallel lanes (planning via prompt-forge pipelines); --auto never
  stops until the TRUE success criteria are accomplished — criteria are
  distilled first, and unclear goals get explicit user approval before
  any code; --mine runs session mining first. Use for "implement X",
  "build X end to end", "use all the skills to ship this", or to re-run
  how past sessions implemented similar goals.
---

# Implement — Orchestrated Implementation

One command that runs the whole pipeline: mine, explore, forge, plan,
execute, debug, validate — with the execution tracked as todos from the
first step to the last proof.

**Relationship to `cook`**: implement is the orchestrator (the
conductor); cook is the execution engine (the player) it delegates the
code-writing phases to. When scope is fully known and the job is a
single lane, `cook` directly is enough. When the job needs session
mining, parallel lanes, prompt-forged planning, or multi-skill
composition, that is implement.

## Command Surface

```
implement "<goal>" [--parallel] [--auto] [--mine] [--fast] [--no-test] [--tdd]
implement mine [--project DIR] [--since DATE] [--until DATE] [--json]
```

| Flag | Effect | Why it exists |
|------|--------|---------------|
| `--parallel` | Plan AND implement in parallel manners: exploration fans out to parallel scout agents; prompt-forge authors the plan as a `.prompts/` pipeline whose independent stages run in parallel; implementation splits into parallel lanes by module boundary, each lane its own todo chain | wall-clock speed on multi-module goals; planning and execution parallelism are one decision, not two |
| `--auto` | No stopping whatsoever until the TRUE success criteria are accomplished. Criteria are distilled FIRST (Phase 0); if they are not clearly laid out, or the goal is not understood, STOP and get the user's approval of the distilled criteria before any code. In-scope actions need no further human gates; the loop ends only when every criterion is proven as the end user | unattended runs with a real finish line instead of "looks done" |
| `--mine` | Run session mining first (Phase 1, never skipped with this flag) | reuse how past sessions actually implemented similar goals |
| `--fast` | Skip the research sub-step inside planning (passed to cook's fast mode) | known territory, known stack |
| `--no-test` | Downgrade the test gate to a warning the user must accept (cook semantics) | environments with no runnable suite; regression rail only |
| `--tdd` | Tests-first per phase (cook semantics) | refactor-heavy goals |

Unknown flags are rejected with this table, never silently ignored.
`--auto` never overrides the authorization boundaries in Phase 5:
destructive operations, out-of-scope edits, and below-threshold shipping
still require explicit consent, flags or no flags.

## Phase 0 — Distill the TRUE success criteria (always first)

Before mining, exploring, or coding, distill the success criteria from
the goal. A TRUE criterion is:

1. **Observable** — checkable from outside the code (response body,
   screen state, file on disk, exit code), not "the code handles it"
2. **End-user provable** — provable by driving the real system as the
   end user per `../../references/end-user-actor.md`
3. **Measurable** — has a pass/fail threshold stated in numbers or
   exact strings

**Approval gate**: if the goal is not clearly laid out, or the
distillation required assumptions the user never stated, present the
distilled criteria and get explicit approval BEFORE Phase 2. Under
`--auto` this is the one mandatory stop — everything after it runs
without stopping. Record the approved criteria verbatim; the final
report grades against exactly these, nothing broader, nothing vaguer.

## Phase 1 — MINE (session-intent)

With `--mine`, or whenever the goal smells like past work ("again",
"like the X feature"), mine previous sessions via `session-intent`:

- Extract past implementation sessions: first prompt (intent), steering
  prompts, tool usage, files touched, commits
- Read the intent behind those sessions' prompts, not just their text —
  what was the user actually trying to get built
- Output: a "previous implementations" matrix (session, intent, approach
  inferred from tools/files, outcome signals) that feeds Phase 2's
  exploration (where did past runs touch?) and Phase 3's prompt (what
  framing worked?)

`implement mine` alone (no goal) runs the mining and prints only the
matrix — a reconnaissance pass, no implementation.

## Phase 2 — EXPLORE (parallel scout agents)

Codebase exploration via scout agents — with `--parallel`, several at
once, each owning a question:

| Scout | Question |
|-------|----------|
| Structure | project type, modules, entry points |
| Patterns | conventions of similar features — implementation must match them |
| Contracts | public APIs, schemas, env vars the goal could touch |
| History | what Phase 1's matrix flagged as past touchpoints |

Synthesize one 3-6 bullet context summary. Contradictions between
scouts are resolved against the actual code, never by majority vote.

## Phase 3 — FORGE (prompt-forge)

Author the implementation prompt with prompt-forge AUTHOR mode, on the
canonical 0.5 XML skeleton — including `<sequential_thinking>`,
`<todos>`, `<authorization>`, `<output_contract>` (with the exact file
paths the run must produce), and `<validation>` (the end-user proof per
criterion). The approved Phase 0 criteria become the prompt's success
metrics verbatim.

## Phase 4 — PLAN (validation-plan + plan-hardening)

- Default: one plan following the `validation-plan` hierarchy, hardened
  per `plan-hardening` (validation gates inside the plan, not after it)
- With `--parallel`: prompt-forge PIPELINE mode — a `.prompts/` tree
  whose independent stages (per module/lane) are planned in parallel and
  declare their dependencies; each stage gets a SUMMARY.md contract

## Phase 5 — EXECUTE (cook's gate discipline)

Execute the plan under cook's gates: no code before the reviewed plan,
no side effects, 100% test pass as the REGRESSION rail, patterns matched
to scout findings. With `--parallel`, lanes run concurrently, each
tracked as its own todo chain; lane merges are serialized through the
contract checks (no two lanes may widen the same public contract without
explicit consent).

Authorization boundaries that even `--auto` respects: destructive
operations (delete/overwrite beyond the plan's touchpoints), edits
outside the approved scope, and shipping anything graded below the
approved criteria — all stop for explicit consent.

## Phase 6 — DEBUG (root-cause-debugging)

Any failure routes here, never to a retry: reproduce, minimize,
hypothesize, instrument; fix the root cause in the real system (no
sleeps, no swallowed exceptions, no symptom patches); then re-validate
the original failure AND its blast radius.

## Phase 7 — VALIDATE (as the end user)

Per criterion, proof gathered by driving the real system:
`functional-validation` protocol, `evidence-gates` standard,
`stack-testing` for the stack-specific real-system checks. Unexecuted =
UNVERIFIED — the `--auto` loop treats UNVERIFIED as NOT DONE and keeps
going (or stops for consent if the blocker needs authorization).

## Phase 8 — REPORT

A criteria-by-criteria proof table: criterion (verbatim from Phase 0) |
proof (tool, action, evidence path) | PASS/FAIL/UNVERIFIED. Plus the
todo ledger: everything done, everything pending and why.

## Execution discipline (all phases)

- Every phase and every parallel lane is a todo; exactly one in progress
  per lane; completed immediately when done; the ledger is read back
  before the report
- Sequential thinking per prompt-forge 0.1 at every phase transition:
  numbered steps, revisions stated, branches justified

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Coding before criteria are distilled and (if unclear) approved | Phase 0 always runs; `--auto` stops exactly there |
| `--auto` as a license to skip validation | The loop ends only on proven criteria; UNVERIFIED = NOT DONE |
| Sequential scout then sequential plan then sequential code on a multi-module goal | `--parallel`: parallel scouts, parallel pipeline stages, parallel lanes |
| Re-implementing from zero what past sessions already built | `--mine` first; read the intent matrix |
| "Implementing" by writing prompts about code | Phase 5 is real execution under cook's gates; prompts are Phase 3 artifacts |
| Retry loops on failure | Phase 6 root-cause loop; a retry is never a fix |

## Related Skills

- `cook` — the execution engine Phases 5 delegates to
- `prompt-forge` — forges the implementation prompt and parallel plan pipelines
- `session-intent` — the mining engine behind Phase 1 / `implement mine`
- `brainstorm` — pre-Phase-0 when the approach itself is undecided
- `validation-plan`, `plan-hardening` — the plan layer
- `root-cause-debugging`, `functional-validation`, `evidence-gates`, `stack-testing` — the proof layer
