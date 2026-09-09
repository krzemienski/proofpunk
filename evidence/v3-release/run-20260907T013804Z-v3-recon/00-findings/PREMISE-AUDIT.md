# PREMISE-AUDIT — work order vs measured reality

Recorded: 2026-09-07T01:53:57Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee

The v3 work order asserts a repo state that no longer holds. Each premise below was
measured against disk this session. This table governs every downstream phase.

| # | Work-order premise | Measured reality | Verdict | Evidence |
|---|---|---|---|---|
| P1 | HEAD is `a41591a` | HEAD is `93c479de`, 10 commits ahead | **STALE** | `git log --oneline a41591a..HEAD` |
| P2 | manifests at 2.2.0 | 2.2.0 in all 5 | HOLDS | `jq .version` on each |
| P3 | 18 skills | 18 at HEAD; 17 on disk on arrival (F-001) | HOLDS after repair | `ls -d skills/*/` |
| P4 | 13 shared references | **14** on disk, all tracked | **WRONG** | `ls references/*.md` |
| P5 | 7 event keys, **9 script registrations** | 7 keys, **11 registrations**, 9 distinct scripts, 9 files | **WRONG** | `jq [.hooks[][].hooks[]] | length` = 11 |
| P6 | head description may breach 1024 | max is 980 (`implement`); `proofpunk` = 720 | **WRONG** | inline python over 18 SKILL.md |
| P7 | Phases 0-4 not yet done | `docs/discovery-register.md` marked **FINAL**, closed 2026-09-04 | **ALREADY DONE** | `docs/discovery-register.md:1-7` |
| P8 | `tools/fresh_evidence.py` | absent; real path `skills/end-user-testing/scripts/` | **WRONG PATH** | `find . -name fresh_evidence*` |
| P9 | `dry-run-install.sh` invokes the installer | MODEL ONLY; declares it never invokes `proofpunk-install.sh` | **CONFIRMED-OPEN** | `verify-harness-integrity` output |
| P10 | root release reports carry false claims | already carry dated superseding notices | **ALREADY FIXED** | A12 lane, per-report line audit |
| P11 | every proofpunk skill also standalone in `~/.claude/skills` | only `proofpunk-doctrine` present | **DISPUTED** | A2 lane, pending confirm |

## Consequence for sequencing

The work order commissions Phases 0-4 as if from zero. They were substantially
executed in a prior session and recorded FINAL. Re-running them from scratch would
discard a closed record and re-derive known answers.

Correct posture: **verify the prior register rather than inherit or ignore it.**
Both refutations it raised (P5, P6) were independently re-measured this session and
the register is CORRECT on both; the work order is wrong. Its remaining OPEN items
(D1/D2 as interpretation, D9b, D9c, Lane B token) stay open — they need an operator,
not more searching.

## Counts of record for all downstream phases

```
skills=18  references=14  commands=6+6  hook_files=9
event_keys=7  registrations=11  distinct_scripts=9  agents=3  tools=21
```

---

## Round 2 — premises refuted by the forensics lanes (each independently re-verified)

| # | Work-order premise | Measured reality | Verdict | Lane / my check |
|---|---|---|---|---|
| P12 | `build-site.py` hardcodes `/proofpunk:cook` at ~line 311 | line 311 is `/proofpunk:install`; `cook` appears **0 times** in the 611-line file | **FALSE** | A6 + `grep -in cook tools/build-site.py` = no hits |
| P13 | `build-site.py` LAYERS map carries dead names | LAYERS (`:167-175`) lists only live skills; counts derive from live globs (`:162`, `:296`) | **FALSE** | A6 + read `:162-180` |
| P14 | dead names survive in live guidance | 88 hits, **all 88** classified historical-provenance prose; 0 live | **FALSE** | A6 |
| P15 | `82a4ba6` force-moved a published tag | that commit records the decision **NOT** to force-move; calls it "risky". No force-move in reflog or history | **INVERTED** | A3 |
| P16 | `truth-audit` slash surface drifts from its script (`--since` rc=2) | wrong-script comparison. `session_intent.py` is a different script for a different step. `init_audit_workspace.py` accepts `--start/--end` correctly; `207e041` fix holds | **FALSE** | A11 (self-corrected) |
| P17 | `~/.config/opencode/commands/` holds stale flags + orphan `proofpunk-cook.md` | zero live proofpunk command files; prior stale state already moved to `_retired-*` | **ALREADY FIXED** | A11 |
| P18 | every proofpunk skill also standalone in `~/.claude/skills` | **zero** of the 18 present there. Asymmetry: `~/.omp/agent/skills/` has all 18 | **FALSE for Claude, TRUE for OMP** | A2 (self-corrected) + F-003 |
| P19 | `InstructionsLoaded` / `PostToolUseFailure` may be unsupported | all 7 event keys current and supported | **HOLDS (supported)** | A7 |
| P20 | 13 references | 14 at HEAD; 13 was correct at `a41591a` (`run-trace-schema.md` added in `73e928e`) | **BOTH RIGHT, different commits** | A6 |

## Round 2 — genuinely open, confirmed by measurement

| item | status | source |
|---|---|---|
| Bash-write bypass | **OPEN**. Working tree swaps SHA-256 content hashing for a stat signature (size+mtime_ns+ctime_ns+inode), 15.5s -> 0.02s | A5 |
| the abandoned shell-parsing attempt | **NOT FOUND** in any ref after 6 distinct searches; exists only as an unattributed comment | A5 |
| `dry-run-install.sh` | MODEL ONLY — never invokes `tools/proofpunk-install.sh`; self-declared | A10 / harness-integrity |
| `truth-forge@1.7.0` still registered | ships live `cook` + `functional-validation` skills on this host | F-003 |
| D1 / D2 / D9b / D9c | OPEN — need an operator, not more searching | prior register + A1 |

## Standing correction

Nine work-order premises are now measurably false or inverted, and Phases 0-4 were
already closed in a prior session. The remaining real work is NOT the front half —
it is the small set of genuinely open items above plus the two defects found this
session (F-002 installer bundler, F-003 competing live sources).
