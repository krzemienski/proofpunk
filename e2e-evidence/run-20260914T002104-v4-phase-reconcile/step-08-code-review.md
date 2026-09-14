# step-08 — Adversarial code review of this session's product changes

Scope: `63727e1..9366214`, product code only — **206 insertions across 4
files**. Method: execute the code against hostile inputs, not read it for
intent.

| File | Δ |
|---|---|
| `tools/verify-evidence-immutability.py` | +138 (new) |
| `tools/verify-command-surface.py` | +51 / −8 |
| `.github/workflows/gates.yml` | +8 |
| `docs/skill-canon.md` | +12 / −3 |

## Finding 1 — `verify-evidence-immutability.py`: 4 hostile cases, all held

| # | Attack | Expected | Result |
|---|---|---|---|
| F1 | Run from an unrelated cwd | `ROOT` anchoring holds | **rc=0 PASS** — anchored on `__file__`, not cwd |
| F2 | Run with `GIT_DIR=/nonexistent` | fail closed, never green | **rc=2** `cannot resolve HEAD; refusing to report a pass` |
| F3 | Delete a tracked capture | detect as deletion | **rc=1**, `cmd_slash_verify.plugin.rc: DELETED` |
| F4 | **Stage** a mutation with `git add` | still FAIL | **rc=1** |

F4 is the one worth calling out. `git diff --name-only` *without* `HEAD`
compares worktree-to-index, so `git add` would hide a mutation completely.
The gate uses `git diff --name-only HEAD`, which compares against the
**commit**, so staging does not launder a bad edit. That was correct by
construction rather than by luck, but it was unverified until now.

Every victim file was restored and confirmed byte-identical.

**Verdict: no defects.** Three independent fail-closed paths (`rc=2` on git
error, on missing capture root, on zero tracked captures) mean the gate
cannot report a vacuous pass.

## Finding 2 — `_TRANSIENT_RE`: the higher-risk change, tested for over-reach

A retry regex that is too broad silently converts real failures into retries.
Six cases through the **real** `is_transient_harness_error()`:

| Case | Want | Got |
|---|---|---|
| `pass=False`, skill not used | False | **False** |
| `pass=False`, wrong marker | False | **False** |
| `pass=False`, model ResultError | False | **False** |
| `pass=False`, model text says "failed with exit code 1" | False | **False** |
| Real harness `ProcessError` | True | **True** |
| `rate_limit_error 429` (pre-existing shape) | True | **True** |

**0 misclassifications.**

The decisive one: model text quoting *"Fatal error in message reader"* verbatim
returns **False**. The `reply` field is deliberately excluded from the search,
so a model explaining an error class cannot be mistaken for host contention.
The new shape did not weaken that guard.

## Finding 3 — a false positive I raised against myself

A substring check reported `verify-command-surface in CI: True`, which would
be a real defect: that harness needs live credentials and has a **52-minute**
worst case (`RETRY_MAX=3` × `RETRY_BACKOFF_S=90` × 15 arms = 45 min of backoff
on top of the observed 6.8-minute run). CI is documented as hermetic.

Grepping the file showed the only occurrences are inside **my own comment**
at lines 103-106. It is never a `run:` step. **CI remains hermetic and
credential-free.**

This is the second time this session a substring/count check produced a false
finding (the first: `grep -c harness_error` counting a schema key on passing
runs). Both were caught by reading the actual structure instead of trusting
the count. Noted as a recurring instrument weakness, not a code defect.

## Finding 4 — the new gate is hermetic

`urllib`, `requests`, `ANTHROPIC`, `API_KEY`, `http`: **none present**.
Stdlib + `git` subprocess only, so it is safe in CI where it is wired.

## Security review

| Check | Result |
|---|---|
| Credentials in tree | **0 files** (omniroute key and operator token both) |
| Credentials in git history | **0 commits** (both) |
| Credentials in this run's evidence | **0 files** |
| Secret values printed | Never — only `len=` and a 7-char prefix |
| Shell injection surface | None: `subprocess.run` with list args, `shell=False` |
| Path traversal | Paths come from `git ls-files`/`git diff`, not user input |
| Destructive operations | `git checkout --` on files whose mutated content was preserved first |

## Residual risk — stated, not resolved

**The retry path has never executed.** `attempt2+ files = 0` in the green run.
The regex is proven discriminating at function level, but a same-run
`attempt1` FAIL → `attempt2` PASS has still not been observed. If the retry
mechanism itself is broken in some way the function-level test cannot reach,
this session's green 6/6 would not reveal it.

This is recorded in `step-07` and reported as **UNPROVEN**, not as a pass.

## Verdict

**No blocking defects.** One recurring instrument weakness (substring checks
producing false findings) worth watching. One residual unknown (retry path)
already disclosed at its correct proof level.
