# step-03 — The gate surface at HEAD, before and after, plus a fresh install

## Gate surface: 15 gates, measured twice

Every gate run unpiped, exit code captured separately from stdout, per the
standing doctrine that a piped `$?` reports the last stage of the pipeline
rather than the command under test.

| Gate | rc BEFORE fixes | rc AFTER fixes |
|---|---|---|
| `verify-orchestration.py` | 0 | 0 |
| `verify-citations.py` | 0 | 0 |
| `verify-harness-integrity.py` | 0 | 0 |
| `verify-router-links.py` | 0 | 0 |
| `verify-mutation-artifact.py` | 0 | 0 |
| `verify-lane-contracts.py` | 0 | 0 |
| `verify-shipped-vs-active.py` | 0 | 0 |
| `verify-proof-vocab.py` | 0 | 0 |
| `verify-counts.py` | 0 | 0 |
| `verify-evidence-immutability.py` | 0 | 0 |
| `test-hooks.sh` | 0 (`HOOK TEST FAILS: 0`) | 0 |
| `test-installer.sh` | 0 (`INSTALLER TEST FAILS: 0`) | 0 |
| `dry-run-install.sh` | 0 (`INSTALL DRY-RUN FAILS: 0`) | 0 |
| `shellcheck` (10 hook scripts) | 0 | 0 |
| **`gauge-report.py`** | **1 — `VERDICT: FAIL — 1 gauge(s) block release: #4 UNMET`** | **0 — `VERDICT: PASS`** |

Raw logs and `.rc` files: `gates/` (before) and `gates-after/` (after).

The fourteen hermetic gates were green in **both** columns. Only the gauge board
disagreed, and only about gauge #4. That is the entire visible signal that
anything was wrong — which is why the defect in `step-02` had survived.

## `shellcheck` is present on this host

The ledger's `still_blocked` list carried:

> `"shellcheck ABSENT on host — improvement I10 cannot be driven"`

Measured this run:

```
$ shellcheck --version
version: 0.11.0
```

It is installed, and it is already wired into CI at `3b6a7f9` scoped to the ten
hook scripts. Driven here: **10/10 clean, rc=0**. That ledger blocker is stale
and is retracted in `step-05`.

## Fresh install into a clean HOME

```
$ H=$(mktemp -d)
$ HOME="$H" bash tools/proofpunk-install.sh --source-dir "$PWD" --hooks
rc=0
```

### Canonical parity — derived from `hooks.json`, not asserted

```
events  want 7  got 7  drift NONE
regs    want 12 got 12 drift NONE
scripts want 10 got 10 drift NONE
```

Both lists are derived from `hooks.json` and compared against the `settings.json`
the installer actually produced. This is the check that closes the `a41591a`
defect class (installer hardcoded its hook list, shipping 6 of 7 scripts and 4 of
6 events).

Per-event registrations in the produced `settings.json`:

```
SessionStart: 1   Stop: 1   SubagentStop: 1   PreToolUse: 5
InstructionsLoaded: 1   PostToolUse: 2   PostToolUseFailure: 1
total: 12
```

All three `Write|Edit` guards and both Bash hooks are present.

### Skills

```
$ ls "$H/.claude/skills" | wc -l
20
$ ls -d "$H"/.claude/skills/*/SKILL.md | wc -l
19
```

19 skills plus the `proofpunk-doctrine` bundle (19 reference files), which is a
bundled doctrine directory rather than a skill — it correctly has no `SKILL.md`.

### Citations in the installed tree

```
reference citations: 137 total, 0 unresolved
```

A first pass of this check reported "0 total, 0 unresolved" — a **vacuous
result**, because the pattern only matched markdown-link syntax `(path.md)` and
the installed skills cite references in backtick/bare form. Recorded because a
zero-denominator check that reports success is exactly the harness class this
repo keeps finding. The corrected pattern finds 137 and resolves all of them.

A broader pattern additionally matched 28 "unresolved" paths — `SUMMARY.md`,
`NAME.md`, `PLAN.md`, `PROMPT.md`, `audit-report.md`. Each was inspected in
context and is an **output filename the skill instructs you to write**, not a
citation:

```
| PIPELINE | `.prompts/<NN>-<stage>/PROMPT.md` per stage | `SUMMARY.md` per stage after execution |
- **Every stage gets a SUMMARY.md** — the contract that lets later stages
```

Counting those as broken citations would have been a false finding.

### Installer `--verify` and idempotency

```
$ HOME="$H" bash tools/proofpunk-install.sh --verify
rc=0    verify     : all skills pass
        == summary: 0 installed, 0 replaced, 19 skipped (collision), 0 missing ==

$ HOME="$H" bash tools/proofpunk-install.sh --source-dir "$PWD" --hooks   # second run
rc=0    registrations: 12 -> 12
```

Idempotent: a re-run does not duplicate registrations — the per-command
idempotency fixed at `99c72fb` still holds.
