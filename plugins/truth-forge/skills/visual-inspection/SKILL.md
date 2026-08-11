---
name: visual-inspection
description: >
  Mandatory visual QA protocol for UI screenshots — iOS (Apple HIG), web
  (WCAG 2.2), and cross-platform. Evaluates layout, overflow, spacing,
  typography, contrast, touch targets, dark mode, and visual hierarchy
  against universal and platform-specific checklists, with severity
  classification and a defect-pattern database. Use before marking ANY
  screenshot as PASS, when reviewing simulator captures, browser
  screenshots, or design-implementation evidence. Trigger even when the user
  just says "check this screenshot", "does this look right", or attaches a
  UI image.
---

# Visual Inspection Protocol

Every screenshot MUST pass this protocol before being marked PASS.

## Scope

Handles: visual defect detection, layout verification, accessibility
compliance, platform guideline conformance.
Does NOT handle: functional validation (does the feature work? — use
`functional-validation`), backend testing, performance profiling.

## Platform Detection

| Indicator | Platform | Reference |
|-----------|----------|-----------|
| `.xcodeproj`, SwiftUI, simulator screenshot | iOS/macOS | LOAD `../../references/ios-hig-checklist.md` |
| HTML/CSS, Playwright, browser screenshot | Web | LOAD `../../references/web-wcag-checklist.md` |
| React Native, Flutter, Expo | Cross-platform | Load BOTH |

Load the platform reference BEFORE reviewing. The universal checklist below
applies to ALL platforms.

## Universal Checklist (ALL must pass)

### 1. Content Overflow & Clipping
- No text overlapping other text
- No content bleeding outside container boundaries
- Scrollable areas not clipped mid-line
- Lists fit inside parent frame
- Badges/labels don't overlap adjacent sections
- No silently-truncated lines (clipped without ellipsis or visible scroll)

### 2. Spacing & Alignment
- Consistent spacing between sections; headers separated above AND below
- Cards padded on all 4 sides; grid items baseline-aligned
- No doubled spacing (two margins stacking)

### 3. Typography & Readability
- Contrast: 4.5:1 normal text, 3:1 large text (18pt+ / 14pt+ bold)
- No truncated text where full text should show
- Platform-token font sizes (no hardcoded tiny fonts)
- Line height 1.5-1.75 for body text
- Dynamic content doesn't push elements off-screen

### 4. Interactive Elements (visual aspect)
- Touch/click targets: min 44x44pt (iOS HIG) / 24x24px (WCAG 2.2)
- Tappable rows have chevrons or affordance; no overlapping tap targets
- Empty states show meaningful message; loading states use skeleton/shimmer

### 5. Visual Hierarchy
- Section headers visually distinct from body
- Cards have visible boundaries (border, shadow, or background difference)
- Active/selected states clearly distinguishable
- Icons aligned with associated text; badge counts within container edges

### 6. Dark/Light Mode
- No pure white (#FFF) on dark backgrounds — semantic tokens
- Glass/blur effects don't wash out content; dividers visible but subtle
- Status indicators contrast in both modes
- Light mode: glass cards opaque enough to read

### 7. Edge Cases
- Long text truncates with ellipsis, not overflow
- Zero-count states handled (empty lists, 0 badges)
- Error states visible, not swallowed
- Navigation transitions don't flash white/blank

## Review Protocol

This skill performs 2D review (visual QA of captures) — that is its job. But
per `../../references/end-user-actor.md`:

- Screenshots SHOULD come from an AI-driven session (you drove the app via
  MCP/automation tools to the state being captured), not from stale or
  third-party captures.
- When a visual finding raises "is this element actually wired up?", that is
  OUT of this skill's scope — escalate to `functional-validation` to DRIVE
  the element as an end user rather than guessing from pixels.

```
1. READ the screenshot with the Read tool (not just confirm it exists)
2. IDENTIFY the platform -> load the matching reference
3. WALK every universal checklist item
4. WALK every platform-specific checklist item
5. For ANY failure, record:
   [SEVERITY] [CHECKLIST_ITEM] — <what you SEE> — <owning view/file> — <suggested fix>
6. Mark PASS only if ALL items pass (universal + platform)
```

A PASS from this skill certifies VISUAL QUALITY ONLY. It never certifies
that anything works — behavioral claims require `functional-validation`
driving the system as the end user, per
`../../references/end-user-actor.md`.

Severity classification and verdict rules: follow
`../../references/severity-model.md` (CRITICAL blocks, HIGH before commit,
state coverage axes).

For contrast estimation from screenshots without devtools, use the
rules-of-thumb table in `ui-experience-audit` (suspect cases get flagged for
tooled verification — never state exact ratios from pixels alone).

## Defect Pattern Database

Consult `../../references/defect-pattern-database.md` for common defects with
root causes and fix patterns across iOS, web, and cross-platform projects.

## Anti-Patterns

| Pattern | Why it's wrong | Do this instead |
|---------|---------------|-----------------|
| Confirming a screenshot exists without reading it | A crash dialog is still a .png | READ it; describe what you SEE |
| Defining PASS criteria after viewing evidence | Confirmation bias | Criteria before evidence |
| Skipping the platform-specific checklist | Universal catches ~60% of issues | Walk BOTH checklists |
| Marking LOW issues "not worth fixing" | Cosmetic debt compounds | Log all severities; fix CRITICAL/HIGH |
| Reviewing only the happy-path screenshot | Edge cases hold most bugs | Empty, overflow, error, dark-mode states too |
| Marking validation complete without the AI actually invoking MCP/automation tools and acting as the end user | Unexecuted validation is not validation | Execute the tools yourself; unexecuted = UNVERIFIED |
| Skipping or faking QA/verification steps under any circumstance | A skipped check tells you nothing while pretending to | Run them or report them UNVERIFIED — no exceptions |
## When NOT to Use

- Functional validation — use `functional-validation`
- Deeper per-screen audit (interaction + content + UX heuristics) — use `ui-experience-audit`
- Backend API testing or performance profiling

## Related Skills

- `ui-experience-audit` — the deeper sibling: this protocol's Phase 1 plus interaction, content, and UX-heuristic phases
- `functional-validation` — exercise real features after visual PASS
- `end-user-testing` — citation standard for screenshot evidence
