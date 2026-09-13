# step-22 — two provenance distinctions worth stating exactly

## 1. README/INSTALL: historical examples vs a live count

The version sweep touched release-facing docs. Measured what actually
changed across f5a5204..HEAD:

    README.md        commits touching it: 0
    tools/INSTALL.md commits touching it: 1

The single INSTALL edit:

    -This installer ships 19 skills backed by 17 shared doctrine references
    +This installer ships 19 skills backed by 18 shared doctrine references

A LIVE count (the tree holds 18 references), not a tag example.

Every historical tag reference is intact and was never touched:

    README   "only `v2.1.0` and `v2.2.0` exist"        intact
    INSTALL  "--ref v2.2.0"                            intact
    INSTALL  "v1.8.0 and v3.0.0 do NOT resolve"        intact

Those describe which tags resolve TODAY, and they stay true precisely
because v4.0.0 is uncut. Rewriting them would have made the docs lie.

## 2. Captured artifact vs verification run — NOT the same claim

evidence/v4-release/gates-da38a8c-20260913T091119Z/ contains five output
files. Those were produced at **da38a8c**, and that capture does NOT
include a dry-run-install artifact.

Separately, a COMPLETE suite was RUN from a clean archive of **398d9ef**,
and that run did include dry-run:

    verifiers 9/9 · hooks 0 · installer 0 · dry-run 0
    integrations 36/36 · bash -n clean over 14 files

The ledger's V15 block reason cites the 398d9ef run. It must not be read
as a claim about the da38a8c artifact, which captured four gates plus
integrations and no dry-run file.

Stated because the difference is easy to blur and impossible to recover
later: a captured artifact proves what it contains, a verification run
proves what it executed, and citing one as the other is how evidence
quietly becomes wrong.

## What this changes
Nothing about the verdicts. V15 stays BLOCKED on P6, P8 and P14/P15;
operator reinstall remains explicitly NOT a release prerequisite.

VERDICT: PASS — provenance recorded at the resolution the distinction
requires.
