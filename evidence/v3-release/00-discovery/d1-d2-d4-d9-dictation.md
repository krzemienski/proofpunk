# D1, D2, D4, D9 — Prompt lane, second lane, and dictation artifacts

Measured 2026-09-02 against `/Users/nick/proofpunk` @ `a41591a`.

## D1 — "the two e prompt" — RESOLVED (standing fallback confirmed)

### Method

Searched every spelling across the whole tree, all branches, all tags, and
every commit body:

| Search | Scope | Hits |
|---|---|---|
| `e2e prompt` | tracked `*.md/*.sh/*.py/*.json`, product tree | **0** |
| `2e prompt` | same | **0** |
| `two prompt` | same | 1 (see below) |
| `two e` / `the 2e` / `E2 prompt` / `2 e prompt` / `two-e` | **all commit bodies, `git log --all`** | **0** |
| same family | `plugins`, `tools`, `docs`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `examples` | 1 (same one) |

Branches: `main` only (plus `origin/HEAD`, `origin/main`).
Tags: `v2.1.0`, `v2.2.0`. No branch or tag encodes a `2e`/`E2` artifact.

The single `two prompt` hit is **not** the referent — it is an unrelated
Python docstring inside a reference file:

```
plugins/proofpunk/skills/prompt-forge/references/prompt-optimization.md:332
    """Compare token usage between two prompt versions."""
```

### Contrast: the prompt lane is real and densely populated

| Term | Tracked files |
|---|---|
| `rate-prompt` | 12 |
| `ship-below-threshold` | 9 |
| `forge-prompt` | 9 |

Prompt-facing artifacts (tracked, 16):
`commands/forge-prompt.md`, `commands/rate-prompt.md`,
`opencode/commands/proofpunk-forge-prompt.md`,
`opencode/commands/proofpunk-rate-prompt.md`,
`skills/prompt-forge/SKILL.md` + 7 files under
`skills/prompt-forge/references/`, `examples/mood-ring/.prompts/
build-mood-ring/{PROMPT.md,RATING.md}`, and two evidence records
(`e2e-evidence/run-command-surface/rate-prompt-records.json`,
`e2e-evidence/run-sdk-probes/skill_prompt_forge.json`).

Untracked: `.planning/proofpunk-agent.prompt.md` (the `*.prompt.md` sweep
returned exactly one file — this work order itself).

### Verdict

**"The two e prompt" = the two prompt-facing commands,
`/proofpunk:forge-prompt` and `/proofpunk:rate-prompt`, over the
`prompt-forge` skill.** No artifact named `2e`, `e2e-prompt`, or `E2` exists
anywhere in the tree, in any branch, in any tag, or in any commit body. The
standing fallback in the work order is confirmed by exhaustive absence plus a
positive match on a two-command lane.

Confidence: **high** on the negative (exhaustive, all refs searched); **high**
on the positive (two commands, one skill, mirrored on both platforms — "two"
is satisfied literally). Logged as the work order directed: a resolution
reached via the standing fallback, not via a located artifact named "2e".

## D2 — "the other lane that needs to be fully verified" — PARTIAL

Four candidates were named in the work order. Status from evidence gathered
so far:

| Candidate | Evidence today | Verdict |
|---|---|---|
| The prompt lane | 16 artifacts, both platforms, real commands | Not "unverified" as a lane — it exists and is proven at least partly (`e2e-evidence/run-command-surface/`, `run-sdk-probes/`). It is L18's subject regardless. |
| `.planning/` Lane B | `.planning/execution-ledger.json:11-19` records `C2_lane_b_unblock` as **BLOCKED**, requiring one of three exact operator tokens (`APPROVE BARRIER DELTA`, `REJECT BARRIER DELTA`, `STOP`) | **Genuinely blocked on a human decision.** Cannot be resolved by any agent action. |
| OpenCode surface UNPROVEN at `8718561` | not yet re-measured | open — Phase 3 re-measures |
| Bash-write bypass | documented open at HEAD | open — L5's subject |

**Ruling deferred.** D2 asks which lane the operator meant; the ledger shows
Lane B is the only one blocked on an *operator token* rather than on work.
That is the strongest single signal, but the OpenCode-UNPROVEN candidate has
not been re-measured yet, so naming a winner now would exceed the evidence.
Resolved in Phase 1 mining, where the session record carries the phrasing.

## D4 — Round-1/round-2 dictation artifacts — RECORDED

Recorded verbatim so no downstream agent re-litigates them:

| Heard | Means | Basis |
|---|---|---|
| "the food club" | "the full scope / the whole plugin" | given in the work order |
| "now they work together" | "**how** they work together" | given in the work order |

Both are stated as resolved in the source brief; this file exists so the
resolution travels with the evidence tree rather than only the prompt.

## D9 — v3-brief dictation artifacts

| Heard | Standing interpretation | Status |
|---|---|---|
| "ProofBunk" | Proofpunk | Confirmed by tree: every manifest, package, and marketplace entry reads `proofpunk`; no `proofbunk` string exists. |
| "Rebo" | the router head, `skills/proofpunk/SKILL.md` | **Standing interpretation retained.** No repo, directory, or file named `rebo` exists in the tree. The head skill was read this session and does route all 17 skills, matching the described role. |
| "Furble's Claude" | the Claude Code invocation contract, `plugins/proofpunk/docs/invocation-contracts.md` | **Standing interpretation retained**; the file exists in the tree (`docs/doc-invocation-contracts.html` is its rendered form). Contents not yet read — Phase 3 reads it end to end. |

No operator round-trip taken, per the work order's instruction.

## Evidence

Produced by `grep` over the product tree, `git branch -a`, `git tag`,
`git log --all --format='%H|%s|%b'` piped through a stdlib regex filter, and
`git ls-files`. Raw command transcripts are the session record.
