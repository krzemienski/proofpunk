# Command-surface end-user proof — `/proofpunk:truth-audit`

The flag-drift fix was previously proven only at *script* level (argparse rc).
That is not the user-facing surface: a user types a slash command, not a python
invocation. This drives the real command through the `claude` CLI.

## Executed

```
cd /tmp/pp_cmdrepo   # fresh git repo, one seed commit
claude -p '/proofpunk:truth-audit . --start 2026-01-01 --end 2026-08-13 --label cmdprobe' \
       --output-format json
```

The slash command **expanded and executed** — 19 records captured in
`claude-cmd-records.json`, including real `Agent` tool dispatches.

## Artifact proves the flags flowed through

The run created `/tmp/pp_cmdrepo/plans/20260825-0140-cmdprobe/` containing
`plan.md`, 9 phase files, and an `evidence/` directory. From `plan.md:11-12`
(copied here as `generated-plan.md`):

```
| Audit window start | `2026-01-01` |
| Audit window end   | `2026-08-13` |
```

The `--label cmdprobe` was honored in the directory name. Under the previously
documented `--since/--until`, the underlying script rejects the invocation with
`rc=2: unrecognized arguments` — so this run could not have produced a workspace
at all.

**This is end-user proof of the fix**, not a script-level check: the flags
entered at the command surface and appear in the generated artifact.

## Honest scope

- `rc=124` — the CLI hit the 200s timeout while a background worker continued.
  The artifact was already written, so the proof stands, but the command did not
  run to completion.
- This proves the **Claude** command surface. The **OpenCode** surface
  (`plugins/proofpunk/opencode/commands/proofpunk-truth-audit.md`) was fixed in
  the same pass and is **NOT** proven here — it needs the `opencode` binary
  driven separately.
- The session advertised tools `['Task','ListAgents','SendMessage','Skill',
  'TaskStop','Workflow']` — no `Write`/`Read`/`Bash`. This is the same
  coordinator profile measured in the SDK, now confirmed in the plain CLI, and
  is why the `Write`-dependent hook probes remain UNPROVEN.
