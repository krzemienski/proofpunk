# 04-remediated — proofpunk-agent v1.0 build plan (normalized form, remediations applied)

Stage-4 output: 01-normalized.md + G-01..G-31 remediations woven in (all CRITICAL + HIGH addressed; G-31 MEDIUM addressed). Edit audit in 04-edits.md. Evidence gates injected in 05-gated.md.

<title>
proofpunk-agent v1.0 — terminal-native mission-control TUI for Claude Agent SDK sessions (repo `krzemienski/proofpunk-agent`, MIT, Python 3.10+, Textual, claude-agent-sdk pinned at Phase 0)
</title>

<phases count="12">

- P0 register-resolution: PHASE0.md resolves all 12 ⚠ rows (§12) via installed SDK source + real smoke session; pin SDK version; every negative verdict engages its §8.2 degradation row; PHASE0.md also records the resolved plugin root + content hash, the `--max-budget` default, and all degradation decisions. 1 file. GATE-P0: sealed run; PHASE0.md exists with all 12 verdict rows + citations; verdict row emitted (G-24).

- P1 scaffold: pyproject, __init__, __main__ (§8.3 CLI), app.py (§6.1 chrome + §6.2 bindings + Screen 1 empty-state placeholder + help binding stub + `n`/`w` disabled-with-tooltip), theme.py. 5 files. GATE-P1: boot capture at ≥100×28; `t`-cycle capture; resize-notice capture below 100×28.

- P2 state core: events.py, reducers/__init__, tree.py (§4 attribution), ledger.py; creates tests_dev/ with the event-log replay harness (contributor rail — NOT product replay; G-14). 4 product files (+tests_dev tree). GATE-P2: replay-determinism rail green (REGRESSION label), rail output cited in the sealed run.

- P3 bridges: bridge/sdk.py — receive loop its own asyncio task (G-07); crash backoff 1s/2s/4s max 3 then frozen + resume-session surfaced; orphan CLI reaped via SDK teardown; queued commands survive in log with explicit replay/drop decision event; queue-depth cap 10k with coalesce→drop-oldest-deltas + `BACKPRESSURE_DROP` event (G-26); SDK sessions launched cwd=repo-root + `--project` same root (G-13); budget hard-stop 90% suspend / 100% halt wired here (G-12). bridge/evidence.py — explicit argv array, absolute pinned script path resolved once at startup, env allowlist PATH/HOME/LANG (G-10); cwd pinned to product repo; watcher confined to `<repo>/e2e-evidence/run-*/` realpath + symlink reject + sanitized names (G-02); plugin-root resolution per contract below (G-01). 2 files. GATE-P3: smoke session events in log; init-run dir created inside repo; burst test with control-event drop count = 0 asserted from disk.

- P4 reducers: hooks.py (two lanes, provenance badge), metrics.py (reservoirs, 5 budget metrics). 2 files. GATE-P4: replay rail green (REGRESSION); verdict row.

- P5 Screen 1: screens/session.py (replaces the P1 placeholder — handoff per G-31; owns inspector widgets + global modals: permission/help/rewind/quit/theme-picker) + scenario_session.py. 2 files. GATE-P5: sealed run — mid-delta streaming capture; tool-card expansion capture; interrupt round-trip; permission-modal interaction never auto-allowed; modal-owns-focus sequencing applied (G-28).

- P6 Screens 2+3 parallel lanes on SEPARATE app instances (G-30): lane A tools.py + scenario_tools.py; lane B hooks.py + scenario_hooks.py; checkpoint/rewind keys land here (tooltip-disabled if Phase 0 row 12 negative — G-17). 4 files. GATE-P6: one sealed run PER lane (G-25); per-lane §7 obligation sets; subagent-spawn/tree-nesting evidence gated here (G-18).

- P7 Screen 4: screens/evidence.py, validation/plans/session.md, scenario_evidence.py. 3 files. GATE-P7: TWO sealed runs read back from disk (blocked-seal run + clean run) — validator report rendered from the clean run's validate output file (G-22); bridge-down pause/resume reconciliation exercised (G-29).

- P8 Screen 5: screens/performance.py, validation/perf/driver.py. 2 files. GATE-P8: exported metrics JSON read from disk, parsed, all five budget values asserted from file contents (G-05); snapshot export lands in run.

- P9 fuzz + keyboard traversal: fuzz_paste.py, fuzz_keys.py, fuzz_resize.py, traversal script (corpus bans wrapper-killing signals and modal-Approve sequences — G-02/G-09); per-command driver timeouts + SIGWINCH resync + BSD/Linux `script` flag map in validation/e2e/README (G-30). ≤5 files. GATE-P9: invariants hold under real-PTY storms; modal stays pending under storm asserted; no wrapper death.

- P10 evidence program — sub-phases enumerated (G-15), each ≤5 files, total new files ≤10: (a) S1–S5 obligation runs; (b) 30-min Performance Budget run (retry ≤2 on infra flake, fresh sealed run each; budget/permission stall = BLOCKED; >20% inter-run variance investigated — G-27); (c) terminal matrix — ≥3 emulators incl. one 256-color + one SSH cell (SSH = operator-provided target rendering the local product over an SSH client; consent prompt before connecting; serial cells — G-19/G-30); (d) self-hosted run last. One sealed run per gate unit; per-cell captures never reused (G-25). GATE-P10: all sub-phase verdict rows.

- P11 docs and release: LICENSE (MIT), README.md, RELEASE.md — cites ONLY P10/P11-run artifacts (G-21); every artifact passes integrity checks (PNG magic / JSON parses / log ≥128 bytes — G-23); secret scan covers ALL artifact types incl. typescripts/screenshots/SSH captures (G-11). 3 files. GATE-P11: RELEASE.md complete; any UNVERIFIED/BLOCKED → stop honestly.

</phases>

<plugin_root_resolution precedence="binding">
1. explicit `--proofpunk-path`
2. `$PROOFPUNK_HOME`
3. dev checkout sibling `plugins/proofpunk/`
4. versioned cache `~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/<version>/` (highest version first)
5. marketplace `~/.claude/plugins/marketplaces/proofpunk-marketplace/plugins/proofpunk/`

Root valid iff it contains `skills/` + `themes/` + `.claude-plugin/plugin.json` whose name field is `proofpunk`. First match in precedence order wins. Resolved root + content hash recorded in PHASE0.md, displayed at startup, re-verified (hash) before every evidence invocation. Mismatch at any point → stop and report, never guess. (G-01)
</plugin_root_resolution>

<refreeze_rule>
A Phase 0 verdict that invalidates a design assumption: return, re-freeze the capability contract, re-slice the affected phases, present the delta for operator approval before resuming. Never code around an unresolved ⚠. (G-16)
</refreeze_rule>

<scope>
<touch>
- files explicitly listed per phase in `<phases>` (P1–P11 file lists are the touch surface; no blanket repo write — G-03)
- local venv, pinned dependency installs
- real SDK sessions within the recorded `--max-budget` (90% suspend / 100% halt — G-12)
- the pinned fresh_evidence.py via explicit argv (invocation only)
- sub-PTYs (per-command timeouts; escape-filtered capture — G-02/G-30); git init/commit locally
</touch>
<no_touch>
- the Proofpunk checkout/plugin in ANY form (read-only consumer; violations reported, never patched)
- product code: no mocks/stubs/test-doubles; tests_dev/ = contributor tooling, never evidence, never imported by product
- permission prompts: never auto-allow (product invariant + fuzz invariant — G-09)
- failed secret scans: never silently overridden (override is a recorded artifact)
- v1.0 CEILING (G-03): no session tabs (`n`/`w` disabled+tooltip), no product session replay, no remote/shared stores, no v1.1/v1.2 surface
- remotes/publishing/budget-cap-raise/evidence-run deletion — explicit operator consent
</no_touch>
</scope>

<stop_conditions>
- Any UNVERIFIED or BLOCKED verdict row → stop, report honestly; never pad a gate
- Gate FAIL → fix real system, re-run from the failed gate's prerequisites; never advance on FAIL
- Prior-phase regression failure at a gate → blocks advancement until fixed
- Timeout ladder (G-06): per-observe ≤30s; per-phase ≤60min; P10 sub-phases ≤90min; SDK connect ≤60s — expiry = BLOCKED with partial artifacts sealed, never a hang
- Plugin-root resolution failure or hash mismatch at any evidence invocation → stop and report
- Budget hard-stop (100%) → BLOCKED; consent required to raise
- Missing wait-for-state match inside its bound → BLOCKED, not retry-storm
</stop_conditions>

<evidence_requirements>
- Every gate = one sealed run: init-run at gate start → next-step artifacts per obligation → seal → validate; PASS row = `| obligation | PASS|FAIL|BLOCKED|UNVERIFIED | <run-id>/<artifact> |` (G-04/G-24)
- Regression rail (G-20): each gate's re-run of the prior phase's Verify emits a `regression-prior-phase` artifact in the CURRENT run; absence blocks PASS
- Per-run freshness (G-25): one sealed run per gate unit; cross-lane/cross-cell capture reuse = gate FAIL
- Artifact integrity (G-23): non-empty + type-consistent (PNG magic / JSON parses / log ≥128 bytes) + validate output cited
- Real PTY only, observe-before-act inside the timeout ladder; screenshots personally read after capture; captured output rendered escape-filtered (G-02)
- Performance numbers only from exported metrics JSON read from disk (G-05); live display never cited
- RELEASE.md freshness (G-21): only P10/P11-run artifacts; verdict vocabulary PASS/FAIL/BLOCKED/UNVERIFIED with full-path citations
</evidence_requirements>
