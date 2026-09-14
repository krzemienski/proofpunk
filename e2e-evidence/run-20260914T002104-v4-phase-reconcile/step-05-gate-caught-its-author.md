# step-05 — The new gate caught me, within the hour

## What happened

After committing `f546cfd`, I re-ran the gate suite with a bash loop that
wrote its captures to `gates-after/` — a directory whose contents that same
commit had just made **tracked**. The loop rewrote 13 committed captures.

`verify-evidence-immutability.py` returned **rc=1** and named every one:

```
gates-after/verify-evidence-immutability.log: REWRITTEN 217B -> 613B
gates-after/verify-mutation-artifact.rc:      REWRITTEN 1B -> 2B
gates-after/verify-orchestration.rc:          REWRITTEN 1B -> 2B
...
VERDICT: FAIL
```

The `1B -> 2B` shape on every `.rc` file is the mechanism in miniature:
Python's `write_text(str(rc))` emits a bare digit; bash's `echo "$rc"` appends
a newline. A one-byte difference, invisible to a human skim, correctly
reported as a modified capture.

## Why this is the strongest evidence the gate works

The defect this gate was written for — an unscoped run overwriting sealed
captures — **recurred within the hour, committed by the gate's own author, in
a different tool, by a different mechanism.** The gate caught it anyway.

That is a stronger result than the synthetic mutation test in `step-03`. The
mutation test proves the gate *can* fail. This proves it fails on a real,
unplanned mutation that a careful operator produced by accident while trying
to do the right thing.

## Disposition — obey the rule, never weaken the gate

Two paths were available:

1. Add `gates-after/` to an exclusion list, or relax the check to ignore
   trailing-whitespace differences.
2. Restore the sealed captures and write the re-run somewhere new.

**Path 1 is the defect class this repository has recorded four times**:
weakening a gate so a run goes green. Rejected. A trailing-newline exemption
would also have blinded the gate to genuine one-byte truncations.

Path 2 taken:

| Step | Command | Result |
|---|---|---|
| Restore | `git checkout -- .../gates-after/` | modified captures: **0** |
| Re-run to a NEW directory | 13 gates → `gates-rerun-post-commit/` | **13 green, 0 failed** |

`printf '%s'` replaced `echo` for the `.rc` files so exit codes are written
byte-identically to the original Python captures — the exit code is still
recorded separately from stdout, and still never piped.

## Result

All 13 hermetic gates rc=0 at this tree state, with every previously
committed capture byte-identical to HEAD.

Evidence: `gates-rerun-post-commit/*.{log,rc}`
