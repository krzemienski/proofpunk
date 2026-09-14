# step-01 — V6 (`verify-command-surface`) is BLOCKED on a credential capability

**Not a product failure. Not a proofpunk defect. A host-environment blocker.**

## Gate result at HEAD `63727e1`

| Gate | rc | Decisive output |
|---|---|---|
| `python3 tools/verify-command-surface.py` | **1** | `full_chain=3/6 plugin_pass=4/6 control_fail=6/6 honest_max=3/6` / `HARNESS ERRORS (1): [('implement', 'plugin')]` |

Evidence: `gates/verify-command-surface.log`, `gates/verify-command-surface.rc`

## Why rc=1 is the gate working, not the gate broken

`tools/verify-command-surface.py` ends with:

```python
ok = (n_plugin_pass == 6 and n_control_fail == 6 and n_honest_max == 6) and not harness_errors
sys.exit(0 if ok else 1)
```

`and not harness_errors` is deliberate — the file's own comment says a green
artifact must never coexist with a recorded harness error on any required arm.
The gate is **failing closed on an uncontrolled variable**, which is the
designed behavior.

## Root cause — established by reading source and by reproduction

1. `~/.claude/settings.json` sets, in its `env` block, both
   `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` (a non-Anthropic router).
   *(Key names only. Values are deliberately not recorded here.)*
2. `tools/verify-command-surface.py:244` — `env = os.environ.copy()` — so every
   arm inherits that ambient auth configuration.
3. The Claude CLI then emits:
   `claude.ai connectors are disabled because ANTHROPIC_API_KEY or another auth
   source is set and takes precedence over your claude.ai login`
4. The `implement` **plugin** arm's message reader dies:
   `Fatal error in message reader: Command failed with exit code 1`, and
   `sdk_probe.py` records `{"harness_error": "ProcessError: ..."}` with rc=2.

The **control** arm survives the same environment because it runs
`--no-plugin` and never reaches the failing path — which is precisely why this
presents as a one-arm harness error rather than a uniform failure.

### Independent reproduction

`python3 tools/sdk_probe.py cmd_slash_implement --cwd <fresh sandbox> --model cc/claude-opus-5`
emitted the identical auth-precedence warning before I terminated it (rc=143 =
my SIGTERM, per the secret-handling halt below).

Evidence: `v6-repro/implement-plugin-repro2.log`

## Why this is blocked rather than fixable by me

Resolving it requires a working auth source for live Claude sessions, which
means **rotating the exposed credential** (see
`step-00-secret-handling-incident.md`) and re-establishing host auth. Rotating
an operator credential on operator infrastructure is a destructive action that
is the operator's decision, not mine.

Two non-options, named so they are not retried:
- **Do not** unset the operator's auth vars to force a green — that mutates the
  operator's environment and changes what the gate measures.
- **Do not** special-case the `implement` arm or relax `and not harness_errors`
  — that is weakening a gate to manufacture a pass, the exact defect class this
  repository's history records four times.

## Status

| Item | Status |
|---|---|
| V6 — every command proven at the real slash surface | **BLOCKED — credential capability** |
| Blocking capability | A valid, non-conflicting auth source for live Claude CLI sessions, after rotation of the exposed token |
| Unblocked by | Operator rotating `ANTHROPIC_AUTH_TOKEN`, then re-running `python3 tools/verify-command-surface.py` |
| Honest maximum achieved | `full_chain=3/6`, `plugin_pass=4/6`, `control_fail=6/6` — recorded, not promoted |

## Secret-handling halt

All authenticated host testing is **stopped** pending rotation. In-flight
`sdk_probe.py` processes were terminated. See
`step-00-secret-handling-incident.md` for the exposure, the measured scrub
(`~/.zsh_history` 6 → 0 occurrences), and the outstanding operator action:
rotate the credential, then delete the `chmod 600` pre-redaction history backup
noted there, which still contains it.
