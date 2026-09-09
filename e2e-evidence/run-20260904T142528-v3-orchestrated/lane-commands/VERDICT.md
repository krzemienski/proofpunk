# Lane Command Surface — VERDICT

Lane: LaneCommandSurface
Repo: `/Users/nick/proofpunk`
Measured: 2026-09-04T15:34:08Z
Owned files: `tools/sdk_probe.py`, `tools/verify-command-surface.py`
Did not edit: `tools/gauge-report.py`, `tools/proofpunk-install.sh`, anything under `plugins/`

## Gauge #4 artifact (for Lane E to wire)

Path: `/Users/nick/proofpunk/evidence/v3-release/l16-commands/command-surface-proof.json`
sha256: `7e4f7093f8e48fcb80bbd97370747650cd8ccdb0ef3983fd6c47d687b3184c0c`
bytes: 40008
`full_chain`: **4/6** (not 6/6)
`plugin_pass`: 6/6
`control_fail`: 6/6
`honest_max_reached`: 6/6

Runner: `python3 tools/verify-command-surface.py`
Exit: `0` at `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-commands/step-02-verify-command-surface.rc`
Stdout: `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-commands/step-02-verify-command-surface.log`

## What changed

`tools/sdk_probe.py`
- Added six slash-typed probes: `cmd_slash_implement`, `cmd_slash_forge_prompt`, `cmd_slash_rate_prompt`, `cmd_slash_truth_audit`, `cmd_slash_verify`, `cmd_slash_install`.
- Existing probes (`router`, `doctrine`, `stop_guard`, `cmd_truth_audit_flags`, `cmd_rate_prompt_flag`, skill_* ) unchanged in name and contract.
- Captures init `slash_commands` + `plugins` so registration and THIS-tree plugin path are observed, not self-reported.
- Requires `UserPromptExpansion` for slash-typed proof (`slash_expanded`).
- Accepts host Skill aliases (`proofpunk:rate-prompt` as well as `proofpunk:prompt-forge`) because the live host surfaces the command as its own skill name.
- Catches `ResultError` (max-turns) so partial init+transcript is kept instead of rc=2 with no JSON.
- Historical `cmd_truth_audit_flags` / `cmd_rate_prompt_flag` remain skill-load (level b), not slash-typed.

`tools/verify-command-surface.py` (new)
- Runs each of the six probes twice (plugin, `--no-plugin`).
- Writes ONE artifact under `evidence/v3-release/l16-commands/`.
- Names proof level per command. Only level (c) counts toward 6/6 full-chain.
- 180s per-arm timeout; `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=5000`.
- Exit 0 when 6/6 plugin pass AND 6/6 control fail AND 6/6 honest-max — not when full_chain is 6/6.

## Proof levels (from command-surface-map.md)

| Level | Meaning | Counts toward 6/6 (c)? |
|---|---|---|
| (a) script-level | backing script invoked directly | no |
| (b) skill-load | `Skill` tool by name, bypassing the command doc | no |
| (c) full-chain | slash typed → registered → expanded → mapped Skill succeeded → unique marker | yes |
| playbook-recognition | slash typed+expanded + local plugin; no backing skill/script executed | no |

## Per-command (second drive, the sealed artifact)

Each control arm: `Unknown command: /proofpunk:<name>`, `slash_registered=false`, `local_plugin_loaded=false`, `pass=false`. That is the non-vacuity proof.

| Command | Honest max | Reached | Plugin rc | Control rc | Skill invoked | Marker | Verdict |
|---|---|---|---|---|---|---|---|
| implement | (c) | **(c)** | 0 | 1 | `proofpunk:implement` succeeded | `--parallel` | **PASS (c)** |
| forge-prompt | (c) | **(c)** | 0 | 1 | `proofpunk:forge-prompt` succeeded | `--depth` | **PASS (c)** |
| rate-prompt | (c) | **(c)** | 0 | 1 | `proofpunk:rate-prompt` succeeded | `--ship-below-threshold` | **PASS (c)** |
| truth-audit | (c) | **(c)** | 0 | 1 | `proofpunk:truth-audit` succeeded; args included `--start 2026-01-01 --end 2026-08-13 --label cmdsurface` | `--start`; `unrecognized arguments` absent | **PASS (c)** |
| verify | playbook-recognition | playbook-recognition | 0 | 1 | none (command doc has no Activate-skill line) | quoted `UNVERIFIED` | **PASS at honest max, not (c)** |
| install | playbook-recognition | playbook-recognition | 0 | 1 | `proofpunk:install` (host-surfaced command skill, not a delivery skill) | slash expanded; no file merge | **PASS at honest max, not (c)** |

Transcripts: `evidence/v3-release/l16-commands/cmd_slash_<name>.plugin.log` and `.control.log`, also copied to `e2e-evidence/run-20260904T142528-v3-orchestrated/lane-commands/step-02-second-drive/`.

## Why install and verify are not (c)

**install.** `/proofpunk:install` is an in-session agent playbook. It has no backing skill under `plugins/proofpunk/skills/` and no backing script. `tools/proofpunk-install.sh` is a different surface (operator-run plugin deployer) — same word, unrelated. SDK sessions in this environment do not advertise `Write`, so the playbook cannot merge CLAUDE.md. First drive hung trying to execute it (~23 min, killed). Second drive: slash registered, `UserPromptExpansion` fired, local plugin loaded, control unknown-command. That is playbook-recognition. Claiming (c) would inflate.

**verify.** Command doc has no `Activate the … skill` line, no flags, and `fresh_evidence.py` is internal to `end-user-testing`, not a user-facing flag on `/proofpunk:verify`. Second drive quoted the command-doc marker (`Unexecuted checks are UNVERIFIED`) with zero tool calls. Playbook-recognition is the honest ceiling.

## First drive (sealed, not overwritten)

`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-commands/step-01-first-drive/`
- implement already (c) on first drive (rc=0, Skill `proofpunk:implement`, `--parallel`).
- forge-prompt / verify plugin arms: ResultError max-turns (rc=2) — no JSON.
- rate-prompt: invoked `proofpunk:rate-prompt` (host alias); probe required only `proofpunk:prompt-forge` → `tool_arg_matches=false`. Fixed by accepting both names.
- truth-audit: 693s, cost $36.94, launched a Workflow; `text_matches=false`. Fixed with 180s timeout + ResultError catch + alias.
- install plugin arm still running when the process was killed (SIGTERM, exit 143).

Second drive used STOP-style prompts, Workflow/ListAgents disallowed, 180s arm timeout. Do not reuse first-drive logs as the gauge artifact.

## Scope of (c)

(c) here is: user typed `/proofpunk:<name>` → CLI registered and expanded the command (`slash_commands` + `UserPromptExpansion`) → THIS tree's plugin path loaded → host invoked a Skill whose name is the command or its documented backing skill → unique flag/marker from the command contract observed.

It is **not** a completed implement/audit/rate job. Coordinator Skill results say `Loaded skill instructions (read-only) … Nothing was executed; delegate execution to a worker.` That is the same coordinator profile measured in `e2e-evidence/run-sdk-probes/VERDICT.md`. Flag mapping for truth-audit is proven as Skill `args` containing `--start/--end/--label`, not as `init_audit_workspace.py` running to completion.

## Open / UNRESOLVED

- Gauge-report.py still cites `command-surface-map.md` and hard-codes `0/6`. Lane E owns that file. Wire it to `evidence/v3-release/l16-commands/command-surface-proof.json` `full_chain` = 4/6. Do not rewrite the map's historical 0/6 claim; that was true when it was sealed.
- OpenCode `/proofpunk-*` surface: not driven. BLOCKED — this harness is `claude-agent-sdk` only.
- OMP `/proofpunk:implement` resolution: still UNVERIFIED (same gap the map named).
- install file-merge execution: UNVERIFIED at slash surface (no Write tool in SDK coordinator). Mechanics remain covered by `tools/dry-run-install.sh`, which is a mirror script, not the command.
- Host Skill name for slash commands is the command (`proofpunk:rate-prompt`), not the skill the command doc names (`prompt-forge`). Observed, not a defect in the command docs.

## Live lock

Released. `tools/sdk_probe.py` is stable. LaneHooksDoctrine may run `stop_guard`, `instructions_loaded`, `blocks_test_file`, `allows_normal_file`, `doctrine` read-only.
