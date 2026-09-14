# step-02 — Fifth defect: the gate locked the doctrine it cites

Found by trying to fix defect four. Writing the workflow rule into
`evidence/AGENTS.md` — the rule meant to stop the mistake that had tripped this
gate three times — was itself refused:

```
MODIFIED COMMITTED CAPTURES (1):
   evidence/AGENTS.md: REWRITTEN 1551B -> 2487B
evidence/AGENTS.md: a modified capture is a fabricated claim.
Restore with `git checkout -- <path>` and write new artifacts to a
fresh run-scoped directory instead of rewriting a sealed one.
```

## Why this is a defect and not the gate doing its job

`evidence/AGENTS.md` is **authored doctrine**, not a capture. It is the file the
deny message itself cites (`a modified capture is a fabricated claim` lives at
`evidence/AGENTS.md:22`). The gate had made this repository's evidence doctrine
permanently uneditable, and its own remedy is incoherent for it: you cannot move
a directory-level `AGENTS.md` into "a fresh run-scoped directory."

Two guards disagreed about the same rule. `capture-guard.sh` has always drawn the
line correctly at runtime:

```
SIDECAR_EXTS = {".md", ".json"}          # authored — always allowed
CAPTURE_EXTS = {".txt",".log",".out",".err",".jsonl",".png",".har",".csv"}
```

`verify-evidence-immutability.py` treated **every** tracked file under the
capture roots as a capture. The hook and the gate now agree.

## The fix, and the two wrong versions of it that were rejected

**Rejected — exempt by extension**, i.e. copy `capture-guard.sh` wholesale.
That guard exempts all `.md`/`.json` because it protects a different thing (a
live tool call writing a raw capture). Copying it here would **gut this gate**:
every `step-NN.md` and every `evidence-inventory.txt` protected this session is
`.md` or `.json`. An advisory flagged this and it is correct.

**Rejected — exempt by basename.** `AGENTS.md`/`README.md` anywhere would also
exempt a `README.md` written *inside* a run directory, which is part of that
run's record. One exists today:
`e2e-evidence/run-20260827T162405-ref-differential-pristine/README.md`.

**Adopted — exempt by path.** Only an authored doc at the **top level** of a
capture root, outside any run or release subdirectory:

```python
def is_authored_doc(path: str) -> bool:
    parts = path.split("/")
    return len(parts) == 2 and parts[1] in AUTHORED_BASENAMES
```

`evidence/AGENTS.md` → depth 2 → exempt. Anything deeper stays a capture.
Exempted docs are counted and printed rather than silently dropped.

## Mutation proof — four arms, all required

| Arm | Condition | rc | Decisive output |
|---|---|---|---|
| 1 | `evidence/AGENTS.md` edited | **0** | `evidence: tracked=408 modified=0 (+1 authored doc(s) — not captures)` |
| 2 | committed `step-01-*.md` tampered | **1** | `...step-01-yield-hypothesis-falsified.md: REWRITTEN 4878B -> 4888B` / `VERDICT: FAIL` |
| 3 | `README.md` **inside** a run dir tampered | **1** | `...ref-differential-pristine/README.md: REWRITTEN 1625B -> 1635B` / `VERDICT: FAIL` |
| 4 | all restored | **0** | `VERDICT: PASS`, empty `git status` |

Arms 2 and 3 are the load-bearing ones: they prove the exemption did not widen
into the thing the gate exists to catch. A `.md` capture is still a capture.

## Session tally of this defect class

Five defects now, every one an instrument that could not fail — or one that
failed on the wrong thing:

| # | Instrument | Failure |
|---|---|---|
| 1 | `gauge-report.py` | pinned to a superseded artifact; no later result could move it |
| 2 | `verify-counts.py` | blind to its own entry point (`skills/` excluded wholesale) |
| 3 | `verify-evidence-immutability.py` | fired on *adding* evidence (staged additions read as mutations) |
| 4 | `verify-counts.py` | blind to markdown tables and prose forms |
| 5 | `verify-evidence-immutability.py` | locked the authored doctrine it cites |

Both immutability defects share a shape: the gate was right about the *rule* and
wrong about the *set it applied to*. Neither was found by reading it. Each
surfaced only when the gate was driven against a case nobody had tried —
committing a run, and editing the doctrine.
