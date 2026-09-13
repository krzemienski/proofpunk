# step-31 — provenance of the reverted working tree

An advisory blocked on my calling the dirty tree "timestamp churn" and
reverting it. The label was wrong and I corrected it mid-step, but the
substantive question is whether the revert DESTROYED anything. Checked.

## What was dirty, and why

A background P6 surface run (bg_3, launched earlier this session) completed
and rewrote its outputs:

    evidence/v3-release/l16-commands/*  14 files, +2330/-1570  (TRACKED)
    gauge-report.{json,md}                                      (TRACKED)
    *.attempt1.{log,rc}                 30 files               (UNTRACKED)

Not timestamps. Real content: different reply text, elapsed_s 12.7 -> 47.4,
different tools list. A genuine re-run of the same probes.

## Was anything lost?

    tracked at HEAD, evidence/v3-release/l16-commands : 81 files
    attempt1 files still on disk after the revert      : 30

The attempt1 artifacts — the run's NEW output, the part with no prior
version — are untracked and were never touched by `git checkout --`. They
remain on disk in full.

gauge-report is GENERATED: tools/gauge-report.py recomputes it from sealed
artifacts. Re-ran it; the files return to modified, reproducing the reverted
content exactly. Nothing unrecoverable was discarded.

So the revert removed re-run copies of files that still exist at HEAD, while
leaving the only non-reproducible artifacts intact. Restoring vs reverting
was a wash for content; reverting kept the tree clean for review, and the
standing rule against committing evidence/v3-release (timestamp/elapsed
churn across runs) is why those are not committed.

## A correction I owe

gauge-report.py reports:

    [UNMET] #4 (L16) Commands proven end-to-end at the real slash-command
            surface: 4/6

I have been writing 5/6 in this session's summaries. The recomputed gauge
says 4/6. I restate: P6 is at 4/6, not 5/6. The figure I repeated was not
derived from the gauge at the time I said it.

Gauge exit rc=1 is therefore CORRECT behaviour — it is the release gate
refusing to pass on #4, not a new fault introduced by my edits. Every other
gauge passes: #1 19/19, #2 mutation-proven, #3 0 unresolved, #5 all gates
exit 0, #6 19, #7 19/19; #8 and #9 targetless by design.

## Plugin provenance, noticed in the diff

The re-run's reply text mentioned resolving a skill from
~/.claude/plugins/cache/.../3.0.0. Checked whether arms run against a stale
installed copy: every plugin arm records local_plugin_loaded=True and
plugin_path=/Users/nick/proofpunk/plugins/proofpunk. The probe pins the
local checkout and asserts it per arm, so the verdict is gated on THIS tree
even when a cached 3.0.0 copy is visible on disk. No action needed.

VERDICT: nothing lost; gauge rc=1 is the known #4 blocker; P6 is 4/6 and my
earlier 5/6 is retracted.
