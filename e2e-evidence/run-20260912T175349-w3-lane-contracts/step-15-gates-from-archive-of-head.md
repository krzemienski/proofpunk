# Gate matrix from an archive of committed HEAD (c2e4734)

Every prior gate run in this session used my working tree. That is not
what a user gets: the lane-contract digest defect fixed in c2e4734 was
invisible from the working tree and visible only from an archive,
because .planning/ exists locally and ships to nobody. So this matrix
runs against 'git archive HEAD | tar -x' — the clone surface.

## Clean-tree facts
  .planning present:            NO (correct — gitignored)
  shipped digest present:       YES
  lane contracts present:       2
  skills present:               18
  hook scripts present:         10

## The matrix
  python3 tools/verify-counts.py           unpiped rc=0
      VERDICT: PASS — live .md counts match the tree
  python3 tools/verify-citations.py        unpiped rc=0
      RESULT: PASS (default: ERROR-only)
  python3 tools/verify-orchestration.py    unpiped rc=0
      documented order, with methods owned exactly once.
  python3 tools/verify-lane-contracts.py   unpiped rc=0
        files under lane ownership: 12
  sh tools/test-hooks.sh                   unpiped rc=0
      HOOK TEST FAILS: 0
  sh tools/dry-run-install.sh              unpiped rc=0
      INSTALL DRY-RUN FAILS: 0
  sh tools/test-installer.sh               unpiped rc=0
      INSTALLER TEST FAILS: 0

  gates failing: 0 of 7

## Linux, both arms, from the same archive
  arm=root: gates failing: 0 of 7
  arm=nonroot: gates failing: 0 of 7
