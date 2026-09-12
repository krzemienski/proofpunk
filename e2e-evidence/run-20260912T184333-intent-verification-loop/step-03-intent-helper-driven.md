# intent_verdict.py — driven, including every boundary

The mechanical half of the intent-verification contract. The model
judges intent; this answers the one question a stop guard can check
without pretending to comprehend anything: may this session stop?

## 1. Intent recovery from a REAL transcript (not a fixture)
```
$ intent_verdict.py recover ~/.claude/projects/.../aba3dd20-3731-438b-96b9-27297f16b796.jsonl
Invoke the skill named exactly 'proofpunk' using the Skill tool. After it loads, quote verbatim the first row of its 'Skill calls' table.
unpiped rc=0
```
Verbatim, not summarized. Grading against a paraphrase grades the
paraphrase.

## 2. The bound — operator-approved cap of 3
```
  attempt=1  may-stop unpiped rc=2  -> BLOCKS, restart implement
  attempt=2  may-stop unpiped rc=2  -> BLOCKS, restart implement
  attempt=3  may-stop unpiped rc=0  -> ALLOWS, owes escalation report
  attempt=4  may-stop unpiped rc=0  -> ALLOWS, owes escalation report
```
Attempts 1-2 refuse the stop. At 3 the stop is ALLOWED — refusing
there would BE the unbounded loop the cap exists to prevent — and the
message demands an escalation report naming the unmet intent.

## 3. MET allows immediately
  MET -> unpiped rc=0 (expect 0)

## 4. Hostile inputs — each must refuse, never pass
```
  no verdict recorded    rc=2  (blocks: absence is not consent)
  invalid verdict string rc=2
  missing transcript     rc=2
  CORRUPT verdict file   rc=2  (blocks — a corrupt verdict is not a passing verdict)
```

The corrupt-file case is the important one. Every other guard in this
plugin fails OPEN when its interpreter is missing, because breaking a
user's tool call is worse than a missed check. This fails CLOSED when
its state is unreadable, because an unreadable verdict is indistinguishable
from an absent one, and absence must never read as consent.

## 5. Atomicity
Writes go through mkstemp + os.replace (intent_verdict.py:113-127), the
same pattern as bash-write-snapshot.sh:147-150. A half-written verdict
never appears on disk, so a crash mid-record cannot manufacture a
passing state.
