# The execution loop — Stages 5-7 in full

Loaded on demand by `implement`'s Stage 5. `SKILL.md` carries the loop's
shape; this file carries the detail you need only once you are inside it.

## Stage 5 — EXECUTE

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
2. **Detect the platform** via `../../../references/platform-routing.md`;
   load only the matching runbook:
   `../../../references/api-validation.md` (backend), `web-validation.md`
   (browser), `cli-validation.md` (CLI), `ios-validation.md` (simulator);
   TUI targets follow the `tui-testing` discipline verbatim.
3. **Start the real runtime** with real dependencies. Startup failure =
   BLOCK, report verbatim, never substitute a fake.
4. **YOU drive it** — browser clicks, real `curl` payloads, the real
   binary, the real simulator. Exercise the happy path AND edge cases.
   Destructive actions require explicit user approval first.
5. **Fresh run-scoped evidence** per the evidence contract — the proof
   standard (Six Steps, Actor Mandate, sealing) is owned by
   `end-user-testing` and applied verbatim here
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

### `--parallel` lane contracts

Lanes run concurrently, each its own todo chain. Before lanes start, the
orchestrator writes a **lane contract** per boundary — an executable file
stating the exact public interface each lane may expose and consume, plus
two more binding fields: which ACQUIRE digest file that lane consumes
(conforming to `../../../references/docs-acquisition.md`), and which
`references/*-validation.md` runbook that lane's proof obligation must use.

Both new fields are resolvable paths, never placeholders. Every lane's
end-user validation includes conformance against all three fields, so a
merge conflict on the interface — or a cross-lane assumption mismatch, two
lanes silently building against different hosts, or one validating with the
wrong runbook — surfaces as a failed validation with evidence, not a review
debate.

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

## Measured additions (carried from the implement merger, 2026-08-12)

1. **Never mutate a running artifact.** Edit, then re-launch.
2. **One driver per shared target.** Kill prior drivers; destroy sessions
   you created.
3. **Push before you optimize.** Harness and drivers belong in the repo.
