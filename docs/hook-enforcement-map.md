# Hook enforcement map

Derived 2026-09-04 from a parse of `plugins/proofpunk/hooks/hooks.json`
(`sha256:e0227d5b825d2d5f943722e4a41c70914b4d7e116dff65b838d6b39457c2ec92`,
2707 bytes) plus a full read of the 9 on-disk `.sh` files. Counts below
are computed, never retyped. Parse dump:
`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-hooks/derived-hooks-parse.json`.

Host semantics that constrain every row: `docs/skill-canon.md` §2.4–§2.6
(`PostToolUse` / `PostToolUseFailure` **cannot deny** — the tool already
ran; `PreToolUse` is the only write-path deny surface; plugin hooks
**merge** with user/project settings, they do not replace them).

## Derived inventory

| Quantity | Value | How derived |
|---|---|---|
| Event keys | **7** | `len(json["hooks"])` → `SessionStart`, `Stop`, `SubagentStop`, `PreToolUse`, `InstructionsLoaded`, `PostToolUse`, `PostToolUseFailure` |
| Registrations | **11** | count of `{type,command,timeout}` objects nested under every group |
| Distinct scripts registered | **9** | unique basename of `hooks/<name>.sh` in those 11 commands |
| On-disk `.sh` files | **9** | `plugins/proofpunk/hooks/*.sh` glob; set-equal to the 9 registered names |
| Scripts registered twice | **2** | `stop-guard.sh` ×2, `bash-write-notice.sh` ×2 |

No script is registered without an on-disk file. No on-disk `.sh` is
unregistered.

## Event key → registration → script

`Can deny?` is the host's decision-control table, not this plugin's
ambition. `Observe` is what the script actually reads. `Doctrine` is the
rule it enforces **when it fires**. Twice-registered scripts have a Why
column.

| # | Event | Matcher | Script | Timeout | Can deny? | Observes | Does not observe | Doctrine enforced | Twice? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `SessionStart` | `startup\|resume\|clear` | `session-start.sh` | 5 | No (injects `additionalContext` only; ignores stdin) | nothing — hardcoded JSON | tool calls, transcripts, disk | Advertises doctrine into session context. Does not enforce it. | no |
| 2 | `Stop` | (none) | `stop-guard.sh` | 10 | Yes — `{"decision":"block","reason":…}` continues the turn | last 40 JSONL lines of `transcript_path`; assistant-role text only; on-disk `e2e-evidence/` / `evidence/` files under `cwd`; `PROOF_NONPATH` regex | live HTTP; whether a cited curl actually ran; subagent transcripts (those arrive on #3); tool_use records that are not assistant text | Unproven completion claim (claim ∧ ¬proof) and claim+proof-without-scout | **yes — Stop + SubagentStop** |
| 3 | `SubagentStop` | (none) | `stop-guard.sh` | 10 | Yes — same contract as #2 | the **subagent** transcript named in that event's stdin | the parent session transcript | Same as #2, for a subagent that can claim completion independently of the parent | **yes — same script as #2** |
| 4 | `PreToolUse` | `Write\|Edit` | `no-test-files.sh` | 5 | Yes — exit 2 + stderr on test-shaped **path**. Content heuristic is warn-only (exit 0) | `tool_input.file_path`; `content` / `new_string` | Bash-authored writes; files already on disk; `old_string` of an Edit | No new test artifacts on the Write/Edit path. Soft warn on `class Fake*/Mock*/Stub*`, `jest.mock`, `unittest.mock`, `sinon.stub`, `@patch`, `MagicMock`, `raise NotImplementedError`, `TODO: implement` | no |
| 5 | `PreToolUse` | `Write\|Edit` | `evidence-guard.sh` | 5 | Yes — exit 2 when path is under `(e2e-)?evidence` **and** payload matches a secret shape | `file_path` + `content`/`new_string` | Bash-authored writes; secrets written outside evidence dirs (explicitly out of lane) | Secret hygiene for evidence dirs | no |
| 6 | `PreToolUse` | `Write\|Edit` | `capture-guard.sh` | 5 | Yes — exit 2 when the target already exists, is under evidence, and has a capture extension | `file_path` + `os.path.exists` | Bash overwrites (`>` / `cp` / `mv`); sidecar `.md`/`.json` (authored, allowed); brand-new captures | Captures are immutable once written | no |
| 7 | `PreToolUse` | `Bash` | `bash-write-snapshot.sh` | 10 | **No** — always exit 0, no stdout. A deny here would re-open the abandoned shell parser | `cwd` tree, hashed; scoped to evidence dirs + test-shaped paths; cap 4000 files | the Bash command text (deliberately unread) | None by itself. Leaves a per-`session_id:tool_use_id:cwd` baseline for #10/#11 | no |
| 8 | `InstructionsLoaded` | (none) | `instructions-loaded.sh` | 5 | No — always exit 0 | `file_path`/`filePath`, `load_reason`/`loadReason`, `cwd` | whether the loaded file's contents match `/proofpunk:install` output | Observability tap only (`~/.claude/proofpunk-loads.jsonl`) | no |
| 9 | `PostToolUse` | `Write\|Edit` | `post-write-walkthrough.sh` | 5 | **No** (host: tool already ran). Speaks via `additionalContext` | `file_path` | whether the subsequent walkthrough actually happens | Reminds: production-code change ⇒ drive the real system next. Silent on evidence/docs/plans/hooks | no |
| 10 | `PostToolUse` | `Bash` | `bash-write-notice.sh` | 10 | **No** (host: tool already ran). NOTICE via `additionalContext` | post-command hashes of protected paths vs the #7 baseline | the Bash command text; writes outside evidence/test paths; a call whose baseline was truncated (`complete:false` → coverage-OFF notice) | Detects (does not undo) Bash bypass of #4/#5/#6: test files, capture tamper, evidence delete, secret-shaped evidence content | **yes — PostToolUse + PostToolUseFailure** |
| 11 | `PostToolUseFailure` | `Bash` | `bash-write-notice.sh` | 10 | **No** (host: tool already ran, then failed). Same NOTICE, `hookEventName` echoed as `PostToolUseFailure` | same as #10 | PreToolUse denials (this event does not fire for rejected-before-execution calls — skill-canon §2.4) | Same as #10 for a Bash call that started and then failed | **yes — same script as #10** |

### Why the two double registrations exist

**`stop-guard.sh` on Stop and SubagentStop.** A subagent can emit "done /
complete / shipped" on its own transcript. Registering only on `Stop`
would let a subagent's unproven completion land while the parent is still
running. Same heuristic, different `transcript_path`. Driven at
script-level with `hook_event_name` in stdin; live `SubagentStop` is
UNVERIFIED (the `stop_guard` sdk probe requires the `Stop` event, not
`SubagentStop`).

**`bash-write-notice.sh` on PostToolUse and PostToolUseFailure.** Effect
hashing has to run whether the Bash call exited 0 or failed after
starting — a `rm` of an evidence capture that then returns non-zero is
still a deletion. The script reads `hook_event_name` and echoes it so
the two events are distinguishable in `additionalContext`. It cannot
deny on either event (skill-canon §2.5).

## Fail-open paths (driven this lane)

### `stop-guard.sh` — now distinguishable

Pre-fix (`sha256:9840595c3a0eb32120ec667b587e03fed627727f936733dafc0e85cea9c907a8`,
HEAD `73e928e`): missing/unreadable transcript, malformed stdin, or
absent `python3` all took `exit 0` with empty stdout — identical to "the
heuristic ran and found nothing." Reproduction:

- `PATH=/bin` (no `python3`) → empty stdout, rc=0
- `transcript_path=/nonexistent/x.jsonl` → empty stdout, rc=0

Post-fix (`sha256:389e11a2a3e86b6a573601866d9d599d4022e04fc92a6016c787045842f32106`):
those paths still **exit 0** (Stop cannot be blocked on an unread
transcript) but emit
`hookSpecificOutput.additionalContext` containing `enforcement OFF (<reason>)`.
A silent stop now means the heuristic actually ran. Reasons driven:

| Reason | Case in `tools/test-hooks.sh` | Pre-fix | Post-fix |
|---|---|---|---|
| `transcript-missing-or-unreadable` | missing path + chmod-000 file | silent | `enforcement OFF` |
| `python3-not-found` | `PATH=/bin` | silent | `enforcement OFF` |
| `stdin-json-unreadable` | payload `not-json` | silent | `enforcement OFF` |

Mutation proof (named mutation `silent-missing-transcript` restored the
pre-fix `exit 0` on the missing/unreadable branch only): baseline rc=0
PASS=60 → mutated rc=2 PASS=58 FAIL=2 (missing-transcript + unreadable
transcript, both named) → restored rc=0 PASS=60, stop-guard.sh
byte-identical to the pre-mutation copy, baseline log
byte-identical to restored log.
`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-hooks/mutation/`.

### `PROOF_NONPATH` — request never confirmed

`stop-guard.sh` credits proof for
`curl <http(s)-url> … 200` or `fresh_evidence.py validate … OK` matched
against **assistant transcript text**. Tightened earlier to require an
`https?://` endpoint plus `200` (bare `"validate OK"` is blocked — case
25). The guard still cannot tell whether that curl ran. A typed sentence
`curl https://api.example/health returned 200` with no network activity
stays silent (case 25c). Closing this by parsing the Bash command is
forbidden (binding doctrine rule 10; an earlier parser falsely blocked
`cp -p`, `mv -f`, `touch -c`, `sed -i -e`). Honest limitation, not a
fix candidate.

### `no-test-files.sh` content heuristic — soft warn, not deny

The script already gated by PATH (`*.test.*`, `__tests__/`, `/tests?/`,
…). A production file `src/gateway.py` containing `class FakeGateway`
passed untouched while `session-start.sh` asserted "no mocks or stubs."

Decision: a **soft warn** (stderr, exit 0) on mock/stub markers in
Write/Edit **content**, never a hard deny. A deny on `class Fake*`
would block legitimate domain names. Markers: `class Fake/Mock/Stub*`,
`jest.mock(`, `unittest.mock`, `sinon.stub(`, `@patch(`, `MagicMock(`,
`raise NotImplementedError`, `TODO: implement`. First hit only.

This heuristic was already in HEAD `73e928e`
(`sha256:9d5d65f99490d8a7b145ada550791c90d6ba1b8bd48361fcd166ed9a69db703c`).
This lane added the discriminating cases and mutation-proved them: named
mutation `silent-mock-content` (skip `MOCK_MARKERS` loop) → exactly one
FAIL (`no-test-files FakeGateway warn missing`) → restore byte-identical,
logs identical.
`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-hooks/mutation-mock-warn/`.

## Doctrine injected vs doctrine enforced

`session-start.sh` additionalContext (verbatim):

> Proofpunk is installed. Doctrine: execution logic over gate logic —
> decompose into tasks and execute each to completion; end-user testing
> is the only PASS (unexecuted checks are UNVERIFIED); no mocks or stubs;
> malformed input must fail clearly and safely. Commands:
> /proofpunk:implement, /proofpunk:verify, /proofpunk:install,
> /proofpunk:truth-audit, /proofpunk:rate-prompt, /proofpunk:forge-prompt.

Shared references add the Iron Rule, capture immutability, secret
hygiene, scout-before-write, "test runners are never validation",
fresh-evidence naming, and "never parse shell to decide a deny."

### Enforced (driven at script-level this lane)

| Rule | Hook | Strength |
|---|---|---|
| Unproven completion is not done | `stop-guard.sh` (#2/#3) | hard block (decision:block) |
| Scout record required alongside proof | `stop-guard.sh` | hard block |
| No new test files on Write/Edit | `no-test-files.sh` | hard deny (exit 2) |
| Mock/stub **content** on a production path | `no-test-files.sh` | **warn only** (exit 0) |
| Secrets not written into evidence via Write/Edit | `evidence-guard.sh` | hard deny |
| Existing captures not overwritten via Write/Edit | `capture-guard.sh` | hard deny |
| Bash bypass of the three Write/Edit guards | `#7 + #10/#11` | **notice only** (cannot deny; write already happened) |
| Production Write/Edit ⇒ walkthrough reminder | `post-write-walkthrough.sh` | reminder only |
| Doctrine visible at session start | `session-start.sh` | injection only |
| Memory-load tap | `instructions-loaded.sh` | log only |

### Unenforced gaps (explicit)

Nothing below is claimed enforced. Several cannot be closed without
violating rule 10 or the host's PostToolUse-cannot-deny table.

1. **Execution logic over gate logic / decompose-into-tasks.** Injected.
   No hook inspects a task graph.
2. **Unexecuted checks are UNVERIFIED.** `stop-guard` only fires on a
   completion-claim regex, not on a skipped validation step with no claim.
3. **Malicious/malformed tool input must fail clearly.** Session-start
   asserts it. No hook validates tool schemas.
4. **Advertised `/proofpunk:*` commands exist and work.** No hook. Lane
   Command Surface owns that gauge.
5. **The AI personally drove the real system (end-user-actor.md).**
   `stop-guard` accepts an on-disk evidence path or a typed curl+200. It
   does not require an MCP/browser/CLI actor.
6. **Test-runner output is never validation.** An assistant can cite
   `e2e-evidence/…/pytest.log` and satisfy proof. No hook distinguishes
   regression-rail files from end-user captures.
7. **Fresh-evidence naming** (`e2e-evidence/run-<ISO>-<slug>/step-NN-…`).
   Any file under `e2e-evidence/` or `evidence/` that exists on disk
   counts. No timestamp/run-dir/step-NN check.
8. **Stale build-cache warning** (`.next`, `.turbo`, `DerivedData`). No hook.
9. **Bash write bypass is unpreventable** without parsing shell. Snapshot
   + notice detect after the fact. `cp -p` / `sed -i -e` / `touch -c`
   against non-protected paths stay silent by design.
10. **`PROOF_NONPATH` does not confirm the HTTP request.** See above.
11. **Mocks already on disk, or introduced via Bash.** Content warn is
    Write/Edit only. `class FakeGateway` created by `cat > src/x.py`
    is at most a Bash-notice if the path looks like a test file.
12. **Scout is a keyword + path-shaped token**, not a real scout pass.
    `Scout context summary: touchpoints src/cart.ts` satisfies it.
13. **Never-pipe-exit-code, mutation-prove-every-gate, derive-never-restate.**
    Process doctrine. No hook.
14. **`SubagentStop` live-session fire.** Script-level only this lane.
15. **Plugin hooks merge, they do not win.** A user `settings.json`
    PreToolUse on `Write|Edit` runs **in addition to** these, in
    parallel (skill-canon §2.6). A project that disables matching is
    outside this plugin.

## Harness

`bash tools/test-hooks.sh` against this tree: **rc=0, PASS=60, FAIL=0**.
Baseline captured before this lane's harness additions: **PASS=50, rc=0**
(`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-hooks/baseline/step-00-test-hooks.log`).
After: **PASS=60** (same path `after/step-01-test-hooks.log`). Strictly
higher: 50 → 60.

New cases that FAIL against the pre-fix `stop-guard.sh` and PASS against
the fixed one (pre-fix hooks dir, current harness: rc=4, FAIL=4):

- stop-guard announces fail-open on missing transcript
- stop-guard announces fail-open on missing python3
- stop-guard announces fail-open on unreadable transcript
- stop-guard announces fail-open on malformed stdin

New cases that FAIL against a `MOCK_MARKERS`-stripped `no-test-files.sh`
and PASS against HEAD (mutation-mock-warn ARM2: rc=1, FAIL=1):

- no-test-files warns on FakeGateway in production content

Every one of the 9 scripts has a block-shaped arm and an allow arm
captured with unpiped rc under
`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-hooks/per-script/`.
Scripts that structurally cannot deny (`session-start`, `instructions-loaded`,
`bash-write-snapshot`, `post-write-walkthrough`, `bash-write-notice`) use
"did work / spoke" vs "silent no-op" as the two arms — claiming a deny
there would be a false claim against skill-canon §2.5.

## Live-session vs script-level proof

`tools/sdk_probe.py` probes this lane is required to RUN (read-only; Lane
Command Surface owns the file): `stop_guard`, `instructions_loaded`,
`blocks_test_file`, `allows_normal_file`, `doctrine`.

Driven this lane after LaneCommandSurface released the live lock
(cwd `lane-hooks/live/probe-cwd`). Unpiped rc + JSON stdout under
`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-hooks/live/`.
This SDK session's available tools were `ListAgents`, `SendMessage`,
`Skill`, `TaskStop`, `Workflow` — **no Write**. That is why the two
Write-path probes could not attempt a write.

| Probe | rc | `pass` | What was actually observed |
|---|---|---|---|
| `doctrine` | 0 | true | Reply starts `Proofpunk is installed. Doctrine: execution logic`. SessionStart stdout contains the same additionalContext. **PASS live** for injection. |
| `instructions_loaded` | 0 | true | `loads_appended` + `loads_this_run`; 62 new JSONL lines, first cwd is this run's probe-cwd. **PASS live** for the tap. Note: the probe's `require_hook_event` is `SessionStart`, not `InstructionsLoaded` — it does not prove the InstructionsLoaded *event name* fired. |
| `stop_guard` | 0 | true | Stop hook_run stdout is `{"decision": "block", "reason": "Proofpunk: a completion was claimed without a cited end-user evidence artifact…"}`. That is this plugin's script, not a generic Stop event. **PASS live** for Stop-path enforcement. |
| `blocks_test_file` | 1 | false | `write_attempted: false`. Model: "No Write tool in this session." File absent is not a deny. **UNVERIFIED live** (probe cannot fire PreToolUse:Write here). |
| `allows_normal_file` | 1 | false | Same missing-Write blocker; `artifact_exists: false`. **UNVERIFIED live**. |

| Hook | Script-level (this lane) | Live-session (`sdk_probe.py`, this run) |
|---|---|---|
| `session-start.sh` | PASS | **PASS** — `doctrine` rc=0, SessionStart stdout is proofpunk additionalContext (`live/step-01-doctrine.json`) |
| `stop-guard.sh` (Stop) | PASS | **PASS** — `stop_guard` rc=0 and stdout is this plugin's `decision:block` (`live/step-05-stop_guard.json`) |
| `stop-guard.sh` (SubagentStop) | PASS (same script) | no probe exists — **UNVERIFIED** |
| `no-test-files.sh` | PASS | **UNVERIFIED live** — SDK session has no Write tool, so PreToolUse:Write never ran (`live/step-03-blocks_test_file.json`, `live/step-04-allows_normal_file.json`) |
| `evidence-guard.sh` | PASS | no probe — **UNVERIFIED live** |
| `capture-guard.sh` | PASS | no probe — **UNVERIFIED live** |
| `bash-write-snapshot.sh` | PASS | no probe — **UNVERIFIED live** |
| `bash-write-notice.sh` | PASS | no probe — **UNVERIFIED live** |
| `post-write-walkthrough.sh` | PASS | no probe — **UNVERIFIED live** |
| `instructions-loaded.sh` | PASS | **PASS** for the tap (cwd-attributed JSONL append). Event-name `InstructionsLoaded` itself is **UNVERIFIED** — the probe keys off SessionStart (`live/step-02-instructions_loaded.json`) |
