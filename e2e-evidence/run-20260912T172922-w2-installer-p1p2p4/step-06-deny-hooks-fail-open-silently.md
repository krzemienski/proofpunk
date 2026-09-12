# Defect drive: deny-capable hooks fail OPEN and SILENT without python3

Instrument: hermetic PATH=/tmp/pp-nopy2-jYKizP/bin (all of /bin + /usr/bin symlinked EXCEPT python*).
Instrument self-check: cat/sed/grep resolve; python3 confirmed absent; 'printf hello | cat' works.

Each deny-capable hook is fed a payload that MUST be denied, twice.

## no-test-files.sh — payload: test-shaped path
  WITH python3   rc=2
    stdout+stderr: Proofpunk: refusing to create a test artifact (/tmp/x/test_thing_test.py). The write path validates by driving the real system as the end user — never by writ
  NO python3     rc=0
    stdout+stderr: 
    bytes of output without python3: 0

## evidence-guard.sh — payload: secret in evidence
  WITH python3   rc=2
    stdout+stderr: Proofpunk: refusing to write probable secret material into an evidence directory. Evidence is committed and public — redact keys/tokens first (see references/
  NO python3     rc=0
    stdout+stderr: 
    bytes of output without python3: 0

## capture-guard.sh — payload: overwrite existing capture
  WITH python3   rc=0
    stdout+stderr: 
  NO python3     rc=0
    stdout+stderr: 
    bytes of output without python3: 0

## Control — stop-guard.sh (deny-capable, correct pattern)
  NO python3     rc=0
    output: {"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"Proofpunk: stop-guard enforcement OFF (python3-not-found). A ran-clean stop is only this notice's absence."}} 
