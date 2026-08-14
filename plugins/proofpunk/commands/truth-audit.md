---
description: Run a repo-wide intent-vs-code truth audit with evidence-backed findings
argument-hint: "<repo-path> [--since DATE] [--until DATE] [--label NAME]"
---

Activate the `codebase-truth-audit` skill and audit:

$ARGUMENTS

Ground every conclusion in a commit, command output, or path:line that resolves in the checked-out tree. Pause for explicit approval before any behavior-changing or destructive remediation.

## Examples

**1. Minimal — audit the current repo**

```
/proofpunk:truth-audit .
```
Full intent-vs-implementation audit with evidence-backed findings; pauses before any behavior change.

**2. With flags — bound the window**

```
/proofpunk:truth-audit . --since 2026-06-01 --label pre-release
```
Audits only the June-forward window and tags all evidence with the `pre-release` label.

**3. Composed — audit, then harden what the audit surfaces**

```
/proofpunk:truth-audit . --label q3
/proofpunk:cook "remediate the 3 HIGH findings from the q3 truth audit"
```
The audit produces the findings; cook executes the approved remediation to end-user proof.

**5. Full command — every option selected**

```
/proofpunk:truth-audit . --since 2026-01-01 --until 2026-08-13 --label fy26-h2-audit
```
Windowed session-intent alignment across the whole repo, every commit in
the window mapped to its transcript intent or marked unrecoverable, labeled
evidence pack under `.planning/audits/fy26-h2-audit/`.
