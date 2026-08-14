---
description: End-user test the current work as the end user, producing executed proof
argument-hint: "[scope-or-entry-point]"
---

Run end-user validation directly — the same protocol `implement` runs inline in Stage 5 (platform detection via `references/platform-routing.md`, then the matching `references/*-validation.md` runbook), with the proof standard owned by `end-user-testing`:

$ARGUMENTS

Run the real system (server, CLI, UI) and exercise the actual user flows. Every claim in the final report must cite executed evidence — a command output, response, or artifact. Unexecuted checks are UNVERIFIED, never PASS.

**4. Scoped — everything you can select**

```
/proofpunk-verify src/checkout
```
`verify` takes a single positional scope — there are no flags to combine.
Everything else is the proof standard: fresh run-scoped evidence, the
assertion defined first, verdict citing full paths.
