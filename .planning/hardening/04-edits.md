# 04-edits — Stage-4 remediation audit trail

Source: 01-normalized.md → 04-remediated.md. One row per finding (G-01..G-31). Format: finding_id | file_section | diff_summary | rationale.

| finding | section | edit | rationale |
|---|---|---|---|
| G-01 | P3 + new `<plugin_root_resolution>` | Added precedence chain (--proofpunk-path > $PROOFPUNK_HOME > checkout > cache > marketplace), root validity = skills/+themes/+plugin.json name=proofpunk, hash recorded + re-verified per invocation | kills planted/stub/wrong-tree binding (SEC-1+FM-5) |
| G-02 | P3 + P9 + evidence_requirements | Watcher confined realpath/symlink-reject; sanitized names; escape-filtered rendering incl. Inspector; fuzz corpus bans SIGINT/exit + modal-Approve sequences | untrusted run-dir + PTY payload trust (SEC-2) |
| G-03 | `<scope>` | v1.0 ceiling restored as no_touch; touch = per-phase file lists | scope ceiling dropped in normalization (SC-01) |
| G-04 | all GATE-* | every gate = sealed run lifecycle + verdict row citing run-id/artifacts | PASS predicate lacked sealed-run contract (ER-1) |
| G-05 | GATE-P8 | metrics JSON read from disk, parsed, budgets asserted from file | on-screen PASS (ER-2) |
| G-06 | stop_conditions | timeout ladder (30s/60min/90min/60s) → BLOCKED not hang | no abort path (FM-1) |
| G-07 | P3 bridge/sdk.py | receive loop own asyncio task; backoff 1/2/4 max3; frozen+resume; orphan reap; queue fate event | starvation + crash-path gaps (FM-2) |
| G-08 | P3 watcher + P7 Screen 4 | covered by G-02 + Screen 4 renders metadata only | ingestion display trust (SEC-3) |
| G-09 | P5/P9 + no_touch | product invariant: no automated input resolves a permission prompt; P9 asserts modal pending under storm | fuzz could Approve (SEC-4) |
| G-10 | P3 bridge/evidence.py | explicit argv, pinned absolute path, env allowlist PATH/HOME/LANG, invocation logged | glob-at-invoke + env inheritance (SEC-5) |
| G-11 | P11 | secret scan over ALL artifact types; pre-seal blocks; committed finding = release FAIL | scan coverage gap (SEC-6) |
| G-12 | P0 record + P3 wiring | budget default in PHASE0.md; HUD aggregate; 90% suspend / 100% halt | unspecified cap (SEC-7) |
| G-13 | P3 | SDK sessions cwd=repo, --project=repo, shown in header | project confinement (SEC-8) |
| G-14 | P2 | "replay harness in tests_dev (contributor rail)" naming; not product replay | v1.1 leak (SC-02) |
| G-15 | P10 | sub-phases enumerated a–d; ≤5 files each; ≤10 total; beyond = new phase | unbounded P10 (SC-03) |
| G-16 | new `<refreeze_rule>` | restored re-freeze/re-slice/delta-approval | dropped branch rule (SC-04) |
| G-17 | P1/P5/P6 ownership map | modals+inspector→P5; help stub+n/w→P1; checkpoint keys→P6; tests_dev→P2 | unowned deliverables (SC-05) |
| G-18 | P5/P6 gates | P5 = modal+interrupt+mid-delta+tool-card; subagent/tree evidence → P6 | P5 Verify breadth (SC-06) |
| G-19 | P10(c) | SSH cell = local product over operator SSH target; consent prompt; serial | remote creep (SC-07) |
| G-20 | evidence_requirements | regression-prior-phase artifact in current run; absence blocks PASS | regression unprovable (ER-3) |
| G-21 | P11 | RELEASE.md cites only P10/P11 artifacts | stale captures (ER-4) |
| G-22 | GATE-P7 | two sealed runs read back; validator report from clean run file | in-app judging (ER-5) |
| G-23 | evidence_requirements | type-consistent integrity + validate output cited | >0 bytes too weak (ER-6) |
| G-24 | GATE-P0 | standard verdict row like every gate | approval ≠ verdict (ER-7) |
| G-25 | P6/P10 + evidence_requirements | one run per gate unit; reuse = FAIL | capture reuse (ER-8) |
| G-26 | P3 | queue cap 10k; coalesce→drop-oldest deltas + BACKPRESSURE_DROP; zero control-drop asserted | unbounded queue (FM-3) |
| G-27 | P10(b) | ≤2 infra-flake re-runs fresh-sealed; stall=BLOCKED; >20% variance investigated | 30-min flake (FM-4) |
| G-28 | P5 | modal owns focus; `i` queues; no layer leak; one path at a time | interrupt/modal race (FM-6) |
| G-29 | GATE-P7 | bridge heartbeat; Screen 4 pause on death; reconcile on resume | split-brain (FM-7) |
| G-30 | P6/P9/P10 | separate app instances; driver timeouts; SIGWINCH resync; BSD/Linux flag map; serial cells | driver portability + collision (FM-8) |
| G-31 | P1/P5 | P1 placeholder vs P5 real screen; handoff documented | dual ownership (SC-08) |

No new phases added (all remediations slot into existing P0–P11 + two structural blocks). All 31 findings addressed.

## Loop-2 consensus remediations (appended per advisory)

| consensus id | edit applied in 05-gated loop-2 rewrite |
|---|---|
| SEC G-01-CRIT | operator-blessed root (TOFU eliminated); SHA-256 over pinned file-set; symlink-reject; atomic hash-then-exec (TOCTOU closed) |
| SEC NEW-HASH | algorithm + file-set + atomicity pinned in plugin_root_resolution |
| SEC NEW-ENV | scrubbed env (PATH=/usr/bin:/bin, HOME=repo/.evidence-home, LANG=C.UTF-8) + VG-P3 env-probe assertion |
| SEC NEW-SSH | consent = target-host argument recorded as audit artifact BEFORE connect; denial blocks cell (c) only |
| SEC NEW-ESC / G-02 | VG-P5 escape-filter + symlink-reject drills with PASS predicates; driver flag map moved to P5 README |
| SEC G-08 | VG-P7 metadata-only render assertion |
| SEC G-10 | VG-P3 env-probe log assertion |
| SEC G-11 | VG-P11: finding = FAIL until remediated AND re-scanned; commits only after scan passes |
| SEC G-12 | VG-P8 final-export budget-agg assertion |
| SEC G-13 | VG-P3 launch-line cwd/--project assertion |
| SC-G17/G31-H | P5 = session.py single-file ownership (modals inside session.py); README moved to P5; P6 = named checkpoint_bindings.py for checkpoint/rewind key bindings (P5 session.py stays sole modal owner) |
| SC-G15-H | overflow rule in P10 plan text: >10 files = stop, new phase + approval |
| ER-G04-CRIT | per-gate init-run→seal→validate execute steps; verdict-row PASS predicate citing validate output |
| ER-GNEW1-CRIT | explicit multi-run exemptions: VG-P7 (2 runs), VG-P10 (per-unit) |
| ER-G23-H | PNG-not-SVG captures; per-gate type-consistency assertions |
| ER-G24-H | PHASE0 rows use PASS/FAIL vocabulary |
| ADV-VGP8-CRIT | ≥30-minute ACTIVE session, seven exports t0..t30, RSS delta t30−t0 |
| FM-G07-CRIT | VG-P3 crash/resume/reap/queue-fate drills with disk assertions |
| FM-G26-H | mixed delta+control burst (non-vacuous); P3 drop-policy vs P8 zero-drop reconciled via delta-only drop class |
| FM-G27-H | P10 units independently blockable; stall = BLOCKED unit only |
| FM-G29-H | VG-P7 bridge-down: badge + disabled actions + heartbeat death + reconciliation, all asserted |
| FM-G30-H | driver flag map landed P5 (pre-P1-boot… corrected: landed in P5 file set, referenced by VG-P1); P6 separate workspaces AND SDK/evidence sessions |


## Loop-4 consensus findings -> loop-5 remediations (user-authorized continuation)

Loop-4: Scope PASS; Security FAIL (ancestor-swap CRITICAL + openat2/Darwin HIGH); Evidence FAIL (seal-never-refuses, bridge-after-seal, blocked-row semantics CRITICALs + 4 slot HIGHs); Failure FAIL (P6M baseline CRITICAL + 4 HIGHs).
| loop-4 finding | loop-5 fix in 05-gated.md |
|---|---|
| SEC verified-exec not implementable on Darwin | syscall choreography -> TRUST INVARIANT T1-T5 (closure properties, portable, mechanism implementation-owned); proven by VG-P3 fail-closed swap drills |
| SEC plain-openat ambiguity | invariant names properties, not syscalls; implementation picks per-platform mechanism |
| ER cmd_seal never refuses | refusal owner named: product pre-seal secret-scan guard (fresh_evidence.py seal writes only) |
| ER bridge drill after seal | bridge drill FIRST, captured before sealing |
| ER blocked-attempt row semantics | expected-refusal row: PASS = guard refused as designed; distinct from gate BLOCKED |
| ER/FM slot mismatches | 12 named drill slots in VG-P3 template+assertion; .png in P7; per-extension min-sizes P7/P9; exact c1..c4 both places |
| FM P6M baseline artifact mismatch | both baselines computed fresh in-gate: merged vs pristine lane-branch replay |
| FM failed-resume induction | SIGSTOP the real CLI child (socket half-open) — no stub |
| FM P8 burst vs envelope | offered-load envelope retained; driver caps sustained below 10k; overload owned by VG-P3 |
| FM manifest ladder drift | manifest synced: 45min wall-clock beyond 30 active + stall>5min=BLOCKED |
