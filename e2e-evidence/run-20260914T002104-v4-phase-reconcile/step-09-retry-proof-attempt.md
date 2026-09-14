# step-09 — I tried to prove the retry path and could not. Here is why.

## The gap I was closing

`step-07` disclosed that V6's green 6/6 proves the **surface**, not the
**retry mechanism**: `attempt2+ files = 0`, so the retry branch never
executed. A same-run `attempt1` FAIL → `attempt2` PASS has never been
observed. I attempted to close that.

## The experiment

Force the transient shape deterministically by pointing the run at an
unreachable endpoint, so every arm fails with a connection error and the
retry branch must fire.

```
ANTHROPIC_BASE_URL=http://127.0.0.1:1 \
ANTHROPIC_AUTH_TOKEN=dummy-not-a-real-key \
PP_CMDSURFACE_OUT_DIR=<fresh> \
PROOFPUNK_SURFACE_MODEL=cc/claude-opus-5 \
python3 tools/verify-command-surface.py
EXIT:1
```

## It failed to falsify — and that is the finding

| Expected | Observed |
|---|---|
| Every arm fails with a connection error | `full_chain=4/6`, real sessions ran |
| `attempt2`/`attempt3` files created | **0 of each** (30 attempt files, all `attempt1`) |
| Retry branch executes | Never reached |

Reading the actual arm log settles it: `cmd_slash_implement.plugin.attempt1`
returned `"pass": true`, `"num_turns": 4`, `"cost_usd": 2.31`,
`"model_pin_honoured": true`, `"no_harness_error": true`. **A real, billed,
successful Claude session ran against an endpoint that refuses connections on
port 1.**

The CLI ignored the unreachable `ANTHROPIC_BASE_URL` and fell back to ambient
host auth. Confirmed by source: neither `tools/verify-command-surface.py` nor
`tools/sdk_probe.py` references `ANTHROPIC_BASE_URL` at all — it is inherited
through `os.environ.copy()` and consumed by the CLI, which treats it as a
preference rather than a binding.

This is **not** a claim that env vars never reach the arms. `step-06` measured
the opposite: unsetting `ANTHROPIC_API_KEY` moved `full_chain` 3/6 → 5/6, so
the environment demonstrably propagates. The narrow, measured fact is that an
unreachable `ANTHROPIC_BASE_URL` does not make the CLI fail — it silently
degrades to another auth source.

## Consequences, stated plainly

1. **The retry path is still UNPROVEN.** I did not close the gap. Two
   deliberate attempts have now failed to observe a same-run retry: the
   stochastic 29% rate did not fire during the green run, and this forced
   experiment could not create the condition.

2. **A harness limitation worth knowing**: `verify-command-surface.py` cannot
   be steered to a specific endpoint by setting `ANTHROPIC_BASE_URL`. A run
   intended to target one provider may silently execute against whatever
   ambient auth the host offers. Every arm records `model_pin_honoured`, so
   the **model** stays attributable — but the **endpoint** does not.

3. **This run cost real money** (~$2.31 on the one arm I inspected, 15 arms
   total) against an endpoint I believed unreachable. Recorded because an
   experiment that silently spends is worth knowing about.

## What I did NOT do

I did not weaken `is_transient_harness_error()`, add a test hook, or
fabricate a failure to make the retry branch run. Either the mechanism gets
observed under a real transient condition or it stays labelled UNPROVEN.
`step-39`'s standard — no mechanism change on a correlation — applies equally
to proving one.

## Status

| Item | Status |
|---|---|
| V6 surface 6/6 | **PASS** (unchanged, `step-07`) |
| V6 retry mechanism | **UNPROVEN** — 2 attempts, neither observed it |
| Endpoint steerability of the harness | **Measured limitation**, newly recorded |

Evidence: `t11-retry-proof/run.log`,
`t11-retry-proof/cmd_slash_implement.plugin.attempt1.log`,
`t11-retry-proof/command-surface-proof.json`
