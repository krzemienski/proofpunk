# Output Contract

Use these templates for a consistent, resumable codebase truth audit. Replace every placeholder with repository-specific evidence. Delete rows that are not applicable only after recording the reason in the no-silent-drops register.

## Workspace layout

Default workspace:

```text
plans/<YYYYMMDD-HHMM>-codebase-truth-audit/
├── plan.md
├── phase-01-scope-and-baseline.md
├── phase-02-intent-and-history.md
├── phase-03-code-and-config-truth.md
├── phase-04-documentation-claims.md
├── phase-05-runtime-evidence.md
├── phase-06-findings-and-remediation.md
├── phase-07-confirmation.md
├── phase-08-approved-remediation.md
├── phase-09-final-verification.md
├── final-report.md
└── evidence/
    ├── repository-metadata.json
    ├── git-status.txt
    ├── git-remotes.txt
    └── <command-logs, measurements, comparisons, censuses>
```

Put user-facing or repository documentation updates at their normal repository locations only after the confirmation gate approves that class of edit. Keep copied raw evidence under `evidence/` so conclusions remain reproducible.

## Plan checklist

Open `plan.md` with an explicit success-criteria matrix. Adapt this default set to the user's request:

| ID | Criterion | Verification | Status | Evidence |
|---|---|---|---|---|
| SC-1 | Repository identity, branch, HEAD, worktree state, constraints, and baseline commands are recorded. | Review `repository-metadata.json`, `git-status.txt`, and baseline log | pending |  |
| SC-2 | Subsystem and decision-carrying-file inventory is complete for the approved scope. | Compare inventory with manifests, entry points, CI, and directory structure | pending |  |
| SC-3 | Relevant history is reconstructed as intent -> action -> changed files -> commit/current result. | Review history matrix coverage | pending |  |
| SC-4 | Actual execution paths are mapped for every in-scope subsystem. | Spot-check citations and trace entry points | pending |  |
| SC-5 | Configuration, threshold, contract, and magic-number provenance is traced from declaration to application. | Review provenance table for unexplained rows | pending |  |
| SC-6 | Every extracted documentation claim is classified and verified against current evidence. | Review docs-drift ledger | pending |  |
| SC-7 | Runtime behavior is validated with real or explicitly labeled production-like evidence. | Review commands, exits, inputs, and metrics | pending |  |
| SC-8 | Findings include severity, blast radius, evidence, remediation options, validation, rollback, and approval needs. | Independent review of findings register | pending |  |
| SC-9 | Confirmation gate records explicit approval before behavior, dependency, destructive, or broad documentation changes. | Review `phase-07-confirmation.md` | pending |  |
| SC-10 | Only approved remediation is executed, and each change has post-change validation. | Review change log and validation logs | pending |  |
| SC-11 | Final report closes every criterion as done, blocked, or not started with no silent drops. | Review final checklist against plan and phase files | pending |  |

Use only three terminal states: `done`, `blocked`, `not started`.

## Repository baseline record

```markdown
## Baseline

| Item | Value | Evidence |
|---|---|---|
| Repository root |  |  |
| Branch |  |  |
| HEAD |  |  |
| Audit window |  |  |
| Worktree state | clean / dirty / unknown |  |
| Package manager |  |  |
| Runtime versions |  |  |
| Build command |  |  |
| Test command |  |  |
| Lint command |  |  |
| Type-check command |  |  |
| Runtime smoke command |  |  |
| CI definition |  |  |
| Deployment definition |  |  |

### Command log

| Command | Working directory | Environment | Exit code | Output artifact | Interpretation |
|---|---|---:|---:|---|---|
|  |  |  |  |  | observed / inferred |
```

Capture exit codes directly. Do not infer success from absence of an error message.

## Scope and subsystem inventory

```markdown
| Subsystem | Purpose inferred from | Decision-carrying files | Entry points | Inputs | Outputs | External dependencies | Status |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  | pending |
```

Rules:

- Include orchestration, configuration, persistence, API/CLI, generated output, integrations, observability, tooling, tests, and deployment surfaces.
- Include files that carry decisions, not necessarily every file in the repository.
- State the source used to infer each purpose.
- Mark uncertain ownership or boundaries explicitly.

## Intent-versus-implementation matrix

```markdown
| Change/session | Intent source | Intended action | Actual action | Files changed | Commit/range | Current verdict | Evidence |
|---|---|---|---|---|---|---|---|
|  | issue/commit/PR/docs/transcript |  |  |  |  | implemented / partial / diverged / unrecoverable |  |
```

Coverage rule: every relevant commit or work item in the selected window appears in the matrix, including commits with no recoverable intent. Use `intent unrecoverable` rather than inventing motivation.

## Code-truth map

```markdown
| Subsystem | Runtime path | Decision points | Data/state | Failure behavior | Evidence |
|---|---|---|---|---|---|
|  | caller -> module -> function -> output |  |  |  |  |
```

For each path, distinguish:

- What the code is named or documented to do.
- What the code actually does at HEAD.
- What tests prove.
- What production-like runs prove.
- What remains unverified.

## Configuration and magic-number provenance

```markdown
| Value/name | Declared at | Loaded/read at | Applied at | Overrides | Live/dead | Verdict | Evidence |
|---|---|---|---|---|---|---|---|
|  | path:line | path:line | path:line |  | live/dead/unknown | holds/changed/resolved/not reproducible |  |
```

Include constants, thresholds, feature flags, defaults, environment variables, CLI options, retries, timeouts, schema versions, and platform-specific branches. Flag every declared value that is never applied and every applied value with no visible declaration.

## Contract audit

```markdown
| Contract | Producer | Consumer | Empty state | Missing state | Error state | Units/base | Version | Evidence |
|---|---|---|---|---|---|---|---|---|
|  |  |  | [] / 0 / null / absent |  |  |  |  |  |
```

Use this for APIs, events, schemas, files, database rows, coordinates, timestamps, and cross-process boundaries. Never let inability to compute surface as a real zero unless the contract explicitly defines that behavior.

## Deviation register

```markdown
| ID | Claim | Prior source | Current location | Verdict | Severity | Blast radius | Evidence | Remediation |
|---|---|---|---|---|---|---|---|---|
|  |  |  | path:line | HOLDS / CHANGED / RESOLVED / NOT REPRODUCIBLE |  |  |  |  |
```

Re-resolve every known deviation at HEAD. Keep historical findings, but label them historical when they no longer apply.

## Documentation-drift ledger

```markdown
| ID | Document | Claim | Current-tense? | Verification | Verdict | Severity | Proposed correction | Evidence |
|---|---|---|---|---|---|---|---|---|
|  |  |  | yes/no |  | HOLDS / STALE / FALSE / ASPIRATIONAL / UNVERIFIABLE |  |  |  |
```

Audit all user-visible and operator-visible claims, including:

- Commands and examples
- Architecture and module counts
- API and configuration behavior
- Performance numbers
- Compatibility and installation requirements
- Security and privacy statements
- Test and CI status
- Version and release history
- Known limitations and TODOs

A current-tense claim requires current evidence. Mark unverifiable claims as unverifiable; do not turn them into soft confirmations.

## Runtime evidence record

```markdown
| Run | Input identity | Input type | Command | Environment | Exit code | Metric | Result | Exactness | Artifact |
|---|---|---|---|---|---:|---|---|---|---|
|  |  | production / production-like / fixture / synthetic |  |  |  |  |  | exact / approximate / count-only / smoke-only |  |
```

Rules:

- State sample size, range, median or distribution, and relevant tolerance.
- Identify whether boundaries, fields, counts, order, and side effects are exact.
- Keep per-input results when aggregation could hide a failure.
- Label fixture and synthetic evidence clearly; do not use it to prove production behavior.
- Attach command logs and output artifacts.

## Failure-class catalog

```markdown
| Failure class | Concrete artifact | Code path | Trigger | Impact | Reproducibility | Validation gap | Remediation |
|---|---|---|---|---|---|---|---|
|  |  | path:line |  |  | observed / intermittent / not observed in N runs |  |  |
```

For `not observed`, name the runs and inputs searched. Do not convert absence of observation into proof of absence.

## Findings register

```markdown
| ID | Finding | Category | Severity | Blast radius | Evidence | Options | Recommended option | Validation | Rollback | Approval |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  | requirement / implementation / config / docs / validation / security / dependency / cleanup |  |  |  |  |  |  |  | A/B/C/D/E |
```

Use severity consistently:

- **Critical**: data loss, security exposure, production outage, irreversible damage, or a false release claim.
- **High**: incorrect behavior or documentation likely to mislead operators/users, or a missing gate.
- **Medium**: maintainability, observability, or reliability weakness with a workaround.
- **Low**: local inconsistency with limited impact.
- **Info**: useful context without required action.

## Cleanup census

```markdown
| Path | Type | Last used/evidence | Referenced by | Recommendation | Risk | Approval | Action | Validation |
|---|---|---|---|---|---|---|---|---|
|  | file/dir/cache/generated output/tool state |  |  | keep/archive/delete |  | pending | pending |  |
```

Rules:

- Archive anything cited as evidence; never delete it.
- Prove zero importers before removing source files or symbols.
- Check for hidden references in CI, scripts, docs, package manifests, deployment config, and generated-code settings.
- Do not touch files carrying uncommitted foreign work.
- Add ignore rules for disposable outputs so they do not reaccumulate.
- Record cache purges separately from evidence deletion.

## Production-readiness scorecard

```markdown
| Area | Check | Result | Evidence | Risk | Remediation |
|---|---|---|---|---|---|
| Build |  | pass/fail/unverified |  |  |  |
| Tests |  | pass/fail/unverified |  |  |  |
| Lint/type check |  | pass/fail/unverified |  |  |  |
| CI |  | current/stale/missing |  |  |  |
| Dependencies |  | current/vulnerable/unpinned/unknown |  |  |  |
| Security |  | pass/fail/unverified |  |  |  |
| Logging/observability |  | adequate/gap/unverified |  |  |  |
| Error handling |  | adequate/gap/unverified |  |  |  |
| Deployment |  | reproducible/manual/unknown |  |  |  |
| Rollback |  | present/missing/unverified |  |  |  |
| Release notes/version |  | current/stale/not warranted |  |  |  |
```

## Confirmation record

Use `phase-07-confirmation.md` for the gate:

```markdown
# Confirmation Gate

## Views presented

- [ ] 1. Requested intent versus current state
- [ ] 2. Change timeline and provenance
- [ ] 3. What actually executes at HEAD
- [ ] 4. Configuration, threshold, and contract provenance
- [ ] 5. Runtime and ground-truth evidence
- [ ] 6. Test, benchmark, and metric quality
- [ ] 7. Documentation-drift ledger
- [ ] 8. Deviation and missing-work list
- [ ] 9. Cleanup census and risks
- [ ] 10. Dependency, security, and production-readiness scorecard
- [ ] 11. Remediation options with validation and rollback
- [ ] 12. Recommended decision and next action

## Decision

| Field | Value |
|---|---|
| Decision date |  |
| Approver |  |
| Approved action classes | A / B / C / D / E |
| Scope and conditions |  |
| Explicitly rejected actions |  |
| Evidence/views reviewed |  |

## Approval legend

- A: documentation-only remediation
- B: runtime/code behavior remediation
- C: cleanup, archive, or deletion
- D: dependency or release changes
- E: hold after the report
```

Do not infer approval from silence, a partial reply, or approval of a different action class.

## Remediation change log

```markdown
| Change | Approved class | Files touched | Pre-change evidence | Post-change validation | Exit codes | Rollback | Status |
|---|---|---|---|---|---|---|---|
|  | A/B/C/D |  |  |  |  |  | pending/done/blocked |
```

One row per logical change. Do not batch unrelated fixes into one row.

## Final report structure

```markdown
# Final Report

## Executive summary

State what was audited, what changed, what passed, what remains blocked, and the production-readiness verdict.

## Success-criteria closure

| ID | Final status | Evidence | Blocker/need |
|---|---|---|---|
| SC-1 | done / blocked / not started |  |  |

## Repository state

| Item | Start | End | Evidence |
|---|---|---|---|
| Branch |  |  |  |
| HEAD |  |  |  |
| Worktree |  |  |  |
| Version |  |  |  |

## Evidence-backed findings

Summarize only findings with citations.

## Remediation executed

| Change | Validation | Behavior changed? | Rollback |
|---|---|---|---|
|  |  | yes/no |  |

## Gates and commands

| Gate | Command | Exit | Result | Artifact |
|---|---|---:|---|---|
|  |  |  |  |  |

## Remaining risks and blockers

| Item | Risk | Needed | Owner/decision |
|---|---|---|---|
|  |  |  |  |

## No silent drops

List every dropped, deferred, downgraded, unverified, blocked, or not-started item. If none, state `none` and cite the completed plan checklist.

## Reproduction guide

List the exact commands and artifacts needed to reproduce the conclusions.
```

Do not restate raw evidence in prose when the evidence directory already contains it; cite the artifact and summarize the verdict.