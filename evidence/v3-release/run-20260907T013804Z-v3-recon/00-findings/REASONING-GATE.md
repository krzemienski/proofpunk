# Sequential reasoning gate — front half closed

Recorded: 2026-09-07T02:29:54Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee

## 1. What was originally wanted (Phase 1)

Recoverable from the record, not re-mined this session — `docs/session-intent-ledger.md`
and `docs/discovery-register.md` already exist and are marked FINAL (closed 2026-09-04).
Round-2 dictation governs: establish what things ARE before changing them. That ordering
is the one instruction this session could still honour, and it is why nothing was fixed.

## 2. What the hosts actually require (Phase 2)

- All 7 `hooks.json` event keys are current and supported, incl. `InstructionsLoaded`
  and `PostToolUseFailure` — the two flagged as most at risk. (A7)
- `PostToolUse` cannot deny; only `PreToolUse` carries a permission decision. (A7)
- OpenCode accepts BOTH `skill/` and `skills/`; the blocking installer question is moot. (A8)
- OMP precedence: native user-level (100) OUTRANKS plugin (90). (A9, corrected)
- Max skill description is 980 chars against a 1024 ceiling — no breach. (verified myself)

## 3. What exists today (Phase 3)

Counts of record: 18 skills · 14 references · 6+6 commands · 9 hook files ·
7 event keys · 11 registrations · 3 agents · 21 tools.

Graph: single root, 17/17 router links, 48/48 reciprocal edges, zero cycles, depth 5,
zero broken citations. (A6)

Gates on the corrected tree: 10 green, 3 red — `gauge-report` (#4 only, 4/6),
`verify-harness-integrity` (3 stale tags), `test-installer` (rc=7, F-002/F-004/F-005).

## 4. Therefore what must change, and in what order

The work order commissions a front half that was already done and a back half aimed
largely at premises that are false. Nine premises were refuted by measurement
(see PREMISE-AUDIT.md). The real remaining work is much smaller and differently shaped:

| # | Work | Why | Blocking |
|---|---|---|---|
| 1 | Decide the fate of the 3 uncommitted in-flight changes | They are the sole cause of rc=7 (F-002) and they swap the Bash-guard hashing strategy (A5). Nothing can be released while the tree is in this state | **operator** |
| 2 | Fix bundler ordering (F-004) | Real defect, exposed by 1. Hits every skill citing a newly-bundled reference | no |
| 3 | Fix group-10 assertion scoping (F-005) | Harness reports FAIL on a TRUE parity claim | no |
| 4 | Fix 3 stale harness-integrity tags (A10) | 2 stale inline tags + 1 undeclared harness | no |
| 5 | Gauge #4: 4/6 commands proven at the slash surface | Sole remaining gauge blocker | no |
| 6 | Uninstall `truth-forge@1.7.0` (F-003) | Live `cook` skill + 6 shadow commands with removed flags | **operator consent** |
| 7 | Bump manifests 2.2.0 -> 3.0.0 | Only after 1-5 | after 1-5 |

## 5. What the work order asked for that should NOT be built

Stated plainly rather than silently dropped:

- **L8 dead-name sweep of generator source** — target does not exist. `tools/build-site.py`
  has zero `cook` hits; line 311 is `/proofpunk:install`. The real drift is on the HOST (F-003).
- **L18 truth-audit flag-drift fix** — false premise; wrong-script comparison. `207e041` holds. (A11)
- **Phases 0-4 re-execution** — already closed; re-running discards a FINAL record.
- **L1 `--ref` bare-SHA support** — a codeload.github.com limitation, not an installer bug;
  docs already scope `--ref` to branch/tag. (A4)

## 6. Honest status of this session

- Front half: **complete**, 13 lanes, 5 findings, all key claims verified at source by me.
- Back half: **not started**, and correctly so — it is gated on operator decisions (item 1).
- One sequencing violation occurred and is recorded, not hidden (SEQ-001).
- v3.0.0 is **not** releasable today. Saying otherwise would be the exact defect class
  this plugin exists to prevent: a claim stated above its proof level.
