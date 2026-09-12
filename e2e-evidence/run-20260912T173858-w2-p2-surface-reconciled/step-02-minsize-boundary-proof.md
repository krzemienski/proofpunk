# fresh_evidence.py min-size enforcement — boundary drive

Defect: references/evidence-contract.md:69 rule 3 requires every artifact
to be > 1024 bytes ('Zero-byte or tiny files are INVALID'). validate only
rejected size==0, so a 40-byte artifact proving nothing returned
'validate OK'. The tool that enforces the evidence contract was
under-enforcing it — the same defect class as a silent fail-open.

Boundary is exclusive: 1024 is NOT > 1024, so 1024 must FAIL.

## artifact of exactly 1023 bytes
   actual size on disk: 1023
   validate rc=2  => REFUSED
   stdout: 
   stderr: THIN: e2e-evidence/run-20260912T173928-b1023/step-01-probe.log (1023 bytes, needs > 1024) — too small to carry a claim; re-capture with its command,

## artifact of exactly 1024 bytes
   actual size on disk: 1024
   validate rc=2  => REFUSED
   stdout: 
   stderr: THIN: e2e-evidence/run-20260912T173928-b1024/step-01-probe.log (1024 bytes, needs > 1024) — too small to carry a claim; re-capture with its command,

## artifact of exactly 1025 bytes
   actual size on disk: 1025
   validate rc=0  => ACCEPTED
   stdout: validate OK: e2e-evidence/run-20260912T173929-b1025
   stderr: 

Expected per contract: 1023 REFUSED, 1024 REFUSED, 1025 ACCEPTED.
