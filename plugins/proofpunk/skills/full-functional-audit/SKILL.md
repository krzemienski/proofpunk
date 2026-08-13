---
name: full-functional-audit
description: >
  App-wide functional audit of a live site or app that inventories EVERY
  user interaction — every screen, page, button, form, link, endpoint, and
  flow — then clicks through everything and validates each one against the
  real running system, remediates failures immediately, and revalidates
  until clean. Five phases: Explore (interaction inventory), Plan, Execute
  (fresh evidence per interaction), Remediate (fix the real system, never
  defer FAILs), Verdict (coverage statement). Use when asked to 'audit the
  whole app', 'click through everything', 'find bugs on this site/URL',
  'test everything', 'full QA sweep', or for pre-release hardening. Not for
  single-feature checks (use functional-validation), per-screen UX review
  (use ui-experience-audit), or one known bug (use root-cause-debugging).
---

# Full Functional Audit

## Run checklist

Copy this checklist and track your progress:

- [ ] Explore: inventory EVERY interaction (screens, buttons, forms, links, endpoints)
- [ ] Plan: assign validation work with resource mutexes
- [ ] Execute: validate each interaction against the real system with fresh evidence
- [ ] Remediate: fix the real system; never defer a FAIL
- [ ] Verdict: final report with coverage statement

Systematic app-wide audit: every interaction exercised against the real
system, every FAIL fixed before the verdict. Nothing deferred.

**READ `../../references/evidence-contract.md` and
`../../references/platform-routing.md` before starting.**

## The Five Phases

```
EXPLORE → PLAN → EXECUTE → REMEDIATE → VERDICT
```

### Phase 1 — EXPLORE: build the interaction inventory

Map the entire application surface:

- **Routes/screens**: every navigable URL, view, or tab
- **Interactions**: every button, form, link, toggle, gesture, upload
- **Endpoints**: every API route with methods and payload shapes
- **Flows**: multi-step journeys (signup, checkout, onboarding, delete)
- **States**: empty, loading, populated, error, unauthenticated, expired-session

Record as a checklist with one row per interaction: `id | surface | action |
expected result | evidence path | verdict`.

The inventory is the audit contract — an interaction missing from the
inventory is an interaction that will silently ship unvalidated.

### Phase 2 — PLAN: assign validation work

Group inventory items into validation batches. Assign **resource mutexes**
so parallel work never corrupts itself:

| Resource | Owner rule |
|----------|-----------|
| Simulator / device | one batch at a time (EXCLUSIVE) |
| Browser session | one batch at a time (EXCLUSIVE) |
| Code edits | EXCLUSIVE — the lead applies fixes |
| Backend dev server / database | read-mostly batches may share; mutating batches serialize |
| Evidence directory | each batch writes its own run-scoped dir |

For large apps (20+ screens), structure the team by platform:

```
iOS:       lead (orchestrator, simulator mutex, applies fixes) + explorer
           (inventory, read-only) + backend-validator (curl, parallel) +
           screen-validator (UI, holds simulator lock)
Web/Full:  lead + explorer + api-validator (curl, parallel-safe) +
           page-validator (browser) + integration-validator (cross-layer:
           frontend actions produce correct backend state)
API-only:  lead + api-validator
```

Whatever the structure: workers provide evidence LOCATIONS, the lead
examines CONTENT — never accept a sub-worker's "PASS" at face value.

Define PASS criteria per item BEFORE execution (observable, measurable).

### Phase 3 — EXECUTE: drive every interaction as the end user

Per `../../references/end-user-actor.md`: every inventory item is DRIVEN by
the agent through MCP/automation tools acting as the end user — not inspected
from screenshots or code. Run each batch against the real system per
`platform-routing.md`:

- YOU click, tap, type, submit through the real interface
- Capture fresh run-scoped evidence from your own driven session
- Mark each item PASS / FAIL / BLOCKED with a full-path citation
- Never skip an item because it "obviously works" — the audit exists to
  catch the ones that obviously work and don't

### Phase 4 — REMEDIATE: fix and revalidate

For every FAIL:

1. Diagnose root cause against the real system
2. Fix the real system (Iron Rule — no mocks, no test-mode branches)
3. Revalidate the failed item AND its blast radius (callers, shared
   contracts, adjacent screens)
4. Only then mark it resolved

**No deferred FAILs.** A FAIL carried into the verdict without a fix is an
audit failure. If a fix is genuinely out of scope, the verdict is FAIL with
the open item listed — never PASS.

### Phase 5 — VERDICT: final report

```markdown
# Full Functional Audit — <app>
Date / run ids / platforms covered
## Coverage
- Interactions inventoried: N
- Validated: N (100% required for PASS)
- Surfaces: <routes, endpoints, flows counts>
- Coverage axes: <light/dark, viewports, states — gaps listed>
## Results
- PASS: n | FAIL: n | BLOCKED: n
## FAIL register
- [id] <interaction> — <root cause> — <fix applied | open> — evidence: <path>
## Verdict
PASS | PASS WITH ISSUES | FAIL | UNVERIFIED — per ../../references/severity-model.md
Behavioral PASS requires that every interaction was actually driven by the
AI as the end user; any interaction not executed is reported UNVERIFIED,
never assumed PASS.
## Evidence index
<run directories>
```

## Orchestration Rules

- **Concurrency cap**: at most a handful of parallel batches; each holds its
  resource mutex exclusively.
- **Evidence isolation**: one run-scoped directory per batch per phase.
- **Regression gate**: after remediation, re-run not just the fixed item but
  every item sharing its resources or contracts.
- **Blast-radius check**: for every fix, walk each caller and shared contract
  before re-marking PASS.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Auditing only the screens the user named | Inventory the whole app, then scope explicitly |
| Marking BLOCKED items as PASS to finish | Verdict is FAIL/BLOCKED with open items listed |
| Fixing a FAIL without revalidating blast radius | Re-run the item + everything sharing its contracts |
| Inventory built from code reading alone | Confirm routes/screens against the running app |
| "99% pass, ship it" | 100% of inventoried interactions validated, or the verdict says otherwise |
| Faking or skipping validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim; unexecuted = UNVERIFIED |

## Example

**Input:** User: 'Audit the whole app at staging.example.com.'

**Output:** An interaction inventory of 63 elements, 63 validations with fresh evidence, 4 FAILs remediated in the real system and revalidated, final verdict with a 100% coverage statement.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `functional-validation` | Phase 3 EXECUTE — every interaction | the per-feature validation engine + Iron Rule |
| `end-user-testing` | all phases | Actor Mandate + evidence sealing |
| `ui-experience-audit` | per-screen UX lens during EXECUTE | heuristic evaluation of flagged screens |
| `root-cause-debugging` | Phase 4 REMEDIATE | root cause of every FAIL before fixing |
| `tui-testing` | auditing TUI apps | PTY driving discipline |

Called by: `production-readiness`.
