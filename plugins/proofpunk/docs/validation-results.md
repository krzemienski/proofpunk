# Validation Results — Proofpunk v1.0.0

All validation was run against the real plugin source. No mocks, no stubs,
no simulated results. Dates of runs: 2026-08-08 (initial pass + policy
enforcement pass), 2026-08-09 (skills-ref.zip second-source pass).

## 1. Manifest Validation — PASS

- `marketplace.json` and `plugin.json` parse as valid JSON.
- Required fields present: marketplace `name`/`owner`/`plugins`; plugin
  `name`/`version`/`description`.
- Names are kebab-case and not on the reserved-name list.
- Marketplace `source: ./plugins/proofpunk` resolves to an existing
  directory with a matching plugin manifest.

## 2. Skill Frontmatter Validation — PASS (10/10)

Every `skills/<name>/SKILL.md` has YAML frontmatter with `name` matching its
directory and a `description`. Line counts (all within progressive-disclosure
budgets):

| Skill | Lines |
|---|---|
| brainstorm | 153 |
| cook | 145 |
| end-user-testing | 172 |
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
`../skills/end-user-testing/scripts/fresh_evidence.py` (expressed there as a
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
| `functional-validation`, `end-user-testing`, `full-functional-audit` | Verdict templates now record "Driven by: AI as end user via <tools> — <actions performed>" and offer UNVERIFIED for unexecuted criteria |
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
| `../references/preflight-checks.md` | NEW shared reference from ref `preflight` (61 lines); linked from `end-user-testing` Step 3 and `platform-routing.md` |
| `../references/ci-gates.md` | NEW shared reference from ref `build-quality-gates` (34 lines); linked from `end-user-testing` Related Skills |
| `../skills/end-user-testing/assets/verdict-template.md` | NEW asset adapted from ref `e2e-validate/templates/verdict.md` with Driven-by / Actions-executed / UNVERIFIED (40 lines) |
| `../skills/validation-plan/references/task-file-format.md` | NEW from ref `code-task-generator` with End-User Actor policy applied (60 lines); linked from `validation-plan` Step 3 |
| `../skills/full-functional-audit/SKILL.md` | Per-platform team templates (iOS / Web-Full / API-only) with EXCLUSIVE/PARALLEL mutex annotations (134 -> 154 lines) |
| `../skills/prompt-forge/SKILL.md` | Input-type handling table, capability-inventory injection, model tone guidance (136 -> 171 lines) |

Post-change verification (all real runs against the packaged source):

- **Structural validator: 0 errors**, 99/99 reference paths resolve (up from
  77 — every new citation from `end-user-testing`, `validation-plan`,
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
  marketplace layout (`proofpunk-marketplace.tar.gz`) per the plugin
  marketplace schema; the `.skill` files prove per-skill format adherence
  and package correctly, but standalone installs lack the shared references.
- **End-to-end dogfood**: the full 10-skill series was executed against a
  real repository (pallets/flask tutorial app, fetched and byte-verified via
  the GitHub MCP cloud plugin) implementing a real feature ("Mood Ring"):
  brainstorm → prompt-forge (91/100 rated prompt) → validation-plan →
  plan-hardening (5 findings dispositioned) → cook (32/32 pytest green) →
  functional-validation + end-user-testing (19-file sealed evidence run,
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

## 12. Session-First Reorientation (v1.2.0) — PASS (16/16)

User correction: the plugin must look at the sessions themselves — transcripts
carry prompt intent; summaries are claims. Added `session-intent` with a real
stdlib parser (`session_intent.py`) for `~/.claude/projects/**/*.jsonl`.

- **Parser verification**: end-to-end run against a constructed fixture in the
  real JSONL event shape — 2 sessions parsed; tool_result events excluded from
  prompts; intent/steering/commit/file extraction asserted correct. Fixture is
  constructed data, honestly labeled; first live-corpus run remains the real
  gate (stated in the skill itself).
- **Format**: 16/16 skills pass official skill-creator validation.
- **References**: incorporated `claude-code-analyzer` body + 4 scripts
  (`bash -n` clean); all path citations re-resolved, 0 broken.

## 13. Doctrine Clarification — Test Runners Are Never Validation (v1.2.1, 2026-08-10)

User correction: the plugin must state explicitly that pytest (and any test
runner) is never the validation mechanism — validation is the live system
driven as the end user; for a JSON/HTTP Flask backend that means real `curl`
requests to the running server on localhost with assertions on real responses.

Changes:

- `references/end-user-actor.md`: new "Test Runners Are Never Validation"
  section + actor/spectator table row. Test-runner output may appear only as
  REGRESSION evidence, clearly labeled. Framework test clients (Flask
  `test_client`) are regression gates, not end users — they bypass the
  network stack. When a contract asks for "tests pass" as proof of done, the
  correct reading is: tests green (regression) AND live end-user drive
  (validation); either alone is incomplete.
- `functional-validation` NEVER list: explicit ban on citing test-runner
  output as validation evidence.
- `stack-testing` rule 5: test output is sealed as REGRESSION evidence only;
  feature verdicts come solely from live end-user driving.
- `examples/mood-ring/.prompts/build-mood-ring/PROMPT.md`: output contract
  amended — the confusing "`pytest` output (must exit 0)" line is now
  "REGRESSION gate, labeled, never a validation verdict" plus explicit curl
  validation requirements; `<validation>` section names curl-to-localhost as
  the mechanism for HTTP backends.

Compliance of the existing demo run under the amended contract: the sealed
run already validates via curl captures of the live server (steps 01, 03–09,
12, 14, 15) and browser drives (steps 10, 11, 13, 18, 19); step-17
(32 passed) stands as the REGRESSION rail. No re-run required; the prompt
amendment aligns the contract with what was actually executed.

## 14. Installer Script (v1.3.0, 2026-08-10) — PASS (8/8 live tests)

`tools/proofpunk-install.sh` installs the 16 skills as plain skills (not a
plugin) into a chosen target (claude-code / omp / --dir), with collision
safety, doctrine injection, and post-install verification. Executed live
before shipping (no claimed-but-unrun behavior):

1. `--target omp --dry-run` — full plan printed, zero writes.
2. GitHub-source install into a sandboxed HOME — 16/16 installed + doctrine
   bundle + verify green. **The verifier caught a real design flaw**: repo
   layout cites doctrine as `../../references/`, broken in a flat skills dir;
   fixed by making installed copies self-contained (citations rewritten,
   cited shared refs bundled inside each skill) — then verify green.
3. Re-run without `--override` — 16/16 SKIP on collision, nothing clobbered.
4. `--override` — replaced with timestamped backups (`.bak-YYYYMMDD-HHMMSS`).
5. `--inject-claude-md` twice — rules block appended once; second run
   "already present — left unchanged" (idempotent).
6. `--source-dir` local checkout — installs offline path, verify green.
7. `--only not-a-skill` — exits 3 (caught a second real bug: the EXIT trap's
   cleanup returned 1 and clobbered the intended code; fixed, re-verified).
8. `bash -n` syntax clean; exit codes 0/1/2/3 as documented in tools/INSTALL.md.

## 15. prompt-forge Rework (v1.4.0, 2026-08-11) — PASS

Directive: rating remediations must be applied immediately and always land
in a file (new file by default, the input file only with consent); every
mode must run sequential thinking, proper XML tags, an authorization
engine, and explicit todo tracking.

Changes to `skills/prompt-forge/SKILL.md` (quick_validate: PASS):

1. **New Section 0 — Always-On Workflow**, binding on all four modes:
   - 0.1 Sequential thinking — numbered reasoning steps with explicit
     revision and branching before any authoring/rating/optimizing.
   - 0.2 Todo discipline — one action per todo, one in-progress at a time,
     immediate completion, pending items finished or reported.
   - 0.3 Authorization engine — decision table: new-file writes need no
     consent (default action); in-place edits, below-threshold shipping,
     overwrites, and report-only ratings all require explicit consent.
   - 0.4 File-output contract — per-mode file matrix
     (`NAME.prompt.md` / `NAME.rating.md` + `NAME.remediated.md` /
     `NAME.optimized.md` / `.prompts/` stages); chat-only suggestions are
     a contract violation.
   - 0.5 XML tag standard — canonical skeleton (`task`, `context`,
     `skills_to_activate`, `mcp_tools`, `sequential_thinking`, `todos`,
     `authorization`, `constraints`, `output_contract`, `validation`,
     `example`) with a required/optional purpose table; aligned with the
     mood-ring demo prompt's existing tag usage.
2. **RATE §2.1 Remediation application (mandatory)** — scorecard alone is
   unfinished: apply top fixes, write `NAME.remediated.md` (in-place only
   with consent), re-score against the same test cases, report
   before/after; below-threshold results route through 0.3.
3. **OPTIMIZE** — optimized prompt written to `NAME.optimized.md` per 0.4;
   failure classification lands in the sequential-thinking chain.
4. **PIPELINE** — every stage prompt follows the 0.5 skeleton; every stage
   maps to a todo.
5. **Anti-patterns** — six new rows: scorecard-only rating, chat-only
   fixes, unconsented in-place edits, below-threshold shipping,
   jump-to-output, ad-hoc XML tags.

Source-gap note (honest gap): the sequential-thinking stage was specified
from the established methodology (numbered steps, revision, branching —
the `ck:sequential-thinking` description fragment in the archive
inventory). The reference archive's `ak-sequential-thinking` copy contains
zero files and its `sequential-thinking` copy has no SKILL.md; the primary
archive's `ck:sequential-thinking` was unreachable this session (HTTP 403).
No content was copied from a source that could not be read.

Frontmatter description rewritten (1011 chars, under the 1024 limit) to
advertise the always-on workflow and file-output remediation contract.

## 16. prompt-forge Command Surface + implement Skill (v1.5.0, 2026-08-11) — PASS

Two directives: (a) the v1.4.0 prompt-forge rework described remediation
abstractly but showed no concrete remediation sample and no CLI arguments;
(b) a new `implement` command should orchestrate the actual implementation
process using ALL skills, with session mining and parallel/auto modes.

### prompt-forge additions (quick_validate: PASS)

1. **Command Surface section** — CLI-style flags mapped onto the
   authorization engine (0.3), so a flag IS the recorded consent:
   `--in-place` (in-place edit consent), `--report-only` (skip file
   output), `--ship-below-threshold` (below-threshold sign-off), `--out`,
   `--depth`, `--evidence` (OPTIMIZE's hard requirement), `--dir`.
   Unknown flags rejected; conflicting flags fail fast.
2. **`references/remediation-sample.md`** — a full worked RATE pass on a
   weak prompt: sequential-thinking chain, scorecard (34/100, rewrite),
   predicted failure modes, four test cases, the remediated file on the
   canonical XML skeleton, re-score (91/100), and what each flag would
   have changed.

### implement skill (quick_validate: PASS)

New skill `skills/implement/SKILL.md` — the orchestrator (conductor) to
cook's execution engine (player), resolving the overlap question
explicitly in both directions:

- **Command surface** *(as of that release; `--no-test` and `--tdd` were
  later removed, and `cook` was merged into `implement` — see
  `improvements.md`)*: `implement "<goal>" [--parallel] [--auto] [--mine]
  [--fast] [--no-test] [--tdd]` and `implement mine [--project] [--since]
  [--until] [--json]`, each flag with a why-it-exists column.
- **Phase 0 — TRUE success criteria distillation**: observable, end-user
  provable, measurable; approval gate when the goal is not clearly laid
  out or not understood — the one mandatory stop under `--auto`.
- **Phase 1 — MINE** via session-intent: past implementation sessions as
  an intent matrix (prompts, tools, files, commits) feeding exploration
  and forging; `implement mine` alone is a reconnaissance-only pass.
- **Phase 2 — EXPLORE** with parallel scout agents (structure, patterns,
  contracts, history); contradictions resolved against the code.
- **Phase 3 — FORGE** via prompt-forge AUTHOR on the canonical XML
  skeleton; approved criteria become the prompt's success metrics verbatim.
- **Phase 4 — PLAN**: validation-plan + plan-hardening; `--parallel` ->
  prompt-forge PIPELINE with parallel independent stages.
- **Phase 5 — EXECUTE** under cook's gates; `--parallel` lanes with
  per-lane todo chains; authorization boundaries (destructive ops,
  out-of-scope edits, below-threshold shipping) bind even `--auto`.
- **Phases 6-8**: root-cause-debugging (no retries as fixes), end-user
  validation (UNVERIFIED = NOT DONE under `--auto`), criteria-by-criteria
  proof table + todo ledger.

### Propagation

plugin.json 1.5.0 (description + 6 keywords), marketplace.json 1.5.0,
README skill table + counts (16 -> 17), installer `ALL_SKILLS` +
INSTALL.md counts/examples updated. Both new/changed skills packaged
self-contained (shared refs bundled, citations rewritten).

## 17. README Command Reference + Architecture Diagrams (v1.5.1, 2026-08-11) — PASS

Directive: the README must lay out every example with every argument —
including positional arguments inside skill commands — every meaningful
permutation with why / what happens / what you end up with, which skills
execute per invocation, and system architecture diagrams.

Delivered in README.md (629 lines, +550):

> **Historical record.** This section describes the surface *as shipped in
> that release*. `cook` and `functional-validation` were later merged into
> `implement`, and the `--tdd` / `--no-test` flags were removed. For the
> current surface see `usage-guide.md` and `improvements.md`.

1. **Dispatch-at-a-glance table** — invocation -> skill fired -> delegation.
2. **§1-8 command references** for every argumented surface: implement
   (positionals `<goal>`/`mine`, 8 flags, 14 permutations), prompt-forge
   (positionals per subcommand, 7 flags, 9 permutations, conflict rules),
   cook (positionals `<goal>`/`<plan-path>`, 5 modes, full mode × --tdd
   12-permutation table), functional-validation (8 flags composing
   analyze->plan->execute->fix->report), session-intent (5 args with
   defaults, filter/output permutations, exit 2), end-user-testing
   (positional `<slug>`, lifecycle as the only valid composition, exit
   codes), stack-testing (`--server`/`--port`/trailing positional),
   installer (13 flags + canonical permutations + conflicts + exit codes).
   Every row answers why / what happens / what you end up with, and names
   the skills executed downstream.
3. **§9 protocol-skill routing** — the 10 flag-less skills: invocation ->
   what happens -> downstream skills, all edges from the skills' own
   Related Skills sections (verified by extraction, not written from
   memory).
4. **Five mermaid architecture diagrams** — repo layout, layered skill
   stack with the doctrine foundation, the full delegation graph (real
   edges only), a sequence trace of
   `implement "add billing webhooks" --parallel --auto --mine`, and the
   evidence lifecycle state diagram.

Mechanical checks: code fences balanced (28/28), 5/5 mermaid blocks
closed, all 17 skill names referenced.

## 18. Related-Skills Closure + Usage Guide (v1.6.0, 2026-08-11) — PASS

Directive: document the plugin and skills properly with `/skill-name
example --arg` usage in Claude Code; ensure every skill needed by the
Related Skills graph actually ships; update the installer and docs.

### Integrity audit (mechanical, full closure)

1. **Related Skills edges**: extracted every backtick-quoted reference in
   all Related Skills sections and resolved each against the skills
   directory. Found ONE dangling edge: session-intent referenced
   `codebase-truth-audit`, which was not in the plugin. **Fixed by
   shipping it**: the skill (SKILL.md + references/output-contract.md +
   scripts/init_audit_workspace.py) integrated as skill #18, with a new
   Related Skills section closing the edge both directions. Re-run of the
   audit: 18/18 skills, zero dangling edges.
2. **Reference citations**: every `references/X` citation in every skill
   file (SKILL.md, references, scripts) resolved against the tree —
   including shared `../../references/` doctrine paths and cross-skill
   `../skill/scripts/` paths. Zero missing targets.
3. **Bundled scripts**: every `scripts/X` citation resolved.
   `init_audit_workspace.py` verified LIVE (not by inspection): ran
   `--repo /tmp/repo --label Proofpunk-v151` end to end — produced a
   real 8-phase audit workspace with captured git evidence (status,
   remotes, metadata). Exit 0, artifacts non-empty.

### Usage guide

New `plugins/proofpunk/docs/usage-guide.md`: how invocation works in
Claude Code (slash command vs natural-language routing vs chaining),
then per-skill sections for all 18 skills with positional arguments,
flags, and literal `/skill-name <args>` example invocations, the three
bundled CLIs (session_intent.py, fresh_evidence.py,
init_audit_workspace.py, with_server.py) with their real argument lists,
and seven chaining recipes. INSTALL.md gained an "After install" usage
section; README links the guide and shows 18 skills.

### Propagation

plugin.json 1.6.0 (description + 3 keywords), marketplace.json 1.6.0,
README table + counts (17 -> 18), installer ALL_SKILLS +
INSTALL.md counts. Both quick_validates PASS (codebase-truth-audit,
session-intent).
