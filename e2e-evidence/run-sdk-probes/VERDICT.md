# SDK end-user validation — 12 PASS, 1 OBSERVED, 2 UNPROVEN

First genuine end-user validation of this plugin. Earlier "validation" ran
`tools/test-hooks.sh`, which executes one hook script in isolation — that proves
a script's output shape and nothing about whether the host loads the plugin,
surfaces its skills, or fires its hooks. This drives a real Claude session with
the plugin loaded through `claude-agent-sdk` 0.2.144 and observes what happens.

Harness: `tools/sdk_probe.py`. Every probe runs twice — with the plugin, and a
control arm without it (`--no-plugin`, `setting_sources=[]`, which excludes
user/project settings sources). That reduces ambient contamination but does not
eliminate it: the control still emits `SessionStart`, so some host-level hooks
run regardless. Claims are scoped accordingly. A probe that cannot fail proves
nothing.

## Results

| Probe | Plugin | Control | Proves |
|---|---|---|---|
| `doctrine` | PASS | FAIL | SessionStart delivers doctrine into live context |
| `router` | PASS | FAIL | the router skill loads and executes |
| `skills_listed` | PASS | FAIL | `proofpunk:end-user-testing` loads from the plugin |
| `skill_implement` | PASS | FAIL | `proofpunk:implement` loads from the plugin |
| `skill_validation_plan` | PASS | — | `proofpunk:validation-plan` loads |
| `skill_root_cause_debugging` | PASS | — | `proofpunk:root-cause-debugging` loads |
| `skill_full_functional_audit` | PASS | — | `proofpunk:full-functional-audit` loads |
| `skill_red_team_eval` | PASS | FAIL | `proofpunk:red-team-eval` loads from the plugin |
| `skill_visual_inspection` | PASS | — | `proofpunk:visual-inspection` loads |
| `skill_production_readiness` | PASS | — | `proofpunk:production-readiness` loads |
| `skill_codebase_truth_audit` | PASS | FAIL | `proofpunk:codebase-truth-audit` loads from the plugin |
| `instructions_loaded` | PASS | FAIL | the InstructionsLoaded tap runs and appends |
| `stop_guard` | OBSERVED | FAIL | Stop event fires, hooks exit clean † |
| `blocks_test_file` | UNPROVEN | — | session advertises no `Write` tool |
| `allows_normal_file` | UNPROVEN | — | same |

**12 plugin-attributed PASS**, 1 host-lifecycle OBSERVED, 2 UNPROVEN.

Every probe with a control arm fails without the plugin. The five skill probes
marked `—` share the identical predicate as the four that were control-tested
(observed `Skill` call + namespaced argument + successful tool result); their
controls were not run, so they are attributable by construction rather than by
a measured negative.

† **Scope limit.** The `hook_response` record's `hook_name` is the *event*
(`"Stop"`, `"SessionStart:startup"`), never the script filename, so this proves
the Stop event fired and its hooks exited `success` — **not** that
`stop-guard.sh` specifically ran. `stop-guard.sh` is silent unless it blocks, so
a clean turn emits no attributable signal. Proving the block path needs a
transcript that trips the heuristic; not done here, and not claimed.

`instructions_loaded` attribution: the plugin arm appended **30 lines** resolving
to this run's cwd, the control arm appended **0**. The arms ran sequentially, so
a concurrent session writing the same cwd could in principle land in either
window — the control's zero makes that unlikely here but does not exclude it.
What is established: with the plugin loaded the tap appends, without it it does
not.

## Four false-pass traps the control arms caught

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

**4. Path identity is not string identity.** `loads_this_run` failed at first
because macOS resolves `/tmp` through a symlink — the tap recorded
`/private/tmp/proofpunk_probe` while the probe compared `/tmp/proofpunk_probe`.
Fixed with `os.path.realpath` on both sides. The 30 lines were always from this
run; the comparison was wrong, not the hook.

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
