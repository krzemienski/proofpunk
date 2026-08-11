---
name: end-user-testing
description: >
  The proof standard for end-user testing: every completion claim is proven
  by driving the real system as the end user, with run-scoped fresh evidence
  (timestamped, sequential, non-empty, never reused across runs), full-path
  citations describing what is SEEN, personally examined proof before any
  task is marked done, cache-clearing before final passes, and refusal to
  PASS without cited artifacts. Includes the fresh_evidence.py helper
  enforcing init-run / next-step / seal / validate. Use when a verdict is
  about to be written, when capturing end-user test evidence, when marking
  tasks complete, or when the user says 'end-user test this', 'capture
  evidence', 'fresh screenshot', 'produce a verdict', or 'prove it's done'.
  Not for writing test suites (use stack-testing) or visual/UX review (use
  visual-inspection or ui-experience-audit).
---

# End-User Testing — The Proof Standard

## Run checklist

Copy this checklist and track your progress:

- [ ] Read the proof obligation (assertion + artifact)
- [ ] Clear caches; preflight and start the real system
- [ ] Drive the system as the end user; capture run-scoped evidence per step
- [ ] Inventory artifacts; personally examine each proof
- [ ] Write the verdict with full-path citations — no artifacts, no PASS

The discipline layer between "work finished" and "work proven". End-user
testing is the only validation: a verdict that cites stale, empty, or
unexamined evidence is invalid, and a task that ran but proved nothing
is not done.

**READ `../../references/evidence-contract.md` — this skill enforces it.**

## The End-User Actor Mandate (canonical — other skills defer here)

This skill owns two rules that every validation-oriented skill in the plugin
applies verbatim instead of re-stating:

1. **The End-User Actor Mandate** — the AI drives the real system itself, as
   the end user: invoke the tools, click the UI, curl the server, run the CLI.
   Marking any validation complete without actually doing this is faking it.
   Unexecuted = UNVERIFIED, always; never upgraded to PASS by assumption.
2. **The fresh-evidence rules** — every proof artifact is run-scoped
   (timestamped run directory), sequential, non-empty, personally examined,
   and never reused across runs; caches are cleared before final passes;
   the evidence directory is sealed with `scripts/fresh_evidence.py`.

When another skill says "apply the Actor Mandate" or "fresh evidence per
`end-user-testing`", it means these two rules and the Six Steps below.

## When This Applies

- A task's proof obligation is about to be executed
- A PASS/FAIL is about to be written anywhere
- A commit is about to happen with no verdict for the current work
- Prior work may have contaminated build caches

## The Six Steps of an End-User Test

### Step 1 — Read the proof obligation

Extract the task's `evidence.assertion`, `evidence.type`,
`evidence.path_template`, `evidence.min_size_bytes` from the plan. If any
are missing, the task is not provable as specified — shrink or re-specify
it before proceeding. (The `validation-plan` and `plan-hardening` skills
author these blocks.)

### Step 2 — Clear stale build caches

Clear caches that can mask regressions — `.next`, `.turbo`, `dist`,
`node_modules/.cache`, `DerivedData`, `__pycache__`, `.pytest_cache`,
`target/`, `build/` — AFTER a dry-run preview and ONLY inside the project
root (`git rev-parse --show-toplevel`). Log the clear operation as
`step-01-cache-clear.log`. Refuse to touch anything outside the project root.

Why: a cached bundle once served correct UI while source on disk was
broken. Never trust a final pass over warm caches.

### Step 3 — Preflight, then start / verify the runtime target

Run the preflight pass from `../../references/preflight-checks.md` FIRST
(project-type detection, environment/toolchain checks, per-platform
sanity checks) so failures are attributed to the work, not to a broken
environment. Then follow `../../references/platform-routing.md` to start
the target. If the target fails to start, report the blockage — do not
simulate.

### Step 4 — Drive the real system yourself, capturing fresh evidence

Per `../../references/end-user-actor.md`: YOU operate the MCP/automation
tools as the end user — click, tap, type, submit — never a passive 2D
check when a tool path exists. Capture into the run-scoped directory with
sequential step names. Enforce min_size_bytes — smaller files are INVALID
evidence; discard and re-capture. The assertion from the proof obligation
is the proof: a test that merely ran without error proves nothing.

### Step 5 — Write the evidence inventory

`evidence-inventory.txt`: every file with byte count, plus a seal line
with timestamp, file count, and total bytes.

### Step 6 — Emit the verdict

```markdown
# End-User Test Verdict — <task_id>
**Verdict:** PASS | FAIL | BLOCKED | UNVERIFIED (steps not executed)
**Run ID:** <run_id>
**Driven by:** AI as end user via <tools actually used> — <actions actually performed>
## PASS criteria (defined in advance)
- [x] <criterion> — evidence: e2e-evidence/<run>/step-NN-....<ext> — <what it shows>
## Evidence inventory
<paste of evidence-inventory.txt>
## Notes
<deviations, risks, follow-ups>
```

A verdict written for steps the AI did not actually execute as the end
user is invalid: mark those criteria UNVERIFIED, never PASS.

A fuller, copy-ready verdict document lives at
`assets/verdict-template.md` — use it for the VALIDATION.md deliverable;
it carries the Driven-by / Actions-executed fields and the UNVERIFIED
status with the rule "never upgrade UNVERIFIED to PASS by assumption".

## Helper Script

`scripts/fresh_evidence.py` enforces the eight fresh-evidence rules — run it (init-run / next-step / seal / validate), never reimplement it by hand. All
operations work against `./e2e-evidence/` in the current working
directory; the active run is the most recent `run-*` subdirectory.

```bash
python3 scripts/fresh_evidence.py init-run <slug>     # create run dir, print run_id
python3 scripts/fresh_evidence.py next-step <slug>    # print next step-NN prefix
python3 scripts/fresh_evidence.py seal                # write evidence-inventory.txt
python3 scripts/fresh_evidence.py validate            # assert freshness + non-emptiness
```

Exit codes: 0 OK, 2 on refusal (bad slug, no active run, stale/empty
artifacts, missing run metadata). `validate` prints `STALE:` / `EMPTY:`
lines for every offending artifact.

## The Verification Loop (every task, every time)

```
1. Worker completes work
2. Worker provides evidence LOCATION
3. YOU personally examine evidence CONTENT
4. YOU match evidence to the pre-defined assertion
5. YOU cite specific proof (full paths, exact output, what is SEEN)
6. ONLY THEN mark the task done
```

Even with parallel workers: workers provide LOCATIONS, you verify
CONTENT. Never trust "X passed" without examining X.

## Refusal Rules

- Refuse to write evidence into `e2e-evidence/` root — always a run subdir.
- Refuse to cite an artifact whose mtime predates the run start.
- Refuse to emit a verdict with an empty inventory.
- Refuse "see evidence directory" citations — demand full paths.
- Refuse "see file" screenshot descriptions — demand what is SEEN.
- Refuse to commit evidence containing tokens, cookies, or secrets.
- Refuse to test an unreachable target — surface the blockage.
- Refuse to delete a prior run's evidence without explicit confirmation.

## Failure Recovery

If you marked something complete prematurely:
1. Acknowledge the error immediately.
2. Re-open the task.
3. Perform the end-user test properly.
4. Document what evidence was actually missing.

## Completion Challenge

"If someone challenged this completion claim, what specific evidence
would I show them?" No citations -> NOT complete.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| "Agent reported 10/10 pass" | Read the actual outputs |
| "Screenshot was captured" | View it; describe what you SEE |
| Reusing a prior task's screenshot | Fresh capture every run |
| Committing a zero-byte PNG | Enforce min size; re-capture |
| Redacting an API body to "{...}" | The body IS the evidence; redact only secrets |
| Final pass over warm caches | Clear caches first, then test |
| A test with no assertion as "proof" | The assertion against the pre-defined threshold IS the proof |
| Marking end-user testing complete without actually driving the system as the end user | Execute the tools yourself; unexecuted = UNVERIFIED |
| Skipping or faking QA/verification steps under any circumstance | Run them or report them UNVERIFIED — no exceptions |


## Example

**Input:** Proof obligation: 'User resets password and lands on dashboard.'

**Output:** init-run -> step-01 screenshot of the reset form -> step-02 video of submit + redirect -> seal -> validate rc=0 -> verdict cites run-2026…/step-02.mp4 by full path.

## Skill calls

Leaf skill — owns canonical methods; calls nothing.

Called by: `codebase-truth-audit`, `cook`, `full-functional-audit`, `functional-validation`, `implement`, `mobile-validation-runner`, `plan-hardening`, `production-readiness`, `red-team-eval`, `root-cause-debugging`, `ui-experience-audit`, `validation-plan`, `visual-inspection`.
