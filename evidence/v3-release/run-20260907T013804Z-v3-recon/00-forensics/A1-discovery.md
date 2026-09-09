# A1 — Discovery Unknowns D1, D2, D5 (STATUS: IN PROGRESS)

Repo: `/Users/nick/proofpunk` @ HEAD `93c479de800fff7e3ceb0be5ccf96f4d494fdaee`, branch `main`.
Measured 2026-09-06/07. Read-only lane.

## Summary

- D1 ("the two e prompt") has TWO independent, never-reconciled readings on disk. Neither is operator-confirmed. No artifact named `2e`, `E2`, `two-e`, or `e2e prompt` exists anywhere in tree, branches, tags, or commit bodies (904-line dump of `git log --all --format=%B` searched, zero hits).
- D2's four candidates are all attested in the record; the winner depends entirely on which D1 reading is adopted, and the record itself says so explicitly (`d1-d2-d4-d9-dictation.md:78-81`: "naming a winner now would exceed the evidence").
- `tools/fresh_evidence.py` is confirmed ABSENT; the real, tracked path is `plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py` (confirmed both by my own `test -f` and independently by the orchestrator's F-002 note).
- `plugins/proofpunk/docs/` contains exactly 7 files — the brief's claimed count is correct, not stale as I initially assumed from other found discrepancies.
- 11 of the 15 D5-listed candidate paths are ABSENT; 4 exist.
- `~/.claude/proofpunk-loads.jsonl` exists (1,899,249 bytes, mtime today) — this is a live host artifact outside the repo tree, worth flagging since nothing in-repo references it by that literal name.

## D1 — "the two e prompt"

**Resolution: contested, not resolved to certainty. Two competing readings exist on disk, both prior-agent products, never corroborated by a literal operator quotation.**

### Exhaustive search performed (per task instructions)

1. `git grep -n -i "e2e prompt"` across tracked, non-ignored content: **0 hits**.
2. `git grep -n -i "two prompt"`: **0 hits**.
3. `git grep -n "ship-below-threshold"`: hits only in `plugins/proofpunk/commands/rate-prompt.md` and its opencode mirror, and in `docs/`/`evidence/` prose about the `--ship-below-threshold` CLI flag of `/proofpunk:rate-prompt` — unrelated to "the two e prompt" as a name.
4. `git log --all --format=%B` dumped to file (904 lines, all 71 commits on all branches — `main` is the only local branch, plus `remotes/origin/main`; tags `v2.1.0`, `v2.2.0`) and grepped for `two.e.prompt|e2e prompt|2e prompt|two-e`: **0 hits**.
5. Filesystem-level search (via `grep_ide` with `gitignore: false`, so untracked and gitignored content included) for `two prompt|e2e prompt`: **0 hits** anywhere on disk.
6. Confirmed via prior-session evidence already on disk (`evidence/v3-release/00-discovery/d1-d2-d8-transcript-evidence.md:125-126`, re-verified per `d1-tui-prompt-resolution.md:15-18` "section E: 0 matches across all commit bodies") that this same exhaustive search was independently run twice before with the same null result.

### Reading A — `.planning/proofpunk-agent.prompt.md` (medium confidence, first-derived)

Quoted evidence, `evidence/v3-release/00-discovery/d1-d2-d8-transcript-evidence.md:100-103`:

> "(61.5KB) and everything under `/Users/nick/proofpunk/.planning/hardening/`. … This artifact is the user's 'two e prompt' reference and defines a SECOND work lane." — `ScoutPlanningPrompt.jsonl:7`, mirrored at `__advisor.jsonl:3`

**Provenance caveat, quoted from the same doc (line 105-106):** "That text was authored by the parent assistant when dispatching the subagent" — i.e. it is agent-interpretation, not an operator quotation, despite arriving in a `role=user` envelope. `docs/discovery-register.md:32` rates this **medium — OPEN**, explicitly: "Prior-agent interpretation, not operator-confirmed."

### Reading B — "the TUI prompt" mis-transcribed (same referent artifact, higher-confidence *mechanism*)

`evidence/v3-release/00-discovery/d1-tui-prompt-resolution.md` (dated 2026-09-04, supersedes-in-place the confidence rating, not the referent) argues the phrase is a speech-to-text error for "the TUI prompt," citing the established error class in the same dictation ("the food club" → "the full scope", `docs/discovery-register.md:35` rated **high**). Quote (`d1-tui-prompt-resolution.md:32-34`):

> Read aloud, **"the TUI prompt" transcribes to "the two e prompt"** — "TUI" is spoken as three letters, T-U-I, and a speech-to-text pass renders the leading "T-U" as "two" and the trailing "I" as "e".

This reading raises confidence to **high** but keeps the *same referent* (`.planning/proofpunk-agent.prompt.md`) — it does not compete with Reading A on target file, only on why that file is the target. Explicitly flagged unresolved at the end of that same doc (line 84-89): "**No operator turn confirms this decoding**, because none exists to find… It would be falsified by any operator turn using 'two e prompt' to mean something else, or by a second TUI-prompt artifact appearing in `.planning/`."

### A third, independently-derived, later document contradicts both

`docs/session-intent-ledger.md` (dated 2026-09-04T05:10:00Z, i.e. same day, cross-checked against `raw/operator-turns.json` and `raw/transcript-user-turns.json` — see visible screenshot capture, row "## 4"): labels the D1/D2 phrase resolution itself as **AGENT-INTERPRETATION**, and states "No commit resolves D1/D2 to certainty" and reports the cross-check result: **9/20 D1 hits mention `proofpunk`, and every one of those 9 is the v3 work order document itself, not an operator utterance; 0/20 D2 hits mention `proofpunk` at all.** Its own conclusion, quoted: "no genuine operator turn has ever named the D1/D2 artifact."

`docs/discovery-register.md:7-15` (the canonical Phase-0-closure register, "Status: FINAL") records the net verdict as: **"D1 / D2 — medium, CLOSED as interpretation — Phase 1 mining independently re-derived the same conclusion instead of inheriting it: zero genuine operator turns corroborate the artifact mapping. The interpretation stands, explicitly labelled as such, and is not reported as evidence-resolved."**

### My finding

D1 is **not resolved to certainty by any document in this repo**, and the repo's own most-authoritative closure document (`docs/discovery-register.md`, marked FINAL) says exactly that. What IS settled, by convergent independent derivation across three separate sessions/documents:
- The referent, if any, is `.planning/proofpunk-agent.prompt.md`.
- No artifact literally named anything resembling "2e"/"E2"/"e2e prompt" exists anywhere.
- No operator turn — as opposed to assistant-authored dispatch text — has ever been found using the phrase "two e prompt."
- The task brief's fallback (D1 = the two commands `/proofpunk:forge-prompt` + `/proofpunk:rate-prompt`) is a DIFFERENT, older, competing hypothesis (`d1-d2-d4-d9-dictation.md`, explicitly superseded — see D2 section below) that the current-FINAL discovery register does not carry forward. I am logging this per the task's own fallback-with-impact instruction: **if the fallback is adopted instead of the `.planning/proofpunk-agent.prompt.md` reading, every downstream claim in the repo's Phase-0/Phase-1 discovery chain about D1/D2/Lane-B being about a TUI build spec is wrong, and the record's own "medium, CLOSED as interpretation" verdict — the strongest evidence in the tree — is being overridden by the task brief's a-priori assumption rather than by new evidence.** I did not find any evidence produced during this run that would justify that override.

## D2 — "the other lane that needs to be fully verified"

Task instructions ask me to test 4 named candidates against the record with quoted evidence and name a winner.

| Candidate | Attested? | Quoted evidence | My assessment |
|---|---|---|---|
| (a) The prompt lane itself | Yes | `d1-d2-d4-d9-dictation.md:73`: "The prompt lane — 16 artifacts, both platforms, real commands — Not 'unverified' as a lane; it exists and is proven at least partly (`e2e-evidence/run-command-surface/`, `run-sdk-probes/`)." | **Ruled out by the record itself** — it says this lane is already at least partly proven, so it does not fit "needs to be fully verified" as an open item. |
| (b) BLOCKED `.planning/` Lane B awaiting operator token | Yes | `.planning/execution-ledger.json` (read directly): `"C2_lane_b_unblock": {"verdict": "BLOCKED", "detail": "consensus-verdict.md:120 forbids agent edits or consensus before an exact operator token... Delegated judgment was attempted twice in prior sessions and RETRACTED as fabricated authority.", "required_token": ["APPROVE BARRIER DELTA","REJECT BARRIER DELTA","STOP"]}`. Also `d1-d2-d4-d9-dictation.md:74`: "`.planning/` Lane B — … **Genuinely blocked on a human decision.** Cannot be resolved by any agent action." | **Strongest single candidate per the record's own words** (line 78-79: "Lane B is the only one blocked on an *operator token* rather than on work. That is the strongest single signal"). |
| (c) OpenCode surface UNPROVEN at `8718561` | Yes | Commit exists: `git log --oneline` shows `8718561 test: before/after proof for harness and installer; opencode blocked`. `e2e-evidence/FIXES.md:17`: "Same flag drift on the **OpenCode** surface \| **UNPROVEN** \| install-level only; sandbox auth fails before dispatch — `run-command-surface/OPENCODE-BLOCKED.md`". `d1-d2-d4-d9-dictation.md:75`: "OpenCode surface UNPROVEN at `8718561` \| not yet re-measured \| open — Phase 3 re-measures". | Attested but explicitly deferred by the record itself pending re-measurement, and the same doc (line 80-81) says naming a winner without that re-measurement "would exceed the evidence." |
| (d) The Bash-write bypass | Yes | `.planning/plugin-improvements.md:20`: "Bash write bypass. The three PreToolUse guards register only under matcher `Write\|Edit`; `cat > f <<EOF`, `tee`, `sed -i`, `python -c open().write()` bypass all three… a naive matcher addition fails open." `plugins/proofpunk/hooks/bash-write-notice.sh:7-10`: "WHAT THIS IS NOT: it does not close the Bash write bypass… This is detection-only". `docs/v3-reasoning-gate.md:46-49`: "**Consequence that constrains L5.** The Bash-write bypass cannot be closed at `PostToolUse`… And it cannot be closed by parsing shell at `PreToolUse`, because that path already falsely blocked `cp -p`, `mv -f`, `touch -c`, `sed -i -e` and was reverted." | Real, extensively documented, explicitly "open — L5's subject" per `d1-d2-d4-d9-dictation.md:76`. This is an open **defect**, not an unverified **lane** — different shape from what "the other lane that needs to be fully verified" describes. |

**Winner, per the record's own explicit ruling (not my own inference):** `d1-d2-d4-d9-dictation.md:78-82` states, verbatim: "**Ruling deferred.** D2 asks which lane the operator meant; the ledger shows Lane B is the only one blocked on an *operator token* rather than on work. That is the strongest single signal, but the OpenCode-UNPROVEN candidate has not been re-measured yet, so naming a winner now would exceed the evidence. Resolved in Phase 1 mining, where the session record carries the phrasing."

Following that pointer: `docs/discovery-register.md:33` gives the actual Phase-1 answer: **D2 = `.planning/` Lane B** — "bound to D1 by the dictation ('that will lead to another lane'), so it inherits D1's confidence. Prior agent scoped it verify-only. Separately: Lane B **execution** is BLOCKED on an exact operator token." Confidence: **medium — OPEN; execution BLOCKED.**

**My finding: (b) is the winner, per the repo's own Phase-1 ruling, at medium confidence, contingent entirely on D1's unresolved status above.** (c) OpenCode-UNPROVEN and (d) Bash-write-bypass remain real, separately-tracked open items in the repo regardless of D2's outcome — they are not competing readings of the same phrase, they are independently real defects that happen to share the word "unproven"/"open" with the D2 language.

## D5 — Referenced-but-unseen artifact inventory

Existence checks run via `test -f`/`test -d` directly against the live tree (not the brief's claims) plus `glob` confirmation.

| Path (as named in brief) | Exists? | Evidence |
|---|---|---|
| `tools/fresh_evidence.py` | **ABSENT** | `test -f tools/fresh_evidence.py` → false. Real tracked path: `plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py` — **EXISTS**, confirmed by `test -f` (true) and independently corroborated by orchestrator IRC note (F-002) and by `evidence/v3-release/00-discovery/d5-referenced-artifacts.md:5-27`, which documents the same discrepancy in detail: "not missing — it was looked for in the wrong place… It is **not** in `tools/`… it is skill-owned, not repo-owned." That doc also flags a live defect (F-D5-1): `__pycache__/fresh_evidence.cpython-311.pyc` ships into the installed tree, a stray compiled artifact. |
| `docs/proposals.md` | **ABSENT** | `test -f docs/proposals.md` → false; also absent from `glob` result over the `docs/` root (only `discovery-register.md` and `session-intent-ledger.md` present there). |
| `docs/platform-parity.md` | **ABSENT** | `test -f` → false; not in glob of `docs/`. |
| `docs/v3-research/r1-candidates.md` | **ABSENT** | `docs/v3-research/` directory itself does not exist (`test -d docs/v3-research` → false), so the file cannot exist. |
| `docs/v3-research/r2-patterns.md` | **ABSENT** | Same as above — parent directory absent. |
| `plugins/proofpunk/manifest.json` | **ABSENT** | `test -f` → false. `glob **/manifest.json` finds only two unrelated files: `evidence/v2.2.0-release/manifest.json` and `evidence/v2.1.0-post-tag/manifest.json` — release snapshots, not the plugin's own manifest. There is no `plugins/proofpunk/manifest.json` on disk at HEAD. |
| `references/memory-contract.md` | **ABSENT** | `test -f references/memory-contract.md` → false; root-level `references/` directory does not exist (`test -d references` → false). Confusable-with: `plugins/proofpunk/references/evidence-contract.md` **EXISTS** but is a different file with a different name — not a match. |
| `.planning/execution-ledger.json` | **EXISTS** | `test -f` → true; directly read and quoted above in D2. Confirmed by `ls -la .planning/` listing (8 files, 1 dir under `.planning/`). |
| `.planning/run-trace.jsonl` | **ABSENT** | `test -f` → false; not in the 8-file `.planning/` listing (`hardening/`, `BUILD-PROMPT.md`, `execution-ledger.json`, `plugin-improvement-criteria.md`, `plugin-improvements.md`, `proofpunk-agent-criteria.md`, `proofpunk-agent.prompt.md`, `v3-criteria.md`, `v3-run-criteria.md`). Note: `plugins/proofpunk/references/run-trace-schema.md` exists as a *schema* doc, a different artifact by a similar name — not a match, and not the same as an actual trace log. |
| `~/.claude/proofpunk-loads.jsonl` | **EXISTS** | `ls -la ~/.claude/proofpunk-loads.jsonl` → `-rw-r--r-- 1 nick staff 1899249 Sep 6 21:43 /Users/nick/.claude/proofpunk-loads.jsonl`. This is a live host artifact outside the repo tree (session/load telemetry), not tracked in git. |
| `plugins/proofpunk/docs/invocation-contracts.md` | **EXISTS** | `test -f` → true; also in the `docs/` glob listing. |
| `plugins/proofpunk/docs/consolidation-decisions.md` | **EXISTS** | `test -f` → true; also in the `docs/` glob listing. |
| `e2e-evidence/FIXES.md` | **EXISTS** | `test -f` → true; content quoted above in the D2 table (row (c), OpenCode UNPROVEN). |
| `plugins/proofpunk/docs/improvements.md` | **EXISTS** | `test -f` → true; also in the `docs/` glob listing. |
| `examples/mood-ring/` | **EXISTS (directory)** | `test -d` → true; glob confirms a full nested tree: `pyproject.toml`, `LICENSE.txt`, `README.rst`, `.gitignore`, `flaskr/` app package, `tests/`, `e2e-evidence/run-20260808T202017-mood-ring/` (a captured demo run with 19 step artifacts), and `.prompts/build-mood-ring/{PROMPT.md,RATING.md}`. |

### `plugins/proofpunk/docs/` full listing and true count

Glob of `plugins/proofpunk/docs/*` returns exactly **7 files**:

1. `architecture.md`
2. `usage-guide.md`
3. `improvements.md`
4. `hooks-and-init-design.md`
5. `validation-results.md`
6. `invocation-contracts.md`
7. `consolidation-decisions.md`

**The brief's claimed count of 7 is CORRECT** — no discrepancy here, contrary to what the orchestrator's brief context (which frames the brief overall as stale relative to a 10-commit-old snapshot) might suggest. This is a case where the stale-snapshot brief happens to still be accurate on this specific figure; I did not assume staleness and verified directly.

## Open questions

- **D1 remains genuinely unresolved to operator-confirmed certainty.** I found no new evidence in this pass that would resolve it further than the repo's own FINAL discovery register already does ("CLOSED as interpretation," explicitly not "evidence-resolved"). Anyone treating D1 as settled beyond that point is going further than the record supports. What I tried beyond re-reading prior work: independent re-run of the full-tree grep and the all-branches/all-tags commit-body search, both confirming the prior null results rather than superseding them.
- **D2's winner (Lane B) is contingent on D1.** If D1 is later resolved differently (e.g., the task brief's own forge-prompt/rate-prompt fallback is adopted with new evidence), D2 would need to be re-derived, since the current chain from D2 to Lane B runs entirely through the D1-TUI-prompt reading's "leads to another lane" clause.
- I did not find any document that resolves the tension between (1) the FINAL discovery register's "medium, CLOSED as interpretation" ruling on D1/D2, and (2) the task brief's framing that assumes/prefers the forge-prompt/rate-prompt standing-fallback as if it were current. I flagged this explicitly rather than silently picking one. I did not attempt to adjudicate which framing this recon run "should" trust — that is outside a read-only forensics lane's remit.

## STATUS: COMPLETE
