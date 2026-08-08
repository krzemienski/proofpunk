# End-User Actor Mandate (shared)

The cross-cutting operating principle for every truth-forge skill:
**the AI is the actor, not the spectator.**

## The Rule

**NON-NEGOTIABLE: validation is never faked, skipped, stubbed, or assumed
complete. The AI executes the tools and performs the actions — every time,
for every skill/feature — or the outcome is reported as UNVERIFIED.**

When verifying, validating, auditing, or testing any system, the AI agent
MUST personally drive the real system as an end user — through MCP tools and
automation interfaces — performing the same actions a human user would:

- Navigate, click, tap, type, scroll, submit, swipe
- Fill forms with real inputs and submit them
- Follow links, open modals, dismiss dialogs, go back
- Trigger errors deliberately and observe recovery

The agent acts **always as an end user**: through the UI, the public API, the
CLI — never through internal backdoors, database writes, or code inspection
presented as behavioral proof.

## 2D Verification Is Not Verification

"2D verification" — looking at a flat screenshot, reading code, or confirming
a file exists — is INSPECTION, not VERIFICATION. It has its place (visual QA,
evidence review), but it can never answer "does this work when used?".

| Spectator behavior (insufficient) | Actor behavior (required) |
|-----------------------------------|---------------------------|
| Screenshot the page and say it looks fine | Drive the page with browser MCP tools: click every control, capture before/after evidence |
| Read the button handler and say it works | Click the button as an end user; observe the outcome |
| Check the API route code | Call the live endpoint with a real payload |
| Confirm a screenshot file exists | Personally capture it mid-interaction, then READ it |
| Delegate the clicking to a subagent and trust its summary | Drive the tools yourself; examine raw evidence yourself |

## Tool Path Priority

Use whichever real tool path is available, in this order of preference:

1. **MCP/automation tools** (browser automation, Playwright, Chrome DevTools,
   simulator control, `idb`) — drive the live system directly
2. **CLI invocation** (`xcrun simctl`, `curl`, the product's own binary) —
   drive the live system through its real interfaces
3. **Static inspection only** — acceptable ONLY when no tool path exists,
   and the verdict must be downgraded accordingly (PASS WITH ISSUES /
   verification-pending, never a full PASS)

If a finding "needs interaction to resolve" and a tool path exists, escalate
to driving. Do not fabricate a verdict from a screenshot alone.

## Responsibility Boundaries

- The AI owns the ACTIONS: every click, tap, keystroke, and API call in a
  validation flow is performed by the agent, on purpose, in order.
- The AI owns the EVIDENCE: artifacts are captured by the agent during its
  own session, run-scoped and fresh (see `evidence-contract.md`).
- The AI owns the VERDICT: PASS is claimed only for behavior the agent
  personally drove and personally reviewed.
- Destructive or irreversible end-user actions (delete, pay, send) require
  explicit user approval BEFORE the agent performs them — being the actor
  never means acting without consent.

## Scope

This mandate applies across ALL truth-forge skills:

- `functional-validation` / `full-functional-audit` — every interaction in
  the inventory is driven, not inspected
- `evidence-gates` — gate evidence must come from an AI-driven session
- `visual-inspection` / `ui-experience-audit` — screenshots are captured
  from driven sessions; unresolved "is it wired up?" findings escalate to
  drive mode when tools exist
- `validation-plan` / `plan-hardening` — gate blocks must specify driven
  end-user actions, not passive checks
- `cook` — implementation is verified by driving the finished feature as an
  end user before finalize
