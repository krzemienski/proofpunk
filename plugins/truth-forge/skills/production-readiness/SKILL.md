---
name: production-readiness
description: Take a codebase from "works on my machine" to shippable — systematic 8-phase production-readiness audit (risk-based cleanup waves, dead code, documentation drift, zero-regression enforcement), spec-vs-implementation compliance audits that find COVERED/INCOMPLETE/MISSING gaps and generate validation gates, and dependency supply-chain health (CVEs, CVSS, lockfile hygiene, license compliance). Use when preparing a first release, open-sourcing, doing a major version bump, auditing whether a spec was fully implemented, reviewing dependency risk, or after a rapid prototyping phase leaves the repo in unknown shape.
---

# Production Readiness

Ship-readiness is proven, not felt. Three lenses, each with its own reference,
all reporting through the plugin's evidence discipline
(`../../references/evidence-contract.md`): every claim in the readiness report
cites the command output, file, or audit artifact that proves it.

## The Three Lenses

1. **Codebase audit** — `references/production-readiness-audit.md`
   Systematic 8-phase methodology: risk-based cleanup waves, parallel audit
   passes, dead-code and documentation-drift hunts, validation gates between
   waves, zero-regression enforcement (the suite is green before and after
   every wave — re-run it, don't assume it).
2. **Spec compliance** — `references/spec-compliance.md`
   Extract every requirement from the spec, map each to implementation
   evidence, and grade COVERED / INCOMPLETE / MISSING. Missing coverage
   generates blocking validation gates — not a shrug in a report footnote.
3. **Dependency health** — `references/dependency-health.md`
   CVE and CVSS triage, lockfile hygiene, freshness vs. stability trade-offs,
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
   (`scripts/` from `evidence-gates` — init-run first).
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

## Related Skills (this plugin)

- `full-functional-audit` — drive every interaction before calling it ready
- `stack-testing` — close coverage gaps the audit finds
- `evidence-gates` — seal each audit wave's proof
- `plan-hardening` — harden the remediation plan before executing it
