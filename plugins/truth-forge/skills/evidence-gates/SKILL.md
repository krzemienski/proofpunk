---
name: evidence-gates
description: >
  Evidence and gate discipline for every completion claim: run-scoped fresh
  evidence (timestamped, sequential, non-empty, never reused across runs),
  full-path citations that describe what is SEEN, personally examined proof
  before marking any gate/task/checkpoint complete, cache-clearing before
  final validation passes, and refusal to PASS without cited artifacts.
  Includes the fresh_evidence.py helper enforcing init-run / next-step /
  seal / validate. Use whenever a verdict is about to be written, when
  capturing validation evidence, when marking gates or phases complete, when
  the user says "capture evidence", "fresh screenshot", "phase gate",
  "produce a verdict", "before advancing", or "prove it's done".
---

# Evidence Gates

The discipline layer between "work finished" and "work proven". A verdict
that cites stale, empty, or unexamined evidence is invalid.

**READ `../../references/evidence-contract.md` — this skill enforces it.**

## When This Applies

- A phase or task is complete and about to advance
- A commit is about to happen with no verdict for the current work
- A PASS/FAIL is about to be written anywhere
- Prior phases may have contaminated build caches

## The Six-Step Phase Gate

For gating a work phase (plan gate, pre-commit gate, pre-advance gate):

### Step 1 — Read the gate criteria

Extract the phase's `evidence.assertion`, `evidence.type`,
`evidence.path_template`, `evidence.min_size_bytes` from the plan. If any are
missing, BLOCK — the phase is not gated. (The `validation-plan` and
`plan-hardening` skills author these blocks.)

### Step 2 — Clear stale build caches

Clear caches that can mask regressions — `.next`, `.turbo`, `dist`,
`node_modules/.cache`, `DerivedData`, `__pycache__`, `.pytest_cache`,
`target/`, `build/` — AFTER a dry-run preview and ONLY inside the project
root (`git rev-parse --show-toplevel`). Log the clear operation as
`step-01-cache-clear.log`. Refuse to touch anything outside the project root.

Why: a cached bundle once served correct UI while source on disk was broken.
Never trust a final pass over warm caches.

### Step 3 — Preflight, then start / verify the runtime target

Run the preflight pass from `../../references/preflight-checks.md` FIRST
(project-type detection, environment/toolchain checks, per-platform
sanity checks) so gate failures are attributed to the work, not to a
broken environment. Then follow `../../references/platform-routing.md`
to start the target. If the target fails to start, BLOCK and report —
do not simulate.

### Step 4 — Drive the real system yourself, capturing fresh evidence

Per `../../references/end-user-actor.md`: YOU operate the MCP/automation
tools as the end user — click, tap, type, submit — never a passive 2D check
when a tool path exists. Capture into the run-scoped directory with
sequential step names. Enforce min_size_bytes — smaller files are INVALID
evidence; discard and re-capture.

### Step 5 — Write the evidence inventory

`evidence-inventory.txt`: every file with byte count, plus a seal line with
timestamp, file count, and total bytes.

### Step 6 — Emit the verdict

```markdown
# Phase Verdict — <phase_id>
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

A verdict written for steps the AI did not actually execute as the end user
is invalid: mark those criteria UNVERIFIED, never PASS.

A fuller, copy-ready verdict document lives at
`assets/verdict-template.md` — use it for the VALIDATION.md deliverable;
it carries the Driven-by / Actions-executed fields and the UNVERIFIED
status with the rule "never upgrade UNVERIFIED to PASS by assumption".

## Helper Script

`scripts/fresh_evidence.py` enforces the eight fresh-evidence rules. All
operations work against `./e2e-evidence/` in the current working directory;
the active run is the most recent `run-*` subdirectory.

```bash
python3 scripts/fresh_evidence.py init-run <slug>     # create run dir, print run_id
python3 scripts/fresh_evidence.py next-step <slug>    # print next step-NN prefix
python3 scripts/fresh_evidence.py seal                # write evidence-inventory.txt
python3 scripts/fresh_evidence.py validate            # assert freshness + non-emptiness
```

Exit codes: 0 OK, 2 on refusal (bad slug, no active run, stale/empty
artifacts, missing run metadata). `validate` prints `STALE:` / `EMPTY:`
lines for every offending artifact.

## The Verification Loop (every gate, every time)

```
1. Worker completes work
2. Worker provides evidence LOCATION
3. YOU personally examine evidence CONTENT
4. YOU match evidence to pre-defined criteria
5. YOU cite specific proof (full paths, exact output, what is SEEN)
6. ONLY THEN mark complete
```

Even with parallel workers: workers provide LOCATIONS, you verify CONTENT.
Never trust "X passed" without examining X.

## Refusal Rules

- Refuse to write evidence into `e2e-evidence/` root — always a run subdir.
- Refuse to cite an artifact whose mtime predates the run start.
- Refuse to emit a verdict with an empty inventory.
- Refuse "see evidence directory" citations — demand full paths.
- Refuse "see file" screenshot descriptions — demand what is SEEN.
- Refuse to commit evidence containing tokens, cookies, or secrets.
- Refuse to validate an unreachable target — surface the blockage.
- Refuse to delete a prior run's evidence without explicit confirmation.

## Failure Recovery

If you marked something complete prematurely:
1. Acknowledge the error immediately.
2. Re-open the task/gate.
3. Perform proper verification.
4. Document what evidence was actually missing.

## Completion Challenge

"If someone challenged this completion claim, what specific evidence would I
show them?" No citations -> NOT complete.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| "Agent reported 10/10 pass" | Read the actual outputs |
| "Screenshot was captured" | View it; describe what you SEE |
| Reusing a prior phase's screenshot | Fresh capture every run |
| Committing a zero-byte PNG | Enforce min size; re-capture |
| Redacting an API body to "{...}" | The body IS the evidence; redact only secrets |
| Final validation over warm caches | Clear caches first, then validate |
| Marking validation complete without the AI actually invoking MCP/automation tools and acting as the end user | Execute the tools yourself; unexecuted = UNVERIFIED |
| Skipping or faking QA/verification steps under any circumstance | Run them or report them UNVERIFIED — no exceptions |
## Related Skills

- `functional-validation` — produces the evidence this skill gates on
- `validation-plan` / `plan-hardening` — author the gate blocks this skill executes
- `visual-inspection` / `ui-experience-audit` — review screenshot evidence quality
- `../../references/ci-gates.md` — P0/P1/P2 classification and rollout order
  for wiring these gates into CI; evidence gates are the runtime contract,
  CI gates are the automation of that contract
