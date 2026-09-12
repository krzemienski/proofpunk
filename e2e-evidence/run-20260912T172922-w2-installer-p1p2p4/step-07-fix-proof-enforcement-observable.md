# FIX PROOF — deny-capable PreToolUse guards now announce enforcement loss

Instrument: hermetic PATH=/tmp/pp-nopy2-jYKizP/bin (all /bin + /usr/bin symlinked EXCEPT python*).
Self-check: cat/sed/grep resolve; python3 absent; 'printf hello | cat' -> hello.

Each hook driven with a MUST-DENY payload, with and without python3.
AFTER-fix requirement: rc stays 0 (never break the tool call) but output is non-empty.

## no-test-files.sh
  WITH python3: rc=2 (deny preserved: YES)
    deny message: Proofpunk: refusing to create a test artifact (/tmp/x/test_thing_test.py). The write path validates by driving
  NO python3:   rc=0 (tool call not broken: YES)
    bytes emitted: 121 (was 0 before the fix)
    notice: Proofpunk: no-test-files enforcement OFF (python3-not-found) — test-file writes are NOT being blocked on this machine. 

## evidence-guard.sh
  WITH python3: rc=2 (deny preserved: YES)
    deny message: Proofpunk: refusing to write probable secret material into an evidence directory. Evidence is committed and pu
  NO python3:   rc=0 (tool call not broken: YES)
    bytes emitted: 139 (was 0 before the fix)
    notice: Proofpunk: evidence-guard enforcement OFF (python3-not-found) — secret material in evidence writes is NOT being blocked on this machine. 

## capture-guard.sh
  WITH python3: rc=2 (deny preserved: YES)
    deny message: Proofpunk: refusing to modify an existing evidence capture — a modified capture is a fabricated claim (see e
  NO python3:   rc=0 (tool call not broken: YES)
    bytes emitted: 145 (was 0 before the fix)
    notice: Proofpunk: capture-guard enforcement OFF (python3-not-found) — overwrites of existing evidence captures are NOT being blocked on this mach

## Non-deny control — platform-steer.sh must stay silent (it genuinely never denies)
  rc=0 bytes=0 (expected 0 bytes — no false notice added)
