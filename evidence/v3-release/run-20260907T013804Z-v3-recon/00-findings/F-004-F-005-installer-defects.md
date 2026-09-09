# F-004 — citation bundler: normalization runs before the fixed-point loop

Recorded: 2026-09-07T02:29:22Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee
Source: A4 lane; independently verified at source by orchestrator.

## Mechanism (verified by reading tools/proofpunk-install.sh:291-323)

```
:296-300   depth-normalize files in $dst/references   <-- runs ONCE, FIRST
:306-322   fixed-point bundling loop                  <-- copies NEW files AFTER
:317         cp "$ref" "$dst/references/$name"        <-- never normalized
```

The loop exists because a bundled reference may itself cite further doctrine, so one
pass is not enough (`:303-305` says exactly this). But normalization is not inside the
loop. Any file the loop copies keeps its un-normalized `references/X.md` citations.

## Why the auto-fix then reports a false FAIL

A4 traced `find_bad()` at `:649-652`: its sibling-fallback excludes paths starting
`references/`, so it cannot see the un-normalized citations the loop just introduced.
Auto-fix re-copies an already-present file (a no-op) and still reports FAIL.

## Why it only surfaced now

At HEAD zero skills cite `run-trace-schema.md`. The working tree adds two citations, so
the loop copies it and the un-normalized path ships. A4 reproduced this independently on
a SECOND skill (`--only proofpunk`, whose SKILL.md:99 also cites it), proving F-002 is
not `end-user-testing`-specific: it hits every skill citing a newly-bundled reference.

## Fix shape (NOT applied)

Move normalization inside the loop, or re-run it after the loop settles.

---

# F-005 — test-installer group 10 asserts on an unrelated exit code

## Verified at source (tools/test-installer.sh:241-260)

The parity probe prints three independent results:

```
scripts True []      <- 9/9,  empty symmetric difference
events  True []      <- 7/7,  empty symmetric difference
regs    True 11 11   <- 11/11
```

Then `:256` gates on:

```sh
if [ "$irc" = "0" ] && ! grep -q "False" "$PH/parity.txt"; then
```

`irc` is the exit code of an unrelated FULL install. When that install fails for any
reason — F-002, say — group 10 reports FAIL while every parity sub-check passed.

## Class

Defect class 1: **a harness assertion that cannot report its own subject truthfully.**
It is the inverse of the classic form: not a gate that cannot fail, but one that cannot
PASS independently of an unrelated failure. Same root cause — the assertion is not
scoped to what it claims to measure.

## Evidence it is a false FAIL

A4 re-derived parity against a `--no-verify` isolated artifact: 9/9 scripts, 7/7 events,
11/11 registrations, zero diff. The parity claim group 10 makes is TRUE; its verdict is wrong.

## Fix shape (NOT applied)

Drop `irc` from the conjunction, or scope the install to `--only proofpunk --hooks`.
