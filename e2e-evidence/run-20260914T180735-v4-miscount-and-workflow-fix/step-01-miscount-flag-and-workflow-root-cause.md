# step-01 — A miscount my evidence quoted uncritically, and the workflow bug behind three gate failures

> **Annotates `run-20260914T180615-v4-yield-hypothesis-falsified/step-01`**, which
> is committed at `95548e2` and therefore read-only. Two corrections below apply
> to it. Neither changes its conclusion.

---

## 1. The quoted subagent output contains a wrong count, and I did not flag it

`step-01` of the prior run quotes `YieldShortArm`'s transcript verbatim as
evidence of the yield-call shape:

```
→ glob(.../references/*.md) ⇒ ok · 19 lines
COUNT 19
→ yield({"data":{"count":19}}) ⇒ ok · 1 line
```

**The count is wrong. `references/` holds 18 files, not 19.**

```
$ ls plugins/proofpunk/references/*.md | wc -l
18
```

The subagent read `glob`'s "19 lines" as a file count. That output includes a
header line, so the file count is 18. This is the same off-by-one that the
`ls | wc -l` habit produces, arriving through a different tool.

### Why this matters beyond the number

The quotation was included to show the **shape of the yield call**, and for that
purpose it is valid — the mechanism it demonstrates is unaffected. But the
surrounding text did not flag the error, so a reader of that sealed capture sees
`COUNT 19` and `{"count":19}` presented without comment, in a session whose
entire subject is count drift and which gates `references` at **18**.

Evidence that quotes a wrong number without marking it wrong is evidence that
can be cited for the wrong number later. Flagged here.

### It also illustrates the session's own finding

`YieldShortArm` was reported **`completed`**. Job status told me nothing about
whether its answer was correct — it was not. This is the converse of the
`LiveProbe4` case in the same run (reported `failed`, work correct), and
together they make the point sharper than either alone:

> `completed` does not mean right. `failed` does not mean wrong. Read the
> artifact.

That is already this repo's stated doctrine for subagent results. This session
produced a clean example of both directions.

---

## 2. A competing explanation for the yield failures, tested and rejected

An advisory proposed that **duration** was the real variable: the three
`completed` audits ran for minutes, the failing probes for seconds.

Tested against all eight runs:

| Hypothesis | Failed set | Completed set | Separates? |
|---|---|---|---|
| **Duration** | 16.3, 18.5, **25.0** s | **20.6**, 28.4, 113, 402, 440 s | **No** — the sets overlap |
| **Yield shape** | 3/3 bare `yield(result)` | 5/5 `yield` carrying `data` | **Yes** — 0 counterexamples |

The decisive pair: `LiveProbe4` ran **25.0 s and failed**, while
`YieldShortArm` ran **20.6 s and completed**. A longer run failed and a shorter
run succeeded, so duration cannot be the discriminator.

The yield-shape split remains clean across all eight runs. The advisory's own
premise — that reply *length* was the variable — was already falsified and
retracted in `95548e2`; this rejects the duration successor on the same
evidence-first basis rather than adopting it because it was proposed later.

---

## 3. Root cause of three immutability failures: one workflow mistake, now documented

The immutability gate refused three operations this session:

| Attempt | Gate output |
|---|---|
| Re-seal after committing a run's inventory | `REWRITTEN 744B -> 864B` |
| Same, next round | `REWRITTEN 222B -> 332B` |
| Edit a committed step to retract a claim | `REWRITTEN 9046B -> 9407B` |

Three incidents, **one cause**: I committed a run directory *while the run was
still in progress*, so every subsequent addition to that run became a rewrite of
a committed capture.

Each time I fixed the incident — restore, move to a fresh run, re-seal — and each
time the cause survived to produce the next one. An advisory correctly pointed
out that fixing incidents is not fixing the bug.

### The fix, written where it will be read

Added to `evidence/AGENTS.md`, beside the existing read-only rule:

- **Never `git add` a run directory until that run is finished and sealed.**
  Restoring the inventory alone does not fix it — a manifest that omits files the
  run now contains is a *false* manifest.
- **Corollary:** a finding that arrives after a run is committed goes in a **new**
  run directory with an explicit supersession header naming the superseded step.
  A committed capture is never edited to agree with a later finding; the record
  shows both what was believed and what replaced it.

This file is the first artifact produced under that rule: the corrections above
belong to a committed run, so they live here instead of being edited into it.

---

## What is not changed

- The yield-shape conclusion in `95548e2` stands: bare `yield(result)` serializes
  as null and reports `failed`; `yield` carrying `data` completes. 8/8.
- `references/` = 18 throughout the repo, gated by `verify-counts.py`. No
  documentation anywhere claims 19; the miscount existed only inside a quoted
  subagent transcript.
