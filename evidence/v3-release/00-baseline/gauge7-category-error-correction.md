# Gauge #7 — an UNMET row that was measuring the wrong thing

Measured: 2026-09-04 | Repo HEAD: `73e928e`
Orchestrator-verified against the live host, not accepted from a lane report.

## The defect

Gauge #7 read:

> Total description chars vs Claude Code's 1,536-char skill-listing budget
> — **13,955 vs 1,536 (9.1×) — UNMET**

It summed all 18 skills' `description` fields and compared the **total**
against 1,536. That is a category error: **1,536 is a _per-skill_ display
truncation cap** (`skillListingMaxDescChars`), not an aggregate budget.

Comparing a sum against a per-entry cap makes the target unsatisfiable except
by deleting ~89% of all routing description text — which would sabotage the
router the gauge exists to protect. A gauge that can only be satisfied by
breaking the thing it measures is a fabricated constraint.

## How it was verified — the live host, not the docs

The decisive evidence is the host's own WARN, captured from a live
`claude_agent_sdk` session
(`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-head/step-16-host-warn.log`,
sha256 `a90eff733771a2d46c9150e561de03589c5efcc3e208b700cef0ffc7aa610b31`):

```
[WARN] Skill listing over budget: 1574 skills, 553023 chars > 150000 budget
— descriptions will be truncated. Run /skills to disable some, or raise
skillListingBudgetFraction in settings.
```

Three facts follow, none of them inferred:

1. **The real aggregate ceiling on this session was 150,000 chars** — not
   1,536. The two numbers differ by ~100×.
2. **`1536` never appears in any live host output.** A grep across the
   entire lane evidence directory returns it only in this repo's own analysis
   files — never in a host emission.
3. **The host's response to over-budget is `descriptions will be truncated`**
   — it truncates, it does not drop skills or refuse to route.

The aggregate ceiling is `skillListingBudgetFraction`, a **percentage of the
model's context window** — host-, model-, and corpus-dependent. It has no
fixed numeric value in any sealed source, so none may be invented.

## Why this matters beyond one row

The 553,023 chars in that WARN are the operator's **entire installed corpus of
1,574 skills**, not proofpunk's 18. Proofpunk's ~13,955 chars are ~2.5% of
the pressure. Shrinking 18 descriptions would not measurably move a host-wide
ceiling dominated by 1,574 other skills — so the old gauge would have driven
real work that could not possibly achieve its stated goal.

This is the repo's own **defect Class 4** (a claim stated above its proof
level) applied to a gauge target rather than a status: a number was adopted
from documentation, its meaning assumed rather than measured, and it then
governed a release gate.

## The correction

| | Before | After |
|---|---|---|
| **#7** | total 13,955 vs 1,536 → **UNMET** | per-skill under the real 1,536 cap → **18/18 PASS** (max 978, `implement`) |
| **#9** | did not exist | aggregate 13,955 chars → **UNMEASURED**, trend-tracking only, explicitly no invented target |

Board: **4/8 PASS → 5/9 PASS**. The improvement is not a relaxed target — #7
now measures the constraint that actually exists, and the aggregate remains
visible as an honestly-unmeasured row rather than being deleted.

## Routing still works under real listing pressure

Six live routing probes ran in the same over-budget session and all six
reached their router-table target, including the negative "routes to nothing"
case (`step-14-live-routing-summary.json`, 6/6 match, real per-probe costs
$0.62–$1.46). Notably `proofpunk:implement` loaded by exact name even though
that name was absent from the truncated `init.skills` listing.

So over-budget truncates descriptions; on this host it did **not** prevent an
exact-name skill load.

## Open / UNRESOLVED

- **The isolated-plugin control arm was not run.** The 1,574-skill / 553,023-char
  figures include the operator's whole corpus. Whether proofpunk's 18 skills
  alone stay under budget is **UNVERIFIED** — it needs a `setting_sources=[]`
  run with only the local plugin loaded.
- **One skill name (`proofpunk:implement`) was missing from `init.skills`
  (17/18).** Whether that is the listing-budget drop path or a
  command/skill name collision is **UNVERIFIED**; the isolated control above
  would discriminate. Recorded, not guessed.
- The model's own listing self-report contradicted the host WARN in the same
  session (`listing_truncated: false` while the host logged truncation). Model
  introspection is not a measurement; every verdict here cites the host WARN.
