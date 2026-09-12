# P7 recomputed against the prompt's own window

## Scope, fixed before counting
Endpoints: d5a50b1..f6141f9 — the 11-commit v4 window the task defines.
d5a50b1 itself is the 2.2.0->3.0.0 bump and is EXCLUDED (it is the v3
boundary). ba97ec6 onward is the prior session's work, listed separately
by the task, and is NOT counted toward v4's P7. This session's four
commits are also excluded for the same reason.

$ git log --oneline --reverse d5a50b1..f6141f9
```
224bb93 release(v3): record operator deferral tokens for the 8 unwired gauges
43f5a98 release(v3): split aggregate deferral into 8 individually-named tokens
90bf91d gauge4: effect-proven level d for install/verify + fail-closed auth hygiene
8bf56ea docs(v3): Phase-4 dispositions — honest applied-vs-open mapping
c752879 v4 W1-W6: ACQUIRE stage, digest contract, steering guard, doc sweep
46ebae6 v4 W7: render-counts.py owns every derived count
42ff1bf docs: reconcile every count claim against disk at HEAD
059f134 chore(gauge): regenerate report at current HEAD
8f69db0 fix(site): derive counts in the generator, close the HTML drift class
639168a docs(architecture): label the tools figure as a directory listing
f6141f9 chore(gauge): refresh snapshot to current HEAD
```
count: 11

## Improvements in that window, one row per commit

| # | commit | improvement | file evidence | observable outcome |
|---|---|---|---|---|
| I1 | `224bb93` | release(v3): record operator deferral tokens for the 8 unwired gauges | docs/v3-gauge-deferrals.md | 1 file changed, 46 insertions(+) |
| I2 | `43f5a98` | release(v3): split aggregate deferral into 8 individually-named tokens | docs/v3-gauge-deferrals.md | 1 file changed, 6 insertions(+), 1 deletion(-) |
| I3 | `90bf91d` | gauge4: effect-proven level d for install/verify + fail-closed auth hygiene | e2e-evidence/run-20260909T190000-v3b-gauge4/out/cmd_slash_forge_prompt.control.attempt1.log | 68 files changed, 7668 insertions(+), 151 deletions(-) |
| I4 | `8bf56ea` | docs(v3): Phase-4 dispositions â honest applied-vs-open mapping | docs/v3-phase4-dispositions.md | 1 file changed, 124 insertions(+) |
| I5 | `c752879` | v4 W1-W6: ACQUIRE stage, digest contract, steering guard, doc sweep | docs/hook-enforcement-map.md | 11 files changed, 513 insertions(+), 32 deletions(-) |
| I6 | `46ebae6` | v4 W7: render-counts.py owns every derived count | README.md | 3 files changed, 343 insertions(+), 34 deletions(-) |
| I7 | `42ff1bf` | docs: reconcile every count claim against disk at HEAD | docs/discovery-register.md | 7 files changed, 178 insertions(+), 25 deletions(-) |
| I8 | `059f134` | chore(gauge): regenerate report at current HEAD | gauge-report.json | 2 files changed, 5 insertions(+), 5 deletions(-) |
| I9 | `8f69db0` | fix(site): derive counts in the generator, close the HTML drift class | docs/commands.html | 29 files changed, 269 insertions(+), 173 deletions(-) |
| I10 | `639168a` | docs(architecture): label the tools figure as a directory listing | docs/doc-architecture.html | 2 files changed, 9 insertions(+), 4 deletions(-) |
| I11 | `f6141f9` | chore(gauge): refresh snapshot to current HEAD | gauge-report.json | 2 files changed, 3 insertions(+), 3 deletions(-) |

## P8 status for each — the honest part

P8 requires each improvement to be individually proven by driving the
real behaviour it changed. For this window that evidence does not
exist: the commits predate this session, and I did not re-drive them.
Gate rc=0 is not P8 evidence — a gate proves counts and exit codes, and
the central finding of this session is that seven green gates coexisted
with a plugin broken on every python3-less machine.

So:
  P7 (>=10 improvements ranked then implemented): the window contains
     11 commits. Whether all 11 are 'improvements' rather than
     mechanical follow-ups is a judgement the operator should make, not
     one I should make in my own favour — two of the 11 are gauge
     snapshot refreshes (059f134, f6141f9) and one is a figure-caption
     fix (639168a). Counting generously gives 11; counting only
     substantive changes gives 8.
  Verdict: UNVERIFIED. Not FAIL — the work plausibly clears the bar.
  Not PASS — I cannot show >=10 SUBSTANTIVE items without grading my
  own predecessor's commits generously, and the threshold is close
  enough to the boundary that the grading choice decides the outcome.

  P8: UNVERIFIED for the same window, no per-item drive exists.

## What would settle it
Re-drive each of the 11 against the behaviour it changed, the way
adcee4b/c169831/e180035/6cc01f9 were driven in this session. That is
11 separate end-user validations and was not attempted here.
