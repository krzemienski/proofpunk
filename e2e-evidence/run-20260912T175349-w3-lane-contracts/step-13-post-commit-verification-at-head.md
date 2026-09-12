# Post-commit verification against committed HEAD (ba16393)

step-11 captured the strict-parsing proof from the WORKING TREE while
the parser was still being edited. That artifact proves a state that
no longer necessarily matches what shipped. This step re-drives the
same cases against a clean 'git archive HEAD' extraction, so the
subject is the committed file and nothing else.

## Subject
  git rev-parse HEAD: ba1639355157ab17531f865acac82d4d2a54f5f2
  extracted to a clean tree via: git archive HEAD | tar -x
  sha256 of the committed helper:
    0a8836709dfde92a09351c527ff5c01135f3848b6228aa4b0066546e275d855c
  sha256 of the working-tree helper:
    0a8836709dfde92a09351c527ff5c01135f3848b6228aa4b0066546e275d855c
  identical: YES

## Tied-mtime targeting, in an isolated tree
  (isolated tree: exactly these two runs exist, so a tie is decidable)
    e2e-evidence/run-20260912T181059-alpha  mtime=1789236659.842544
    e2e-evidence/run-20260912T181059-beta  mtime=1789236659.842544
    tied: True

  alpha holds one 1200-byte artifact -> must validate rc=0
  beta  holds one   50-byte artifact -> must validate rc=2
    validate --run alpha  unpiped rc=0
    validate --run beta   unpiped rc=2
  Different verdicts under a genuine tie is the whole point: without
  --run both invocations would resolve to the same arbitrary winner.

## Malformed invocations, committed parser
    seal junk                  rc=2
    validate junk              rc=2
    validate --bogus           rc=2
    validate --run             rc=2
    next-step                  rc=2
    next-step a b              rc=2
    --run twice                rc=2
    init-run --run             rc=2
    --run nonexistent          rc=2
  All refuse rc=2.

## Group 9b of the committed harness
  sh tools/test-installer.sh  unpiped rc=0
  == group 9: fresh_evidence.py strict seal/validate contract
    PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
    PASS: fresh_evidence --run targets a specific run under tied mtimes; parser refuses junk
  == group 12: F-D5-2 installed fresh_evidence.py is runnable
    PASS: F-D5-2: fresh_evidence.py present in installed tree
    PASS: F-D5-2: installed fresh_evidence.py --help exits 0
  INSTALLER TEST FAILS: 0
