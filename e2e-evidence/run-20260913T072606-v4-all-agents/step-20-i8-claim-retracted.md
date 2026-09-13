# step-20 — RETRACTION: step-19's I8 claim was wrong

## What step-19 claimed
"I8 moves from 'fix correct but unguarded' to individually proven:
reverting it alone now fails a named check."

## That is false
Re-running the exact mutation after the guard hardening:

    plugin's 18 delivery skills -> 17     caught = FALSE

## Why my step-19 test appeared to pass
The two mutations step-19 DID catch were on lines 28 and 31 of the router
SKILL.md. I concluded the file was now guarded. It is not — those were
caught in an isolated probe that fed text straight to the regex, not
through the verifier's own file walk.

## The real reason: SKILL.md files are excluded BY DESIGN

    HISTORICAL_PREFIXES includes '<repo>/plugins/proofpunk/skills/'

Every SKILL.md under that tree is skipped by verify-counts. The regex
matches the mutated line perfectly — ('17', 'skills') — but the file never
reaches the regex.

My earlier probe called `is_historical_path()` with a RELATIVE path, which
returns False; the verifier walks ABSOLUTE paths, which return True. I
tested the function with an input shape the program never uses, and
believed the answer.

## What is actually true

    CLAIM_RE widening       : real and useful — it exposed four stale
                              counts in docs/architecture.md, which IS
                              scanned, and those fixes are guarded.
    router SKILL.md counts  : still UNGUARDED, by an explicit design
                              decision I did not notice before claiming
                              otherwise.

## P8 status, corrected

    individually proven : I1, I5        (2 of 15 — NOT 3)
    unguarded           : I8, I9
    unmeasured          : 11

step-19 is not deleted. It is superseded by this step, because its
CLAIM_RE work and the four stale-count fixes stand — only its I8
conclusion was wrong.

## The pattern, for the fourth time today
A check that appeared to pass because I fed the checker an input the real
program never produces. Same class as the whitespace-wrap false negative
and the UNCOVERED-line false positive: the instrument was wrong, and this
time it was wrong in the direction that flattered my work.

VERDICT: I8 UNPROVEN. P8 stays PARTIAL at 2 of 15.
