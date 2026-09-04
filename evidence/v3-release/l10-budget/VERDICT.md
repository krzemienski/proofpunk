# VERDICT — Gauge #7 redesign (L10)

Measured: 2026-09-04 (UTC) | Repo HEAD at start: `73e928e` (working tree
had one untracked dir, `e2e-evidence/run-20260904T142528-v3-orchestrated/`,
unrelated to this scope, untouched)

## What was found

**The gauge was defective.** `tools/gauge-report.py:279-293` (pre-fix)
summed the `description` field across all 18 skills (13,955 chars,
live-measured) and compared that TOTAL against 1,536, labeling it "Claude
Code's 1,536-char skill-listing budget." Target: `<=1,536`.

I verified this against two independent primary-source layers:

1. **Repo-local secondary source** — `docs/skill-canon.md:171-172` states
   verbatim: "Claude Code's tier-1 gate is the 1,536-character
   `description` + `when_to_use` cap **per skill**, not a whole-listing
   budget." `docs/skill-canon.md:123` gives the verbatim vendor quote
   confirming the same.
2. **Independent live fetch** — I fetched
   `https://code.claude.com/docs/en/skills` directly this session (not
   trusting the repo's restatement alone) and confirmed the vendor's own
   text: the `description` field row says "the combined `description` and
   `when_to_use` text is truncated at **1,536 characters** in the skill
   listing"; the `when_to_use` field row says it "counts toward the
   1,536-character cap"; and the "Skill descriptions are cut short"
   troubleshooting section reveals the REAL aggregate mechanism is
   `skillListingBudgetFraction` — a **percentage of the model's context
   window** (default ~1%), configurable, and explicitly independent of the
   per-entry `skillListingMaxDescChars` cap ("each entry's combined text is
   capped at 1,536 characters **regardless of budget**").

The old target was unsatisfiable except by deleting ~89% of all routing
description text (13,955 → ≤1,536), which would have broken the adaptive
router L10 exists to build. Per the work order's own rule ("A gauge the
red-team agent can satisfy without doing the work is a failed gauge —
redesigned, not accepted"), a gauge only satisfiable by sabotaging the
feature it protects is the same failure in the opposite direction.

Full analysis with both primary-source quote sets:
`evidence/v3-release/l10-budget/gauge7-defect-analysis.md`.

## What changed

1. **`tools/gauge-report.py`** — redesigned `g_description_budget()`
   (gauge #7) to measure the real documented constraint: for each of the
   18 skills, `len(description) + len(when_to_use)` against the 1,536-char
   per-skill cap (`skillListingMaxDescChars`). Target: 18/18 under cap.
   Added a new gauge **#9** (L10) that reports the genuine open aggregate
   question — total `description`+`when_to_use` chars across all skills —
   with status **UNMEASURED**, because the real host mechanism
   (`skillListingBudgetFraction`) has no fixed numeric value in any sealed
   source and cannot be computed from static files (it depends on host,
   model, and live session context state). No other gauge's logic (#1–#6,
   #8) was touched. The tool's exit-code contract
   (`sys.exit(1)` while any gauge != PASS, `sys.exit(0)` when all PASS) was
   not altered.
2. **`docs/v3-gauges.md`** — row #7 updated to the new definition
   (baseline `18/18 (max 978/1536, implement)`, target `18/18`, measured
   `18/18 (max 978/1536, implement) — PASS`, evidence cited by
   `path@sha256` plus a pointer to the defect analysis). New row #9 added
   for the aggregate trend metric, `UNMEASURED`, following row #8's exact
   established pattern (baseline / real-target-rationale-in-Target-column /
   measured-value / evidence). Two new bullets added under "Notes on rows
   with no defined target" explaining the #7 redesign and the new #9 row —
   both scoped to row #7 and its notes per the task's ownership
   boundary.
3. **`evidence/v3-release/l10-budget/`** (new dir, my sole write scope
   besides the two files above) — `gauge7-defect-analysis.md`, this
   `VERDICT.md`, `evidence-inventory.txt`, and `mutation/` (24 files: full
   before/mutated/after-restore capture, sha256 manifest, exit codes
   recorded separately from stdout throughout).

## Proof level achieved

**Script-level and end-user-level**, both verified:

- **Script-level**: `python3 tools/gauge-report.py` runs clean (rc — 4
  gauges not-PASS is expected and unrelated to this change; see below),
  writes `gauge-report.md` + `gauge-report.json`.
- **End-user-level**: I ran the tool as an operator actually would — four
  full arms (pre-change baseline, post-redesign baseline, mutated,
  restored), each captured with stdout, stderr, and exit code in separate
  files (never piped-and-inspected `$?`), each JSON diffed field-by-field
  against its neighbor arm.

### No other gauge changed as a result of this edit

Compared full gauge JSON, `#1`–`#6` and `#8`, before vs. after the
redesign (`step-00-pre-change-gauge-report.json` vs.
`step-01-baseline-redesigned-gauge-report.json`):

| # | Before status/measured | After status/measured | Changed? |
|---|---|---|---|
| 1 | PASS / `18/18` | PASS / `18/18` | no |
| 2 | PASS / `baseline=48 mutated=47 restored=48 byte_identical=True` | same | no |
| 3 | UNMET / `29 unresolved (top-level: 0)` | same | no |
| 4 | UNMET / `0/6` | same | no |
| 5 | PASS / 4 gate exit codes all 0 | same | no |
| 6 | PASS / `18` | same | no |
| **7** | UNMET / `13955 vs 1536 (9.1x)` | **PASS** / `18/18 (max 978/1536, implement)` | **yes — intended** |
| 8 | UNMEASURED / `6186 bytes` | same | no |
| 9 | (did not exist) | UNMEASURED / `13955 chars` | new row, intended |

Only gauge #7 changed status (correctly, per the redesign), and gauge #9
is a genuinely new row. Every other gauge is byte-for-byte identical in
status and measured value.

### Mutation proof — gauge #7 can actually fail

Full arm sequence, all captured under `evidence/v3-release/l10-budget/mutation/`:

| Arm | Action | Gauge #7 status | Gauge #7 measured | Exit code |
|---|---|---|---|---|
| baseline (post-redesign) | none | PASS | `18/18 (max 978/1536, implement)` | 1 (unrelated gauges) |
| mutated | `visual-inspection`'s `description` inflated to 1,956 chars (via a real edit to `plugins/proofpunk/skills/visual-inspection/SKILL.md`, verified with the tool's own `parse_frontmatter_fields()` before writing) | **UNMET** | `17/18 (max 1956/1536, visual-inspection)` | 1 |
| restored | file restored from an independent backup written before mutation | PASS | `18/18 (max 978/1536, implement)` | 1 (unrelated gauges) |

The mutated arm's detail field reads: *"over the 1536-char per-skill cap:
[('visual-inspection', 1956)]"* — gauge #7 correctly names the exact skill
that violates the cap.

**Byte-identical restore, proven three independent ways:**
1. `sha256(restored file) == sha256(original file)` —
   `766e9f126f5ecd7b9baf61607a6a0ed5fc0626e91cd4d50157d2da3044a926cb` both
   times (`step-03-restore-sha256-proof.txt`).
2. `git status --short plugins/proofpunk/skills/visual-inspection/` and
   `git diff --stat` on the file both report **zero output** after
   restore — confirms the restored file matches the committed blob exactly
   (independent of my own sha256 capture).
3. `step-01-baseline-redesigned-run.log` and
   `step-04-final-restored-run.log` (the tool's full stdout on the
   pre-mutation and post-restore trees) share the **identical sha256**
   (`e680d553e068104523beb0654b6baa5c9f827f55c0a16ec20ec35ab0d067813a`) —
   byte-level proof the tool's entire output, not just gauge #7's field,
   is unchanged.

**Full-gauge-set recovery** (not just #7): all 9 gauges' status and
measured value in `step-04-final-restored-gauge-report.json` match
`step-01-baseline-redesigned-gauge-report.json` exactly, field-for-field
(verified programmatically, all 9 rows `MATCH`).

**Exit codes captured separately from stdout throughout** — every arm has
a dedicated `.rc` file written from the subprocess's `returncode`
attribute directly, never derived from a piped shell command.

## What did NOT change

- Gauges #1–#6, #8's logic, baseline, target, and measured values.
- The tool's exit-code contract: still `sys.exit(1)` while any gauge is
  not PASS, `sys.exit(0)` only when all gauges PASS. Verified: rc=1 in
  every arm here (4–6 gauges not-PASS throughout), consistent before and
  after.
- `gauge-report.md` / `gauge-report.json` output mechanism — unchanged
  `write_report()`.
- No other file outside `tools/gauge-report.py` (gauge #7 block only),
  `docs/v3-gauges.md` (row #7 + its notes only), and
  `evidence/v3-release/l10-budget/**` was written or modified.

## Post-mutation overall gauge-report state (informational, not this
lane's concern)

After redesign and restore, `python3 tools/gauge-report.py` reports
5/9 gauges PASS (up from 4/8 before this change — gauge #7 flipped
UNMET→PASS; #9 is new and UNMEASURED, doesn't count toward pass). The
remaining non-PASS gauges (#3 citations, #4 command-surface, #8 median
body size UNMEASURED, #9 aggregate exposure UNMEASURED) are owned by
other lanes/agents and untouched by this change.
