# D5 (sweep) — HEURISTIC scan of backtick-quoted paths in guidance

Measured 2026-09-02 @ `a41591a`. **Partial** follow-up to
`d5-referenced-artifacts.md`, which resolved only `fresh_evidence.py`.
**D5 is not complete.**

**Scope limits — this is NOT "every artifact referenced".** The scan sees
only backtick-quoted paths carrying a known extension, inside 51 guidance
files. It does **not** cover: `assets/` and `themes/`, YAML frontmatter
fields, bare unquoted filenames in prose, paths inside JSON manifests,
extensionless references, or the OMP/OpenCode mirrors.

Of the 60 unresolved: 9 classified as placeholders, 6 examined individually,
and **45 classified in bulk by their citing file
(`consolidation-decisions.md`) without each being opened.** That bulk step is
an inference, not a verified reading, and is labelled as such below.

**Remaining D5 work:** build an explicit named-artifact checklist from the
work order and guidance, and verify each entry in its own context. The
Phase 3 end-to-end read is where that lands.

## Method

Extracted every backtick-quoted path ending `.py .sh .md .json .ts .jsonl`
from 51 guidance files (root `README/CLAUDE/AGENTS`, `tools/*.md`,
`plugins/proofpunk/docs/*.md`, `references/*.md`, all 18 `SKILL.md`,
`commands/*.md`). Each reference resolved **relative to its citing file
first**, then against repo root and common roots, then by whole-tree glob.

Raw output: `raw/referenced-artifacts-sweep.txt` (`PY_RC=0`).

| Metric | Value |
|---|---|
| Guidance files scanned | 51 |
| Distinct path references | 296 |
| Unresolved | **60** |
| — placeholder-like (`NAME.md`, `SUMMARY.md`, `RULES.md`, `__main__.py`) | 9 |
| — needing judgement | 51 |

### Method correction — a false finding caught before it was written

The first run reported **183/296 unresolved** and would have branded the
skill tree as massively broken. The resolver was wrong, not the tree: it
never tried paths relative to the citing file, so every
`../../references/*.md` citation — the plugin's entire doctrine-citation
convention — was scored missing. All 13 resolve correctly from their citing
`SKILL.md`. Fixing the resolver dropped unresolved from 183 to 60.

Recorded because the first number was a *measurement artifact*, exactly the
class the work order warns about. Nothing was reported from it.

## Findings

### F-D5-3 — most unresolved refs are likely correct HISTORY (BULK-INFERRED)

`plugins/proofpunk/docs/consolidation-decisions.md` accounts for most of the
51. It names pre-consolidation skills — `cook/SKILL.md`,
`functional-validation/SKILL.md`, `e2e-validate/SKILL.md`,
`create-validation-plan/SKILL.md`, `harden-plan/SKILL.md`,
`deepen-prompt-plan/SKILL.md`, `fresh-evidence/SKILL.md`,
`gate-validation-discipline/SKILL.md`, `ios-validation-runner/SKILL.md`,
`full-ui-experience-audit/SKILL.md`, `build-quality-gates/SKILL.md`,
`code-task-generator/SKILL.md`, `create-meta-prompts/SKILL.md` — precisely
because that document records **what was merged into what**. A merge log that
stopped naming its inputs would be useless.

**Confidence: inferred, not verified.** These 45 were classified by their
citing file, not by opening each citation's surrounding context. Treated as
a hypothesis for the Phase 3 read to confirm or overturn.

If it holds, it matters for L8: the work order directs sweeping dead names
(`cook`, `functional-validation`) from active guidance, and
`consolidation-decisions.md` is the provenance record, not active guidance.
No sweep directive is issued from this file — Phase 3 decides.

### F-D5-4 — individually inspected entries

| Reference | Cited by | Status after reading the line |
|---|---|---|
| `api/web/cli/ios-validation.md` | `implement/SKILL.md:242` | **NOT a defect — retracted.** An earlier draft of this file called it a malformed citation. Reading the line disproves that: "The platform runbooks (`api/web/cli/ios-validation.md`) are shared doctrine in `references/`, not a skill — Stage 5 loads them directly." It is prose shorthand naming four runbooks, deliberately not a link. No fix required; the earlier L17 directive is withdrawn. |
| `.omp/AGENTS.md` | `docs/invocation-contracts.md` | Unresolved as written; repo has `AGENTS.md`, `tools/AGENTS.md`, `evidence/AGENTS.md` and no `.omp/` variant. **Context not yet read** — could equally be prose about the OMP host's own file. Phase 2 (C4) and the Phase 3 read decide. No directive issued. |
| `.code-task.md` | `docs/consolidation-decisions.md` | No basename match in tree. Probably a historical artifact name. Context not read. |
| `evaluate-session.sh`, `fresh-evidence.sh` | `docs/consolidation-decisions.md` | Named as pre-merge scripts; no basename match. Same historical class, same confidence caveat. |
| `a-sql-review-prompt.prompt.md`, `.prompts/onboarding/NN-stage/PROMPT.md` | `README.md` | Illustrative example paths in prose. Not defects; noted so a future gate does not flag them. |

### F-D5-5 — placeholder tokens must be excluded from any citation gate

Nine references are documented *templates*, not paths: `NAME.md`,
`NAME.rating.md`, `NAME.optimized.md`, `NAME.remediated.md`,
`NAME.prompt.md`, `SUMMARY.md`, `RULES.md`, `__main__.py`. They describe the
prompt-forge output contract (`NAME.rating.md` etc.) and are correct as
written. Any L12/L15 citation gate must whitelist this shape or it will
generate nine permanent false positives.

## Consequence for later phases

No documentation-fix directives are issued from this heuristic scan. Two
*gate-design* lessons stand, because both come from errors made and measured
inside this sweep:

1. **L12/L15 (gates)** — a citation gate MUST resolve paths relative to the
   citing file. Not doing so produced a false 183/296-unresolved reading here.
2. **L12/L15 (gates)** — a citation gate MUST whitelist documented
   placeholder shapes (`NAME.*`, `SUMMARY.md`, `RULES.md`, `__main__.py`) or
   it generates nine permanent false positives.

Everything else — including whether `consolidation-decisions.md` should be
excluded from the L8 dead-name sweep — is deferred to the Phase 3 read of the
actual files.

## Evidence

`evidence/v3-release/00-discovery/raw/referenced-artifacts-sweep.txt` —
full unresolved list with citing files, `PY_RC=0` captured separately.
