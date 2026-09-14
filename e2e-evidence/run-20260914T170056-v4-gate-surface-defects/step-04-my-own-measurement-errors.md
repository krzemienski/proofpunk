# step-04 — Three measurement errors I made, and how each was caught

Recorded because this repository's standing rule is that an honest open item
outranks a green claim that does not survive checking. Each of these produced a
*wrong reading* that I acted on before correcting.

---

## Error 1 — I masked an exit code with a pipe, then blamed the tool

```
$ python3 .../fresh_evidence.py validate --run "$RUN" 2>&1 | tail -10; echo "validate rc=$?"
no .run-meta in e2e-evidence/run-20260914T165003-v4-gate-surface
validate rc=0
```

I read that as **"validate prints a refusal and still exits 0"** — a fail-open in
the evidence validator itself — and began investigating it as a third defect.

It was my error. `$?` after a pipeline reports the exit status of `tail`, not of
`python3`. Re-measured unpiped:

```
$ python3 .../fresh_evidence.py validate --run "$RUN" > out.log 2>&1; echo "UNPIPED validate rc=$?"
UNPIPED validate rc=2
```

`main()` returns 2 on `Refusal` (`fresh_evidence.py:353-355`). The tool was
always correct.

This is the exact trap the CI workflow documents in its own header — *"never pipe
a command whose exit code is reported"* — and I walked into it while auditing for
that class. No product change was made; the correction is the artifact.

## Error 2 — A vacuous citation check that reported success

My first installed-tree citation check returned:

```
citations: 0 total, 0 unresolved
```

Zero unresolved out of **zero examined** is not a pass, it is a check that never
ran. The regex only matched markdown-link syntax `](path.md)`, and the installed
skills cite references in backtick/bare form. Corrected pattern:

```
reference citations: 137 total, 0 unresolved
```

The real result is stronger than the vacuous one — but had the installer been
broken, the first check would have reported green anyway.

## Error 3 — An over-broad pattern that manufactured 28 false findings

Widening the pattern to catch bare `.md` references produced:

```
total 168 unresolved 28
UNRESOLVED ('prompt-forge/SKILL.md', 'SUMMARY.md')
UNRESOLVED ('prompt-forge/SKILL.md', 'NAME.md')
...
```

Reading the surrounding lines settled it — these are **output filenames the skill
instructs the agent to create**, not links to existing files:

```
| PIPELINE | `.prompts/<NN>-<stage>/PROMPT.md` per stage | `SUMMARY.md` per stage after execution |
│   └── SUMMARY.md     # filled after execution: what it produced, key outputs
```

Reporting 28 broken citations would have been a false finding, and "fixing" them
would have damaged working skills.

---

## Why these are in the evidence tree

All three were caught before they reached a conclusion in the completion report,
but two of them (1 and 3) were *acted on* first — I started diagnosing a
non-existent fail-open, and I nearly filed 28 fabricated citation defects. The
pattern in every case is the same: **a measurement instrument that is itself
wrong produces a confident false reading.** That is the same class as the two real
defects this run fixed, applied to my own tooling rather than the repo's.
