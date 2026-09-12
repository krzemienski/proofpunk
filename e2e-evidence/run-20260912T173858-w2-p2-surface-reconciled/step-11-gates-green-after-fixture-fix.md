# Gate matrix — re-captured after the harness fixture fix (e180035)

step-10 recorded test-installer.sh at rc=1. That was a real red gate:
the fixture's 7-byte 'clean' artifact was refused by the stricter
validator. The fixture was stale, not the product. Re-run in full:

python3 tools/verify-counts.py             unpiped rc=0
    scanned 56 live .md files
    VERDICT: PASS — live .md counts match the tree

python3 tools/verify-orchestration.py      unpiped rc=0
    VERDICT: PASS — the 18 skills execute as one delegation DAG, in the
    documented order, with methods owned exactly once.

python3 tools/verify-citations.py          unpiped rc=0
    
    RESULT: PASS (default: ERROR-only)

bash tools/test-hooks.sh                   unpiped rc=0
      PASS: platform-steer fails open silently on malformed stdin
    HOOK TEST FAILS: 0

bash tools/dry-run-install.sh              unpiped rc=0
    
    INSTALL DRY-RUN FAILS: 0

bash tools/test-installer.sh               unpiped rc=0
      PASS: F-D5-2: installed fresh_evidence.py --help exits 0
    INSTALLER TEST FAILS: 0

## Linux parity for the same matrix (debian:stable-slim, root and non-root)
### arm=root
  python3 tools/verify-counts.py           unpiped rc=0
  python3 tools/verify-orchestration.py    unpiped rc=0
  python3 tools/verify-citations.py        unpiped rc=0
  sh tools/test-hooks.sh                   unpiped rc=0
  sh tools/dry-run-install.sh              unpiped rc=0

### arm=nonroot
  python3 tools/verify-counts.py           unpiped rc=0
  python3 tools/verify-orchestration.py    unpiped rc=0
  python3 tools/verify-citations.py        unpiped rc=0
  sh tools/test-hooks.sh                   unpiped rc=0
  sh tools/dry-run-install.sh              unpiped rc=0

