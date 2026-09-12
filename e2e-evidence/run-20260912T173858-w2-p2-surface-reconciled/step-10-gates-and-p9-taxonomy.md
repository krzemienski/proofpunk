# Gate matrix + P9 hook taxonomy, measured

## Part 1 — full gate matrix, macOS, unpiped rcs
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
bash tools/test-installer.sh               unpiped rc=1
      PASS: F-D5-2: installed fresh_evidence.py --help exits 0
    INSTALLER TEST FAILS: 1

## Part 2 — P9: which hooks can actually deny

P9 as written assumes '14 cases = 7 hooks x (block + allow)'. That
assumption is false in two ways: there are 10 hooks, not 7, and a block
case is not applicable to a hook with no deny path. Measured below by
driving each hook, not by reading the table.

| hook | event(s) | deny mechanism | measured |
|---|---|---|---|
| `bash-write-notice.sh` | PostToolUse,PostToolUseFailure | none | see drives below |
| `bash-write-snapshot.sh` | PreToolUse | none | see drives below |
| `capture-guard.sh` | PreToolUse | exit 2 | see drives below |
| `evidence-guard.sh` | PreToolUse | exit 2 | see drives below |
| `instructions-loaded.sh` | InstructionsLoaded | none | see drives below |
| `no-test-files.sh` | PreToolUse | exit 2 | see drives below |
| `platform-steer.sh` | PreToolUse | none | see drives below |
| `post-write-walkthrough.sh` | PostToolUse | none | see drives below |
| `session-start.sh` | SessionStart | none | see drives below |
| `stop-guard.sh` | Stop,SubagentStop | decision:block | see drives below |

### Deny-capable hooks driven with a must-deny payload
  no-test-files.sh  deny payload -> unpiped rc=2  (expect 2)
  evidence-guard.sh deny payload -> unpiped rc=2  (expect 2)
  capture-guard.sh  deny payload -> unpiped rc=2  (expect 2)
  stop-guard.sh     claim-without-proof -> decision:block EMITTED

### Allow-path control for the same four (a guard that always denies is also broken)
  no-test-files.sh  production path -> unpiped rc=0  (expect 0)
  evidence-guard.sh clean evidence  -> unpiped rc=0  (expect 0)
  capture-guard.sh  NEW capture     -> unpiped rc=0  (expect 0)
  stop-guard.sh     no claim         -> silent/allow (expect)
