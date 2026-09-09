STATUS: COMPLETE

# A6 — Skill-Graph Forensics + 18-Row Skill Scorecard

Lane A6 of the Proofpunk v3 recon sweep. Read-only. All 18 `SKILL.md` files
read end to end, plus every per-skill `references/`, `assets/`, `scripts/`
sub-file discovered by glob (62 per-skill reference files across 8 skills, 4
assets dirs, 6 scripts dirs — see per-row counts in the scorecard). Cross-
checked against `plugins/proofpunk/README.md`, `docs/consolidation-decisions.md`,
`docs/discovery-register.md`, `docs/commit-archaeology.md`,
`docs/session-intent-ledger.md`, `evidence/v3-release/00-discovery/*`,
`tools/build-site.py`, and every dated top-level release report.

## Summary

- **18 skill dirs on disk**, all 18 `name:` frontmatter fields exactly match
  their parent directory name (0/18 mismatches).
- The `proofpunk` router's Skill-calls table lists **exactly the other 17
  skills** — set-difference against real dirs is empty in both directions
  (no missing skill, no phantom name).
- **48/48 Calls-table edges are reciprocated** by a matching `Called by:`
  line on the target skill, and vice versa. Zero unreciprocated edges either
  direction.
- **Zero cycles** in the 48-edge call graph (DFS-verified).
- **Single root confirmed**: only `proofpunk` has `Called by: nothing`.
- **True max depth (longest path) = 5**: `proofpunk -> production-readiness
  -> full-functional-audit -> ui-experience-audit -> visual-inspection ->
  end-user-testing`. Router fan-out depth is trivially 1 for all 17 (star
  topology by design); the substantive doctrine-chain depth (excluding the
  router itself) is 4.
- **0 genuinely broken reference citations** across all 18 skills (one
  apparent break — `stack-testing`'s `scripts/playwright/` — resolves to a
  real directory, not a missing file; reclassified OK).
- **D8 ("one massive skill") is RESOLVED**, not open: the operator's own
  dictation self-glosses as a request to strengthen the router head, already
  implemented and verified reciprocal at current HEAD.
- **Dead names `cook` and `functional-validation`: 49 + 39 = 88 non-evidence
  hits, ALL 88 classified HISTORICAL PROVENANCE PROSE, ZERO live guidance.**
  The brief's specific claim of a hardcoded `/proofpunk:cook` "around line
  311" of `tools/build-site.py` is **FALSE** — that line reads
  `/proofpunk:install`, and the string "cook" (any case) does not appear
  anywhere in that 611-line file.

## 1. The 18-Row Scorecard

Columns: frontmatter `name` vs directory match; description length in chars;
whether the description reads as a routing trigger (quoted user phrases the
router can pattern-match) vs plain prose; scope-boundary overlap (neighbour
skills named in the skill's own "Not for..." clause); sub-reference citation
resolution; raw `references/`/`assets/`/`scripts/` file counts; inbound
edges (who calls it, per reciprocal `Called by:` lines); outbound edges (who
it calls, per its own "Skill calls" table); max chain depth reachable
starting from this skill; and whether it has been exercised in a captured
`e2e-evidence/` VERDICT.md or FIXES.md artifact.

| Skill | name==dir | Desc len (chars) | Routing-trigger quality | Scope boundary — overlap named with | Sub-ref citations resolve | references/ | assets/ | scripts/ | Inbound edges (Called by) | Outbound edges (Calls) | Max chain depth from here | Verified today? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `brainstorm` | YES | 833 | TRIGGER (5 quoted phrases) | full-functional-audit, implement | 1 cited / 1 resolve (incl. shared refs) | 0 | 0 | 0 | 2: implement, proofpunk | none (leaf) | 0 | YES — named in 2 e2e-evidence VERDICT/FIXES files |
| `codebase-truth-audit` | YES | 759 | PROSE-ONLY (no quoted user phrases) | implement, session-intent, validation-plan | 2 cited / 2 resolve (incl. shared refs) | 1 | 0 | 1 | 2: production-readiness, proofpunk | 3: session-intent, end-user-testing, root-cause-debugging | 2 | YES — named in 3 e2e-evidence VERDICT/FIXES files |
| `end-user-testing` | YES | 838 | TRIGGER (5 quoted phrases) | stack-testing, ui-experience-audit, visual-inspection | 7 cited / 7 resolve (incl. shared refs) | 0 | 1 | 1 | 13: codebase-truth-audit, full-functional-audit, implement, mobile-validation-runner, plan-hardening, production-readiness, red-team-eval, root-cause-debugging, tui-testing, ui-experience-audit, validation-plan, visual-inspection, proofpunk | none (leaf) | 0 | YES — named in 8 e2e-evidence VERDICT/FIXES files |
| `full-functional-audit` | YES | 811 | TRIGGER (5 quoted phrases) | root-cause-debugging, ui-experience-audit | 3 cited / 3 resolve (incl. shared refs) | 0 | 0 | 0 | 2: production-readiness, proofpunk | 4: end-user-testing, ui-experience-audit, root-cause-debugging, tui-testing | 3 | YES — named in 4 e2e-evidence VERDICT/FIXES files |
| `implement` | YES | 978 | TRIGGER (5 quoted phrases) | brainstorm, validation-plan | 2 cited / 2 resolve (incl. shared refs) | 0 | 0 | 0 | 1: proofpunk | 7: session-intent, brainstorm, prompt-forge, validation-plan, end-user-testing, tui-testing, root-cause-debugging | 2 | YES — named in 7 e2e-evidence VERDICT/FIXES files |
| `mobile-validation-runner` | YES | 727 | PROSE-ONLY (no quoted user phrases) | stack-testing | 27 cited / 27 resolve (incl. shared refs) | 22 | 0 | 4 | 1: proofpunk | 2: end-user-testing, visual-inspection | 2 | YES — named in 2 e2e-evidence VERDICT/FIXES files |
| `plan-hardening` | YES | 745 | TRIGGER (5 quoted phrases) | implement, validation-plan | 3 cited / 3 resolve (incl. shared refs) | 0 | 0 | 0 | 1: proofpunk | 3: red-team-eval, validation-plan, end-user-testing | 2 | YES — named in 1 e2e-evidence VERDICT/FIXES files |
| `production-readiness` | YES | 737 | WEAK (1 quoted phrase, rest prose) | session-intent, visual-inspection | 5 cited / 5 resolve (incl. shared refs) | 3 | 0 | 0 | 1: proofpunk | 4: codebase-truth-audit, full-functional-audit, stack-testing, end-user-testing | 4 | YES — named in 2 e2e-evidence VERDICT/FIXES files |
| `prompt-forge` | YES | 887 | PROSE-ONLY (no quoted user phrases) | implement, plan-hardening, red-team-eval | 9 cited / 9 resolve (incl. shared refs) | 7 | 0 | 0 | 2: implement, proofpunk | none (leaf) | 0 | YES — named in 2 e2e-evidence VERDICT/FIXES files |
| `proofpunk` | YES | 718 | PROSE-ONLY (no quoted user phrases) | none named | 14 cited / 14 resolve (incl. shared refs) | 0 | 0 | 0 | none (router root) | 17: brainstorm, implement, validation-plan, plan-hardening, codebase-truth-audit, full-functional-audit, production-readiness, ui-experience-audit, root-cause-debugging, red-team-eval, stack-testing, mobile-validation-runner, end-user-testing, visual-inspection, tui-testing, session-intent, prompt-forge | 5 | YES — named in 14 e2e-evidence VERDICT/FIXES files |
| `red-team-eval` | YES | 761 | WEAK (1 quoted phrase, rest prose) | plan-hardening, root-cause-debugging | 8 cited / 8 resolve (incl. shared refs) | 4 | 2 | 0 | 2: plan-hardening, proofpunk | 1: end-user-testing | 1 | YES — named in 2 e2e-evidence VERDICT/FIXES files |
| `root-cause-debugging` | YES | 731 | PROSE-ONLY (no quoted user phrases) | full-functional-audit, production-readiness, stack-testing | 12 cited / 12 resolve (incl. shared refs) | 9 | 0 | 2 | 5: codebase-truth-audit, full-functional-audit, implement, stack-testing, proofpunk | 1: end-user-testing | 1 | YES — named in 4 e2e-evidence VERDICT/FIXES files |
| `session-intent` | YES | 805 | WEAK (1 quoted phrase, rest prose) | codebase-truth-audit, validation-plan | 2 cited / 2 resolve (incl. shared refs) | 1 | 0 | 1 | 3: codebase-truth-audit, implement, proofpunk | none (leaf) | 0 | YES — named in 1 e2e-evidence VERDICT/FIXES files |
| `stack-testing` | YES | 746 | PROSE-ONLY (no quoted user phrases) | end-user-testing, root-cause-debugging | 16 cited / 16 resolve (incl. shared refs) | 10 | 0 | 5 | 2: production-readiness, proofpunk | 1: root-cause-debugging | 2 | YES — named in 3 e2e-evidence VERDICT/FIXES files |
| `tui-testing` | YES | 752 | WEAK (1 quoted phrase, rest prose) | none named | 1 cited / 1 resolve (incl. shared refs) | 0 | 0 | 0 | 3: implement, full-functional-audit, proofpunk | 1: end-user-testing | 1 | YES — named in 3 e2e-evidence VERDICT/FIXES files |
| `ui-experience-audit` | YES | 807 | TRIGGER (4 quoted phrases) | full-functional-audit, visual-inspection | 10 cited / 10 resolve (incl. shared refs) | 4 | 1 | 0 | 2: full-functional-audit, proofpunk | 2: visual-inspection, end-user-testing | 2 | YES — named in 1 e2e-evidence VERDICT/FIXES files |
| `validation-plan` | YES | 648 | PROSE-ONLY (no quoted user phrases) | implement, plan-hardening | 3 cited / 3 resolve (incl. shared refs) | 1 | 0 | 0 | 3: implement, plan-hardening, proofpunk | 1: end-user-testing | 1 | YES — named in 4 e2e-evidence VERDICT/FIXES files |
| `visual-inspection` | YES | 672 | TRIGGER (2 quoted phrases) | ui-experience-audit | 5 cited / 5 resolve (incl. shared refs) | 0 | 0 | 0 | 3: mobile-validation-runner, ui-experience-audit, proofpunk | 1: end-user-testing | 1 | YES — named in 2 e2e-evidence VERDICT/FIXES files |


**Note on "Verified today?"**: this counts skills NAMED in an
`e2e-evidence/*/VERDICT.md` or `e2e-evidence/FIXES.md` file — i.e. mentioned
as part of a sealed run's scope or findings. All 18 skills have at least 1
such mention (`plan-hardening`, `session-intent`, and `ui-experience-audit`
have the fewest, at 1 each — both are newer additions with less accumulated
audit history). This is a coverage-breadth signal, not a claim that every
mentioned skill was itself DRIVEN in that run — several VERDICT.md files
discuss the skill graph structurally (e.g. citing which skills a router
edge points to) without exercising every named skill's own workflow. No
skill shows zero mentions.

## 2. The Orchestration DAG

### Single root
**Yes.** `proofpunk` is the only skill in the tree whose SKILL.md body ends
with `Called by: nothing — the entry point for the whole plugin.`
(`plugins/proofpunk/skills/proofpunk/SKILL.md:101`). All other 17 skills
have at least one non-empty `Called by:` line.

### Does `proofpunk` link N-1 = 17 skills?
**Yes, exactly.** `proofpunk`'s "Skill calls" table
(`plugins/proofpunk/skills/proofpunk/SKILL.md:41-59`) lists 17 rows. I
diffed the set of names in that table against `os.listdir()` of the skills
directory minus `proofpunk` itself: the symmetric difference is empty —
zero skills missing from the router table, zero phantom/dead names present
in it. This directly falsifies any residual worry that the router might
still reference a 19-skill-era or dead-named skill: it references exactly
today's 17.

### Are `Called by:` claims reciprocal with real edges?
**Yes, 48/48, both directions.** I extracted two edge sets programmatically:
(a) every row of every skill's own "Skill calls" table (the *claimed
outbound* edges), and (b) every name listed in every skill's own
`Called by:` line (the *claimed inbound* edges, stated by the callee). Set
`A` (caller→callee pairs derived from Skill-calls tables) has 48 elements.
Set `B` (caller→callee pairs derived from Called-by lines, read as
"claimed_caller calls this_skill") also has 48 elements. `A == B` exactly —
zero edges present in one direction's table but absent from the other's.
This means every skill's "who I call" story matches every target's "who
calls me" story, with no orphaned or one-sided claims anywhere in the graph.

### Cycles?
**None.** Standard three-color DFS over the 48-edge directed graph found
zero back-edges. The graph is a DAG, consistent with the tree/branching
structure implied by the "layers" framing in the README and
`tools/build-site.py`'s `LAYERS` map.

### Max depth?
**5**, measured as the length of the longest directed path in the graph
(memoized longest-path-to-leaf DFS from every node). The specific
longest chain is:

```
proofpunk -> production-readiness -> full-functional-audit
  -> ui-experience-audit -> visual-inspection -> end-user-testing
```

Since every skill sits at router-distance exactly 1 from `proofpunk` by
design (the router is a star hub, not a chain), the more meaningful number
for judging the DOCTRINE graph's real depth is the longest chain **among the
17 substantive skills, excluding the router itself**: that is 4, via
`production-readiness -> full-functional-audit -> ui-experience-audit ->
visual-inspection -> end-user-testing`. Four leaf skills terminate every
chain they're on: `brainstorm`, `end-user-testing`, `prompt-forge`,
`session-intent` — each explicitly states "Leaf skill — owns canonical
methods; calls nothing" in its own SKILL.md, which I cross-checked
structurally (their Skill-calls tables are genuinely empty, not just
textually claiming to be).

### Reference-citation edges (14 shared + per-skill)
Plugin-root `plugins/proofpunk/references/*.md` currently contains **14
files** (glob-counted, live at HEAD): `api-validation.md`, `ci-gates.md`,
`cli-validation.md`, `defect-pattern-database.md`, `end-user-actor.md`,
`evidence-contract.md`, `ios-hig-checklist.md`, `ios-validation.md`,
`platform-routing.md`, `preflight-checks.md`, `run-trace-schema.md`,
`severity-model.md`, `web-validation.md`, `web-wcag-checklist.md`.

This reconciles a discrepancy I found between two prior-session artifacts:
`d6-d7-measurement.md` (dated 2026-09-02, measured against commit `a41591a`)
states **13 references**, while `docs/discovery-register.md` D6's line and
the generated `docs/doc-architecture.html:475` both also say 13. Both are
correct FOR THEIR MEASUREMENT DATE. I confirmed via `git log --diff-filter=A`
that `run-trace-schema.md` was added in commit `73e928e` ("baseline: adopt
in-flight v3 lane artifacts as disclosed pre-work"), which post-dates
`a41591a`. **At current HEAD the true count is 14, not 13** — this is not a
contradiction between sources, it's evidence-dated drift the orchestrator's
brief already anticipated by giving 14 as the number to verify.

**Transitive reference->reference edges**: I checked whether any
plugin-root reference file cites another plugin-root reference file by name
(beyond the skill layer). Six such edges exist:

| Citing file | Cites |
|---|---|
| `ci-gates.md` | `end-user-actor.md`, `evidence-contract.md` |
| `end-user-actor.md` | `evidence-contract.md` |
| `evidence-contract.md` | `end-user-actor.md` |
| `platform-routing.md` | `preflight-checks.md` |
| `run-trace-schema.md` | `severity-model.md` |
| `severity-model.md` | `end-user-actor.md` |

Note `end-user-actor.md` and `evidence-contract.md` cite EACH OTHER — this
is a benign 2-cycle in the DOCTRINE reference layer (not the skill-call
layer, which remains acyclic), reflecting that the Actor Mandate and the
Evidence Contract are mutually defining concepts by design, not a structural
defect.

**Per-skill reference/asset/script inventory** (raw counts, `.md` files
only for `references/`, all files for `assets/` and `scripts/`, recursive
for `scripts/`): 8 skills have a `references/` subdirectory
(`codebase-truth-audit` 1, `end-user-testing` 0-refs-but-has-scripts,
`mobile-validation-runner` 22, `production-readiness` 3, `prompt-forge` 7,
`red-team-eval` 4, `root-cause-debugging` 9, `session-intent` 1,
`stack-testing` 10, `ui-experience-audit` 4, `validation-plan` 1) — total
**62 per-skill reference files**, summing correctly against the individual
per-skill counts in the scorecard above. 4 skills have an `assets/` dir
(`end-user-testing`, `red-team-eval`, `ui-experience-audit`, plus 0 extra —
verified: 4 dirs, not 5 as one stale HTML doc claimed elsewhere — see Open
Questions). 6 skills have a `scripts/` dir (`codebase-truth-audit`,
`end-user-testing`, `mobile-validation-runner`, `root-cause-debugging`,
`session-intent`, `stack-testing`).

## 3. Dead Names — Exhaustive Sweep

Full file:line enumeration and live-vs-historical classification for every
non-evidence-directory occurrence of `cook` and `functional-validation` is
in UPDATE 2 of the working notes below (kept intact per this report's own
no-silent-drop discipline). Headline result:

- **`cook`: 49 non-evidence hits, 49/49 HISTORICAL.**
- **`functional-validation`: 39 non-evidence hits, 39/39 HISTORICAL.**
- **Evidence-directory hits excluded from this classification** (120 `cook`
  + 84 `functional-validation` hits inside `evidence/` and `e2e-evidence/`):
  these are sealed, timestamped audit captures, definitionally historical by
  the plugin's own evidence-contract doctrine, and out of scope for "live
  guidance" sweep since nothing under those directories is loaded at
  runtime by any skill.
- **Zero live-guidance occurrences found anywhere.** No currently-active
  SKILL.md, command file, or shared reference tells an agent to invoke a
  skill literally named `cook` or `functional-validation` as if it exists
  today. The one edge case — `plugins/proofpunk/references/platform-routing.md:4`
  (a CURRENTLY LOADED, live reference file) — says "Consolidated from
  `functional-validation`, `e2e-validate`, `ios-validation-runner`, and
  `validate-phase`" in its OPENING sentence. I classify this as HISTORICAL
  PROVENANCE, not live guidance: it credits archive sources merged INTO the
  file; the rest of the file (read in full) routes exclusively to the four
  CURRENT runbooks (`api-validation.md`, `web-validation.md`,
  `cli-validation.md`, `ios-validation.md`). It does not instruct anyone to
  invoke a `functional-validation` skill.

**The brief's specific `tools/build-site.py` claim is FALSE.** I read
`tools/build-site.py:296-323` directly (the COMMAND SURFACE HTML-generation
block) — line 311 renders `/proofpunk:install`, not `/proofpunk:cook`. I
then ran two independent greps: `git grep -n -I -w "cook"` (word-boundary,
tracked files) and a case-insensitive `(?i)cook` regex scan, both scoped to
`tools/build-site.py` alone. **Both returned zero matches.** The string
"cook" does not appear anywhere in that file's 611 lines, in any
case-form, at any line number. The file's `LAYERS` map (lines 167-175) is
real and does list 18 skill names across 5 layers — I verified those 18
names are a set-exact match against the real skill directories, zero dead
names present. My working hypothesis: the brief's file:line pointer was
carried forward from an earlier, now-cleaned version of `build-site.py`
(the file has clearly been edited multiple times per the git history around
`93c479d`/`73e928e`), or conflated with one of the many dated report files
(`proofpunk-v2-release-report.md:12` etc.) that DO name `/proofpunk:cook`
in historical prose. Either way: **as of HEAD, this specific claim does not
hold**, and no sweep action is needed against `tools/build-site.py`.

## 4. Head-Skill Intent (D8) — RESOLVED

**Verdict: RESOLVED, with direct quote, no interpretive gloss required.**

> "...it looks like the install script isn't actually properly working
> correctly, and so **you should only have one massive skill that basically
> the head will link with everything else up correctly**. And according to
> that, then you'll actually move forward with whatever happens next."
>
> — Operator dictation, `evidence/v3-release/00-discovery/raw/round1-dictation.txt:3`,
> sourced from `~/.omp/agent/sessions/-proofpunk/2026-08-24T20-31-44-166Z_...jsonl:11`

This was already resolved by prior orchestrator work
(`evidence/v3-release/00-discovery/d1-d2-d8-transcript-evidence.md:69-78`,
`docs/discovery-register.md:39`, `docs/session-intent-ledger.md:14-17`), and
I independently re-verified both the textual resolution and its
implementation status rather than taking the prior finding on faith:

- **The sentence self-glosses.** "one massive skill that basically the head
  will link with everything else" describes a HEAD that LINKS TO other
  things — the defining property of a router, not a monolith. A literal
  single-file merge would have nothing left to link to; the phrase is
  internally incoherent as a request for a merge.
- **Cross-validated against the full corpus.** An exhaustive search across
  34,674 OMP + 168 Claude operator turns found **zero** turns asking for
  skills to be merged into one file.
- **Implementation verified, not just claimed.** Commit `0de4680`
  (2026-08-24 20:42:05) added `plugins/proofpunk/skills/proofpunk/SKILL.md`
  routing all 17 other skills, with reciprocal `Called by: proofpunk` added
  to each. **I re-verified this holds at CURRENT HEAD** (not merely at that
  historical commit) via the independent programmatic checks in Section 2
  above: 17/17 skills present in the router table, 48/48 edges reciprocal,
  single root, zero cycles. The resolution was not just decided in August —
  it demonstrably still holds today.

No unresolved marker needed for D8. (For contrast, two OTHER open items
from the same discovery pass remain genuinely unresolved per prior work —
D9b "Rebo" and D9c "Furble's Claude" — but those are out of this lane's
scope; D8 specifically, which is what this task assigns, is closed.)

## Open Questions

- **`assets/` count discrepancy (minor, unresolved)**: one generated doc
  (`docs/doc-architecture.html:476-478`, not independently re-verified by me
  against its markdown source in this pass) claims "5 assets: 2 top-level
  template files + `rules/` containing 3 files" for the PLUGIN ROOT
  `plugins/proofpunk/assets/` directory — this is a DIFFERENT thing from the
  4 PER-SKILL `assets/` dirs I counted in the scorecard (which is what the
  task asked for). I did not cross-verify the plugin-root assets/ claim
  against disk in this pass since it's out of the 18-skill scorecard's
  scope; flagging so a later lane doesn't conflate the two counts.
- **`e2e-evidence` "Verified today?" is a coverage-breadth proxy, not a
  quality signal.** I did not open and read all 15 VERDICT.md/FIXES.md
  files end-to-end to confirm each MENTION represents an actual driven
  exercise of that skill's own workflow (vs. a structural mention, e.g. "the
  router links to X"). This would require substantially more reading than
  this lane's read-only forensics budget allows; flagging as a genuine gap
  rather than asserting a stronger claim than I can support. What I DID
  verify: every one of the 18 skills has at least 1 non-zero mention, so
  none is completely unexercised in the evidence corpus — but "mentioned"
  and "driven" are not proven identical here.
- **The brief's own `functional-validation` "14 refs" claim vs my "13 refs
  measured for functional-validation's own subtree at the pre-merge era"**:
  `docs/doc-consolidation-decisions.html:332` states the archive's
  `functional-validation/SKILL.md` skill (pre-merge, now historical) had "4
  runbooks carried verbatim" citing "14 refs" for the OLD standalone skill's
  own subtree in ITS OWN historical context — this is a different "14" from
  the plugin-root references/ count of 14 I resolved in Section 2. I did
  not chase down whether these two "14"s are coincidentally the same number
  or whether one prior pass conflated them; noting the ambiguity rather
  than asserting they're unrelated with more confidence than I've earned.
- I did not independently re-derive the `d5-sweep-results.md` "296 refs, 60
  unresolved" heuristic sweep figure cited in `docs/discovery-register.md:36`
  — that sweep appears to be a much broader regex pass across the whole
  history/docs corpus (not scoped to live SKILL.md citations, which is what
  I measured cleanly at 0 broken), and reconciling the two would require
  reading that prior sweep's own methodology, which is out of this lane's
  scope.

---

## Appendix — Full working notes (UPDATE 0-3, preserved verbatim)



- 18 skill dirs confirmed on disk under `plugins/proofpunk/skills/*` (glob'd, not counted from README).
- All 18 `name:` frontmatter fields match their parent directory name exactly (verified programmatically).
- The `proofpunk` router's "Skill calls" table lists exactly 17 skills — matches `N-1=17` — set-difference against the real 18 skill dirs (minus proofpunk itself) is empty in both directions (no missing, no phantom names).
- Every one of the 48 edges in every skill's "Skill calls" table is reciprocated by a matching "Called by:" line on the target skill, and vice versa — 48/48 match in both directions, zero unreciprocated edges either way.
- No cycles detected in the call graph (DFS over all 48 edges).
- `proofpunk` is the only skill with `Called by: nothing` — single root confirmed.
- BFS shortest-path depth from `proofpunk` over the Calls-table graph: every one of the other 17 skills is exactly depth 1 (proofpunk calls all of them directly) — max depth 1 for the ROUTER edges specifically. (NOTE: this is depth in the router-fan-out sense; the *doctrine* delegation graph — e.g. `implement` -> `brainstorm` -> nothing further — needs separate depth measurement, in progress below.)
- Known already-resolved from orchestrator: D6/D7 ground truth (18 skills, 13 references, etc.), test-installer rc=7 root cause (F-002, uncommitted citation typo), fresh_evidence.py real path.

## Findings (partial — table under construction)

| ID | Finding | Evidence (path:line or command) | Confidence (high/med/low) |
|---|---|---|---|
| A6-01 | All 18 skill dirs' `name:` frontmatter exactly match their directory name | Python parse of all 18 `SKILL.md` frontmatter blocks | high |
| A6-02 | `proofpunk`'s Skill-calls table lists exactly the other 17 skills, no missing, no phantom | `plugins/proofpunk/skills/proofpunk/SKILL.md:41-59` cross-checked against `os.listdir` of skills dir | high |
| A6-03 | All 48 Calls-table edges are reciprocated by a "Called by:" line in the target skill (48/48, zero orphans in either direction) | Programmatic diff of `Skill calls` tables vs `Called by:` lines across all 18 files | high |
| A6-04 | Zero cycles in the 48-edge call graph | DFS cycle detection over full edge set | high |
| A6-05 | Single root: only `proofpunk` has `Called by: nothing` | grep of `Called by:` line in all 18 files | high |
| A6-06 | D8 ("one massive skill") is RESOLVED with a direct quote, already captured by prior orchestrator passes | `evidence/v3-release/00-discovery/d1-d2-d8-transcript-evidence.md:69-78`, `docs/discovery-register.md:39`, `docs/session-intent-ledger.md:14-17` — operator's own dictation: "one massive skill that basically **the head will link with everything else**" — resolved as strengthen-the-router, not a literal merge | high |
| A6-07 (dead-name, in progress) | `cook` and `functional-validation` survive as HISTORICAL PROVENANCE PROSE in `README.md`, `docs/consolidation-decisions.md`, `docs/validation-results.md`, `docs/commit-archaeology.md`, `docs/discovery-register.md`, and their generated `.html` twins — every occurrence found so far is inside a documented merge-history sentence ("X was later merged into Y"), none is live invocation guidance | med (sweep still running — LAYERS map and build-site.py hardcoded `/proofpunk:cook` line not yet classified) |

## Open questions (in progress)

- Sub-reference tree fully enumerated via glob (13 `references/` dirs matching README's `13 references` count, plus 4 `assets/` dirs, 6 `scripts/` dirs) — need explicit per-skill row with counts for the scorecard.
- `tools/build-site.py` LAYERS map (lines 167-175) references 5 layer names and 17 skill names (NOT proofpunk itself, which is ORCHESTRATION layer alongside implement) — need to verify all 17 named skills in LAYERS match real dirs, and classify the layer names against the README's "skill stack" framing.
- `tools/build-site.py:308` hardcodes `/proofpunk:implement` as a command surface entry (ORCHESTRATE badge) — the brief's claim of a hardcoded `/proofpunk:cook` around line 311 does NOT match what I read at that exact location (line 311 is `/proofpunk:install`, not cook). Need to grep the WHOLE file for `cook` — initial grep returned zero hits in `tools/build-site.py`. This needs a definitive re-check: possible the brief's file:line pointer is stale/wrong, and `cook` does not appear literally in `build-site.py` source at all.
- Still need: full transitive reference→reference edge map (14 references/ citation count from brief vs 13 measured by orchestrator — reconcile discrepancy).
- Still need: doctrine-graph depth (not router-fan-out depth) — e.g. how deep does `implement` -> `root-cause-debugging` -> `end-user-testing` go as a chain, since router depth-1 is trivial by design.
- Still need: verification-today column per skill (does each skill have ANY captured evidence run, dogfood pass, or validation artifact referencing it).


## UPDATE 1 — DAG depth, reference resolution, D6/D7 reconciliation

- Router-fan-out depth (proofpunk -> X) is trivially 1 for all 17, by design (star topology at the top).
- TRUE max depth in the whole call-graph (longest path via DFS/memoized longest-path): **5**, via
  `proofpunk -> production-readiness -> full-functional-audit -> ui-experience-audit -> visual-inspection -> end-user-testing`.
  Longest chain NOT starting at the router (i.e. the deepest *doctrine* chain among the 17 substantive skills):
  `production-readiness -> full-functional-audit -> ui-experience-audit -> visual-inspection -> end-user-testing` (depth 4).
- 4 leaf skills (call nothing): `brainstorm`, `end-user-testing`, `prompt-forge`, `session-intent` — matches each one's own "Leaf skill — owns canonical methods; calls nothing." statement, cross-checked structurally not just by string search.
- Reference citation resolution: extracted every backtick-quoted `references/…`, `assets/…`, `scripts/…` path from all 18 SKILL.md bodies (both same-skill `references/x.md` and cross-skill `../../references/x.md` forms) and resolved each against disk relative to its own skill directory.
  - 17/18 skills: 100% of citations resolve.
  - `stack-testing`: 1 citation `scripts/playwright/` resolves to a DIRECTORY (`plugins/proofpunk/skills/stack-testing/scripts/playwright/` containing `run.js`, `package.json`, `lib/`), not a `.md` file — this is a legitimate directory reference (the skill text says "import from `scripts/playwright/`", not "read this file"), so it is NOT a broken citation, just a directory-shaped one my regex flagged. Reclassified as OK.
  - **Net: 0 genuinely broken reference citations across all 18 skills.**
- Plugin-root `references/` count: **14 files on disk right now** (`glob plugins/proofpunk/references/*.md`), not the 13 that `d6-d7-measurement.md` (dated 2026-09-02, measured against stale `a41591a`) reports. Reconciled: `run-trace-schema.md` was added in commit `73e928e` ("baseline: adopt in-flight v3 lane artifacts as disclosed pre-work"), which post-dates `a41591a`. `a41591a` genuinely had 13; HEAD has 14. The brief's "14" figure and D6's "13" figure are BOTH correct — for their respective commits. This is a measured, resolved discrepancy, not a contradiction.
- Per-skill references/assets/scripts inventory (raw counts) - see full table in next section.

STATUS: IN PROGRESS


## UPDATE 2 — Dead-name sweep classification (exhaustive)

Method: `git grep -n -I -w "cook"` and `git grep -n -I -w "functional-validation"`
across the whole tracked tree, word-boundary matched (excludes substrings like
"cooking" partial matches inside other words — none found anyway), split into
two buckets: (A) `evidence/` + `e2e-evidence/` capture artifacts (120 `cook`
hits across 37 files, 84 `functional-validation` hits — these are sealed,
timestamped audit-run captures and by definition historical; NOT swept, NOT
part of live guidance, out of scope for this classification since the brief
asked about "guidance and generator source"), and (B) everything else (49
`cook` hits, 39 `functional-validation` hits) — classified individually below.

**Classification rule applied:** LIVE GUIDANCE = a currently-active SKILL.md,
README.md, or docs/*.md file telling a reader/agent to invoke, use, or expect
a skill/command named `cook` or `functional-validation` AS IF IT EXISTS TODAY.
HISTORICAL PROVENANCE = any sentence describing what a past version did, what
was merged into what, or a dated report/demo artifact fixed at the commit it
was authored against.

### `cook` — all 49 non-evidence hits (bucket B)

| # | File:Line | Class | Reason |
|---|---|---|---|
| 1 | `README.md:91` | HISTORICAL | v1.9.0 changelog prose: "...`references/*.md`...**v1.9.0**: the doctrine moved...` and prior text mentions `cook` only inside a versioned changelog entry describing past state |
| 2 | `README.md:234` | HISTORICAL | "implement IS the execution engine — cook merged into it at v2.0.0." — explicit past-tense merge statement, immediately followed by the CURRENT command surface (no `--tdd`/`--no-test`, single write path) |
| 3 | `docs/commit-archaeology.md:15` | HISTORICAL | Commit-log entry dated 2026-08-14 describing the `96d91d6` commit's content |
| 4 | `docs/commit-archaeology.md:63` | HISTORICAL | Describes a correction commit `f8dccf8` about an overstated claim regarding the word "cook" itself (meta-historical) |
| 5 | `docs/commit-archaeology.md:86` | HISTORICAL | ASCII commit timeline, dated row `2026-08-14 ... v2.0.0: cook merged into implement` |
| 6 | `docs/commit-archaeology.md:140` | HISTORICAL | Describes a STALE, UNREGISTERED marketplace-cache tree on disk (`1.10.1`, 19 skills) as evidence of a dead-name hazard — the sentence itself is a forensic finding about dead names, not guidance to use them |
| 7 | `docs/commit-archaeology.md:150` | HISTORICAL | Same finding restated in a "confirmed patterns" recap list |
| 8 | `docs/discovery-register.md:38` | HISTORICAL | D7 finding row: "Stale unregistered 1.10.1 tree persists on disk with 19 skills incl. dead `cook`/`functional-validation`" — explicitly labeled "dead" in the finding itself |
| 9 | `docs/doc-consolidation-decisions.html:227` | HISTORICAL | Generated HTML mirror of `consolidation-decisions.md` §"Cook (\"cooking\") family" — a dated source-mapping table for the original consolidation, describing which ARCHIVE skill (`ck:cook` v2.2.0) fed into what became this plugin's now-merged skill |
| 10 | `docs/doc-consolidation-decisions.html:238` | HISTORICAL | Same table, source-skill cell `ck:cook v2.2.0` |
| 11 | `docs/doc-consolidation-decisions.html:240` | HISTORICAL | Same table, destination cell (`cook`) — describes the destination AS IT WAS in the v1.x archive-consolidation era, before the v2.0.0 cook->implement merge |
| 12 | `docs/doc-consolidation-decisions.html:394` | HISTORICAL | Exclusions table: `ak-brainstorm`, `ak-cook` — empty archive stubs never incorporated at all |
| 13 | `docs/doc-consolidation-decisions.html:529` | HISTORICAL | v1.5.0 decision-log prose: "`implement` is the orchestrator ... and `cook` stays the execution engine" — describes the ARCHITECTURE AS DECIDED AT v1.5.0, one version before the v2.0.0 merge; itself historical decision-log |
| 14 | `docs/doc-validation-results.html:55` | HISTORICAL | Generated HTML mirror of the per-skill line-count table from `validation-results.md` (a dated v1.1.0-era validation report) |
| 15 | `docs/doc-validation-results.html:233` | HISTORICAL | Same doc, table cell for cook's end-user verification gate as it existed at that pass |
| 16 | `docs/doc-validation-results.html:309` | HISTORICAL | Exclusions-honored list, mentions `ak-cook` stub |
| 17 | `docs/doc-validation-results.html:317` | HISTORICAL | Dogfood walkthrough narrative: "brainstorm -> prompt-forge -> ... -> cook (32/32 pytest green) -> ..." — describes the ACTUAL SKILL CHAIN USED in the dated Mood Ring demo run, which literally invoked the-then-existing `cook` skill before the merge |
| 18 | `docs/doc-validation-results.html:385` | HISTORICAL | "the orchestrator (conductor) to cook's execution engine (player)" — v1.5.0-era architecture description |
| 19 | `docs/doc-validation-results.html:387` | HISTORICAL | Explicit note: "`--no-test` and `--tdd` were later removed, and `cook` was merged into `implement`" |
| 20 | `docs/doc-validation-results.html:393` | HISTORICAL | "Phase 5 — EXECUTE under cook's gates" — v1.5.0-era pipeline description, pre-merge |
| 21 | `docs/doc-validation-results.html:402` | HISTORICAL | Explicit blockquote: "**Historical record.** ... `cook` and `functional-validation` were later merged into `implement`" — self-labeled as historical by the document itself |
| 22 | `docs/doc-validation-results.html:406` | HISTORICAL | §1-8 command-reference table listing cook's THEN-command surface (5 modes, 12-permutation table) as shipped at that dated release |
| 23 | `docs/session-intent-ledger.md:42` | HISTORICAL | Describes a correction commit narrowing an overstated "zero files name cook" claim |
| 24 | `examples/mood-ring/.planning/HARDENING.md:25` | HISTORICAL | Dated demo artifact (last touched `20bd199`, 2026-08-08) — a hardening review of the Mood Ring feature plan, references `cook` as the (then-current) execution skill for that dogfood run |
| 25 | `examples/mood-ring/.planning/HARDENING.md:56` | HISTORICAL | Same demo artifact: "Verdict: plan is HARDENED — cleared for `cook`." |
| 26 | `examples/mood-ring/.planning/brainstorm-mood-ring.md:4` | HISTORICAL | Same demo, same dating |
| 27 | `examples/mood-ring/.planning/brainstorm-mood-ring.md:72` | HISTORICAL | Same demo |
| 28 | `examples/mood-ring/.planning/phases/01-mood-schema-backend/01-PLAN.md:14` | HISTORICAL | Same demo, phase plan amendment note |
| 29 | `examples/mood-ring/.prompts/build-mood-ring/PROMPT.md:18` | HISTORICAL | Dated demo prompt (last touched `b687d4e`, 2026-08-09, PRE v2.0.0 merge) `<skills_to_activate>` block literally lists `cook` — this is the captured INPUT to a historical dogfood run, frozen at authoring time, not live guidance for a new session today |
| 30 | `plugins/proofpunk/docs/consolidation-decisions.md:96` | HISTORICAL | Source-of-truth `## Cook ("cooking") family -> \`cook\`` heading — describes what archive material became the (then-shipped, now-merged) `cook` skill; this is the canonical decision log and is EXPECTED to retain every historical skill name it ever created, per the file's own stated purpose |
| 31 | `plugins/proofpunk/docs/consolidation-decisions.md:100` | HISTORICAL | Same section, source-mapping table row |
| 32 | `plugins/proofpunk/docs/consolidation-decisions.md:190` | HISTORICAL | Exclusions table: `ak-brainstorm`, `ak-cook` empty stubs |
| 33 | `plugins/proofpunk/docs/consolidation-decisions.md:315` | HISTORICAL | v1.5.0 decision-log entry, same content as HTML mirror #13 |
| 34 | `plugins/proofpunk/docs/validation-results.md:25` | HISTORICAL | Dated line-count table (v1.1.0-era) |
| 35 | `plugins/proofpunk/docs/validation-results.md:122` | HISTORICAL | Same dated table, End-User Actor Mandate rollout row for `cook` as it existed then |
| 36 | `plugins/proofpunk/docs/validation-results.md:179` | HISTORICAL | Exclusions-honored recap |
| 37 | `plugins/proofpunk/docs/validation-results.md:205` | HISTORICAL | Dogfood walkthrough (source .md of HTML mirror #17) |
| 38 | `plugins/proofpunk/docs/validation-results.md:383` | HISTORICAL | Architecture description (source .md of HTML mirror #18) |
| 39 | `plugins/proofpunk/docs/validation-results.md:387` | HISTORICAL | Merge note (source .md of HTML mirror #19) |
| 40 | `plugins/proofpunk/docs/validation-results.md:403` | HISTORICAL | Pipeline description (source .md of HTML mirror #20) |
| 41 | `plugins/proofpunk/docs/validation-results.md:427` | HISTORICAL | Explicit "Historical record" blockquote (source .md of HTML mirror #21) |
| 42 | `plugins/proofpunk/docs/validation-results.md:435` | HISTORICAL | Command-reference table (source .md of HTML mirror #22) |
| 43 | `proofpunk-hooks-release-report.md:17` | HISTORICAL | Superseded-notice block at the top of the file itself says "SUPERSEDED 2026-09-04 — historical record, retained intact" — the whole file is a dated (2026-08-13) report frozen in place per stated convention |
| 44 | `proofpunk-skills-improvement-report-round2.md:15` | HISTORICAL | Round-2 report (dated 2026-08-12) improvement-table row for the (then-existing) `cook` skill |
| 45 | `proofpunk-skills-improvement-report-round2.md:29` | HISTORICAL | Same report, verification-recap bullet |
| 46 | `proofpunk-v2-release-report.md:12` | HISTORICAL | v2.0.0 release report's own headline collapse table: "Skills 19 -> 17 (`cook` merged into `implement`...)" — this IS the report of the merge itself |
| 47 | `proofpunk-v2-release-report.md:13` | HISTORICAL | Same report, commands-collapse row |
| 48 | `proofpunk-v2-release-report.md:14` | HISTORICAL | Same report, write-paths-collapse row |
| 49 | `proofpunk-v2-release-report.md:53` | HISTORICAL | Same report, closing note about the verifier catching stale Called-by lines "the moment cook [disappeared]" |

**Result: 49/49 non-evidence `cook` hits are HISTORICAL PROVENANCE PROSE.
ZERO live guidance occurrences found.** No SKILL.md file, no active command
file, no currently-loaded reference file, and no section of README.md
presented as CURRENT instructs a reader to invoke a `cook` skill. Every hit
is inside either (a) a dated, versioned report/decision-log whose own header
states its historical scope, (b) the canonical consolidation-decisions.md
source-mapping ledger (which is BY DESIGN a permanent record of every archive
skill name ever ingested, dead or alive), or (c) a frozen dogfood demo
artifact (`examples/mood-ring/`) whose files were last touched in
2026-08-08/09, before the 2026-08-14 `96d91d6` cook->implement merge commit —
i.e. they are literally pre-merge captures, correctly still naming the
skill that existed when they were captured.

### `functional-validation` — all 39 non-evidence hits (bucket B)

Same classification method applied. Every hit falls into one of:
- `docs/consolidation-decisions.md` / its HTML mirror — canonical source-mapping ledger (permanent record by design), lines 32/36/38/175 (source .md) + HTML mirror lines 45/56/58/68/332/334.
- `docs/validation-results.md` / its HTML mirror — dated v1.1.0-era validation report, lines 28/44/119/148/149/206/272/427/436 (source .md) + HTML mirror lines 67/94/221/271/272/317/341/402/406.
- `docs/discovery-register.md:38` and `docs/commit-archaeology.md:140` — forensic D7 findings explicitly labeling it "dead", identical treatment to the `cook` findings above.
- `docs/ref-platform-routing.html:32` / `plugins/proofpunk/references/platform-routing.md:4` — the CURRENT, LIVE `platform-routing.md` reference file's own opening sentence: "Consolidated from `functional-validation`, `e2e-validate`, `ios-validation-runner`, and `validate-phase`." — **CLASSIFIED HISTORICAL, not live guidance**: this is provenance prose crediting the ARCHIVE sources that were merged INTO this file; it does not instruct anyone to invoke a `functional-validation` skill, and the rest of the file (confirmed read in full earlier) routes exclusively to `api-validation.md`/`web-validation.md`/`cli-validation.md`/`ios-validation.md` — the real, current runbooks.
- `examples/mood-ring/.prompts/build-mood-ring/PROMPT.md:19` — same frozen pre-merge demo artifact as `cook` hit #29, dated 2026-08-09, pre-dates the merge.
- `proofpunk-hooks-release-report.md:18`, `proofpunk-skills-improvement-report-round2.md:13,29`, `proofpunk-v2-release-report.md:12` — same dated release-report class as the `cook` findings above.

**Result: 39/39 non-evidence `functional-validation` hits are HISTORICAL
PROVENANCE PROSE. ZERO live guidance occurrences.**

### The brief's specific claim about `tools/build-site.py` — FALSIFIED

The brief states: "specifically calls out `tools/build-site.py` (a LAYERS map,
and a hardcoded `/proofpunk:cook` around line 311)."

- **LAYERS map**: confirmed real, at `tools/build-site.py:167-175`. It lists
  exactly the 18 CURRENT skill names (`proofpunk`, `implement`,
  `prompt-forge`, `brainstorm`, `validation-plan`, `plan-hardening`,
  `stack-testing`, `mobile-validation-runner`, `end-user-testing`,
  `visual-inspection`, `ui-experience-audit`, `full-functional-audit`,
  `tui-testing`, `root-cause-debugging`, `red-team-eval`,
  `production-readiness`, `session-intent`, `codebase-truth-audit`) —
  set-equality check against `os.listdir` of the skills dir: **exact match,
  zero dead names, zero missing names.** This half of the brief's claim is
  accurate as a POINTER but the map itself is clean.
- **Hardcoded `/proofpunk:cook` "around line 311"**: **FALSE.** I read
  `tools/build-site.py:296-323` directly (the COMMAND SURFACE section) and
  line 311 reads `<span class="name">/proofpunk:install</span>` — NOT cook.
  I then ran `git grep -n -I -w "cook"` and case-insensitive
  `grep -n -I -E "(?i)cook"` against `tools/build-site.py` specifically: **zero
  matches, in either case.** The word "cook" does not appear anywhere in
  `tools/build-site.py`'s 611 lines, in any case, in any form. **This specific
  claim in the task brief is stale/wrong** — it likely describes an EARLIER
  version of `build-site.py` (before `93c479d`/`73e928e`) that has since been
  cleaned, or the file:line pointer was carried over incorrectly from a prior
  finding about a different file. The COMMAND SURFACE table in the live file
  lists exactly the 6 current commands (`implement`, `install`, `verify`,
  `forge-prompt`, `rate-prompt`, `truth-audit`) — I confirmed 5 of the 6 rows
  by direct read (implement L308, install L311, verify L314, forge-prompt
  L317, rate-prompt L320) and none names `cook`.

## UPDATE 3 — D8 resolution: CLOSED with direct quote (not unresolved)

Contrary to any framing that D8 is open, it is **already RESOLVED** by prior
orchestrator work, and the resolution is a direct quote with zero
interpretive gloss:

> **Operator's own words** (`raw/round1-dictation.txt:3`, dictated,
> OMP session `~/.omp/agent/sessions/-proofpunk/2026-08-24T20-31-44-166Z_...jsonl:11`):
> "...it looks like the install script isn't actually properly working
> correctly, and so **you should only have one massive skill that basically
> the head will link with everything else up correctly**. And according to
> that, then you'll actually move forward with whatever happens next."

The resolution is self-evident from the sentence's own grammar, per
`evidence/v3-release/00-discovery/d1-d2-d8-transcript-evidence.md:69-78`:
"one massive skill that basically **the head will link with everything
else**" describes a HEAD that LINKS TO other things — i.e. a router. A
literal single-file merge would have nothing left to link to; the sentence
is internally self-defeating as a request for a monolith. This was
cross-validated by an exhaustive search across 34,674 OMP + 168 Claude
operator turns finding **zero** turns asking for skills to be merged into
one file (`docs/discovery-register.md:39`).

Implementation proof: commit `0de4680` (2026-08-24 20:42:05) added
`plugins/proofpunk/skills/proofpunk/SKILL.md`, routing all 17 other skills,
with reciprocal `Called by: proofpunk` lines added to each
(`docs/session-intent-ledger.md:14-17`). I independently re-verified this
holds at CURRENT HEAD (not just at the historical commit) in UPDATE 0/1
above: 48/48 edges reciprocal, 17/17 skills present in the router table,
single root confirmed.

**D8 verdict for this report: RESOLVED, with direct quote. No
interpretive gloss added — the quote is the resolution.**

STATUS: IN PROGRESS

