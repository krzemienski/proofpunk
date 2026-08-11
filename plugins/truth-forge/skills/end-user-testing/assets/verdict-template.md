# Verdict: [JOURNEY_NAME]

**Status:** [PASS / FAIL / BLOCKED / UNVERIFIED]
**Timestamp:** [ISO8601]
**Platform:** [type]
**Driven by:** AI as end user via [MCP/automation tools actually used]
**Actions executed:** [what the AI actually did — navigated, clicked X,
submitted Y, called Z — or "none (no tool path available)"]

## PASS Criteria (defined before execution)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | [specific criterion] | PASS / FAIL / UNVERIFIED | `[evidence path]` |
| 2 | [specific criterion] | PASS / FAIL / UNVERIFIED | `[evidence path]` |

## Evidence Review

### [evidence-file-1.ext]
- **Read:** Yes
- **Content:** [description of what the evidence SHOWS]
- **Assessment:** [matches/contradicts PASS criteria]

## Failure Details (if FAIL)

**Expected:** [from PASS criteria]
**Observed:** [from evidence]
**Root cause:** [diagnosis]
**Affected file:** [path:line]

## Verdict

```
OVERALL: [PASS / FAIL / BLOCKED / UNVERIFIED]
Reason: [evidence-backed explanation]
```

UNVERIFIED is the honest state for any criterion whose validation was not
actually executed by the AI as the end user. Never upgrade UNVERIFIED to
PASS by assumption.
