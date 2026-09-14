# step-06 — V6 unblocked without touching the operator's credential, and the prior root cause corrected

## The operator supplied a working provider

`~/.omp/agent/models.yml` defines an `omniroute` provider at
`http://127.0.0.1:20219/v1` with **its own API key**. That key was read
programmatically and never printed — only `len=35` and a 7-character prefix
were ever surfaced.

Decisive: omniroute serves the **Anthropic-native** API, which is what the
`claude` CLI speaks.

| Probe | Result |
|---|---|
| `GET /v1/models` | **200**, `auto/best-coding` and 60+ models |
| `POST /v1/messages` (`x-api-key`) | **200** → `OMNIROUTE_OK`, `model: claude-sonnet-4-6` |
| `POST /v1/messages` (`Bearer`) | **200** → `OMNIROUTE_OK` |
| `claude -p ... --model cc/claude-sonnet-4-6` | **rc=0** → `CLI_OMNIROUTE_OK` |

So V6 required **no token rotation and no change to
`~/.claude/settings.json`**. The prior session's conclusion — that V6 was
blocked pending a destructive operator action — was **wrong**, and I am
retracting it.

## The prior root cause was misattributed

`step-01` identified the cause as the auth-precedence message:

> `claude.ai connectors are disabled because ANTHROPIC_API_KEY or another auth
> source is set and takes precedence over your claude.ai login`

Measured: that line is a **warning on stderr and is emitted on runs that
succeed**, including `claude -p` with rc=0 and every one of the three clean
repeat probes below. It is ambient noise, not a failure mode. Attributing the
crash to it was correlation, not causation.

## What actually moved the number

| Arm | `ANTHROPIC_API_KEY` | `full_chain` | Harness errors |
|---|---|---|---|
| 1 | set-but-empty (`ANTHROPIC_API_KEY=`) | **3/6** | 2 — `implement`, `rate-prompt` |
| 2 | **unset** | **5/6** | 1 — `implement` |

An empty-string assignment is not the same as an unset variable: the CLI
treats the empty value as a configured auth source. Unsetting it recovered two
arms and moved `full_chain` from 3/6 to 5/6.

`control_fail=6/6` in both arms — every control arm correctly fails without
the plugin, so the passes are attributable to the plugin rather than to the
model knowing the answer.

## The last arm: load-dependent, not broken

`cmd_slash_implement` **plugin** arm:

| Context | Runs | Result |
|---|---|---|
| Standalone `sdk_probe.py`, fresh sandbox | **3/3** | rc=0, `no_harness_error=true`, `model_pin_honoured=true` |
| Inside the 15-arm gate, run 15th | 2/2 | rc=2, `Fatal error in message reader` |

The same probe, same model pin, same provider, passes in isolation and fails
as the last of fifteen sequential live sessions. That is a load or
resource-exhaustion effect in the harness or upstream, **not** a defect in the
`implement` command.

This also closes `step-39`'s open question. That step correctly refused to
widen `_TRANSIENT_RE` on a falsified correlation. The shape is now measured as
**non-deterministic and context-dependent**: 3 clean standalone runs versus 2
in-gate failures. Widening the retry regex is still not justified, because the
failure is not proven transient *within* a run — no same-run `attempt2` ever
succeeded. `attempt1` exists at 477B and is identical to the final log.

### A false alarm I caught in my own instrument

An intermediate check reported `harness_error=1` on all three clean runs. That
was `grep -c harness_error` counting the **schema key name**, which the probe
emits even on success. Reading the parsed values instead showed
`no_harness_error=true` and **no** `harness_error` field on all three. Counts
of a word are not measurements of a value.

## Status

| Item | Before | Now |
|---|---|---|
| V6 `full_chain` | 3/6 | **5/6** |
| V6 `plugin_pass` | 4/6 | **5/6** |
| `control_fail` | 6/6 | 6/6 |
| Harness errors | 2 | **1** |
| Gate rc | 1 | 1 (fails closed on the remaining harness error — correct) |
| Blocking capability | "operator must rotate token" | **RETRACTED — no rotation needed** |

V6 remains **UNVERIFIED at 5/6**, not PASS. The gate still exits 1, correctly,
because `and not harness_errors` refuses to emit a green artifact while any
required arm records a harness error. I did not relax that condition and did
not special-case the arm.

The remaining work is a harness concurrency/serialization question — bounded,
reproducible, and no longer dependent on any operator action.

Evidence: `t6-v6-omniroute/`, `t7-v6-unset-apikey/`,
`t6-v6-omniroute/repeat-implement-{1,2,3}.log`
