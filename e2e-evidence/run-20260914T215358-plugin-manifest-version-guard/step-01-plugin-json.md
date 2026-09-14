# plugin.json is NOT missing — my probe looked in the wrong directory
utc : 2026-09-14T21:53:58.009732Z
HEAD: 8b29394

## The advisory, and why its premise was wrong

An advisory reported that AGENTS.md names `.claude-plugin/plugin.json` as a
release-parity target but "that file does not exist", citing MY probe, which
printed `(absent)` for both root-level paths. The proposed remedy was to
resolve the doc or the missing manifest before the v4 sweep.

Measured: the manifests DO exist.

    plugins/proofpunk/.claude-plugin/plugin.json   4.0.0
    plugins/proofpunk/.omp-plugin/plugin.json      4.0.0
    plugins/proofpunk/package.json                 4.0.0

My earlier probe hard-coded ROOT/.claude-plugin/plugin.json. The manifests
live UNDER plugins/proofpunk/. The probe could not see its subject and
reported absence as a defect — the same instrument failure this session has
now produced five times, and this instance nearly caused a DOC FIX DELETING A
CORRECT INSTRUCTION. That is worse than the original false alarm: it would
have removed a true release requirement on the strength of a bad probe.

## What was actually wrong

Two real things, neither the advisory's hypothesis:

1. My new version-parity check (8b29394) only covered the two ROOT marketplace
   catalogs. The two per-plugin manifests — the files AGENTS.md actually names
   — were unguarded. Four version fields guarded, two missed.

2. AGENTS.md wrote the path as `.claude-plugin/plugin.json`, which reads as
   repo-root and is what sent the probe astray. Ambiguous, not false.

## Fix

- check_marketplace_counts() now also compares both per-plugin manifests.
- AGENTS.md names all four full paths and cites the gate that enforces them.

mutation_test verify-counts.py plugin-manifest arm: baseline rc=0 -> named
mutation (plugins/proofpunk/.claude-plugin/plugin.json version -> 3.9.9) ->
mutated_rc=1 naming the file and both versions -> restored byte-identical
(git diff --stat empty) -> rc=0.

All 14 gates rc=0, captured unpiped.

## Standing correction

No drift existed in these files. This is a guard, not a repair. Said plainly
because the session's running score of "defects found" should not absorb a
finding whose real content is "my instrument was broken."
