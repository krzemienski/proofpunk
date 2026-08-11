#!/usr/bin/env python3
"""Initialize a generic codebase truth-audit workspace."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable


PHASES: tuple[tuple[str, str], ...] = (
    ("phase-01-scope-and-baseline.md", "Scope and Baseline"),
    ("phase-02-intent-and-history.md", "Intent and History Reconstruction"),
    ("phase-03-code-and-config-truth.md", "Code and Configuration Truth"),
    ("phase-04-documentation-claims.md", "Documentation Claim Audit"),
    ("phase-05-runtime-evidence.md", "Runtime and Evidence Validation"),
    ("phase-06-findings-and-remediation.md", "Findings and Remediation Plan"),
    ("phase-07-confirmation.md", "Confirmation Gate"),
    ("phase-08-approved-remediation.md", "Approved Remediation"),
    ("phase-09-final-verification.md", "Final Verification and Report"),
)

DEFAULT_CRITERIA: tuple[tuple[str, str], ...] = (
    ("SC-1", "Repository identity, branch, HEAD, worktree state, constraints, and baseline commands are recorded."),
    ("SC-2", "Subsystem and decision-carrying-file inventory is complete for the approved scope."),
    ("SC-3", "Relevant history is reconstructed as intent -> action -> changed files -> commit/current result."),
    ("SC-4", "Actual execution paths are mapped for every in-scope subsystem with resolving path:line evidence."),
    ("SC-5", "Configuration, threshold, contract, and magic-number provenance is traced from declaration to application."),
    ("SC-6", "Every extracted documentation claim is classified and verified against current evidence."),
    ("SC-7", "Runtime behavior is validated with real or explicitly labeled production-like evidence and reproducible commands."),
    ("SC-8", "Findings include severity, blast radius, evidence, remediation options, validation, rollback, and approval needs."),
    ("SC-9", "The confirmation gate records explicit approval before behavior, dependency, destructive, or broad documentation changes."),
    ("SC-10", "Only approved remediation is executed, and each change has post-change validation."),
    ("SC-11", "The final report closes every criterion as done, blocked, or not started with no silent drops."),
)


def run_git(repo: Path, args: Iterable[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            text=True,
            capture_output=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def git_value(repo: Path, args: Iterable[str]) -> str | None:
    code, stdout, _ = run_git(repo, args)
    return stdout if code == 0 and stdout else None


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "codebase-truth-audit"


def unique_path(base: Path) -> Path:
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}-{suffix}")
        suffix += 1
    return candidate


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def criteria_table() -> str:
    rows = ["| ID | Criterion | Verification | Status | Evidence |", "|---|---|---|---|---|"]
    rows.extend(f"| {key} | {criterion} |  | pending |  |" for key, criterion in DEFAULT_CRITERIA)
    return "\n".join(rows)


def build_plan(args: argparse.Namespace, workspace: Path, metadata: dict[str, object]) -> str:
    return f"""# Codebase Truth Audit Plan

## Audit metadata

| Field | Value |
|---|---|
| Workspace | `{workspace}` |
| Repository | `{metadata['repository']}` |
| Branch | `{metadata['branch']}` |
| HEAD | `{metadata['head']}` |
| Audit window start | `{args.start or 'not specified'}` |
| Audit window end | `{args.end or 'not specified'}` |
| Created | `{metadata['created_at']}` |
| Worktree status | `{metadata['status_summary']}` |

Replace every default below with repository-specific requirements before discovery closes.

## Success criteria

{criteria_table()}

## Scope register

| Subsystem | Decision-carrying files | Entry points | Owner/source | Status | Evidence |
|---|---|---|---|---|---|
|  |  |  |  | pending |  |

## Safety register

| Constraint | Scope affected | Enforcement | Status |
|---|---|---|---|
| Existing dirty/untracked files are foreign work | all | check `git status` before edits | active |
| No behavior change before explicit approval | code/config | confirmation gate | active |
| No deletion/archive before explicit approval | cleanup | confirmation gate | active |

## Phase log

| Phase | Status | Started | Finished | Evidence |
|---|---|---|---|---|
{chr(10).join(f"| {title} | pending |  |  |  |" for _, title in PHASES)}

## No-silent-drops register

| Item | Disposition | Reason | Blocker/need | Evidence |
|---|---|---|---|---|
| none recorded |  |  |  |  |
"""


def phase_template(title: str, workspace: Path) -> str:
    return f"""# {title}

## Objective

Describe the repository-specific objective for this phase.

## Inputs

| Input | Source | Status |
|---|---|---|
|  |  | pending |

## Work log

| Time (UTC) | Action | Command/tool | Exit/result | Evidence |
|---|---|---|---|---|
|  |  |  |  |  |

## Findings

| ID | Finding | Severity | Evidence | Remediation option | Approval required |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## Exit criteria

- [ ] Evidence cited for every conclusion.
- [ ] Incomplete or blocked items copied to the no-silent-drops register in `plan.md`.
- [ ] Next-phase dependencies recorded.

Workspace: `{workspace}`
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a codebase truth-audit workspace.")
    parser.add_argument("--repo", required=True, help="Repository root or a path inside it")
    parser.add_argument("--label", default="codebase-truth-audit", help="Workspace label")
    parser.add_argument("--start", help="Audit-window start date or commit")
    parser.add_argument("--end", help="Audit-window end date or commit")
    parser.add_argument(
        "--output-root",
        help="Parent directory for the audit workspace (default: <repo>/plans)",
    )
    args = parser.parse_args()

    supplied_repo = Path(args.repo).expanduser().resolve()
    if not supplied_repo.exists():
        print(f"error: repository path does not exist: {supplied_repo}", file=sys.stderr)
        return 2

    git_root_value = git_value(supplied_repo, ["rev-parse", "--show-toplevel"])
    repo = Path(git_root_value).resolve() if git_root_value else supplied_repo
    branch = git_value(repo, ["branch", "--show-current"]) or "not a git repository or detached HEAD"
    head = git_value(repo, ["rev-parse", "HEAD"]) or "unavailable"
    status_code, status, status_err = run_git(repo, ["status", "--short"])
    if status_code != 0:
        status = f"git status unavailable: {status_err or 'unknown error'}"
    status_lines = [] if not status else status.splitlines()
    status_summary = "clean" if status_code == 0 and not status_lines else f"{len(status_lines)} status entries"

    output_root = Path(args.output_root).expanduser().resolve() if args.output_root else repo / "plans"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M")
    workspace = unique_path(output_root / f"{stamp}-{slugify(args.label)}")
    evidence = workspace / "evidence"
    evidence.mkdir(parents=True, exist_ok=False)

    created_at = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    metadata: dict[str, object] = {
        "created_at": created_at,
        "supplied_repo": str(supplied_repo),
        "repository": str(repo),
        "branch": branch,
        "head": head,
        "audit_window": {"start": args.start, "end": args.end},
        "status_summary": status_summary,
        "status_entries": status_lines,
    }

    write_text(evidence / "repository-metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False))
    write_text(evidence / "git-status.txt", status or "clean")
    remotes_code, remotes, remotes_err = run_git(repo, ["remote", "-v"])
    write_text(evidence / "git-remotes.txt", remotes if remotes_code == 0 else remotes_err or "unavailable")

    write_text(workspace / "plan.md", build_plan(args, workspace, metadata))
    for filename, title in PHASES:
        write_text(workspace / filename, phase_template(title, workspace))
    write_text(workspace / "final-report.md", "# Final Report\n\nComplete after all success criteria are closed.\n")

    print(workspace)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
