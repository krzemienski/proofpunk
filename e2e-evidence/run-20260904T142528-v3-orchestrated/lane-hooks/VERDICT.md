# LaneHooksDoctrine VERDICT

Repo: `/Users/nick/proofpunk`. HEAD at start `73e928e`. Lane owns
`plugins/proofpunk/hooks/*`, `tools/test-hooks.sh`,
`docs/hook-enforcement-map.md`.

## What changed (file:line)

- `plugins/proofpunk/hooks/stop-guard.sh` — fail-open is now observable.
  Missing `python3`, missing/unreadable transcript, malformed stdin, or a
  heuristic python crash emit
  `hookSpecificOutput.additionalContext` containing `enforcement OFF (<reason>)`
  and still exit 0. Silent stop means the heuristic ran.
  `sha256:389e11a2a3e86b6a573601866d9d599d4022e04fc92a6016c787045842f32106`
  (was `9840595c3a0eb32120ec667b587e03fed627727f936733dafc0e85cea9c907a8`).
- `tools/test-hooks.sh` — HOME isolated; case 4 flipped from "must be
  silent" to "must announce fail-open"; added python3-absent, unreadable
  transcript, malformed stdin, FakeGateway warn, RealGateway silent,
  session-start stdin-ignored, instructions-loaded malformed, snapshot
  Bash/non-Bash, PROOF_NONPATH honesty. PASS 50 → 60.
  `sha256:69abc3af953a61ec098b42ebc8c6d91740b81625fb462e06e9e6e2899ad949b3`.
- `docs/hook-enforcement-map.md` — NEW. 7 event keys, 11 registrations,
  counts derived from a parse of `hooks.json`
  (`sha256:e0227d5b825d2d5f943722e4a41c70914b4d7e116dff65b838d6b39457c2ec92`).
- `plugins/proofpunk/hooks/no-test-files.sh` — **not edited**. Content
  heuristic (`MOCK_MARKERS`, Fake/Mock/Stub class, etc.) was already in
  HEAD `73e928e`
  (`sha256:9d5d65f99490d8a7b145ada550791c90d6ba1b8bd48361fcd166ed9a69db703c`).
  Decision: keep it as a **soft warn**, never a hard deny. Discriminating
  cases + mutation proof added.
- `hooks.json` and the other 8 scripts — **not edited**.

## What was driven

- `bash tools/test-hooks.sh` unpiped, rc captured as a sibling file:
  - baseline (pre-harness-edit, current HEAD hooks): PASS=50 rc=0
    `baseline/step-00-test-hooks.log` + `.rc`
  - after (current hooks + new cases): PASS=60 rc=0
    `after/step-01-test-hooks.log` + `.rc`
  - pre-fix stop-guard + pre-fix no-test-files in a copied hooks dir,
    current harness: rc=4 PASS=56 FAIL=4 (the four fail-open cases)
    `after/step-02-pre-fix-hooks.log` + `.rc`
- Per-script block + allow arms, unpiped rc: `per-script/*/rc`
- Mutation `silent-missing-transcript` on `stop-guard.sh`:
  baseline PASS=60 rc=0 → mutated rc=2 PASS=58 FAIL=2 (missing transcript
  + unreadable transcript, both named) → restore byte-identical, logs
  identical. `mutation/`
- Mutation `silent-mock-content` on `no-test-files.sh`:
  baseline PASS=60 rc=0 → mutated rc=1 FAIL=1 (`FakeGateway warn missing`)
  → restore byte-identical, logs identical. `mutation-mock-warn/`
- `PATH=/bin` python3-absent: pre-fix silent, post-fix
  `enforcement OFF (python3-not-found)`.
- Five `sdk_probe.py` live probes after LaneCommandSurface released the
  lock, cwd `live/probe-cwd`, unpiped rc+JSON under `live/`:
  `doctrine` rc=0 pass=true; `instructions_loaded` rc=0 pass=true;
  `stop_guard` rc=0 pass=true (stdout is this plugin's decision:block);
  `blocks_test_file` rc=1 pass=false (`write_attempted: false` — SDK
  session has no Write tool); `allows_normal_file` rc=1 pass=false (same).

## Per-claim

| Claim | Verdict | Citation |
|---|---|---|
| `hooks.json` has 7 event keys and 11 registrations of 9 scripts | **PASS** | `derived-hooks-parse.json` (`event_key_count=7`, `registration_count=11`, `distinct_script_count=9`, `on_disk_sh_count=9`); source `plugins/proofpunk/hooks/hooks.json@sha256:e0227d5b825d2d5f943722e4a41c70914b4d7e116dff65b838d6b39457c2ec92` |
| `stop-guard.sh` and `bash-write-notice.sh` each registered twice, for the reasons in the map | **PASS** | same parse, `registered_twice`; host semantics `docs/skill-canon.md` §2.4–§2.5 |
| `PostToolUse` cannot deny | **PASS** (canon, not re-driven) | `docs/skill-canon.md` §2.5; scripts exit 0 and speak via `additionalContext` |
| Fail-open missing transcript / missing python3 / unreadable / malformed stdin is distinguishable from ran-clean | **PASS** (script-level) | `after/step-01-test-hooks.log` PASS lines; mutation `mutation/step-02-mutated.log` names the two transcript cases |
| `PROOF_NONPATH` cannot confirm the HTTP request | **PASS** (limitation confirmed, not "fixed") | case 25c in `tools/test-hooks.sh`; map §fail-open. Rule 10 forbids a shell-parse close. |
| `class FakeGateway` on a production path warns, does not deny | **PASS** (script-level) | `per-script/no-test-files-warn-FakeGateway/rc` = 0 and stderr contains `Fake/Mock/Stub class`; mutation-mock-warn ARM2 FAIL=1 names that case |
| `bash tools/test-hooks.sh` exits 0 with case count strictly above 50 | **PASS** | before PASS=50 `baseline/step-00-test-hooks.rc`=0; after PASS=60 `after/step-01-test-hooks.rc`=0 |
| Every of 9 scripts has block-shaped + allow arm with unpiped rc | **PASS** (script-level) | `per-script/` |
| All 7 event keys and 11 registrations covered in `docs/hook-enforcement-map.md` | **PASS** | that file, table rows #1–#11 |
| Every unenforced doctrine rule listed | **PASS** | map §Unenforced gaps, 15 items |
| Live `sdk_probe.py` `stop_guard` | **PASS** | `live/step-05-stop_guard.rc`=0; hook_run stdout is `{"decision": "block", "reason": "Proofpunk: a completion was claimed without a cited end-user evidence artifact…"}` (`live/step-05-stop_guard.json`) |
| Live `sdk_probe.py` `instructions_loaded` | **PASS** (tap) / event-name UNVERIFIED | `live/step-02-instructions_loaded.rc`=0; `loads_this_run=true` (62 new lines, cwd=probe-cwd). Probe keys `require_hook_event=SessionStart`, not `InstructionsLoaded`. |
| Live `sdk_probe.py` `blocks_test_file` | **UNVERIFIED** | `live/step-03-blocks_test_file.rc`=1; `write_attempted: false`; reply "No Write tool in this session." File absence is not a deny. |
| Live `sdk_probe.py` `allows_normal_file` | **UNVERIFIED** | `live/step-04-allows_normal_file.rc`=1; same missing-Write blocker. |
| Live `sdk_probe.py` `doctrine` | **PASS** | `live/step-01-doctrine.rc`=0; reply `Proofpunk is installed. Doctrine: execution logic`; SessionStart stdout is the same additionalContext. |
| Live `SubagentStop` fire | **UNVERIFIED** | no probe exists; script is the same file as Stop |
| Live Bash-bypass notice / capture-guard / evidence-guard | **UNVERIFIED** | no sdk_probe names for them |

Proof level: harness/parse claims are script-level. Live PASS is only
`doctrine`, `stop_guard` (Stop path), and the `instructions_loaded` tap.
Write-path live proof is UNVERIFIED because this SDK session has no Write
tool (`ListAgents`, `SendMessage`, `Skill`, `TaskStop`, `Workflow` only).

## Open / UNRESOLVED

1. **Write-path live probes UNVERIFIED.** `blocks_test_file` and
   `allows_normal_file` cannot fire PreToolUse:Write in this SDK session
   (no Write tool). Need a session that actually exposes Write — not a
   harness change in this lane (Lane B owns `sdk_probe.py`).
2. **`InstructionsLoaded` event name** not proven; the probe attributes
   via SessionStart + JSONL cwd.
3. **15 unenforced doctrine rules** listed in the map. Several are
   structural (PostToolUse cannot deny; never parse shell; transcript
   is not the network). Not closable in this lane.
4. **`PROOF_NONPATH` request-never-made** stays an honest limitation.
5. **Content heuristic is warn-only.** A determined agent can still
   land `class FakeGateway` on a production path via Write (warned) or
   Bash (unseen unless the path looks like a test file).
6. Did not edit `tools/gauge-report.py` (Lane E) or
   `tools/proofpunk-install.sh` (Lane A) or any `skills/` file.
