# Gauge #7 — live host listing behavior

Measured: 2026-09-04T14:43:56Z | Repo HEAD SKILL.md sha256
`b1e50906fc10b89471a837eaaef1d78c2ded0c10edd538782bc667adb5d2a3c9`
Host: Claude Code `2.1.239` via `claude_agent_sdk`, model `cc/claude-opus-5[1m]`.
Plugin loaded: `SdkPluginConfig(type="local", path=/Users/nick/proofpunk/plugins/proofpunk)`.
`setting_sources` was **not** cleared — this session also loaded the operator's ambient skill corpus.

This file is a measurement, not a gauge-report.py edit. Lane E owns that tool.

## What the host actually did

Verbatim CLI WARN, captured from the live `live_listing_content.py` session and
persisted at `step-16-host-warn.log`:

```
2026-09-04T14:43:56.945Z [WARN] Skill listing over budget: 1574 skills, 553023 chars > 150000 budget — descriptions will be truncated. Run /skills to disable some, or raise skillListingBudgetFraction in settings.
```

sha256 `a90eff733771a2d46c9150e561de03589c5efcc3e208b700cef0ffc7aa610b31`

Derived facts from that one line:

| Field | Value | Source |
|---|---|---|
| Action | **truncate descriptions** (host's own words) | WARN text |
| Aggregate budget this session | **150000 chars** | WARN text (`> 150000 budget`) |
| Listed skills (host-wide) | **1574** | WARN text |
| Listed description chars (host-wide) | **553023** | WARN text |
| Ratio | 553023 / 150000 = **3.69×** over | arithmetic on the WARN numbers |

This is **not** the 1,536 number. 1,536 never appears in the live host output.

## What 1,536 is (and is not)

`docs/skill-canon.md` and `evidence/v3-release/l10-budget/gauge7-defect-analysis.md`
already record 1,536 as `skillListingMaxDescChars` — a **per-skill** display
truncation cap, not a whole-listing budget. Live confirmation:

- No proofpunk skill description is within 46 chars of 1,536 (max 978,
  `implement`; head is shortest at 718). See
  `evidence/v3-release/00-baseline/description-budget-baseline.md`.
- The host WARN names a **different** ceiling: 150000 chars for the whole
  listing, via `skillListingBudgetFraction`.

Comparing proofpunk's ~13,955 description chars against 1,536 is a category
error: it treats a per-entry cap as an aggregate budget. Satisfying
`sum(descriptions) <= 1536` would require deleting ~89% of routing text and
would fight the router's job.

## What the SDK init payload showed

From `step-07-listing-dump.json` (and the same init block in
`step-15-listing-content.json`):

- `init.skills` is a **name-only** list (1208 strings). No descriptions.
- Namespaced proofpunk skills present: **17** (missing `proofpunk:implement`).
- `proofpunk:implement` **is** in `init.slash_commands` (the plugin also
  ships `commands/implement.md`).
- Bare `implement` is absent from `init.skills`.

Whether that one missing skill-name is caused by the listing-budget rank/drop
path, or by a command/skill name collision on `proofpunk:implement`, is
**UNVERIFIED**. This session was not an isolated-plugin control
(`setting_sources=[]`). The 1574 / 553023 figures include the operator's
entire installed corpus, not proofpunk alone.

## What the model reported vs what the host logged

`step-15-listing-content.json` model reply (self-report, not host):

- `listing_truncated: false`, `warning_verbatim: null`
- `implement_present: true`
- mixed command names (`proofpunk:forge-prompt`, `proofpunk:install`, …)
  into `proofpunk_names`
- claimed `proofpunk:prompt-forge` description = 1049 chars (the skill's
  real description is 887) and most other proofpunk descriptions as 0

The model's listing introspection is **not a measurement**. It contradicts
the host WARN on the same session. Verdicts below cite the WARN, not the
model JSON.

## Routing still worked

Six live goals (build / audit / bug / proof / planning / nothing) all
reached the router-table target, including `proofpunk:implement` on the
build ask — `Skill` loaded it by exact name even though that name was
absent from `init.skills`. See `step-14-live-routing-summary.json`.

So: over-budget **truncates descriptions**; it does **not**, on this host
and this ask, prevent an exact-name `Skill` load of a proofpunk delivery
skill.

## Recommended restatement of gauge #7 (Lane E decides)

Do **not** invent a new numeric aggregate target. The live budget is a
fraction of the context window (here 150000 chars) and moves with host,
model, and whatever else is installed.

Falsifiable replacement, two rows:

1. **Per-skill cap (already true, keep as #7 or fold into spec-basics):**
   every skill's resolved `description` (+ `when_to_use` if present) `<= 1536`.
   Target `18/18`. This is the documented `skillListingMaxDescChars` check.
2. **Host-behavior row (new, no fixed char target):** a live session with
   the plugin loaded must persist the CLI line matching
   `Skill listing over budget:` **or** the absence of that line.
   - If the WARN is absent: record `over_budget=false` and the session's
     `n_skills` / description-char total from the same debug log.
   - If the WARN is present: record `skills`, `chars`, `budget`, and the
     host's named action (`descriptions will be truncated`). PASS is
     "we captured the host's real action", not "chars <= N".

Optional isolated arm, not required to close #7: rerun with
`setting_sources=[]` and only the local proofpunk plugin, to see whether
18 skills / ~13955 chars alone stay under the session budget. That arm
was **not** run here.

No description rewrite is recommended. The head is already the shortest
description (718). Shrinking the other 17 does not address a 150000-char
host-wide ceiling dominated by 1574 installed skills.
