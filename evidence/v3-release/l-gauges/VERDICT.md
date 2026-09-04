# VERDICT — gauge-report.py mutation proof (Phase 5 / gauge board tooling)

Date: 2026-09-04 | Repo HEAD: `9963648` (working tree dirty — Phase 5 pre-work adopted)

## What this proves

Two independent mutations against `tools/gauge-report.py`, each reverted to a
byte-identical restore, demonstrating the tool cannot produce a false PASS:

1. **Evidence-path mutation** — one gauge's cited artifact path is redirected
   to a nonexistent file. The gauge that was PASS at baseline flips to
   UNVERIFIED **by name**, the summary count drops, and the process exit
   code stays non-zero.
2. **Threshold mutation** — one gauge's PASS/UNMET comparison is corrupted
   to an impossible-to-satisfy condition. The gauge that was PASS at
   baseline flips to UNMET **by name**, the summary count drops further,
   and the exit code stays non-zero.

Both mutations are reverted; the restored output is **byte-identical** to
the pre-mutation baseline capture (verified below, not merely asserted).

## Arms

| Arm | rc | PASS count | Notes |
|---|---:|---:|---|
| step-01 baseline | 1 | 4/8 | honest state today: 4 gauges PASS, 4 UNMET/UNMEASURED |
| step-02 mutated (missing artifact) | 1 | 3/8 | gauge #6 (L14) flips PASS -> UNVERIFIED by name |
| step-03 restored | 1 | 4/8 | byte-identical to step-01 (sha256 match, see evidence-inventory.txt) |
| step-04 mutated (impossible threshold) | 1 | 3/8 | gauge #1 (L12) flips PASS -> UNMET by name |
| step-05 final restored | 1 | 4/8 | byte-identical to step-01 (sha256 match, see evidence-inventory.txt) |

Exit codes captured separately from stdout in every arm's own `.rc` file —
never through a pipeline, per the constraint that a piped capture records
the wrong process's exit code.

## Discrimination check (mutation-proof requirement)

- step-01 and step-04 differ: baseline shows `[PASS] #1 ... 18/18`; mutated
  shows `[UNMET] #1 ... 18/18` — the mutation is named, not silent.
- step-01 and step-02 differ: baseline shows `[PASS] #6 ... 18`; mutated
  shows `[UNVERIFIED] #6 ... None` — the mutation is named, not silent.
- step-01, step-03, step-05 stdout logs share sha256
  `8ee61983789c2f65a2d52d01087f6d45469fd3054809334944d47c510f46c7e6` —
  restore is exact, not approximate.

## Finding this mutation test surfaces about the tool itself

`gauge-report.py` correctly treats **UNVERIFIED evidence** and **UNMET
targets** as distinct failure classes (both non-zero exit, both block
`VERDICT: PASS`, but reported with different status strings so a reader
can tell "the number is bad" from "the proof of the number is missing").
No gate in this tool can pass silently: every one of the 8 gauges appears
in the printed table and the JSON payload on every run, whether it passes
or not.

## Acceptance mapping

- `docs/v3-gauges.md` exists with real measured values or explicit
  UNMEASURED — see that file.
- `gauge-report.py` exits non-zero while gauges are unmet (today's honest
  state: 4/8 PASS, rc=1 in every captured arm above).
- Every gauge cites its evidence by `path@sha256` — see `gauge-report.md`
  and `gauge-report.json` at repo root, and the Evidence column of
  `docs/v3-gauges.md`.
- Mutation logs saved: this directory, `step-01` through `step-05`,
  `evidence-inventory.txt` sha256-manifested.
