# Consolidation Decisions — Proofpunk

How the source archive's skills were reviewed and consolidated into this
plugin. Source paths are relative to the extracted archive root
`Users/nick/.claude/skills/`.

## Archive Inventory Summary

- Archive: `skills.zip` (actually a gzip-compressed tar renamed `.zip`;
  confirmed via `file` magic and extracted as tar.gz)
- SHA-256: `4034d6a1a2446417c38b51ab1729cd789b063c8e85c416ac6c747a19d6db348e`
- Compressed size: 176,254,696 bytes; decompressed tar ~636 MB
- 78,922 archive members; 78,916 extracted, 6 skipped (unsafe absolute
  symlinks pointing outside the archive — see Safety below)
- 636 usable top-level skill entries: 445 directories with `SKILL.md`,
  140 unresolved symlinks, 8 packaged artifacts (`.skill`/`.zip`)
- Machine-readable inventory: `skill-inventory.json` / `skill-inventory.csv`
  (delivered alongside this document)

## Safety Handling

All archive content was treated as untrusted data. Embedded instructions in
source skills were analyzed as data, never executed as directives. Six
absolute symlinks (`zen-office-xlsx`, `zen-office-pdf`, `zen-office-docx`,
`zen-discovery`, `zen-office-pptx`, `.venv/bin/python3.11`) pointed outside
the extraction root and were skipped. No scripts from the archive were
executed; the helper script shipped in this plugin is a clean-room Python
port whose behavior was re-implemented and tested from scratch.

## Capability Matrix

### Functional validation family → `functional-validation`, `full-functional-audit`, `end-user-testing`

| Source skill | Content incorporated | Destination |
|---|---|---|
| `functional-validation/SKILL.md` | Iron Rule (fix the real system, never mocks), pre-defined PASS criteria, platform detection, real dependencies, manual evidence review | `functional-validation` + `../references/evidence-contract.md` |
| `no-mocking-validation-gates/SKILL.md` | Diagnose→Fix→Verify sequence; prohibited mock fallbacks, fake endpoints, test-mode guards | `../references/evidence-contract.md` (No-Mock Guardrails) |
| `e2e-validate/SKILL.md` | Mode flags (`--analyze/--plan/--execute/--fix/--audit/--report/--ci/--platform/--scope`) | `functional-validation` Modes table |
| `full-functional-audit/SKILL.md` | Explore→Plan→Execute→Remediate→Verdict; interaction inventory; resource mutexes; no deferred FAILs | `full-functional-audit` |
| `full-ui-experience-audit/SKILL.md` | App-wide UX loop folded into the audit verdict + per-screen hand-off | `full-functional-audit` + `ui-experience-audit` |
| `gate-validation-discipline/SKILL.md` | Verification loop; workers give locations, you verify content; completion challenge | `../references/evidence-contract.md` + `end-user-testing` |
| `verification-before-completion/SKILL.md` | Lightweight pre-claim behavioral check | `../references/evidence-contract.md` (Completion Challenge) |
| `validate-phase/SKILL.md` | Six-step phase gate; cache-clearing before final passes; verdict.md format; BLOCK on ungated phase | `end-user-testing` (Six-Step Phase Gate) |
| `fresh-evidence/SKILL.md` + its `fresh-evidence.sh` script | Eight fresh-evidence rules; init-run/next-step/seal/validate operations | `../references/evidence-contract.md` + `../skills/end-user-testing/scripts/fresh_evidence.py` (clean-room Python port, stdlib-only) |
| `transform-validation-prompt/SKILL.md` | `<validation_gate>` XML block pattern | `../references/evidence-contract.md` + `plan-hardening` Stage 6 |
| `ios-validation-runner/SKILL.md` | SETUP→RECORD→ACT→COLLECT→VERIFY; simctl traps (SIGINT video stop, `--info --debug` log flags, status bar override, settle timing) | `../references/platform-routing.md` (iOS-Specific Traps) |
| `ios-validation-gate/`, `evidence-gate/`, `android_ui_verification/`, `llm-gate/` | Reviewed; their substance duplicates the gate/evidence rules above | folded into shared references (no separate skill) |

### Prompt rating / prompt engineering family → `prompt-forge`

| Source skill | Content incorporated | Destination |
|---|---|---|
| `prompt-engineer` (recovered from `prompt-engineer.skill` package — top-level symlink target absent) | Prompt patterns, system-prompt architecture, structured outputs, context management, optimization, evaluation frameworks | `prompt-forge` Sections 1+3 + `skills/prompt-forge/references/*.md` (6 files carried) |
| `prompt-factory/SKILL.md` | Mandatory 5–7 question intake; prompt-only output; format routing (XML/Claude/ChatGPT/Gemini); Core vs Advanced modes; seven quality gates | `prompt-forge` Section 1 (intake + quality gates) |
| `create-meta-prompts/SKILL.md` | `.prompts/` pipeline layout; Do/Plan/Research/Refine purpose routing; dependency-aware execution; SUMMARY.md contract | `prompt-forge` Section 4 (PIPELINE) |
| Prompt rating need (from task: "prompt rating ones") | 7-dimension /100 rubric with test cases and before/after re-measurement | `prompt-forge` Section 2 (RATE), backed by `../skills/prompt-forge/references/evaluation-frameworks.md` |

### Validation-plan family → `validation-plan`, `plan-hardening`

| Source skill | Content incorporated | Destination |
|---|---|---|
| `create-validation-plan/SKILL.md` | `.planning/` BRIEF→ROADMAP→phases hierarchy; PLAN/SUMMARY/VALIDATION per phase; blocking cumulative gates | `validation-plan` |
| `deepen-prompt-plan/SKILL.md` | Confidence-gap scoring (`trigger_count + risk_bonus + critical_section_bonus`); targeted research of weak sections; preserve original intent | `plan-hardening` Stages 3–5 |
| `harden-plan/SKILL.md` | Red-team lenses, gap register, surgical remediation, gate injection, consensus validation; no finalize with open critical findings | `plan-hardening` Stages 4–7 |
| `transform-validation-prompt/SKILL.md` | Arbitrary-prompt → validation-gated-prompt conversion | `plan-hardening` Prompt Transformation Mode |

### Visual inspection family → `visual-inspection`, `ui-experience-audit`

| Source skill | Content incorporated | Destination |
|---|---|---|
| `visual-inspection/SKILL.md` + `references/` | Universal 7-section checklist; platform routing; severity table; defect-pattern database | `visual-inspection` + shared `references/` |
| `visual-inspection.zip` (packaged artifact) | Verified as a duplicate of the extracted `visual-inspection/` directory; used the directory copy | — (duplicate, not double-counted) |
| `ui-experience-audit/SKILL.md` + `references/` + `assets/` | 6-phase protocol (triage, visual, interactive, content, heuristics, synthesis); identify-and-delegate vs drive-interaction modes; evidence-capture conventions; verdict rules; report template; Nielsen's 10; contrast rules-of-thumb | `ui-experience-audit` (+ its 4 references + template carried) |

Checklist deduplication: the archive carried two diverging copies each of
`ios-hig-checklist.md`, `web-wcag-checklist.md`, and `defect-pattern-database.md`
(under `visual-inspection/` and `ui-experience-audit/`). The
`ui-experience-audit` copies are supersets (141 vs 57 lines for the defect
database, 163 vs 136 for WCAG) and were kept as the single canonical copies
in plugin-root `references/`; both skills reference them to prevent future
drift.

### Brainstorm ("B-range") family → `brainstorm`

| Source skill | Content incorporated | Destination |
|---|---|---|
| `brainstorm/SKILL.md` (`ck:brainstorm` v2.4.0) | Scout-first gate; exact-requirements gate; present-before-asking gate; problem-first inversion; scope decomposition; YAGNI/KISS/DRY; brutal honesty; anti-rationalization table; report structure; plan handoff | `brainstorm` |

Adaptations: `ck:` prefixes removed; claudekit-specific tools
(`AskUserQuestion`, `ck:scout`, `/ck:plan`, TaskCreate) generalized to
plain agent interactions and this plugin's own skills; AgentWiki/`--html`/
`--wiki` publishing dropped (external service dependency); journal and
project-organization hooks dropped (claudekit ecosystem only). Core review
criteria (the four HARD GATES) preserved verbatim in substance.

### Cook ("cooking") family → `cook`

| Source skill | Content incorporated | Destination |
|---|---|---|
| `cook/SKILL.md` (`ck:cook` v2.2.0) | No-code-before-plan gate; scout-first gate; exact-requirements gate; no-side-effects gate with user-decided regression options; mode matrix (interactive/fast/auto/parallel/no-test/tdd); blocking review gates; anti-rationalization | `cook` |

Adaptations: mandatory claudekit subagent roster (`code-reviewer`,
`tester`, `git-manager`, `/ck:project-management`, `/ck:journal`)
generalized — review and testing checks are kept as enforceable checklist
items rather than hard-coded external agent names, so the skill works
without the claudekit ecosystem. Added the End-User Actor Mandate as the
finalize-time verification standard.

### Skill-creator / plugin-format family → build process (not a shipped skill)

| Source skill | Use |
|---|---|
| `skill-creator/SKILL.md` + its `plugin-marketplace-overview.md` and `plugin-marketplace-schema.md` references | Drove this plugin's structure: marketplace + plugin manifests, `skills/<name>/SKILL.md` layout, kebab-case names, reserved-name check, concise pushy descriptions, references kept on-demand |
| `working-with-cc` references `plugins-reference.md`, `plugins.md`, `plugin-marketplaces.md` | Canonical plugin layout (`.claude-plugin/plugin.json`, optional commands/agents/hooks/.mcp.json) and manifest field reference |

## Cross-Cutting Addition: End-User Actor Mandate

Per explicit user directive, a shared mandate
(`../references/end-user-actor.md`) was added across ALL skills: the AI
personally drives the real system as an end user via MCP/automation tools —
clicking, tapping, typing, submitting — instead of passive "2D" verification
(screenshots without interaction, code reading, existence checks). Static
inspection remains valid for visual QA, but any behavioral claim requires
driven interaction when a tool path exists, and verdicts are capped
otherwise. This strengthens the sources' "identify-and-delegate" default to
"drive whenever tools exist."

## Exclusions

| Source | Decision | Reason |
|---|---|---|
| `spec-miner` | EXCLUDED | Dangling symlink; target content absent from the archive. Cannot incorporate what cannot be read. |
| 6 absolute symlinks (`zen-office-*`, `zen-discovery`, `.venv/bin/python3.11`) | EXCLUDED | Unsafe: point outside the archive root; skipped at extraction. |
| `show-off/scripts/node_modules` and similar dependency trees | EXCLUDED | Vendored third-party dependencies, not skill content. |
| `._*` AppleDouble files, `.DS_Store` | EXCLUDED | macOS metadata noise. |
| AgentWiki publishing, claudekit journaling/project-management hooks | EXCLUDED | External service/ecosystem dependencies that would violate the no-unsupported-dependencies requirement. |

## Design Principles Applied

1. **Synthesis over concatenation** — 20+ source skills became 10 coherent
   plugin skills; shared rules were extracted into 4 canonical references
   (evidence-contract, end-user-actor, platform-routing, severity-model)
   instead of being duplicated per skill.
2. **Ecosystem independence** — all claudekit/MCP-service hard dependencies
   removed; every skill degrades to explicit BLOCKED/delegate verdicts
   rather than failing obscurely.
3. **No placeholders, no mocks** — every shipped file is complete; the one
   bundled script is fully implemented and functionally tested.

---

# Second Source Set — skills-ref.zip

A second archive was supplied after the initial consolidation and processed
as a full new source set: inventory, capability-matrix diff against the
first archive, and consolidation decisions for everything new.

## Archive Inventory Summary (skills-ref.zip)

- Archive: `skills-ref.zip` (a real ZIP this time, confirmed via magic bytes)
- SHA-256: `fe1209f9bdf10fc2249552dbcd8b4b48b9f59a69aeef9fe0db7d60bc5e009d7d`
- Compressed size: 26,223,521 bytes
- 549 top-level entries under the extracted `.claude/skills/` root:
  533 directories (334 with `SKILL.md`), 16 plain files
- Machine-readable inventory: `ref-skill-inventory.json` / `.csv`
  (delivered alongside this document)
- Lineage: same collection as the first archive — every `references/` file
  present in both archives is byte-identical. The deltas live in `SKILL.md`
  bodies and in skills that exist only in this second set.

## Capability-Matrix Additions (skills-ref.zip)

| Source skill (skills-ref.zip) | Content incorporated | Destination |
|---|---|---|
| `functional-validation/SKILL.md` + `references/{ios,web,api,cli}-validation.md` | Richer version of the skill: per-platform validation runbooks, Failure Diagnosis Table, Multi-Platform Order (Database → Backend API → Frontend/CLI/Mobile), Evidence Quality Standards, Mock Detection Red Flags, NEVER list | `../skills/functional-validation/SKILL.md` (Step 1 runbook-loading table + new sections) + 4 runbooks carried verbatim into `../skills/functional-validation/references/` |
| `preflight/SKILL.md` | Environment/toolchain preflight pass: project-type detection, universal checks, per-platform checks, summarize step | `../references/preflight-checks.md` (NEW shared reference; SessionForge-specific tooling removed); linked from `end-user-testing` Step 3 and `platform-routing.md` |
| `build-quality-gates/SKILL.md` | P0/P1/P2 CI gate classification, rollout order, baseline-first adoption | `../references/ci-gates.md` (NEW shared reference); linked from `end-user-testing` Related Skills |
| `e2e-validate/templates/verdict.md` | Full copy-ready verdict document | `../skills/end-user-testing/assets/verdict-template.md` (NEW asset), adapted with Driven-by / Actions-executed fields and the UNVERIFIED status rule |
| `full-functional-audit/SKILL.md` (ref version) | Per-platform team structure: iOS / Web-Full / API-only worker templates with EXCLUSIVE/PARALLEL resource mutex annotations; "workers provide evidence LOCATIONS, the lead examines CONTENT" | `../skills/full-functional-audit/SKILL.md` Phase 2 |
| `prompt-enhancer/SKILL.md` + `optimize-prompt/SKILL.md` | Input-type handling table (voice transcript / file path / partial idea / single word / multi-part); capability-inventory injection (`<skills_to_activate>`, `<mcp_tools>`); model-specific tone guidance | `../skills/prompt-forge/SKILL.md` Section 1 (AUTHOR) |
| `code-task-generator/SKILL.md` | `.code-task.md` standalone task-file format — the ONLY "task generator" present in either archive | `../skills/validation-plan/references/task-file-format.md` (NEW), with the End-User Actor policy applied: acceptance criteria are executable end-user actions with an explicit "When is a driven action" clause; anti-pattern "marking criteria done without executing them = validation theater; unexecuted = UNVERIFIED". Linked from `validation-plan` Step 3. |

## Exclusions (skills-ref.zip)

| Source | Decision | Reason |
|---|---|---|
| `testing-anti-patterns`, `tdd-workflow`, `testing-strategy` | EXCLUDED | Their core loop is TDD-with-mocks (mock-first test doubles as the default), which directly contradicts this plugin's Iron Rule (fix the real system; never mocks/stubs/test doubles). Incorporating them would create an internal policy conflict. |
| `website-bug-hunt` | EXCLUDED | Duplicates capabilities already covered by the user's own `bug-hunnter` skill and this plugin's `full-functional-audit`; adding it would create a third overlapping audit path. |
| `worktree-merge-validate` | EXCLUDED | Hard dependency on the Auto-Claude worktree runner ecosystem; would violate ecosystem independence. |
| `ak-brainstorm`, `ak-cook` | EXCLUDED | Empty stubs (0 files) — nothing to incorporate. |
| Dated duplicate skill copies, `._*` AppleDouble files, `.DS_Store` | EXCLUDED | Older duplicates of already-consolidated skills and macOS metadata noise. |

## Cross-Source Verification

- Every incorporated delta was diffed against the plugin's existing content
  before merging; where both archives carried the same skill, the richer
  `SKILL.md` won and shared `references/` were confirmed byte-identical
  (no drift between the two source sets).
- The policy applied to `code-task-generator` is the same End-User Actor
  Mandate enforced across the whole plugin (see the Cross-Cutting Addition
  section above) — acceptance criteria must be driven actions, and
  unexecuted validation is UNVERIFIED, never PASS.

# Third Source Pass — Mission-Fit Expansion (v1.1.0, 2026-08-09)

## Trigger

Post-delivery review found the original scan classified only ~38 of the
archive's 445 skills into target categories; the remaining 407 were bucketed
as "other" without a usefulness determination. The expansion re-scanned the
FULL universe — 445 archive skills + 334 skills-ref skills = 664 unique after
dedup (111 present in both) — and classified every skill by usefulness domain
(validation-qa-testing 101, evidence-planning 121, prompt-llm-agents 151,
marketing-seo-content 62, web-frontend-design 60, data-analytics 39,
devops-git-ci 23, mobile-ios-android 22, accessibility 5, security 3, ...).

## Source availability

- `skills.zip` (original 445): URL now returns **403 Forbidden** — sources only
  available from the earlier inventory; cannot re-read, cannot incorporate.
- `skills-ref.zip`: re-downloaded and SHA-256 verified identical to the first
  pass (`fe1209f9bdf1...`). 334 readable skills on disk. All incorporations
  below come from this set.

## Incorporated (26 sources → 5 new skills)

| New skill | Sources incorporated |
|---|---|
| `stack-testing` | `python-testing`, `golang-testing`, `cpp-testing`, `django-tdd`, `springboot-tdd`, `python-fastapi-backend-testing`, `webapp-testing` (+ `with_server.py`, 3 examples), `playwright-skill` (+ runner/helpers/API ref), `condition-based-waiting` (+ example) |
| `mobile-validation-runner` | `ios-validation-runner` (+ validate.sh), `ios-validation-gate`, `ios-simulator-control` (+ reference.md, 3 scripts), `xc-mcp` (+ 8 workflows, 6 references), `complete-expo-ios-testing-workflow`, `expo-ios-complete-testing-workflow`, `preflight` |
| `root-cause-debugging` | `diagnose` (+ hitl-loop template), `root-cause-tracing` (+ find-polluter.sh), `debug-like-expert` (+ 5 references), `trace` |
| `production-readiness` | `production-readiness-audit`, `spec-compliance`, `dependency-health` |
| `red-team-eval` | `red-team` (+ evals assets), `eval-harness`, `ultraqa`, `eval` |

Incorporation method: source bodies preserved as per-skill `references/`
(frontmatter stripped; archive-internal `Conflicts`/`Related Skills` sections
removed; internal paths re-pointed to the new bundle layout), with an authored
SKILL.md per skill that enforces the Iron Rule, the End-User Actor Mandate,
and fresh-evidence discipline, and routes to the right reference.

## Exclusions (with reasons)

| Source(s) | Reason |
|---|---|
| `accessibility-compliance-accessibility-audit`, `accesslint-audit/scan/diff`, `android_ui_verification`, `android-ui-journey-testing`, `mcp-audit`, `agenttrace-session-audit`, `advanced-evaluation`, `agent-evaluation`, `edge-case-analyzer` | Only in the 403-inaccessible skills.zip; cannot incorporate what cannot be read. Mobile skill explicitly flags the Android gap rather than improvising it. |
| `python-fastapi-claude-backend-testing` | Dated duplicate of `python-fastapi-backend-testing` (same claude-code-api subject). |
| `SKILL 2026-*.md` dated copies inside `ios-validation-gate`, `production-readiness-audit`, `playwright-skill` | Older duplicates. |
| `release` | Hardwired to the oh-my-claudecode repo ecosystem. |
| `ck-debug`, `fix`, `ak-debug`, `ship` | Empty stubs (no SKILL.md, empty references/). |
| `testing-anti-patterns`, `tdd-workflow`, `testing-strategy` | Still excluded (mock-first doctrine conflicts with the Iron Rule). `cpp-testing`/`springboot-tdd`/`django-tdd` were incorporated WITH adaptation notes: mock-framework chapters are for reading existing suites; new tests hit the real system (Testcontainers pattern endorsed). |
| `playwright-skill/.validation/` PNGs, `.temp-execution-*.js`, `.DS_Store`, `package-lock.json` | Stale evidence, temp files, OS noise, regenerable lockfile. |

# Fourth Source Pass — Session-First Reorientation (v1.2.0, 2026-08-09)

## Trigger

User correction after v1.1.0: the goal was never only the static skill
archive — the plugin must look at **the sessions themselves**, because the
transcripts are where the intent behind each prompt lives. This matches the
companion 30-day audit task's doctrine ("intent reconstruction → code truth →
frame evidence"; session summaries are claims about a tree that has since
moved; every commit row cites a session intent source or "intent
unrecoverable").

## Incorporated (1 source + 1 new capability)

- `claude-code-analyzer` → bundled as `session-intent/references/` (usage
  analytics lane; its jq-based JSONL extraction mechanics informed the new
  parser). Its 4 scripts preserved under `references/scripts/`.
- NEW `session-intent` skill: `scripts/session_intent.py` (Python stdlib)
  parses `~/.claude/projects/**/*.jsonl` into a per-session intent matrix —
  first user prompt (stated intent), steering prompts, tool counts, files
  touched, observed `git commit` invocations, branch, models, time bounds.
  SKILL.md codifies: transcripts = evidence, summaries = claims; null intent
  stays null; commit alignment by window+branch+file overlap with per-row
  disclosure; INTENT-MATCHED / INTENT-PARTIAL / INTENT-UNRECOVERABLE verdicts.

## Considered, not incorporated (with reasons)

| Source | Reason |
|---|---|
| `mem-search` | Requires the claude-mem external memory ecosystem; unsupported dependency. Its cross-session search need is served by the parser + grep over extracted JSON. |
| `optimize-prompt` | Prospective prompt crafting (raw input → good prompt), not retrospective intent reconstruction. |
| `learner` | Extracts a reusable skill from a conversation — different question than "what was the user trying to get done". |
| `agenttrace-session-audit`, `evaluate-session.sh` | Only in the 403-inaccessible skills.zip. |

## Validation

Parser verified end-to-end against a constructed fixture in the real Claude
Code JSONL shape (2 sessions: tool-result events correctly excluded from
prompts; intent, steering, commit, and file extraction all asserted). The
fixture is constructed format-conformance data, NOT a captured session — the
parser has not yet run against the live transcript corpus on the user's
machine, and the skill says to treat that first live run as the real gate.

## prompt-forge rework (v1.4.0, 2026-08-11)

Decision: rebuilt `prompt-forge` around an always-on workflow (Section 0)
rather than patching each mode separately — the directive (immediate
file-applied remediation, sequential thinking, XML tags, authorization,
todos) binds all four modes identically, so a single binding section plus
per-mode hooks avoids four divergent copies of the same rules. The XML tag
standard extends the tag set already proven in the mood-ring demo prompt
(`task/context/constraints/output_contract/validation/example` +
`skills_to_activate/mcp_tools`) with `sequential_thinking`, `todos`, and
`authorization`. Sequential-thinking methodology was specified from
established practice because both archive copies of the source skill were
empty (see validation-results.md §15) — no unreadable source was
paraphrased.

## implement skill + prompt-forge command surface (v1.5.0, 2026-08-11)

Decision: layered architecture rather than merging — `implement` is the
orchestrator (mining, parallel scouts, prompt-forged planning, parallel
lanes, criteria distillation, auto loop) and `cook` stays the execution
engine it delegates code phases to. Both have auto/parallel vocabulary;
the division of labor (conductor vs player) is stated in both skills so
routing is unambiguous. prompt-forge's flags were placed in a Command
Surface section rather than inline per mode, because every flag is an
authorization-engine consent and 0.3 is the single table they map to.
The remediation sample was written as a reference file (not inline) to
keep SKILL.md within size discipline while still showing a real
before/after with actual scores.

## codebase-truth-audit integration (v1.6.0, 2026-08-11)

Decision: ship the skill inside the plugin rather than rewrite
session-intent's edge around its absence — the user's standing rule is
that the Related Skills graph must be closed (every referenced skill
present), and the intent → code-truth → evidence → deviation pipeline is
a real two-lane design, not a mention. The skill was already consolidated
and validated in earlier work, so integration was a copy plus a new
Related Skills section in both directions, plus a live end-to-end run of
its workspace script as the incorporation gate. Usage documentation went
into a dedicated docs/usage-guide.md rather than inflating the README
further: the README's command reference is the flag/permutation truth,
the usage guide is the hands-on `/skill-name` path.
