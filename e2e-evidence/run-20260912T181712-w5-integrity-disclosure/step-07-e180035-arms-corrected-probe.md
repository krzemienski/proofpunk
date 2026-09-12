# e180035: discriminating arms, with the probe corrected

step-06 reported 'group 9 builds its clean artifact with: echo PASSED'
for BOTH arms, which is wrong. That grep scanned the whole file and
matched the thin-case line, which legitimately still uses echo PASSED
in the repaired fixture. The arms' rc values were right; the line
describing WHY was not. Superseded here rather than edited, because
step-06 is already sealed.

## The actual fixture difference, measured inside group 9 only
  BEFORE (c169831):
    verdict artifact built by: echo PASSED > "$(python3 "$FE" next-step verdict).txt"
    padding present          : NO
  AFTER (e180035):
    verdict artifact built by: printf 'PASSED %s\n' "$PAD" > "$(python3 "$FE" next-step verdict).txt"
    padding present          : PAD=$(python3 -c "print('.' * 1100)")

BEFORE writes a 7-byte verdict artifact; AFTER pads it past the
1024-byte floor while keeping the tamper case same-size.

## Both arms run, validator held constant at the fixed version
  BEFORE (c169831): unpiped rc=1
      FAIL: fresh_evidence contract drift — expected [empty_seal_rc=2 empty_validate_rc=2 unsealed_rc=2 sealed_clean_rc=0 samesize_tamper_rc=2] got [empty_seal_rc=2 empty_validate_rc=2 unsealed_rc=2 sealed_clean_rc=2 samesize_tamper_rc=2]
    INSTALLER TEST FAILS: 1
  AFTER (e180035): unpiped rc=0
      PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
    INSTALLER TEST FAILS: 0

Only the fixture differs between arms. BEFORE fails with contract
drift naming sealed_clean_rc; AFTER passes. The failing arm reproduces
the exact defect the commit fixed.
