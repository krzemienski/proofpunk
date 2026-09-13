# Step 6 - The completion gate, and clearing every gate to zero

## The gate (AC5)
completion_gate.py is the executable contract, not prose:

  live child  -> writes NOTHING, exits 2, names the running agents
  nothing live -> writes the summary atomically, exits 0

Driven, 16 assertions across 5 cases, GATE FAILS: 0:
  live child            exit 2, no artifact, names 'scout'
  all terminal          exit 0, artifact names both agents, records
                        'failed' as terminal, refuses to quote total_*,
                        and does NOT say 'successfully'
  leaked 257h child     exit 0, artifact labels it 'aged out'
  unknown age           exit 0, artifact says 'NOT proven finished'
  no tracker            exit 0, artifact says it 'confirms NOTHING'
                        and 'absence of evidence'

The no-tracker case matters: on OMP and OpenCode the tracker does not
exist, so the artifact states plainly that it proves nothing rather
than implying a clean run.

## Gate state: 0 known defects

  verify-orchestration       rc=0
  verify-citations           rc=0
  verify-counts              rc=0   skills 19, refs 17
  verify-lane-contracts      rc=0
  verify-proof-vocab         rc=0
  verify-router-links        rc=0
  verify-shipped-vs-active   rc=0
  verify-mutation-artifact   rc=0
  verify-harness-integrity   rc=0
  test-hooks.sh              HOOK TEST FAILS: 0
  dry-run-install.sh         INSTALL DRY-RUN FAILS: 0

## Three of those were FAILING AT HEAD before this work
Attributed by re-running each against a clean git archive, not assumed:

  verify-shipped-vs-active   FAIL at HEAD -> fixed
    cause: verify-lane-contracts.py was never wired into CI.
    fix: added it to .github/workflows/gates.yml.

  verify-harness-integrity   FAIL at HEAD -> fixed
    cause: verify-lane-contracts.py carried no PP-HARNESS-SUBJECT tag.
    Three attempts were needed. The tag must be a COMMENT (not a
    docstring line), and its declared subject must appear as a literal
    token in non-comment source. My first two declarations named
    *.contract.yml basenames that never appear -- the script globs a
    directory. The honest subject is the directory itself.

  verify-proof-vocab         FAIL at HEAD -> fixed
    cause: 6 uncited status words in .planning/*.prompt.md, which the
    verifier includes in scope BY DESIGN (its header lists
    .planning/*.md as a living doc).
    fix: cited the doctrine reference that governs each claim.
    Both cited files exist on disk -- verified, not assumed.

## Correction to my own earlier reporting
I twice described these as 'pre-existing, not mine' and moved on. They
were inherited, but a defect I ship over is still a defect I shipped.
All three are now fixed rather than attributed.
