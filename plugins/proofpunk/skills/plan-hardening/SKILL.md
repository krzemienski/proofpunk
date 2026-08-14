---
name: plan-hardening
description: >
  Second-pass plan strengthening: red-teams a draft plan through multiple
  adversarial lenses, scores confidence gaps, researches weak sections
  injects or strengthens proof obligations, and surgically remediates
  findings while preserving the original intent. Also converts arbitrary
  prompts or plans into proof-carrying versions using the standard proof
  block. Use when a plan exists but may be shallow, overconfident, missing
  failure modes, or lacking proof obligations — 'harden this plan', 'deepen
  this plan', 'red-team my plan', 'stress-test this design', 'add proof
  obligations to this prompt' — or before executing any high-stakes
  multi-phase plan. Not for authoring a plan from scratch (use
  validation-plan) or executing one (use implement or implement).
---

# Plan Hardening

A plan that survives contact with reality. Takes a draft plan (or prompt)
and returns a stronger, proof-carrying version with the original intent intact.

**READ `../../references/evidence-contract.md` — injected proofs follow its pattern.**

## Stage 1 — Load and classify

Read the plan/prompt fully. Classify:

- **Type**: implementation plan, migration, refactor, prompt, research plan
- **Maturity**: sketch (no structure), draft (phases, no proofs), proven
- **Blast radius**: which contracts, data, and users it touches
- **Original intent**: write it down in one paragraph — every later edit is
  checked against this. Hardening strengthens; it never re-scopes silently.

## Stage 2 — Structural parse

Extract: objectives, phases/tasks, dependencies, contracts, existing
validation, open questions. Anything implied but unstated goes on the gap
list — implicit assumptions are where plans fail.

## Stage 3 — Confidence-gap scoring

Score each section:

```
gap_score = trigger_count + risk_bonus + critical_section_bonus
```

- **trigger_count**: hedging language ("should work", "probably", "assume"
  "etc."), undefined terms, missing owners, unverifiable claims
- **risk_bonus**: touches data migrations, auth, payments, public APIs
  irreversible operations
- **critical_section_bonus**: section is on the plan's critical path

Rank sections by gap_score. High scorers get research and rewriting; low
scorers get proof checks only.

## Stage 4 — Red-team dispatch (four lenses)

Attack the plan from each lens and record findings in a gap register:

| Lens | Questions |
|------|-----------|
| Adversary | How does this break under hostile input, race conditions, partial failure? |
| Operator | What breaks at 3am? Rollback path? Observability? Data recovery? |
| Integrator | Which contracts does this silently change? Who calls the touched code? |
| Skeptic | Which claims have no evidence? What is assumed about the environment, data shape, scale? |

Each finding: `id | section | lens | severity | description | suggested fix`.
Severity per `../../references/severity-model.md` — CRITICAL findings block
finalization.

## Stage 5 — Surgical remediation

For each finding, patch the smallest unit that resolves it:

- Research weak sections against real sources (docs, code, live system)
- Replace hedged claims with verified ones or explicit open questions
- Add missing failure handling, rollback, and observability steps
- Call out contract changes explicitly with migration notes

Preserve the plan's structure and voice where sound — this is surgery, not a
rewrite from scratch.

## Stage 6 — Proof-obligation injection

Every phase without a proof obligation gets one; weak ones get strengthened:

```xml
<proof_obligation id="PO-{N}" blocking="true">
Actor: the AI agent drives these actions as an end user via MCP/automation
tools — no passive checks, no delegated clicking
Prerequisites: [dependencies started + healthy]
Execute: [real system interaction, driven end-user actions]
Capture: [save output to evidence/]
Pass criteria: [specific, observable, measurable]
Review: [READ evidence and describe what is seen]
Verdict: PASS → next task | FAIL → fix real system → re-run | UNVERIFIED → not executed
Mock guard: IF tempted to mock → STOP → fix real system
</proof_obligation>
```

Proof semantics follow `../../references/end-user-actor.md`: a proof whose
actions were not actually executed by the AI resolves to UNVERIFIED, never
to PASS.

Make proofs cumulative where the plan is phased (phase N re-proves 1..N-1).

## Stage 7 — Consensus validation and final output

Re-read the hardened plan end to end:

- [ ] Original intent preserved (check against Stage 1 paragraph)
- [ ] Every CRITICAL/HIGH finding resolved or explicitly accepted with reason
- [ ] Every phase carries a blocking proof obligation with observable criteria
- [ ] Every behavioral criterion is paired with an end-user action the AI
      will actually execute via MCP/automation tools — no proof that can be
      "verified" by inspection, assumption, or delegation alone
- [ ] No new hedging language introduced
- [ ] Gap register included as an appendix with disposition per finding

Output the hardened plan plus the gap register. Do NOT finalize while
critical findings remain open.

## Prompt Transformation Mode

For an arbitrary prompt (not a plan), run the same pipeline but rewrite the
prompt itself: add explicit context, observable success criteria, the proof
block above, and anti-mock instructions — converting "do X" into "do X and
prove it with fresh evidence".

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| Hardening that silently changes scope | Check every edit against the Stage 1 intent paragraph |
| Red-team findings listed but not remediated | Every finding gets a disposition: fixed, accepted-with-reason, or blocking |
| Gates with subjective criteria ("works well") | Observable, measurable criteria only |
| Full rewrite when the draft is 80% sound | Surgical edits; preserve what works |
| Finalizing with open CRITICAL findings | Block until cleared or explicitly accepted by the user |
| Faking or skipping validation | Owned by `end-user-testing` — apply its Actor Mandate verbatim; unexecuted = UNVERIFIED |

## Example

**Input:** User: 'Harden this migration plan before Friday.'

**Output:** The draft is attacked through 4 lenses, 6 confidence gaps scored, 2 weak sections researched, proof obligations injected into phases 2-4 — original intent preserved, plan now has zero unverifiable steps.

## Skill calls

| Calls | When | What it hands over |
|-------|------|--------------------|
| `red-team-eval` | Stage 4 red-team dispatch | the four adversarial lenses |
| `validation-plan` | Stage 6 proof-obligation injection | the PO format being injected |
| `end-user-testing` | injected proofs | the proof standard obligations must satisfy |
