---
name: mobile-validation-runner
description: >
  Drive and validate iOS apps end-to-end on real simulators — five-phase
  SETUP, RECORD, ACT, COLLECT, VERIFY protocol with video recording, log
  streaming, and screenshot evidence; three-facet validation checkpoints
  (simulator + backend + log analysis); xcrun simctl device control; XC-MCP
  accessibility-first UI automation; Expo/React Native simulator workflows;
  preflight environment checks. Use when validating an iOS or Expo feature,
  marking any mobile task complete, booting/controlling simulators,
  capturing mobile UI evidence, or debugging Metro/simulator issues.
  Unexecuted mobile validation is UNVERIFIED, never done. Not for web,
  desktop, or API validation (use functional-validation) or non-iOS test
  suites (use stack-testing).
---

# Mobile Validation Runner

## Run checklist

Copy this checklist and track your progress:

- [ ] SETUP: preflight environment, boot simulator, install build
- [ ] RECORD: start video + log streaming
- [ ] ACT: drive the feature via accessibility-first UI automation
- [ ] COLLECT: screenshots, video, logs, backend traces
- [ ] VERIFY: three-facet checkpoints (simulator + backend + logs) — unexecuted = UNVERIFIED

The End-User Actor Mandate applied to mobile: you personally boot the
simulator, install the build, drive the UI, and collect the evidence —
or the feature is UNVERIFIED. See `../../references/end-user-actor.md`.

## Core Protocol (non-negotiable)

Five phases, from `references/ios-validation-runner.md`:

1. **SETUP** — preflight the environment (`references/preflight.md`: Xcode,
   simctl, dev server, disk), boot a clean simulator, start the backend.
2. **RECORD** — start video recording + log streaming BEFORE acting.
3. **ACT** — drive the feature as the end user: taps, typing, gestures,
   navigation. Prefer accessibility-driven interaction (XC-MCP) over blind
   coordinates; fall back to coordinates only when the a11y tree is empty.
4. **COLLECT** — screenshots at every state change, stop recording, pull
   crash logs and app/syslog output.
5. **VERIFY** — the three-facet gate (`references/ios-validation-gate.md`):
   simulator evidence + backend health/endpoint proof + log correlation.
   All three must agree before any completion claim.

Seal the evidence directory with the `end-user-testing` skill's
`fresh_evidence.py` (init-run → capture → seal → validate).

## Reference Routing

| Situation | Read |
|---|---|
| Full validation run with recording + gates | `references/ios-validation-runner.md` (+ `scripts/validate.sh`) |
| Completion gate enforcement | `references/ios-validation-gate.md` |
| Raw device control: boot/install/launch/screenshot/logs | `references/ios-simulator-control.md`, `references/simctl-command-reference.md` (+ `scripts/simulator.sh`) |
| Xcode builds, a11y-first UI automation, caching | `references/xc-mcp.md` + `references/xc-mcp-tool-reference.md` (+ `scripts/xc_mcp_wrapper.sh`); workflows: `references/xc-mcp-workflow-build-project.md` (build), `references/xc-mcp-workflow-run-tests.md` (test), `references/xc-mcp-workflow-ui-automation.md` (a11y-first UI), `references/xc-mcp-workflow-app-deployment.md` (deploy), `references/xc-mcp-workflow-fresh-install.md` (fresh install), `references/xc-mcp-workflow-simulator-management.md` (simulators), `references/xc-mcp-workflow-debug-failures.md` (failures), `references/xc-mcp-workflow-configure-caching.md` (caching setup) |
| Expo / React Native end-to-end | `references/expo-e2e-testing-workflow.md` (comprehensive), `references/expo-testing-workflow.md` (idb coordinate lane) |
| Session start / "environment feels wrong" | `references/preflight.md` |

## Platform Notes

- **iOS coverage is complete** (simctl + XC-MCP + idb lanes are all bundled).
- **Android**: the two Android verification sources (`android_ui_verification`,
  `android-ui-journey-testing`) were present only in the original skills.zip,
  which is no longer accessible — Android guidance is therefore NOT bundled and
  must not be improvised from memory; flag it as a gap if a task needs it.
- XC-MCP and idb are external tools; if unavailable, `scripts/simulator.sh` — run it to cover
  the simctl-only lane and BLOCKED beats simulated results.

## Anti-Patterns

- Screenshot-only "validation" without driving the UI → inspection, not proof.
- Marking a mobile task done from a successful BUILD → build success proves
  compilation, nothing else.
- Skipping log correlation because the UI "looked right" → silent crashes and
  failed backend calls hide exactly there.
- Reusing screenshots from a previous run → violates fresh evidence.


## Bundled resources

- `scripts/example.sh` — runnable end-to-end example session (boot, build, record, validate). Run it as a smoke test of the protocol.
- `references/xc-mcp-operation-enums.md` — read when a tool call needs an exact operation/enum value.
- `references/xc-mcp-accessibility-patterns.md` — read before writing accessibility-first UI automation.
- `references/xc-mcp-mcp-configuration.md` — read when configuring the XC-MCP server itself.
- `references/xc-mcp-progressive-disclosure.md` — read for token-efficient XC-MCP usage patterns.
- `references/xc-mcp-caching-strategy.md` — read when build/simulator caching behaves unexpectedly.

## Example

**Input:** User: 'Validate the new onboarding on iPhone 16 simulator.'

**Output:** SETUP boots the simulator and installs the build, RECORD captures video, ACT walks 5 onboarding screens via accessibility queries, COLLECT pulls logs, VERIFY passes all three facets with video evidence.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `end-user-testing` | COLLECT/VERIFY sealing | fresh-evidence sealing of the run directory |
| `visual-inspection` | every captured screenshot | audit before trusting it |
| `functional-validation` | backend facet | the web/API equivalent checks |
