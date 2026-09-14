# step-04 — Verification of the committed tree, and an honest note on its independence

## Independence: DEGRADED, stated plainly

The work order requires an independent agent re-derive every count and re-run
every gate without reading the implementing narrative. I dispatched one
(`IndepVerify`). It **failed in 3.9s**:

```
[omniroute/cx/gpt-6-astra] 401 [codex] All 1 connection(s) authentication
expired — please reconnect in the dashboard (type=authentication_error
param=invalid_api_key)
```

This is the **same credential exhaustion** that blocks V6 (`step-01`), on a
different route. Per the standing rule *"three probes of the same
misconfiguration are not three pieces of evidence — they are one, repeated"*,
I did not re-dispatch.

**Everything below is therefore SELF-verification, not independent
verification.** It is re-derived from the tree rather than restated from my
own narrative, but it does not satisfy the independence requirement.
**Independent verification remains OPEN**, blocked on the same credential
capability as V6.

## Canonical inventory — re-derived by walking the tree

| Dimension | Measured at `f546cfd` |
|---|---|
| Skills | **19** |
| Shared references | **18** |
| Commands (Claude) | **7** |
| Commands (OpenCode) | **7** |
| Hook files | **11** |
| Hook event keys | **7** |
| Hook registrations | **12** |
| Distinct hook scripts | **10** |
| Agents | **3** |

Work-order counts (18 / 13 / 6+6 / 10 / 9 registrations, v2.2.0 at `a41591a`)
are **114 commits stale** and are preserved as history, not treated as targets.

### A discrepancy I raised against myself, and resolved

My first parity check reported `cc == oc commands: False`. Investigated rather
than dismissed: OpenCode command files carry a `proofpunk-` filename prefix
(`proofpunk-verify.md` vs `verify.md`) — that is how namespacing works on that
host. `verify-shipped-vs-active.py` strips the prefix before comparing.
**My check was wrong; the gate is right.** 7+7 parity holds.

Similarly, my first installed-tree citation check reported 1 unresolved. It
used a markdown-link regex; skills cite with backticks. Corrected form: **136
citations checked, 0 unresolved.** The repo's own `verify-citations.py`
independently reports 0 ERROR, 0 WARN.

## Claim verification at `f546cfd`

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Every tracked capture byte-identical to HEAD | **PASS** | `git diff --name-only HEAD -- evidence e2e-evidence` rc=0, 0 lines |
| 2 | `verify-command-surface.py` no longer defaults to the sealed path | **PASS** | default is `e2e-evidence/cmdsurface-<UTC>` |
| 3 | Explicit sealed path refuses without writing | **PASS** | rc=1, `refusing to write into sealed evidence`; 0 files modified after |
| 4 | New gate registered in CI | **PASS** | `tools/verify-evidence-immutability.py` present in `.github/workflows/gates.yml` |
| 5 | New gate is non-vacuous | **PASS** | fails closed on zero tracked captures, on missing capture root, and rc=2 on any git error |
| 6 | `docs/skill-canon.md` current totals match live tree | **PASS** | all six numbers (12/10/11/7/18/19) match measurement |

## Fresh install into a clean `mktemp -d` HOME

No credentials were copied into any sandbox — `ANTHROPIC_AUTH_TOKEN`,
`ANTHROPIC_API_KEY`, and `ANTHROPIC_BASE_URL` were **removed** from the child
environment.

| Arm | Command | rc | Result |
|---|---|---|---|
| Bad flag | `proofpunk-install.sh --source-dir . --hooks --yes` | **1** | `ERROR: unknown option: --yes (try --help)` — **correct fail-fast**, nothing installed |
| Skills | `--target claude-code --source-dir .` | **0** | `19 installed, 0 replaced, 0 skipped, 0 missing` |
| Hooks | `--target claude-code --source-dir . --hooks` | **0** | 10 hook scripts copied; settings written |
| Idempotency | same `--hooks` command, 2nd run | **0** | registrations **12 → 12 (STABLE)** |

The `--yes` failure was **my flag error, not an installer defect** — and the
installer behaved exactly as its contract requires: named the bad option,
exited non-zero, installed nothing.

### Produced `settings.json` vs `hooks.json` — zero drift

| | `hooks.json` (canonical) | Installed `settings.json` |
|---|---|---|
| Event keys | 7 | **7** |
| Registrations | 12 | **12** |
| Distinct scripts | 10 | **10** |

Events: `InstructionsLoaded`, `PostToolUse`, `PostToolUseFailure`,
`PreToolUse`, `SessionStart`, `Stop`, `SubagentStop`.
All three `Write|Edit` guards (`no-test-files.sh`, `evidence-guard.sh`,
`capture-guard.sh`) and both Bash hooks (`bash-write-snapshot.sh`,
`bash-write-notice.sh`) are present.

Installed skills: **19**. Installed-tree citations: **136 checked, 0
unresolved**.

Evidence: `t5-fresh-install/install*.{log,rc}`,
`t5-fresh-install/installed-settings.json`,
`t5-fresh-install/installed-citations.txt`

## Gate suite at `f546cfd`

All 13 hermetic gates rc=0, exit codes recorded separately from stdout, never
piped. `bash -n` over all hook scripts and shell tools: 0 failures.

Evidence: `gates-after/*.{log,rc}`

## What is NOT proven here

- **Independent verification** — blocked, credential exhaustion (above).
- **V6 / live slash-command surface** — blocked, same root cause
  (`step-01`). `verify-command-surface.py` was deliberately not run.
- **Published-ref install** — 43 commits are unpushed and no `v4.0.0` tag
  exists. Installing "from the published ref" cannot be verified because the
  ref does not exist. Labeled **blocked**, not passed.
