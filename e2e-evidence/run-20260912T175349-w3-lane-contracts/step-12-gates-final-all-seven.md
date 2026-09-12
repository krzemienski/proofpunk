# Final gate matrix — all seven, after the --run and parser changes

python3 tools/verify-counts.py             unpiped rc=0
    scanned 57 live .md files
    VERDICT: PASS — live .md counts match the tree

python3 tools/verify-citations.py          unpiped rc=0
    
    RESULT: PASS (default: ERROR-only)

python3 tools/verify-orchestration.py      unpiped rc=0
    VERDICT: PASS — the 18 skills execute as one delegation DAG, in the
    documented order, with methods owned exactly once.

python3 tools/verify-lane-contracts.py     unpiped rc=0
    LANE CONTRACTS: 2 checked, 0 error(s)
      files under lane ownership: 12

bash tools/test-hooks.sh                   unpiped rc=0
      PASS: platform-steer fails open silently on malformed stdin
    HOOK TEST FAILS: 0

bash tools/dry-run-install.sh              unpiped rc=0
    
    INSTALL DRY-RUN FAILS: 0

bash tools/test-installer.sh               unpiped rc=0
      PASS: F-D5-2: installed fresh_evidence.py --help exits 0
    INSTALLER TEST FAILS: 0

## One of these was red a moment ago
verify-counts.py failed rc=1 with:
  proofpunk-v4-status-report.md:73: 2 hook (live accepts [7, 10, 12])
The report's commit-window paragraph said '2 hook files', which the
count gate reads as a claim about how many hooks the plugin has. The
figure was a diff statistic, not a hook count, but the gate cannot tell
those apart from prose — and it is right not to guess. Rephrased to
'a pair of files under plugins/proofpunk/hooks/'. The gate caught a
real ambiguity in my own writing.

## Linux parity for the changed tool
  test-installer.sh arm=root: unpiped rc=0  INSTALLER TEST FAILS: 0
  test-installer.sh arm=nonroot: unpiped rc=0  INSTALLER TEST FAILS: 0
