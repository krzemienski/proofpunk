# The Claude Code adapter: wired, driven, and mutation-proven

## Driven through the real hook
Payloads carry a REAL on-disk evidence file and real scout prose, so the
evidence and scout branches pass and the intent branch is what decides.
```
  MET verdict                 -> 0 bytes, ALLOWED   (the control)
  no verdict recorded         -> BLOCK 'no intent verdict recorded'
  UNMET attempt 1             -> BLOCK naming the unmet item
  UNMET attempt 3 (cap spent) -> 0 bytes, ALLOWED, escalation owed
  missing session_id          -> BLOCK (cannot identify whose verdict)
  helper deleted              -> BLOCK (cannot check, cannot accept)
  two sessions, same cwd      -> A=MET allowed, B=no-verdict BLOCKED
```
The MET control is what makes the rest non-vacuous: if the evidence
branch were still firing, MET would block too.

## The harness
  bash tools/test-hooks.sh unpiped rc=0
  88 PASS / 0 FAIL
    PASS: intent gate: MET verdict stops silently
    PASS: intent gate: missing verdict blocks the stop
    PASS: intent gate: UNMET blocks and names the gap
    PASS: intent gate: verdicts do not leak across sessions in one cwd
    PASS: intent gate: missing session_id fails closed

## Why 5 existing cases had to change
They assert a fully-proven claim stops SILENTLY — the old contract
(claim + evidence + scout). The new contract adds a fourth conjunct.
Each now records a MET verdict for its own session id, so it still
asserts the evidence and scout logic without also asserting the absence
of intent verification.

The cheap alternative — block only when a verdict EXISTS and says
UNMET — was rejected. It turns absence into consent, and a session that
never asked whether it did the right thing is the common failure the
gate exists for.

## Fixture non-vacuity
Removing the MET fixture loop from a scratch copy: rc=5, exactly the 5
intent failures. The fixture is doing real work, not masking the gate.

## Gate non-vacuity — mutation
Neutering the gate (block never emitted) in a scratch copy:
    gate neutered in scratch copy (block never emitted)
    rc=4
    intent-gate FAILs: 4
      FAIL: intent gate: missing verdict did not block — got:
      FAIL: intent gate: UNMET did not block with its reason — got:
      FAIL: intent gate: a foreign session inherited a verdict — got:
      FAIL: intent gate: missing session_id did not fail closed — got:

4 of 5 IG cases fail. The MET control correctly still passes — it
expects silence, which a disabled gate also produces. A mutation that
failed all 5 would mean the control was measuring the gate rather than
the evidence branch.

## Key derivation trap, hit twice
The fixture first recorded verdicts against $PWD while the payloads
send cwd=$TMP. Different cwd, different sha256 key, fixture silently
inert. That is the same trap that produced the cross-session bypass
earlier in this run — the key is sha256(session_id + ':' + cwd), and
BOTH halves have to match.
