# fresh_evidence.py min-size enforcement — boundary drive

Defect: references/evidence-contract.md:69 rule 3 requires every artifact
to be > 1024 bytes ('Zero-byte or tiny files are INVALID; discard and
re-capture'). validate rejected only size==0, so a 40-byte artifact
proving nothing returned 'validate OK'. The tool that enforces the
evidence contract was under-enforcing it — the same defect class as a
silent fail-open, in the one script every proof in this repo depends on.

The bound is EXCLUSIVE: 1024 is not > 1024, so 1024 must be refused.
An earlier draft used '< MIN_SIZE_BYTES' and accepted exactly 1024;
this drive is what caught it.

## artifact of exactly 1023 bytes
   size on disk: 1023
   validate unpiped rc=2  => REFUSED
   stdout: 
   stderr: THIN: e2e-evidence/run-20260912T173941-b1023/step-01-probe.log (1023 bytes, needs > 1024) — too small to carry a claim; re-capture with its command, rc, and surrounding

## artifact of exactly 1024 bytes
   size on disk: 1024
   validate unpiped rc=2  => REFUSED
   stdout: 
   stderr: THIN: e2e-evidence/run-20260912T173942-b1024/step-01-probe.log (1024 bytes, needs > 1024) — too small to carry a claim; re-capture with its command, rc, and surrounding

## artifact of exactly 1025 bytes
   size on disk: 1025
   validate unpiped rc=0  => ACCEPTED
   stdout: validate OK: e2e-evidence/run-20260912T173942-b1025
   stderr: 

Contract-required outcome: 1023 REFUSED, 1024 REFUSED, 1025 ACCEPTED.

Consequence on this repo's own evidence: the stricter validate immediately
invalidated two artifacts in the preceding W1 run (903 B and 996 B), which
is the tool working as intended rather than a regression.
