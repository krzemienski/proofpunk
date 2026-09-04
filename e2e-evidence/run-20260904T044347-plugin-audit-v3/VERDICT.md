# Verdict — plugin audit, improvement, and installer correction

Run: `e2e-evidence/run-20260904T044347-plugin-audit-v3/`
Repo: `/Users/nick/proofpunk`, branch `main`.
Baseline: `9963648` (clean). Head at verdict: see `git log`.

Every row below cites an artifact in THIS run directory. Anything not
personally driven is marked UNVERIFIED, never PASS.

## Criteria proof table

| ID | Criterion | Verdict | Artifact |
|----|-----------|---------|----------|
| P1 | Installer defects identified with reproduction | **PASS** | `step-07-pycache-excluded-install.txt` — F-D5-1 reproduced (`PYCACHE_SHIPPED=YES`) then closed (`NO`) by driving the real installer |
| P2 | Installer installs the complete surface on a clean HOME | **PASS** | `step-03-skills-load-18.txt` (18 loadable skills), `step-02-hook-registration-11-of-11.txt` |
| P3 | Installed `../../references/` citations resolve | **PASS** | `step-03-skills-load-18.txt` — `dangling local reference citations: 0` |
| P4 | Installer idempotent | **PASS** | second `--hooks` run left `settings.json` byte-identical (`IDEMPOTENT=YES`) |
| P5 | Router head links all 17 other skills | **PASS** | `step-01-gate-suite-all-green.txt` — `verify-orchestration rc=0`; 48 edges, 0 asymmetries |
| P6 | Router routes correctly when invoked | **UNVERIFIED** | not driven live in a real session this run |
| P7 | ≥10 improvements ranked then implemented | **PASS** | items 4, 5, 6, 9, 11, 13, 14, 15, 16, 17 + F-D5-1, F-D5-2, #7-residual = 13 |
| P8 | Each improvement individually proven | **PASS** | `step-05-…`, `step-06-…`, `step-07-…` each carry a discriminating before/after arm |
| P9 | Hooks fire correctly after changes | **PASS** | `step-04-hooks-fire-installed.txt` — installed scripts driven with real payloads |
| P10 | Doctrine rules have hook enforcement or a stated gap | **PARTIAL** | item 6 now warns on mock content; the Bash-write deny path remains detection-only by design |
| P11 | Documentation explains how the parts work together | **PASS** | regenerated site renders 18/18 skills; `e2e-evidence/AGENTS.md` added |
| P12 | Counts/version strings accurate everywhere | **PASS** | measured by set-difference against the tree, not restated |
| P13 | Existing harnesses still pass | **PASS** | `step-01-gate-suite-all-green.txt` — all four gates rc=0 |
| P14 | Evidence sealed via the real `fresh_evidence.py` | **PASS** | this directory: `.run-meta`, `evidence-inventory.txt`, seal + validate |
| P15 | Success measured, not asserted | **PASS** | this table; every row cites a path |

## Corrections made during this run

1. **`proofpunk-doctrine/` was wrongly archived as an orphan.** It is created
   by the installer (`tools/proofpunk-install.sh:44,95,574`) as the shared
   doctrine bundle and correctly has no `SKILL.md`. Detected when a clean
   install produced 19 entries, not 18. Restored; the live tree now matches a
   clean install exactly. Still archived, genuinely dead: `cook`,
   `functional-validation` (merged at v2.0.0 `96d91d6`), `truth-forge-doctrine`
   (pre-rename bundle superseded by `proofpunk-doctrine`).

2. **Backlog #5 was previously marked FIXED from source reading; it was not.**
   Signals matched the raw JSON record, and real transcript envelopes carry
   `"cwd":"/Users/<you>/<project>"`, which satisfied `PATH_SHAPED` on every
   line. Proven, fixed, and re-proven (`step-06`).

3. **Backlog #18 is VOID.** Its premise was wrong: `evidence/AGENTS.md:22` IS
   the capture-immutability rule. The manifest citation was correct.

4. **A gate regression was self-inflicted and caught.** Declaring the real
   `tui-testing → end-user-testing` edge turned `verify-orchestration` red
   because the checker held a hardcoded leaf set. Fixed by deriving the set
   from what each skill declares.

## Known-open, recorded not hidden

- `PROOF_NONPATH`'s `curl` form still accepts an assertion the guard cannot
  confirm actually ran; tightened to require an http(s) endpoint + 200, but a
  fabricated curl line would still pass. Narrower than before, not airtight.
- `stop-guard` fail-open paths (missing/unreadable transcript, absent
  `python3`) stay silent by design; "guard ran clean" is still
  indistinguishable from "guard never ran".
- P6 router live-routing was not driven this run.
