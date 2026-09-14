# proofpunk v4 — status against P1-P15

Re-graded at HEAD. The previous version of this file graded a tree **110
commits behind** (it claimed "20 commits" from `a2fdeb9`; the measured figure
at re-grade time was 110), so every verdict in it described code that no
longer existed. That file is superseded, not amended.

Criteria source: `.planning/plugin-improvement-criteria.md` (operator-approved
2026-09-01). Verdicts restricted to PASS / FAIL / BLOCKED / UNVERIFIED per that
document's line 41.

Evidence: `e2e-evidence/run-20260914T220201-v4-matrix-regrade-installer/`
(`validate rc=0`, unpiped).

## Criteria-proof table

| ID | Criterion | Verdict | Evidence |
|---|---|---|---|
| P1 | Installer defects identified with reproduction | PASS | Real install into a clean temp HOME, rc=0, no blocker reproduced — `step-01-p1-p4-p12-p13.md` |
| P2 | Installer installs complete surface on clean HOME | **FAIL** | 19 skills + 10 hooks + 12 registrations, but **0 commands and 0 agents**; threshold requires 6 and 3 — `step-01-p1-p4-p12-p13.md` |
| P3 | Installed `references/` citations resolve | PASS | Installed layout: 136 real citations, 0 dangling — `step-01-p1-p4-p12-p13.md` |
| P4 | Installer is idempotent | PASS | Second install rc=0, settings.json byte-identical, registrations 12→12 — `step-01-p1-p4-p12-p13.md` |
| P5 | Router head links all other skills | PASS | Installed router references 18/18 non-router skills, 0 orphans — `step-02-p5-p6-p9-p14-p15.md` |
| P6 | Router routes correctly when invoked | UNVERIFIED | `verify-command-surface.py` yields a distribution, not a verdict: 14 runs scoring 0,3,3,4,4,4,4,4,5,5,5,6 of 6 — `step-02-p5-p6-p9-p14-p15.md` |
| P7 | ≥10 improvements ranked, then implemented | PASS | 12 commits in `c62c3e0~12..HEAD`, each with file + observable outcome — `step-03-p7-p8-p10-p11.md` |
| P8 | Each improvement individually proven | PASS | 11/12 cite an evidence path, 7/12 also carry a mutation arm; the 12th is whitespace — `step-03-p7-p8-p10-p11.md` |
| P9 | Hooks fire correctly, block + allow | PASS | 17 cases driven directly against the 10 installed scripts, unpiped rc — `step-02-p5-p6-p9-p14-p15.md` |
| P10 | Doctrine rules have enforcement or a stated gap | PASS | `references/enforcement-map.md`: "4 of 17 have a hook", "Globally unenforced: zero" — `step-03-p7-p8-p10-p11.md` |
| P11 | Documentation explains architecture | UNVERIFIED | Mechanical half passes (136 citations resolve). Prose-correctness review of 19 SKILL.md / 158,603 B not started — `step-03-p7-p8-p10-p11.md` |
| P12 | Counts/version strings accurate everywhere | PASS | `verify-counts.py` rc=0, now covering both marketplaces and both plugin manifests — `step-01-p1-p4-p12-p13.md` |
| P13 | Existing harnesses still pass | PASS | The four named harnesses, each unpiped rc=0 — `step-01-p1-p4-p12-p13.md` |
| P14 | Evidence run sealed via real `fresh_evidence.py` | PASS | init-run → seal rc=0 → validate rc=0; mutate → seal **rc=2 refused** — `step-02-p5-p6-p9-p14-p15.md` |
| P15 | Success is measured, not asserted | PASS | Every row above carries a permitted verdict and a citation; three invalid probes recorded as discarded — `step-02-p5-p6-p9-p14-p15.md` |

**PASS=12 FAIL=1 UNVERIFIED=2** (previously PASS=6 FAIL=2 UNVERIFIED=7).

## Three probes discarded during this re-grade

Recorded because a discarded probe is a finding, and because each would have
produced a false PASS:

1. **P3 was vacuous.** The first citation probe matched `](../path.md)` only.
   Installed skills cite `references/x.md` bare, so it checked **0** links and
   reported 0 dangling. Re-measured: 144 found, 8 flagged, 136 real after
   excluding `references/*-validation.md` glob prose.
2. **P9 reused P13's harness.** I first graded P9 from `test-hooks.sh` output
   (103 PASS, 0 FAIL). That is P13's subject, already closed with it — one
   artifact grading two criteria is asserting, not measuring.
3. **P9's second attempt read the wrong channel.** Only `stop-guard.sh` emits
   a JSON `decision`; the other nine signal by exit code, which is what the
   criterion asks for. "1/10 blocked" was the probe, not the hooks.

## P2 is the one FAIL, and it is a criterion-vs-installer question

The repo ships 7 commands and 3 agents under `plugins/proofpunk/`. No
installer flag installs either for the `claude-code` target — `--plugins`
covers OMP/OpenCode glue only. Those surfaces reach a user through the
marketplace path instead.

FAIL is honest as the criterion is **written**. Whether to rescope the
threshold to the skills surface, or to grow the installer a commands/agents
flag, is an operator decision and is not made here.

## Criteria-doc drift, filed not fixed

`.planning/plugin-improvement-criteria.md:20` says "18 skills" and `:23`
says "17 other skills". The tree has **19** skills (18 routable + the
`proofpunk` router). Both P2 and P5 therefore carry a stale threshold.

Not silently corrected: the document is operator-approved, and editing a
threshold while grading against it is grading yourself.

## What remains before v4 ships

1. **P11** — read all 19 SKILL.md files (158,603 B) for prose correctness:
   instructions contradicting `references/`, doctrine stated but unenforced,
   cross-skill conflict. `prompt-forge` (17,307 B) and `codebase-truth-audit`
   (15,330 B) are the largest and have never been reviewed.
2. **P6** — decide what a stochastic router harness means for a pass/fail
   gate: best-of-N, quorum, or accept distribution reporting.
3. **P2** — operator call on threshold vs installer scope.

Pushing and tagging remain authorization boundaries under
`.planning/plugin-improvement-criteria.md` D3.
