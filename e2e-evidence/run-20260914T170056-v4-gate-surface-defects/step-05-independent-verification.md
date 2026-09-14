# step-05 — Independent verification, and the blocker that was only half true

## The standing blocker

The ledger carried:

> `"Independent verification — subagent routes 401; self-verification only (step-04)"`

## Reconfirmed: the subagent path is genuinely dead

A default-worker subagent was dispatched with a trivial read-only task (count
skill directories). It died in **197 ms**:

```
[omniroute/cx/gpt-6-astra] 401 [codex] All 1 connection(s) authentication
expired — please reconnect in the dashboard (type=authentication_error
param=invalid_api_key)
```

Direct probes of each configured role against `127.0.0.1:20219`:

| Role | Model | HTTP |
|---|---|---|
| `default` | `cc/claude-opus-5` | **200** |
| `task` | `cf/@cf/deepseek-ai/deepseek-r1-distill-qwen-32b` | **200** |
| `advisor` | `cx/gpt-6-astra` | **401 codex expired** |
| `plan` | `cx/gpt-5.6-terra` | **401 codex expired** |

`~/.omp/agent/config.yml` sets `task.agentAdvisor.task: "on"`, which attaches the
**advisor** to every spawned subagent. The worker's own role is healthy; the
advisor it is paired with is not, so the 401 kills the subagent before it starts.
That is `step-11`'s diagnosis from the prior run, independently reproduced.

## But "independent verification is blocked" was still wrong

The subagent *facility* is blocked. Independent verification is not. Routing a
verifier through the headless CLI on the live `cc/claude-opus-5` route works:

```
$ ANTHROPIC_BASE_URL=http://127.0.0.1:20219 claude -p "$(cat prompt-run3.txt)" \
    --model cc/claude-opus-5 --permission-mode bypassPermissions
rc=0
```

The verifier was instructed not to read any `step-*.md`, report, or narrative
written by me, and to verify only by running commands itself.

## Result: 5/5 PASS, including the adversarial probe

Full table at `independent/verdict-run3.md`. Summary:

| Claim | Verdict | Decisive output (verifier's own) |
|---|---|---|
| C1 mutation catches a corrupted count, restores byte-identically | **PASS** | baseline `rc=0`; mutated `VERDICT: FAIL — 1 mismatch(es)` + `SKILL.md:4: 11 skills (live accepts [18, 19])` `rc=1`; restored sha256 `48a7905f…c215825` matches |
| C2 gauge #4 = 6/6, gauge-report rc=0 | **PASS** | `[PASS] #4 … 6/6`; `VERDICT: PASS`; `rc=0` |
| C3 no hardcoded `v3-release/l16-commands` path | **PASS** | `grep_rc=1` (no match) |
| C4 all 10 verifier gates rc=0 | **PASS** | ten `rc=0` lines |
| C5 **adversarial** forged 6/6 with a passing control arm must not poison the gauge | **PASS** | forgery present → gauge still `6/6`, and the only source cited in `gauge-report.json` is the real `t10` artifact |

C5 is the one that matters most: the verifier built a **fresh forgery itself**
(`measured_at` 2099, `commands[0].control.pass=true`), placed it in the evidence
tree, and confirmed the gauge refused it rather than taking the newest/highest
number. My own version of that test was run against the disqualifier functions
directly; the verifier's ran end-to-end through the real gauge.

## Tree left as found

```
$ git status --porcelain | grep -v '^??'
 M gauge-report.json
 M gauge-report.md
 M tools/gauge-report.py
 M tools/verify-counts.py

$ ls e2e-evidence/_probe
ls: cannot access 'e2e-evidence/_probe': No such file or directory

$ sha256sum plugins/proofpunk/skills/proofpunk/SKILL.md
48a7905fb9272fa605fba9ceab158e5c4b67194cc8d9d4e3d243ae5c8c215825
```

Exactly the four intended modifications; the probe is gone and the mutated file
is byte-identical to its committed state.

## Two earlier verifier runs, recorded rather than hidden

| Run | rc | Outcome |
|---|---|---|
| run1 | 0 | Reported MET and recorded an intent verdict, but `claude -p` emitted only its final message — **the per-claim table was lost**. Not citable as a table. |
| run2 | **1** | Died: `Autocompact is thrashing: the context refilled to the limit within 3 turns of the previous compact, 3 times in a row.` Produced **no verdict file**. |
| run3 | 0 | Scoped prompt with small-output discipline and a mandatory file target. **Produced the table above.** |

run1 and run2 are kept (`verifier-run1.log`, `verifier-run2.log`) because a run
that produced no usable verdict is part of the record, not something to quietly
drop. Only run3 is cited as evidence.

## Status change

| Item | Before | Now |
|---|---|---|
| Independent verification | BLOCKED (self-verification only) | **DONE — 5/5 PASS via headless CLI, adversarial probe included** |
| Subagent delegation on this host | blocked | **still blocked** — needs an operator config change, named below |

**Operator action to restore subagents:** point `modelRoles.advisor` and
`modelRoles.plan` at a live route (e.g. `omniroute/cc/claude-opus-5`), or set
`task.agentAdvisor.task: "off"`. I did not edit `~/.omp/agent/config.yml` — it is
operator configuration outside this repository.
