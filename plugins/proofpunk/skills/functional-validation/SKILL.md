---
name: functional-validation
description: >
  Real-system functional validation with the Iron Rule: if the real system
  doesn't work, FIX THE REAL SYSTEM — never mocks, stubs, test doubles, fake
  endpoints, or test-mode bypasses. Detects the platform (iOS, web, browser
  app, API, CLI, Flutter, full-stack), starts the real runtime, exercises
  features through the same interfaces real users experience, captures fresh
  run-scoped evidence, and gates completion on personally reviewed proof.
  Use when asked to validate an app or feature works, verify a fix, test
  end-to-end in a browser or runtime, prove something runs, or before
  marking ANY feature complete — 'does this work?', 'make sure it runs',
  'validate the app functions'. Not for app-wide exhaustive audits (use
  full-functional-audit), repo audits (use codebase-truth-audit), or
  test-suite authoring (use stack-testing).
---

# Functional Validation

## Run checklist

Copy this checklist and track your progress:

- [ ] Detect the platform (iOS / web / API / CLI / Flutter / full-stack)
- [ ] Start the real runtime (no mocks, stubs, or test-mode bypasses)
- [ ] Exercise features through the real user interfaces
- [ ] Capture fresh run-scoped evidence
- [ ] Personally review the proof; fix the real system if it fails

Validate features against the REAL system through REAL interfaces. No mocks,
no stubs, no simulated success.

## The Iron Rule

```
IF the real system doesn't work, FIX THE REAL SYSTEM.
NEVER create mocks, stubs, test doubles, or test files as a substitute.
ALWAYS validate through the same interfaces real users experience.
```

Integration failure sequence: Diagnose -> Fix -> Verify. Nothing else.

**READ `../../references/evidence-contract.md` before starting — it defines
the evidence rules every verdict must satisfy.**
**READ `../../references/end-user-actor.md` — YOU are the actor. You drive the
real system as an end user through MCP/automation tools. Passive 2D review
(screenshots, code reading) is inspection, not verification.**

## Protocol

### Step 0 — Define PASS criteria first

Write 3-5 specific, observable, measurable PASS criteria BEFORE touching the
system. Example: "POST /login with valid credentials returns 200 and a JWT;
the dashboard then renders the user's name." Not: "login works."

### Step 1 — Detect the platform

**LOAD `../../references/platform-routing.md`** and follow its detection
table. Identify: runtime to start, interfaces to exercise, evidence to
capture, and platform-specific traps (iOS status bar, web cache poisoning,
CLI exit codes).

Then LOAD the matching platform runbook — it has the exact
build/launch/interact/capture sequence:

| Platform | Runbook |
|----------|---------|
| iOS/macOS | `references/ios-validation.md` |
| CLI | `references/cli-validation.md` |
| Backend API | `references/api-validation.md` |
| Web frontend | `references/web-validation.md` |
| Full-stack | Load BOTH api + web runbooks |

Load ONLY the runbooks that apply — loading all four wastes context.

### Step 2 — Start the real runtime with real dependencies

Start the dev server, boot the simulator, run the binary, or bring up the
compose stack. Use REAL dependencies: the real database, the real API, the
real filesystem. If a dependency is unavailable, surface the blockage —
never substitute a fake.

If startup fails: BLOCK. Report the startup error verbatim. Do not proceed.

### Step 3 — Exercise the feature as a user would (YOU drive it)

Per the End-User Actor Mandate: YOU personally operate the tools. Do not
delegate the clicking to a subagent and trust its summary; do not conclude
from code or a static screenshot when a tool path exists to act.

| Platform | Interface YOU drive |
|----------|-----------|
| Web | browser automation: navigate, click, fill, submit |
| iOS | simulator: launch, tap, type, deep-link |
| API | `curl -i` with real payloads against live endpoints |
| CLI | invoke the real binary with real arguments |
| Full-stack | one journey crossing every boundary (UI -> API -> DB -> UI) |

Exercise the happy path AND the edge cases: empty input, oversized input,
unauthenticated access, error states. Destructive actions (delete, pay, send)
require explicit user approval BEFORE you perform them.

### Step 4 — Capture fresh evidence

Use the run-scoped convention from the evidence contract:

```
e2e-evidence/run-<ISO-compact>-<slug>/step-NN-<action>-<result>.<ext>
```

The helper `../end-user-testing/scripts/fresh_evidence.py` enforces naming,
freshness, and non-emptiness:

```bash
python3 ../end-user-testing/scripts/fresh_evidence.py init-run login-flow
python3 ../end-user-testing/scripts/fresh_evidence.py next-step submit-credentials
```

### Step 5 — Review the evidence personally

READ every artifact. Describe what you SEE, not what you expected. Grep logs
for errors. Check crash reports. Match each PASS criterion to a specific
citation (full path + what it shows).

### Step 6 — Verdict

```
## Functional Validation — <feature>
PASS criteria (defined in advance): <list>
Driven by: AI as end user via <MCP/automation tools actually used> — <actions actually performed>
Evidence: <run dir>
- [x] <criterion> — evidence: <full path> — <what it shows>
Verdict: PASS | FAIL | BLOCKED | UNVERIFIED (not executed)
```

If any criterion was not verified by an action you actually executed, the
verdict for that criterion is UNVERIFIED — never assumed PASS.

FAIL -> fix the real system -> re-run FROM STEP 2 (partial re-validation
misses regressions). BLOCKED -> surface the blockage; never convert to PASS
by simulating.

## Failure Diagnosis Table

When validation FAILs, diagnose by symptom before touching code:

| Failure | Likely cause | Fix |
|---------|--------------|-----|
| App shows error dialog | Backend down or error handling broken | Read the error text; check backend logs; fix the API or handling |
| Screenshot shows wrong screen | Navigation failed (URL, coordinates, timing) | Fix navigation; increase wait time |
| API returns 500 | Handler crash | Server logs -> stack trace -> fix the handler |
| CLI exits non-zero | Reported error | Read stderr; fix what it names |
| Black/blank screenshot | App hasn't rendered | Increase settle time after launch |
| Data not showing | Backend down or wrong endpoint | Verify backend health; check API prefix |

## Multi-Platform Order

When a change spans layers, validate the deepest dependency FIRST:

```
Database -> Backend API -> Frontend / CLI / Mobile
```

A frontend bug is often a backend bug. Bottom-up isolation prevents fixing
the wrong layer.

## Evidence Quality Standards

| Quality | Example | Why |
|---------|---------|-----|
| Good | Screenshot showing "41 sessions" badge | Proves specific data loaded |
| Bad | Screenshot showing the screen exists | Proves nothing about correctness |
| Good | curl body `{"total": 41, "items": [...]}` | Proves expected data |
| Bad | `200 OK` | Proves the endpoint exists, not that it's correct |
| Good | CLI: `Processed 150 files in 2.3s` | Proves function AND performance |
| Bad | CLI: `Done` | Proves it finished, not that it worked |

## Mock Detection — Red Flags

These thoughts mean you are about to violate the Iron Rule. STOP:

| The thought | Reality |
|-------------|---------|
| "Add a mock fallback for testing" | Mocks test mock behavior. Green light on broken code |
| "A quick unit test to verify" | Unit tests miss integration breaks — API 200 while UI shows "No Data" |
| "Stub the database" | In-memory DBs skip constraints, migrations, real SQL dialect |
| "Real system is too slow/complex" | Then it's too slow for users — that IS the bug |
| "Add a test-mode flag" | Two code paths; the production one breaks untested |
| "Just for local development" | "Just for local" artifacts get committed and deployed |

## NEVER

- NEVER write test files as validation — a passing suite with a broken app
  is worse than no tests
- NEVER cite pytest/JUnit/`go test`/any test-runner output as VALIDATION
  evidence — test runners are regression tooling; validation is `curl`,
  browser, or simulator against the live system only. Framework test clients
  (Flask `test_client` et al.) bypass the network the user experiences —
  regression gate at most, never the verdict
- NEVER mock HTTP clients — mocks don't change when the real API changes
- NEVER use in-memory databases — they accept invalid SQL and skip migrations
- NEVER render components in isolation as validation — integrated behavior
  is the only behavior users see
- NEVER claim PASS without reading the evidence — file existence is not
  verification
- NEVER validate against a "test" configuration — one mode: the one users
  experience
- NEVER skip re-validation after a fix — fixing one thing can break another

## No-Mock Guardrails

Refuse on sight:

| Temptation | Do instead |
|------------|-----------|
| "Mock the API so the UI test passes" | Fix the API or the UI's use of it |
| "Add a test-mode flag that returns canned data" | Seed the real dev database |
| "Stub the failing module" | Diagnose why it fails; fix it |
| "Write a unit test that asserts the mock" | Exercise the real interface |
| "Skip the check, it works locally" | Run it; capture the output |

## Modes (from e2e-validate)

| Mode | Behavior |
|------|----------|
| `--analyze` | inventory features + interfaces, define PASS criteria, no execution |
| `--plan` | produce an ordered validation plan with gates |
| `--execute` | run the plan, capture evidence |
| `--fix` | remediate FAILs against the real system, then re-validate |
| `--audit` | full pass over every feature (see `full-functional-audit`) |
| `--report` | synthesize verdicts into one report |
| `--platform <p>` | override platform detection |
| `--scope <s>` | limit to a feature, flow, or path |
| `--ci` | machine-readable output, non-zero exit on FAIL |

Modes compose: default flow is analyze -> plan -> execute -> (fix) -> report.

## Anti-Patterns

| Pattern | Why wrong | Do this |
|---------|-----------|---------|
| Confirming a screenshot exists without reading it | Screenshot examination is owned by `visual-inspection` | Apply its review protocol — never trust an unread capture |
| PASS criteria written after viewing evidence | Confirmation bias | Criteria first, always |
| `build succeeded` cited as functional evidence | Builds prove compilation, not behavior | Exercise the running feature |
| Reusing last run's screenshot "because nothing changed" | Stale evidence poisons verdicts | Fresh capture every run |
| Happy-path-only validation | Edge cases carry most defects | Empty, overflow, error, unauthenticated states too |
| Faking or skipping validation | Unexecuted validation is not validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim |

## Example

**Input:** User: 'Does the new checkout flow actually work?'

**Output:** The real server is started, the flow is driven in a real browser (cart -> payment -> confirmation), each step evidenced; the promo-code FAIL is fixed in the real system and re-proven.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `end-user-testing` | Steps 4-5 evidence | fresh-evidence rules + fresh_evidence.py helper |
| `visual-inspection` | any screenshot evidence | examination of what the capture actually shows |

Called by: `cook`, `full-functional-audit`, `implement`, `mobile-validation-runner`, `red-team-eval`, `root-cause-debugging`, `ui-experience-audit`.
