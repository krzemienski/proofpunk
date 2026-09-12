# The intent gate works, and it breaks 5 existing tests. That is a decision, not a bug.

## What the gate does, driven through the real hook
Payloads carry a REAL evidence path and a real scout record, so the
evidence branch passes and the intent branch is actually reached.
The MET case returning 0 bytes is what proves the test is non-vacuous:
if the evidence branch were still firing, MET would block too.
```
  MET verdict                 -> 0 bytes   ALLOWED
  no verdict recorded         -> block: 'no intent verdict recorded for this session'
  UNMET attempt 1             -> block: 'not met (verdict=UNMET, attempt 1 of 3)'
  UNMET attempt 3 (cap spent) -> 0 bytes   ALLOWED, escalation owed
  missing session_id          -> block  (cannot identify whose verdict applies)
  helper deleted              -> block  (cannot check, so cannot accept)
```

## The 5 failures are one case, repeated
```
  FAIL: stop-guard false-blocked proven claim — got: {"decision": "block", "reason": "Proofpunk: n
  FAIL: stop-guard spoke on fully-proven claim — got: {"decision": "block", "reason": "Proofpunk: 
  FAIL: stop-guard spoke on real evidence path — got: {"decision": "block", "reason": "Proofpunk: 
  FAIL: stop-guard rejected a real curl assertion — got: {"decision": "block", "reason": "Proofpun
  FAIL: stop-guard curl+200 honesty case spoke — got: {"decision": "block", "reason": "Proofpunk: 
```
Every one asserts a fully-proven claim stops SILENTLY. My gate blocks
them because they carry no intent verdict.

## Why this is a contract change, not a defect
Those tests encode the old contract: 'claim + evidence + scout = may
stop'. The new contract adds a fourth conjunct: 'and the original
intent was verified as met'. A test asserting silence on a session that
never verified intent is asserting the behaviour the operator asked me
to remove.

So the tests are not wrong — they are OUT OF DATE, and updating them is
the substance of the change rather than an accommodation to it.

## What I am NOT doing
Not weakening the gate to keep them green. The obvious cheap fix is to
only block when a verdict EXISTS and says UNMET — silent when absent.
That inverts the whole point: the common failure is a session that
never asked whether it did the right thing, and 'absent' would become
consent. Absence of a verdict must block, which is exactly what these
5 tests now catch.

## The right update
Each of the 5 payloads gains a recorded MET verdict for its session, so
it still asserts what it was written to assert (evidence and scout
logic) without asserting the absence of intent verification. Plus a new
case pinning the intent gate itself, mutation-proven the way Case 5b
was earlier this session.

Recorded before touching the harness so the reasoning is auditable
rather than reconstructed from a diff.
