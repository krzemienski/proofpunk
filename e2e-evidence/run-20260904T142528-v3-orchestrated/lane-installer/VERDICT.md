# LaneInstaller VERDICT — proofpunk installer at HEAD 73e928e

Scope: `tools/proofpunk-install.sh` (read + mutation-restore only; **no net edit**), `tools/test-installer.sh` (+44 lines, groups 11–12).
Evidence root: `/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-installer/`
Installer identity: sha256 `be60e6bef14182c3c38962d72c50bd8c73ce2e1a13649a233a60b9393d56f88e` matches `git show 73e928e:tools/proofpunk-install.sh` (`step-06-before-arm.sha256`, `step-06-before-vs-workdir.rc=0`, `step-11-restore.sha256`, `step-12-restore.sha256`). `bash -n` clean: `step-06-before-arm-bash-n.rc=0`.

Proof level of every claim below is **script-level isolated HOME**, never live-session, never the operator's real `~`.

## What changed

- `tools/proofpunk-install.sh`: **no net change**. HEAD already excludes `__pycache__`/`*.pyc` at line 283. Mutated twice for doctrine-5, restored byte-identical each time.
- `tools/test-installer.sh`: appended **group 11** (F-D5-1 planted-bytecode exclude) and **group 12** (F-D5-2 installed `fresh_evidence.py --help` rc=0). Source group count 10 → 12 (`step-09-group-count-before.txt`, `step-13-group-count-after.txt`).

## What was driven

Isolated scratch `HOME`/`--dir` via `drive-installer.sh`. Unpiped `cmd > log 2>&1; echo $? > log.rc` for every arm.

Derived source truth (`step-00-source-truth.txt`): 18 skills, 14 references, 6 commands, 9 hook scripts named in `hooks.json`, 11 registrations.

### (a) default full install — PASS

- Command: `bash tools/proofpunk-install.sh --source-dir $REPO --dir $DIR_A` with isolated HOME.
- `step-01-default-full-install.rc` = `0`
- `step-01-default-full-install.log` line 5 `installing : 18 skill(s)`, line 45 `18 installed, 0 replaced, 0 skipped`
- `step-01-inventory.txt`: `skill_dir_count=18`, all 18 have `SKILL.md`, doctrine present with all 14 refs, `pycache_in_install_a=0`, `fresh_evidence.py` present under `end-user-testing/scripts/`.

### (b) `--hooks` on CLEAN HOME (no prior settings.json) — PASS

- `step-02-hooks-clean-home.rc` = `0`
- `step-02-hooks-clean-home.log`: 9 scripts copied, 11 events `added` (SessionStart, Stop, SubagentStop, 4× PreToolUse, InstructionsLoaded, PostToolUse×2, PostToolUseFailure).
- `step-02-hooks-inventory.txt`: `settings_valid_json=True`, `missing_copied=[]`, `missing_from_settings=[]`, `want_regs=11 got_regs=11`, `event_symdiff=[]`, `duplicate_event_command_pairs=[]`.
- Captured settings: `step-02-settings.json` (valid JSON, 7 event keys, 11 registrations).

### (c) `--hooks` twice (idempotency) — PASS

- `step-03-hooks-idempotent-second.rc` = `0`
- `step-03-hooks-idempotent-second.log`: every event `already present`; `SKIP proofpunk (already exists)`.
- Script counts in settings after second run (`step-02-hooks-inventory.txt`): each unique script appears once except `stop-guard.sh=2` and `bash-write-notice.sh=2`, matching the two distinct events those scripts are registered on in `hooks.json`. No duplicate `(event, command)` pairs.

### (d) `--only end-user-testing` — PASS

- `step-04-only-skill.rc` = `0`
- `step-04-only-inventory.txt`: `top_dirs=['end-user-testing']`, `fresh_evidence.py` present (10412 B).

### (e) existing install collision then `--override` — PASS

- First: `step-05a-existing-first.rc=0`
- Collision: `step-05b-collision.rc=0`, log `1 skipped (collision)`
- Override: `step-05c-override.rc=0`, log `1 replaced`; `step-05-collision-override-inventory.txt`: `canary_in_live=False`, bak dir contains canary.

## Recorded findings

### F-D5-1 `__pycache__` ships into installed tree — NOT REPRODUCING as a leak at HEAD; exclude already present; assertion added and mutation-proven

HEAD installer already contains:

```
(cd "$src" && tar cf - --exclude='__pycache__' --exclude='*.pyc' .) | (cd "$dst" && tar xf -)
```

cited `step-06-exclude-lines.txt` (before-arm `git show 73e928e` and workdir, both line 283).

Source tree **does** contain host bytecode (`step-00-source-pycache.txt`):
`plugins/proofpunk/skills/stack-testing/scripts/__pycache__/with_server.cpython-311.pyc`

Default install against that source produced **zero** pycache/pyc in the dest (`step-08-pycache-after-arm.txt`: `source_pycache_count=2`, `installed_pycache_count=0`, `EXCLUDED`). Command that failed to reproduce a leak: the step-01 default full install (`step-01-default-full-install.rc=0` + inventory `pycache_in_install_a=0`).

No installer fix shipped — the fix is already in 73e928e. Group 11 plants bytecode in a scratch **source** so the assertion is non-vacuous.

Mutation proof (doctrine 5):
1. Green: `step-10-test-installer-baseline.rc=0`, group 11 PASS (`source had 3 pycache/pyc entries, installed tree has 0`).
2. One named mutation: drop `--exclude` on the tar line. Red: `step-11-mutation-f-d5-1.rc=1`, log `FAIL: F-D5-1 pycache leak — installer copied host bytecode; rc=0 source_pyc=3 dest_pyc=3`. Only group 11 failed.
3. Restore from sha256-matched before-arm: `step-11-restore.sha256` = `be60e6bef14182c3c38962d72c50bd8c73ce2e1a13649a233a60b9393d56f88e`. Green: `step-13-test-installer-restore.rc=0`.

### F-D5-2 `fresh_evidence.py` ships only via wholesale copy, nothing asserting it — CONFIRMED as a harness gap; assertion added and mutation-proven

Installed tree **does** contain a runnable helper:
- Isolated `--only` install: `step-07-fresh-evidence-help.rc=0`, usage printed (`step-07-fresh-evidence-help.log`).
- Full install: `step-07b-fresh-evidence-help-from-full.rc=0`.

Group 9 still only hits the **source** copy. Group 12 now installs then runs `python3 $INSTALLED/end-user-testing/scripts/fresh_evidence.py --help` and requires rc=0.

Mutation proof:
1. Green: group 12 PASS in `step-10-test-installer-baseline.log`.
2. One named mutation: add `--exclude='fresh_evidence.py'` to the tar copy. Red: `step-12-mutation-f-d5-2.rc=6`, group 12 `FAIL: F-D5-2: fresh_evidence.py missing after install` and `--help rc=2` (`can't open file ... No such file or directory`). Collateral verify failures on other groups are the missing-script fallout, not a second mutation.
3. Restore byte-identical: `step-12-restore.sha256` matches before-arm. Green: `step-13-test-installer-restore.rc=0`.

### F-D3-2 coverage rests on a single harness group (`test-installer.sh:257`) — NOT REPRODUCING (structurally false at HEAD)

`step-14-f-d3-2.txt`:
- HEAD 73e928e already had **10** `echo "== group` lines (groups 1–10).
- Line 257 at HEAD is group 10's `ok "installed tree matches canonical hooks.json ..."` call, not the only group.
- After this lane: **12** groups. Line 257 is still that same `ok` line.

Command that failed to reproduce “single group”: `python3` count of `echo "== group` against `git show 73e928e:tools/test-installer.sh` → 10.

## Harness final

`bash tools/test-installer.sh` → `step-13-test-installer-restore.rc=0`, `INSTALLER TEST FAILS: 0`, 12 groups (was 10 at HEAD, assignment mentioned 7 — that count was already stale before this lane).

## Observed, not a FAIL of the driven default path

- Default `--dir` install does **not** copy `plugins/proofpunk/commands/` (6 files in source: forge-prompt, implement, install, rate-prompt, truth-audit, verify). The installer is a plain-skills copier; commands are plugin-glue (`--plugins`). Not driven this lane → **UNVERIFIED** as a product defect.
- Group 8 still only name-checks 3 of 9 hook scripts. Group 10 + this lane's isolated inventory cover all 9/11. Left as-is (group 10 already derives from `hooks.json`).

## Open / UNRESOLVED

- None for the three named findings.
- `--plugins` / command-surface install path: **UNVERIFIED** (out of the five required drive steps; LaneCommandSurface owns `sdk_probe.py`).
- Host bytecode remains in the **source** tree at `plugins/proofpunk/skills/stack-testing/scripts/__pycache__/`. Installer excludes it; cleaning the checkout is not this lane's file ownership (`plugins/` belongs to other lanes).
