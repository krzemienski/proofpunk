# Content Quality Audit — Phase 3 Method

Visual layout can be flawless and content can still fail. A perfectly aligned code block whose syntax highlighting drops contrast to 2.1:1 fails. A chart that conveys data only by color fails. A page of text laid out at 95 characters per line fails readability even at perfect contrast. This phase audits content fitness-of-purpose, separately from the layout that holds it.

## Audit categories

| Category | When present in screen | Reference section |
|----------|----------------------|-------------------|
| Prose (paragraph text, headings, lists) | Almost always | [§ Prose](#prose) |
| Code blocks | Docs, IDEs, dev tools, READMEs | [§ Code blocks](#code-blocks) |
| Diagrams | Architecture, flowcharts, system maps | [§ Diagrams](#diagrams) |
| Data visualisations | Dashboards, analytics, reporting | [§ Data visualisations](#data-visualisations) |
| Tables | Structured data | [§ Tables](#tables) |
| Embedded media | Video, audio, iframes | [§ Embedded media](#embedded-media) |
| Form copy | Labels, helper text, errors, placeholders | [§ Form copy](#form-copy) |

Walk every category present in the screen. If a category is absent, skip it.

---

## Prose

| Check | Rule | Common failure |
|-------|------|----------------|
| Heading hierarchy | One `<h1>` per page, no skipped levels | h1 → h3 (skipped h2) |
| Body size | Web: 16 px (1 rem) min on mobile / iOS: 17 pt body | 12–14 px body text |
| Line length | 65–75 characters per line | Full-width text on 1440 px viewport |
| Line height | 1.5–1.75 for body, 1.2–1.4 for headings | Line-height 1.0 ("compressed") |
| Paragraph spacing | Visible whitespace between paragraphs | Walls of text without breaks |
| Body contrast | 4.5:1 (AA) | Light gray on white at 3.0:1 |
| Muted text contrast | Still 4.5:1 — "muted" is not exempt | `gray-400` on white |
| Emphasis | Used for meaning, not decoration | Everything bold, nothing emphasized |
| Link distinction | Underline OR distinct color + non-color cue | Color-only link distinction (color-blind fail) |
| Justified text | Avoid full justification (creates "rivers") | `text-align: justify` on narrow column |
| Hyphenation | Use sparingly; avoid mid-word breaks | Aggressive auto-hyphenation in narrow columns |
| Reading order | Visual order matches DOM / semantic order | CSS positioning that scrambles tab order |

### Failure examples
- Heading levels: a "Settings" page with a single `<div class="title">` styled to look like h1 — fails screen-reader navigation
- Line length: Medium-style 50-char column on mobile is fine; same column at desktop full-width 1600 px is unreadable
- Muted text: design systems often use `text-gray-400` for "secondary" — at #9CA3AF on white that's only 2.85:1, fails AA

---

## Code blocks

Code-block defects are common because designers focus on the page and developers focus on the code, but no one owns "how the code reads on the page".

| Check | Rule | Common failure |
|-------|------|----------------|
| Monospace font | `<code>` and `<pre>` use a monospaced face (SF Mono, JetBrains Mono, Menlo, Consolas, system-ui-monospace) | Code rendered in proportional font; alignment broken |
| Background contrast | Code-block bg distinct from page bg, but not so dark it fails text contrast | Light theme with 90% white code bg — invisible boundary |
| Syntax highlighting contrast | Every token color ≥ 4.5:1 against the code bg | Comment color at 3.1:1 — common Prism / Monokai default failure |
| Line wrapping | Long lines wrap or scroll horizontally — never silently truncate | Lines clipped at viewport with no scroll |
| Mobile horizontal scroll | If wrap disabled, horizontal scroll must be obvious (scrollbar or shadow) | Code clipped at right edge with no scroll affordance |
| Copy affordance | Copy button visible on hover (desktop) or always-visible (mobile) | No copy button — users must select-by-hand |
| Language label | Visible label or filename above the block | No indication of language (TypeScript? JavaScript? both?) |
| Line numbers | Aligned right of monospace gutter, dimmer than code text | Line numbers selectable on copy (paste includes them) |
| Code vs output distinction | Different visual treatment for code input vs program output | Both rendered identical; user cannot tell what to type |
| Inline code | `<code>` styled distinctly from prose (background tint, monospace) | Inline code looks like surrounding text |
| Long token handling | Long URLs / strings wrap with `overflow-wrap: anywhere` or `word-break: break-word` | Long token forces page horizontal scroll |
| Diff blocks | Added / removed lines distinguishable beyond color (+/− prefix, background) | Color-only diff fails for color-blind users |

### Verification on a screenshot
- Read three code-token colors against the code background and check contrast (use a contrast checker mentally: 4.5:1 minimum)
- Check whether a long line in the block exceeds the visible width — if the right edge has no `…` ellipsis, no scroll handle, and no wrap, that's silent truncation
- Check whether the code is selectable as text vs an image (selectable code is the floor; image-rendered code is a CRITICAL fail)

---

## Diagrams

Diagrams should communicate without requiring the user to interact, but should also reward interaction when offered.

| Check | Rule | Common failure |
|-------|------|----------------|
| Title above | Diagram has a heading or caption that names what it shows | Untitled diagram |
| Short description | 1–2 sentence summary near the diagram | Reader has to infer purpose |
| Alt text / `<title>` / `<desc>` | SVG has `<title>` and `<desc>` elements; img has alt | `alt=""` or `alt="image"` |
| Long description | Complex diagrams have a longer text description (linked, expandable, or below) | Detail only readable from the image |
| Color is not sole channel | Patterns, shapes, direct labels, or icons supplement color | Two lines distinguished only by red vs green |
| Direct labels | Labels next to elements when possible | Labels only in legend, requiring eye-jumps |
| Legend present and matched | Legend symbols match exactly what's in the diagram | Legend uses circles, diagram uses squares |
| Sufficient contrast | Strokes ≥ 3:1 against background, text ≥ 4.5:1 | Light gray strokes invisible in light mode |
| Interactive nodes (if present) | Clickable nodes have hover / focus state, keyboard-reachable, role declared | Click works on mouse only |
| Hover-only info | Any info revealed on hover also available via focus / tap / always-visible | Mobile / keyboard users get nothing |
| Resizes | Vector format (SVG) preferred; raster has 2× resolution | Pixelated PNG on retina |
| Print friendly | Black-and-white print preserves meaning | Color-only meaning lost on print |

### Mermaid / generated diagrams

When the diagram is generated (Mermaid, PlantUML, Graphviz), check:
- The rendered output, not just the source
- Whether arrow heads / dashed lines / box shapes survive at the rendered size
- Whether long node labels overflow boxes
- Whether dark mode inverts the diagram (often it does not)

---

## Data visualisations

Charts have the strictest requirements because they must also serve people who cannot see them at all.

| Check | Rule | Common failure |
|-------|------|----------------|
| Title | Chart has a clear text title | "Chart" or no title |
| Description / takeaway | One sentence of "what this chart shows" | User has to derive insight from raw data |
| Axes labelled | Both axes have units in the label | Y-axis says "Value", no units |
| Legend matched | Series labels in legend match colors in chart exactly | Legend in different order than stacked bars |
| Direct labels | Where space allows, label data points directly | All labelling forces eye-jumps to legend |
| Color not sole channel | Patterns, shapes, line styles, icons supplement color | Stacked bar with only color distinguishing 5 categories |
| Color-blind palette | Test with deuteranopia / protanopia simulator | Red-green pairing — fails for ~8% of men |
| Keyboard navigation | Each data point reachable via Tab + arrow keys | Mouse-only data exploration |
| Tooltip on focus | Tooltips trigger on focus, not just hover | Keyboard users can't see point values |
| Tooltip persists | Tooltip dismisses with Esc, not movement-only | Tooltip vanishes before being read |
| Resize 200% | Chart still readable at 200% zoom | Labels overlap at zoom |
| Alt text | `alt` describes purpose, not "chart" | `alt="bar chart"` (useless) |
| Alt + table | Complex charts: alt for purpose + linked data table for detail | Only alt; raw data inaccessible |
| No essential info on hover only | Important values readable from default state | Must hover on every point to read values |

### The Cesal-style alt-text recipe for charts

> `[Chart type] of [data] showing [reason for visualization]. [Link to data table or notable detail].`

Example: "Bar chart of monthly revenue Jan–Dec 2025 showing seasonal Q4 peak. Q4 revenue was 3.1× Q1. Underlying data table below."

---

## Tables

| Check | Rule | Common failure |
|-------|------|----------------|
| `<th>` for headers | Use `<th>` with `scope="col"` / `scope="row"` | All `<td>`; screen reader can't navigate |
| Caption | `<caption>` or visible heading | Untitled tables |
| Sortable headers | If sortable, indicate with icon + `aria-sort` | Sort works on click, no visual hint |
| Alternating rows | Row striping for readability when > 5 rows | Solid white wall of cells |
| Mobile reflow | Tables either scroll horizontally OR collapse to cards on narrow viewports | Tables overflow viewport silently |
| Tabular numerals | Numbers use `font-variant-numeric: tabular-nums` | Numbers in proportional font misalign |
| Currency / unit alignment | Numbers right-aligned, units consistent | Mixed currency formats in same column |
| Empty cells | Use `—` or "N/A", not blank | Blank cells indistinguishable from missing data |

---

## Embedded media

| Check | Rule | Common failure |
|-------|------|----------------|
| Video captions | All video has captions or transcript | None |
| Audio transcript | Audio-only content has full transcript | None |
| Autoplay | No autoplay with sound | Auto-plays on load |
| Controls keyboard accessible | Play / pause / seek reachable via keyboard | Mouse-only controls |
| Aspect ratio reserved | `aspect-ratio` or `width`/`height` attrs prevent CLS | Layout shift on load |
| Pause / stop control | Anything that moves > 5s has pause | Carousels with no pause |
| Reduced motion | Animations respect `prefers-reduced-motion` | Always animated |

---

## Form copy

| Check | Rule | Common failure |
|-------|------|----------------|
| Visible label | Every input has a `<label>` (placeholder is NOT a label) | Placeholder-only labels (vanish on focus) |
| Helper text | Constraints explained before submission | "Password too short" only after submit |
| Error placement | Inline, near field, after submit / blur | Toast that disappears in 3 s |
| Error language | Plain-language, says what to do | "Validation failure (E_INVALID_INPUT_42)" |
| Required marking | Asterisk + `aria-required="true"` + visible legend | Asterisk only, no legend |
| Autocomplete hints | `autocomplete="email"` etc. on common fields | No autocomplete attrs |
| Character count | Visible counter for max-length fields | No counter; user types past limit |
| Confirmation | Destructive / irreversible actions confirmed | One-click delete with no confirm |

---

## Output format

```
## Phase 3 — Content Quality Audit (<screen name>)

### Categories present
- Prose: yes
- Code blocks: yes (3 blocks)
- Diagrams: no
- Data viz: yes (2 charts)
- Tables: no
- Embedded media: no
- Form copy: yes

### Findings
- [SEVERITY] [CATEGORY] — <what you see> — <suggested fix>
```
