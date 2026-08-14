---
name: ui-experience-audit
description: >
  Deep end-to-end audit of any UI screen across four dimensions — visual
  defects, interactive elements, content quality, and UX heuristics — ending
  in one severity-classified report. Inventories every action item (button
  link, field, gesture), verifies each is discoverable and reachable, audits
  prose / code-block / diagram / data-viz rendering, and evaluates against
  Nielsen's 10 heuristics plus affordance theory. Modes:
  identify-and-delegate (screenshot only) or drive-interaction (drive the
  live system as an end user — preferred). Use when reviewing a UI screen
  page, or flow — 'review this screen', 'audit this page', 'QA this view'
  'is this UI good' — iOS, web, or cross-platform. Not for pixel-checklist
  screenshot QA (use visual-inspection) or app-wide functional sweeps (use
  full-functional-audit).
---

# UI Experience Audit

## Run checklist

Copy this checklist and track your progress:

- [ ] Choose mode (identify-and-delegate vs drive-interaction — prefer driving)
- [ ] Inventory every interactive element; verify discoverable/reachable
- [ ] Audit visual defects, content rendering, data-viz
- [ ] Evaluate against Nielsen's 10 heuristics + affordances
- [ ] Emit one severity-classified report

A complete per-screen audit ending in a single severity-classified report.
Catches what checklist-only inspection misses: buttons that look tappable but
aren't wired up, code blocks that render unreadable, charts that exclude
keyboard users, heuristic violations on pixel-perfect screens.

## The Protocol at a Glance

```
Phase 0  Triage          → right-size the audit; catch show-stoppers first
Phase 1  Visual          → layout, contrast, typography, platform conformance
Phase 2  Interactive     → inventory + affordance + reach + (drive | delegate)
Phase 3  Content quality → prose, code blocks, diagrams, data viz, media
Phase 4  UX heuristics   → Nielsen's 10 + affordance/signifier alignment
Phase 5  Synthesis       → severity-classified report + hand-offs
```

Run all phases in order. A phase failure does not abort the audit — record
and continue. Phase 5 decides go/no-go.

## What is a "screen"

A single user-facing surface — a page, modal, sheet, major view, or discrete
component with its own context. A whole app is not a screen (use
`full-functional-audit`). A button is not a screen.

## Mode Selection (READ FIRST)

Both modes run all 5 phases; they differ only in Phase 2 depth.

| Mode | When | Phase 2 behavior |
|------|------|------------------|
| **Drive-interaction** (heavy, PREFERRED) | Any tool path exists: browser automation, Playwright, Chrome DevTools MCP, simulator control (`simctl`, `idb`), running dev server | YOU personally tap / click / focus / type each action item as an end user, capturing pre/post evidence per element |
| **Identify-and-delegate** (light) | Only a screenshot exists; no live system reachable | Build the inventory and assess affordance/reach from the image; hand functional verification off with a structured task list |

Per `../../references/end-user-actor.md`: **if a tool path exists, DRIVE.**
Static screenshots are 2D inspection — they cannot resolve "is it wired up?".
Escalate to drive mode rather than fabricating a verdict. Destructive or
auth-gated actions (delete, pay, send) drop back to delegate for that element
unless the user explicitly approves the action.

### Evidence capture (drive mode)

```
evidence/audit-<screen>-<YYYYMMDD-HHMM>/
├── 00-pre-audit.png
├── NN-element-<id>-<label>-pre.png / -post.png / .log
├── coverage/{light,dark}-{desktop,mobile}.png
└── audit-report.md
```

The per-element `.log` records: element, selector/coordinates, pre-state
action taken, post-state, verdict, evidence paths.

## References (load on demand)

Always: `references/interactive-element-audit.md`
`references/content-quality-checklist.md`
`references/ux-heuristics-checklist.md`
`../../references/defect-pattern-database.md`
Platform: `../../references/ios-hig-checklist.md` (iOS)
`../../references/web-wcag-checklist.md` (web), both (cross-platform).
Web/cross-platform: `references/responsive-audit.md`.
Report: copy `assets/audit-report-template.md`.

## Audit Discipline

1. **Define PASS criteria before viewing evidence** — 3-5 observable things
   that would make this screen pass. Audit against the list, not vibes.
2. **Inventory before judging** — Phase 2 starts with a COMPLETE list of
   action items; then evaluate each.
3. **Assume nothing works until verified** — pattern-matching ("that's a
   button, buttons work") is the #1 source of false-affordance misses.

A 0-finding audit is suspicious: real screens have >= 3 LOW-or-above
findings. Zero findings means you skipped a phase.

## Phase 0 — Triage (30 seconds)

Record as CRITICAL immediately: missing/broken content (empty chart plot
broken image, "undefined"/"NaN" as text), lorem ipsum or placeholder data
visible error states/stack traces, crash or blank screens, unstyled-content
flash residue, visible console errors.

**Coverage check**: note which axes the evidence covers (light/dark
viewports, empty/loading/populated/error, long content). Single-axis coverage
caps the verdict at PASS (LIMITED COVERAGE) — and is itself a finding.

## Phase 1 — Visual Defect Inspection

Walk the universal checklist (overflow/clipping, spacing/alignment
typography/contrast, heading hierarchy, affordance sizing, visual hierarchy
dark/light mode, edge cases) then the platform checklist from the loaded
reference. This is the same protocol as `visual-inspection`; canonical
checklists live in the shared references.

Contrast from a screenshot: use rules of thumb (legibly distinct -> likely
pass; "soft"/faded -> suspect, flag MEDIUM for tooled check; squint-to-read
-> HIGH–CRITICAL; pale gray on white -> CRITICAL). Never state exact ratios
from pixels alone — prefer Lighthouse/Axe/DevTools when the system is live.

## Phase 2 — Interactive Element Audit

Follow `references/interactive-element-audit.md`:

1. **Inventory** every action item: buttons, links, inputs, toggles, swipe
   targets, draggables, hover-revealed controls, keyboard shortcuts
2. Record per item: position, type, signifier present?, affordance match?
   target size, focus order
3. **Verify reachability** — minimum target size, tab order, no covering
   element stealing hits
4. **Verify functionality** per mode:
   - *Drive*: YOU act as the end user via the tool path — tap/click/focus
     each element, capture pre/post evidence, record outcomes in the .log
   - *Delegate*: produce the structured hand-off task list

False affordances (looks tappable, isn't) and missing signifiers (works but
invisible) are both failures. A screenshot that cannot resolve wiring ->
PASS WITH ISSUES (verification pending), never PASS.

## Phase 3 — Content Quality Audit

Follow `references/content-quality-checklist.md`: prose (heading hierarchy
line length 65-75 chars, body >= 16px web / 17pt iOS), code blocks
(monospace, highlight contrast, mobile wrap, copy affordance, language
label), diagrams (title, alt text, non-color channels, keyboard reachability)
data viz (tabindex per point, tooltips without mouse, labelled axes, legend
text alternative), media (captions, transcripts, no autoplay with sound).

## Phase 4 — UX Heuristic Evaluation

Follow `references/ux-heuristics-checklist.md`: Nielsen's 10 (system status
visibility, real-world match, user control, consistency, error prevention
recognition over recall, flexibility, minimalist design, error recovery
help) plus affordance/signifier alignment for every interactive element.
Cite the heuristic number and name per violation.

## Phase 5 — Synthesis

Combine into the report shape in `assets/audit-report-template.md`. Verdict
rules and severity definitions: `../../references/severity-model.md`.

- FAIL — any CRITICAL
- PASS WITH ISSUES — zero CRITICAL, >= 1 HIGH, remediation scheduled
- PASS (LIMITED COVERAGE) — clean but single-axis coverage
- UNVERIFIED — behavioral checks were not actually executed by the AI as
  the end user (reported honestly, never laundered into PASS)
- PASS — zero CRITICAL/HIGH, full coverage, and behavioral findings rest on
  actions the AI actually executed

The report header records the tools and actions actually performed. An audit
that executed nothing says so — skipping or faking verification steps is a
process violation, not a shortcut.

Hand-offs: wiring doubts -> the shared runbooks (`references/*-validation.md`); app-wide scope ->
`full-functional-audit`; pure pixel QA -> `visual-inspection`.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Confirming a screenshot exists without reading it | READ it; describe what you SEE |
| Guessing wiring from pixels when tools exist | DRIVE the element as the end user |
| Stopping at Phase 1 because "layout looks good" | Run all phases — bugs live in interaction/content/UX |
| Skipping Phase 0 triage | Show-stoppers first, always |
| PASS from a single screenshot | State coverage; cap at LIMITED COVERAGE |
| Estimating exact contrast from pixels | Rules of thumb; flag for tooled verification |
| Treating heuristics as opinions | Cite number + name |
| Faking or skipping validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim; unexecuted = UNVERIFIED |

## Example

**Input:** User: 'Audit the settings page.'

**Output:** Drive-interaction mode: 14 action items inventoried, 2 unreachable (keyboard), 1 contrast failure (4.1:1 < 4.5:1), heuristic violations H5/H8 — one severity-classified report.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `visual-inspection` | Phase 1 visual defects | the checklist protocol for screenshots |
| `end-user-testing` | evidence capture | run-scoped evidence rules |

Called by: `full-functional-audit`.
