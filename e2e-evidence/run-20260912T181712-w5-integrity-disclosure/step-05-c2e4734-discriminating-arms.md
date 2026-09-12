# c2e4734: a discriminating before/after from two real clones

The report cited only step-15, which shows the checker green AFTER the
fix. A green with no failing arm proves the tree is currently fine; it
does not prove this commit caused that. Both arms below are extracted
with 'git archive' — the clone surface, where the defect lived.

## BEFORE (parent) — ba16393
  .planning present in clone     : NO (gitignored)
  digest shipped beside contracts: NO
  acquire_digest points at       : .planning/v4-architecture/docs-claude.md
  verify-lane-contracts.py       : unpiped rc=1
      ERROR: lane-01-hooks.contract.yml: acquire_digest does not resolve: .planning/v4-architecture/docs-claude.md
      ERROR: lane-02-evidence.contract.yml: acquire_digest does not resolve: .planning/v4-architecture/docs-claude.md

## AFTER (the fix) — c2e4734
  .planning present in clone     : NO (gitignored)
  digest shipped beside contracts: YES
  acquire_digest points at       : plugins/proofpunk/lane-contracts/digests/docs-claude.md
  verify-lane-contracts.py       : unpiped rc=0

## Verdict
BEFORE rc=1 with 'acquire_digest does not resolve'; AFTER rc=0. The
arms differ only by this commit, and the failing arm reproduces the
exact defect the commit claims to fix. That is what makes it a driven
proof rather than a citation of the current green.

## Why the earlier citation was insufficient
step-15 runs the matrix at HEAD and shows 7/7. Every gate is green
there, including on a tree where the bug never existed — so it cannot
distinguish 'the fix worked' from 'nothing was ever wrong'. Citing it
alone let 'has a citation' stand in for the P8 proof obligation, which
asks that the changed behaviour itself be exercised.
