# step-10 — Command injection in the installer (CWE-78), found and closed

**Severity: HIGH. Arbitrary command execution from an installer flag.**
Found because `shellcheck` was installed and finally run — the improvement
(I10) that had been recorded as undrivable.

## The vulnerability

`tools/proofpunk-install.sh` line 61, before:

```sh
run()  { if [ "$DRY_RUN" -eq 1 ]; then say "  [dry-run] $*"; else eval "$@"; fi; }
```

Every one of the 11 call sites passed a **string** with its variables
single-quoted:

```sh
run "mkdir -p '$DIR'"
```

A single quote inside `$DIR` closes that quoting, and `eval` executes whatever
follows. `--dir` is user-supplied.

`shellcheck` flagged it as **SC2294** — *"eval negates the benefit of
arrays"* — which reads like a style note. It is not.

## Driven, not theorised

```
bash tools/proofpunk-install.sh \
  --dir "/tmp/pptest/a'\$(touch /tmp/PWNED_PROOFPUNK)'b" \
  --source-dir "$PWD" --only brainstorm --no-doctrine
EXIT:1
```

```
ls /tmp/PWNED_PROOFPUNK  ->  /tmp/PWNED_PROOFPUNK
INJECTION CONFIRMED
```

The injected `touch` executed. The install log shows the mechanism plainly:
the subshell ran, then the real directory was never created —

```
tools/proofpunk-install.sh: line 305: cd: /tmp/pptest/a'$(touch /tmp/PWNED_PROOFPUNK)'b/brainstorm: No such file or directory
```

Any command would have run, with the invoking user's privileges. This is the
documented install path (`--dir PATH  any explicit directory`), not an
internal one.

## The fix — remove `eval`, do not escape harder

```sh
run()  {
  if [ "$DRY_RUN" -eq 1 ]; then
    say "  [dry-run] $*"
  else
    "$@"
  fi
}
```

All 11 call sites converted from quoted strings to real argv:

```sh
run mkdir -p "$DIR"
run mv "$dst" "$bak"
run rm -rf "$dst"
...
```

The shell never re-parses a path, so metacharacters in **any** argument are
inert by construction rather than by careful quoting maintained at 11 sites.
Escaping the inputs instead would have left the next call site one missing
quote away from the same bug.

## Verification — same attack, before and after

| Arm | Command | rc | `/tmp/PWNED_PROOFPUNK` | Outcome |
|---|---|---|---|---|
| **Before** | injection `--dir` | **1** | **created** | **INJECTION CONFIRMED** |
| **After** | byte-identical command | **0** | **absent** | **INJECTION BLOCKED** |

After the fix the install *succeeds*, treating the hostile string as a literal
directory name:

```
  INSTALL brainstorm
  ✓ brainstorm
== summary: 1 installed, 0 replaced, 0 skipped (collision), 0 missing ==
```

`ls /tmp/pptest/` shows the literal directory `a'$(touch ` — data, not code.

## No regression

| Check | Command | rc |
|---|---|---|
| Syntax | `bash -n tools/proofpunk-install.sh` | **0** |
| Normal install, clean HOME | `--target claude-code --source-dir .` | **0** |
| Installer harness | `bash tools/test-installer.sh` | **0** |
| Dry-run harness | `bash tools/dry-run-install.sh` | **0** |

## Shellcheck sweep — the rest of the surface

**10/10 hook scripts clean.**

One finding in `stop-guard.sh` is a **false positive**, verified by
reproduction rather than dismissed:

```
SC1007: Remove space after = if trying to assign a value
  _hookdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
```

`CDPATH= cd` is the deliberate POSIX idiom for scoping an empty variable to a
single command. Driven:

| Command | Result |
|---|---|
| `CDPATH=/tmp/cdpathdemo/decoy bash -c 'cd -- sub && pwd'` | `/tmp/cdpathdemo/decoy/sub` — **wrong directory** |
| `CDPATH=/tmp/cdpathdemo/decoy bash -c 'CDPATH= cd -- sub && pwd'` | `/tmp/cdpathdemo/real/sub` — correct |

Without the idiom, `cd` resolves through `CDPATH` and silently lands
elsewhere, which would point `helper` at the wrong `intent_verdict.py`.
Removing it would **introduce** a bug. Left as-is.

Remaining `tools/proofpunk-install.sh` notes (SC2329 unused function, SC2181
`$?` style, SC2015 `A && B || C`) are style-level, not security, and are not
changed in this commit.

## Why this sat undetected

`shellcheck` was absent from the host, so improvement I10 was recorded as
undrivable across multiple releases. `bash -n` passes on this code — the
syntax is valid; only the **semantics** are dangerous. No other gate reads
shell for injection patterns. The installer harness never passed a hostile
path, so it exercised the vulnerable line thousands of times without
triggering it.

Evidence: `/tmp/inject.log` (before), `/tmp/inject2.log` (after) — both
reproduced here; installer diff in this commit.
