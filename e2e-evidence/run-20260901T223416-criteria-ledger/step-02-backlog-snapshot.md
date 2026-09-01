# proofpunk plugin — ranked improvements (P7 backlog)

Derived from five parallel audit lanes plus session mining, 2026-09-01.
Baseline: v2.2.0, branch `main` @ `327f883`, 18 skills / 6 commands / 3 agents / 7 hooks / 13 references.

Severity: BLOCKER = broken for a real user · MAJOR · MINOR · NIT.
Status: DONE = orchestrator personally verified · IN-FLIGHT = lane running · OPEN.

## The root cause behind most of these

Hand-maintained lists drift from their source of truth. Measured recurrences:
skill-count strings regressed 4× (`.planning/BUILD-PROMPT.md:103-105`); `evidence-guard.sh`
shipped registered-but-dead from v1.10.0 through v2.1.0 (commit `99c72fb`); the installer's
hook list drifted from `hooks.json` (fixed below). **Mitigation: derive, never restate.**

| # | Sev | Improvement | Evidence | Proof obligation (P8) | Status |
|---|-----|-------------|----------|----------------------|--------|
| 1 | BLOCKER | Installer derives hook copy + registration from `hooks.json` instead of two hardcoded lists. Previously `session-start.sh` was never copied and `SessionStart`/`InstructionsLoaded` never registered — a `--hooks` install silently shipped without doctrine injection or the observability tap. | installer had `hooks.json`=False, `session-start.sh`=False, SessionStart=False, InstructionsLoaded=False | fresh temp-HOME install: 7/7 scripts, 6 events, 8 registrations; rerun `diff_rc=0` | **DONE** |
| 2 | BLOCKER | `stop-guard.sh` role-blind scan. Lines 49-56 regex-matched raw JSONL with no `json.loads` and no `role` check: a user's own question triggered a block, and user words containing "screenshot"/"touchpoints" silenced the guard for a genuinely unproven assistant claim. | reproduced both directions by orchestrator | 6 cases: user-only silent, spoof blocks, proof+scout silent, no-proof blocks, malformed silent, missing silent | **DONE** |
| 3 | BLOCKER | Bash write bypass. The three PreToolUse guards register only under matcher `Write\|Edit`; `cat > f <<EOF`, `tee`, `sed -i`, `python -c open().write()` bypass all three plus `post-write-walkthrough.sh`. Guards read `tool_input.file_path`, absent on Bash payloads — a naive matcher addition fails open. | `hooks.json:40`; probe: guard returns rc=2 even with `tool_name:"Bash"`, proving the gate is purely the matcher | Bash heredoc writing `.test.ts` → rc=2; benign Bash write → rc=0; Write-path behavior unchanged | IN-FLIGHT |
| 4 | MAJOR | `stop-guard.sh` PROOF regex fires on bare "screenshot"/"verdict" with no disk-existence check — a claim citing no real file passes. | `stop-guard.sh:37`; probe SG-GAP rc=0 silent | claim naming a nonexistent path → blocks; claim naming a real captured artifact → silent | OPEN |
| 5 | MAJOR | `stop-guard.sh` SCOUT regex — same defect class, satisfied by the word "touchpoints" alone. | `stop-guard.sh:38` | prose-only scout → blocks; scout citing real files → silent | OPEN |
| 6 | MAJOR | No hook enforces the "no mocks or stubs" doctrine that `session-start.sh:7` asserts. `no-test-files.sh` gates by path only, so `src/gateway.ts` containing `class FakeGateway` passes untouched. Soft-warn heuristic, not a hard deny. | `session-start.sh:7` vs `no-test-files.sh:27-30` | production file with `class Fake*`/`jest.mock(` → warns; clean file → silent | OPEN |
| 7 | MAJOR | Doc drift: `tools/INSTALL.md:92,174` claims OpenCode ships "1 agent"; the tree has 4. `proofpunk-v2-release-report.md:18` cites non-existent top-level `opencode/agents/`, `omp/agents/` paths and a stale count of 3. | measured `ls plugins/proofpunk/opencode/agents/` = 4 | every count in the doc re-measured and matching the tree | IN-FLIGHT |
| 8 | MAJOR | `commands/rate-prompt.md:44` and the OpenCode sibling both claim `--report-only` composes with `--out`, contradicting `prompt-forge/SKILL.md:173-175` which rejects that exact pair. The false claim propagates into `docs/commands.html:191-192`. | three-way citation | all three files quoted post-edit and in agreement | IN-FLIGHT |
| 9 | MAJOR | Retroactive changelog note: `evidence-guard.sh` shipped dead in every `--hooks` install v1.10.0→v2.1.0. Users on those installs must re-run `--hooks` to activate secrets enforcement. No user-facing note exists. | `e2e-evidence/run-20260827T213000-installer-hook-registration/verdict.json:56` | note present in README/changelog naming affected versions and the remedy | OPEN |
| 10 | MEDIUM | `tools/test-hooks.sh` cannot catch #2 or #3 no matter what payloads are added: every case invokes scripts directly, never exercising `hooks.json`'s matcher, and no fixture puts CLAIM/PROOF/SCOUT words on a `role:"user"` line. 23/23 passed while both BLOCKERs were live. | `test-hooks.sh:31-38`, `:186-200` | new cases fail against pre-fix scripts and pass against fixed ones | OPEN |
| 11 | MEDIUM | `evidence-guard.sh:25` and `capture-guard.sh:27` independently duplicate the same `in_evidence` regex — a future evidence-dir convention change can silently diverge them. | both files | both guards classify an identical path set identically | OPEN |
| 12 | MEDIUM | OpenCode `proofpunk-rate-prompt.md` `argument-hint` omits `--ship-below-threshold` that the skill supports and the Claude Code sibling advertises. | frontmatter vs `commands/rate-prompt.md:3` | both command docs advertise the same flag set as the skill | IN-FLIGHT |
| 13 | MEDIUM | No CI gate runs `tools/verify-orchestration.py`; it is a manual pre-release step. The DAG has drifted silently before and the verifier caught it. | `proofpunk-hooks-release-report.md:35-37`; `CLAUDE.md:14-19` | gate runs and fails on an induced DAG break | OPEN |
| 14 | MINOR | Only v2.1.0 and v2.2.0 are real git tags; v1.x/v2.0.x exist solely as commit-message labels, so the manifest's tag-vs-HEAD trust mechanism does not extend backward. | `git tag` | documented or tags created | OPEN |
| 15 | MINOR | 57 `e2e-evidence/run-*` dirs split across two naming conventions (32 timestamped, 25 bare) — the bare ones cannot be ordered without opening each verdict. | `ls -d e2e-evidence/run-*` | convention documented; new runs uniformly timestamped | OPEN |
| 16 | MINOR | `references/ci-gates.md` is cited only by the router's descriptive table, never loaded mid-workflow by any executing skill — unlike all 12 other references. Wire it into a workflow step or demote it. | citation map | reference either loaded by a named skill step or removed from the owns-table | OPEN |
| 17 | MINOR | `assets/rules/evidence-contract.md` (15 lines) and `references/evidence-contract.md` (131 lines) share a filename with zero verbatim overlap — two independent doctrine documents one rename away from confusion. | unified diff: all lines differ | one renamed, or a header in each naming its distinct role | OPEN |
| 18 | NIT | `evidence/v2.2.0-release/manifest.json:39` cites `evidence/AGENTS.md:22` for the capture-immutability rule; that rule is at line 20 (line 22 is the adjacent secrets rule). Historical manifest — annotate rather than edit. | off-by-two | corrected citation or an annotation noting the drift | OPEN |

## Architecture note — the head skill

The operator asked for "one massive skill that the head will link with everything else up
correctly." Measured finding: `skills/proofpunk/SKILL.md` (83 lines) **already routes to all 17
other skills** — verified by regex over the router against the directory listing, 17/17 matched,
0 orphans — with a per-skill handoff column and a 13-row shared-doctrine table. Per operator
decision D1, the 18 skills stay separate and independently invocable; the router is the head.
No merge is required. The real gaps were the layers *below* the router (#1-#3), not the router.

## Selected implementation set (≥10, mapped to P7/P8)

Committed this run: **#1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11, #12** — twelve items, each
with the proof obligation stated above. #13-#18 are recorded, ranked, and deliberately deferred
as MINOR/NIT with no user-visible breakage; they are not silently dropped.
