# D5 explicit inventory + F-D6-4 registration count — CLOSED

Measured: 2026-09-04 (UTC) | Repo HEAD: `9963648` (working tree dirty)
Method: `os.walk` over the product tree (excluding `.git`, `node_modules`,
`__pycache__`, `.omc`, `.debug`, `banks`) for D5; `json.load` of
`plugins/proofpunk/hooks/hooks.json` walked programmatically for F-D6-4.
Neither result is a grep heuristic — both enumerate real objects.

## D5 — explicit named-artifact inventory: 26/26 located

The Phase 0 register left D5 **PARTIAL**, because the earlier sweep was a
citation heuristic (296 refs / 60 unresolved) rather than an explicit
inventory of the artifacts guidance actually names. That inventory is now
complete. Every named artifact resolves:

| Artifact | Path |
|---|---|
| `fresh_evidence.py` | `plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py` |
| `hooks.json` | `plugins/proofpunk/hooks/hooks.json` |
| 9 hook scripts | `plugins/proofpunk/hooks/*.sh` |
| `proofpunk-install.sh`, `test-installer.sh`, `test-hooks.sh`, `dry-run-install.sh` | `tools/` |
| `verify-orchestration.py`, `sdk_probe.py`, `build-site.py`, `generate-themes.py` | `tools/` |
| `palettes.json` | `plugins/proofpunk/themes/palettes.json` |
| `invocation-contracts.md`, `consolidation-decisions.md`, `improvements.md`, `architecture.md` | `plugins/proofpunk/docs/` |
| `proofpunk.ts` | `plugins/proofpunk/extensions/proofpunk.ts` |
| `execution-ledger.json` | `.planning/execution-ledger.json` |

**Not located: none.** D5 moves PARTIAL → **RESOLVED (high)**.

Confirms F-D6-1: `fresh_evidence.py` is skill-owned, not in `tools/`. Any
guidance placing it in `tools/` is wrong and belongs in the drift inventory.

## F-D6-4 — registration count: the work order is wrong, the repo is right

Walked `hooks.json` programmatically rather than counting by eye:

| Metric | Work order claims | **Measured** |
|---|---|---|
| Event keys | 7 | **7** ✓ |
| Script registrations | 9 | **11** ✗ |
| Distinct scripts | — | **9** |
| Hook files on disk | 9 | **9** ✓ |

Two scripts are registered twice, which is the entire discrepancy:

- `stop-guard.sh` → `Stop` **and** `SubagentStop`
- `bash-write-notice.sh` → `PostToolUse`/`Bash` **and** `PostToolUseFailure`/`Bash`

Full registration table:

| Event | Matcher | Script | Timeout |
|---|---|---|---|
| SessionStart | `startup\|resume\|clear` | `session-start.sh` | 5 |
| Stop | (none) | `stop-guard.sh` | 10 |
| SubagentStop | (none) | `stop-guard.sh` | 10 |
| PreToolUse | `Write\|Edit` | `no-test-files.sh` | 5 |
| PreToolUse | `Write\|Edit` | `evidence-guard.sh` | 5 |
| PreToolUse | `Write\|Edit` | `capture-guard.sh` | 5 |
| PreToolUse | `Bash` | `bash-write-snapshot.sh` | 10 |
| InstructionsLoaded | (none) | `instructions-loaded.sh` | 5 |
| PostToolUse | `Write\|Edit` | `post-write-walkthrough.sh` | 5 |
| PostToolUse | `Bash` | `bash-write-notice.sh` | 10 |
| PostToolUseFailure | `Bash` | `bash-write-notice.sh` | 10 |

Integrity checks, both clean:
- Scripts registered but absent from disk: **none**
- Files on disk but never registered: **none**
  (This is the `99c72fb` defect class — `evidence-guard.sh` once shipped
  unregistered. Not reproducing.)

### Downstream consequence — binding

The release-validation criterion must read **11 registrations across 7 event
keys, 9 distinct scripts**. Left uncorrected, a gate asserting "9
registrations" fails against a correct repo, or worse, passes by counting
distinct scripts and calling them registrations. `architecture.md:497`
already states the correct value.

## Open / UNRESOLVED

- **D1 / D2** — still lack operator corroboration; carried into Phase 1
  mining (`SessionMiner` lane). Held at medium confidence as prior-agent
  interpretations, per the register's own confidence rule.
- **D9b ("Rebo") / D9c ("Furble's Claude")** — unattested across the tree,
  97 Claude session files, and 7,320 OMP session files. No further source is
  known to exist. Recorded unresolved with attempts, never guessed.
