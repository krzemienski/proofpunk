# Severity Model (shared)

Canonical severity classification and verdict rules for all Proofpunk
review and audit skills. Consolidated from `visual-inspection`,
`ui-experience-audit`, and `full-functional-audit`.

## Severity Levels

| Severity | Definition | Action |
|----------|-----------|--------|
| CRITICAL | Content unreadable or missing, overlapping text, crash state, broken interaction (false affordance), unrecoverable error, accessibility blocker, lorem ipsum / placeholder in production-looking UI | Fix immediately, blocks completion |
| HIGH | Broken layout, misaligned elements, illegible content (e.g. failing code-block contrast), heuristic violation causing user confusion, undersized or overlapping touch targets | Fix before commit |
| MEDIUM | Inconsistent spacing, weak signifier, redundant content, minor heuristic drift, suspect contrast | Fix in same session |
| LOW | Cosmetic polish, subtle alignment drift, edge-case rendering | Log for future pass |

Do not mark LOW issues "not worth fixing" — accumulated cosmetic debt
compounds into perceived low quality. Log ALL severities; fix CRITICAL/HIGH
immediately, track MEDIUM/LOW.

## Verdict Rules

| Verdict | Condition |
|---------|-----------|
| FAIL | Any CRITICAL finding in any phase |
| PASS WITH ISSUES | Zero CRITICAL, but >= 1 HIGH or accumulated MEDIUM; shippable only if HIGH issues are tracked and remediation scheduled |
| PASS (LIMITED COVERAGE) | Zero CRITICAL and zero HIGH, but coverage is single-axis (only light mode, only desktop, only happy path); the audited slice passes but a global PASS is not earned |
| BLOCKED | Runtime target unreachable or evidence capture impossible — never convert a BLOCKED into a PASS by simulating |
| UNVERIFIED | Validation steps were not actually executed by the AI as the end user — never report unexecuted validation as done |
| PASS | Zero CRITICAL, zero HIGH, full coverage represented, AND every behavioral criterion was verified by the AI driving the real system as the end user (see `end-user-actor.md`) |

A PASS for behavior requires executed, tool-driven, end-user-perspective
checks. Inspection-only evidence (screenshots, code reading, unit tests,
delegated summaries) caps behavioral verdicts at PASS WITH ISSUES
(verification pending) or UNVERIFIED — never a full behavioral PASS.

## Coverage Axes

A verdict must state which axes were covered:

- Light mode AND dark mode
- Multiple viewports (mobile, tablet, desktop) for web
- Empty / loading / populated / error states
- Long-content / overflow states

Any single-axis coverage is itself a finding ("dark mode not audited").

## Finding Record Format

```
[SEVERITY] [CHECKLIST_ITEM or ELEMENT] — <what you SEE, concretely> — <suggested fix>
```

Every finding names: the failed criterion, the observable defect, the owning
view/file (when identifiable), severity, and a suggested fix.

## Suspicion Rule

A 0-finding audit of a real screen is suspicious. Even good screens typically
have >= 3 LOW-or-above findings. Zero findings usually means a phase was
skipped — re-run before reporting.
