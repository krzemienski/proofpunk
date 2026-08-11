---
name: stack-testing
description: Real-system test discipline per stack — pytest/Go/C++/Django/Spring Boot gotchas that cause flaky CI, FastAPI HTTP/SSE testing with curl, Playwright browser automation with server lifecycle management, and condition-based waiting to kill timing flakes. Use when writing, debugging, or deflaking test suites in Python, Go, C++, Django, Spring Boot, or FastAPI projects; when tests pass locally but fail in CI; when browser e2e needs a dev server managed; or when any test uses sleep()/arbitrary timeouts. Enforces the plugin's Iron Rule — mocks chapters in references are for understanding existing suites only; new tests run against the real system.
---

# Stack Testing

Test against the REAL system, per stack. This skill bundles the field-tested
"what goes wrong" knowledge for each major test stack and the browser-e2e
helpers, under one discipline: no mocks for new tests, no arbitrary sleeps,
evidence for every green claim.

## Operating Rules

1. **Iron Rule applies to tests too** — per `../../references/end-user-actor.md`
   and the evidence contract at `../../references/evidence-contract.md`: a green
   test run you did not personally execute is UNVERIFIED. Never claim "tests
   pass" from reading code.
2. **No new mocks/stubs/test doubles.** Several references below document mock
   frameworks (GoogleMock, MockMvc, factory patterns) — those chapters exist to
   help you READ and FIX existing suites. New tests you write hit the real
   database, real server, real browser. Testcontainers-style real services in
   Docker are the gold pattern (see `references/springboot-testing-gotchas.md`).
3. **No `sleep()` in tests.** Replace every arbitrary timeout with condition
   polling — `references/condition-based-waiting.md` is the canonical pattern,
   with `examples/condition_based_waiting.ts`.
4. **Flaky = bug.** A test that "sometimes passes" is a defect in the test or
   the system, never a reason to re-run CI until green. Diagnose per stack
   below; escalate to the `root-cause-debugging` skill when the cause is unclear.
5. **Test output is REGRESSION evidence, never VALIDATION evidence.** Pipe the
   final run to a file and seal it with the `end-user-testing` skill's
   `fresh_evidence.py` — labeled REGRESSION ("the suite is green"). The
   feature-level verdict comes only from driving the live system as the end
   user (`functional-validation`: `curl` for JSON backends, browser for UI,
   simulator for mobile). A green suite cited as proof a feature works is a
   doctrine violation — see `../../references/end-user-actor.md`.

## Reference Routing

| Situation | Read |
|---|---|
| pytest fixture/parametrize/async/coverage weirdness | `references/pytest-gotchas.md` |
| Go `t.Parallel()` races, TestMain, benchmarks, test cache | `references/go-testing-gotchas.md` |
| C++ GoogleTest/CTest, sanitizers, coverage, fuzzing | `references/cpp-testing-gtest.md` |
| Django TestCase vs TransactionTestCase, factory_boy, DRF | `references/django-testing-gotchas.md` |
| Spring Boot Testcontainers, context cache, @Transactional | `references/springboot-testing-gotchas.md` |
| FastAPI/OpenAI-compatible HTTP + SSE endpoints via curl | `references/fastapi-backend-testing.md` |
| Local web app e2e with dev-server lifecycle (Python Playwright) | `references/webapp-testing.md` + `scripts/with_server.py` |
| Full browser automation (multi-viewport, forms, link checks) | `references/playwright-browser-automation.md` + `scripts/playwright/` |
| Any timing flake, race, "works on my machine" | `references/condition-based-waiting.md` |

## Browser E2E Quickstart

```bash
# single dev server + Playwright script, lifecycle managed
python3 scripts/with_server.py --server "npm run dev" --port 5173 \
  -- python3 your_check.py
# richer automation: universal Playwright runner (requires npm i playwright)
cd scripts/playwright && npm install && node run.js --help
```

`examples/` holds reconnaissance-then-action, console-logging, and static-HTML
patterns from the source skills.

## Anti-Patterns

- Writing a mock to "unblock" a failing real dependency → fix the real system.
- Re-running CI to make a flake disappear → diagnose with the stack reference.
- Asserting "tests pass" from a stale terminal scrollback → fresh evidence run.
- Copying fixture patterns between stacks → scoping rules differ per framework;
  read the matching gotchas file FIRST.

## Related Skills (this plugin)

- `functional-validation` — feature-level PASS/FAIL against the real system
- `end-user-testing` — seal test output as fresh run evidence
- `root-cause-debugging` — when a test failure's cause is unclear
- `cook` — implementation loop that these tests gate
