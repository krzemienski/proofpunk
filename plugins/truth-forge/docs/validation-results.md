# Validation Results — truth-forge v1.0.0

All validation was run against the real plugin source. No mocks, no stubs,
no simulated results. Dates of runs: 2026-08-08 (initial pass + policy
enforcement pass), 2026-08-09 (skills-ref.zip second-source pass).

## 1. Manifest Validation — PASS

- `marketplace.json` and `plugin.json` parse as valid JSON.
- Required fields present: marketplace `name`/`owner`/`plugins`; plugin
  `name`/`version`/`description`.
- Names are kebab-case and not on the reserved-name list.
- Marketplace `source: ./plugins/truth-forge` resolves to an existing
  directory with a matching plugin manifest.

## 2. Skill Frontmatter Validation — PASS (10/10)

Every `skills/<name>/SKILL.md` has YAML frontmatter with `name` matching its
directory and a `description`. Line counts (all within progressive-disclosure
budgets):

| Skill | Lines |
|---|---|
| brainstorm | 153 |
| cook | 145 |
| evidence-gates | 172 |
| full-functional-audit | 154 |
| functional-validation | 239 |
| plan-hardening | 145 |
| prompt-forge | 171 |
| ui-experience-audit | 194 |
| validation-plan | 143 |
| visual-inspection | 144 |

(Line counts reflect the final state after the skills-ref.zip incorporation;
all remain within progressive-disclosure budgets, with heavier detail pushed
into per-skill `references/`.)

## 3. Internal Reference Integrity — PASS (99/99)

Every `references/`, `assets/`, and `scripts/` path cited from any plugin
markdown file was resolved against the filesystem: 99 citations checked, 0
broken. This includes the cross-skill relative paths used inside skills —
e.g. `skills/functional-validation/SKILL.md` reaches the helper at
`../skills/evidence-gates/scripts/fresh_evidence.py` (expressed there as a
dot-dot path) and every skill reaches the shared contract at
`../references/evidence-contract.md` (expressed there as `../../`).

## 4. Placeholder / Dependency Scan — PASS

- No placeholder tokens (`[TODO]`, `[INSERT ...]`, `[PLACEHOLDER]`, `{???}`,
  `FIXME`) in any shipped file. Four scanner hits were manually reviewed and
  confirmed to be the placeholder-DETECTION rules themselves (the
  defect-database row describing lorem-ipsum detection, prompt-forge's
  no-placeholders quality gate, and this document's own description of the
  scan) — legitimate content.
- The bundled script imports only Python stdlib (`re`, `sys`, `pathlib`,
  `datetime`, `__future__`). No external or unsupported dependencies anywhere
  in the plugin.
- No macOS metadata (`._*`, `.DS_Store`) and no `__pycache__` in the tree.
- `python3 -m py_compile` on `fresh_evidence.py`: OK.

## 5. Functional Tests — `fresh_evidence.py` (12/12 PASS)

Real invocations against a scratch directory (`/tmp/fe-test`):

| # | Test | Expected | Actual |
|---|------|----------|--------|
| 1 | `init-run login-flow` | exit 0, prints `run-<ISO>-login-flow`, creates dir + `.run-meta` + empty inventory | PASS |
| 2 | `init-run "bad slug!"` | exit 2, `slug must be kebab-case alnum/dash/underscore` | PASS |
| 3 | `next-step home-loaded` | exit 0, prints `.../step-01-home-loaded` | PASS |
| 4 | capture two artifacts (>1KB each) | files land at printed prefixes; step numbers sequential | PASS |
| 5 | `seal` | writes inventory with per-file byte counts + `sealed=... count=2 total_bytes=3041` | PASS |
| 6 | `validate` (clean run) | exit 0, `validate OK: e2e-evidence/run-...` | PASS |
| 7 | `validate` with a zero-byte artifact | exit 2, `EMPTY: ... (zero bytes)` + `validate FAIL: 1 issues` | PASS |
| 8 | `validate` with a 2020-mtime artifact | exit 2, `STALE: ... (mtime 1577808000 < run-start ...)` | PASS |
| 9 | `next-step`/`seal`/`validate` with no run | all exit 2, `no active run` | PASS |
| 10 | unknown command `frobnicate` | exit 2 + usage | PASS |
| 11 | `init-run` with no slug | exit 2, `init-run requires a slug` | PASS |
| 12 | `validate` after removing bad artifacts | exit 0 (recovery path works) | PASS |

Malformed and incomplete inputs fail clearly and safely (exit 2 + a specific
stderr message); no tracebacks, no partial writes on refusal paths.

## 6. Capability Smoke Review — PASS

Each of the 10 skills was re-read after authoring to verify its incorporated
source capabilities are present and internally consistent (gate patterns
match `evidence-contract.md`, severities match `severity-model.md`, platform
traps match `platform-routing.md`, end-user mandate cited where actions
occur). See `consolidation-decisions.md` for the full source-to-skill map.

## 7. Blocked Item (environment limitation)

`claude plugin validate .` and a live `/plugin install` smoke test could not
be run: the `claude` CLI is not available in this environment. Mitigation:
the structural checks in sections 1–3 implement the documented manifest and
layout contract from the archive's own `skill-creator` and `working-with-cc`
plugin references (required fields, kebab-case names, reserved-name check,
`skills/<name>/SKILL.md` layout, marketplace source resolution). Installing
from the packaged archive (README section "Installation") performs the final
in-product verification.

## 8. End-User Validation Policy Enforcement Audit — PASS

Full-plugin audit and rewrite pass enforcing the policy: **validation is
never faked, skipped, stubbed, or assumed complete — the AI actually
executes MCP/automation tools and acts as the end user, for every
skill/feature, or reports the outcome UNVERIFIED.**

Changes applied and re-verified:

| Location | Change |
|---|---|
| `../references/evidence-contract.md` | Added "The Non-Negotiable Validation Rule" after the Iron Rule; added two refusal rules (no completing validation without the AI invoking tools as the end user; no skipping/faking QA steps under any circumstance) |
| `../references/end-user-actor.md` | Non-negotiable statement at the head of The Rule |
| `../references/severity-model.md` | Added UNVERIFIED verdict; PASS for behavior now requires executed, tool-driven, end-user checks |
| All 10 skills | Two anti-pattern rows added to every anti-pattern table (verified placed inside tables with matching column counts) |
| `functional-validation`, `evidence-gates`, `full-functional-audit` | Verdict templates now record "Driven by: AI as end user via <tools> — <actions performed>" and offer UNVERIFIED for unexecuted criteria |
| `validation-plan` | VALIDATION.md handoff requires an explicit record of executed end-user actions |
| `plan-hardening` | Consensus checklist requires every behavioral criterion to pair with a driven end-user action; gate block verdict adds UNVERIFIED |
| `cook` | End-user verification gate: never skipped/faked; no tool path -> report says UNVERIFIED with reason; finalize cites driven evidence per criterion |
| `brainstorm` | Success metrics/validation criteria must be phrased as end-user-executable checks |
| `prompt-forge` | Quality gate 8: end-user validation clause for any system-touching prompt |
| `visual-inspection` | PASS certifies visual quality only; behavioral claims route to driven validation |
| `ui-experience-audit` + report template | UNVERIFIED verdict added; template header records tools + actions actually executed |
| `README.md` | Operating Principle 2 restated with the non-negotiable language |

Post-change verification: structural validator 0 errors (77 reference paths
checked — all new `end-user-actor.md` citations resolve); every anti-pattern
table pipe-count verified; policy-language coverage confirmed in 10/10
skills with 9/10 linking the shared mandate directly and `brainstorm`
linking it from its report criteria; `fresh_evidence.py` recompiles clean
(the script itself was not modified in this pass).

## 9. Second-Source Pass — skills-ref.zip Incorporation — PASS

Date of runs: 2026-08-09. Source: `skills-ref.zip`, SHA-256
`fe1209f9bdf10fc2249552dbcd8b4b48b9f59a69aeef9fe0db7d60bc5e009d7d`
(26,223,521 bytes; 549 top-level entries, 334 with `SKILL.md`). Full
source-to-destination map in `consolidation-decisions.md` ("Second Source
Set").

Changes applied in this pass:

| Location | Change |
|---|---|
| `../skills/functional-validation/references/{ios,web,api,cli}-validation.md` | 4 platform runbooks carried verbatim from the ref `functional-validation` (85/88/75/120 lines) |
| `../skills/functional-validation/SKILL.md` | Step 1 runbook-loading table; Failure Diagnosis Table; Multi-Platform Order; Evidence Quality Standards; Mock Detection Red Flags; NEVER list (158 -> 239 lines) |
| `../references/preflight-checks.md` | NEW shared reference from ref `preflight` (61 lines); linked from `evidence-gates` Step 3 and `platform-routing.md` |
| `../references/ci-gates.md` | NEW shared reference from ref `build-quality-gates` (34 lines); linked from `evidence-gates` Related Skills |
| `../skills/evidence-gates/assets/verdict-template.md` | NEW asset adapted from ref `e2e-validate/templates/verdict.md` with Driven-by / Actions-executed / UNVERIFIED (40 lines) |
| `../skills/validation-plan/references/task-file-format.md` | NEW from ref `code-task-generator` with End-User Actor policy applied (60 lines); linked from `validation-plan` Step 3 |
| `../skills/full-functional-audit/SKILL.md` | Per-platform team templates (iOS / Web-Full / API-only) with EXCLUSIVE/PARALLEL mutex annotations (134 -> 154 lines) |
| `../skills/prompt-forge/SKILL.md` | Input-type handling table, capability-inventory injection, model tone guidance (136 -> 171 lines) |

Post-change verification (all real runs against the packaged source):

- **Structural validator: 0 errors**, 99/99 reference paths resolve (up from
  77 — every new citation from `evidence-gates`, `validation-plan`,
  `platform-routing.md`, and these docs to the new references/assets
  resolves). 4 warnings, all manually confirmed as the
  placeholder-DETECTION rules themselves.
- **New-file spot checks**: all 8 new carried/authored files non-trivial
  (1,204–6,680 bytes); policy language (`UNVERIFIED`, end-user/driven-action
  clauses) confirmed present in both new policy-bearing files
  (`task-file-format.md`, `verdict-template.md`).
- **`fresh_evidence.py` functional re-run: 12/12 PASS** against a fresh
  scratch directory (init-run, bad-slug refusal, next-step sequencing,
  artifact capture, seal with `count=2 total_bytes=3548` in the inventory,
  clean validate, empty-artifact refusal, stale-artifact refusal, no-run
  refusals, unknown-command refusal, missing-slug refusal, recovery
  validate). The script was not modified in this pass; the re-run confirms
  no collateral damage.
- **Exclusions honored**: `testing-anti-patterns` / `tdd-workflow` /
  `testing-strategy` (mock-first TDD conflicts with the Iron Rule),
  `website-bug-hunt` (duplicates `bug-hunnter` + `full-functional-audit`),
  `worktree-merge-validate` (Auto-Claude ecosystem dependency), and the
  empty `ak-brainstorm` / `ak-cook` stubs were NOT incorporated — verified
  absent from the plugin tree.

## 10. Official skill-creator Format + Packaging Pass — PASS (10/10)

Date of run: 2026-08-09. Tooling: the environment's own `skill-creator`
skill (its `quick_validate.py` and `package_skill.py` scripts, external to
this plugin).

- **First run found one real violation**: `validation-plan`'s description
  used `->` arrows; the official contract forbids `<`/`>` in descriptions
  (max 1024 chars, kebab-case name ≤64, frontmatter keys restricted to
  name/description/license/allowed-tools/metadata/compatibility).
  **Fixed** (`->` → `→`) and re-validated.
- **Final: 10/10 skills "Skill is valid!"** under the official validator.
- **Packaging: 10/10 `.skill` files produced** by `package_skill.py` (zip
  format, `<skill-name>/SKILL.md` at archive root, integrity-checked).
  Distribution note: the 10 skills share plugin-root `references/` by design
  (`../../references/...` links), so the installable unit for the set is the
  marketplace layout (`truth-forge-marketplace.tar.gz`) per the plugin
  marketplace schema; the `.skill` files prove per-skill format adherence
  and package correctly, but standalone installs lack the shared references.
- **End-to-end dogfood**: the full 10-skill series was executed against a
  real repository (pallets/flask tutorial app, fetched and byte-verified via
  the GitHub MCP cloud plugin) implementing a real feature ("Mood Ring"):
  brainstorm → prompt-forge (91/100 rated prompt) → validation-plan →
  plan-hardening (5 findings dispositioned) → cook (32/32 pytest green) →
  functional-validation + evidence-gates (19-file sealed evidence run,
  `validate OK`) → visual-inspection (found + fixed a real HIGH contrast
  defect) → ui-experience-audit → full-functional-audit (PASS). Walkthrough
  report delivered alongside this document.

## 11. Mission-Fit Expansion Pass (v1.1.0) — PASS (15/15)

Triggered by a post-delivery usefulness audit: the original scan had bucketed
407/445 archive skills as "other" without classification. Full-universe
re-scan (664 unique skills, 15 usefulness domains) identified 26 readable,
mission-aligned sources in skills-ref.zip (re-downloaded; SHA-256 matched the
first pass) and consolidated them into 5 new skills: `stack-testing`,
`mobile-validation-runner`, `root-cause-debugging`, `production-readiness`,
`red-team-eval`.

Results:

- **Format**: all 15 skills pass the official skill-creator frontmatter
  validation (one YAML colon-in-flow-scalar error found in
  `root-cause-debugging`'s description during authoring; fixed with a block
  scalar before delivery).
- **Reference integrity**: 149 path citations across the expanded plugin
  resolved against the filesystem; 10 broken citations found inside
  incorporated reference bodies (paths relative to their original skill
  layouts) — all re-pointed to the bundle layout; final count 0 broken.
- **Script integrity**: bundled Python (`with_server.py`) compiles; all 6
  bundled shell scripts pass `bash -n`; the Playwright runner parses under
  `node --check`.
- **Policy**: mock-framework sources incorporated only with explicit Iron
  Rule adaptation notes; mock-first doctrine skills remain excluded (see
  consolidation-decisions.md, Third Source Pass).
- **Honesty gap preserved**: Android and accessibility-audit sources exist
  only in the now-inaccessible (403) skills.zip; the mobile skill documents
  the Android gap explicitly instead of improvising content.
