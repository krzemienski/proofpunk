# The two W4 doc fixes: what proves them, and what does not

I described both as 'proven by driving'. That is false and worth
correcting precisely, because the distinction is this plugin's entire
subject.

## What these fixes are
Both change PROSE in markdown that an agent reads. Neither changes an
executable path. There is no runtime to drive: the 'end user' of a
skill file is a model reading it, and I cannot instrument that here.
So the honest proof standard is textual verification against the tree,
not end-user driving.

## Fix 1 — ci-gates.md wiring note
Claim now made by the file: production-readiness loads it, citing
skills/production-readiness/SKILL.md:41-43.

Verified — the cited lines say what the reference claims:
```
     When the audit finds no pre-commit or CI gates configured, load
     `../../references/ci-gates.md` and propose its P0→P1→P2 rollout rather
     than inventing gate criteria ad hoc.
```
Note the wording in the SKILL is an INSTRUCTION to load, which is what
a skill can express. Whether a model obeys it in a live session is not
something this session measured, and the reference no longer asserts
more than the instruction's existence.

The defect it replaced was falsifiable and is now false:
```
previous text (git show HEAD~1) —
  **Wiring gap (as of this note):** no executing skill loads this file mid-workflow —
  it is currently cited only descriptively in `skills/proofpunk/SKILL.md`'s reference
  table. The natural loader is `production-readiness`'s codebase-audit lens (its own
```
That claimed no executing skill loads the file. The instruction at
:41-43 predates the claim, so the note was false when written.

## Fix 2 — router count wording
NOT a defect in routing. Measured:
  delivery skills (excluding router): 17
  named by the router               : 17
  unrouted                          : none
  The convention is already documented — architecture.md states
  '18 (17 delivery skills + 1 router)', and verify-counts.py accepts
  both 18 and 17 for this reason. So '17' was never wrong; it was
  ambiguous beside a repo whose every other count is 18. This is a
  wording clarification, not a count correction, and P5's 17/17 was
  measuring the right population all along.

## Gates after both edits
  python3 tools/verify-counts.py         rc=0
  python3 tools/verify-citations.py      rc=0
  python3 tools/verify-orchestration.py  rc=0

## Verdict on these two fixes
  ci-gates.md   — the false claim is verifiably gone; the replacement
                  claim is verified against the cited lines. TEXTUALLY
                  VERIFIED, not end-user driven.
  router count  — wording only; routing coverage unchanged at 17/17.
                  TEXTUALLY VERIFIED.

Neither belongs in the 'proven by driving' column with the hook and
installer fixes. P11 stays UNVERIFIED regardless: two prose fixes in
two files is not a correctness review of eighteen skills.
