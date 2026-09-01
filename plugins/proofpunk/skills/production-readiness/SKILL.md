---
name: production-readiness
description: >
  Take a codebase from 'works on my machine' to shippable — systematic
  8-phase production-readiness audit (risk-based cleanup waves, dead code
  documentation drift, zero-regression enforcement), spec-vs-implementation
  compliance audits that find COVERED/INCOMPLETE/MISSING gaps, and
  dependency supply-chain health (CVEs, CVSS, lockfile hygiene, license
  compliance). Use when preparing a first release, open-sourcing, doing a
  major version bump, auditing whether a spec was fully implemented
  reviewing dependency risk, or after rapid prototyping leaves the repo in
  unknown shape. Not for runtime feature QA (drive the real system per the shared runbooks),
  screenshot review (use visual-inspection), or intent provenance (use
  session-intent).
---

# Production Readiness

## Run checklist

Copy this checklist and track your progress:

- [ ] Run the 8-phase readiness audit (cleanup waves, dead code, doc drift, zero-regression)
- [ ] Run spec-vs-implementation compliance scan (COVERED / INCOMPLETE / MISSING)
- [ ] Audit dependency supply chain (CVEs, CVSS, lockfile, licenses)
- [ ] Generate remediation plan with validation gates
- [ ] Execute approved remediations; re-verify zero regressions

Ship-readiness is proven, not felt. Three lenses, each with its own reference
all reporting through the plugin's evidence discipline
(`../../references/evidence-contract.md`): every claim in the readiness report
cites the command output, file, or audit artifact that proves it.

## The Three Lenses

1. **Codebase audit** — `references/production-readiness-audit.md`
   Systematic 8-phase methodology: risk-based cleanup waves, parallel audit
   passes, dead-code and documentation-drift hunts, validation checkpoints between
   waves, zero-regression enforcement (the suite is green before and after
   every wave — re-run it, don't assume it).
   When the audit finds no pre-commit or CI gates configured, load
   `../../references/ci-gates.md` and propose its P0→P1→P2 rollout rather
   than inventing gate criteria ad hoc.
2. **Spec compliance** — `references/spec-compliance.md`
   Extract every requirement from the spec, map each to implementation
   evidence, and grade COVERED / INCOMPLETE / MISSING. Missing coverage
   generates blocking validation checkpoints — not a shrug in a report footnote.
3. **Dependency health** — `references/dependency-health.md`
   CVE and CVSS triage, lockfile hygiene, freshness vs. stability trade-offs
   supply-chain attack surface, license compliance. Every dependency is
   justified or removed.

## When to Run Which

| Trigger | Lens |
|---|---|
| First release / open-sourcing / version bump | All three, in the order above |
| "Did we implement everything in the spec?" | Spec compliance |
| Dependabot noise, audit findings, new package request | Dependency health |
| Post-hackathon repo in unknown shape | Codebase audit first |

## Workflow

1. Baseline: green suite + fresh evidence run BEFORE touching anything
   (`scripts/` from `end-user-testing` — init-run first).
2. Codebase audit waves, riskiest first; suite re-run after every wave.
3. Spec-compliance matrix appended to the readiness report.
4. Dependency report: CVEs by CVSS band, remediation or explicit acceptance.
5. Verdict: READY / READY-WITH-CONDITIONS / NOT-READY, every line cited.

## Anti-Patterns

- Deleting "dead" code without a green-suite safety net per wave.
- Declaring spec coverage from memory of the codebase → extract and map.
- Auto-upgrading everything to silence audit output → triage by CVSS and
  blast radius; pin with justification.
- A readiness report with no reproducible commands in it.


## Example

**Input:** User: 'Get this repo ready for its first release.'

**Output:** 8-phase audit finds 12 risks (3 high), compliance scan shows 31 COVERED / 4 INCOMPLETE / 2 MISSING, 1 CVE flagged with CVSS 7.5 — remediation plan with validation gates delivered.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `codebase-truth-audit` | cleanup waves | the audit engine for dead code + drift |
| `full-functional-audit` | functional lens | app-wide interaction validation pre-release |
| `stack-testing` | zero-regression enforcement | regression rail per stack |
| `end-user-testing` | all evidence | fresh-evidence sealing |

Called by: `proofpunk`.
