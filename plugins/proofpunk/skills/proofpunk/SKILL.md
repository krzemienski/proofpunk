---
name: proofpunk
description: >
  Router and entry point for the proofpunk plugin's 17 delivery skills —
  reads a request, names the single best-fit skill (or short ordered chain
  for compound asks), and hands off without repeating that skill's own
  doctrine. Covers the full arc: brainstorm a design, plan or harden a
  multi-phase build, implement it end to end, audit a repo or a running
  app, chase a bug to its root, red-team an artifact, and prove any of it
  against the real system (web, API, CLI, iOS, TUI). Use when unsure which
  proofpunk skill applies, when a request spans more than one skill's
  scope, or when you want a map of the whole plugin before picking a
  skill yourself. Not a substitute for any listed skill's own workflow —
  it only routes.
---

# ProofPunk — Plugin Router

## Run checklist

- [ ] Classify the request: design, build, audit, bug, or proof ask
- [ ] Pick the single best-fit skill (or shortest ordered chain)
- [ ] Hand off — quote the ask, do not restate the target skill's method
- [ ] If nothing fits, say so rather than forcing a match

## Why a router

17 narrow skills, each cross-referencing neighbors in its own "Not for..."
clause — enough once inside one skill's context, not enough cold. This is
the one lookup before the 17 file reads.

## How to route

1. Classify by the ask's *shape*, not keywords — before any repo work.
2. Compound asks chain left to right; each named skill still runs its own
   full workflow, never shortcut.
3. Prefer the narrower skill over the broader one on ambiguity.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `brainstorm` | idea unclear, options untested, no plan exists yet | the raw ask, unfiltered |
| `implement` | scope is known and something must get built end to end | the approved design or plan |
| `validation-plan` | a multi-phase build needs a written roadmap before code | the goal and phase boundaries |
| `plan-hardening` | a draft plan or prompt exists but needs adversarial stress | the draft artifact |
| `codebase-truth-audit` | intent vs. implementation drift across a whole repo | the repo root and audit scope |
| `full-functional-audit` | every screen or endpoint of a live app needs a sweep | the app URL or entry point |
| `production-readiness` | shipping a first release or major version | the repo and target release date |
| `ui-experience-audit` | one screen or flow needs a UX/visual pass | the screen or flow in question |
| `root-cause-debugging` | one bug, unclear cause, symptom fixes keep failing | the reproduction steps or error |
| `red-team-eval` | a finished plan or output needs hostile review before ship | the artifact to attack |
| `stack-testing` | writing or deflaking tests for a specific language/framework | the failing suite or stack name |
| `mobile-validation-runner` | an iOS/Expo feature needs simulator proof | the feature and simulator target |
| `end-user-testing` | any completion claim needs run-scoped proof | the proof obligation to satisfy |
| `visual-inspection` | a screenshot needs a pass/fail verdict | the captured screenshot |
| `tui-testing` | a terminal app needs PTY-driven proof | the TUI binary and target behavior |
| `session-intent` | reconstructing why a past change happened | the commit or session in question |
| `prompt-forge` | authoring, rating, or optimizing a prompt itself | the prompt draft or goal |

## Shared doctrine — what every skill defers to

Routing names a skill; these files are the rules that skill obeys. The
installer rewrites these citations to self-contained copies, so they
resolve both in this repo and in an installed tree.

| Reference | Owns |
|-----------|------|
| `../../references/end-user-actor.md` | the Actor Mandate — who drives the system |
| `../../references/evidence-contract.md` | run-scoped, sealed, non-empty evidence |
| `../../references/platform-routing.md` | which runbook a target maps to |
| `../../references/api-validation.md` | backend/API proof |
| `../../references/web-validation.md` | browser proof |
| `../../references/cli-validation.md` | CLI proof |
| `../../references/ios-validation.md` | simulator proof |
| `../../references/severity-model.md` | how findings are ranked |
| `../../references/defect-pattern-database.md` | known defect shapes |
| `../../references/preflight-checks.md` | what must hold before a run |
| `../../references/ci-gates.md` | regression posture in CI |
| `../../references/web-wcag-checklist.md` | accessibility criteria |
| `../../references/ios-hig-checklist.md` | iOS interface criteria |

Called by: nothing — the entry point for the whole plugin.
