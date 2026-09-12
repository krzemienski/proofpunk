# RETRACTION — the prompt's commit window was right; my correction was wrong

In step-01 of this run I recorded: '17 exclusive at session start, not
11 ... the prompt's 11 is the outlier.' That was wrong, and the error
was mine: I tested d5a50b1..HEAD and d5a50b1..a2fdeb9 but never tested
the window the prompt actually describes.

The prompt separates two things: the v4 window itself, and 'what the
prior session added on top' (ba97ec6, ad62851, 944eaa6, da8cdf6,
6363c5f). Excluding those, measured:
```
$ git rev-list --count d5a50b1..f6141f9
11
$ git rev-list --count d5a50b1..ba97ec6^   # same boundary, stated the other way
11
```

11. Exactly as the prompt said.

It is corroborated by every other figure the prompt gives for that
window, all of which match this range and none of which match mine:
```
$ git diff --shortstat d5a50b1..f6141f9
 120 files changed, 9155 insertions(+), 419 deletions(-)
files changed: 120
SKILL.md files touched: 1
hook files touched: 2
```
Prompt: '120 files, +9,155/-419, but only 1 SKILL.md and 2 hook files
touched.' Measured: 120 files, +9155/-419, 1 SKILL.md, 2 hook files.
Four independent figures, four exact matches. The range is settled.

## The three windows, named so nobody conflates them again
```
  d5a50b1..f6141f9                    11  v4 proper — the prompt's window
  d5a50b1..a2fdeb9                    17  + prior session's 5 commits + its ledger
  d5a50b1..HEAD                       21  + this session's commits
```

## What this invalidates
The P7 ledger at
e2e-evidence/run-20260912T172206-v4-p7-p8-items/step-01-improvement-ledger.md
claims '17 commits, d5a50b1..a2fdeb9 exclusive' and counts 13
improvements across that range. It reached >=10 by scoping to a range
that includes work the prompt explicitly excludes from v4.

P7 therefore stays UNVERIFIED. A correct P7 count must be taken against
d5a50b1..f6141f9 (11 commits) and re-derived, not inherited.

## The general lesson, since it cost a wrong public claim
I measured three ranges and none was the one described. The prompt
characterised its window by four independent facts (commit count, file
count, line delta, SKILL.md/hook counts); checking any ONE of the other
three against my candidate range would have refuted 17 immediately.
A count alone is a weak identifier for a commit range.
