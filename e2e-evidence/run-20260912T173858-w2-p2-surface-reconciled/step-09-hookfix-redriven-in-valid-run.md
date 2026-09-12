# Hook enforcement-notice fix — re-driven inside the VALID run

The original defect drive and fix proof live in
run-20260912T172922-w2-installer-p1p2p4, which commit c169831 later
invalidated (two artifacts below the min-size threshold). Rather than
cite a verdict across an invalid seal, the whole experiment is re-driven
here against the current tree.

## Instrument
Hermetic PATH: every executable in /bin and /usr/bin symlinked into a
temp dir EXCEPT anything matching python*. Absence is structural, so it
behaves identically for root and non-root on any platform.
```
PATH=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.PtnJsVsYP3/bin
cat resolves:     cat
sed resolves:     sed
grep resolves:    grep
python3 resolves: (absent — required for this instrument to be valid)
control, cat works: hello
```
An earlier attempt at this instrument omitted cat and produced rc=127
from the harness itself, which would have been reported as a hook
defect. The self-check above exists because of that.

## The three deny-capable PreToolUse guards
### no-test-files.sh — payload: test-shaped path
  python3 PRESENT — unpiped rc=2 (2 = deny). Deny preserved by the fix: YES
    message: Proofpunk: refusing to create a test artifact (/tmp/x/test_thing_test.py). The write path validates by driving the real 
  python3 ABSENT  — unpiped rc=0 (0 = tool call not broken)
    bytes emitted: 121   (this was 0 before the fix — total silence)
    notice: Proofpunk: no-test-files enforcement OFF (python3-not-found) — test-file writes are NOT being blocked on this machine. 

### evidence-guard.sh — payload: secret in an evidence write
  python3 PRESENT — unpiped rc=2 (2 = deny). Deny preserved by the fix: YES
    message: Proofpunk: refusing to write probable secret material into an evidence directory. Evidence is committed and public — r
  python3 ABSENT  — unpiped rc=0 (0 = tool call not broken)
    bytes emitted: 139   (this was 0 before the fix — total silence)
    notice: Proofpunk: evidence-guard enforcement OFF (python3-not-found) — secret material in evidence writes is NOT being blocked on this machine. 

### capture-guard.sh — payload: overwrite of an existing capture
  python3 PRESENT — unpiped rc=2 (2 = deny). Deny preserved by the fix: YES
    message: Proofpunk: refusing to modify an existing evidence capture — a modified capture is a fabricated claim (see evidence/AG
  python3 ABSENT  — unpiped rc=0 (0 = tool call not broken)
    bytes emitted: 145   (this was 0 before the fix — total silence)
    notice: Proofpunk: capture-guard enforcement OFF (python3-not-found) — overwrites of existing evidence captures are NOT being blocked on this machine. 

## Controls
### stop-guard.sh — already had the correct pattern; must be unchanged
  unpiped rc=0
  output: {"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"Proofpunk: stop-guard enforcement OFF (python3-not-found). A ran-clean stop is only this notice's absence."}} 

### platform-steer.sh — genuinely never denies; must stay silent
  unpiped rc=0  bytes=0
  A non-zero byte count here would mean the fix had leaked a false
  enforcement notice onto a hook that never had enforcement to lose.
