# step-03 — A sealed-evidence defect, its root cause, and the gate that now catches it

**Proof level: script (the gate is a script; its subject is the real repository tree).**

## The defect, found by measurement

At HEAD `63727e1`, `git status` reported **15 modified tracked files** under
`evidence/v3-release/l16-commands/` — committed captures, rewritten in place
in the working tree.

| Capture | Sealed (HEAD) | Mutated | Shape |
|---|---|---|---|
| `cmd_slash_implement.plugin.log` | 13706B | 477B | **truncated — a green capture replaced by a crash log** |
| `cmd_slash_implement.plugin.rc` | `0` | `2` | **verdict flipped** |
| `cmd_slash_install.plugin.log` | 30991B | 57771B | rewritten |
| `command-surface-proof.json` | 44842B | 83394B | rewritten |
| *(11 more)* | — | — | rewritten |

Total: 15 files, 3980 insertions, 1202 deletions.

`evidence/AGENTS.md` states the rule this violates: *"never edit, backfill, or
'clean up' captures — a modified capture is a fabricated claim."*

**Thirteen gates ran green across this state.** None of them compares a
capture against the blob that was committed, so the single defect class the
evidence tree exists to prevent was the one class no gate could observe.

## Root cause — read from source, not inferred

`tools/verify-command-surface.py` (pre-fix, lines 88-96):

```python
# ... a partial/failed run against the canonical path overwrites
# sealed logs from the last green run, so full verification runs use the
# override and promote to canonical ONLY on a complete green run ...
OUT_DIR = os.environ.get("PP_CMDSURFACE_OUT_DIR") or os.path.join(
    ROOT, "evidence", "v3-release", "l16-commands")
```

The comment describes the safe convention **and the code does the opposite**:
absent the environment variable, the default *is* the sealed canonical path.
The convention was documentation only — any unscoped invocation overwrote
sealed captures, exactly as the comment predicted. The failed V6 run
(`step-01`) was such an invocation.

## Fix 1 — the writer fails closed

`OUT_DIR` now defaults to a timestamped `e2e-evidence/cmdsurface-<UTC>`
directory, and an explicit attempt to target the sealed path exits non-zero
before any write.

| Arm | Command | rc | Decisive output |
|---|---|---|---|
| Explicit sealed path | `PP_CMDSURFACE_OUT_DIR=evidence/v3-release/l16-commands python3 tools/verify-command-surface.py --help` | **1** | `refusing to write into sealed evidence: evidence/v3-release/l16-commands` |
| No override | module import, `OUT_DIR` read | **0** | `/Users/nick/proofpunk/e2e-evidence/cmdsurface-20260914T143749` |

Sealed captures modified by either arm: **0**.
Evidence: `t2-outdir-failclosed/armA-sealed-refused.{log,rc}`,
`t2-outdir-failclosed/armB-default-outdir.log`

## Fix 2 — `tools/verify-evidence-immutability.py`

A Class-1 detector for the class itself: every tracked file under `evidence/`
and `e2e-evidence/` must be byte-identical to its committed blob.

### Mutation test — the gate is proven able to fail

The mutation reproduces the real incident: truncate a committed capture to a
crash line.

| Arm | State | rc | Decisive output |
|---|---|---|---|
| 1 | clean tree | **0** | `PASS evidence-immutability: 1583 committed captures byte-identical to HEAD` |
| 2 | `cmd_slash_implement.plugin.log` truncated to 30B | **1** | `evidence/v3-release/l16-commands/cmd_slash_implement.plugin.log: TRUNCATED 13706B -> 30B` / `VERDICT: FAIL` |
| 3 | restored | **0** | `PASS evidence-immutability: 1583 committed captures byte-identical to HEAD` |

`0 → 1 → 0`, with the failing arm naming the exact file and the exact shape.
Reverting the fix turns the gate red; restoring returns it to green
byte-identically. The victim file was restored in a `finally` block and
verified byte-identical to the original.

`mutation_test tools/verify-evidence-immutability.py: baseline rc=0, mutated_rc=1 (TRUNCATED 13706B -> 30B), restored byte-identical rc=0 — green -> red -> green`

Evidence: `t3-evidence-immutability/arm{1,2,3}-*.{log,rc}`

### What this gate CANNOT observe — stated, not glossed

- **Untracked files.** New captures are how evidence is supposed to arrive;
  the gate is deliberately silent on them.
- **A mutation that is already committed.** Once a bad edit is committed,
  HEAD and the worktree agree and this gate goes quiet. It guards the window
  between mutation and commit — where the measured incident lived. Catching a
  committed mutation needs history analysis this gate does not perform.
- **Whether a capture's content is truthful.** Byte-identical to HEAD is the
  entire claim.
- **A ref-less/detached state** where HEAD cannot resolve: reported as an
  error (rc=2), never as a pass.

## Restoration — nothing destroyed

The 15 mutated files were **copied to
`mutated-captures-preserved/` before restoration**, so the crashed run's
output survives as its own artifact rather than being deleted. The sealed
captures were then restored with `git checkout --`, and all **26** tracked
files in that directory verified byte-identical to their committed blobs.

No historical capture was modified to make any gate pass. The restoration
moved captures *back* to their committed state; it did not edit them.

## Gate suite after both fixes

13 gates run, exit codes recorded separately from stdout, never piped:

`verify-evidence-immutability` **0** · `verify-shipped-vs-active` **0** ·
`verify-counts` **0** · `verify-orchestration` **0** ·
`verify-harness-integrity` **0** · `verify-citations` **0** ·
`verify-router-links` **0** · `verify-proof-vocab` **0** ·
`verify-lane-contracts` **0** · `verify-mutation-artifact` **0** ·
`test-hooks` **0** · `test-installer` **0** · `dry-run-install` **0**

`bash -n` over all hook scripts and shell tools: **0 failures**.

`verify-mutation-artifact.py` initially returned **1** against the new gate —
correctly, since no mutation artifact existed yet. This document is that
artifact; it is not a workaround for the detector but the evidence it
requires.

Evidence: `gates-after/*.{log,rc}`
