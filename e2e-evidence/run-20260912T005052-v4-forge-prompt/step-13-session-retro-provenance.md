# Session retro + intent reconstruction — PROVENANCE ONLY

**Classification: provenance, NOT release proof.** Nothing in this file clears
AC1, AC6, or install level (d). Those need distinct end-user proof.

Run: `e2e-evidence/run-20260912T005052-v4-forge-prompt`
Skills applied: `session-jsonl-retro`, `session-intent`

## session-jsonl-retro — labelled denominators

| Denominator | Count |
|---|---|
| Session files | 23 |
| JSON lines | 1,184 |
| Message-type lines | 326 |
| Records with text | 176 |
| Sessions with `human_typed` | 22 of 23 |

Speaker classified by payload shape, not `type`. Every `human_typed` prompt in
the corpus is a harness probe (`sdk_probe.py`, `verify-command-surface.py`
arms) — e.g. `Reply with exactly: AUTH_OK`, `Invoke the skill named exactly
'proofpunk'`, `Read once: ... reply with ONLY that absolute path`.

## session-intent — validated matrix

| Signal | Measured |
|---|---|
| Sessions with timestamps | 22 (23 files, 1 with no message-type lines) |
| Branches represented | `main` only — no discriminating signal |
| Repo paths referenced (validated extractor) | 23 |
| Sessions invoking `git commit` | 0 |
| **INTENT-PARTIAL** | **5** of 31 commits |
| **INTENT-UNRECOVERABLE** | **26** of 31 commits |

PARTIAL rows (single-file overlap, signal stated per doctrine #3):

| Commit | Best session | Overlap |
|---|---|---|
| `8537b3f` | `8a9e4029` | 1 |
| `93c479d` | `e7b33e68` | 1 |
| `d1ecbb0` | `e7b33e68` | 1 |
| `b4bd03a` | `8a9e4029` | 1 |
| `a41591a` | `e7b33e68` | 1 |

**COVERAGE GAP — a finding, not a footnote.** The transcripts do not cover the
v4 development window. Intent for 26 of 31 commits is unrecoverable from
session evidence, and is **not** backfilled from commit messages (doctrine #2:
the assistant authored them, making them claims about itself).

## Parser-validation defect (recorded, not hidden)

The first extractor read only `tool_use` input fields and reported **1**
unique repo path. An independent raw-payload regex oracle found **27 paths /
425 raw hits** — a 26-path undercount.

Consequence: the first published denominator ("3 touches / 1 file / zero
overlap") was **INVALID and is WITHDRAWN**, along with the alignment verdict
built on it (reported as 2 PARTIAL / 29 UNRECOVERABLE). The table above uses
the validated extractor and supersedes it.

Root cause: the alignment *method* was corrected after review, but the
*parser feeding it* was never validated — so a correct method ran on bad data
and produced a confident wrong answer.

## What the commit log shows that transcripts cannot

The v4 design record lives in commits, not sessions:

- `c752879` — v4 W1-W6: ACQUIRE stage, digest contract, steering guard
- `46ebae6` — v4 W7: render-counts.py owns every derived count
- `90bf91d` — **gauge4: effect-proven level d for install/verify** (2026-09-09)

That last commit establishes level (d) as deliberate design, not an accident
of the harness — relevant to W-C1, which must not re-specify a target the
maintainer intentionally built toward.
