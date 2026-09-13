# step-14 — a false negative in my own completeness checker

## What happened
I wrote a checker to confirm step-13 names every release blocker. It reported:

    NO   V12/P8 named

I was about to amend the artifact. Reading it first showed the content was
already there:

    line 20: V12  PARTIAL-RETRACTED   P8 each improvement individually proven
    line 42: 2. **V12 / P8 — PARTIAL, retracted from PASS.** 15 improvements map to only 8
    line 43: distinct evidence artifacts. A shared artifact proves the batch, not the

## Root cause
The checker searched the raw text for the literal phrase
`"8 distinct evidence artifacts"`. In the file that phrase WRAPS:

    ...map to only 8\ndistinct evidence artifacts...

so the substring never matched. The document was complete; the instrument
was broken.

## The fix
Normalize whitespace before matching:

    flat = re.sub(r"\s+", " ", text)

Re-run over all seven required elements:

    YES  V6/P6 + the 1/3 measurement
    YES  V12/P8 + many-to-one reason
    YES  V13/V14 P14/P15 retroactive
    YES  V2/V3 architectural limits
    YES  no-tag state
    YES  gates green but insufficient
    YES  release requirements listed
    all present: True

step-13 was NOT amended. Editing a correct artifact to satisfy a broken
check would have corrupted evidence to make a tool happy.

## Second occurrence of this class today
Earlier, a substring scan flagged four "terminal status" phrases in
completion-summary as overclaims. Reading them showed all four CONTRAST with
terminal status ("not by a recorded terminal status", "crashed without
writing a terminal status"). Also a checker defect, also no edit made.

## The lesson
A failing check has two possible causes, and the instrument is one of them.
Both times the artifact was right. Both times the cheap move — edit the
document until the check goes green — would have made the evidence worse.
Read the source the check is complaining about before believing it.

VERDICT: step-13 verified complete (7/7 elements, whitespace-normalized).
No evidence amended. Two checker false negatives recorded.
