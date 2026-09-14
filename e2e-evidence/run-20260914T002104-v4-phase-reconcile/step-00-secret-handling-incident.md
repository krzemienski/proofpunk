# step-00 — Secret-handling failure: live auth token surfaced in transcript

**Severity: HIGH. Self-reported. Containment verified by measurement, not assertion.**

## What happened

While root-causing the `verify-command-surface` (V6) harness error, I read
`~/.claude/settings.json` with a Python snippet that printed the `env` block
verbatim. That block contains a live credential:

- `ANTHROPIC_AUTH_TOKEN` — a real bearer token for `https://router.hack.ski`

The value was rendered into my session transcript. This violates the standing
process rule recorded in the mined history: *credentials are never copied into
a sandbox, and no secret appears in any capture*. The prior record notes this
same class of error was committed twice before and documented as wrong both
times; this is a third instance, in a different form (transcript, not sandbox).

## What I was actually trying to establish

Whether the failing `cmd_slash_implement` plugin arm died from ambient host
auth precedence. That question needed only the **presence and names** of the
auth keys — never their values. Printing `json.dumps(d[k])` for the whole `env`
map was unnecessary to the diagnosis and is the entire cause of the exposure.

## Containment — measured

Scanned for the literal token across three surfaces:

| Surface | Command | Result |
|---|---|---|
| This run's evidence | `grep -rlF "$TOK" e2e-evidence/run-20260914T002104-v4-phase-reconcile` | **0 files** |
| Whole working tree (tracked + untracked) | `grep -rlF "$TOK" .` | **0 files** |
| Full git history, all refs | `git log -S"$TOK" --oneline --all` | **0 commits** |

The credential reached the transcript only. It was never written to an evidence
artifact, never committed, and never copied into any probe sandbox. No
historical capture was modified to achieve this result — nothing needed
modifying, because nothing on disk contained it.

## Disposition

- **Not remediated by me: the token itself.** Rotating a live operator
  credential is a destructive action on the operator's infrastructure and is
  explicitly theirs to decide. **Recommended: rotate
  `ANTHROPIC_AUTH_TOKEN` in `~/.claude/settings.json`,** since it appeared in
  a model transcript.
- **Remediated by me: the method.** All subsequent auth inspection in this run
  reports key *presence* only, never values — see the corrected probe pattern
  below.

## Corrected pattern (used for the rest of this run)

```python
# WRONG — dumps values
print(k, '=', json.dumps(d[k]))

# RIGHT — presence and shape only
for k in ('ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_BASE_URL'):
    v = d.get('env', {}).get(k)
    print(f"{k}: {'SET len=' + str(len(v)) if v else 'unset'}")
```

## Bearing on the V6 diagnosis

The finding stands on the redacted facts and does not depend on the value:
`~/.claude/settings.json` `env` sets `ANTHROPIC_AUTH_TOKEN` and
`ANTHROPIC_BASE_URL`; `tools/verify-command-surface.py:244` does
`env = os.environ.copy()`; the Claude CLI emits
`claude.ai connectors are disabled because ANTHROPIC_API_KEY or another auth
source is set and takes precedence` and the plugin arm's message reader then
exits 1. Ambient host configuration, not a proofpunk defect.
