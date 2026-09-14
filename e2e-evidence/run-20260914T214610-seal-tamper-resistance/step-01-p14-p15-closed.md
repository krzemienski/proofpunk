# P14/P15: seal is now tamper-RESISTANT, not merely tamper-evident
utc : 2026-09-14T21:46:10.773061Z
HEAD: f1d2147

## The blocker, quoted from the repo's own status report

proofpunk-v4-status-report.md:75-83 named this as open and as the reason P14
and P15 are not closed:

    "seal recomputes every digest from what is on disk, so the sequence
     seal -> edit -> seal always yields a run that validates. Sealing is
     tamper-evident only against an edit *not* followed by a re-seal. ...
     That is a real product improvement this session did not make."

Two criteria hung on it: P14 UNVERIFIED (no run could be cited as honestly
sealed) and P15 FAIL (a sealed run had been mutated). The report's own
conclusion: "Why this is not a release."

## Reproduced before fixing — rc=0 -> rc=0, the defect transition

    init-run; write step-01 (substantial, fresh)
    seal      rc=0
    validate  rc=0        <- clean baseline, so the next result means something
    overwrite step-01 entirely
    seal      rc=0
    validate  rc=0        <- TAMPER LAUNDERED

A first probe was INCONCLUSIVE: validate returned 2 on the first seal (stale
mtime), so "refused" could not be distinguished from "invalid anyway". It is
recorded because a probe that cannot see its subject is the failure mode this
whole session kept hitting. The clean-baseline rerun above is the real one.

## Root cause

fresh_evidence.py:136 — cmd_seal rebuilt every row from disk and overwrote the
inventory unconditionally. validate compares disk against the inventory and was
always correct; the record it compares against was being erased by the act of
re-recording it.

## Fix

cmd_seal now reads the existing inventory first. If a step's size+sha256 differ
from what was already sealed, it REFUSES (exit 2) and names each mutated file
with both digests. Appending a NEW step is untouched — that is the normal
workflow, and the evidence contract's remedy for a wrong artifact is to
supersede it with a new one so a reader sees both.

## Driven proof, both arms

    A) tamper:  seal rc=0, validate rc=0, overwrite, seal -> rc=2 REFUSED
                "refusing to re-seal: these artifacts were MODIFIED after
                 sealing, and re-sealing would erase the original record"
    B) append:  seal rc=0, add step-02, seal rc=0, validate rc=0
                no regression to the legitimate path

Both arms matter: a fix that refused everything would also "pass" arm A.

## Blast radius

All 14 gates rc=0, captured unpiped. Every gate in this repo writes evidence
through this helper, so the append path is exercised repo-wide by that run.

## Honest scope

This closes the named product defect. It does NOT by itself convert P14/P15 to
PASS in the status report: those verdicts also rest on historical runs that
were mutated, and history cannot be un-mutated. What is now true is that the
mutation this report disclosed can no longer be performed silently.
