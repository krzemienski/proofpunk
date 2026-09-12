# Full gate matrix against committed HEAD (ba16393)

Run from a clean 'git archive HEAD' extraction, so the subject is what
a user would clone rather than my working tree.

  python3 tools/verify-counts.py           unpiped rc=0
      VERDICT: PASS — live .md counts match the tree
  python3 tools/verify-citations.py        unpiped rc=0
      RESULT: PASS (default: ERROR-only)
  python3 tools/verify-orchestration.py    unpiped rc=0
      documented order, with methods owned exactly once.
  python3 tools/verify-lane-contracts.py   unpiped rc=1
        files under lane ownership: 12
  sh tools/test-hooks.sh                   unpiped rc=0
      HOOK TEST FAILS: 0
  sh tools/dry-run-install.sh              unpiped rc=0
      INSTALL DRY-RUN FAILS: 0
  sh tools/test-installer.sh               unpiped rc=0
      INSTALLER TEST FAILS: 0

## Which criteria this evidence supports at HEAD
  P3  citations resolve          -> verify-citations rc=0
  P12 counts/versions accurate   -> verify-counts rc=0
  P13 harnesses pass             -> all seven rc=0 above

## Which criteria are NOT re-proven here, and are downgraded
  P5  router links all 17 — the PASS was inherited from a prior
      session's run and was not re-driven in this one. Downgraded to
      UNVERIFIED rather than carried forward on inheritance.
  P14 sealed run — the seal this cites was produced before this final
      gate pass, so it cannot describe HEAD. Re-sealed after this
      artifact lands; the verdict rests on that seal, not an earlier one.
