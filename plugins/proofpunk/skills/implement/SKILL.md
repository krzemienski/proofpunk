---
name: implement
description: >
  Execution-first implementation orchestrator: distills TRUE success
  criteria, mines past sessions (session-intent), explores with parallel
  scouts, forges the build prompt (prompt-forge), decomposes into a task
  graph where every task carries a proof obligation, then runs the execution
  loop — execute a task, end-user test it immediately, record the proof —
  until every criterion is proven. End-user testing is the only validation,
  always. Flags: --parallel (executable lane contracts), --auto (never stops
  until proven), --mine, --fast, --no-test, --tdd. Use when asked to
  'implement X', 'build X end to end', 'use all the skills to ship this', or
  to re-run how past sessions implemented similar goals. Not for scoped
  single features without orchestration (use cook) or planning without
  building (use validation-plan).
---

# Implement — Execution-First Orchestration

## Run checklist

Copy this checklist and track your progress:

- [ ] Distill TRUE success criteria (user approval if unclear)
- [ ] MINE past sessions and EXPLORE the codebase with scouts
- [ ] FORGE the build prompt; DECOMPOSE into a task graph with proof obligations
- [ ] EXECUTE loop: task -> end-user test -> record proof in the ledger
- [ ] Stuck protocol on any unproven task (attempt, root-cause x3, split, escalate)
- [ ] REPORT from the execution ledger

One command that runs the whole build: mine, explore, forge, decompose,
execute, prove — tracked as a live execution ledger from the first task
to the last proof.

**Relationship to `cook`**: implement is the orchestrator; cook is the
execution engine it delegates single-lane builds to. Both share the same
doctrine: tasks execute to completion, and completion is proven by
end-user testing.

## The Execution Doctrine — four laws

1. **The unit of progress is the task.** Not the phase, not the gate.
   A task is DONE only when its end-user test has produced proof.
2. **End-user testing is the only validation. Always.** Driving the real
   system as the end user is how anything gets proven. Test suites are
   the regression rail — they protect proven work, they never prove it.
3. **The plan is a living task list, not a gate you pass once.** Execution
   updates it: tasks split when they get stuck, appear when scouts
   discover work, and complete only with proof attached.
4. **The loop always knows its next action.** No dead stops. When a task
   cannot advance, the stuck protocol names the next action — and only a
   decision a human must make may halt the run.

## Command Surface

```
implement "<goal>" [--parallel] [--auto] [--mine] [--fast] [--no-test] [--tdd]
implement mine [--project DIR] [--since DATE] [--until DATE] [--json]
```

| Flag | Effect | Why it exists |
|------|--------|---------------|
| `--parallel` | Parallel everywhere: scouts fan out, the plan is forged as a `.prompts/` pipeline whose independent stages run in parallel, and the build splits into lanes by module boundary — each lane bound by an executable lane contract | wall-clock speed on multi-module goals |
| `--auto` | Never stops until every TRUE criterion is proven. Criteria are distilled FIRST; if they are unclear, the run escalates for approval before any code — that escalation is the one mandatory stop. Everything else the stuck protocol handles without stopping | unattended runs with a real finish line |
| `--mine` | Run session mining first (never skipped with this flag) | reuse how past sessions actually built similar things |
| `--fast` | Skip the research sub-step (passed to cook's fast mode) | known territory, known stack |
| `--no-test` | Downgrades the *regression rail* (automated suites) to a warning the user must accept. End-user testing is never downgraded — it is the only proof there is | environments with no runnable suite |
| `--tdd` | Tests-first per task (rail written before the task's code) | refactor-heavy goals |

Unknown flags are rejected with this table, never silently ignored.

## Stage 0 — Distill the TRUE success criteria (always first)

Before mining, exploring, or coding, distill the success criteria. A
TRUE criterion is:

1. **Observable** — checkable from outside the code (response body,
   screen state, file on disk, exit code), not "the code handles it"
2. **End-user provable** — provable by driving the real system as the
   end user per `../../references/end-user-actor.md`
3. **Measurable** — a pass/fail threshold in numbers or exact strings

If the goal is unclear or the distillation required unstated assumptions,
**escalate**: present the distilled criteria and get explicit approval
before any code. This is an escalation for a decision only a human can
make — not a review gate — and under `--auto` it is the one mandatory
stop. Record the approved criteria verbatim in the execution ledger; the
final report grades against exactly these.

## Stage 1 — MINE (session-intent)

With `--mine`, or when the goal smells like past work, mine previous
sessions via `session-intent`: past implementation sessions, the intent
behind their prompts, files touched, commits. Output: a previous-
implementations matrix feeding Stage 2 (where past runs touched) and
Stage 3 (what framing worked). `implement mine` alone prints only the
matrix — reconnaissance, no build.

## Stage 2 — EXPLORE (parallel scout agents)

| Scout | Question |
|-------|----------|
| Structure | project type, modules, entry points |
| Patterns | conventions of similar features — code must match them |
| Contracts | public APIs, schemas, env vars the goal could touch |
| History | what Stage 1's matrix flagged as past touchpoints |

Synthesize one 3-6 bullet context summary. Contradictions resolve against
the actual code, never by vote.

This stage **calls `brainstorm`** — its GATE 2 (scout-first) and GATE 3
(exact requirements) govern what the scouts extract and when questions may
be asked. Apply that skill's rules verbatim; they are not repeated here.

## Stage 3 — FORGE (prompt-forge)

Author the build prompt with prompt-forge AUTHOR mode on the canonical
XML skeleton — including `<sequential_thinking>`, `<todos>`,
`<authorization>`, `<output_contract>` (exact file paths the run must
produce, starting with the execution ledger), and `<validation>` (the
end-user test per criterion). The Stage 0 criteria become the prompt's
success metrics verbatim.

## Stage 4 — DECOMPOSE into the task graph

Break the goal into tasks. **Every task is created with a proof
obligation** — written before the task starts. This stage **calls
`validation-plan`** — the proof-obligation format (PO-N) and the
cumulative-proof rule are its canonical definitions, applied here
verbatim:

```
task:
  id: T3
  scope: cart total includes tax
  depends_on: [T1]
  proof_obligation:
    end_user_test: POST /cart/items with a taxable item, then GET /cart
    assertion: response.total == response.subtotal + response.tax AND response.tax > 0
    artifact: execution-ledger entry + response body capture
```

A task is **READY** when every task it depends on is PROVEN. A task is
**DONE** only when its proof obligation is satisfied and the artifact is
recorded in the ledger. A task without a writable proof obligation is a
specification bug: shrink it until the obligation is writable.

## Stage 5 — EXECUTE the loop

```
while any task is not DONE:
    task = highest-priority READY task
    execute task                    # real code, real system — no mocks
    run task.proof_obligation       # end-user test, immediately
    if proof produced:  mark DONE, record artifact in the ledger
    else:               enter the stuck protocol
    update the regression rail      # suites protect proven work
```

This stage **calls `cook`** (the per-task execution contract) and
**`end-user-testing`** (the proof executed after every task — Six Steps,
Actor Mandate, sealed fresh evidence).

The end-user test runs **immediately after each task**, not in a
validation phase at the end. Integration failures surface while the
context that caused them is still loaded, and the final report is an
aggregation of per-task proofs — never a fresh round of testing
reconstructed from memory.

**With `--parallel`**: lanes run concurrently, each its own todo chain.
Before lanes start, the orchestrator writes a **lane contract** per
boundary — a file stating the exact public interface each lane may
expose and consume. Every lane's end-user tests include conformance
against that file, so a merge conflict surfaces as a failed end-user
test with evidence, not a review debate.

## Stage 6 — The stuck protocol (replaces retry loops and dead stops)

When a task's proof fails, the loop climbs a bounded ladder:

1. **Attempt** the obvious fix once.
2. **Root-cause loop** (max 3 hypotheses) via `root-cause-debugging`:
   reproduce, minimize, instrument; fix the cause, never the symptom.
3. **Split** the task into smaller tasks, each with its own writable
   proof obligation; a task that cannot be proven can almost always be
   divided into tasks that can.
4. **Escalate** to the user with a structured blocker report: what was
   tried (with evidence), the root cause found or ruled out, the exact
   decision needed. Only decisions a human must make — destructive
   operations, out-of-scope edits, secrets, ambiguous criteria — reach
   this rung. Under `--auto`, rungs 1-3 never stop the run.

Authorization boundaries (destructive operations, edits outside the
approved scope, credentials) are escalation triggers, not gates: the
loop routes to rung 4, it never silently proceeds and never silently
stops.

## Stage 7 — REPORT from the ledger

The report is generated FROM the execution ledger, not reconstructed:

- **Criteria-proof table**: criterion (verbatim from Stage 0) | end-user
  test run | artifact | PASS / FAIL / UNVERIFIED
- **Task ledger**: every task, its proof obligation, its artifact
- **Todo ledger**: everything done, everything pending and why

## The execution ledger (`.planning/execution-ledger.json`)

The run's single source of truth, updated live as tasks complete:

```json
{
  "goal": "…", "criteria": ["…verbatim…"],
  "tasks": [{"id": "T3", "scope": "…", "depends_on": ["T1"],
             "proof_obligation": {"end_user_test": "…", "assertion": "…"},
             "status": "done", "artifact": ".planning/evidence/T3-response.json"}],
  "escalations": [{"task": "T4", "rung": 4, "decision_needed": "…"}]
}
```

An interrupted run resumes from the ledger: DONE tasks with artifacts
are kept, everything else re-enters the loop. `--auto` long runs are
therefore resumable, and the Stage 7 report is a render of this file.

## The end-user testing proof standard

"Prove something" has a precise meaning here, and it is **owned by the
`end-user-testing` skill** — its Six Steps, the End-User Actor Mandate,
and the fresh-evidence rules apply verbatim to every task proof in the
execution loop. Read its SKILL.md at Stage 5; do not improvise a local
variant. The assertion itself (observable vs the criterion's stated
threshold, defined in advance) is written into each task's proof
obligation at Stage 4, in the `validation-plan` format.

Test runners (pytest, jest, go test) are the regression rail: they run
after proof to protect it. They are never the validation itself.

## Execution discipline (all stages)

- Every stage, task, and parallel lane is a todo; exactly one in progress
  per lane; completed immediately when proven; the ledger is read back
  before the report
- Sequential thinking per prompt-forge 0.1 at every stage transition:
  numbered steps, revisions stated, branches justified

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Gate-thinking: "passed review, so we may now code/test" | Execution-thinking: tasks run when READY, complete when PROVEN |
| Validation as a phase at the end | End-user testing immediately after every task; report = aggregation |
| Marking a task done because it ran | A task is done when its proof obligation produced an artifact |
| A test with no assertion as "proof" | Assertions against the criterion's threshold are the proof |
| Retry loops on failure | The stuck protocol: attempt, root-cause, split, escalate |
| `--auto` as a license to skip proof | `--auto` ends only when every criterion is proven; UNVERIFIED = NOT DONE |
| Parallel lanes merging on trust | Lane contracts as executable files; conformance is end-user tested |
| Re-implementing what past sessions built | `--mine` first; read the intent matrix |

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `session-intent` | Stage 1 MINE | prior implementations + intent of similar past work |
| `brainstorm` | Stage 2 EXPLORE | scout-first rule + exact-requirements gates applied to the goal |
| `prompt-forge` | Stage 3 FORGE | the build prompt on the canonical XML skeleton |
| `validation-plan` | Stage 4 DECOMPOSE | task-graph + proof-obligation XML format |
| `cook` | Stage 5 EXECUTE | per-task execution semantics (the loop contract) |
| `end-user-testing` | Stage 5 proof of every task | Six Steps, Actor Mandate, fresh-evidence sealing |
| `functional-validation` | Stage 5 driving web/API/CLI runtimes | platform detection + real-runtime driving |
| `root-cause-debugging` | Stage 6 stuck protocol rung 2 | root cause of any unproven task |
| `stack-testing` | regression rail after proof | per-stack test discipline protecting proven work |
