# P4 — installer idempotency, re-captured with full context

Supersedes step-05 of run-20260912T172922-w2-installer-p1p2p4, which was
903 bytes and refused by the stricter min-size rule. Same measurement,
captured with the commands, rcs, and surrounding state it was missing.

## HOME under test
/tmp/pp-p2-qW8jVh

## The two runs (identical flags, same HOME)
```
bash tools/proofpunk-install.sh --target claude-code --source local --source-dir $(pwd) --hooks --themes --plugins
```
run1 rc=0 — e2e-evidence/run-20260912T172922-w2-installer-p1p2p4/step-02-install-run1-clean-home.log
run2 rc=0 — e2e-evidence/run-20260912T172922-w2-installer-p1p2p4/step-04-install-run2-idempotency.log

## settings.json, byte-for-byte, after each run
```
$ diff /tmp/pp-settings-run1.json /tmp/pp-settings-run2.json
unpiped diff rc=0  (0 = files identical)
```

## sha256 of both snapshots (a diff rc alone does not show WHAT was compared)
14737c5b0a82d8bbaa1382a55bd39c8486242d3eafaf2358cf1cca108ed557b1  /tmp/pp-settings-run1.json
14737c5b0a82d8bbaa1382a55bd39c8486242d3eafaf2358cf1cca108ed557b1  /tmp/pp-settings-run2.json

## Registered hook commands, parsed from each snapshot
### /tmp/pp-settings-run1.json
  InstructionsLoaded: 1 -> instructions-loaded.sh
  PostToolUse: 2 -> post-write-walkthrough.sh, bash-write-notice.sh
  PostToolUseFailure: 1 -> bash-write-notice.sh
  PreToolUse: 5 -> no-test-files.sh, evidence-guard.sh, capture-guard.sh, bash-write-snapshot.sh, platform-steer.sh
  SessionStart: 1 -> session-start.sh
  Stop: 1 -> stop-guard.sh
  SubagentStop: 1 -> stop-guard.sh
  total registered commands: 12
### /tmp/pp-settings-run2.json
  InstructionsLoaded: 1 -> instructions-loaded.sh
  PostToolUse: 2 -> post-write-walkthrough.sh, bash-write-notice.sh
  PostToolUseFailure: 1 -> bash-write-notice.sh
  PreToolUse: 5 -> no-test-files.sh, evidence-guard.sh, capture-guard.sh, bash-write-snapshot.sh, platform-steer.sh
  SessionStart: 1 -> session-start.sh
  Stop: 1 -> stop-guard.sh
  SubagentStop: 1 -> stop-guard.sh
  total registered commands: 12

A duplicate registration would show here as the same script name twice
on one event, or as a rising total between run1 and run2. Neither occurs.

## Second run's disposition of the 18 skills
== summary: 0 installed, 0 replaced, 18 skipped (collision), 0 missing ==
SKIP lines counted: 18
Collision protection held: nothing was silently replaced.

## Litter check — a second run must not accumulate backups
skill .bak-* dirs:      0
settings.json.bak files: 1  (one, overwritten in place, not one per run)

VERDICT P4: PASS — no duplicate hook registrations, no JSON corruption.
