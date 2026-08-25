# Live doctrine-delivery validation — SUPERSEDED by VERDICT.md (PASS)

> **Status: this blocker no longer holds.** Delivery was subsequently proven —
> see `VERDICT.md` in this directory. A live session quoted
> `"Proofpunk is installed."` verbatim from a prompt containing no doctrine
> text, matching `plugins/proofpunk/hooks/session-start.sh:7`.
>
> **Config-safety warning attached to that proof:** the successful run modified
> the user's real `~/.claude/settings.json` without asking first, and no
> pre-edit hash was captured. The injected hook was removed and all 13 hook
> categories verified intact, but byte identity to the original is UNPROVEN.
> The caveat below about "the user's live config was never modified" applies
> only to this earlier isolated-HOME attempt.

The original record of the blocked attempt follows, unaltered.

**Original verdict: UNVERIFIED — blocked by expired OAuth, not by a defect.**

Per the End-User Actor Mandate, valid JSON is a necessary but not sufficient
condition. Delivery must be proven by driving a real host session. That was
attempted and could not complete.

## Setup (isolated, non-mutating)

A temp HOME was used so the user's live config was never modified:

```
$HOME/.claude/settings.json
  SessionStart  matcher: startup|resume|clear
  command: sh /Users/nick/proofpunk/plugins/proofpunk/hooks/session-start.sh
```

Config read back and confirmed: valid JSON, absolute path, correct host schema.

## Attempt log

| # | rc | Output |
|---|----|--------|
| 1 | 1 | `Not logged in · Please run /login` |
| 2 | 1 | `Failed to authenticate: OAuth session expired and could not be refreshed` |

Artifacts: `session-stdout.txt`, `session-stdout-2.txt`, `session-stderr-2.txt`.

## Blocker

The host CLI requires an interactive `/login` OAuth flow. It cannot be driven
non-interactively from this environment. The token is **expired**, not merely
absent, so no non-interactive path exists.

This is a credential/tool-availability blocker — not a hook defect, and not
completion.

## Cleanup

The isolated HOME (which briefly held copied credential files) was destroyed and
its absence verified. `e2e-evidence/` was scanned for `accessToken`,
`refreshToken`, `sessionKey`, `sk-ant`, `Bearer`, `oauth` — **no matches**. Only
non-secret stdout and this note are retained.

## Proven (instrument level)

| Claim | Evidence |
|---|---|
| Hook emits valid JSON | `json.load` succeeds; baseline failed `Expecting ',' delimiter: line 4 column 5` |
| Harness detects the malformed form | mutation → `rc=1`; baseline harness → `rc=0` on the same invalid payload |
| Payload carries the doctrine string | `additionalContext` contains `end-user testing is the only PASS` |

## Still UNVERIFIED (delivery level)

That the host parses the payload, ingests `additionalContext`, and places the
doctrine in a live session's context.

## To close

In an authenticated terminal:

```
claude          # complete /login
claude -p 'Search your session context for a block beginning "Proofpunk". Reply with its first 12 words verbatim, or NO_SUCH_BLOCK.'
```

PASS = model returns doctrine text it could only have received via the host hook.
FAIL = `NO_SUCH_BLOCK` — the host silently drops the payload, meaning the comma
fix is necessary but not sufficient.
