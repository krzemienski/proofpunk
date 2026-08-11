# truth-forge

An execution-first delivery **plugin for Claude Code, oh-my-pi (OMP), and OpenCode**:
18 skills that make "done" mean *proven by end-user testing*. The AI drives the real system as an end user — clicking,
typing, submitting via MCP/automation tools — and any claim it did not actually execute
is reported **UNVERIFIED**, never PASS. No mocks, no stubs, no test-mode bypasses.

## Install

**Claude Code** (plugin — skills, commands, SessionStart doctrine hook):

```
/plugin marketplace add krzemienski/truth-forge
/plugin install truth-forge@truth-forge-marketplace
```

**oh-my-pi / OMP** (plugin — skills, commands, doctrine-guard extension; catalog at
`.omp-plugin/marketplace.json`, Claude-compatible `.claude-plugin/` fallback):

```
omp plugin marketplace add krzemienski/truth-forge
omp plugin install truth-forge@truth-forge
```

**OpenCode** — the installer drops the plugin, commands, agent, and skills into
`~/.config/opencode/`, or use the full plugin via the same catalog above.
**Any agent** — plain skills into any directory:

```
bash tools/truth-forge-install.sh --target claude-code            # ~/.claude/skills (also read by OpenCode + OMP)
bash tools/truth-forge-install.sh --target omp --themes --plugins # oh-my-pi skills + themes + extension
bash tools/truth-forge-install.sh --target opencode --themes --plugins
bash tools/truth-forge-install.sh --target agents                 # ~/.agents/skills (shared)
```

Or download `truth-forge-marketplace.tar.gz` from this repo's release artifacts and
extract it into your marketplaces directory.

## Themes — 20 flat-black cyberpunk variations

`plugins/truth-forge/themes/` ships 20 themes (neon-tokyo, acid-rain, vapor-grid,
code-fall, static-noir, …) inspired by the Hyper terminal's theme contract: pure
`#000000` canvas, two-neon accent systems, tuned status colors. One canonical
palette source (`themes/palettes.json`) renders to three formats via
`tools/generate-themes.py`:

| Format | Files | Install target |
|--------|-------|----------------|
| OMP theme JSON | `themes/omp/*.json` | `~/.omp/agent/themes/` |
| OpenCode theme JSON | `themes/opencode/*.json` | `~/.config/opencode/themes/` |
| Hyper module | `themes/hyper/*.js` | merge into `~/.hyper.js` (decorateConfig contract) |

`truth-forge-install.sh --themes` copies them into every detected platform.
Claude Code has no custom-palette API, so the Claude plugin ships the themes
for the other surfaces you run beside it.

## The skills

| Skill | What it enforces |
|-------|------------------|
| `brainstorm` | Scout-first, exact-requirements, present-before-asking discipline; no code before an approved design |
| `prompt-forge` | Prompt AUTHOR / RATE (7-dimension /100 rubric) / OPTIMIZE / PIPELINE modes with a scored quality bar |
| `validation-plan` | BRIEF → ROADMAP → per-phase PLAN/SUMMARY/VALIDATION with blocking **cumulative** proof obligations |
| `plan-hardening` | Confidence-gap scoring, 4 red-team lenses, dispositioned gap register, proof-obligation injection |
| `cook` | Task-by-task execution of validation plans; every task completes only with end-user proof (the engine `implement` delegates to) |
| `implement` | Orchestrated front door composing ALL skills: session mining (`--mine`), parallel scout agents, prompt-forged plans, parallel lanes (`--parallel`), no-stop mode with distilled success criteria, stuck protocol, live execution ledger (`--auto`) |
| `functional-validation` | Drive the real system end-to-end per platform (web/iOS/API/CLI runbooks) |
| `end-user-testing` | Run-scoped fresh evidence (`fresh_evidence.py`: init-run/next-step/seal/validate), verdict templates |
| `visual-inspection` | Screenshot-driven visual QA with severity model (found a real HIGH defect in the demo) |
| `ui-experience-audit` | 6-phase UX protocol: triage, visual, interactive, content, Nielsen heuristics, synthesis |
| `full-functional-audit` | App-wide interaction inventory → execute → remediate → verdict |
| `stack-testing` | Per-stack real-system test discipline: pytest/Go/C++/Django/Spring gotchas, FastAPI SSE testing, Playwright e2e, condition-based waiting (no sleeps, no new mocks) |
| `mobile-validation-runner` | iOS end-user validation: SETUP→RECORD→ACT→COLLECT→VERIFY, three-facet checks, simctl/XC-MCP/Expo lanes, preflight checks |
| `root-cause-debugging` | Reproduce-first diagnosis, backward call-chain tracing, pollution bisection; symptomatic hacks forbidden |
| `production-readiness` | 8-phase ship-readiness audit + spec-compliance matrix (COVERED/INCOMPLETE/MISSING) + dependency supply-chain health |
| `red-team-eval` | 4-lens hostile review of plans/prompts/artifacts, eval-driven development, QA cycling until measured goal attainment |
| `session-intent` | Reconstruct what was actually ASKED from Claude Code transcripts themselves: per-session intent matrix, session-to-commit alignment, intent-vs-implementation verdicts |
| `codebase-truth-audit` | Evidence-backed repo-wide truth audits: intent-from-history, code/config/doc/runtime verification, approval-gated remediation (the code-truth lane to session-intent's intent lane) |

`prompt-forge` gained its always-on workflow + command surface in v1.4.0/v1.5.0, `implement` arrived in v1.5.0, and `codebase-truth-audit` in v1.6.0 — closing the last dangling Related Skills edge (session-intent's intent → code-truth pipeline). **v1.7.0**: the doctrine moved from gate-logic to execution-logic — tasks carry proof obligations, validation is end-user testing always, `evidence-gates` became `end-user-testing` — plus the 20-theme flat-black cyberpunk pack and OMP/OpenCode platform support.

**Hands-on invocation examples for every skill (`/skill-name <positional> --flag`): `plugins/truth-forge/docs/usage-guide.md`.**
Five were added in v1.1.0 and `session-intent` in v1.2.0 from a second full-universe scan (664 unique skills
across both source archives, classified by usefulness domain) — see
`plugins/truth-forge/docs/consolidation-decisions.md`.

Shared doctrine lives in `plugins/truth-forge/references/` — the Iron Rule (fix the real
system), the End-User Actor Mandate, the evidence contract, severity model, platform
routing, preflight checks, and CI gate classification.


## Command reference — every argument, every permutation, what executes

Conventions: `<angle>` = required positional argument, `[bracket]` = optional,
`A | B` = alternatives, `--flag=value` takes a value. **Skills executed** names
the skills that fire beyond the one invoked, in firing order, taken from each
skill's own Related Skills / delegation contract.

### Dispatch at a glance

| You run | Skill that fires | Then delegates to |
|---------|------------------|-------------------|
| `implement "<goal>" [flags]` | `implement` | session-intent, prompt-forge, validation-plan, plan-hardening, cook, root-cause-debugging, functional-validation, end-user-testing, stack-testing |
| `implement mine [filters]` | `implement` (Phase 1 only) | session-intent |
| `prompt-forge author\|rate\|optimize\|pipeline ...` | `prompt-forge` | none (leaf); pipeline stages later execute under cook |
| `cook <goal\|plan-path> [mode] [--tdd]` | `cook` | brainstorm, validation-plan, functional-validation, end-user-testing |
| `functional-validation --analyze\|--plan\|--execute\|--fix\|--audit\|--report` | `functional-validation` | end-user-testing, full-functional-audit, visual-inspection, ui-experience-audit, validation-plan |
| `session_intent.py [filters] [outputs]` | `session-intent` | none (leaf tool) |
| `fresh_evidence.py init-run\|next-step\|seal\|validate` | `end-user-testing` | none (leaf tool) |
| `with_server.py --server ... --port ... -- <check>` | `stack-testing` | none (leaf tool) |
| `truth-forge-install.sh [flags]` | installer (tools/, not a skill) | installs all 17 skills + doctrine |

---

### 1. `implement` — orchestrated implementation

```
implement <goal> [--parallel] [--auto] [--mine] [--fast] [--no-test] [--tdd]
implement mine [--project DIR] [--since DATE] [--until DATE]
```

**Positional arguments**

| Argument | Why it exists | What happens |
|----------|---------------|--------------|
| `<goal>` | the implementation target, in natural language | fed to Phase 0 and distilled into TRUE success criteria (observable, end-user provable, measurable); unclear goals stop here for your approval |
| `mine` (subcommand) | reconnaissance-only mode | runs session mining and prints the previous-implementations matrix; zero code touched |

**Flags**

| Flag | Why it exists | What happens |
|------|---------------|--------------|
| `--parallel` | multi-module goals where wall-clock matters | parallel scout agents (structure/patterns/contracts/history), plan authored as a `.prompts/` pipeline with parallel independent stages, execution split into parallel lanes by module boundary |
| `--auto` | unattended runs with a real finish line | no stopping until every success criterion is proven as the end user; the ONLY mandatory stop is Phase 0 approval when criteria aren't clearly laid out; destructive ops, out-of-scope edits, below-threshold shipping still stop for consent |
| `--mine` | you've implemented similar things before | Phase 1 runs session-intent: past sessions become an intent matrix (prompts, tools, files, commits) that feeds exploration and forging |
| `--fast` | known territory, known stack | planning's research sub-step skipped (cook fast-mode semantics) |
| `--no-test` | no runnable suite in this environment | the regression rail downgrades to a warning you must explicitly accept; end-user testing is never downgraded |
| `--tdd` | refactor-heavy goals | tests for current behavior written before the change, re-verified after |
| `--project DIR` (mine) | scope mining to one project | substring filter on project dir slug / cwd |
| `--since DATE` / `--until DATE` (mine) | time-box the mining | transcript events outside the window are excluded |

**Permutations — what each combination does and what you end up with**

| Invocation | Why you'd use it | What happens, end to end | Skills executed | You end up with |
|------------|------------------|--------------------------|-----------------|-----------------|
| `implement "add billing webhooks"` | standard supervised run | Phase 0 criteria (approval if unclear) → explore → forge prompt → plan → execute the task loop (prove each task as you go) → report from the ledger | prompt-forge → validation-plan → plan-hardening → cook → functional-validation → end-user-testing → stack-testing | implementation + criteria-by-criteria proof table + todo ledger |
| `... --mine` | reuse past approaches | Phase 1 mines sessions first; the intent matrix steers scouts (past touchpoints) and the forged prompt (framings that worked) | session-intent → *(as above)* | + previous-implementations matrix |
| `... --parallel` | multi-module, speed matters | 4 parallel scouts; prompt-forge PIPELINE authors `.prompts/` with parallel stages; cook executes lanes concurrently; contract checks serialize lane merges | *(scouts in parallel)* → prompt-forge (PIPELINE) → cook (lanes) → functional-validation → end-user-testing | + `.prompts/` tree with PROMPT.md + SUMMARY.md per stage |
| `... --auto` | run unattended | criteria confirmation (if the goal is unclear) is the ONLY mandatory stop; the loop executes → end-user tests → stuck protocol until every criterion is proven; UNVERIFIED = NOT DONE | + root-cause-debugging on every failure | proof table with PASS per criterion, or an explicit blocker statement naming the consent needed |
| `... --parallel --auto` | unattended multi-module | both behaviors combined; the stuck protocol handles failures automatically — only human-decision escalations (destructive ops, out-of-scope edits, unclear criteria) stop the run | *(both chains above)* | full pipeline artifacts + ledger-rendered proof table; the only stops are criteria confirmation and consent escalations |
| `... --auto --mine` | unattended, informed by history | mining feeds the criteria distillation itself (past intent sharpens what "done" means) | session-intent → full auto chain | + intent matrix cited in the final report |
| `... --parallel --mine` | supervised but fast and informed | parallel scouts ALSO receive the mined touchpoint list as their History lane assignment | session-intent → parallel scouts → parallel pipeline → supervised cook | combined artifacts, human checkpoints intact |
| `... --parallel --auto --mine` | "full send" | every stage maximally delegated; the run stops only for criteria confirmation (if needed) and authorization-boundary consents | session-intent → parallel scouts → prompt-forge PIPELINE → parallel cook lanes → root-cause-debugging loop → proof layer | everything above; the complete trail from mined intent to sealed evidence |
| any of the above `+ --fast` | you know the codebase cold | research sub-step skipped everywhere planning happens | same chains, research elided | same artifacts, faster planning |
| any of the above `+ --no-test` | environment can't run suites | the regression rail becomes a warning requiring your explicit acceptance; end-user testing still mandatory | same chains | report carries the accepted warning verbatim |
| any of the above `+ --tdd` | refactoring existing behavior | characterization tests written first per phase, re-verified after | same chains | + characterization test suite |
| `implement mine` | "show me how we built things" | mining only, prints the matrix to stdout, exits | session-intent | previous-implementations matrix |
| `implement mine --project shop --since 2026-07-01` | scoped recon | AND-composed filters: only July+ sessions in the shop project | session-intent | filtered matrix |

**Conflicts**: no two flags conflict. Unknown flags are rejected with the flag
table. `--auto` never overrides the authorization boundaries.

---

### 2. `prompt-forge` — author / rate / optimize / pipeline

```
prompt-forge author "<goal>" [--out PATH] [--depth core|advanced]
prompt-forge rate NAME.md [--in-place] [--report-only] [--ship-below-threshold] [--out PATH]
prompt-forge optimize NAME.md --evidence FILE [--in-place] [--out PATH]
prompt-forge pipeline "<goal>" [--dir PATH]
```

**Positional arguments**

| Argument | Why it exists | What happens |
|----------|---------------|--------------|
| `"<goal>"` (author, pipeline) | the prompt's purpose in natural language | drives the 5-7 intake questions, then authoring on the canonical XML skeleton |
| `NAME.md` (rate, optimize) | the prompt file under review | the rating's subject AND the default base name for output files (`NAME.rating.md`, `NAME.remediated.md`, `NAME.optimized.md`) |

**Flags** — each one IS a recorded authorization-engine consent:

| Flag | Modes | Why it exists | What happens |
|------|-------|---------------|--------------|
| `--out PATH` | all | you control where artifacts land | deliverable written to PATH instead of the default name |
| `--depth core\|advanced` | author | intake question 4 as a flag | core = instruction set only; advanced = few-shot set, edge cases, fallbacks |
| `--in-place` | rate, optimize | consent to edit your input file | the input file itself is replaced; no `.remediated`/`.optimized` copy |
| `--report-only` | rate | consent to skip file output | scorecard only; without this flag a rating with no remediated file violates the file-output contract |
| `--ship-below-threshold` | rate, optimize | sign-off for below-threshold shipping | a `needs-work`/`rewrite` result may be finalized; without it the report states what's still missing |
| `--evidence FILE` | optimize | OPTIMIZE's hard requirement, machine-checkable | real captured failure output drives the fix classification; WITHOUT this flag optimize does not run — it asks for a real bad output first |
| `--dir PATH` | pipeline | multi-pipeline repos | pipeline rooted at PATH (default `.prompts/<slug>`) |

**Permutations**

| Invocation | What happens | You end up with |
|------------|--------------|-----------------|
| `rate prompts/login.md` | rubric scoring against 3-5 built test cases → top fixes APPLIED → remediated version re-scored | `login.rating.md` + `login.remediated.md` + before/after scores |
| `rate prompts/login.md --in-place` | same, but `login.md` itself is replaced by the remediated version | `login.rating.md` + edited `login.md` |
| `rate prompts/login.md --report-only` | scorecard and predicted failure modes only | `login.rating.md` |
| `rate prompts/login.md --ship-below-threshold` | if the re-score still lands at needs-work, it ships anyway — with your sign-off recorded | files + recorded sign-off in the report |
| `rate prompts/login.md --out review.md` | artifacts at your path | `review.md` (+ `login.remediated.md`) |
| `optimize prompts/login.md --evidence bad-output.txt` | failures classified (ambiguity / missing context / format drift / reasoning gap / overflow) → targeted fixes → same test cases re-run | `login.optimized.md` + before/after scores |
| `optimize prompts/login.md` (no --evidence) | **does not run** — demands a real captured bad output first | nothing; a question back to you |
| `author "a SQL review prompt" --depth advanced` | intake → authored prompt with few-shot set, edge cases, fallbacks | `a-sql-review-prompt.prompt.md` |
| `pipeline "onboarding revamp" --dir .prompts/onboarding` | dependency-aware Research/Plan/Do stages authored | `.prompts/onboarding/NN-stage/PROMPT.md` tree |

**Conflicts (rejected, fail fast)**: `--in-place` + `--out` (two
destinations), `--report-only` + `--out` (nothing to write), `--report-only`
+ `--in-place` (no output vs edit). Unknown flags rejected with the table.

A complete worked rating — weak prompt, 34/100 scorecard, remediated file,
91/100 re-score — lives in `plugins/truth-forge/skills/prompt-forge/references/remediation-sample.md`.

Skills executed: none downstream (leaf). It is executed BY `implement`
(Phases 3-4) and pairs with `plan-hardening` / `validation-plan`.

---

### 3. `cook` — the execution engine

```
cook <goal> [mode] [--tdd]
cook <plan-path> [mode] [--tdd]
```

**Positional arguments**

| Argument | Why it exists | What happens |
|----------|---------------|--------------|
| `<goal>` | a feature/fix in natural language | full pipeline: scout the codebase → exact requirements → research → decompose into proof-carrying tasks → implement → end-user test each task → finalize |
| `<plan-path>` | a pre-written plan file | the scout step is skipped — the plan encodes scout output; execution follows the plan's task list |

**Modes** (pick one; interactive is the default)

| Mode | Research | Checkpoints | Progression | Why you'd use it |
|------|----------|--------------|-------------|------------------|
| `interactive` (default) | yes | human confirmation at each checkpoint | one step at a time | supervised work, unfamiliar territory |
| `fast` | no | human confirmation at each checkpoint | one step at a time | known stack, known patterns |
| `auto` | yes | auto-approve LOW-risk only; high-risk stops | continuous on low-risk | unattended on well-bounded changes |
| `parallel` | optional | human confirmation at each checkpoint | batched groups | independent phases executed in batches |
| `no-test` | yes | human confirmation at each checkpoint | one step at a time | no runnable suite; the rail becomes a warning you must accept |

**Permutations — mode × `--tdd`**

| Invocation | What happens | You end up with |
|------------|--------------|-----------------|
| `cook "add avatar upload"` | full supervised pipeline, 4 human checkpoints | feature + test pass + end-user evidence |
| `cook "add avatar upload" --tdd` | characterization tests before each phase's change, re-verified after | + safety net for every touched behavior |
| `cook "add avatar upload" fast` | research skipped; checkpoints unchanged | same, faster ramp-up |
| `cook "add avatar upload" fast --tdd` | known territory + tests-first | same artifacts, fastest supervised path |
| `cook "add avatar upload" auto` | low-risk steps auto-approved; any high-risk step (contract change, deletion, migration) stops for you | continuous progress with named stops |
| `cook "add avatar upload" auto --tdd` | unattended + tests-first; high-risk stops still apply | same, with regression net |
| `cook "add avatar upload" parallel` | independent tasks batched concurrently, proof per batch | batched-phase execution log |
| `cook "add avatar upload" parallel --tdd` | batches with tests-first inside each phase | same + net |
| `cook "add avatar upload" no-test` | 100%-pass requirement downgraded to a warning you must explicitly accept; acceptance criteria, regression walk, contract checks still enforced | report carrying the accepted warning |
| `cook "add avatar upload" no-test --tdd` | warning mode, but characterization tests still written (they just aren't the proof) | tests exist; the rail is advisory |
| `cook .planning/ROADMAP.md` | plan file loaded; scout skipped; proof obligations per plan phase | plan executed end to end |
| `cook .planning/ROADMAP.md --tdd` | plan-driven + tests-first | same + net |

Skills executed: `brainstorm` (when the approach is undecided upstream),
`validation-plan` (authors the plans cook executes), `functional-validation`
+ `end-user-testing` (Gate 4 end-user proof). It is executed BY `implement`
Phase 5.

---

### 4. `functional-validation` — end-user proof protocol

```
functional-validation [--analyze] [--plan] [--execute] [--fix] [--audit] [--report]
                      [--platform web|ios|api|cli] [--ci]
```

No positional arguments. Flags compose into the default flow
**analyze → plan → execute → (fix) → report**.

| Flag | Why it exists | What happens |
|------|---------------|--------------|
| `--analyze` | criteria before execution (confirmation-bias guard) | inventory features + interfaces, define PASS criteria; NO execution |
| `--plan` | ordered, proof-carrying validation | ordered validation plan with proof obligations per feature |
| `--execute` | the actual driving | run the plan against the real system, capture evidence |
| `--fix` | remediation inside the loop | fix FAILs against the real system, then re-validate |
| `--audit` | one feature isn't enough | full pass over EVERY feature (delegates to `full-functional-audit`) |
| `--report` | one verdict document | synthesize all verdicts into a single report |
| `--platform <p>` | detection got it wrong | force the platform runbook |
| `--ci` | automation needs exit codes | machine-readable output, non-zero exit on FAIL |

**Permutations**

| Invocation | What happens |
|------------|--------------|
| `functional-validation` (no flags) | full default flow: analyze → plan → execute → fix (if FAILs) → report |
| `--analyze` alone | feature inventory + PASS criteria only; nothing executed |
| `--analyze --plan` | criteria + proof-carrying plan, still zero execution |
| `--execute` alone | run an existing plan; refuses if no criteria exist yet |
| `--execute --fix` | execute and remediate in one loop, re-validating after each fix |
| `--audit --ci` | full-app pass with machine-readable verdicts and a failing exit code on any FAIL — the CI wiring |
| `--platform ios --execute` | force the iOS runbook (pairs with `mobile-validation-runner` lanes) |

Skills executed: `end-user-testing` (freshness + citation for every verdict),
`full-functional-audit` (on `--audit`), `visual-inspection` /
`ui-experience-audit` (reviewing captured visual evidence), `validation-plan`
(embedding checks as blocking proof obligations).

---

### 5. `session-intent` — transcript mining

```
python3 scripts/session_intent.py [--projects-dir DIR] [--project SUBSTR]
                                  [--since YYYY-MM-DD] [--until YYYY-MM-DD]
                                  [--json out.json] [--md out.md]
```

No positional arguments. Exit code 2 when no transcripts match (never a
silent empty success).

| Argument | Default | Why it exists | What happens |
|----------|---------|---------------|--------------|
| `--projects-dir DIR` | `~/.claude/projects` | non-standard transcript locations | scans DIR for `*.jsonl` transcripts |
| `--project SUBSTR` | all projects | scope to one codebase | substring filter on project dir slug / cwd |
| `--since` / `--until` | unbounded | time-box the reconstruction | events outside the window excluded |
| `--json out.json` | stdout matrix | machine consumption by other tools | writes the full per-session records as JSON |
| `--md out.md` | stdout matrix | attachable evidence artifact | writes the rendered intent matrix as markdown |

**Permutations**

| Invocation | What happens |
|------------|--------------|
| no args | mine everything under `~/.claude/projects`, print the matrix |
| `--project shop --since 2026-07-01` | AND-composed filters: July+ sessions in the shop project only |
| `--json out.json --md out.md` | both artifacts written; stdout still prints the summary |
| `--since 2026-08-01 --until 2026-08-07` | one-week window across all projects |

Skills executed: none (leaf tool). Consumed BY `implement --mine` /
`implement mine`; its matrix pairs with `production-readiness`
(spec-compliance vs intent-compliance) and `root-cause-debugging`
(when INTENT-PARTIAL rows reveal unauthorized scope).

---

### 6. `end-user-testing` — the fresh-evidence lifecycle

```
python3 scripts/fresh_evidence.py init-run <slug>
python3 scripts/fresh_evidence.py next-step <slug>
python3 scripts/fresh_evidence.py seal
python3 scripts/fresh_evidence.py validate
```

**Positional argument**

| Argument | Why it exists | What happens |
|----------|---------------|--------------|
| `<slug>` | run identity — evidence is run-scoped so stale artifacts can't be reused | `init-run` creates `run-<timestamp>-<slug>/` and prints the run_id; `next-step` prints the next `step-NN` prefix inside it |

This is a lifecycle, not a combinatorial flag set — the ordered sequence is
the only valid composition: **init-run → next-step × N (each evidence
capture) → seal → validate**. Exit codes: `0` OK; `2` refusal (bad slug,
no active run, stale/empty artifacts, missing metadata) — `validate` prints
`STALE:` / `EMPTY:` for every offending artifact so nothing fails silently.

Skills executed: none (leaf tool). It is executed BY cook's Gate 4,
`functional-validation`, `mobile-validation-runner`, `implement` Phase 7,
`red-team-eval`, `production-readiness` — every verdict in the plugin seals
through this lifecycle.

---

### 7. `stack-testing` — real-server test rigs

```
python3 scripts/with_server.py --server "<start-cmd>" --port N -- <check-cmd>
cd scripts/playwright && npm install && node run.js --help
```

| Argument | Why it exists | What happens |
|----------|---------------|--------------|
| `--server "<start-cmd>"` | tests need the REAL server, lifecycle-managed | starts the dev server, waits for the port (condition-based, no sleeps) |
| `--port N` | readiness is proven by the port answering | poll until accepting connections or fail loudly |
| `-- <check-cmd>` (trailing positional) | the actual check to run against the live server | runs your check (Playwright script, curl probe, pytest e2e), then tears the server down |

Skills executed: none (leaf tool). Consumed BY `cook`, `functional-validation`,
`root-cause-debugging` (turning a reproducer into a permanent regression test).

---

### 8. `tools/truth-forge-install.sh` — the installer

No positional arguments; everything is flags. Full table with
why-it-exists lives in `tools/INSTALL.md`; the flags:

| Flag | Why it exists |
|------|---------------|
| `--target claude-code\|omp` | which agent's skills dir to install into |
| `--dir PATH` | explicit skills dir (overrides --target) |
| `--source github\|local` / `--source-dir PATH` / `--ref REF` | where the skills come from: GitHub at a ref, or a local checkout |
| `--only a,b,c` | surgical subset instead of all 17 |
| `--list` | show what would be installed, then exit |
| `--override` | consent to REPLACE same-name skills (timestamped `.bak` backups) |
| `--backup` / `--no-backup` | backup control when overriding |
| `--with-doctrine` / `--no-doctrine` | include the truth-forge-doctrine bundle (Iron Rule, End-User Actor Mandate, remediation definition) |
| `--inject-claude-md FILE` | append the idempotent BEGIN/END TRUTH-FORGE RULES block to your CLAUDE.md |
| `--dry-run` | print the full plan, write nothing |
| `--verify` / `--no-verify` | post-install self-check (structure, citations, doctrine) |
| `--quiet` | summary only |

**Canonical permutations**

| Invocation | What happens |
|------------|--------------|
| `truth-forge-install.sh --target claude-code` | first-time: all 18 skills + doctrine + verify, from GitHub |
| `--target omp --themes --plugins` | 18 skills + 20 themes + doctrine-guard extension for oh-my-pi |
| `--only prompt-forge,implement --override` | surgical refresh of two skills, backups taken |
| `--source local --source-dir /path/to/repo --no-verify` | offline install from a checkout, self-check skipped |
| `--inject-claude-md ~/.claude/CLAUDE.md` | rules block appended once; re-running leaves it unchanged (idempotent) |

**Conflicts (fail fast)**: `--target` + `--dir` (two destinations);
`--dry-run` + `--override` (plan-only vs mutate); `--source github` without
network. Exit codes: 0 success, 1 environment/usage error, 2 install
failure, 3 unknown skill in `--only`.

---

### 9. Protocol skills — no flags, what fires when you invoke them

These skills take natural-language input only (no arguments); what matters
is what they execute downstream:

| You invoke | What happens | Skills executed downstream |
|------------|--------------|---------------------------|
| `brainstorm` | scout-first ideation with trade-off analysis; no code before an approved design | validation-plan (plan the design), plan-hardening (red-team it), cook (build it) |
| `validation-plan` | BRIEF → ROADMAP → per-phase PLAN/SUMMARY/VALIDATION with blocking cumulative proof obligations | plan-hardening (strengthen drafts), end-user-testing (executes the proof blocks), cook (executes phases) |
| `plan-hardening` | confidence-gap scoring, 4 red-team lenses, dispositioned gap register | validation-plan (the plans it hardens), prompt-forge (the prompts it hardens), brainstorm (upstream) |
| `visual-inspection` | screenshot QA with severity classification | ui-experience-audit (deeper pass), functional-validation (exercise after visual PASS) |
| `ui-experience-audit` | 6-phase UX protocol (triage → visual → interactive → content → heuristics → synthesis) | visual-inspection (Phase 1), functional-validation (drives flagged flows), full-functional-audit (app-wide), end-user-testing (citations) |
| `full-functional-audit` | app-wide interaction inventory → execute → remediate → verdict | functional-validation (per-interaction protocol), end-user-testing (batch verdicts), ui-experience-audit (per-screen), validation-plan (fix list → plan) |
| `mobile-validation-runner` | iOS end-user validation: SETUP→RECORD→ACT→COLLECT→VERIFY; lanes: simctl (bundled, always available), XC-MCP (a11y-first UI automation), Expo/idb (React Native) | visual-inspection (audit every screenshot), ui-experience-audit (per-screen), end-user-testing (sealing), functional-validation (web/API equivalent) |
| `root-cause-debugging` | reproduce → minimize → hypothesize → instrument; fixes the ROOT CAUSE, never the symptom | stack-testing (reproducer → regression test), functional-validation (blast-radius re-check), plan-hardening (large fixes), end-user-testing (claims) |
| `production-readiness` | 8-phase ship-readiness audit + spec-compliance matrix + dependency health | full-functional-audit (drive everything), stack-testing (close gaps), end-user-testing (seal waves), plan-hardening (remediation plan) |
| `red-team-eval` | 4-lens hostile review of plans/prompts/artifacts + measured QA cycles | plan-hardening (planning-stage lenses), prompt-forge (rubric rating), functional-validation (post-convergence PASS/FAIL), end-user-testing (seal scores) |

---

## System architecture

### 1. Repository layout

```mermaid
graph TD
    M["truth-forge-marketplace<br/>.claude-plugin/marketplace.json"]
    M --> P["plugins/truth-forge<br/>the plugin"]
    M --> T["tools/<br/>truth-forge-install.sh + INSTALL.md"]
    M --> E["examples/mood-ring<br/>the sealed live walkthrough"]
    P --> S["skills/ — 17 skills"]
    P --> R["references/ — 9 shared doctrine files"]
    P --> D["docs/ — consolidation + validation records"]
    R -.->|cited by| S
```

### 2. The skill stack (layers)

```mermaid
graph TB
    subgraph ORCH["Orchestration"]
        IMP["implement"]
    end
    subgraph PROMPT["Prompt and Plan"]
        PF["prompt-forge"]
        BS["brainstorm"]
        VP["validation-plan"]
        PH["plan-hardening"]
    end
    subgraph EXEC["Execution"]
        CK["cook"]
        ST["stack-testing"]
        MVR["mobile-validation-runner"]
    end
    subgraph PROOF["Proof"]
        FV["functional-validation"]
        EG["end-user-testing"]
        VI["visual-inspection"]
        UX["ui-experience-audit"]
        FFA["full-functional-audit"]
    end
    subgraph DEEP["Deep analysis"]
        RCD["root-cause-debugging"]
        RTE["red-team-eval"]
        PR["production-readiness"]
        SI["session-intent"]
    end
    subgraph DOC["Doctrine — plugins/truth-forge/references/"]
        REF["end-user-actor.md<br/>evidence-contract.md<br/>severity-model.md<br/>platform-routing.md<br/>preflight-checks.md<br/>ci-gates.md<br/>defect-pattern-database.md<br/>web-wcag-checklist.md<br/>ios-hig-checklist.md"]
    end
    ORCH --> PROMPT
    ORCH --> EXEC
    ORCH --> PROOF
    ORCH --> DEEP
    PROMPT --> EXEC
    EXEC --> PROOF
    DEEP --> PROOF
    PROOF -.->|every verdict cites| DOC
    EXEC -.->|discipline from| DOC
    PROMPT -.->|stage 8 from| DOC
```

### 3. Delegation graph (who actually invokes whom)

Edges taken from each skill's own contract — not aspirational.

```mermaid
graph LR
    IMP["implement"] --> SI["session-intent"]
    IMP --> PF["prompt-forge"]
    IMP --> VP["validation-plan"]
    IMP --> PH["plan-hardening"]
    IMP --> CK["cook"]
    IMP --> RCD["root-cause-debugging"]
    IMP --> FV["functional-validation"]
    IMP --> EG["end-user-testing"]
    IMP --> ST["stack-testing"]
    IMP --> BS["brainstorm"]
    CK --> VP
    CK --> FV
    CK --> EG
    CK --> BS
    BS --> VP
    BS --> PH
    BS --> CK
    VP --> PH
    VP --> EG
    VP --> CK
    PH --> VP
    PH --> PF
    PF --> PH
    PF --> VP
    FV --> EG
    FV --> FFA["full-functional-audit"]
    FV --> VI["visual-inspection"]
    FV --> UX["ui-experience-audit"]
    FFA --> FV
    FFA --> EG
    FFA --> UX
    UX --> VI
    UX --> FV
    MVR["mobile-validation-runner"] --> VI
    MVR --> UX
    MVR --> EG
    RCD --> ST
    RCD --> FV
    RCD --> EG
    ST --> FV
    ST --> EG
    ST --> RCD
    ST --> CK
    PR["production-readiness"] --> FFA
    PR --> ST
    PR --> EG
    PR --> PH
    RTE["red-team-eval"] --> PH
    RTE --> PF
    RTE --> FV
    RTE --> EG
    SI --> PR
    SI --> RCD
    SI --> EG
    EG --> FV
    EG --> VI
    EG --> UX
```

### 4. One command traced: `implement "add billing webhooks" --parallel --auto --mine`

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant I as implement
    participant SI as session-intent
    participant SC as scout agents
    participant PF as prompt-forge
    participant PL as validation-plan + plan-hardening
    participant CK as cook
    participant RC as root-cause-debugging
    participant PR as proof layer (functional-validation + end-user-testing + stack-testing)
    U->>I: implement "add billing webhooks" --parallel --auto --mine
    I->>SI: Phase 1: mine past implementation sessions
    SI-->>I: intent matrix (prompts, tools, files, commits)
    I->>I: Phase 0: distill TRUE success criteria
    alt criteria not clearly laid out
        I->>U: present distilled criteria
        U-->>I: approval (the only mandatory stop)
    end
    par Phase 2: parallel exploration
        I->>SC: structure scout
        I->>SC: patterns scout
        I->>SC: contracts scout
        I->>SC: history scout (fed by mined matrix)
    end
    SC-->>I: 3-6 bullet context summary
    I->>PF: Phase 3: forge implementation prompt (canonical XML skeleton)
    PF-->>I: prompt with output_contract + validation per criterion
    I->>PF: Phase 4: --parallel -> PIPELINE mode, .prompts/ stages in parallel
    PF-->>I: dependency-aware stage tree
    I->>PL: harden the plan (proof obligations inside, not after)
    par Phase 5: parallel execution lanes
        I->>CK: lane A (webhook endpoint)
        I->>CK: lane B (signature verification)
        I->>CK: lane C (persistence + retries)
    end
    loop --auto: until every criterion is proven
        CK-->>I: lane result
        alt failure
            I->>RC: reproduce, minimize, root-cause fix
            RC-->>I: fix + blast-radius re-check
        end
        I->>PR: validate criterion as the end user
        PR-->>I: PASS / UNVERIFIED (= NOT DONE, keep going)
    end
    I->>U: criteria-by-criteria proof table + todo ledger + sealed evidence
```

### 5. The evidence lifecycle (every verdict, every skill)

```mermaid
stateDiagram-v2
    [*] --> InitRun: fresh_evidence.py init-run <slug>
    InitRun --> Capture: run-<timestamp>-<slug>/ created
    Capture --> Capture: next-step <slug> per artifact (step-NN)
    Capture --> Seal: fresh_evidence.py seal
    Seal --> Validate: evidence-inventory.txt written
    Validate --> Passed: exit 0 — fresh + non-empty + cited
    Validate --> Refused: exit 2 — STALE:/EMPTY: per artifact
    Refused --> Capture: re-capture the offending artifact
    Passed --> [*]: verdict may cite this run
```

Every PASS the plugin ever reports hangs off this lifecycle; anything not
executed through it is reported **UNVERIFIED**, never PASS.

## The proof: `examples/mood-ring/`

A complete live walkthrough on the **Flaskr** tutorial app (from `pallets/flask`, BSD-3):
the **Mood Ring** feature (per-post mood emoji 😀🙂😐😢🔥 + filter bar), built and audited
end-to-end by the original 10 skills in series:

- `.planning/` — brainstorm, BRIEF/ROADMAP, proof-carrying phase plans, hardening gap register,
  per-phase SUMMARY+VALIDATION, visual-inspection / UX / full-functional audit reports
- `.prompts/` — the authored build prompt and its 91/100 rating
- `e2e-evidence/run-20260808T202017-mood-ring/` — the sealed evidence run
  (19 artifacts; `validate OK`), including 5 browser screenshots committed as PNGs
  (see the README in that directory for what each one proves).
- `flaskr/`, `tests/` — the implementation: 32/32 tests green (24 baseline + 8 new)

Highlights from the run: a forged `<script>alert(1)</script>` mood POST safely defaults
to 😐 with a flash notice; an invalid `?mood=🦄` returns 200 unfiltered; visual
inspection caught (and the loop fixed) a blue-on-blue invisible "All" filter label.

## Repo layout

```
.claude-plugin/marketplace.json   marketplace manifest
plugins/truth-forge/              the plugin (18 skills + references + docs)
examples/mood-ring/               the live walkthrough (app + plans + evidence)
```

## License

MIT for the truth-forge plugin and documentation (see `LICENSE`). The Flaskr example
under `examples/mood-ring/` is derived from the Flask tutorial and remains BSD-3-Clause
(see `examples/mood-ring/LICENSE.txt`).
