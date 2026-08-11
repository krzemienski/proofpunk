---
name: codebase-truth-audit
description: Conduct an evidence-backed, end-to-end audit and safe remediation of any software repository. Reconstruct change intent from history, verify code, configuration, documentation, runtime behavior, dependencies, and production readiness; identify drift, dead code, stale docs, cleanup risks, and remediation options; pause for explicit approval before behavior or destructive changes; then execute approved remediation with validation. Use when asked to audit a codebase, compare implementation with intent or docs, plan a refactor, clean a repository safely, close documentation drift, or prepare a repo for production.
---

# Codebase Truth Audit

Use this workflow for repository-wide truth audits and safe remediation. It is codebase-agnostic: derive paths, subsystems, commands, windows, baselines, and acceptance criteria from the user's request and the target repository. Do not carry over project-specific paths, dates, thresholds, subsystem names, or prior findings from another audit.

## Core contract

1. Ground every conclusion in evidence: a commit, command output, test result, measurement, or `path:line` that resolves in the checked-out tree.
2. Work from the repository, not from summaries, memory, session narratives, or prior reports. Treat those as leads and verify them independently.
3. Do not use mocks, fixtures, synthetic inputs, or fabricated expected values to claim production behavior. If only test fixtures exist, label the result fixture-backed rather than production-backed.
4. Do not edit runtime behavior, delete files, archive artifacts, or rewrite documentation before the confirmation gate records the user's explicit approval for that class of change.
5. Never overwrite, restore, or delete work that may belong to someone else. Check `git status` before edits and stop the affected item if a file is already dirty.
6. Make one change, validate it, then proceed. Do not batch unrelated fixes.
7. Do not tune constants merely to make a metric pass. Explain a behavior change and validate its mechanism, or leave it out.
8. Do not narrow scope silently. Any dropped, deferred, downgraded, or unverified item must appear in the final report with its reason and blocker.
9. Continue every unblocked lane when one lane is blocked. A blocker is not permission to stop the whole audit.
10. Persist progress continuously so a fresh session can resume from the audit workspace.

## Required inputs

Resolve these at task start:

| Input | Resolution rule |
|---|---|
| Repository root | Use the user's path when supplied; otherwise locate the repository explicitly. Confirm with `git rev-parse --show-toplevel` when possible. |
| Branch and HEAD | Resolve live with `git branch --show-current` and `git rev-parse HEAD`; never reuse a prior identifier. |
| Worktree state | Record `git status --short`. Treat existing modified/untracked files as foreign work. |
| Audit window | Use the user's dates or commit range when supplied. If unspecified, state the selected window and why it is appropriate. |
| Scope | Derive subsystems from the request, architecture, ownership files, manifests, entry points, and directory structure. Do not assume a fixed subsystem list. |
| Ground truth | Identify real acceptance tests, production-like inputs, golden datasets, metrics, and expected behavior. Distinguish ground truth from convenience fixtures. |
| Safety constraints | Record files, branches, data, credentials, or environments that must not be touched. |
| Success criteria | Build an explicit checklist before discovery. Each item needs a verification method and evidence artifact. |
| Confirmation requirements | Identify actions requiring user approval: behavior changes, migrations, deletion, destructive cleanup, dependency changes, and public API changes. |

Ask the user only when a missing input materially changes scope or safety and cannot be inferred from the repository. Prefer bounded choices and continue with safe read-only discovery when possible.

## Workflow

### 0. Initialize the audit

1. Resolve repository root, branch, HEAD, remotes, tags, and worktree status.
2. Inventory available tools, skills, test runners, linters, CI definitions, package managers, and deployment manifests.
3. Create an audit workspace. Prefer the bundled scaffold:

```bash
python3 scripts/init_audit_workspace.py --repo /path/to/repo --label codebase-truth-audit
```

Use `--start` and `--end` for a bounded history audit. The script creates `plans/<timestamp>-codebase-truth-audit/` with a plan, phase files, and an `evidence/` directory. Adjust its templates to match the repository and user requirements.
4. Record the execution method honestly. If delegation or a tool is unavailable, run directly and state that framing in the report.

### 1. Scope and baseline

- Define the subsystem inventory and the decision-carrying files for each subsystem. Include entry points, orchestration, configuration, persistence, external integrations, generated output, tooling, and tests.
- Establish baseline commands for build, test, lint, type-check, and runtime smoke checks. Prefer existing project commands; do not invent replacements.
- Run only appropriate baseline checks. Capture command, working directory, environment, version, output location, and exit code. Do not infer success from a prompt or partial log.
- Open the plan with the success-criteria checklist. Every criterion must end as **done**, **blocked**, or **not started**.

### 2. Intent and history reconstruction

- Build the timeline from source control: commits, tags, branches, merges, reverts, file histories, authorship, and commit messages.
- For each relevant change, map original intent → action taken → files changed → commit or uncommitted change → current result.
- Use issues, pull requests, design docs, session transcripts, or prior reports only as corroborating sources. Verify their claims at HEAD.
- Flag scope narrowing, waived anomalies, superseded plans, unverified assumptions, and claims that no longer resolve.
- Produce an intent-versus-implementation matrix. Include `intent unrecoverable` explicitly where evidence is absent; do not imply coverage.

### 3. Code and configuration truth

For each subsystem:

- Read the decision-carrying files end to end. Trace actual execution paths rather than relying on names or comments.
- Map inputs, outputs, state, error behavior, concurrency, persistence, external calls, and ownership boundaries.
- Verify configuration from declaration → load → runtime application. Flag declared-but-unused, default-overridden, duplicated, dead, or undocumented settings.
- Build a magic-number and threshold provenance table: value, declared location, read location, applied location, live/dead verdict, and evidence.
- Trace data contracts, including `null` versus empty values, optional fields, unit conventions, coordinate or time bases, schema versions, and failure propagation.
- Identify dead code, dead branches, stale feature flags, unused dependencies, orphaned generated files, and importer-proof candidates.
- Re-verify every known deviation at the current `path:line` and classify it as **HOLDS**, **CHANGED**, **RESOLVED**, or **NOT REPRODUCIBLE**.

### 4. Documentation claim audit

- Extract verifiable claims from README files, contributor guidance, changelogs, architecture docs, API docs, runbooks, comments, examples, and release notes.
- Classify each claim as **HOLDS**, **STALE**, **FALSE**, **ASPIRATIONAL**, or **UNVERIFIABLE**.
- Require every current-tense claim to cite evidence that resolves at HEAD. Relabel historical claims instead of silently preserving them.
- Check version numbers, file counts, module lists, diagrams, command examples, environment requirements, performance figures, security statements, and support promises.
- Produce a docs-drift ledger with severity, affected users, correction proposal, and verification evidence.

### 5. Runtime and evidence validation

- Use real production-like inputs and direct product entry points. Do not claim behavior from wrappers, mocks, or synthetic harnesses unless those are the actual production surface.
- Exercise one meaningful input at a time when per-input signal matters. Avoid aggregations that hide failures.
- Cache or reuse existing evidence when valid; do not regenerate expensive artifacts just to make them look fresh.
- Capture measurements with sample size, range, median or distribution, environment, input identity, and command. State exactly which metric is measured.
- Compare results to ground truth using the project's accepted tolerances. Distinguish count matching from exact matching, approximate metrics from exact metrics, and smoke checks from regression gates.
- For every failure class, collect at least one concrete artifact and the code path that produced it, or state `not observed in N runs` with the runs identified.

### 6. Findings and remediation plan

Synthesize only evidence-backed findings into:

- Missing requirements
- Misunderstood or superseded intent
- Implementation deviations
- Configuration and threshold drift
- Documentation drift
- Dead code, dead configuration, and orphaned artifacts
- Validation gaps
- Security, privacy, reliability, and compliance risks
- Dependency, build, deployment, and observability risks
- Cleanup candidates with risk and retention rationale
- Existing evidence that was ignored or misused

For each finding, record severity, blast radius, evidence, affected success criteria, remediation options, validation method, rollback plan, and whether user approval is required.

### 7. Confirmation gate

Pause before any behavior change, dependency change, migration, file deletion, archive action, or broad documentation rewrite. Present these views in the user's language:

1. Requested intent versus current state
2. Change timeline and provenance
3. What actually executes at HEAD
4. Configuration, threshold, and contract provenance
5. Runtime and ground-truth evidence
6. Test, benchmark, and metric quality
7. Documentation-drift ledger
8. Deviation and missing-work list
9. Cleanup census with keep/archive/delete recommendations and risks
10. Dependency, security, and production-readiness scorecard
11. Remediation options with validation and rollback
12. Recommended decision and immediate next action

Ask for an explicit ruling on each applicable action class:

- **A — Documentation-only remediation**
- **B — Runtime/code behavior remediation**
- **C — Cleanup, archive, or deletion**
- **D — Dependency or release changes**
- **E — Hold after the report**

Record the ruling, date, approver, scope, and any conditions in the audit workspace. Treat silence or an ambiguous answer as no approval.

### 8. Execute approved remediation

- Documentation: close every verified stale or false claim, cite current evidence, preserve history, and update indexes or navigation.
- Code: implement only approved behavior changes; keep each change small; validate after each step; update tests and docs in the same logical change.
- Cleanup: classify every candidate as keep, archive, or delete. Archive cited evidence; never delete it. Prove zero importers before removing code or files. Keep disposable outputs ignored so they do not reaccumulate.
- Dependencies: update only approved packages; record current version, target version, reason, compatibility evidence, and rollback path.
- Production readiness: verify build, tests, lint, type checks, CI, packaging, deployment manifests, secrets handling, logging, observability, error behavior, rollback, and release notes.
- Versioning: update version and changelog only when the change warrants it. State whether output or behavior changed.

### 9. Final verification and report

Close the audit with a reproducible report. For every success criterion, report exactly one state:

- **Done** — include the evidence artifact.
- **Blocked** — include what was tried, the alternative attempted, what is needed, and which criteria remain achievable.
- **Not started** — include the reason.

Include commands and exit codes for every gate, changed-file summary, risks that remain, rollback notes, and a no-silent-drops section listing every dropped or incomplete item. Do not call partial completion done.

## Orchestration

- Use at most six concurrent lanes. Reduce concurrency when tools rate-limit or operations interfere.
- If delegation is available, probe it with one control task before fanout. If delegation fails, say so and continue orchestrator-direct.
- Keep read-only discovery lanes separate from write lanes. Isolate code changes in a branch or worktree when the repository workflow supports it.
- Use an independent verification pass for irreversible or critical work. Do not let the same lane both perform and approve high-risk changes.
- Persist lane outputs in the shared audit workspace before synthesizing them.

## Evidence rules

- Prefer `path:line` for code and docs, commit hashes for history, artifact paths for generated evidence, and exact command transcripts for runtime checks.
- Re-resolve line references after edits. A citation that no longer resolves is historical, not current evidence.
- Copy referenced evidence into the audit workspace when the original location is disposable or ignored by version control.
- Keep raw logs when they support a verdict. Redact secrets and credentials.
- Mark inference clearly. Do not present an inferred result as an observed result.

## Bundled resources

- `scripts/init_audit_workspace.py` — create a timestamped audit workspace, capture repository metadata, and seed the plan, phase files, evidence directory, and default success criteria.
- `references/output-contract.md` — detailed templates for the plan, success-criteria matrix, phase reports, confirmation views, remediation register, cleanup census, and final report.

Read `references/output-contract.md` before producing the first audit artifact or the final report.
## Related Skills (this plugin)

- `session-intent` — the intent-reconstruction lane feeding Phase 2 (intent and history)
- `production-readiness` — ship-readiness audits; this is the repo-truth sibling
- `root-cause-debugging` — when audit findings need cause tracing before remediation
- `end-user-testing` — fresh-evidence discipline for every audit claim
