# F-003 — three competing proofpunk sources live on this host

Recorded: 2026-09-07T01:54:55Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee

## Measured

`omp plugin list`:
```
truth-forge@truth-forge (1.7.0) (user)
proofpunk@proofpunk  (2.2.0) (user)
```

Plus 19 live user-level skill dirs in `~/.omp/agent/skills/` (18 skills + `proofpunk-doctrine`).

| source | version | skills | precedence (A9 measured) |
|---|---|---|---|
| `~/.omp/agent/skills/` user-level | unversioned | 18 + doctrine | **native = 100 (WINS)** |
| `proofpunk@proofpunk` plugin | 2.2.0 | 18 | omp-plugins = 90 |
| `truth-forge@truth-forge` plugin | 1.7.0 | 18 incl. **cook**, **functional-validation** | omp-plugins = 90 |

## Consequence 1 — the loaded skill is NOT the plugin

User-level (100) outranks plugin (90). For `implement`:

```
user-level : da44582882e97ca1…  (LOADED)
repo HEAD  : 5ed7370e501388b8…
```

They differ in citation form only:

```
repo HEAD  : `../../references/platform-routing.md`   (repo-relative)
user-level : `references/platform-routing.md`         (installed-flat)
```

Benign in content — but it proves the installer rewrote citations on install, and that the
copy actually loaded on this host is an INSTALLED artifact, not the repo tree. Any claim of
the form "the skill says X" must name WHICH copy was read.

## Consequence 2 — the dead names are not dead

`truth-forge@1.7.0` is the PRE-RENAME plugin (`1fa27b3` renamed truth-forge -> proofpunk).
It is still registered and still ships `cook` and `functional-validation` as LOADABLE skills.

The work order treats these as dead strings surviving in docs and generator source. That is
an understatement: on this host they are live, loadable skills that a bare-name invocation
can reach. Sweeping the strings from `build-site.py` would not remove them.

## Consequence 3 — bare-name invocation is unattributable, confirmed by measurement

Three sources define `implement`. Only namespaced `/proofpunk:...` invocation is attributable.
This validates the work order constraint, and now has a measured basis rather than an assumption.

## Correction to lane A9

A9 reported all 27 entries in `~/.omp/agent/skills/` are dot-prefixed `.bak-*` and therefore
contribute zero live skills. **Refuted by direct measurement:** 19 plain entries are live.
The `.bak-*` dirs (hundreds, back to 2026-08-11) coexist with them. A9 counted only backups.

## Not fixed here

Phase 5, and touching installed dirs needs operator consent.

---

## Update — the stale plugin also owns a live COMMAND surface (verified at source)

`~/.config/opencode/commands/` holds **12** proofpunk-lineage command files, not 6:

```
proofpunk-forge-prompt.md    truth-forge-cook.md
proofpunk-implement.md       truth-forge-forge-prompt.md
proofpunk-install.md         truth-forge-implement.md
proofpunk-rate-prompt.md     truth-forge-rate-prompt.md
proofpunk-truth-audit.md     truth-forge-truth-audit.md
proofpunk-verify.md          truth-forge-verify.md
```

`truth-forge-cook.md` read in full:

```
description: Execute an existing plan or goal under cook execution discipline
argument-hint: "<goal-or-plan-path> [--fast] [--no-test] [--tdd]"

Activate the `cook` skill and run it against: $ARGUMENTS
```

Three separate regressions in one live file:

1. It activates **`cook`** — a skill deleted from proofpunk at `96d91d6` (merged into `implement`).
2. It advertises **`--no-test` and `--tdd`** — flags `implement`'s own SKILL.md explicitly states "no longer exist".
3. It is reachable *today* because `truth-forge@1.7.0` supplies the `cook` skill it names (see the plugin skill list above), so the command is not even a dangling reference — it resolves.

### Why the earlier lane read this as "not reproduced"

A11 correctly found no file named `proofpunk-cook.md` and reported the work order's
claim unreproduced. That is right on the literal string and wrong on the substance:
the orphan exists under the pre-rename prefix. The work order named the wrong file,
not a nonexistent problem.

### Corrected scope

The "sweep dead names from guidance and generator source" lane (L8) is aimed at the
wrong target. Measured:

| target | dead names present? | evidence |
|---|---|---|
| `tools/build-site.py` | **NO** — 0 hits, line 311 is `/proofpunk:install` | my grep + read |
| repo live guidance | **NO** — all 88 hits historical prose | A6 |
| **installed host surface** | **YES** — 6 command files + a live `cook` skill | this finding |

The drift is not in the repo. It is on the host, from a plugin the repo no longer
publishes. No amount of repo-side sweeping removes it; it needs an uninstall, which
requires operator consent per the work order's own authorization boundary.
