# Visual Inspection — Mood Ring UI (visual-inspection skill)

**Driven by:** AI as end user via browser_* tools (real Chromium screenshots, driven navigation).
**Evidence examined (content, personally reviewed):**
step-18-final-index-all.png, step-10-filter-fire.png, step-11-filter-sob.png,
step-13-edit-form-preselect.png — all in e2e-evidence/run-20260808T202017-mood-ring/.

## Universal checklist (7 sections)

1. **Layout & alignment** — post headers, bylines, Edit actions align on the flaskr grid;
   filter bar sits above the list; no overflow at 1920px. PASS.
2. **Typography & readability** — serif headings / sans body per existing stylesheet; bylines
   italic slate. PASS — except V-01 below.
3. **Color & contrast** — V-01: active "All" pill is `#377ba8` text on `#377ba8` background
   (base `a { color:#377ba8 }` meets `.mood-filter a.active { background:#377ba8 }`):
   the label is INVISIBLE in step-18 (first pill renders solid blue, empty). Emoji pills
   unaffected (color glyphs ignore `color`). WCAG 2.2 fails 1.4.3 (contrast ~1:1) and
   1.4.1 (active state conveyed by color whose foreground vanished). **HIGH.**
4. **Interactive-state visibility** — hover/focus states unchanged from base flaskr (no
   focus outline removal introduced). Active filter pill visible for emoji; broken for
   text ("All") — same root cause as V-01.
5. **Imagery/icons** — emoji render in-color at consistent size in both title spans and
   filter pills (steps 10/11/13/18). PASS.
6. **Content states** — empty state ("No posts with this mood yet — write one!") verified
   in browser on empty DB and in step-14 (0-article filter). Populated/loading/error:
   loading n/a (server-rendered), error state = flaskr flash (verified in step-15). PASS.
7. **Localization hazards** — emoji are locale-neutral; date format pre-existing. PASS.

## Platform checklist (web / WCAG 2.2 spot items)

- Keyboard: filter bar is real `<a href>` links — focusable/operable. PASS.
- `aria-label="Filter posts by mood"` present on the nav. PASS.
- Contrast: V-01 (above) is the only failure found.

## Findings

| id | severity | finding | evidence |
|----|----------|---------|----------|
| V-01 | HIGH | Active "All" filter label invisible (blue-on-blue) | step-18-final-index-all.png — first pill solid blue, no glyph |

## Remediation (Iron Rule — fix the real system)

`style.css`: add `color: white` to `.mood-filter a.active`. Re-verified by fresh
screenshot after fix (see step-19 in the evidence run) and pytest re-run.

**Verdict after remediation: PASS** (visual quality of the changed UI; behavioral claims
are covered by the driven gate evidence in 02-VALIDATION.md).
