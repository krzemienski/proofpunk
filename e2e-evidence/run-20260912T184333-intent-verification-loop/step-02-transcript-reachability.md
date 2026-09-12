# The design's load-bearing fact: original intent is mechanically reachable

The whole feature rests on one question — can a stop surface see the
ORIGINAL request, not just the recent tail? Measured against real
Claude Code transcripts rather than assumed.

## Real transcripts under ~/.claude/projects/*proofpunk*/
  transcripts inspected: 5
    aba3dd20-3731-438b-9  lines=  39  user_records=3
      first user prompt: Invoke the skill named exactly 'proofpunk' using the Skill tool. After it loads, quote verbatim
    2bce84e8-dccd-4aad-b  lines= 102  user_records=10
      first user prompt: Invoke the skill named exactly 'proofpunk:implement' using the Skill tool, then state in one li
    e085046c-311b-4ebb-a  lines=  39  user_records=3
      first user prompt: Invoke the skill named exactly 'proofpunk' using the Skill tool. After it loads, quote verbatim
    bac121ff-bdee-4bb4-9  lines=  39  user_records=3
      first user prompt: Invoke the skill named exactly 'proofpunk' using the Skill tool. After it loads, quote verbatim
    e7b33e68-b739-43c2-9  lines=  92  user_records=9
      first user prompt: Invoke the skill named exactly 'proofpunk:implement' using the Skill tool, then state in one li

## What this establishes
error: command not found: user
1. Every transcript contains typed  records, and the FIRST one is
   the session's original request — verbatim, not summarized.
error: command not found: transcript_path
2. A Claude Code Stop hook receives , which points at
   this complete JSONL. The whole session is readable.
3. stop-guard.sh today reads only the last 40 lines
   (plugins/proofpunk/hooks/stop-guard.sh:111-112). That bound is
   SELF-IMPOSED for latency, not a platform limit.

So criterion C3 — 'the pass reads the whole session, not a tail window'
— is achievable on Claude Code without any new platform capability.

## The caveat that shapes the design
Reading the transcript is mechanical. JUDGING whether the original
intent was met is not: it is a natural-language comparison between a
request and everything that followed. A shell hook cannot do that, and
a regex pretending to would be a guard faking comprehension.

Hence the split recorded in step-01: the hook checks that a verdict
EXISTS and what it SAYS; the model produces the verdict. Both halves
are then mechanically checkable.
