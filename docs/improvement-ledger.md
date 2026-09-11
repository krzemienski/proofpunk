# Improvement ledger — re-measured at `93c479d`

Measured: 2026-09-04 | Repo HEAD at start of this lane: `93c479de800fff7e3ceb0be5ccf96f4d494fdaee`.
Method: glob + parse of `plugins/proofpunk/{skills,references,commands,opencode/commands,hooks}`, full read of `hooks.json`, `git tag -l`, directory listing of `e2e-evidence/run-*`. No status label was copied from `.planning/plugin-improvements.md`.

## Derived canon (recomputed, never restated)

| Thing | Count | Derivation |
|---|---|---|
| Skills | **18** | `plugins/proofpunk/skills/*/SKILL.md` |
| Shared references | **15** | `plugins/proofpunk/references/*.md` (the work-order's 13 omitted `run-trace-schema.md`; a reference has been added since this lane's `14` measurement) |
| Commands (Claude Code) | **6** | `plugins/proofpunk/commands/*.md` |
| Commands (OpenCode) | **6** | `plugins/proofpunk/opencode/commands/*.md` |
| Hook scripts | **10** | `plugins/proofpunk/hooks/*.sh` |
| Hook event keys | **7** | top-level keys of `hooks.json` `.hooks` |
| Hook registrations | **12** | every `command` object under those events |
| Agents | **3 / 4 / 3** | `agents/` · `opencode/agents/` · `omp/agents/` |
| Real git tags | **2** | `git tag -l` → `v2.1.0`, `v2.2.0` |
| `e2e-evidence/run-*` dirs | **72** | 52 timestamped `run-YYYYmmddTHHMMSS-*`, 20 bare |

Defect classes are those in `docs/commit-archaeology.md` (Class 1 harness-cannot-fail, Class 2 hardcoded-count drift, Class 3 shipped-not-wired, Class 4 claim-above-proof).

## The 18 backlog items

| # | Status at `93c479d` | Evidence `file:line` | Class |
|---|---|---|---|
| 1 | **CLOSED** | `tools/proofpunk-install.sh:409-429` copies scripts named by `hooks.json`; `:468` registers events from the same parse | 2, 3 |
| 2 | **CLOSED** | `plugins/proofpunk/hooks/stop-guard.sh:125-137` (`is_assistant_line`); `:208` skips unparseable lines | 1 |
| 3 | **PARTIAL** (by design) | `plugins/proofpunk/hooks/hooks.json:40` deny guards stay on `Write\|Edit`; `:60` Bash matcher is `bash-write-snapshot.sh` only. Detection, not prevention. | 1 |
| 4 | **CLOSED** | `stop-guard.sh:91-99` `PROOF_NONPATH` requires curl+http(s)+200 or `fresh_evidence validate`+OK; `:99` `PROOF_PATH` requires `e2e-evidence/` or `evidence/` | 1 |
| 5 | **CLOSED** | `stop-guard.sh:108` `PATH_SHAPED`; `:139-145` matches extracted assistant text, never raw JSON (cwd envelope) | 1 |
| 6 | **CLOSED** | `plugins/proofpunk/hooks/no-test-files.sh:46-65` warns on `class Fake*` / `jest.mock(`; still a warn, not a deny | 1 |
| 7 | **CLOSED** | `tools/INSTALL.md:58` and `:140` say OpenCode ships **4 agents** (matches glob) | 2 |
| 8 | **CLOSED** | `plugins/proofpunk/commands/rate-prompt.md:42-45` and `opencode/commands/proofpunk-rate-prompt.md:18-21` both reject `--report-only`+`--out`, matching `prompt-forge/SKILL.md:173-175` | 2 |
| 9 | **CLOSED** | `README.md:44-48` names v1.10.0–v2.1.0, `evidence-guard.sh`, and the `--hooks` re-run remedy | 3, 4 |
| 10 | **CLOSED** | `tools/test-hooks.sh` (60 cases at the hooks-lane after-arm); role-spoof / fabricated-path / bare-keyword cases exist. Direct script invocation still cannot see `hooks.json` matchers — recorded as a remaining Class 1 limit, not a reopen of #10 | 1 |
| 11 | **CLOSED** at source; **detector added this lane** | regex literals are byte-identical at `evidence-guard.sh:29` and `capture-guard.sh:31`; `tools/verify-shipped-vs-active.py:200-217` now asserts that identity | 2 |
| 12 | **CLOSED** | `opencode/commands/proofpunk-rate-prompt.md:3` argument-hint includes `--ship-below-threshold` | 2 |
| 13 | **CLOSED** | `.github/workflows/gates.yml:56-57` runs `verify-orchestration.py` unpiped | 3 |
| 14 | **CLOSED** | `README.md:39-42` documents that only `v2.1.0`/`v2.2.0` are real tags; `git tag -l` this session printed exactly those two | 2 |
| 15 | **CLOSED** | `e2e-evidence/AGENTS.md:16-26` documents the timestamped convention and that 20 historical bare names stay immutable. Live count at this measurement: **72** run dirs (52 timestamped / 20 bare), not the 57/32/25 figure written at an earlier HEAD | 2 |
| 16 | **CLOSED this lane** | Before: `run-trace-schema.md` shipped, cited by no `SKILL.md`. After: `plugins/proofpunk/skills/proofpunk/SKILL.md:99` and `end-user-testing/SKILL.md:133-135`. `python3 tools/verify-router-links.py` rc=0, `doctrine_refs=14 all_resolved=true` at time of run (current disk count: **15**) | 3 |
| 17 | **CLOSED** | `plugins/proofpunk/assets/rules/evidence-contract.md:10-15` names itself the path-scoped hygiene rule and points at `references/evidence-contract.md` as the doctrine. Same filename, distinct roles, headers present | 2 |
| 18 | **VOID** | Premise was false. `evidence/AGENTS.md:22` **is** the capture-immutability rule (`:24` is secrets). `evidence/v2.2.0-release/manifest.json:39` citation is correct. Confirmed by reading those lines this session | 4 (the original report of a defect was itself a Class 4 overclaim) |

## Improvements implemented this lane

Permanent detectors beat one-off repairs. Class 2 (`tools/verify-counts.py`) is owned by LaneDocumentation and was not authored here; it is wired into CI from this lane so the shipped-vs-active check can see it.

| ID | What | `file:line` |
|---|---|---|
| I1 | Class 1 detector | `tools/verify-mutation-artifact.py:1-175` |
| I2 | Class 3 detector | `tools/verify-shipped-vs-active.py:1-229` |
| I3 | Class 4 detector | `tools/verify-proof-vocab.py:1-140` |
| I4 | CI wiring of I1–I3 + router-links + counts | `.github/workflows/gates.yml:84-97` |
| I5 | `run-trace-schema.md` cited from the router | `plugins/proofpunk/skills/proofpunk/SKILL.md:99` |
| I6 | `run-trace-schema.md` loaded by an executing skill | `plugins/proofpunk/skills/end-user-testing/SKILL.md:133-135` |
| I7 | `in_evidence` regex identity (item 11 detector) | `tools/verify-shipped-vs-active.py:200-217` |
| I8 | tools index lists the four class detectors | `tools/AGENTS.md:20-23` |
| I9 | Class 1 matcher is per-line, never DOTALL | `tools/verify-mutation-artifact.py:134-136` |
| I10 | Live SDK drivers excluded from hermetic CI demand | `tools/verify-shipped-vs-active.py:47,148` |

Plugin manifests (`.claude-plugin/plugin.json`, `.omp-plugin/plugin.json`, `package.json`) still name `"functional validation"` in their description string. Main assigned that three-file fix to LaneDocumentation. Not touched.

## Measured-success table

Every before/after pair is unpiped (`cmd` then a sibling `.rc` written from the process returncode, never a pipeline). Captures live under `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-improvements/`.

| Item | What changed (`file:line`) | Before-arm | After-arm | Verdict |
|---|---|---|---|---|
| I1 Class 1 detector | `tools/verify-mutation-artifact.py` NEW | `step-02-mutation-artifact-before.log` rc=3, names the three NEW files | `step-14-mutation-artifact-after-tighten.log` rc=0; mutation `step-19-class1-mutated-new-harness.log` rc=1 names `verify-dummy-mutation.py`; restore `step-20-class1-restored.rc`=0 | **PASS** (script-level) |
| I2 Class 3 detector | `tools/verify-shipped-vs-active.py` NEW | `step-04-shipped-vs-active-tight-before.log` rc=2, `shipped-not-active: run-trace-schema.md` plus `ci-unwired` | `step-10-shipped-vs-active-after.log` rc=0; mutation `step-21-class3-mutated-uncited-ref.log` rc=1 names `_mutation-uncited.md`; restore `step-22-class3-restored-after-dummy.rc`=0 | **PASS** (script-level) |
| I3 Class 4 detector | `tools/verify-proof-vocab.py` NEW | `step-05-proof-vocab-tight-before.log` rc=1, 9 uncited hits | `step-11-proof-vocab-after.log` rc=0; mutation `step-17-class4-mutated-bare-DONE.log` rc=1 names `tools/AGENTS.md:57 STATUS: DONE`; restore `step-18-class4-restored.rc`=0 | **PASS** (script-level) |
| I4 CI wiring | `.github/workflows/gates.yml:84-97` | `step-04-shipped-vs-active-tight-before.log` `ci-unwired: verify-mutation-artifact.py, verify-proof-vocab.py, verify-router-links.py, verify-shipped-vs-active.py` | `step-10-shipped-vs-active-after.log` `PASS ci-wiring` | **PASS** (script-level) |
| I5+I6 run-trace-schema cite | `proofpunk/SKILL.md:99`, `end-user-testing/SKILL.md:133-135` | `step-04-…` `shipped-not-active: run-trace-schema.md` | `step-06-router-links-after-cite.log` rc=0 `doctrine_refs=14 all_resolved=true`; `step-10-…` `refs disk=14 cited=14` (captured-log values; current disk count is **15**) | **PASS** (script-level) |
| I7 in_evidence identity | `verify-shipped-vs-active.py:200-217` | (no before: the two regexes were already identical; the check is new) | `step-10-…` `PASS in_evidence-regex '(^|/)(e2e-evidence\|evidence)(/|$)'` | **PASS** (script-level). Discriminating mutation would require editing `hooks/*.sh`, which LaneHooksDoctrine owns — **not mutation-proven against a diverge**. |
| I8 tools/AGENTS.md | `tools/AGENTS.md:20-23` | HEAD `git show 93c479d:tools/AGENTS.md` has no Class 1/3/4/2 rows | file now lists all four; `step-23-proof-vocab-after-agents-restore.rc`=0 | **PASS** (script-level) |
| I9 Class 1 per-line matcher | `verify-mutation-artifact.py:134-136` | `step-12-mutation-artifact-after-premut.log` rc=1 was a *false* FAIL on sibling `verify-counts.py` plus a DOTALL self-certify path | `step-14-…` rc=0, per-line, sibling printed `UNPROVEN-SIBLING` | **PASS** (script-level) |
| I10 live-driver exclusion | `verify-shipped-vs-active.py:47,148` | putting `verify-command-surface.py` in CI was attempted then reverted — that file drives `sdk_probe.py` (live SDK), not hermetic | after-arm `ci harnesses=11` excludes it; `sdk_probe.py` remains the documented CI gap in `gates.yml:17-21` | **PASS** (script-level) |
| #16 originally OPEN | see I5+I6 | `step-01-shipped-vs-active-before.log` (wide regex, then tightened in step-04) | same as I5+I6 | **PASS** (script-level) |

An earlier Class 3 mutation (drop the router row only, `step-15-class3-mutated-drop-trace-cite`) stayed green because `end-user-testing/SKILL.md` still cited the file. That arm proves nothing about the router row; the dummy-file arm (`step-21`) is the discriminating one. Recorded, not hidden.

## Proved vs attempted

| | Count | Notes |
|---|---|---|
| Attempted | **12** | I1–I10 plus (a) plugin-manifest dead-name fix, halted by Main; (b) adding `verify-command-surface.py` to hermetic CI, reverted after reading its header (`tools/verify-command-surface.py:1-27` drives live SDK) |
| Proved | **10** | I1–I6, I8–I10, and #16. I7 is implemented and green but not mutation-proven (would require editing a sibling-owned hook) |
| Halted / reverted | **2** | plugin.json trio (LaneDocumentation); live command-surface CI step |

## Open / UNRESOLVED

- **#3** remains PARTIAL by design. Bash-write prevention is out of scope; snapshot+notice is the contract.
- **`PROOF_NONPATH` curl form** still cannot confirm the HTTP request was made (`stop-guard.sh:88-94`; archaeology + hooks-lane map). Rule 10 forbids a shell-parse close.
- **`sdk_probe.py` / `verify-command-surface.py`** are live-session harnesses. Class 1 prints `UNPROVEN-LIVE` for `sdk_probe.py`. They are not hermetic CI. Gauge #4 is LaneCommandSurface's artifact.
- **`tools/verify-counts.py`** (Class 2) is sibling-owned. Class 1 prints `UNPROVEN-SIBLING` until that lane lands a mutation artifact. This lane wired it into `gates.yml:96-97`.
- **Dead `"functional validation"` string** in `.claude-plugin/plugin.json:4` and `.omp-plugin/plugin.json:4` — LaneDocumentation. `package.json:5` does **not** carry that phrase.
- **Shared-reference count is 15** (was 14 at this lane's measurement, up from the work-order's 13). `run-trace-schema.md` was the first extra file; another reference has been added since. Class 2 (sibling) must accept the current disk count or it will FAIL live docs that are now correct.
- **I7 in_evidence identity** is not mutation-proven. The two literals match today; a diverge would require editing `hooks/*.sh`.
- Router-row-only Class 3 mutation (`step-15`) was non-discriminating. Do not cite it as proof.
- This ledger is script-level. No live agent session was driven.
