# Gauge #7 defect analysis — fabricated aggregate constraint

Measured: 2026-09-04 (UTC) | Repo HEAD at analysis time: `73e928e`
Method: primary-source verification against `docs/skill-canon.md` (repo-local
secondary derivation) AND a fresh live fetch of the actual vendor page
(`https://code.claude.com/docs/en/skills`, retrieved this session,
2026-09-04) — the primary source itself, not a repo restatement of it.

## The defect

`tools/gauge-report.py:279-293` (pre-fix) summed the `description` field of
all 18 skills and compared the **total** (13,955 chars, live-measured; the
baseline doc's frozen snapshot recorded 13,949 — see "Baseline drift" below)
against 1,536, calling that ceiling "Claude Code's 1,536-char skill-listing
budget." Target: `<=1,536`.

This is a fabricated constraint. 1,536 is not, and has never been, a
whole-listing budget in any documented Claude Code behavior.

## Primary-source proof

### Repo-local secondary source (already on disk, cited by the work order)

`docs/skill-canon.md:171-172`:
> Claude Code's tier-1 gate is the 1,536-character `description` +
> `when_to_use` cap **per skill**, not a whole-listing budget [2].

`docs/skill-canon.md:123` (verbatim vendor quote, in the Description Field
Length Rules table, "Claude Code (local skill)" row):
> the **combined** `description` + `when_to_use` text is **truncated at
> 1,536 characters** in the system-prompt skill listing (a display-time
> truncation, not a validation error) ... Verbatim: "the combined
> `description` and `when_to_use` text is truncated at 1,536 characters in
> the skill listing to reduce context usage"

`docs/skill-canon.md:381` (the C7 per-skill conformance table header) already
encodes the correct semantics as a column: "≤1536 combined w/ `when_to_use`
(Claude Code local listing budget — no `when_to_use` present, so this column
== description length)" — i.e. this repo's own canon document already
contains, unused, the exact per-skill check that gauge #7 should have been
running from the start.

### Independent primary-source verification (this session, live fetch)

I did not trust the repo's restatement alone. I fetched
`https://code.claude.com/docs/en/skills` directly this session and located
the same claim in the vendor's own words, in two places:

1. Frontmatter field table, `description` row:
   > Put the key use case first: the combined `description` and
   > `when_to_use` text is truncated at 1,536 characters in the skill
   > listing to reduce context usage.

2. Frontmatter field table, `when_to_use` row:
   > Appended to `description` in the skill listing and **counts toward the
   > 1,536-character cap**.

3. Troubleshooting section, "Skill descriptions are cut short" (this is the
   section that actually describes the *aggregate* mechanism — and it is
   NOT a fixed character count):
   > Claude Code loads a listing of skill names and descriptions into
   > context so Claude knows what's available. The listing always contains
   > every skill name, but if you have many skills, Claude Code shortens
   > descriptions to fit the listing's character budget... **The budget
   > scales at 1% of the model's context window.** When the listing
   > overflows, Claude Code drops descriptions starting with the skills you
   > invoke least...
   >
   > To raise the budget, set the `skillListingBudgetFraction` setting
   > (e.g. `0.02` = 2%) or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment
   > variable to a fixed character count... You can also trim the
   > `description` and `when_to_use` text at the source: put the key use
   > case first, since **each entry's combined text is capped at 1,536
   > characters regardless of budget**. The cap is configurable with
   > `skillListingMaxDescChars`.

This is unambiguous and confirms both halves of the repo's own claim:
- The 1,536 number is a **per-entry** cap (`skillListingMaxDescChars`,
  default 1,536), applied to each skill's combined `description` +
  `when_to_use` independently.
- The actual **aggregate** mechanism is `skillListingBudgetFraction`, a
  **percentage of the model's context window** (default ~1%), not a fixed
  character count. Its real value therefore depends on which host, which
  model, and what else already occupies context in a given session — it
  cannot be computed from static repository files alone.

**Conclusion: I confirm the defect. There is no documented whole-listing
1,536-char budget anywhere in the primary source. The old gauge #7 compared
an aggregate sum against a per-item cap — a category error.**

## Why the old target was unsatisfiable without destroying the router

Per-skill, this repo is nowhere close to the real cap: max combined length
is 978 chars (`implement`), 63.7% of the 1,536 per-skill cap, with 46 chars
of headroom below even the 1024-char open-spec ceiling
(`description-budget-baseline.md`).

But summed across all 18 skills, the aggregate is 13,955 chars — 9.1x the
per-skill number the old gauge mistook for an aggregate budget. Satisfying
`total <= 1,536` would require deleting roughly 88.9% of all routing
description text (13,955 -> ≤1,536), leaving an average of ~85 chars of
description per skill. That is not a real target: it directly conflicts
with L10's own purpose (an adaptive router that discriminates between 18
skills), which requires enough descriptive text per skill to disambiguate
"debug this" from "review this" from "audit this." A gauge that can only be
satisfied by making the router itself worse is not a quality gate — it is
self-defeating, and per the work order's own rule ("A gauge the red-team
agent can satisfy without doing the work is a failed gauge — redesigned,
not accepted"), the reverse failure mode also applies here: a gauge that
*cannot* be satisfied without actively sabotaging the feature it is meant
to protect is equally a failed gauge, just failed in the other direction.

## Baseline drift note

`description-budget-baseline.md` (sealed 2026-09-04, HEAD `9963648`) records
the aggregate as 13,949 chars. A live re-measurement this session via the
tool's own `load_skills()` reports 13,955 — a 6-char drift, consistent with
this doc's own stated policy ("this file's Measured column... re-run it and
trust its output, not this document's cache," `docs/v3-gauges.md:5-7`). The
redesigned gauge below reports the live number, not the frozen baseline
snapshot, matching gauges #1, #3, #6, and #8's existing convention of
recomputing from `load_skills()` on every run rather than reading numbers
out of baseline prose.

## Redesign

Gauge #7 is redesigned to measure the constraint that is actually
documented and actually satisfiable: **per-skill** `description` (+
`when_to_use` when present) against the 1,536-char truncation cap, 18/18
target. See `tools/gauge-report.py`'s `g_description_budget()` for the
implementation and `docs/v3-gauges.md` row #7 for the updated board entry.

A second row (#9, L10) was added for the genuine open question — aggregate
listing-pressure exposure — per the work order's explicit instruction to
"consider whether a second honest row is warranted" and follow row #8's
UNMEASURED precedent. See "Row #9" section below.

### Why row #9 exists and why it carries no target

`description-budget-baseline.md`'s own "Open / UNRESOLVED" section already
says the aggregate question "is not measured here — it requires driving a
live host, not reading files." My independent primary-source read confirms
exactly why: the real mechanism (`skillListingBudgetFraction`, default ~1%
of context window) has no fixed numeric value in any sealed source in this
repo, and cannot have one — its value depends on which host, which model,
and how much else is in context during a live session, none of which this
static-analysis tool can observe. Inventing a fixed aggregate threshold
(the old gauge's 1,536) was exactly the error this redesign fixes; adding a
*new* fixed threshold in its place would repeat the same mistake with a
different number. Per the work order: "If no numeric target exists in any
sealed source, mark it UNMEASURED — do NOT invent a threshold." Row #9
therefore reports the real, live-measured aggregate character count (a
genuine, sealed-evidence-backed number, useful for trend tracking, and the
number the old gauge #7 was — correctly — computing all along) with status
UNMEASURED and an explicit detail explaining why no target exists,
following row #8's exact pattern.

## Sources cited

- `docs/skill-canon.md:171-172` (repo-local secondary derivation)
- `docs/skill-canon.md:123` (repo-local secondary derivation, verbatim
  vendor quote)
- `docs/skill-canon.md:381` (repo-local secondary derivation, per-skill
  table header already encoding correct semantics)
- `https://code.claude.com/docs/en/skills` (primary source, live fetch,
  retrieved 2026-09-04, this session — frontmatter field table and
  "Skill descriptions are cut short" troubleshooting section)
- `evidence/v3-release/00-baseline/description-budget-baseline.md` (sealed
  per-skill measurement data, F-C7-2 finding)
