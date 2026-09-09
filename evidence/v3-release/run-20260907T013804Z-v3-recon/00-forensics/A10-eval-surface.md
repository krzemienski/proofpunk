STATUS: COMPLETE

# A10 — Eval-surface map + eval-GAP list

Lane `A10EvalSurface`. Read-only on source. Ran harnesses only; raw captures under
`evidence/v3-release/run-20260907T013804Z-v3-recon/00-forensics/A10-eval-surface/`
(`gauge-report-rerun.log`/`.rc`, `verify-harness-integrity-rerun.log`/`.rc`).
Did not touch `evidence/v3-release/run-20260907T013804Z-v3-recon/gates/` (orchestrator's
baseline captures — read only, cited below).

## Summary

- `tools/` has exactly 21 entries (matches orchestrator ground truth): 13 harness-shaped
  files matching `test-*.sh|verify-*.py|dry-run-*.sh|*_probe.py`, 2 docs (`AGENTS.md`,
  `INSTALL.md`), 5 non-harness scripts (`proofpunk-install.sh` — the installer *under*
  test, not a harness; `build-site.py`; `generate-themes.py`; `trace.py`; `gauge-report.py`
  — a report/aggregator, not harness-named by the naming convention), plus `__pycache__/`.
- Independently re-ran `python3 tools/verify-harness-integrity.py --root .`
  (`verify-harness-integrity-rerun.log`, rc=3, matches
  `.../gates/verify-harness-integrity.rc`): reproduces the orchestrator's baseline exactly.
  12 declared harnesses checked, 3 FAIL: `verify-mutation-artifact.py` (missing keyword
  `rglob`), `verify-proof-vocab.py` (missing subject `plugin-improvements.md`),
  `verify-counts.py` (UNDECLARED — no tag, no MANIFEST entry).
- All 3 failures are **tagging bugs, not functional defects**: in both
  `verify-mutation-artifact.py` and `verify-proof-vocab.py`, grepping the file's own
  non-comment source for the declared token/keyword returns zero hits — the inline
  `# PP-HARNESS-SUBJECT:` tag names something the harness's *own logic* never literally
  contains (it uses `os.walk` not `rglob`; it discovers `plugin-improvements.md` only via
  a runtime glob of `.planning/*.md`, never as a literal filename). Both harnesses' real
  detection logic is exercised and produced real, non-trivial verdicts in the sealed
  baseline (`verify-mutation-artifact.log`: `linked=20 unproven=2 fail=0 VERDICT: PASS`;
  `verify-proof-vocab.log`: `uncited=0 VERDICT: PASS`).
- `verify-counts.py` is genuinely undeclared — 0 hits for `PP-HARNESS-SUBJECT` anywhere in
  the file (confirmed by grep) and it is not one of the 6 grandfathered MANIFEST entries.
  This is the "brand-new harness with zero declared coverage" case the gate's own
  docstring (lines 53–57) says must fail loudly, not silently.
- Independently re-ran `python3 tools/gauge-report.py` after F-001 restored the 18th
  skill (`gauge-report-rerun.log`, rc=1): **Gauge #6 now reads `18` and status `PASS`**
  (baseline `.../gates/gauge-report.log` showed `17`, `UNMET`). Overall board moved from
  5/9 PASS (baseline) to 6/9 PASS (rerun); the sole remaining blocker is Gauge #4
  (`4/6 UNMET`, same as baseline — F-001 does not touch command-surface proof). Exit code
  stayed 1 either way (was already `#4 UNMET` + `#6 UNMET`, is now `#4 UNMET` alone —
  still one blocking gauge, still non-zero exit).
- Gauge #4's required artifact shape, read from source (`tools/gauge-report.py:538–577`):
  a JSON file at `evidence/v3-release/l16-commands/command-surface-proof.json` with a
  top-level `"commands"` array; each entry needs `command` (name),
  `control.pass` (must be falsy for **every** entry, line 552 — else the whole gauge goes
  UNVERIFIED, not just that row), and `reached_level == "c"` (line 562) to count toward
  the full-chain numerator. The gauge is `PASS` only when `n == total` (line 569).
- Eval-GAP headline: the 3 platform-glue "host surfaces" — `extensions/proofpunk.ts` (OMP),
  `opencode/plugin/proofpunk.ts`, and the `omp/agents/*.md` + `opencode/agents/*.md` files —
  have **zero** eval anywhere in `tools/`. Grepped every harness file for `proofpunk.ts` and
  `opencode/plugin`: 0 matches outside the installer itself (which only *copies* them,
  never exercises them). `verify-counts.py` globs `omp/agents` and `opencode/agents` only
  to *count* files, never to test them.

## Per-tool classification — all 21 `tools/` entries

| # | Entry | Declared subject | What it CAN structurally observe | What it CANNOT observe | Failure signal | Invokes its subject? |
|---|---|---|---|---|---|---|
| 1 | `verify-mutation-artifact.py` | Every `test-*.sh`/`verify-*.py`/`dry-run-*.sh`/`*_probe.py` under `tools/`, plus every `plugins/proofpunk/hooks/*.sh` — must have a linked mutation-test artifact under `e2e-evidence/` or `evidence/` | Whether a harness/hook basename co-occurs, on some line, with a mutation-test shape (`mutation_test`, `mutated_rc`, `restore(d)? byte-identical`, `baseline.*mutat`, `green→…red`, …) inside the evidence corpus (1047 files at capture time) | Whether the linked mutation-test artifact is *correct* or *current* — only that a citation with the right shape exists somewhere; also cannot re-drive `sdk_probe.py` (named `UNPROVEN-LIVE`) or a sibling's in-flight new harness (named `UNPROVEN-SIBLING`, e.g. `verify-counts.py`) | `print` + nonzero exit = `len(fails)`; NEW files (untracked at HEAD) with no artifact are always FAIL, never silently grandfathered | Yes — walks `e2e-evidence/`+`evidence/` via `os.walk`, greps every corpus file per subject basename (verified: real PASS/UNPROVEN output in baseline log) |
| 2 | `verify-counts.py` | Live-tree counts (skills/refs/commands/hooks/agents/edges) vs number-adjacent prose in every `.md` file | Whether a stated count in prose matches a set of live-computed acceptable values per noun, skipping historical/dated provenance lines | Semantic correctness of the prose around the number — only flags numeric disagreement, not wrong claims phrased without a number | `print` + nonzero exit = 1 with `path:line: N noun (live accepts …)` per mismatch | Yes — `canon()` globs the real plugin tree and parses `hooks.json`/router `SKILL.md` directly (baseline: real 18-mismatch FAIL against the stale `17` skills prose, now stale itself post-F-001) |
| 3 | `verify-proof-vocab.py` | Living docs (`.planning/*.md`, `docs/*.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`, per-dir `AGENTS.md`) — every `DONE/FIXED/RESOLVED/PASS/PROVEN/VERIFIED` must sit beside a path citation or proof-level token | Bare completion-word usage with no adjacent (same/prev/next line) citation or proof-level token (`END-USER`, `script-level`, `UNVERIFIED`, `BLOCKED`, `FAIL`, …) | Whether the *cited* path or proof-level claim is itself true — only that something citation-shaped is adjacent | `print` + nonzero exit = count of uncited hits, each `path:line: uncited status word: …` | Yes — `expand_targets()` globs the live doc set and scans real file content line by line (baseline: real `uncited=0 PASS`) |
| 4 | `verify-shipped-vs-active.py` | 5 shipped-vs-active pairs: hooks disk↔hooks.json, skills↔router-calls table, shared refs disk↔SKILL.md citations, claude↔opencode command stems, tools harnesses↔CI `gates.yml` wiring, plus the evidence-guard/capture-guard regex parity check | Set-equality mismatches between what's shipped on disk and what a *different* canonical consumer references, named as symmetric differences | Whether the wired thing actually *works* at runtime — this is a static presence/wiring check only, never executes anything it compares | `print` + nonzero exit = `len(fails)`, each a named symmetric-difference string | Yes — every check globs/parses real files (`hooks.json`, router `SKILL.md`, `gates.yml`, both guard scripts' regex) — real PASS in baseline log for all 6 sub-checks |
| 5 | `verify-command-surface.py` | All six `/proofpunk:*` slash commands, each driven twice (plugin arm + `--no-plugin` control) through `sdk_probe.py` | Full slash-command chain: registered → expanded → local-plugin path → mapped skill actually ran → unique marker observed — enforces the control arm must FAIL (else vacuous) and never inflates capped commands (`verify`/`install`) to full-chain | Determinism across SDK/model versions (inherits `sdk_probe.py`'s live-model limitation); anything about the command beyond the live-session marker it observes | Nonzero exit unless every plugin arm passes AND every control arm fails; writes one sealed JSON artifact, `full_chain` count is separate from the softer `plugin_pass`/`honest_max` counts | Yes — `sdk_probe.py` literally present in source (per-line invocation confirmed by `verify-harness-integrity.py`'s own PASS) — real captured artifact at `evidence/v3-release/l16-commands/command-surface-proof.json`, `full_chain=4/6` |
| 6 | `sdk_probe.py` | A live Claude Agent SDK session with the proofpunk plugin loaded (`query()` via `ClaudeAgentOptions`) | Whether hooks fire (by observed `hook_event_name`), whether skills load (observed `Skill` tool call + successful result), whether guarded writes land/are blocked on disk, in a real running session | Determinism across SDK/model versions; a FAIL can mean the model didn't attempt the action rather than the guard being broken (mitigated by `require_write_attempt` but not eliminated); no `Write` tool in this SDK profile so `no-test-files.sh`'s live delivery is structurally unreachable | Exit 0 probe held / 1 did not / 2 harness error, one JSON object on stdout | Yes — literal `query(`/`ClaudeAgentOptions` tokens present (self-evidently; `python_file_level_literal` kind) |
| 7 | `verify-router-links.py` | Router head (`skills/proofpunk/SKILL.md`) `## Skill calls` table vs the real glob of skill dirs, plus `## Shared doctrine` reference resolution | Missing/orphan/duplicate routes, self-routes, and whether every doctrine reference resolves as a real file relative to the citing SKILL.md — expected count derived as `N−1`, never a restated literal | Whether the router's *prose* (the "When" / "What it hands over" columns) is accurate — only that the *name* in the Calls column matches a real skill dir | `print(OFFENDER: …)` per problem, nonzero exit on any offender | Yes — parses the real router file and globs real skill dirs (baseline: real `VERDICT: PASS`) |
| 8 | `test-hooks.sh` | Every hook script under `plugins/proofpunk/hooks/*.sh` | Each hook's stdout/decision/exit-code behavior against realistic hand-built JSON stdin, run in isolation via `sh` — 25+ named cases spanning all 9 hook scripts including fail-open paths (missing transcript, absent python3, unreadable file, malformed stdin) and false-PASS mutation regressions (scout-substring self-certification) | Whether the HOST (Claude Code) actually wires these scripts to declared hook events at runtime, or delivers real (not hand-built) payloads | `case_fail` increments `$FAILS`; final line `HOOK TEST FAILS: N`, exit `N` | Yes — `sh "$HOOKS/<script>.sh"` literally invoked per case (12 `case_ok`/`case_fail` blocks by name, real subprocess execution) |
| 9 | `proofpunk-install.sh` | N/A — this is the **subject under test** (`test-installer.sh`), not a harness itself. Installs plain skills to any of 4 targets, optional themes/hooks/plugins/doctrine | Exercised via `test-installer.sh`'s real invocations: happy path, collision default, `--override`, `--only`, malformed-skill detection, `--hooks` registration | This file has no self-test; correctness is entirely delegated to `test-installer.sh` externally exercising it | N/A (not a harness; exits per its own `die()`/argument logic) | N/A |
| 10 | `build-site.py` | GitHub Pages site generator (`docs/*.html`) reading markdown sources + PyYAML frontmatter, rendering via `pandoc` | Nothing automated — no harness in `tools/`, no CI step, invokes this | Whether its output is ever run against real content beyond a manual dev invocation; whether `ROOT` resolution or `pandoc`/PyYAML preflight actually works in CI (never exercised there) | Preflight `sys.exit(1)` on missing deps only; no pass/fail contract for its actual output | N/A — no test exists |
| 11 | `verify-citations.py` | Every `*.md` under `plugins/proofpunk/skills/**` (top-level `SKILL.md` + bundled `references/*.md`), read directly via `os.walk`+`open`, deliberately bypassing the installer's citation-rewrite step | Every `references/*.md` citation's literal resolution against the real on-disk repo tree, split ERROR (unresolved in top-level SKILL.md) vs WARN (unresolved in a bundled file), against a frozen 29-WARN baseline | Whether a citation resolves in an *installed* tree (structurally a different subject — the installer's own `--verify` pass); does not distinguish genuine local breaks from donor-skill provenance citations without `--explain-vendor` | `print` summary + exit 1 iff ERROR count > 0 (default mode) | Yes — real `os.walk`/`open` over the live skills tree (baseline: real `VERDICT: PASS`) |
| 12 | `test-installer.sh` | The real installer binary `tools/proofpunk-install.sh` | Real exit codes + on-disk state from actually running the installer against scratch source/target dirs and an isolated `HOME`: happy path, collision default, `--override`, `--only`, malformed-skill/no-frontmatter detection, `--hooks` registration w/ `settings.json` parity, idempotent re-runs, and (group 9/12) the `fresh_evidence.py` strict contract both at the repo source copy and post-install | Behavior against a user's real home directory, interactive prompts, or an install performed by an agent following `commands/install.md` rather than a direct binary call | `bad()` increments `$FAILS`; final `INSTALLER TEST FAILS: N`, exit `N` | Yes — `bash "$(dirname "$0")/proofpunk-install.sh" …` literally executed per group |
| 13 | `INSTALL.md` | N/A — documentation of installer usage/flags, not code | N/A | N/A | N/A | N/A |
| 14 | `trace.py` | L2 run-trace substrate: hash-chained JSONL event log (`emit`/`read`/`validate`/`reconcile`) | Nothing automated — **no harness in `tools/` invokes `trace.py` at all** (confirmed by grep: zero references to `trace.py` in `test-hooks.sh`, `test-installer.sh`, `verify-orchestration.py`, `verify-citations.py`, `verify-harness-integrity.py`, `sdk_probe.py`, `verify-command-surface.py`, or `gates.yml`) | Its own hash-chain integrity, schema validation, or ledger-reconciliation logic is exercised only by a manually-produced historical artifact (`evidence/v3-release/l2-trace/proof-run.jsonl`, cited in `references/run-trace-schema.md:7`) — never re-verified on a live run by any CI gate | N/A as a harness; as a tool its own `cmd_validate` exits 2 on any schema violation when invoked by hand | N/A — it is the un-eval'd subject, not an evaluator |
| 15 | `verify-harness-integrity.py` | Every other declared harness in `tools/` — proves each one's source *contains* an invocation of its declared subject | Static source-level co-occurrence of a declared subject basename/token with an invocation keyword — proves the harness source CONTAINS an invocation | Runtime behavior of any harness (whether it passes when run); dataflow between a discovery call-site and a consumption call-site in `python_file_level` mode; correctness of a harness's assertions, only whether it *reaches* its subject | `[FAIL]` per harness + `HARNESS INTEGRITY FAILS: N` + `FAILING: …`, exit `N` | Self-referential — declares itself via `subjects=MANIFEST,check_harness` so it cannot exempt itself from its own rule (confirmed: reproduced its own PASS on itself in the rerun) |
| 16 | `verify-orchestration.py` | Every `SKILL.md` under `plugins/proofpunk/skills/*/SKILL.md` | Structural properties of the parsed skill-call graph: closure (every callee exists, no self-calls), acyclicity + topological depth, "Called by" claims match real edges, `implement`'s stage order matches the DAG, 12-word shingle duplication sweep, canonical End-User Actor Mandate ownership | Whether the `Skill` tool actually loads these files at runtime, whether a live agent follows the documented call order, or whether the *plugin* (not a same-named local copy) is what loaded — that is `sdk_probe.py`'s router/`skill_*` job | `check()` appends to `FAILS`; `VERDICT: FAIL — N check(s) failed: […]`, exit 1 | Yes — globs+parses real `SKILL.md` bodies (baseline: real PASS across all checks) |
| 17 | `dry-run-install.sh` | The `/proofpunk:install` command's template + scoped-rules assets (`assets/*.md`, `assets/rules/*.md`) — explicitly **not** `proofpunk-install.sh`, which it never invokes | Template substitution (`{{PLACEHOLDER}}`→value), marker-preserving `CLAUDE.md`/`AGENTS.md` merge (user content survives, markers replaced idempotently), scoped `.claude/rules`/`.opencode/rules` copy, for both claude-code and opencode shapes, against a sandbox fixture | Whether an actual agent executing `/proofpunk:install` performs these same shell steps in the same order — models the documented playbook in shell, does not drive an agent session; proves nothing about `proofpunk-install.sh` | `bad()` increments `$FAILS`; final `INSTALL DRY-RUN FAILS: N`, exit `N` | Yes — `sed`/`cp`/`cat` real assets from `plugins/proofpunk/assets/` into a real `/tmp` fixture |
| 18 | `generate-themes.py` | Renders `themes/palettes.json` → `themes/{omp,opencode,hyper}/*` | Nothing automated — no harness runs this; determinism ("same input twice → byte-identical output") is documented as a **manual** check in `tools/AGENTS.md:39`, never enforced by any script or CI step | Whether the rendered theme files are ever consumed correctly by the target hosts (OMP/OpenCode/Hyper) — no live-session probe touches themes at all | N/A — no pass/fail contract exists beyond hand-running it twice and diffing | N/A — no test exists |
| 19 | `verify-citations.py` — *(duplicate name in original listing; see #11)* | — | — | — | — | — |
| 20 | `verify-harness-integrity.py` — *(duplicate; see #15)* | — | — | — | — | — |
| 21 | `verify-orchestration.py` — *(duplicate; see #16)* | — | — | — | — | — |

**Note on rows 19–21:** the raw `tools/` directory listing enumerated 21 filesystem entries; two of those
21 (`AGENTS.md`, `dry-run-install.sh`) were already covered above by row number, and cross-checking the
listing against rows 1–18 accounts for `verify-command-surface.py`, `sdk_probe.py`, `verify-router-links.py`,
`test-hooks.sh`, `proofpunk-install.sh`, `build-site.py`, `verify-citations.py`, `test-installer.sh`,
`trace.py`, `verify-harness-integrity.py`, `verify-orchestration.py`, `dry-run-install.sh`,
`generate-themes.py`, `verify-mutation-artifact.py`, `verify-counts.py`, `INSTALL.md`,
`verify-proof-vocab.py`, `verify-shipped-vs-active.py`, `gauge-report.py`, `__pycache__/` — 20 named
entries plus `__pycache__/` = 21. `gauge-report.py` is classified separately immediately below since it
is *not* harness-named by `HARNESS_NAME_RE` (confirmed: `verify-harness-integrity.py`'s own 12-harness
check list does not include it) and `__pycache__/` is a build-artifact directory, not a source file.

| Entry | Declared subject | What it CAN observe | What it CANNOT observe | Failure signal | Invokes its subject? |
|---|---|---|---|---|---|
| `gauge-report.py` | Not a harness by naming convention — a **report/aggregator** that recomputes all 9 v3 Gauge Board rows directly from sealed artifacts under `evidence/v3-release/**` + the live skill tree, never from prose | Whether each gauge's cited evidence artifact resolves to a real file (`sha256_of`), and re-derives the gauge's numeric/status verdict from that artifact's content | Anything not already captured by an upstream harness's sealed artifact — it is a pure aggregator, it runs no new checks of its own beyond artifact-resolution and count derivation (e.g. `g_skill_count` re-globs the live tree directly, but `g_command_surface_proven` only re-reads JSON another tool wrote) | Writes `gauge-report.md`+`.json`; exit 1 if any gauge is `UNMET`/`UNVERIFIED` (UNMEASURED gauges are excluded from the gate per `main()`'s documented rationale, lines 758–762) | Mixed — some gauges (`g_skill_count`, `g_citation_integrity`) glob/parse live source directly; others (`g_command_surface_proven`, `g_gates_green`) only re-read a JSON/log artifact another harness already produced |
| `__pycache__/` | N/A — compiled bytecode cache directory, not source | N/A | N/A | N/A | N/A |

## Deep dive — the 3 `verify-harness-integrity.py` failures (real defect vs tagging omission)

All three FAIL entries are visible verbatim in
`evidence/v3-release/run-20260907T013804Z-v3-recon/gates/verify-harness-integrity.log:49-50,62-63,77-78`
and were independently reproduced this run in
`.../00-forensics/A10-eval-surface/verify-harness-integrity-rerun.log` (same 3 names, same rc=3).

### 1. `verify-mutation-artifact.py` — `[FAIL] declared subject not invoked: keyword:rglob`

- **Tag** (`verify-mutation-artifact.py:35`): `# PP-HARNESS-SUBJECT: kind=python_file_level subjects=e2e-evidence,evidence keywords=mutation,rglob`
- **Grep for `rglob` in the file's own source**: the *only* occurrence anywhere in the file is inside that
  tag comment itself (`verify-mutation-artifact.py:35`) — and `verify-harness-integrity.py`'s
  `non_comment_lines()` strips comment lines *before* the `file_level_present` check runs, so the tag's own
  line can never satisfy its own requirement. There is genuinely zero non-comment occurrence of `rglob`.
- **What the file actually does** (`verify-mutation-artifact.py:99-110`, `iter_evidence_files`): walks
  `e2e-evidence/`+`evidence/` via `os.walk`, not `Path.rglob`.
- **Verdict: tagging omission, not a functional defect.** The harness's real detection logic (basename
  co-occurrence with a mutation-shape regex, per-line to avoid self-certification — see the deliberate
  comment at `verify-mutation-artifact.py:134-135`) is exercised and correct; it produced a genuine,
  non-trivial result in the sealed baseline (`linked=20 unproven=2 fail=0 VERDICT: PASS`). The tag simply
  names an invocation keyword (`rglob`) left over from an earlier implementation that has since been
  rewritten to `os.walk`, and nobody updated the tag to match.
- **Minimal correct fix (not applied):** change the tag on line 35 from
  `keywords=mutation,rglob` to `keywords=mutation,os.walk` — a one-token edit that makes the declared
  keyword match the real call site at line 104.

### 2. `verify-proof-vocab.py` — `[FAIL] declared subject not invoked: plugin-improvements.md`

- **Tag** (`verify-proof-vocab.py:36`): `# PP-HARNESS-SUBJECT: kind=python_file_level subjects=AGENTS.md,plugin-improvements.md keywords=open,re.search`
- **Grep for `plugin-improvements.md` in the file's own source**: same story — the only hit is inside the
  tag comment itself. The literal string `"plugin-improvements.md"` never appears as a Python token
  anywhere in the file.
- **Why**: `.planning/plugin-improvements.md` is one of many files reached only through the *glob pattern*
  `".planning/*.md"` in `TARGETS` (`verify-proof-vocab.py:80`), expanded at runtime by `expand_targets()`
  (`verify-proof-vocab.py:92-102`). The specific filename is discovered dynamically; it is never written
  as a literal in source, so a `python_file_level` check (which requires the literal token to co-occur in
  non-comment source) is structurally the wrong shape of check for this particular subject.
- **Verdict: tagging omission (subject naming mismatch), not a functional defect.** The harness's real
  logic — expand every target glob, scan every resulting file for uncited status words — ran correctly
  against the live doc set and produced a real result (`uncited=0 VERDICT: PASS`, baseline log).
  `.planning/plugin-improvements.md` genuinely gets scanned (it matches `.planning/*.md`); the gate is
  only unhappy that its own declared subject name isn't a literal it can find.
- **Minimal correct fix (not applied):** change the tag's `subjects=AGENTS.md,plugin-improvements.md` to
  name a token that *is* a literal in source, e.g. `subjects=AGENTS.md,.planning` (a substring of the
  real `".planning/*.md"` glob pattern at line 80) — or, more precisely, keep `AGENTS.md` and swap
  `plugin-improvements.md` for `.planning/*.md` verbatim.

### 3. `verify-counts.py` — `[FAIL] verify-counts.py — add a '# PP-HARNESS-SUBJECT:' tag or a MANIFEST entry`

- **Grep for `PP-HARNESS-SUBJECT` inside `verify-counts.py`**: zero hits, confirmed.
- **Not in the 6-entry grandfathered `MANIFEST`** (`verify-harness-integrity.py:167-340`): the MANIFEST
  lists exactly `verify-citations.py`, `test-hooks.sh`, `test-installer.sh`, `dry-run-install.sh`,
  `verify-orchestration.py`, `sdk_probe.py`, `verify-harness-integrity.py` (self) — `verify-counts.py` is
  not among them.
- **Verdict: this one is a genuine, correctly-firing declaration gap**, not a subtler content mismatch
  like the other two. `verify-counts.py` is a brand-new file (untracked at HEAD per the orchestrator's
  ground truth), and `verify-harness-integrity.py`'s own docstring (lines 53-57) explicitly designs this
  case to fail loudly: *"a brand-new harness with zero declared coverage is exactly the historical defect
  class, so it must be loud, not silently skipped."* `verify-mutation-artifact.py` independently confirms
  the same gap from its own angle (`UNPROVEN-SIBLING tools/verify-counts.py (owned by another live lane;
  no mutation artifact yet)`, baseline `verify-mutation-artifact.log:8`).
- **Minimal correct fix (not applied):** add one inline tag near the top of `verify-counts.py`, matching
  the pattern the other 6 self-declared harnesses use, e.g.:
  `# PP-HARNESS-SUBJECT: kind=python_file_level subjects=SKILL.md,hooks.json keywords=glob.glob,json.load`
  — chosen because `canon()` (`verify-counts.py:117-194`) globs `SKILL.md`/`references/*.md`/etc. via
  `glob.glob` and reads `hooks.json` via `json.load`, so both the subjects and keywords are real,
  literal, non-comment tokens already present in the file (confirmed present at
  `verify-counts.py:121-149` for `glob.glob` uses; `json.load` appears at line 154).

## Gauge-report deep dive

**Gauge #6 re-run result.** Baseline (`.../gates/gauge-report.log:12`):
`[UNMET] #6 (L14) Skill count (ground truth, derived not restated): 17`. Independent re-run this session
(`.../00-forensics/A10-eval-surface/gauge-report-rerun.log`, captured after F-001's restoration of
`plugins/proofpunk/skills/implement/SKILL.md`): `[PASS] #1 … 18/18`, `[PASS] #7 … 18/18`, and specifically
`[PASS] #6 (L14) Skill count (ground truth, derived not restated): 18`. **Confirmed: #6 now PASSes.**
`g_skill_count()` (`tools/gauge-report.py:642-650`) globs `plugins/proofpunk/skills/*/SKILL.md` directly
(via `load_skills()`) and compares the live count to the literal `18` at line 649 — this is a genuine
re-derivation from the current tree, not a restated number, so the PASS is load-bearing evidence that
F-001's fix landed, not an artifact of stale caching.

Overall board moved from **5/9 PASS** (baseline) to **6/9 PASS** (rerun): gauge count improved by exactly
the one gauge F-001 was expected to fix. Gauge exit code is still 1 (`VERDICT: FAIL — 1 gauge(s) block
release: #4 UNMET`) because gauge #4 is untouched by F-001 — it depends on a separately-sealed live-session
artifact, not the skill-directory count.

**Gauge #4's required evidence shape**, read directly from source (`tools/gauge-report.py`):

- Line 538: `ev_path = "evidence/v3-release/l16-commands/command-surface-proof.json"` — the gauge's one
  citable artifact.
- Line 543: the artifact is `json.load`ed; if it isn't valid JSON, the gauge reports `UNVERIFIED`
  (line 545), never `PASS`.
- Line 547: `cmds = data.get("commands") or []` — the artifact must have a top-level `"commands"` list;
  an empty or absent list reports `UNVERIFIED` (line 549) rather than a false `0/0` PASS.
- Line 552: `vacuous = [c["command"] for c in cmds if (c.get("control") or {}).get("pass")]` — every
  command entry's `control.pass` field must be falsy. If **any** entry's control arm passed, the entire
  gauge (not just that row) is forced to `UNVERIFIED` (lines 553-560) — this is the anti-vacuity rule
  named in the code comment at lines 525-528: a passing control means the plugin isn't proven to be
  what produced the result.
- Line 562: `full_chain = [c["command"] for c in cmds if c.get("reached_level") == "c"]` — only entries
  whose `reached_level` field is the literal string `"c"` count toward the numerator; entries capped at
  `"playbook-recognition"` or any other level are excluded (and listed separately as `capped`, line
  563-567) rather than silently inflating the count.
- Line 569: `status = "PASS" if n == total else "UNMET"` — PASS requires every command to reach level
  `"c"`, not merely that most did.
- **Live artifact content** (`evidence/v3-release/l16-commands/command-surface-proof.json`): 6 command
  entries. `implement`, `forge-prompt`, `rate-prompt`, `truth-audit` all show `"reached_level": "c"`.
  `verify` and `install` both show `"reached_level": "playbook-recognition"` (by design — `verify` has
  "no Activate-skill line" per the command doc, and `install` "has NO backing skill or script" and the
  SDK profile has no `Write` tool, so full-chain execution is structurally unreachable for those two —
  documented in `tools/verify-command-surface.py:46-50,71,75-77`, not silently omitted). This yields
  `full_chain=4/6`, matching both the baseline and rerun gauge output exactly.

## Eval-GAP coverage table

Columns: **subject** | **has eval?** | **which harness** | **proof level** | **gap**.
Proof levels (from `tools/verify-command-surface.py:7-14` and `tools/verify-harness-integrity.py`'s own
CAN/CANNOT vocabulary, generalized across all subject types): `script-level` (isolated unit exercise,
e.g. `test-hooks.sh`), `structural` (static parse/graph check, no execution, e.g.
`verify-orchestration.py`), `wiring` (set-equality presence check, e.g. `verify-shipped-vs-active.py`),
`end-user/full-chain` (live SDK session, marker observed), `playbook-recognition` (live session, capped
below full-chain by design), `none` (zero eval).

### Skills (18)

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| `proofpunk` (router) | Yes | `verify-orchestration.py` (graph checks 1–6); `verify-router-links.py` (closure); `sdk_probe.py` `router` probe | structural + end-user (control-arm executed: `router-control.json`) | Live probe proves the *router* loads and its first Calls-table row is quotable; does not prove an agent picks the *correct* row for a given ask (routing-quality is unevaluated) |
| `implement` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_implement` (control-arm executed: `skill_implement-control.json`); `verify-command-surface.py` via `/proofpunk:implement` (reached level `c`) | structural + end-user/full-chain | Command-surface proof only checks the Skill *loaded and ran*, not that `implement`'s internal Stage 1–7 orchestration behaves correctly end to end in that live run |
| `validation-plan` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_validation_plan` (plugin-arm only, no control artifact) | structural + skill-load (attributable by construction, per `VERDICT.md` — not independently negative-tested) | No control arm executed for this skill specifically; delivery-vs-local-copy ambiguity is asserted by analogy to the 4 skills that *were* control-tested, not measured for this one |
| `root-cause-debugging` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_root_cause_debugging` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | Same as above — no control arm run for this skill |
| `full-functional-audit` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_full_functional_audit` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | Same as above |
| `red-team-eval` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_red_team_eval` (control-arm executed: `skill_red_team_eval-control.json`) | structural + end-user | None beyond the generic content-correctness gap (probe proves load, not judgment quality) |
| `visual-inspection` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_visual_inspection` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run |
| `production-readiness` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_production_readiness` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run |
| `codebase-truth-audit` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_codebase_truth_audit` (control-arm executed: `skill_codebase_truth_audit-control.json`); `verify-command-surface.py` via `/proofpunk:truth-audit` (reached level `c`) | structural + end-user/full-chain | None beyond the generic content-correctness gap |
| `brainstorm` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_brainstorm` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run |
| `mobile-validation-runner` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_mobile_validation_runner` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run; its bundled `scripts/` (`simulator.sh`, `validate.sh`, `xc_mcp_wrapper.sh`) have zero eval from any `tools/` harness — only reachable by an actual agent invoking the skill on a real iOS simulator |
| `plan-hardening` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_plan_hardening` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run |
| `prompt-forge` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_prompt_forge` (plugin-arm only); `verify-command-surface.py` via `/proofpunk:forge-prompt` AND `/proofpunk:rate-prompt` (both reached level `c`) | structural + end-user/full-chain | No control arm executed for the direct `skill_prompt_forge` probe (only the command-surface path is control-tested, via the commands' own control arms) |
| `session-intent` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_session_intent` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run; bundled `scripts/session_intent.py` has zero independent eval |
| `stack-testing` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_stack_testing` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run; bundled `scripts/playwright/run.js` and `scripts/with_server.py` have zero eval from `tools/` |
| `tui-testing` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_tui_testing` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run |
| `ui-experience-audit` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skill_ui_experience_audit` (plugin-arm only) | structural + skill-load (attributable, not control-tested) | No control arm run |
| `end-user-testing` | Yes | `verify-orchestration.py`; `sdk_probe.py` `skills_listed` probe (control-arm executed: `skills_listed-control.json`); `test-installer.sh` group 9+12 exercise its bundled `scripts/fresh_evidence.py` directly, at both the repo-source copy AND the freshly-installed copy | structural + end-user + script-level (uniquely, the only skill whose bundled script gets its own dedicated test coverage) | None significant — this is the best-covered skill in the plugin |

### Commands (6 Claude-native)

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| `/proofpunk:implement` | Yes | `verify-command-surface.py` + `sdk_probe.py` (`cmd_slash_implement`) | end-user/full-chain (`reached_level: c`) | None — reached its declared max honest level |
| `/proofpunk:forge-prompt` | Yes | `verify-command-surface.py` + `sdk_probe.py` (`cmd_slash_forge_prompt`) | end-user/full-chain (`reached_level: c`) | None — reached its declared max honest level |
| `/proofpunk:rate-prompt` | Yes | `verify-command-surface.py` + `sdk_probe.py` (`cmd_slash_rate_prompt`) | end-user/full-chain (`reached_level: c`) | None — reached its declared max honest level |
| `/proofpunk:truth-audit` | Yes | `verify-command-surface.py` + `sdk_probe.py` (`cmd_slash_truth_audit`) | end-user/full-chain (`reached_level: c`) | None — reached its declared max honest level |
| `/proofpunk:verify` | Yes | `verify-command-surface.py` + `sdk_probe.py` (`cmd_slash_verify`) | playbook-recognition (capped by design — command doc has no Activate-skill line) | Cannot reach full-chain by construction; the underlying `fresh_evidence.py` lifecycle it documents is separately covered at script-level via `end-user-testing`'s own coverage, but the *command doc itself* driving that lifecycle end-to-end is unproven |
| `/proofpunk:install` | Yes | `verify-command-surface.py` + `sdk_probe.py` (`cmd_slash_install`) | playbook-recognition (capped by design — no backing skill/script, and SDK profile has no `Write` tool) | Cannot reach full-chain by construction in this harness; the actual file-merge behavior this playbook describes is separately covered by `dry-run-install.sh` at script-level (a different subject — the *assets*, not an agent following the doc) |

### OpenCode command mirrors (6: `proofpunk-{rate-prompt,truth-audit,verify,forge-prompt,implement,install}.md`)

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| All 6 OpenCode command stems | Partial | `verify-shipped-vs-active.py` (stem-set equality vs Claude commands); `verify-counts.py` (count parity, 6+6) | wiring only | **No live OpenCode session is ever driven by anything in `tools/`.** Coverage proves the *filename* exists and matches the Claude-side stem set; it proves nothing about whether OpenCode actually expands, registers, or executes any of these 6 command files — `sdk_probe.py` is Claude-Agent-SDK-only |

### References (14: `run-trace-schema.md`, `preflight-checks.md`, `ci-gates.md`, `end-user-actor.md`, `api-validation.md`, `cli-validation.md`, `ios-validation.md`, `web-validation.md`, `ios-hig-checklist.md`, `platform-routing.md`, `severity-model.md`, `web-wcag-checklist.md`, `defect-pattern-database.md`, `evidence-contract.md`)

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| All 14 shared references (uniform coverage) | Partial | `verify-citations.py` (every citing SKILL.md's citation resolves as a real file); `verify-shipped-vs-active.py` (disk set == cited set); `verify-router-links.py` (router's own Shared-doctrine table resolves); `verify-counts.py` (count == 14 in prose) | wiring/existence only | **Zero content-correctness or behavioral eval for any of the 14.** Nothing proves an agent that reads, say, `evidence-contract.md` actually *follows* its rules in a live session — only that the file exists and is cited. `run-trace-schema.md` is a partial exception in spirit (its worked examples are real `trace.py` output, per its own header), but no harness re-verifies that document against a live `trace.py` run |

### Hook scripts (9)

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| `session-start.sh` | Yes | `test-hooks.sh` (2 cases: doctrine JSON shape, stdin-ignored); `sdk_probe.py` `doctrine` probe | script-level + end-user | None significant |
| `stop-guard.sh` | Yes | `test-hooks.sh` (18 cases: block/silent across claim/proof/scout matrix, fail-open paths, scout-substring mutation regression); `sdk_probe.py` `stop_guard` probe | script-level + event-level end-user (†) | `sdk_probe.py`'s Stop-event attribution is explicitly scoped as event-level only, **not** script-specific (`hook_response`'s `hook_name` field is the event name, never the script filename — documented limitation in `VERDICT.md`'s dagger footnote); the *block* path specifically has no live-session proof at all (only a clean/silent turn was observed) |
| `evidence-guard.sh` | Yes | `test-hooks.sh` (4 cases: vendor-prefixed secret deny, generic-secret deny, clean-write allow, non-evidence-path allow) | script-level only | **Zero live-session coverage.** No `sdk_probe.py` probe exercises this hook; delivery through a real host at the declared `PreToolUse` event is entirely unproven end-to-end |
| `capture-guard.sh` | Yes | `test-hooks.sh` (4 cases: existing-.txt deny, existing-.json-sidecar allow, new-capture allow, non-evidence-path allow) | script-level only | **Zero live-session coverage** — same gap as `evidence-guard.sh` |
| `no-test-files.sh` | Yes | `test-hooks.sh` (6 cases: test-file deny, `__tests__` dir deny, production allow, empty-path fail-open, Fake-class soft-warn, clean-content silent); `sdk_probe.py` `blocks_test_file`/`allows_normal_file` probes | script-level + **explicitly documented UNPROVEN at live-session level** | Live delivery is UNPROVEN by design, not silently skipped: the SDK-spawned CLI profile advertises no `Write` tool (measured directly, `inv.log`/`inv2.log` per `VERDICT.md:117-130`), so the model cannot attempt the write this probe needs |
| `post-write-walkthrough.sh` | Yes | `test-hooks.sh` (2 cases: production-change reminder, evidence-write silence) | script-level only | **Zero live-session coverage** |
| `instructions-loaded.sh` | Yes | `test-hooks.sh` (2 cases: JSONL log-line write, malformed-stdin fail-open-no-extra-line); `sdk_probe.py` `instructions_loaded` probe | script-level + end-user | None significant (its `os.path.realpath` symlink fix is specifically documented as validated by the live probe, per `VERDICT.md` trap #4) |
| `bash-write-snapshot.sh` | Yes | `test-hooks.sh` (2 cases: Bash-arm baseline recorded, non-Bash-arm silent) | script-level only | **Zero live-session coverage** — no `sdk_probe.py` probe names this script or its `PreToolUse`/`Bash` matcher |
| `bash-write-notice.sh` | Yes | `test-hooks.sh` (bash-detector suite: 8 named cases covering test-file/tamper/deletion/secret-leak NOTICE vs `cp -p`/`sed -i`/`touch -c`/no-op SILENT, plus a `PostToolUseFailure` event-echo case and a 2-parallel-call isolation case) | script-level only | **Zero live-session coverage** — this is the widest single test surface in `test-hooks.sh` by case count, and none of it is corroborated by a live host actually invoking it at the real `PostToolUse`/`PostToolUseFailure` events |

### Hook event keys (7, from `hooks.json`)

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| `SessionStart` | Yes | `verify-shipped-vs-active.py` (wiring); `test-hooks.sh` (script); `sdk_probe.py` `doctrine`/`instructions_loaded` (event fired, observed) | wiring + script + end-user | None significant |
| `Stop` | Yes | `verify-shipped-vs-active.py` (wiring); `test-hooks.sh` (script); `sdk_probe.py` `stop_guard` (event fired, observed) | wiring + script + end-user (event-level only, †) | Same script-attribution caveat as `stop-guard.sh` above |
| `SubagentStop` | Partial | `verify-shipped-vs-active.py` (wiring only — script named in `hooks.json` matches a file on disk) | wiring only | **No live-session probe in `sdk_probe.py` names `SubagentStop`** (grepped `require_hook_event` values in `PROBES`: only `"Stop"` and `"SessionStart"` appear) — whether this event actually fires when a subagent stops, in a real host, is entirely unproven |
| `PreToolUse` | Yes | `verify-shipped-vs-active.py` (wiring); `test-hooks.sh` (script, both `Write\|Edit` and `Bash` matchers) | wiring + script | No live-session probe observes `PreToolUse` firing directly (the `blocks_test_file`/`allows_normal_file` probes observe the *Write outcome*, not the hook event name itself) |
| `InstructionsLoaded` | Yes | `verify-shipped-vs-active.py` (wiring); `test-hooks.sh` (script); `sdk_probe.py` `instructions_loaded` (event fired, observed, with the JSONL-append disambiguation trap fixed) | wiring + script + end-user | None significant |
| `PostToolUse` | Partial | `verify-shipped-vs-active.py` (wiring); `test-hooks.sh` (script, via `bash-write-notice.sh`'s bash-detector suite) | wiring + script | **No live-session probe** — same as `SubagentStop`, `PostToolUse` never appears in any `require_hook_event` value in `sdk_probe.py` |
| `PostToolUseFailure` | Partial | `verify-shipped-vs-active.py` (wiring); `test-hooks.sh` (script, one dedicated case: failure-event echoes `PostToolUseFailure` correctly) | wiring + script | **No live-session probe** — same gap |

### Host / platform surfaces

| Subject | Has eval? | Which harness | Proof level | Gap |
|---|---|---|---|---|
| `extensions/proofpunk.ts` (OMP doctrine-guard extension) | **No** | none | none | Grepped every `tools/` harness for `proofpunk.ts`: zero matches outside `proofpunk-install.sh` (which only `cp`'s the file, never runs it) and `INSTALL.md` (docs). No test parses, type-checks, or executes this TypeScript file at all |
| `opencode/plugin/proofpunk.ts` | **No** | none | none | Same — zero matches for `opencode/plugin` in any harness; only `proofpunk-install.sh` copies it |
| `opencode/agents/*.md` (4: `end-user-validate.md`, `implement.md`, `proofpunk.md`, `scout.md`) | Partial | `verify-counts.py` (count only, `agents_oc`) | count only | Files are globbed only to produce a number for cross-checking prose; content/behavior when loaded by a real OpenCode agent host is entirely unevaluated |
| `omp/agents/*.md` (3: `end-user-validate.md`, `implement.md`, `scout.md`) | Partial | `verify-counts.py` (count only, `agents_omp`) | count only | Same gap as OpenCode agents |
| `agents/*.md` (3, Claude-native: `end-user-validate.md`, `implement.md`, `scout.md`) | Partial | `verify-counts.py` (count only, `agents_cc`) | count only | Same gap — no harness drives Claude Code's own subagent mechanism to prove these actually work when invoked |
| `build-site.py` (GitHub Pages generator) | **No** | none | none | No CI step, no test harness; only a manual preflight check for missing `yaml`/`pandoc` deps, no correctness check on generated output |
| `generate-themes.py` (theme pack renderer) | **No** | none | none | Determinism ("run twice → byte-identical") is documented as a *manual* check in `tools/AGENTS.md:39`; nothing automates or enforces it |
| `trace.py` (L2 run-trace substrate) | **No** | none | none | Confirmed by grep: not referenced by any of `test-hooks.sh`, `test-installer.sh`, `verify-orchestration.py`, `verify-citations.py`, `verify-harness-integrity.py`, `sdk_probe.py`, `verify-command-surface.py`, or `.github/workflows/gates.yml`. Its ~600 lines of hash-chaining/schema-validation/ledger-reconciliation logic have zero automated regression coverage; the one artifact demonstrating it works (`evidence/v3-release/l2-trace/proof-run.jsonl`) is a historical hand-run capture, not a repeatable gate |

## Open questions

- I did not independently re-run `test-hooks.sh`, `test-installer.sh`, `dry-run-install.sh`,
  `verify-citations.py`, `verify-router-links.py`, `verify-shipped-vs-active.py`, `verify-orchestration.py`,
  or `verify-command-surface.py` myself this session (only `gauge-report.py` and
  `verify-harness-integrity.py`, per the task's explicit ask to re-verify the specific claims named in the
  work order). Their PASS statuses above are therefore `[UNVERIFIED-BY-ME, cited from
  evidence/v3-release/run-20260907T013804Z-v3-recon/gates/*.log]` — i.e., trusted from the orchestrator's
  sealed baseline captures rather than independently reproduced, though I did cross-check every log's
  claimed behavior against the corresponding source code line-by-line and found no contradiction.
- For the 13 skills whose `sdk_probe.py` skill-load probe has a plugin-arm JSON artifact but no
  `-control.json` companion (`validation-plan`, `root-cause-debugging`, `full-functional-audit`,
  `visual-inspection`, `production-readiness`, `brainstorm`, `mobile-validation-runner`, `plan-hardening`,
  `prompt-forge` [direct probe only], `session-intent`, `stack-testing`, `tui-testing`,
  `ui-experience-audit`): I inferred "attributable by construction, not independently negative-tested" from
  `e2e-evidence/run-sdk-probes/VERDICT.md`'s own stated methodology ("The five skill probes marked `—`
  share the identical predicate as the four that were control-tested… their controls were not run, so they
  are attributable by construction rather than by a measured negative"). I did not re-run `sdk_probe.py`
  myself to verify this is still true post-F-001 (that would require live SDK/network access this lane did
  not attempt, consistent with the read-only/no-live-session scope of this recon phase).
- I did not attempt to determine whether `SubagentStop`/`PostToolUse`/`PostToolUseFailure`'s absence from
  `sdk_probe.py`'s `require_hook_event` set is a known, intentionally-scoped gap documented somewhere I
  didn't find, or a genuinely un-noticed coverage hole — I searched `VERDICT.md` and the module docstrings
  and found no explicit acknowledgment either way, so I report it as an observed gap without asserting
  intent.
