# Implement Stage Trace — where a claim can pass without proof

Measured: 2026-09-04 (UTC) | Repo HEAD: `40abc0b` (working tree dirty)
Method: stage boundaries read directly from
`plugins/proofpunk/skills/implement/SKILL.md` (`^## Stage \d`); event keys read
from `plugins/proofpunk/hooks/hooks.json` by `json.load`, not by grep. Guard
behaviour taken from the per-script rows already measured in
`codebase-analysis.md:113-120`.

This closes the Phase 3 item "trace one full `implement --parallel --auto
--mine` run through Stages 0-7, noting every point where a claim could pass
without proof". It is the input set for the enforcement lanes (L4/L5/L6/L7).

## The 8 declared stages

| Stage | Name |
|---|---|
| 0 | Distill the TRUE success criteria (always first) |
| 1 | MINE (session-intent) |
| 2 | SCOUT (mandatory, subagents) |
| 3 | FORGE (prompt-forge) |
| 4 | DECOMPOSE into the task graph |
| 5 | EXECUTE the loop |
| 6 | The stuck protocol |
| 7 | REPORT from the ledger |

## The 7 registered hook event keys

`SessionStart`, `Stop`, `SubagentStop`, `PreToolUse`, `InstructionsLoaded`,
`PostToolUse`, `PostToolUseFailure` — read programmatically from `hooks.json`.

## Stage x enforcement — measured, not assumed

| Stage | Enforcement today | Can a claim pass unproven here? |
|---|---|---|
| 0 criteria | **none** | **Yes.** Criteria quality is prose-only. A run may declare a weak, unmeasurable criterion and no hook objects. |
| 1 MINE | **none** | **Yes.** `--mine` can be skipped silently; nothing records that mining ran. |
| 2 SCOUT | `Stop`/`SubagentStop` -> `stop-guard.sh` | **Partly.** Enforced only at Stop, never at the moment of the first write. The two-word substring escape was closed at `d1ecbb0`; the ordering gap (edit-before-scout within a run) is not closed by a Stop-time check. |
| 3 FORGE | **none** | **Yes.** |
| 4 DECOMPOSE | **none** | **Yes.** Proof obligations are a written convention, unenforced at write time. |
| 5 EXECUTE | `PreToolUse`/`Write\|Edit` -> `no-test-files.sh`, `evidence-guard.sh`, `capture-guard.sh`; `PreToolUse`/`Bash` -> `bash-write-snapshot.sh` | **Yes, for Bash.** The three denying guards match `Write|Edit` only. Bash-authored writes are detected after the fact by `bash-write-notice.sh` and **never denied** — the largest open gate at HEAD, documented open. |
| 6 stuck | **none** | **Yes.** Rungs are prose; nothing records which rung was reached. |
| 7 REPORT | `Stop`/`SubagentStop` -> `stop-guard.sh` | **No, for cited claims.** PROOF citations must resolve to real files under `e2e-evidence/` or `evidence/`. This is the strongest point in the pipeline. |

## Finding F-S-1 — enforcement is concentrated at the ends

Six of eight stages (0, 1, 3, 4, 6, and the Bash half of 5) have **no**
enforcement. The pipeline is guarded at the write boundary (`Write|Edit`) and
at the exit boundary (`Stop`), and is unguarded everywhere in between.

Consequence: a run can reach Stage 7 having skipped mining, forged nothing,
written no proof obligations, and authored files through Bash — and the only
thing that must hold is that whatever it *cites* at the end resolves to a real
file. That is a meaningful floor, but it is a floor on **citation integrity**,
not on **process conformance**.

This is exactly the gap L6 (`verify-runtime.py`) was scoped to close: the
existing verifier proves the *declared* graph, never the graph that actually
ran.

## Open / UNRESOLVED

- Whether an ordering violation (edit before scout) is detectable at all from
  the current hook surface is **not established here**. `PreToolUse` fires per
  tool call with no stage context; nothing in the payload names a stage. This
  is a design question for L2's trace substrate, not a measurement gap.
- No claim is made here about OMP or OpenCode enforcement. Those surfaces have
  their own contracts (`invocation-contracts.md`) and are owned by L14.
