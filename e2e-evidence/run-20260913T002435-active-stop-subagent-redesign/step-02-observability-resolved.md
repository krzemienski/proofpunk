# Step 2 - Crux resolved: subagent state IS observable, the window is the bug

## Question
At the moment a stop hook fires, can it observe that background
subagents are still running? If not, the requested design is
unimplementable as specified.

## Answer: OBSERVABILITY: PROVEN-AVAILABLE via transcript tool_use/tool_result pairing

### The mechanism (measured on a real transcript)
Each subagent spawn is a tool_use block whose name is Agent (in older
transcripts, Task). Its completion is a tool_result block whose
tool_use_id equals that spawn's id.

  spawn  id in tool_use(name=Agent)
  finish tool_result.tool_use_id == that id

Therefore:
  spawn WITHOUT matching result = subagent STILL RUNNING
  spawn WITH    matching result = subagent FINISHED

Measured on the newest transcript (3547 records):
  Agent/Task spawns:            13
  spawns with a result:         13   -> finished
  spawns with no result:         0   -> none outstanding

The pairing is total: every spawn resolved. The discriminator works.

### A second, cheaper marker also exists
isSidechain appears in 1470 of 1500 transcripts scanned. Subagent-side
records carry it, so a SubagentStop transcript is distinguishable from
a main-thread one by content, not only by hook_event_name.

### Why the shipped guard still cannot see any of it
stop-guard.sh:134 reads only the LAST 40 LINES.

  spawn distance from end-of-file: min 546, max 3393 lines
  spawns visible in a 40-line window: 0 of 13

The guard misses 100% of spawns in this sample. The information is
present in the file and discarded by the read window.

## What this changes about the design
The redesign does NOT need a new runtime API, and does NOT need an
out-of-band tracker as its primary mechanism. It needs:
  1. a full-file (or spawn-aware) scan for unresolved spawn ids;
  2. Stop vs SubagentStop to take DIFFERENT code paths
     (currently: 1 reference to hook_event_name, 0 conditionals);
  3. a bound on cost, because hooks.json gives Stop timeout 10s and
     the scanned file was 3547 records.

## Correction to my own earlier search
My first probe searched for tool name 'Task' and found 0 hits in 400
transcripts, which would have wrongly suggested spawns are not
recorded. The tool is named 'Agent' in current transcripts. Widening
the token set is what produced the real answer -- the earlier null was
my wrong needle, not an absent signal.
