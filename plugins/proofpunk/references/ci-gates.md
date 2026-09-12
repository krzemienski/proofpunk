# CI / Pre-Commit Quality Gates (shared)

Methodology for layered build-quality gates, condensed from
`build-quality-gates`. Use when a project needs pre-commit hooks or CI gates
that catch failures early without slowing the loop.

**Loaded by:** `production-readiness`, from its codebase-audit lens
(`skills/production-readiness/SKILL.md:41-43`) — when that audit finds a project
has no pre-commit or CI gates configured, it loads this file and proposes the
P0→P1→P2 rollout below rather than inventing gate criteria ad hoc.

This note previously described that wiring as an open gap and asked a follow-up
lane to add the load instruction. The instruction was added; the note was not
updated, so the file spent that time contradicting the skill that loads it. A
reference asserting its own disuse is worse than one that says nothing: it tells
a reader the opposite of what the tree does.

## Priority Classification

Gates are classified by blast radius and rolled out iteratively:

| Priority | What it catches | When | Target time |
|----------|----------------|------|-------------|
| P0 Critical | Temp files, missing deps, broken fixtures, syntax errors | Pre-commit | <10s |
| P1 Enhanced | Shell quality, debug statements, import hygiene, doc freshness | Pre-commit | <30s |
| P2 Optimization | Cross-module integration, performance regression, full static analysis | Pre-push or CI | <120s |

**Rollout order matters**: P0 first (highest ROI), measure improvement, then
P1, then P2. Each tier should show measurable CI-failure-rate improvement
before the next is added.

## Baseline First

Analyze the last ~50 CI runs and categorize failures (temp files, deps,
imports, test infra, code quality, build config, environment) before writing
any gate. Gates target the failure categories that actually occur.

## Relationship to End-User Testing

CI gates are fast mechanical checks — the regression rail. They complement,
never replace, the end-user testing proof standard in `evidence-contract.md`. A green pre-commit hook
proves the build is clean; it does not prove the feature works. Behavioral
proof still requires the AI driving the real system as the end user per
`end-user-actor.md`. Conversely, do not put slow end-to-end journeys in
pre-commit; P2/CI is the right layer for anything over ~30s.
