---
description: Run a repo-wide intent-vs-code truth audit with evidence-backed findings
argument-hint: "<repo-path> [--since DATE] [--until DATE] [--label NAME]"
---

Activate the `codebase-truth-audit` skill and audit:

$ARGUMENTS

Ground every conclusion in a commit, command output, or path:line that resolves in the checked-out tree. Pause for explicit approval before any behavior-changing or destructive remediation.

**5. Full command — every option selected**

```
/proofpunk-truth-audit . --since 2026-01-01 --until 2026-08-13 --label fy26-h2-audit
```
Windowed session-intent alignment across the whole repo, every commit in
the window mapped to its transcript intent or marked unrecoverable, labeled
evidence pack under `.planning/audits/fy26-h2-audit/`.
