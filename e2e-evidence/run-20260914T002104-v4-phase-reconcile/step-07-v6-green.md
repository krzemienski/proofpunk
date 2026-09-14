# step-07 — V6 reaches 6/6, and the retry fix that a passing run does not prove

## Result

```
python3 tools/verify-command-surface.py   rc=0
full_chain=6/6  plugin_pass=6/6  control_fail=6/6  honest_max=6/6
HARNESS ERRORS: []
```

Artifact: `t10-v6-retry-fixed/command-surface-proof.json`,
`measured_at 2026-09-14T15:40:18Z`, surface model pinned `cc/claude-opus-5` on
all 15 arms.

| Command | Honest max | Reached |
|---|---|---|
| `implement` | c | **c** |
| `forge-prompt` | c | **c** |
| `rate-prompt` | c | **c** |
| `truth-audit` | c | **c** |
| `verify` | d | **d** |
| `install` | d | **d** |

`control_fail=6/6`: every `--no-plugin` control arm fails, so each pass is
attributable to the plugin rather than to the model already knowing the
answer.

## The diagnosis, corrected twice

**First correction** (`step-06`): the auth-precedence warning was never the
cause. It appears on runs that succeed.

**Second correction, here**: I first theorised the remaining failure was
positional — the 15th arm exhausting something. Controlled repeats falsified
it:

| Condition | Result |
|---|---|
| Standalone, 3 runs | 3 PASS |
| Immediately after a full gate run | PASS |
| Back-to-back, no pause | **rc=2, rc=0, rc=2** |

**5 PASS / 2 FAIL across 7 identical runs — 29%, stochastic.** Not
positional, not load-accumulated. In a later run the failing arm moved from
`implement` to `forge-prompt`, which independently confirms it is not bound to
one command. Every failure log is byte-identical at 477B.

## Why the first retry fix did not work — proven by execution, not inspection

Adding `Fatal error in message reader` to `_TRANSIENT_RE` produced **zero**
retries: every arm still logged `attempt 1/3`, and no `attempt2` file existed.

Executing the real function against the real log found the reason:

```
parsed JSON?:                        True
harness_error field:                 ProcessError: Command failed with exit code 1 ...
regex matches harness_error field:   False
regex matches RAW body:              True
is_transient_harness_error(...):     False
```

`is_transient_harness_error()` takes the `parsed` branch whenever probe JSON
decodes, and that branch **deliberately** searches only harness-level fields —
never the raw body — so a genuine probe failure that merely quotes an error
word cannot be mistaken for host contention. The phrase I matched lives on a
stderr line *outside* the JSON.

I matched the shape the field actually carries
(`ProcessError: Command failed with exit code 1`) rather than widening the
search to the raw body, which would have defeated that scoping guard.

### The fix is discriminating — all three cases checked

| Input | Expected | Got |
|---|---|---|
| Failing arm log | transient=True | **True** |
| Passing arm log | transient=False | **False** |
| Genuine probe failure (`pass=False`, no harness_error) | transient=False | **False** |

## What this run does NOT prove

**`attempt2+ files: 0`.** All 15 arms passed on the first attempt, so the
retry path never executed in the green run. This run proves **the surface is
6/6**; it does **not** prove the retry mechanism works end to end in the
harness. The retry logic is verified at function level (the table above) and
by the falsified-then-remeasured failure statistics — not by an observed
same-run recovery.

Stating it plainly: a same-run `attempt1` FAIL followed by `attempt2` PASS has
still never been observed. `step-39` demanded exactly that evidence before
trusting retry, and it remains unobserved. Given a 29% stochastic rate, the
green run is consistent with luck (≈0.71^15 ≈ 0.6% for all-15-clean by chance,
so more likely the rate is arm-dependent or lower than measured here).

**Therefore V6 is reported as: surface 6/6 PASS, retry mechanism UNPROVEN.**

## Status change

| | Before | Now |
|---|---|---|
| V6 gate rc | 1 | **0** |
| full_chain | 3/6 | **6/6** |
| Harness errors | 2 | **0** |
| Blocker | "operator must rotate token" | **RETRACTED — never needed** |

No gate was relaxed. `and not harness_errors` is untouched; it simply has no
harness errors to refuse.
