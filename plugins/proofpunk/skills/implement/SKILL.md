---
name: implement
description: >
  The single write path: scouts the real codebase (mandatory, subagents)
  distills TRUE success criteria, mines past sessions (session-intent)
  forges the build prompt (prompt-forge), decomposes into a task graph where
  every task carries a proof obligation, then runs the execution loop —
  implement a task, drive the finished feature as the end user immediately
  record the proof — until every criterion is proven. End-user validation is
  an inline phase of every task, not an optional skill: the real runtime gets
  driven as the end user, always, with fresh run-scoped evidence. Never
  writes test files; validation is the completed user job. Flags: --parallel
  (executable lane contracts), --auto (never stops until proven), --mine
  --fast. Use when asked to 'implement X', 'build X end to end', 'ship X'
  'make X work', 'use all the skills to ship this', or to execute a plan
  against a real codebase. Not for planning without building (use
  validation-plan) or ideation (use brainstorm).
---

# Implement — The Single Write Path

## Run checklist

Copy this checklist and track your progress:

- [ ] Distill TRUE success criteria (user approval if unclear)
- [ ] SCOUT the real codebase with subagents (mandatory — never skipped)
- [ ] MINE past sessions; FORGE the build prompt; DECOMPOSE the task graph
- [ ] EXECUTE loop: task → end-user validation (inline) → proof in the ledger
- [ ] Stuck protocol on any unproven task (attempt, root-cause ×3, split, escalate)
- [ ] REPORT from the execution ledger

One command that runs the whole build: scout, mine, forge, decompose
implement, drive-as-end-user, prove — tracked as a live execution ledger
from the first task to the last proof.

## The Execution Doctrine — four laws

1. **The unit of progress is the task.** A task is DONE only when its
   end-user validation has produced proof.
2. **End-user validation is the only proof. Always.** Driving the real
   system as the end user is how anything gets proven. A task that ran but
   proved nothing is not done. There are no test files in this pipeline:
   if you are about to write one, you are off the path — go drive the real
   thing instead.
3. **The plan is a living task list.** Tasks split when stuck, appear when
   scouts discover work, and complete only with proof attached.
4. **The loop always knows its next action.** No dead stops; only a
   decision a human must make may halt the run.

## Command Surface

```
implement "<goal>" [--parallel] [--auto] [--mine] [--fast]
implement mine [--project DIR] [--since DATE] [--until DATE] [--json]
```

| Flag | Effect |
|------|--------|
| `--parallel` | Scouts fan out; the build splits into lanes by module boundary — each lane bound by an executable lane contract, conformance proven by end-user validation |
| `--auto` | Never stops until every TRUE criterion is proven; unclear criteria escalate before any code — the one mandatory stop |
| `--mine` | Run session mining first (never skipped with this flag) |
| `--fast` | Skip the research sub-step (known territory, known stack) |

Unknown flags are rejected with this table, never silently ignored.
(`--no-test` / `--tdd` no longer exist — the pipeline never writes test
files; projects with existing suites keep them as a regression concern
owned outside this skill.)

## Stage 0 — Distill the TRUE success criteria (always first)

A TRUE criterion is **observable** (checkable from outside the code)
**end-user provable** (drivable as the end user), and **measurable**
(pass/fail threshold in numbers or exact strings). Unclear criteria
escalate for approval before any code. Record the approved criteria
verbatim in the execution ledger; the final report grades against exactly
these.

## Stage 1 — MINE (session-intent)

With `--mine`, or when the goal smells like past work, mine previous
sessions via `session-intent`. Output: a previous-implementations matrix
feeding the scouts (where past runs touched) and the forge (what framing
worked). `implement mine` alone prints only the matrix.

## Stage 2 — SCOUT (mandatory, subagents)

**The codebase walk happens before any edit, every time.** This stage is
never skipped and never performed from memory — subagents walk the real
tree. (With `--fast`, the scout is a single quick pass, not zero passes.)

| Scout | Question |
|-------|----------|
| Structure | project type, modules, entry points |
| Patterns | conventions of similar features — code must match them |
| Contracts | public APIs, schemas, env vars the goal could touch |
| History | what Stage 1's matrix flagged as past touchpoints |

Synthesize one 3-6 bullet context summary. Contradictions resolve against
the actual code, never by vote. Every scout runs in its own subagent
context and returns a summary; the main session never trusts a summary it
cannot tie to files the scout names.

This stage **calls `brainstorm`** — its GATE 2 (scout-first) and GATE 3
(exact requirements) govern what the scouts extract and when questions may
be asked.

## Stage 3 — FORGE (prompt-forge)

Author the build prompt with prompt-forge AUTHOR mode on the canonical XML
skeleton — including `<sequential_thinking>`, `<todos>`, `<authorization>`
`<output_contract>` (exact file paths the run must produce, starting with
the execution ledger), and `<validation>` (the end-user validation per
criterion). The Stage 0 criteria become the prompt's success metrics
verbatim.

## Stage 4 — DECOMPOSE into the task graph

Every task is created with a **proof obligation** — written before the task
starts (the PO-N format is owned by `validation-plan`; the cumulative-proof
rule is its canonical definition):

```
task:
  id: T3
  scope: cart total includes tax
  depends_on: [T1]
  proof_obligation:
    end_user_validation: POST /cart/items with a taxable item, then GET /cart
    assertion: response.total == response.subtotal + response.tax AND response.tax > 0
    artifact: execution-ledger entry + response body capture
```

A task is **READY** when every task it depends on is PROVEN. A task is
**DONE** only when its proof obligation is satisfied and the artifact is
recorded in the ledger.

## Stage 5 — EXECUTE the loop

```
while any task is not DONE:
    task = highest-priority READY task
    implement task                    # production code only, following scout-found patterns
    run task.proof_obligation         # END-USER VALIDATION, immediately, inline (below)
    if proof produced:  mark DONE, record artifact in the ledger
    else:               enter the stuck protocol
    update the regression posture     # existing suites, if any, still pass
```

### End-user validation is inline — not a skill you can skip

After every task, immediately drive the finished feature as the end user:

1. **Criteria first** — the task's assertion was written at Stage 4; it is
   the proof. A run that merely "didn't error" proves nothing.
2. **Detect the platform** via `../../references/platform-routing.md`;
   load only the matching runbook:
   `../../references/api-validation.md` (backend), `web-validation.md`
   (browser), `cli-validation.md` (CLI), `ios-validation.md` (simulator);
   TUI targets follow the `tui-testing` discipline verbatim.
3. **Start the real runtime** with real dependencies. Startup failure =
   BLOCK, report verbatim, never substitute a fake.
4. **YOU drive it** — browser clicks, real `curl` payloads, the real
   binary, the real simulator. Exercise the happy path AND edge cases.
   Destructive actions require explicit user approval first.
5. **Fresh run-scoped evidence** per the evidence contract — the proof standard (Six Steps, Actor Mandate, sealing) is owned by `end-user-testing` and applied verbatim here.

   (`e2e-evidence/run-<ISO>-<slug>/step-NN-…`); review every artifact
   personally — describe what you SEE.
6. **Verdict per criterion**: PASS with full-path citation, or
   FAIL/BLOCKED/UNVERIFIED with the reason. FAIL → fix the real system →
   re-drive from step 3.

**The Iron Rule applies to every task:** if the real system doesn't work
fix the real system — never mocks, stubs, test doubles, fake endpoints, or
test-mode bypasses. Never write a test file as validation; never cite a
test runner as proof. Existing project suites are a regression concern and
stay green, but they prove nothing here.

**With `--parallel`**: lanes run concurrently, each its own todo chain.
Before lanes start, the orchestrator writes a **lane contract** per
boundary — an executable file stating the exact public interface each lane
may expose and consume. Every lane's end-user validation includes
conformance against that file, so a merge conflict surfaces as a failed
validation with evidence, not a review debate.

## Stage 6 — The stuck protocol

1. **Attempt** the obvious fix once.
2. **Root-cause loop** (max 3 hypotheses) via `root-cause-debugging` —
   reproduce, minimize, instrument; fix the cause, never the symptom.
3. **Split** the task into smaller provable tasks.
4. **Escalate** with a structured blocker report. Only decisions a human
   must make reach this rung. Under `--auto`, rungs 1-3 never stop the run.

Authorization boundaries are escalation triggers: the loop routes to rung
4, never silently proceeds and never silently stops.

## Stage 7 — REPORT from the ledger

- **Criteria-proof table**: criterion (verbatim) | end-user validation run | artifact | PASS / FAIL / UNVERIFIED
- **Task ledger**: every task, its proof obligation, its artifact
- **Todo ledger**: everything done, everything pending and why

## The execution ledger (`.planning/execution-ledger.json`)

The run's single source of truth, updated live. An interrupted run resumes
from the ledger: DONE tasks with artifacts are kept, everything else
re-enters the loop.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Gate-thinking ("passed review, now we may code") | Execution-thinking: tasks run when READY, complete when PROVEN |
| Validation as a phase at the end | End-user validation immediately after every task; report = aggregation |
| Writing a test file to "verify" | Never — drive the real feature as the end user |
| Marking a task done because it ran | Done = proof obligation produced an artifact |
| Parallel lanes merging on trust | Lane contracts as executable files; conformance is end-user validated |
| Editing before scouting | Stage 2 is mandatory; scouts walk the real tree first |
| Re-implementing what past sessions built | `--mine` first; read the intent matrix |

## Measured additions (carried from the implement merger, 2026-08-12)

1. **Never mutate a running artifact.** Edit, then re-launch.
2. **One driver per shared target.** Kill prior drivers; destroy sessions
   you created.
3. **Push before you optimize.** Harness and drivers belong in the repo.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `session-intent` | Stage 1 MINE | prior implementations + intent of similar past work |
| `brainstorm` | Stage 2 SCOUT | scout-first rule + exact-requirements gates applied to the goal |
| `prompt-forge` | Stage 3 FORGE | the build prompt on the canonical XML skeleton |
| `validation-plan` | Stage 4 DECOMPOSE | task-graph + proof-obligation XML format |
| `end-user-testing` | Stage 5 proof of every task | the proof standard, Six Steps, fresh-evidence sealing |
| `tui-testing` | Stage 5 when the target is a TUI | PTY driving discipline |
| `root-cause-debugging` | Stage 6 stuck protocol rung 2 | root cause of any unproven task |

The platform runbooks (`api/web/cli/ios-validation.md`) are shared doctrine
in `references/`, not a skill — Stage 5 loads them directly.

Called by: nothing — the top of the write path.
skill defers to it; nothing defers into it.
