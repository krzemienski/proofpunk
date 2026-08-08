# Evidence Contract (shared)

Canonical evidence standard for every truth-forge skill. Consolidated from
`fresh-evidence`, `gate-validation-discipline`, `no-mocking-validation-gates`,
`verification-before-completion`, and `transform-validation-prompt`.

**Companion mandate: `end-user-actor.md` — the AI personally drives the real
system as an end user via MCP/automation tools. Evidence that does not come
from an AI-driven end-user session (when a tool path exists) is insufficient
for a full PASS.**

## The Iron Rule

```
IF the real system doesn't work, FIX THE REAL SYSTEM.
NEVER create mocks, stubs, test doubles, fake endpoints, or test-mode bypasses.
ALWAYS validate through the same interfaces real users experience.
```

## The Non-Negotiable Validation Rule

```
Validation must NEVER be faked, skipped, stubbed, or assumed complete.
For every skill/feature the plugin touches, the AI must actually execute
the relevant MCP/automation tool(s) and perform the actions as a real end
user would — not delegated, not skipped, not marked complete without
actual execution. A validation step that was not executed is a validation
step that DID NOT HAPPEN: report it as UNVERIFIED, never as done.
```

This is the enforcement arm of the Iron Rule: "real validation only" means
the AI directly operates the tools, acting as the end user across all
affected surfaces. Unit tests, code reading, file-existence checks, and
delegated summaries are supporting signals — they are never a substitute
for the AI having personally performed the end-user action.

When an integration fails, the only valid sequence is: Diagnose -> Fix -> Verify.
Prohibited: mock fallbacks, fake endpoints, conditional test-mode responses,
simulated data presented as real output, fabricated expected values.

## The Verification Loop

```
1. Worker completes work
2. Worker provides evidence LOCATION
3. You personally examine evidence CONTENT
4. You match evidence to pre-defined PASS criteria
5. You cite specific proof (file paths, line numbers, exact output)
6. ONLY THEN mark complete
```

"Agent reported 10/10 pass" is not evidence. Read the actual outputs. View the
screenshot and describe what you SEE. Quote the actual success line.

## Pre-Defined PASS Criteria

Define specific, observable, measurable PASS criteria BEFORE capturing any
evidence. Defining criteria after viewing evidence is confirmation bias.

Good: "Dashboard shows 4 chart cards with MRR, ARR, Churn, NRR values populated"
Bad: "Dashboard looks right"

## Fresh-Evidence Rules

1. **Run-scoped directory** — all artifacts for one run live under
   `e2e-evidence/run-<ISO-compact>-<slug>/`, never in `e2e-evidence/` root.
2. **Sequential naming** — `step-NN-<action>-<result>.<ext>`, zero-padded,
   globally sequential within the run.
3. **Non-empty** — every artifact > min_size_bytes (default 1024). Zero-byte
   or tiny files are INVALID; discard and re-capture.
4. **Fresh** — artifact mtime must be >= run start. Reusing a prior run's
   artifact in a verdict is FORBIDDEN.
5. **Cited by full path** — verdicts cite exact files, not "see evidence dir".
6. **Describes what is SEEN** — captions describe content ("Dashboard rendered
   with 4 chart cards (MRR $12,450 ...)"), not existence ("screenshot taken").
   For API responses quote actual body AND headers.
7. **Inventory** — every run dir contains `evidence-inventory.txt` listing
   every file with byte count.
8. **Gitignored** — `e2e-evidence/` is gitignored by default; at most commit
   `verdict.md` / `report.md`, never binary artifacts with secrets.

Helper: `../skills/evidence-gates/scripts/fresh_evidence.py` implements
init-run / next-step / seal / validate with these rules enforced.

## Validation Gate Pattern

Embed gates in plans and prompts with this structure:

```xml
<validation_gate id="VG-{N}" blocking="true">
Actor: AI drives these actions as an end user via MCP/automation tools
Prerequisites: [dependencies started + healthy]
Execute: [real system interaction — driven, not observed]
Capture: [save output to evidence/]
Pass criteria: [specific, observable, measurable — defined in advance]
Review: [READ the evidence and describe what is seen]
Verdict: PASS → next task | FAIL → fix real system → re-run
Mock guard: IF tempted to mock → STOP → fix real system
</validation_gate>
```

## Stale Cache Warning

Build caches (`.next`, `.turbo`, `DerivedData`, `node_modules/.cache`, `dist`,
`__pycache__`) can mask regressions — a cached bundle can serve correct UI
while source on disk is broken. Clear relevant caches BEFORE final validation
passes, and never clear anything outside the project root.

## Secret Hygiene

Redact API tokens, auth headers, and session cookies from captured evidence.
Capture `Authorization: [REDACTED]`. Never commit evidence containing secrets.

## Refusal Rules

- Refuse to mark PASS without cited evidence paths.
- Refuse to cite an artifact older than the current run.
- Refuse to emit a verdict with an empty evidence inventory.
- Refuse to validate when the runtime target is unreachable — surface the
  blockage instead of simulating success.
- Refuse "see file" descriptions — demand a description of what is SEEN.
- Refuse to mark validation complete without the AI having actually invoked
  the MCP/automation tools and acted as the end user.
- Refuse to skip or fake QA/verification steps under any circumstance —
  time pressure, "it obviously works", and "tests pass" are not exceptions.

## Completion Challenge

Before any completion claim ask: "If someone challenged this claim, what
specific evidence would I show them?" If you cannot answer with citations,
the work is NOT complete.
