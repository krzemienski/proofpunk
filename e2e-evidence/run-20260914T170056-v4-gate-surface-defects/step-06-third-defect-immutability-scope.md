# step-06 — Defect 3: the immutability gate fired on the act of adding evidence

Found while committing this run's own artifacts, which is the only way it could
have been found: the gate only misbehaves when a new run directory is staged.

## Symptom

With this run's 103 new capture files staged:

```
$ python3 tools/verify-evidence-immutability.py ; echo rc=$?
== committed-capture immutability at HEAD 3b6a7f9
   evidence: tracked=408 modified=0
   e2e-evidence: tracked=1786 modified=103

MODIFIED COMMITTED CAPTURES (103):
   e2e-evidence/run-20260914T170056-v4-gate-surface-defects/.run-meta: MODIFIED
   e2e-evidence/.../d-i8-mutation/before.log: MODIFIED
   ...
VERDICT: FAIL
rc=1
```

103 committed captures reported as mutated.

## Measured: none of them were committed

```
$ n=0; a=0
$ for p in $(git diff --name-only HEAD -- e2e-evidence); do
>   n=$((n+1)); git cat-file -e HEAD:"$p" 2>/dev/null || a=$((a+1)); done
$ echo "changed=$n absent_from_HEAD=$a"
changed=103 absent_from_HEAD=103
```

**All 103 are absent from HEAD.** Every one is a brand-new capture created by
this run. Zero real mutations.

## Root cause

`verify-evidence-immutability.py:87` used:

```python
diff = git("diff", "--name-only", "HEAD", "--", root)
```

`git diff HEAD` reports staged **additions** alongside modifications. A path that
does not exist in HEAD has no committed blob, so it cannot have drifted from one
— but the gate treated every reported path as a mutated committed capture.

The gate's own docstring already drew the correct boundary:

> "Anything about UNTRACKED files. A new capture is how evidence is supposed to
> arrive; this gate is silent on it by design."

That silence held only until the capture was **staged**. The moment a run
directory was `git add`ed — the normal, required path for committing
evidence — the gate turned red.

## Why this mattered rather than being cosmetic

This is the same false-alarm shape the gate exists to prevent, pointed at itself.
A gate that fails every time evidence is added correctly gets muted, excluded, or
`continue-on-error`'d — and then the real check it performs (catching a rewritten
capture, the `verify-command-surface.py` incident of 2026-09-14) is gone with it.
The prior run's own note records the discipline of refusing to "add an exclusion
or whitespace exemption" to make this gate pass; the failure mode here is the
pressure to do exactly that.

## The fix

Compare only paths that actually have a committed blob:

```python
candidates = [p for p in diff.stdout.splitlines() if p.strip()]
changed = []
for p in candidates:
    if git("cat-file", "-e", f"HEAD:{p}").returncode == 0:
        changed.append(p)
added = len(candidates) - len(changed)
```

New additions are counted and reported as out of scope rather than silently
dropped, so the number stays visible:

```
   e2e-evidence: tracked=1786 modified=0 (+103 newly added, not in HEAD — out of scope)
```

The docstring's "WHAT THIS GATE CANNOT OBSERVE" section now states the staged-
addition boundary explicitly, with this measurement.

## Mutation proof — the gate must still catch a real mutation

| Arm | Condition | rc | Decisive output |
|---|---|---|---|
| 1 | 103 new captures staged | **0** | `e2e-evidence: tracked=1786 modified=0 (+103 newly added, not in HEAD — out of scope)` |
| 2 | append `TAMPERED` to a **real committed** capture (`evidence/v3-release/l16-commands/command-surface-proof.json`) | **1** | `MODIFIED COMMITTED CAPTURES (1):` / `...command-surface-proof.json: REWRITTEN 44842B -> 44852B` / `VERDICT: FAIL` |
| 3 | restore that file | **0** | `PASS evidence-immutability: 2194 committed captures byte-identical to HEAD` |

Arm 2 is the load-bearing one: the fix narrows scope to paths present in HEAD,
and a genuine rewrite of one of those still fails, names the file, and reports
the byte delta. Arm 3 confirms the worktree was left clean:

```
$ git diff --name-only HEAD -- evidence/v3-release
(empty)
```

## Gate surface after this fix

All 15 gates rc=0: the 10 Python verifiers, `gauge-report.py`, `test-hooks.sh`,
`test-installer.sh`, `dry-run-install.sh`, and `shellcheck` over the 10 hook
scripts. Logs in `gates-final/`.
