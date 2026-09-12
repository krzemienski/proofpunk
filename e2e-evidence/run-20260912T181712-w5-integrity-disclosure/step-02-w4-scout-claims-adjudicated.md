# W4 partial: a scout's five claims, each checked against the tree

ScoutSkills returned after ~40 minutes with five defect claims. Two are
real, two are wrong, one is cosmetic. They are adjudicated here rather
than adopted, because a subagent report is a claim and this session has
already been burned four times by findings the instrument manufactured.

## CONFIRMED — ci-gates.md asserted its own disuse, falsely
Claim: production-readiness:41-43 instructs loading ci-gates.md, while
ci-gates.md:7-14 says no executing skill loads it.

Both sides read and verified:
```
production-readiness/SKILL.md:41-43 —
     When the audit finds no pre-commit or CI gates configured, load
     `../../references/ci-gates.md` and propose its P0→P1→P2 rollout rather
     than inventing gate criteria ad hoc.

references/ci-gates.md:7-14 (before this fix) —
  **Wiring gap (as of this note):** no executing skill loads this file mid-workflow —
  it is currently cited only descriptively in `skills/proofpunk/SKILL.md`'s reference
  table. The natural loader is `production-readiness`'s codebase-audit lens (its own
  skill-local production-readiness-audit reference): when that audit finds a project has no
  pre-commit/CI gates configured, it should load this file to propose a P0→P1→P2
  rollout rather than inventing gate criteria ad hoc. That wiring change is not made
  here — a follow-up lane must add the load instruction to
  `skills/production-readiness/SKILL.md`.
```
The note asks a follow-up lane to add a load instruction that already
exists three files away. A reference asserting its own disuse is worse
than one saying nothing: it tells the reader the opposite of what the
tree does. This is exactly the defect class W4 exists to find, and no
gate could have caught it — both files are internally consistent.
Fixed: the note now states its loader with a file:line citation.

## CONFIRMED (cosmetic) — the router undercounts itself
proofpunk/SKILL.md said '17 delivery skills' in four places against 18
skill directories. Measured:
  skill dirs on disk   : 18
  named in router body : 18
  missing from router  : none
The router names all 18 and routes to all of them; '17' meant 'other
than me', which is defensible but ambiguous in a repo where every other
count is 18. Disambiguated rather than renumbered — P5's 17/17 was
measuring the right thing.

## REFUTED — session-intent script paths
Claim: SKILL.md:112-117 cites references/scripts/... but the scripts
live at references/claude-code-analyzer/scripts/*.
```
cited at SKILL.md:112 —
  - `references/scripts/analyze.sh` — primary session-analysis driver; run first.
on disk —
  references/scripts/analyze-claude-md.sh
  references/scripts/analyze.sh
  references/scripts/fetch-features.sh
  references/scripts/github-discovery.sh
```
The cited path is exact. No claude-code-analyzer directory exists.

## REFUTED — 'wrong relative path' in three skills
Claim: visual-inspection, ui-experience-audit and full-functional-audit
cite references/*-validation.md with no own references/ dir, so the
path is wrong and should be ../../references.

Every citation in all three resolved from its own skill directory:
  visual-inspection        ../../references/defect-pattern-database.md      resolves=True
  visual-inspection        ../../references/end-user-actor.md               resolves=True
  visual-inspection        ../../references/ios-hig-checklist.md            resolves=True
  visual-inspection        ../../references/severity-model.md               resolves=True
  visual-inspection        ../../references/web-wcag-checklist.md           resolves=True
  ui-experience-audit      ../../references/defect-pattern-database.md      resolves=True
  ui-experience-audit      ../../references/end-user-actor.md               resolves=True
  ui-experience-audit      ../../references/ios-hig-checklist.md            resolves=True
  ui-experience-audit      ../../references/severity-model.md               resolves=True
  ui-experience-audit      ../../references/web-wcag-checklist.md           resolves=True
  ui-experience-audit      references/content-quality-checklist.md          resolves=True
  ui-experience-audit      references/interactive-element-audit.md          resolves=True
  ui-experience-audit      references/responsive-audit.md                   resolves=True
  ui-experience-audit      references/ux-heuristics-checklist.md            resolves=True
  full-functional-audit    ../../references/end-user-actor.md               resolves=True
  full-functional-audit    ../../references/evidence-contract.md            resolves=True
  full-functional-audit    ../../references/platform-routing.md             resolves=True
  unresolvable: 0
../../references IS correct from a skill directory. ui-experience-audit
legitimately has both its own references/ and shared ones, which is what
made the pattern look inconsistent. verify-citations.py agrees: rc=0.

## Score
  2 real (1 substantive, 1 cosmetic), 2 refuted, of 5 claims checked.
  A 40% false-positive rate is why claims get adjudicated, not adopted.

## W4 remains OPEN
This covers five claims about four skills. It is not the prose
correctness review of all 18, and P11 stays UNVERIFIED. The two
largest skills — prompt-forge (17,307 B) and codebase-truth-audit
(15,330 B) — have still not been read.
