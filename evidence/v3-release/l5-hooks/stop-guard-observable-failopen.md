# L5 — stop-guard fail-open made observable; Case 4 contract updated

Measured: 2026-09-04 (UTC) | Repo HEAD: `40abc0b` (working tree dirty)

## What happened

`bash tools/test-hooks.sh` exited **0** early in this session and **1** later.
LaneA flagged it and proved it pre-existing rather than caused by their work,
using an isolated worktree at HEAD (`test-hooks.sh` exits 0 there). Correct
attribution: an **uncommitted WIP diff** to
`plugins/proofpunk/hooks/stop-guard.sh` (+51/-9) was present in the working
tree and broke exactly one case.

Failing case, verbatim:

```
FAIL: stop-guard spoke on missing transcript (must be silent) — got:
{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":
"Proofpunk: stop-guard enforcement OFF (transcript-missing-or-unreadable).
A ran-clean stop is only this notice's absence."}}
```

## Diagnosis — the WIP is right, the test encoded the old contract

This is a **design conflict, not a bug**. The WIP's own header states the
intent:

> Fail-open is observable. Missing python3, missing/unreadable transcript, or
> a heuristic crash used to exit 0 with no output — identical to "ran clean".

That is this repo's **defect Class 1**: a guard whose "cannot fail" state is
indistinguishable from its "passed" state. The same shape as
`dry-run-install.sh` never invoking the installer (`5e5150b`). The WIP closes
it by emitting an `enforcement OFF (<reason>)` notice and still exiting 0 —
`Stop` must never be blocked on a transcript the guard could not read.

`tools/test-hooks.sh:58` asserted the **old** contract (silence on a missing
transcript). Under the new design, silence is reserved for "the heuristic
actually ran and found nothing to enforce" — a strictly stronger guarantee.
The test, not the hook, was stale.

## The change

Case 4 now asserts three things instead of one:

1. it must **never** emit `"decision": "block"` (unchanged safety property),
2. it **must** announce `enforcement OFF (transcript-missing-or-unreadable)`,
3. silence is now a **failure** for this input, not a pass.

## Mutation proof

Ran against the real harness, three arms, exit codes captured separately from
stdout:

| Arm | Action | rc | Result |
|---|---|---:|---|
| 1 baseline | unmodified working tree | 0 | `HOOK TEST FAILS: 0` |
| 2 mutated | reverted `emit_off "transcript-missing-or-unreadable"` back to a bare `exit 0` | 1 | `HOOK TEST FAILS: 1` — the new assertion fires by name |
| 3 restored | original bytes rewritten | 0 | `HOOK TEST FAILS: 0` |

- Restore is **byte-identical**: sha256 before == sha256 after (verified in the
  same evaluation as the mutation, not recalled).
- The harness **detects** the mutation, so the assertion is not vacuous.

## Scope note

`stop-guard.sh` itself was **not** modified by this work — it was left exactly
as its author's WIP had it (proven by the byte-identical restore above). The
only edit is to `tools/test-hooks.sh` Case 4, bringing the harness in line with
the hook's improved contract.

## Proof level

**Script-level.** The real harness was executed across three arms with real
exit codes. Not end-user proven: no live Claude Code session was driven to
observe the `additionalContext` notice actually surfacing at a real `Stop`
event. That remains covered only by `sdk_probe.py`, which
`codebase-analysis.md:74` records as **not wired into CI**.

## Open

- Whether a real host renders `additionalContext` on `Stop` in a way the
  operator actually sees is **UNVERIFIED here** — it requires a live session,
  not a harness. Carried to L14 (platform parity).
