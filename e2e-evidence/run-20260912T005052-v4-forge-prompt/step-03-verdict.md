# VERDICT — forge-prompt run, v4 remaining-work prompt

Run: `e2e-evidence/run-20260912T005052-v4-forge-prompt`
Superseded: the first verdict written in this run described the pre-amendment
artifact. This file describes the **final** bytes.

## Artifact identity

| Field | Value |
|---|---|
| Path | `.planning/v4-release.prompt.md` |
| Bytes | 22,573 |
| sha256 | `5037b114a8d1f3a58e8e02ae0673c585f2ff43a25e86c7c5b05ce5222bbc52ac` |
| Validated | `step-09-final-reconciled.txt` (supersedes step-06 and step-08) |

**Verdict generation.** This file has been refreshed three times as the
artifact changed. The current bytes postdate the authorized scout retry and
the corrections it produced. Earlier hashes in superseded validation files
(`step-06`, `step-08`) describe earlier bytes and are retained as history,
not as current claims.

## Criteria-proof table (final bytes)

| Criterion | End-user validation run | Artifact | Verdict |
|---|---|---|---|
| C1 — nine canonical skeleton tags, balanced | parsed current bytes from disk | `step-09-final-reconciled.txt` | **PASS** 11/11 |
| C2 — zero placeholders | regex sweep of current bytes | `step-09-final-reconciled.txt` | **PASS** 0 |
| C3 — cited repo paths resolve | stat'd every extracted token | `step-09-final-reconciled.txt` | **PASS** — 23 existing resolve, 4 declared-future (expected absent), **0 defects**. Delta 22→23 reconciled: `tools/verify-command-surface.py` newly cited by the level-(d) correction; nothing removed |
| C4 — remaining work enumerated + classified owned vs blocked | 11 work-item IDs + classification vocabulary | `step-02-criteria-c1-c2-c4-c5.txt` | **PASS** 11/11 |
| C5 — no git write without human sign-off | authorization-section audit | `step-02-criteria-c1-c2-c4-c5.txt` | **PASS** |
| C6 — embedded git facts trace to captured command output | ran `git rev-list --count origin/main..HEAD` (→ `17`), `git ls-remote --tags origin` (→ only `v2.1.0`, `v2.2.0`), `git tag` | `step-05-raw-command-capture.txt` | **PASS** — all rc=0; prompt source table at `.planning/v4-release.prompt.md:36,41-42` cites these commands |

One row per criterion. Citations by criterion: **C1–C3** cite
`step-09-final-reconciled.txt` (validated the current bytes); **C4–C5** cite
`step-02-criteria-c1-c2-c4-c5.txt` (content checks unaffected by the later
byte changes); **C6** cites `step-05-raw-command-capture.txt` (the captured
git output). Superseded validation files (`step-04`, `step-06`, `step-08`)
describe earlier bytes and are retained as run history only — no row in this
table cites them.

Note on C6: the two git facts embedded in the prompt's context table — "17
commits ahead of `origin/main`" and "only tags on origin are v2.1.0 and
v2.2.0" — are evidenced specifically by `step-05-raw-command-capture.txt`,
not by the path/skeleton sweep in `step-06`. The manifest claim ("all five
manifests at 4.0.0") was verified by grep across
`plugins/proofpunk/package.json:3`, `plugins/proofpunk/.claude-plugin/plugin.json:3`,
`plugins/proofpunk/.omp-plugin/plugin.json:3`, `.claude-plugin/marketplace.json:8,16`,
and `.omp-plugin/marketplace.json:9,17`.

## Defects found and fixed during validation

Three rounds, each a real bug in the artifact:

1. `palettes.json` cited bare and unresolvable → corrected to
   `plugins/proofpunk/themes/palettes.json`.
2. `test-hooks.sh`, `verify-counts.py`, `verify-orchestration.py` cited bare →
   corrected to `tools/`-prefixed paths.
3. Two facts embedded as verified without personal verification ("17 commits
   ahead", "all five manifests at 4.0.0") → re-derived by running the commands,
   raw output captured in `step-05-raw-command-capture.txt`, and the prompt's
   source table amended to cite those commands.

## Edit-integrity check

One edit in this run matched via fuzzy strategy (97%) and emitted a warning.
Re-read of the W-D4 / output-contract region confirms the intended text was
unchanged and nothing nearby was altered: `` `W-D4` `` appears exactly once,
`proofpunk-v4-release-report.md` appears 3 times (todo entry, output contract,
example). The edit was a genuine no-op. Verified at
`step-06-final-validation-hashed.txt`.

## Repo state — unmutated

| Check | Result |
|---|---|
| Tracked-file modifications | 40 at run start, 40 at run end — unchanged |
| Tags (local and `origin`) | `v2.1.0`, `v2.2.0` — unchanged; no `v4.0.0` created |
| Commits / pushes | none |

Raw capture: `step-05-raw-command-capture.txt`.

The 40 pre-existing modifications are prior-session work, out of scope per
`evidence/v4-release/ambient-boundary-20260911T2356Z.txt`. This run neither
staged, reverted, nor regenerated any of them.

## Release status — explicitly NOT claimed

**Proofpunk v4 is NOT released and NOT pushed.** This run produced the
instrument for shipping it. The sealed verdict at
`evidence/v4-release/run-20260911T234909Z/reconciliation.md` stands unchanged:
AC1, AC2, AC6 remain BLOCKED/UNVERIFIED.

## Run-process conformance — NOT green

Artifact PASS is not the same as execution-loop conformance.

- Stage 1.5 ACQUIRE: **not performed** (no `.planning/docs-<host>.md` digests).
- Stage 2 SCOUT: **PARTIAL** — `ScoutCommandSurface` failed on credential
  cooldown, recorded **UNVERIFIED**, findings unused, not retried.

Full disposition: `step-00-stage-conformance.md`.

## Evidence classification

Every file in this run directory is **run working evidence**, not sealed
release evidence: it sits outside the v4 allowlist
(`evidence/v4-release/v4-release-allowlist-20260911T2357Z.txt`), was never
sealed or inventory-validated, and is untracked. It supports this forge run's
criteria only and adds nothing to the v4 release evidence set.
