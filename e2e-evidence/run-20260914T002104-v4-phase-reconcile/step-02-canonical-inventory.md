# step-02 — Canonical inventory measured at HEAD `63727e1`

Every count below was **derived from the tree**, not restated from any prior
document. This supersedes the work order's historical counts and the Phase 0
register's D6 row, both of which were measured at `a41591a` / `9963648`.

## The work order's premise is 114 commits stale

| | Work order says | Measured at HEAD | Δ |
|---|---|---|---|
| HEAD | `a41591a` (2026-09-01) | **`63727e1`** (2026-09-13) | +114 commits |
| Version | `2.2.0` | **`4.0.0`** | +2 major |

`git rev-list --count a41591a..HEAD` = **114**.

## Canonical counts (this is the source of truth for all later phases)

| Dimension | Work order (v2.2.0) | Phase 0 register D6 | **HEAD `63727e1`** |
|---|---|---|---|
| Skills | 18 | 18 | **19** |
| Shared references | 13 | 15 | **18** |
| Commands (Claude) | 6 | 6 | **7** |
| Commands (OpenCode) | 6 | 6 | **7** |
| Hook files | 10 | 10 | **11** |
| Hook event keys | 7 | 7 | **7** |
| Hook registrations | 9 | 12 | **12** |
| Distinct hook scripts | 9 | 10 | **10** |
| Agents | — | 3/4/3 | **3** |
| Tools | 10 | 22 | **27** |

Derivation: `plugins/proofpunk/skills/*/` (dirs), `references/*.md`,
`commands/*.md`, `opencode/commands/*.md`, `hooks/*`, `agents/*`, `tools/*`;
hook events/registrations/scripts walked programmatically from `hooks.json`.

### The 19 skills

`brainstorm`, `codebase-truth-audit`, **`completion-summary`**,
`end-user-testing`, `full-functional-audit`, `implement`,
`mobile-validation-runner`, `plan-hardening`, `production-readiness`,
`prompt-forge`, `proofpunk`, `red-team-eval`, `root-cause-debugging`,
`session-intent`, `stack-testing`, `tui-testing`, `ui-experience-audit`,
`validation-plan`, `visual-inspection`

`completion-summary` is the 19th — added after the work order was written. It
is the skill the ledger's I3 finding corrected ("claimed it *proves agents
terminated*; it confirms recorded completion only").

### Hook surface

- **7 event keys**: `InstructionsLoaded`, `PostToolUse`, `PostToolUseFailure`,
  `PreToolUse`, `SessionStart`, `Stop`, `SubagentStop`
- **12 registrations**, **10 distinct scripts**: `bash-write-notice.sh`,
  `bash-write-snapshot.sh`, `capture-guard.sh`, `evidence-guard.sh`,
  `instructions-loaded.sh`, `no-test-files.sh`, **`platform-steer.sh`**,
  `post-write-walkthrough.sh`, `session-start.sh`, `stop-guard.sh`

`platform-steer.sh` is new since the work order — and is the subject of V10
("inherited platform-steer mutation gap closed").

## Conflict disposition

Per the work order's own instruction — *"Derive present-day counts from D6.
Preserve conflicting historical counts in the record, identify the conflict
explicitly, and do not force the implementation or its gates to satisfy
inconsistent numeric assertions"* — the historical counts are preserved above
and **not** treated as targets. No gate was adjusted to satisfy 18/13/6/9.

Two work-order assertions were already refuted by the prior run and remain
refuted at HEAD:
1. "9 script registrations" — the repo is right at 12.
2. The head's folded `description: >` risking the 1024-char ceiling — `proofpunk`
   has the *shortest* description of all skills.

## Toolchain presence on this host

| Tool | Status |
|---|---|
| python3 | PRESENT 3.11.6 |
| tar | PRESENT bsdtar 3.5.3 |
| git | PRESENT 2.55.0 |
| pandoc | PRESENT 3.11 |
| node | PRESENT v22.22.3 |
| bun | PRESENT (required by `test-integrations.mjs`) |
| jq | PRESENT (jaq 2.3.0) |
| mmdc | PRESENT 11.6.0 |
| PyYAML | PRESENT 6.0.2 |
| claude-agent-sdk | PRESENT |
| **shellcheck** | **ABSENT** — bears on improvement I10 |
| claude | PRESENT 2.1.270 |
| opencode | PRESENT 1.18.30 |
| omp | PRESENT 18.1.20 |

All three target hosts are installable on this machine, so per-host conformance
can be driven rather than asserted — **except** where a live authenticated
session is required, which is blocked (see `step-01`).
