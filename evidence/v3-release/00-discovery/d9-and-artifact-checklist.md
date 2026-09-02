# D9 — v3-brief dictation artifacts + named-artifact checklist

Measured 2026-09-02 @ `a41591a`.
Raw: `raw/d9-and-artifact-checklist.txt` (`PY_RC=0`).

## D9 — the three dictation artifacts

Whole-tree scan, every text file, word-boundary match, case-insensitive:

| Term | Hits in tree | Where |
|---|---|---|
| `proofbunk` | **1** | only in my own D-register file (`d1-d2-d4-d9-dictation.md:100`) |
| `rebo` | **1** | only in my own D-register file (`:101`) |
| `furble` | **1** | only in my own D-register file (`:102`) |

Zero occurrences in any product file, manifest, doc, script, or commit-tracked
artifact. The only matches are the rows where this session wrote the terms
down. Self-reference excluded, the true count is **0/0/0**.

### Session-record search — required by the register, now done

Both stores searched for the three terms in genuine operator turns
(role-gated, injected content excluded). Raw:
`raw/d9-session-search.txt` (`PY_RC=0`).

| Store | Files scanned | proofbunk | rebo | furble |
|---|---|---|---|---|
| Claude (`~/.claude/projects/*proofpunk*`) | 97 | 0 | 0 | 0 |
| OMP (`~/.omp/agent/sessions`) | 7,320 | 5 | 5 | (same set) |

**Every OMP hit is today's work order, not an earlier operator turn.** All
five carry identical surrounding text — "ProofBunk, Rebo, and Furble's Claude
are treated as dictation artifacts for D9 to resolve" — and all are dated
`2026-09-02` (`08-31`, `08-18`, `07-19`, plus `__advisor.jsonl:3`). They are
this task's own `<context>` block echoing back through the store.

**Conclusion: the three terms are unattested in the historical record.** No
operator ever said them before this work order. There is nothing to settle
them against.

### Resolutions

| Heard | Resolution | Basis | Confidence |
|---|---|---|---|
| **"ProofBunk"** | **Proofpunk** — RESOLVED | Rename history confirms it: `1fa27b3` (2026-08-11) "v1.8.0: rename truth-forge -> proofpunk", with `c090ff1` "Remove stale `__pycache__` artifact from pre-rename tree" the same day. Origin `20bd199` (2026-08-08) shipped as `truth-forge`. The project has had exactly two names, neither `proofbunk`. | **high** |
| **"Rebo"** | the router head, `skills/proofpunk/SKILL.md` — **UNRESOLVED, standing interpretation** | No file, dir, repo, or operator turn named `rebo` exists. The interpretation fits the described role ("the head links everything"), and D8 independently established the head is a router — but the term itself is unattested, so this remains an assumption, not a finding. | **low-medium** |
| **"Furble's Claude"** | the Claude Code invocation contract, `docs/invocation-contracts.md` — **plausible, term still unattested** | File now read end to end: it is the trigger-owner map across Claude Code / OpenCode / OMP, researched 2026-08-13 from vendor sources, and it does own the Claude Code invocation contract the interpretation names. That makes the *referent* real and the mapping coherent; it does not attest the *word*. | **medium** |

No operator round-trip taken, per the work order.

**Status: D9 is partially resolved.** ProofBunk is settled by rename history.
Rebo and Furble's Claude are recorded as **unresolved with standing
interpretations** — searched in both stores and the full tree, found nowhere,
with what was tried recorded here. Per the work order, an unknown that resists
resolution stays visible rather than being quietly replaced by a guess.

### Bonus finding from reading `invocation-contracts.md`

**F-D9-1 — `.omp/AGENTS.md` is NOT a broken reference.** The D5 sweep flagged
it as unresolved. Reading `invocation-contracts.md:14` shows why that was
wrong: the Memory row documents OMP's own convention — "`.omp/AGENTS.md` +
sticky `RULES.md`". It describes the *host's* file layout, not a path in this
repo. Same for `RULES.md`. Both D5 flags are retracted; two of the sweep's 51
"needs review" entries are now explained.

## Named-artifact checklist (the explicit D5 inventory)

Every artifact the work order's `<output_contract>` names, tested for
existence. This is the checklist form D5 owes — enumerated from the source
document rather than inferred from a parser.

### Front-half artifacts (Phases 0-4)

| Artifact | State |
|---|---|
| `evidence/v3-release/00-baseline/tool-inventory.md` | **EXISTS** (written this session) |
| `docs/discovery-register.md` | ABSENT — Phase 0 deliverable, pending |
| `docs/session-intent-ledger.md` | ABSENT — Phase 1 |
| `docs/commit-archaeology.md` | ABSENT — Phase 1 |
| `docs/skill-canon.md` | ABSENT — Phase 2 |
| `evidence/v3-release/00-baseline/codebase-analysis.md` | ABSENT — Phase 3 |
| `docs/proposals.md` | ABSENT — Phase 4 |
| `docs/v3-research/r1-candidates.md` | ABSENT — Phase 4 |
| `docs/v3-research/r2-patterns.md` | ABSENT — Phase 4 |

### New tooling (Phase 5)

All **ABSENT**, as expected before Phase 5: `tools/trace.py`,
`tools/verify-runtime.py`, `tools/gauge-report.py`, `tools/memory.py`,
`tools/route-eval.py`, `tools/harvest.py`, `tools/build-manifest.py`,
`tools/verify-manifest.py`, `tools/test-platform-parity.sh`,
`tools/test-regressions.sh`.

### New doctrine and release artifacts (Phase 5-6)

All **ABSENT**: `references/run-trace-schema.md`,
`references/memory-contract.md`, `docs/v3-gauges.md`,
`docs/platform-parity.md`, `proofpunk-v3-release-report.md`,
`plugins/proofpunk/manifest.json`, `.planning/run-trace.jsonl`.

### Pre-existing artifacts the work order extends

| Artifact | State |
|---|---|
| `e2e-evidence/FIXES.md` | **EXISTS** — gains one row per fix |
| `plugins/proofpunk/docs/improvements.md` | **EXISTS** — updated to the measured ledger |

### One consequential absence

| Artifact | State |
|---|---|
| `.planning/lane-b-audit.md` | **ABSENT** |

This is the file `LaneBPromptAudit` was assigned to write ("WRITE exactly one
new file: `/Users/nick/proofpunk/.planning/lane-b-audit.md`"). Combined with
that lane's 0-byte `.md` output against a 524 KB `.jsonl`, the conclusion is
that **the Lane B audit never produced its report**. Recorded so no later
phase mistakes the lane for completed work.

## Summary

- 26 of 28 named artifacts ABSENT — correct for this point in the run
  (Phases 0-4 in progress, Phase 5 not started).
- 2 EXIST as pre-existing files to be extended.
- 1 absence (`lane-b-audit.md`) is a finding, not a schedule item.
