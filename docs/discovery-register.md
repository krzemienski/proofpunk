# Discovery Register — Phase 0 (DRAFT — Phase 0 NOT complete)

One row per unknown: resolution, evidence path, confidence. Unresolved entries
stay visible. Measured 2026-09-02 against `/Users/nick/proofpunk` @ `a41591a`.

**Status: DRAFT.** Phase 0 is not closed. Open at the time of writing:
D1/D2 are medium-confidence prior-agent interpretations with no operator
corroboration; D5's explicit named-artifact inventory is incomplete; D9b/D9c
are unresolved; several Setup items (lane-skill activation) are still pending.
Nothing downstream may cite this file as a completed phase gate.

Confidence rule used throughout: only text an **operator actually typed or
dictated** is primary evidence. Assistant-authored text delivered to a
subagent in a `role=user` envelope is an **agent interpretation**.

| # | Unknown | Resolution | Evidence | Confidence |
|---|---|---|---|---|
| D1 | "the two e prompt" | `.planning/proofpunk-agent.prompt.md` (61.5 KB, Part I spec + Part II build prompt) + `.planning/hardening/`. **Prior-agent interpretation, not operator-confirmed.** The operator said only "look for the two e prompt"; the naming comes from `ScoutPlanningPrompt.jsonl:7`, authored by the parent assistant. No artifact named `2e`/`E2` exists in tree, branches, tags, or commit bodies. | `evidence/v3-release/00-discovery/d1-d2-d8-transcript-evidence.md`; `raw/round1-dictation.txt` | **medium — OPEN** |
| D2 | "the other lane that needs to be fully verified" | `.planning/` Lane B — bound to D1 by the dictation ("that will lead to another lane"), so it inherits D1's confidence. Prior agent scoped it verify-only. Separately: Lane B **execution** is BLOCKED on an exact operator token (`APPROVE BARRIER DELTA` / `REJECT BARRIER DELTA` / `STOP`). | same; `.planning/execution-ledger.json:11-19` | **medium — OPEN**; execution **BLOCKED** |
| D3 | Gate inventory + blind spots | 6 gates measured. `test-hooks.sh` invokes 9/9 scripts; `test-installer.sh` is the **only** driver of the shell installer (14 refs); `dry-run-install.sh` is **MODEL ONLY** — reimplements the `/proofpunk:install` playbook, invokes no subject. 7 surfaces have **no gate at all**. | `evidence/v3-release/00-discovery/d3-gate-inventory.md` | **high** |
| D4 | Round-1 dictation artifacts | "the food club" appears verbatim → "the full scope / the whole plugin". "now they work together" was a mis-transcription; the operator said "**how** they work together". | `raw/round1-dictation.txt` | **high** |
| D5 | Artifacts referenced but not seen | `fresh_evidence.py` located at `skills/end-user-testing/scripts/` (skill-owned, not `tools/`), installed copy present, 15 consumers. Heuristic sweep: 296 refs, 60 unresolved, mostly historical names in `consolidation-decisions.md`. | `d5-referenced-artifacts.md`; `d5-sweep-results.md` | **PARTIAL — OPEN** (explicit inventory lands in the Phase 3 read) |
| D6 | Ground-truth counts | 18 skills · 13 references · 6+6 commands · 9 hook files · **7 event keys / 11 registrations / 9 distinct scripts** · 3/4/3 agents · 10 tools. | `d6-d7-measurement.md` | **high** |
| D7 | Installed-vs-repo state | Installed 2.2.0 matches repo HEAD exactly (same commit SHA `a41591a`, 18 skills). One registered version — the `f95ba9d` duplicate-injection failure is **not** reproducing. Stale unregistered 1.10.1 tree persists on disk with 19 skills incl. dead `cook`/`functional-validation`. | `d6-d7-measurement.md` | **high** |
| D8 | "one massive skill" | **Strengthen and prove the existing router head — not a single-file merge.** Resolved from the operator's own words: "one massive skill that basically **the head will link with everything else**". Zero merge requests across 34,674 OMP + 168 Claude operator turns. | `d1-d2-d8-transcript-evidence.md`; `raw/round1-dictation.txt` | **high** |
| D9a | "ProofBunk" | **Proofpunk.** Rename history: `1fa27b3` (2026-08-11) "v1.8.0: rename truth-forge -> proofpunk"; origin `20bd199` shipped as `truth-forge`. Two names ever, neither `proofbunk`. | `d9-and-artifact-checklist.md` | **high** |
| D9b | "Rebo" | **UNRESOLVED.** Standing interpretation: the router head. Term unattested in tree, in 97 Claude session files, and in 7,320 OMP session files — every apparent hit is today's work order echoing back. | `d9-and-artifact-checklist.md`; `raw/d9-session-search.txt` | **low-medium — OPEN** |
| D9c | "Furble's Claude" | Plausible: `docs/invocation-contracts.md`, now read — it is the trigger-owner map across all three hosts. Referent real; **term still unattested**. | same | **medium — OPEN** |

## Findings raised during discovery

| ID | Finding | Consequence |
|---|---|---|
| F-D6-4 | **The work order's "9 script registrations" is wrong** — true count is 11 registrations / 9 distinct scripts (`stop-guard.sh` and `bash-write-notice.sh` each registered twice). `architecture.md:497` already had it right; the repo is correct, the work order is not. | The release-validation criterion must be corrected or its gate fails spuriously. |
| F-D3-1 | `dry-run-install.sh` models the install playbook rather than driving it; `/proofpunk:install` has **no gate at the real slash surface**. | L16's harness-integrity gate must key on *declared subject → invocation*, not filename. |
| F-D3-2 | Installer coverage rests on a single harness group (`test-installer.sh:257`). | Single point of observation; L1 and L16 must treat it as load-bearing. |
| F-D5-1 | `__pycache__` ships into the installed tree (`cpython-311` bytecode from the build host). | Installer hygiene defect, ungated. |
| F-D5-2 | The installer has no explicit `scripts/` copy path; `fresh_evidence.py` ships only because `skills/**` is copied wholesale. | Nothing asserts it — L1 must add the assertion. |
| F-D7-1 | Stale unregistered 1.10.1 tree with dead skill names persists on disk. | Any tool globbing the marketplace cache sees 19 skills and two removed names. |
| F-D7-2 | Zero proofpunk hook registrations in `~/.claude/settings.json`. | The installer's `settings.json` merge is **unexercised on this host** until a clean-HOME `--hooks` install is driven. |
| F-D9-1 | `.omp/AGENTS.md` and `RULES.md` are **not** broken references — `invocation-contracts.md:14` documents OMP's own memory layout. | Two D5 sweep flags retracted. |
| F-T1 | `shellcheck` is **absent** on this host. | L5's lint lane cannot run as written; must install, vendor, or record an explicit exception. |
| F-T2 | `jq` resolves to `jaq 2.3.0`, not GNU jq. | Any harness assuming GNU semantics is untested here. |

## Method corrections made during Phase 0

Each was a near-miss that would have produced a false finding:

1. **Role gating alone is insufficient** — skill-injection payloads arrive in `role=user` envelopes. Three "operator" D8 hits were the `proofpunk` SKILL.md body.
2. **A masked failure produced a 0-byte artifact** — `$?` was reset by a following command. Deleted, never cited; re-run with `set -o pipefail` and rc captured separately.
3. **768-char display truncation hid the decisive sentence** — the "two e prompt" phrase sits past the cutoff; the text had to be written to a file and printed from an offset.
4. **A wrong resolver produced a false 183/296-unresolved reading** — citations must resolve relative to the citing file. All 13 doctrine references are fine.
5. **`grep` found no matches ≠ absence** — `test-hooks.sh` resolves scripts through `$HOOKS`, so a literal-string count reported 0 for a harness that invokes all 9.
6. **A `role=user` envelope is not an operator turn** — the strongest-looking D1/D2 evidence was an assistant-authored task assignment; downgraded to medium.

## What must close before Phase 0 is complete

- **D1/D2** — search operator turns for any corroboration of the
  `.planning/proofpunk-agent.prompt.md` mapping (carried into Phase 1 mining).
- **D5** — explicit named-artifact inventory verified in context, not by
  parser heuristic (Phase 3 end-to-end read).
- **D9b/D9c** — remain unresolved with what was tried recorded; no further
  source is known to exist.
- **Setup** — lane-skill activation and the MCP/skill inventory row.
