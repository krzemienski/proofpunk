# Correction: "fail CLOSED throughout" overstates what f37931a does

The commit message for f37931a says the intent gate is "Fail CLOSED
throughout". That is wrong at the boundary, and the distinction is the
kind that matters when someone later reasons about what the hook
guarantees.

History is not being rewritten for wording. The correction lives here,
in the same sealed run the commit cites.

## Two layers, two deliberately opposite policies

### Layer 1 — the outer wrapper: fails OPEN, and announces
```
  malformed stdin:
    ALLOWS, announces: Proofpunk: stop-guard enforcement OFF (stdin-json-unreadable). A r
  empty stdin:
    ALLOWS, announces: Proofpunk: stop-guard enforcement OFF (stdin-json-unreadable). A r
```
It cannot parse the payload, so it cannot know whether a completion was
even claimed. Blocking every unparseable stop would trap sessions on a
hook bug rather than on a real finding. It allows, and says enforcement
is OFF so the silence is not mistaken for a clean run.

### Layer 2 — the intent gate: fails CLOSED
```
  no-session-id: BLOCKS — Proofpunk: a completion was claimed but this session has no se
  no-verdict: BLOCKS — Proofpunk: no intent verdict recorded for this session. Before
```
Here the payload IS readable and a claim WAS made. The gate is the
check, so an unverifiable check is a failed check.

## The accurate sentence
  "The intent gate fails CLOSED when the payload is readable; the
   wrapper fails OPEN on unreadable stdin and announces enforcement-off."

## Why the sloppy version was dangerous
"Fail closed throughout" invites a reader to assume an unparseable
payload also blocks. It does not — and that is correct behaviour, but
only if it is written down. A future change that 'fixed' the wrapper to
match the overstated claim would trap every session whose hook input
was momentarily malformed.
