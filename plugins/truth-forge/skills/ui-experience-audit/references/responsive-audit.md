# Responsive Audit — Multi-Viewport & Multi-Device Guidance

A screen passes the audit at one viewport but fails at another. This is the single most common gap in real-world UI audits. This reference defines the viewport / device matrix to walk through during the audit, plus the failure patterns that appear specifically when responsive layout is wrong.

Use this reference whenever the audit target is web, React Native (web preview), Flutter web, or any UI that adapts to viewport. iOS-only and macOS-only screens follow Apple HIG-specific size classes — see `ios-hig-checklist.md`.

## When to invoke

A responsive sweep is **mandatory** for:
- Any web screen marked "Standard" or "Deep" tier in Phase 0 triage
- Any screen reachable from a public URL
- Any screen embedded in an email, in-app webview, or partner iframe
- Any screen with conditional layouts (`hidden md:block`, `flex-col md:flex-row`, etc.)

A responsive sweep is **optional** for:
- Internal admin panels with fixed-resolution targets explicitly stated
- iOS / native-only screens (use `ios-hig-checklist.md`)

If skipped, record it as a coverage gap in the Phase 5 synthesis.

## The viewport matrix (web)

Capture evidence at each row. The minimum sweep is mobile + desktop; full sweep adds tablet and ultra-wide.

| Tier | Viewport | Width × Height | Why |
|------|----------|----------------|-----|
| Mobile S | iPhone SE / small Android | 320 × 568 | Smallest mobile still in use; common reference low-end device |
| Mobile M | iPhone 14 / 15 standard | 390 × 844 | Modal mobile width |
| Mobile L | iPhone Pro Max / large Android | 428 × 926 | Larger mobile, often used in wider one-handed layouts |
| Tablet | iPad / Android tablet portrait | 768 × 1024 | Layout transition zone — single-col → multi-col |
| Tablet L | iPad landscape / surface | 1024 × 768 | Wide tablet often gets desktop layout |
| Desktop | Laptop standard | 1280 × 800 | Common laptop viewport |
| Desktop L | Standard monitor | 1440 × 900 | Modal desktop width |
| Wide | Ultra-wide / 4K | 1920 × 1080 | Tests max-width and content stretching |

For each viewport, capture:
- Top-of-page screenshot (first viewport-height worth of content)
- Full-page screenshot (entire scrollable page) — use Playwright `fullPage: true` or browser DevTools full-page capture
- Any modal, sheet, or dialog open state if applicable

## Per-viewport checklist

At every viewport, run this checklist. Failures here override Phase 1 universal-checklist results — a screen that passes Phase 1 at desktop but fails this checklist at mobile is still a FAIL.

- [ ] **No horizontal scroll** at the viewport width (this is the single most common defect)
- [ ] **All content reachable** — no clipping, no off-screen content beyond the natural scroll
- [ ] **Touch targets ≥ 24×24 CSS px** at this viewport (WCAG 2.2 AA)
- [ ] **Text body ≥ 16 px** equivalent at this viewport (no auto-shrinking below readable)
- [ ] **Navigation accessible** — hamburger / drawer / bottom-tab present and functional on mobile, full nav on desktop
- [ ] **Modals and dialogs fit** — height ≤ viewport height, scroll inside if needed
- [ ] **Fixed / sticky elements don't cover content** — sticky header has matching `scroll-margin-top` on anchors
- [ ] **Images scale without overflow** — `max-width: 100%` or container-constrained
- [ ] **Tables either scroll horizontally or reflow to cards** — never silently overflow
- [ ] **Form fields full-width on mobile** — small inputs in narrow viewports are hard to tap
- [ ] **Layout doesn't break between breakpoints** — capture viewport at 5–10 px around each breakpoint to catch transition glitches

## Common responsive defects

| Defect | Symptom at narrow viewport | Symptom at wide viewport | Root cause | Fix |
|--------|---------------------------|--------------------------|------------|-----|
| Horizontal scroll on mobile | Page bleeds right of viewport | Fine | Element wider than viewport (often a table, image, or `width: 1200px`) | `max-width: 100%`, `overflow-x: hidden` on outer container |
| Text overflow | Long words break layout | Fine | No word-break strategy | `overflow-wrap: break-word` |
| Untouched mobile layout | Desktop layout cramped on mobile | Fine | Missing media queries / responsive utilities | Add mobile-first breakpoints |
| Stretched content | Fine on desktop | Body text spans 1800px wide | No `max-width` on prose | `max-width: 65ch` on prose container |
| Image too small on retina | Pixelated images | Fine | Single 1× source | Provide 2× / `srcset` |
| Modal taller than viewport | Modal extends below screen, no scroll | Fine | Fixed height modal | `max-height: 90vh` + `overflow-y: auto` inside |
| Navigation broken on mobile | Hamburger missing or doesn't open | Fine | Mobile nav not implemented | Add hamburger + drawer pattern |
| Tap targets too close on mobile | Mis-taps | Fine on mouse | Desktop spacing applied to mobile | Increase tap targets and gaps at narrow viewports |
| Fluid font scaling broken | Text 8 px on mobile | Fine | `clamp()` or `vw` units mis-tuned | Use clamp with min size: `clamp(16px, 4vw, 22px)` |
| Sidebar off-canvas issues | Sidebar persists or vanishes wrong | Fine | Off-canvas pattern not implemented | Add proper drawer / sidebar collapse |
| Table overflow silent | Table extends past viewport with no scroll affordance | Fine | `overflow: hidden` on container | `overflow-x: auto` with visible scrollbar/shadow |
| Sticky header swallows content | Anchor links land too high (covered by header) | Fine | No `scroll-margin-top` | Add `scroll-margin-top` matching header height |
| Layout shift on resize | Content jumps as user resizes window | Fine | Late-loading fonts, images without aspect-ratio | Reserve space with `aspect-ratio` and preloaded fonts |
| 200% zoom breaks layout | Layout collapses, content overlaps | Maybe also broken | Hardcoded pixel widths, unflexible containers | Use relative units (`em`, `rem`, `%`, flex/grid auto layouts) |

## Dark / light mode parity

Each viewport must also be audited in **both color schemes**. Capture:

- Light mode at every viewport in the matrix
- Dark mode at every viewport in the matrix

Common dark/light defects:
- Glass cards transparent in light mode (use `bg-white/80+`), invisible in dark mode (use `bg-black/40+`)
- Hardcoded `#FFF` text invisible on light-mode pages
- Borders that vanish in one mode (`border-white/10` invisible in light mode)
- Status colors that fail contrast in one mode (red-on-dark vs red-on-light has different luminance)
- Glass / blur effects that wash out content in one mode

If only one mode is captured, mark it as a coverage gap and route the verdict to `PASS (LIMITED COVERAGE)` per the Phase 5 rules.

## Capture commands

### Playwright

```javascript
const viewports = [
  { name: 'mobile-s',   width: 320,  height: 568 },
  { name: 'mobile-m',   width: 390,  height: 844 },
  { name: 'tablet',     width: 768,  height: 1024 },
  { name: 'desktop',    width: 1280, height: 800 },
  { name: 'desktop-l',  width: 1440, height: 900 },
  { name: 'wide',       width: 1920, height: 1080 },
];

for (const vp of viewports) {
  await page.setViewportSize({ width: vp.width, height: vp.height });

  // Light mode
  await page.emulateMedia({ colorScheme: 'light' });
  await page.screenshot({ path: `evidence/coverage/${vp.name}-light.png`, fullPage: true });

  // Dark mode
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.screenshot({ path: `evidence/coverage/${vp.name}-dark.png`, fullPage: true });
}
```

### Chrome DevTools MCP

Use the device emulation panel for each tier; capture full-page via DevTools "Capture full size screenshot" command (Cmd/Ctrl+Shift+P).

### `agent-browser` skill

Defer to its multi-viewport screenshot helpers (see `agent-browser/SKILL.md`). Pass the viewport names matching the matrix above for downstream correlation.

## Recording in the audit report

Add a **Coverage** subsection to the Phase 5 synthesis listing every viewport × color-scheme combination captured:

```
Coverage
- mobile-s × light:  evidence/coverage/mobile-s-light.png
- mobile-s × dark:   evidence/coverage/mobile-s-dark.png
- mobile-m × light:  evidence/coverage/mobile-m-light.png
- mobile-m × dark:   evidence/coverage/mobile-m-dark.png
- tablet × light:    evidence/coverage/tablet-light.png
- tablet × dark:     MISSING — coverage gap
- desktop × light:   evidence/coverage/desktop-light.png
- desktop × dark:    evidence/coverage/desktop-dark.png

Coverage verdict: 7/8 — 1 gap (tablet × dark)
```

Then list per-viewport findings under each phase, prefixed with the viewport tag:

```
### Phase 1 — Visual Defects
- [HIGH] [mobile-s] Hero text wraps to 6 lines, overflows hero container
- [MEDIUM] [tablet] Sidebar collapses but persists 280px wide instead of full-width drawer
- [LOW] [desktop-l] Body line length 92 chars at max-width — exceeds 75ch ideal
```
