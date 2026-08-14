# UI Experience Audit — <SCREEN_NAME>

**Tier:** Skim | Standard | Deep
**Mode:** identify-and-delegate | drive-interaction
**Platform:** iOS | macOS | web | cross-platform (RN / Flutter / Expo)
**Auditor:** <name or "Claude (skill: ui-experience-audit)">
**Date:** <YYYY-MM-DD>
**Actions executed by AI as end user:** <list of tools + actions actually
performed, e.g. "browser MCP: clicked Save, submitted empty form, navigated
back" — or "none (no tool path available)">

## Evidence reviewed

- <path/to/screenshot1.png>
- <path/to/screenshot2.png>
- (additional artifacts: DOM snapshots, accessibility trees, recordings)

## Coverage

<!-- List every viewport × color-scheme × state combination captured -->
<!-- Mark gaps explicitly so the verdict can route correctly -->

| Viewport | Light mode | Dark mode | Empty state | Error state | Overflow state |
|----------|------------|-----------|-------------|-------------|----------------|
| mobile-s |     ✓      |     ✗     |      ✗      |      ✗      |       ✗        |
| mobile-m |     ✓      |     ✓     |      ✓      |      ✗      |       ✗        |
| tablet   |     ✗      |     ✗     |      ✗      |      ✗      |       ✗        |
| desktop  |     ✓      |     ✓     |      ✓      |      ✓      |       ✓        |

**Coverage gaps:** <list — these will route the verdict to LIMITED COVERAGE if no CRITICAL/HIGH findings>

## PASS criteria (defined before viewing evidence)

<!-- Anti-confirmation-bias rule: write down 3–5 specific things that would make this screen pass, BEFORE you open the screenshot. Then audit against this list, not vibes. -->

1.
2.
3.

---

## Phase 0 — Triage

<!-- 30-second show-stopper scan. Lorem ipsum, broken images, missing chart bars, error banners, console errors visible, blank-but-bordered containers. -->

- [SEVERITY] [TRIAGE_CATEGORY] — <what you see> — <suggested fix>

(or: "No triage-level issues" if clean)

## Phase 1 — Visual Defects

<!-- Universal checklist + platform-specific (iOS HIG / WCAG 2.2). Use the per-viewport tag if multiple viewports were audited. -->

- [SEVERITY] [VIEWPORT_TAG] [CHECKLIST_ITEM] — <what you see> — <suggested fix>

## Phase 2 — Interactive Elements

**Inventory:** <N> action items

| ID | Position | Type | Label | Signifier | Affordance match | Target size | Verdict |
|----|----------|------|-------|-----------|------------------|-------------|---------|
| 1  |          |      |       |           |                  |             |         |
| 2  |          |      |       |           |                  |             |         |

### Verification (drive mode) — per-element log

<!-- For each element exercised in drive mode, record action + outcome. -->

- **Element 1** (<label>)
  - Pre-action: <evidence path>
  - Action: <command>
  - Post-action: <evidence path>
  - State change: <observed>
  - Verdict: PASS | FAIL — <reason>

### Hand-off (delegate mode) — verification needed

<!-- Structured task list for the receiving skill. -->

```
implement (validation phase):
  - [Element <id>] <action to verify>

ios-validation-runner:
  - [Element <id>] <iOS-specific verification>

full-functional-audit:
  - <flow-level concern that exceeds this screen>
```

### Findings

- [SEVERITY] Element <id> (<label>) — <signifier / affordance / reach / functional finding> — <fix>

## Phase 3 — Content Quality

**Categories present:** prose ☐ | code blocks ☐ | diagrams ☐ | data viz ☐ | tables ☐ | embedded media ☐ | form copy ☐

- [SEVERITY] [CONTENT_TYPE] — <finding> — <fix>

## Phase 4 — UX Heuristics

<!-- Cite the specific heuristic number + name. Multiple violations of the same heuristic are listed separately. -->

- [SEVERITY] [Heuristic #N: <name>] — <violation> — <offending element> — <suggested fix>

## Phase 5 — Synthesis & Verdict

### Severity tally

| Severity | Count |
|----------|-------|
| CRITICAL |       |
| HIGH     |       |
| MEDIUM   |       |
| LOW      |       |

### Verdict

<!-- Apply the verdict rules:
  FAIL                    = any CRITICAL
  PASS WITH ISSUES        = no CRITICAL, but ≥1 HIGH or accumulated MEDIUM
  PASS (LIMITED COVERAGE) = no CRITICAL/HIGH, but coverage gaps exist
  PASS                    = no CRITICAL/HIGH AND coverage is multi-axis
  Behavioral claims (element works, flow completes) require actions the AI
  actually executed as the end user. If validation was not executed, say
  UNVERIFIED — never report unexecuted checks as done.
-->

**Verdict:** PASS | PASS WITH ISSUES | PASS (LIMITED COVERAGE) | FAIL | UNVERIFIED (behavioral checks not executed)

**Rationale:** <one sentence explaining why this verdict>

### Hand-offs

```
implement (validation phase):
  -

full-functional-audit:
  -

ios-validation-runner:
  -

gate-validation-discipline:
  -
```

### Open questions / follow-ups

<!-- Things you couldn't resolve from the available evidence. Each should either become a hand-off task or a re-audit when the missing evidence is captured. -->

- [ ]
- [ ]
- [ ]

---

*Generated using the `ui-experience-audit` skill, 5-phase protocol.*
