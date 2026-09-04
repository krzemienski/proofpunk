# Proofpunk

Evidence-driven delivery pipeline for Claude Code: brainstorm, plan, harden,
implement, end-user test, and audit — with executed proof, no-mock
discipline, and an end-user actor mandate baked into every skill.

Consolidated from a curated review of a 445-skill archive. See
`docs/consolidation-decisions.md` for the full source mapping.

## Operating Principles

1. **The Iron Rule** — if the real system doesn't work, fix the real system.
   Never mocks, stubs, test doubles, fake endpoints, or test-mode bypasses.
2. **End-User Actor Mandate** — validation is NEVER faked, skipped, stubbed,
   or assumed complete. The AI personally executes MCP/automation tools and
   performs the actions as a real end user — clicking, tapping, typing,
   submitting — across every skill in this plugin. Not delegated, not
   skipped, not marked complete without actual execution. Unexecuted
   validation is reported as UNVERIFIED, never as done. Passive "2D"
   verification (screenshots without interaction, code reading, file
   existence checks) is inspection — it can support a verdict but never
   substitute for driven end-user action.
3. **Fresh evidence** — run-scoped, sequential, non-empty, never reused
   across runs, cited by full path with a description of what is SEEN.
4. **Gates before claims** — PASS criteria defined before evidence; no gate,
   task, or phase is marked complete without personally examined proof.

## Skills

| Skill | Use it to |
|-------|-----------|
| `proofpunk` | Router head: reads the ask, names the single best-fit skill (or short ordered chain for compound asks), hands off without repeating that skill's doctrine |
| `brainstorm` | Decide the approach: scout-first ideation, trade-off analysis, brutal honesty, approved design before any code |
| `validation-plan` | Author BRIEF -> ROADMAP -> per-phase plans with blocking cumulative proof obligations |
| `plan-hardening` | Red-team a draft plan (4 lenses), score confidence gaps, inject proof obligations, strengthen prompts |
| `implement` | Implement features/plans with review gates, side-effect-proofing, and end-user verification |
| `full-functional-audit` | Audit EVERY interaction in an app: Explore -> Plan -> Execute -> Remediate -> Verdict |
| `end-user-testing` | Fresh run-scoped evidence, cache clearing, citation discipline, phase verdicts |
| `visual-inspection` | Mandatory visual QA for screenshots (iOS HIG, WCAG 2.2, defect database) |
| `ui-experience-audit` | Deep per-screen audit: visual + interactive + content + Nielsen heuristics |
| `prompt-forge` | Author, rate (rubric + test cases), optimize prompts; build meta-prompt pipelines |
| `stack-testing` | Per-stack real-system testing: pytest/Go/C++/Django/Spring gotchas, FastAPI SSE, Playwright e2e, condition-based waiting |
| `mobile-validation-runner` | iOS simulator validation: SETUP→RECORD→ACT→COLLECT→VERIFY, three-facet gates, simctl/XC-MCP/Expo |
| `tui-testing` | End-user proof for terminal UIs (Ink, blessed, textual, ratatui): real-PTY driving, observe-then-act waits, three-facet evidence (screen + disk + logs) |
| `root-cause-debugging` | Reproduce-first diagnosis, backward tracing, pollution bisection — no symptomatic hacks |
| `production-readiness` | 8-phase ship-readiness audit, spec-compliance matrix, dependency supply-chain health |
| `red-team-eval` | 4-lens hostile review, eval-driven development, QA cycling to measured goal attainment |
| `session-intent` | Reconstruct per-session intent from Claude Code transcripts; intent-vs-implementation matrices |
| `codebase-truth-audit` | Evidence-backed repo-wide audit: reconstruct change intent from history, verify code/config/docs/deps, approval-gated safe remediation |

Shared references (loaded on demand by the skills):
`references/evidence-contract.md`, `references/end-user-actor.md`,
`references/platform-routing.md`, `references/preflight-checks.md`,
`references/api-validation.md`, `references/cli-validation.md`,
`references/ios-validation.md`, `references/web-validation.md`,
`references/ci-gates.md`, `references/severity-model.md`,
`references/ios-hig-checklist.md`, `references/web-wcag-checklist.md`,
`references/defect-pattern-database.md`.

Helper script: `skills/end-user-testing/scripts/fresh_evidence.py`
(`init-run` / `next-step` / `seal` / `validate`; Python 3.8+, stdlib only).
Verdict report template: `skills/end-user-testing/assets/verdict-template.md`.

## Installation

### From a local marketplace directory

```bash
# clone or unpack proofpunk-marketplace, then in Claude Code:
/plugin marketplace add /path/to/proofpunk-marketplace
/plugin install proofpunk@proofpunk-marketplace
```

### From the packaged archive

```bash
tar -xzf proofpunk-marketplace.tar.gz
/plugin marketplace add ./proofpunk-marketplace
/plugin install proofpunk@proofpunk-marketplace
```

Verify: `/plugin` should list `Proofpunk` with 18 skills.

## Representative Usage

**Validate one feature against the real system**

```
Validate the login flow end-to-end.
→ end-user-testing: defines PASS criteria, starts the dev server,
  drives the browser as an end user (fill form, submit, observe dashboard),
  captures e2e-evidence/run-.../step-NN-*.png, verdict with full-path citations.
```

**Audit a whole app before release**

```
Run a full functional audit of the app.
→ full-functional-audit: inventories every route/button/form/endpoint,
  batches with resource mutexes, drives every interaction, fixes FAILs
  against the real system, revalidates blast radius, final verdict report.
```

**Review a screen**

```
Audit this settings screen (screenshot attached / running on localhost:3000).
→ ui-experience-audit: triage, visual defects, interactive inventory,
  content quality, Nielsen heuristics — driving the live page when tools
  are available, otherwise identify-and-delegate with a hand-off task list.
```

**Plan a multi-phase build that can't fake progress**

```
Create a validation plan for the notifications feature.
→ validation-plan: .planning/BRIEF.md + ROADMAP.md + phases/*/ with
  evidence gate blocks; phase N re-proves phases 1..N-1.
```

**Strengthen a draft plan**

```
Harden .planning/phases/02-sync/02-01-PLAN.md before we execute it.
→ plan-hardening: red-teams through adversary/operator/integrator/skeptic
  lenses, remediates the gap register, injects blocking proof obligations.
```

**Implement after approval**

```
Implement the notifications plan.
→ implement: scout, exact requirements, plan review gate, implementation,
  code review, end-user drive of the finished feature, report.
```

**Author or rate a prompt**

```
Rate this system prompt and fix what's weak: <prompt>
→ prompt-forge: rubric score /100 across 7 dimensions, test cases,
  before/after re-measurement on real failure outputs.
```

**Capture gated evidence manually**

```bash
python3 skills/end-user-testing/scripts/fresh_evidence.py init-run phase-03
python3 skills/end-user-testing/scripts/fresh_evidence.py next-step submit-form
# ... capture artifacts into the printed path prefix ...
python3 skills/end-user-testing/scripts/fresh_evidence.py seal
python3 skills/end-user-testing/scripts/fresh_evidence.py validate
```

## Typical Pipeline

```
brainstorm → validation-plan → plan-hardening → implement
     → stack-testing (per-stack suites, deflaking)
     → full-functional-audit
     → mobile-validation-runner (iOS features)
     → ui-experience-audit / visual-inspection
     → end-user-testing verdicts at every phase boundary
Support lanes: session-intent (what was actually asked, from transcripts),
root-cause-debugging (any failure), red-team-eval (hostile review + measured
quality), production-readiness (release gate)
```

## Requirements

No external dependencies. The helper script uses Python 3 stdlib only.
Platform tooling (browser automation, simulator control, Playwright, curl)
is used when available; skills degrade to explicit BLOCKED/delegate verdicts
rather than simulating results when no tool path exists.
