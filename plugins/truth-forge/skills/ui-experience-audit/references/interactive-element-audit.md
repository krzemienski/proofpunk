# Interactive Element Audit — Phase 2 Method

The bulk of UI defects do not live in pixels — they live in the gap between *what looks tappable* and *what actually responds*. This phase closes that gap.

## What counts as an interactive element

Be liberal in the inventory. Anything that *could* be a target of user action goes in:

| Category | Examples |
|----------|----------|
| Primary buttons | "Save", "Submit", "Continue", "Buy now" |
| Secondary buttons | "Cancel", "Skip", "Learn more" |
| Icon buttons | Trash, edit, share, more (⋯), close (×), back (‹) |
| Links | Inline anchors, navigation links, breadcrumbs |
| Form fields | Text input, textarea, select, checkbox, radio, switch, slider, date picker, file upload |
| List rows | Tappable cells, swipe actions, drag handles |
| Tab bars / segmented controls | Bottom tab bar (iOS), top tabs, segmented pickers |
| Cards | Tappable cards (entire card is target), within-card buttons |
| Gestures | Swipe-to-delete, pull-to-refresh, long-press, pinch, double-tap, drag |
| Hover-revealed | Menus, tooltips, context-menu triggers |
| Keyboard shortcuts | Hinted in UI ("⌘K to search") or implicit (Tab, Enter, Esc) |
| Voice / accessibility | VoiceOver actions, accessibility custom actions |
| External handoffs | Share sheets, deep links, URL schemes |

## Step 1 — Inventory

Walk the screenshot top-to-bottom, left-to-right. For each interactive element, record a row:

```
| ID | Position | Type | Label | Signifier | Affordance match | Target size | Notes |
|----|----------|------|-------|-----------|------------------|-------------|-------|
| 1  | top-right | icon button | (none — looks like a magnifying glass) | icon shape | YES — search convention | ~24×24 px | Below WCAG min |
| 2  | center | primary button | "Continue" | filled rect, accent color | YES | ~280×48 pt | OK |
| 3  | bottom-left list row | list cell | "Settings" | chevron, row height | YES | full row | OK |
| 4  | inline | text styled bold blue | "terms of service" | color + underline? | UNKNOWN — no underline visible | text-only | Possible false negative — looks decorative |
```

If you can't tell whether something is interactive from the screenshot, that itself is a finding (weak / missing signifier — Phase 4 heuristic #6 violation).

## Step 2 — Affordance / signifier check

For every row, two questions:

1. **Does the visual match an interactive convention?** (button shape, underline, icon, cursor change, shadow, hover state) — this is the *signifier*
2. **If a user trusted the signifier, would the system respond?** — this is whether the *perceived affordance* matches the *actual affordance*

The four failure modes:

| Perceived | Actual | Failure mode | Severity |
|-----------|--------|--------------|----------|
| Looks interactive | Is interactive | ✓ correct | n/a |
| Looks interactive | Is NOT interactive | **False affordance** — user taps and nothing happens | HIGH–CRITICAL |
| Looks NOT interactive | Is interactive | **Hidden affordance** — feature undiscoverable | HIGH |
| Looks NOT interactive | Is NOT interactive | ✓ correct | n/a |

False affordances are the most common defect this phase catches. Watch for: bold colored text that isn't a link, card-shaped elements that aren't tappable, icons that aren't buttons.

**Concrete check for `cursor:pointer` no-handler defect** (iter-16 finding F-1A pattern):

```bash
# 1. Find every selector that sets cursor:pointer
grep -rn "cursor:\s*pointer" path/to/css/

# 2. For each selector, confirm a JS click handler is bound
agent-browser open <url>
agent-browser eval "(() => { const el = document.querySelector('<sel>'); if (!el) return 'no-element'; const events = (typeof getEventListeners === 'function') ? getEventListeners(el) : null; return events ? Object.keys(events) : 'getEventListeners-unavailable'; })()"
# Output should include "click" — if it returns [] or undefined, the cursor:pointer is a lie

# 3. Fallback when getEventListeners is unavailable: dispatch a click and watch for any side effect
agent-browser screenshot pre-click.png
agent-browser click '<selector>'
agent-browser screenshot post-click.png
# diff — if zero pixels changed and no fetch fired, the handler is missing
```

If `cursor:pointer` is set but no click handler is bound, that is a HIGH false-affordance defect. The cursor tells the user "clicking will do something"; the system contradicts the cursor by doing nothing.

Hidden affordances are second most common. Watch for: swipe gestures with no visual hint, long-press menus with no signifier, double-tap actions, hover-only menus on touch devices.

## Step 3 — Reachability

For each element, verify it can actually be reached by every input modality the platform supports:

### Touch reachability
- Touch target ≥ **44×44 pt** (Apple HIG) or **24×24 CSS px** (WCAG 2.2 AA) — measure from screenshot or DOM
- Targets ≥ **8 pt** apart from each other (no thumb-overlap zones)
- Target not occluded by overlay, fixed header, sticky element, keyboard, or notch
- Target inside the safe area on iOS (no clipping under home indicator / Dynamic Island)

### Keyboard reachability (web + macOS)
- Element is in the tab order (no `tabindex="-1"` on what should be focusable)
- Focus indicator is visible (≥ 2 px outline, 3:1 contrast against adjacent colors)
- Tab order matches visual reading order
- No keyboard trap (Esc / Shift+Tab / Tab can always escape)
- Activation via Enter or Space works as expected

### Screen reader reachability
- Element has an accessible name (label, aria-label, accessibilityLabel)
- Role is correct (`role="button"`, `.accessibilityAddTraits(.isButton)`)
- State is announced (selected, checked, expanded, disabled, busy)

If any modality fails, that's a Phase 2 finding.

## Step 4 — Functional verification

Behaviour depends on which mode the audit is running in.

### Identify-and-delegate (light mode)

You only have screenshots. Functional verification is impossible from an image. Produce a structured task list and hand off:

```
## Functional verification needed

### functional-validation
- Tap "Continue" button (id 2) — verify navigation to next screen
- Submit empty form — verify validation message appears
- Tap search icon (id 1) — verify search overlay opens

### ios-validation-runner
- Verify tab bar bottom-inset on iPhone 14 Pro (notch device)
- Verify swipe-to-delete on list rows in Settings

### Notes
- Element 4 ("terms of service") — uncertain if interactive; needs DOM inspection
```

The receiving skill takes it from there.

### Drive-interaction (heavy mode)

You have a tool path to the live system. Exercise each item in inventory order, capturing evidence per element:

| Tool | Use for |
|------|---------|
| `xcrun simctl io <UDID> screenshot` | iOS before / after screenshots |
| `idb ui describe-all --udid <UDID>` | iOS accessibility tree, exact tap coordinates |
| `idb ui tap <x> <y>` | iOS tap |
| `idb ui swipe x1 y1 x2 y2` | iOS swipe gesture |
| `agent-browser` / Playwright / Chrome DevTools MCP | Web click, type, scroll, screenshot |
| Browser DevTools accessibility panel | Web focus order, ARIA, computed roles |

For each element exercised, record:

```
- Element id 2 ("Continue" button)
  - Pre-tap screenshot: <path>
  - Action: idb ui tap 200 720
  - Post-tap screenshot: <path>
  - State change: navigated to /onboarding/step-2 — expected
  - Verdict: PASS

- Element id 1 (search icon)
  - Pre-tap screenshot: <path>
  - Action: idb ui tap 360 56
  - Post-tap screenshot: <path>
  - State change: NONE — overlay did not open
  - Verdict: FAIL (CRITICAL — false affordance, search not wired up)
```

Stop driving and report immediately if you encounter:
- A modal that prevents further interaction
- A crash or error state (capture the dump)
- A destructive action confirmation (do not proceed without explicit user approval)
- Any payment / auth / submit-once boundary

## Common defects this phase catches

| Defect | Symptom | Root cause | Typical fix |
|--------|---------|------------|-------------|
| False affordance | Looks tappable, doesn't respond | Stale handler removed, missing `onClick`, `Button` style on a `View` | Wire up handler or change to non-interactive style |
| Hidden affordance | Feature exists but no visual hint | Swipe / long-press only, no icon / animation / onboarding hint | Add a visible signifier or onboarding tooltip |
| Sub-minimum target | < 44×44 pt or < 24×24 px | Icon-only button without padding | Expand padding to meet minimum |
| Target overlap | Adjacent buttons too close, mis-taps | < 8 pt gap | Add gap, increase row height |
| Focus trap | Tab key can't escape modal | Missing focus-trap exit logic | Wire Esc + Shift+Tab cycling |
| Invisible focus | No outline on tab | `outline: none` with no replacement | 2 px focus ring with 3:1 contrast |
| Occluded target | Bottom tab bar hides last list row | Missing `safeAreaInset` / scroll padding | Add bottom inset matching tab height |
| Disabled-looking-active | Disabled button looks identical to enabled | Missing opacity / cursor change | Add `cursor: not-allowed` + reduced opacity |
| Hover-only menu on touch | Submenu only opens on hover, never on touch | CSS `:hover` with no touch fallback | Add tap toggle |

## Output format

Phase 2 produces two artifacts: the inventory table and the verification log. Both feed into the Phase 5 synthesis.

```
## Phase 2 — Interactive Element Audit (<screen name>)

### Inventory (N items)
<inventory table>

### Verification (drive mode) | Hand-off (delegate mode)
<verification log OR structured hand-off task list>

### Findings
- [SEVERITY] Element <id> (<label>) — <finding> — <suggested fix>
```
