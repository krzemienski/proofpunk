# step-11 — P14 and P15: a clean, immutable, sealed run

## Why these were FAIL/UNVERIFIED before
P14 (sealed via fresh_evidence) and P15 (success measured, not asserted) both
failed in the prior task for the same reason: I edited artifacts AFTER sealing
them, twice. A sealed run whose contents changed afterwards proves nothing —
the seal is the claim that they did not.

## This run
    run-20260913T072606-v4-all-agents

    steps sealed        : 10
    validate            : OK
    inventory rows      : 12
    post-seal mutations : 0

Verified independently of `validate` by recomputing SHA-256 for every file
named in evidence-inventory.txt and comparing against the recorded digest.
Zero mismatches.

## The steps
    step-01-warning-attribution.md
    step-02-omp-contract.md
    step-03-opencode-harness.md
    step-04-p5-p6-p9.md
    step-05-p10-enforcement-map.md
    step-06-p11-prose-review.md
    step-07-p11-round2.md
    step-08-p11-round3.md
    step-09-platform-steer-mutation.md
    step-10-p7-p8-improvements.md

## P15 — measured, not asserted
Every verdict in this run cites a command output or a file read, and several
CONTRADICT what I expected going in:

- I predicted the reported hooks.json warning was proofpunk's. It is not —
  the scan named claude-code-harness 4.16.3.
- I predicted OMP could write the tracker once I had the contract. The
  contract proved the opposite.
- My first hook-taxonomy classifier said 3 block-capable; reading the source
  said 4. The measurement corrected me.
- My 83-file citation sweep looked like a fix and took verify-citations from
  0 to 75 errors. Reverted.
- My P6 portability fix made the metric WORSE (plugin_pass 6/6 -> 4/6).
  Reverted.

A run where the measurements only ever confirmed the plan would be the
suspicious one.

## What I SEE
10 sealed steps, an inventory that still matches byte-for-byte, and a set of
verdicts that changed my mind five times. Nothing was edited after sealing;
where a later step superseded an earlier finding, it was added as a NEW step
(step-07 and step-08 supersede step-06's round-1 disposition) rather than
rewriting the sealed one.

VERDICT: P14 PASS (sealed, validate OK). P15 PASS (0 post-seal mutations;
success measured against artifacts, not asserted).
