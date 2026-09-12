# I tested against real user state. Process defect, disclosed.

## What happened
Every drive of intent_verdict.py in this task wrote to the real
~/.proofpunk/intent/. By the time it was noticed there were 22 verdict
files there, all mine.

The helper's own harness cases are clean -- tools/test-hooks.sh
redirects HOME to a temp dir at line 8, so the committed tests never
touched user state. The pollution came from my ad-hoc command-line
drives, which inherited the real HOME.

## Why it matters beyond tidiness
1. A stale verdict in that directory is READ BY THE STOP GUARD. A
   leftover MET could authorize a stop for any session whose
   sha256(session_id:cwd) happened to collide -- which is exactly the
   cross-session bypass class this feature was built to close.
2. It made my own testing unreliable. One arm reported may-stop rc=0
   on the first failure; the cause was a reused session id inheriting
   a spent cap from an earlier arm, not a bug in the cap. I nearly
   'fixed' working code because of it.

## Cleanup, auditable
Every test id carried this process's pid (-50378), so removal keyed on
that rather than a blanket wipe:
```
  removed: 22 files, all pid-suffixed test sessions
  kept:    none
  remaining in ~/.proofpunk/intent: 0
```
The directory was empty before this task -- the feature is new, so
nothing of the user's was at risk. That is luck, not design.

## The fix for practice
Drives get an isolated HOME, the way the committed harness already
does. Verified:
```
  captured original intent for iso-demo
  isolated HOME now holds:  1 file
  real HOME still holds:    0 files
```

## Status of the capture cases
The six capture behaviours proven earlier (fresh, repeated-with-
paraphrase, post-UNMET, post-cap, corrupt-refusal, missing-id) were
driven against real HOME. The RESULTS stand -- each used a fresh
random session id, so no arm read another's state -- but the practice
was wrong and is recorded here rather than quietly corrected.
