# SDK end-user validation — 3 PASS, 2 UNPROVEN

First genuine end-user validation of this plugin. Earlier "validation" ran
`tools/test-hooks.sh`, which executes one hook script in isolation — that proves
a script's output shape and nothing about whether the host loads the plugin,
surfaces its skills, or fires its hooks. This drives a real Claude session with
the plugin loaded through `claude-agent-sdk` 0.2.144 and observes what happens.

Harness: `tools/sdk_probe.py`. Every probe runs twice — with the plugin, and a
control arm without it (`--no-plugin`, `setting_sources=[]` so ambient host
config cannot contaminate the result). A probe that cannot fail proves nothing.

## Results

| Probe | Plugin | Control | Proves |
|---|---|---|---|
| `doctrine` | PASS | FAIL | SessionStart delivers doctrine into live context |
| `skills_listed` | PASS | FAIL | a plugin skill loads *from the plugin* |
| `router` | PASS | FAIL | the router skill loads and executes |
| `blocks_test_file` | UNPROVEN | — | session advertises no `Write` tool |
| `allows_normal_file` | UNPROVEN | — | same |

3/3 pass loaded, 3/3 fail unloaded.

## Three false-pass traps the control arms caught

Each was a real defect in the probe, found only by running the control.

**1. Text matching is not proof.** `router-control` returned
`text_matches: True` with the plugin absent — the model shelled out with `Bash`,
found `SKILL.md` on disk, and quoted the table. Fixed by requiring an observed
`Skill` invocation.

**2. Bare skill names are contaminated.** All 17 plugin skills also exist
standalone in `~/.claude/skills/` on this host, so invoking `end-user-testing`
proves nothing about plugin delivery — the control loaded it successfully with
the plugin absent. Fixed by requiring the namespaced `proofpunk:` form.

**3. An invocation is not a load.** Both arms then invoked
`proofpunk:end-user-testing` and both matched the argument — `tool_arg_matches`
was `True` in the control too. The call had *failed*; the model simply retried
with the bare name. Fixed by capturing `ToolResultBlock` by `tool_use_id` and
requiring the argument-matching call to have actually succeeded:

```
skills_listed          text:T  invoked:T  arg:T  succeeded:T   PASS
skills_listed-control  text:T  invoked:T  arg:T  succeeded:F   FAIL
```

Only `tool_succeeded` separates them. Without it the control would have passed.

## UNPROVEN: the two write probes

`no-test-files.sh` (PreToolUse) is **not** validated end-to-end. The SDK session
advertises only `Task, ListAgents, SendMessage, Skill, TaskStop, Workflow` — no
`Write`. Measured directly (`inv.log`, `inv2.log`):

```
A no-tools-arg            : ['Task','ListAgents','SendMessage','Skill','TaskStop','Workflow']
B allowed_tools=['Write'] : ['Task','ListAgents','SendMessage','Skill','TaskStop','Workflow']
C setting_sources=['user']: ['Task','ListAgents','SendMessage','Skill','TaskStop','Workflow']
ADVERTISED TOOLS (tools=['Write']): []
```

`allowed_tools` filters an existing set; it cannot grant a missing tool. Passing
`tools=["Write"]` filtered the coordinator set to empty. With no `Write` tool the
model cannot attempt the write, so an absent file proves nothing about the guard.

The hook is verified at two lower levels — it denies with rc=2 on a test-file
payload, and `tools/test-hooks.sh` fails against a mutated copy — but **delivery
through a live session is UNPROVEN** and is reported as such, not inferred from
the script-level result.

This is a constraint of the SDK-spawned CLI profile in this environment, not a
plugin defect.

## Reproduce

```bash
python3 tools/sdk_probe.py doctrine                 # PASS  (exit 0)
python3 tools/sdk_probe.py doctrine --no-plugin     # FAIL  (exit 1)
```

Exit codes: 0 held, 1 did not hold, 2 harness error — never conflated.
