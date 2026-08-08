# UI Defect Pattern Database

Common defects across iOS, web, and cross-platform with root causes and fix patterns. Organized by audit phase: triage (Phase 0), visual (Phase 1), interactive (Phase 2), content (Phase 3), and UX heuristic (Phase 4).

## Phase 0 — Triage Defects (CRITICAL by default)

| Defect | Visual Symptom | Root Cause | Fix |
|--------|---------------|------------|-----|
| Missing chart content | Chart container present but bars / lines / points absent | Data not loaded, render bug, CSS height percent without parent height | Verify data flow, fix render logic |
| Broken `<img>` | Alt text or browser-default broken-image icon | Bad URL, CORS failure, missing asset | Fix path, add error fallback |
| Lorem ipsum visible | "Lorem ipsum dolor sit amet" or "[TODO]" rendered | Placeholder copy not replaced before ship | Replace with real copy |
| Hardcoded test data | "John Doe", "test@test.com", "555-555-5555" in production-looking UI | Test fixtures leaked to production build | Replace with real / dynamic data |
| Raw error in UI | Stack trace, "TypeError: undefined", "500 Internal Server Error" | Unhandled exception surfaced to user | Add error boundary + user-friendly message |
| `undefined` / `null` / `NaN` text | Literal "undefined" rendered as content | Missing fallback in template (`${user.name ?? 'Guest'}`) | Add nullish-coalesce or default |
| Blank where content should be | Empty bordered container, list with no rows or empty state | Missing empty-state UI, data fetch failure | Add explicit empty state with message |
| Unstyled content flash captured | Default browser button styling, default font on custom design | FOUC — CSS not loaded before screenshot | Capture after `networkidle` / load fonts before render |
| Console errors / warnings in-page | DevTools error count visible, in-page warning banners from dev tooling | Dev mode left enabled in evidence | Re-capture in production-like build |

## Phase 1 — Visual Defects

### iOS / SwiftUI

| Defect | Visual Symptom | Root Cause | Fix |
|--------|---------------|------------|-----|
| VStack overflow | Content clipped at bottom, no scroll | `VStack` in constrained height without `ScrollView` | Wrap in `ScrollView(.vertical)` |
| Fixed frame too small | Content overlapping card boundaries | `.frame(height: N)` too small for dynamic content | `.frame(minHeight: N)` + `.clipped()` |
| Environment crash | Blank screen or crash on navigation | `@Observable` not injected on sibling `NavigationDestination` | `.environment()` on ALL destination branches |
| LazyVGrid misalign | Grid items offset from each other | Missing `.alignment` on `GridItem` | Set explicit alignment on GridItem |
| GeometryReader zero | Blank view on first render | GeometryReader reports 0,0 before layout pass | Default size fallback |
| Sheet wrong color scheme | Sheet content in light mode when app is dark | Missing `.preferredColorScheme(.dark)` on sheet | Add color scheme to sheet content |
| @AppStorage stale | Feature flags don't update after reinstall | UserDefaults cached from previous install | `simctl uninstall` before `install` |
| Safe area violation | Text under status bar or home indicator | Content outside `safeAreaInset` | Respect safe area insets |
| Tab bar occlusion | Last list item hidden behind tab bar | Missing content inset on ScrollView | Add `.safeAreaInset(edge: .bottom)` or proper padding |
| Nav bar overlap | Custom nav overlapping status bar | Incorrect navigation bar height | Use system `NavigationStack` / `navigationTitle` |
| Sidebar clipping | Nav items below fold invisible (no scroll) | Plain VStack with 20+ items, no ScrollView | Wrap sidebar nav in `ScrollView(.vertical)` |
| Badge overflow | Badge "17" clips outside icon bounds | Badge not constrained to parent | `.clipShape()` or constrain badge frame |
| Shimmer flash | White flash before shimmer gradient starts | No initial fill color on shimmer layer | Set `.fill(theme.glassBackground)` as base |
| Text size violation | Hardcoded `size: 10` or `size: 12` | Not using Dynamic Type / theme tokens | Use `.font(.system(...))` or theme font tokens |
| Monospaced digit shift | Numbers shift layout when values change | Proportional digit widths | `.monospacedDigit()` on counters/badges |

### Web / CSS

| Defect | Visual Symptom | Root Cause | Fix |
|--------|---------------|------------|-----|
| Horizontal scroll | Scrollbar at narrow viewports | Element exceeds viewport width | `max-width: 100%`, `overflow-x: hidden` on container |
| Text overflow | Long words break layout | No word-break strategy | `overflow-wrap: break-word` or `word-break: break-word` |
| Invisible focus ring | No visible focus indicator on tab | `outline: none` with no replacement | `outline: 2px solid` with 3:1 contrast |
| Placeholder contrast fail | Light gray placeholder text | Placeholder not meeting 4.5:1 ratio | Darken placeholder color or use floating label |
| CLS layout shift | Elements jump during page load | Images without dimensions, late-loading fonts | `aspect-ratio` or `width`/`height` on images |
| FOIT text flash | Text invisible then suddenly appears | Web font blocking render | `font-display: swap` or preload critical fonts |
| Stacking context break | Modal behind content, z-index war | Unmanaged z-index values | Establish z-index scale, use CSS layers |
| Touch target too small | Tiny icon buttons (16x16) | No padding expansion | `padding` to expand clickable area to 44x44 |
| Dark mode border invisible | Borders vanish in dark mode | Hardcoded `border-gray-200` | Semantic tokens: `border-gray-200` light / `border-gray-700` dark |
| Glass card invisible (light) | Card background transparent in light mode | `bg-white/10` opacity too low | `bg-white/80` or higher for light mode |
| Muted text too light | Secondary text unreadable | `gray-400` on white background | `slate-600` (#475569) minimum for muted text |
| Sticky covers content | Fixed/sticky header hides scrolled content | No scroll-margin or padding offset | `scroll-margin-top` matching header height |
| Form label missing | Input has no visible label | Placeholder-only pattern | Add visible `<label>` with `for` attribute |
| Skip link absent | No keyboard shortcut to skip nav | Missing skip-to-content link | Add as first focusable element |

### Cross-Platform / General

| Defect | Visual Symptom | Root Cause | Fix |
|--------|---------------|------------|-----|
| Color-only status | Status conveyed only by color | No icon or text supplement | Add icon + text alongside color indicator |
| Empty state blank | White/blank space where content should be | No empty state handler | Add meaningful empty state message + icon |
| Loading frozen | UI appears frozen during data fetch | No loading indicator | Show skeleton/shimmer/spinner during load |
| Truncation without ellipsis | Text cut off abruptly | `overflow: hidden` without `text-overflow: ellipsis` | Add `text-overflow: ellipsis` + `white-space: nowrap` |
| Double spacing | Extra vertical gap between sections | Two margins stacking (CSS) or double padding (SwiftUI) | Collapse margins or audit spacing modifiers |
| Icon-text misalign | Icon vertically offset from adjacent text | Different alignment defaults | Explicit vertical centering (`.alignmentGuide` / `align-items: center`) |
| Modal viewport overflow | Dialog taller than screen | Fixed height modal on small viewport | `max-height: 90vh` + scroll internal content |
| Error state swallowed | No error feedback to user | `catch` block with no UI update | Show inline error message near the failure point |
| Badge zero shown | "0" badge displayed when it shouldn't be | No zero-check before rendering badge | `if count > 0 { Badge(count) }` |
| White flash on transition | Brief white screen between views | Background color not set on destination view | Set background color on all views in navigation stack |
| Shared-token cascade | Fixing one element's color/spacing breaks another semantically-different element | One design token reused across multiple selectors with different visual roles (e.g. `--color-muted` for caption AND badge text) | Audit token reuse: `grep "var(--color-X)"` to find all consumers; if consumers belong to different visual roles, split into separate tokens BEFORE changing the value. iter-16 findings F-1B-cascade and F-2D-latent are canonical — fixing dark-mode caption contrast unmasked badge contrast because both used `--color-text-muted`. |

## Phase 2 — Interactive Element Defects

| Defect | Visual Symptom | Root Cause | Fix |
|--------|---------------|------------|-----|
| False affordance — colored text | Bold colored inline text that isn't a link | Color-only emphasis with no anchor | Either make it a real link or remove the link-like styling |
| False affordance — card | Card-styled element that doesn't respond to tap | Card visual treatment with no `onTapGesture` / `onClick` | Wire up handler, or remove card chrome |
| False affordance — disabled-looking | Button that looks disabled but is enabled | Insufficient contrast for active state | Increase active-state saturation / contrast |
| Hidden affordance — swipe-only | Feature exists, no signifier | Swipe gesture without icon, hint, or onboarding | Add visual cue (drag handle, animation, first-use tooltip) |
| Hidden affordance — long-press | Long-press menu with no signal | iOS context menu with no `…` button alternative | Provide both gesture and visible button |
| Hidden affordance — hover menu | Submenu only on hover | CSS `:hover` with no touch fallback | Add tap-to-toggle for touch devices |
| Sub-minimum target | Icon button too small to tap reliably | 16×16 icon with no padding | Expand to 44×44pt iOS / 24×24px WCAG via padding |
| Target overlap | Mis-tap between adjacent buttons | < 8 pt gap between targets | Add gap, or merge / restructure |
| Focus trap | Tab key cycles forever inside modal | Missing focus-trap exit logic | Wire Esc + boundary cycling |
| Invisible focus | No outline on Tab | `outline: none` with no replacement | 2 px outline with 3:1 contrast |
| Wrong tab order | Tab jumps unexpectedly | Positive `tabindex` values (`tabindex="3"`) | Remove positive tabindex; use DOM order |
| Occluded target | Bottom row hidden behind sticky / tab bar | No content inset | Add `safeAreaInset(.bottom)` (iOS) or `padding-bottom` (web) |
| Disabled button no cursor | Disabled button looks identical to enabled | Missing `cursor: not-allowed` + opacity | Add disabled styling + ARIA `aria-disabled` |
| Form field no label | Input has placeholder but no label | Placeholder-only pattern | Add visible `<label>` with `for` attr |
| Missing accessibility name | Icon button has no screen-reader label | Missing `aria-label` / `accessibilityLabel` | Add descriptive label |

## Phase 3 — Content Quality Defects

| Defect | Visual Symptom | Root Cause | Fix |
|--------|---------------|------------|-----|
| Code block low contrast | Comment color vs code bg below 4.5:1 | Default theme syntax-highlight palette | Use accessible theme (e.g. GitHub Dark Default, Solarized) and verify each token |
| Code block silent truncation | Long line clipped at right edge, no scroll | `overflow: hidden` without `overflow-x: auto` | Enable horizontal scroll with visible scrollbar, or wrap with `white-space: pre-wrap` |
| Code in proportional font | Code looks like prose | Missing `<code>`/`<pre>` or CSS not loaded | Apply `font-family: ui-monospace, SF Mono, Menlo, Consolas` |
| No copy affordance | User must select code by hand | No copy button | Add hover-revealed copy button (desktop) or always-visible (mobile) |
| Code/output indistinguishable | User can't tell what to type vs what's printed | Same styling for both | Different bg or label ("Output:" header) |
| Line numbers selectable | Copy includes line numbers | Line numbers in same `<pre>` | Use CSS counters or `user-select: none` on numbers |
| Diagram color-only | Lines distinguished only by red/green | No patterns / shapes / direct labels | Add dashed/dotted line styles, shapes, or direct labels |
| Diagram no alt | SVG with no `<title>` / `<desc>` | Plain `<svg>` export | Add `<title>` + `<desc>`, or descriptive caption below |
| Hover-only chart info | Tooltip required to read values | All values in tooltip only | Show key values inline (axis labels, direct callouts), or pair with data table |
| Chart not keyboard-reachable | Mouse-only data exploration | No `tabindex`, no key handlers | Add `tabindex="0"` to data points + arrow-key navigation |
| Table no header semantics | Screen reader can't navigate | All `<td>`, no `<th>` with `scope` | Use `<th scope="col">` / `<th scope="row">` |
| Tabular numerals misaligned | Digits shift between rows | Proportional digit widths | `font-variant-numeric: tabular-nums` (web) / `.monospacedDigit()` (SwiftUI) |
| Mobile table overflow | Table extends past viewport | Fixed-width table | Wrap in scroll container OR collapse to cards on narrow viewport |
| Body text too small | < 16 px on mobile | Hardcoded 12–14 px | Use 16 px (1 rem) min on mobile |
| Line length too long | Body text spans full 1440 px viewport | No `max-width` on prose container | `max-width: 65ch` on body container |
| Muted text contrast fail | "Secondary" text below 4.5:1 | `text-gray-400` (#9CA3AF) on white | Use `slate-600` (#475569) minimum for muted |
| Heading skip | h1 → h3 with no h2 | Designer-driven hierarchy ignoring DOM levels | Use semantic h2 (style separately if visual differs) |
| Placeholder-only label | Form field label vanishes on focus | `placeholder` used as label | Add `<label>` with `for=`; placeholder for examples only |

## Phase 4 — UX Heuristic Violations

| Heuristic | Violation symptom | Common cause | Fix |
|-----------|-------------------|--------------|-----|
| 1 (Visibility of system status) | Submit button no loading state | Missing async-state UI | Spinner on tap, disable button while pending |
| 1 (Visibility) | Sidebar nav item not highlighted on current page | No active-route style | Style active route with bg + accent border |
| 2 (Match real world) | Error: "401 Unauthorized" shown to user | Raw HTTP response surfaced | Translate to "Please sign in to continue" |
| 2 (Match real world) | Date in MM/DD when locale is DD/MM | Hardcoded format | Use locale-aware date formatter |
| 3 (User control & freedom) | Multi-step form loses data on Back | No state persistence between steps | Persist to local state or session storage |
| 3 (User control & freedom) | Modal with no close, no Esc handler | Missing dismiss controls | Add × button + Esc key handler |
| 4 (Consistency & standards) | "Save" / "Update" / "Apply" for same op | Different teams owning different screens | Pick one verb in design system, enforce |
| 4 (Consistency & standards) | iOS bottom-sheet on one screen, modal on another | Different presentation patterns | Standardize per use-case in design system |
| 5 (Error prevention) | Delete button next to Save, same style | No visual differentiation of destructive actions | Destructive = red / outlined / requires confirm |
| 5 (Error prevention) | Free-text date entry | No constraint on format | Use date picker |
| 6 (Recognition over recall) | Active filter not visible after applied | No filter chip / pill | Add chip showing filter, × to clear |
| 6 (Recognition over recall) | "Format: YYYY-MM-DD" only in help text | Format hidden | Show inline placeholder example |
| 7 (Flexibility & efficiency) | No keyboard shortcuts in daily-use tool | Power-user features absent | Add shortcuts + visible hint (e.g. `⌘K`) |
| 8 (Aesthetic & minimalist) | Five primary buttons on one screen | No clear primary action | Promote one to primary, others secondary/tertiary |
| 9 (Recognize / diagnose / recover) | "An error occurred" with no detail | Generic catch-all error message | State problem + cause + recovery in plain text |
| 9 (Recognize / diagnose / recover) | Toast vanishes in 3s, error unread | Auto-dismiss too short | Persistent inline error at field |
| 10 (Help & documentation) | Icon-only button with no tooltip | Missing tooltip / aria-label | Add tooltip + aria-label |
| Affordance — false | Bold colored text isn't a link | Decorative styling using link conventions | Either make link or remove conventions |
| Affordance — hidden | Swipe-to-archive with no signifier | Gesture-only feature | Add visual cue or onboarding hint |
