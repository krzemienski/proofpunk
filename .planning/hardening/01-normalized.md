# 01-normalized — proofpunk-agent v1.0 build prompt (canonical form)

Source: `.planning/hardening/00-draft.md` (62,932 bytes). Authority: Part I spec embedded in source; this normalization preserves phase/scope/stop/evidence semantics in canonical fields.

<title>
proofpunk-agent v1.0 — terminal-native mission-control TUI for Claude Agent SDK sessions (repo `krzemienski/proofpunk-agent`, MIT, Python 3.10+, Textual, claude-agent-sdk pinned at Phase 0)
</title>

<phases count="12">
- P0  register-resolution: PHASE0.md resolves all 12 ⚠ rows (§12) via installed SDK source + real smoke session; pin SDK version; every negative verdict engages its §8.2 degradation row. 1 file. Gate: verification + operator approval.
- P1  scaffold: pyproject, __init__, __main__ (§8.3 CLI), app.py (§6.1 chrome + §6.2 bindings + Screen 1 empty state), theme.py (20 palettes, fallback, degradation ladder). 5 files. Verify: real PTY boot, `t` cycles, resize notice <100×28.
- P2  state core: events.py, reducers/__init__, tree.py (§4 attribution order), ledger.py. 4 files. Verify: replay-determinism rail.
- P3  bridges: bridge/sdk.py (single-owner client, command queue, backpressure §8.2 r4, error map §8.4), bridge/evidence.py (fresh_evidence.py runner + ≤1s watcher; plugin-root resolution contract — root iff skills/ + themes/, glob script under it, --help exit 0; cwd pinned to product repo). 2 files. Verify: smoke session streams events; init-run lands in product repo.
- P4  reducers: hooks.py (two lanes, provenance badge), metrics.py (reservoirs, 5 budget metrics). 2 files. Verify: replay rail.
- P5  Screen 1: session.py + scenario_session.py. 2 files. Verify §7 S1 obligations (subagent spawn, mid-delta capture, tool card, interrupt, permission modal).
- P6  Screens 2+3 parallel lanes: (tools.py + scenario_tools.py) ∥ (hooks.py + scenario_hooks.py). 4 files. Verify both §7 obligation sets.
- P7  Screen 4: evidence.py, plans/session.md, scenario_evidence.py. 3 files. Verify self-hosting (init via UI, ≥3 captures, blocked-then-clean seal, validate in-app).
- P8  Screen 5: performance.py, perf/driver.py. 2 files. Verify 5 metrics live + `b` export lands.
- P9  fuzz + keyboard traversal: fuzz_paste/keys/resize + traversal script. ≤5 files. Verify invariants under real-PTY storms (§10.1 cat 4–5).
- P10 evidence program (execution-heavy): per-screen obligation runs, 30-min Performance Budget run, terminal matrix (≥3 emulators incl. 256-color + SSH), self-hosted run last; new files only under validation/plans/ (≤5 per sub-phase).
- P11 docs and release: LICENSE (MIT), README.md, RELEASE.md (verdict table, every §7 + §10.3 obligation → verdict + artifact). 3 files.
</phases>

<scope>
<touch>
- everything under the new repo `krzemienski/proofpunk-agent/`
- local venv, pinned dependency installs
- real SDK sessions within default --max-budget
- the resolved fresh_evidence.py (invocation only)
- sub-PTYs; git init/commit locally in the new repo
</touch>
<no_touch>
- the Proofpunk checkout/plugin in ANY form (read-only consumer; violations reported, never patched)
- product code: no mocks/stubs/test-doubles; tests_dev/ is contributor tooling, never evidence, never imported by product
- permission prompts: never auto-allow
- failed secret scans: never silently overridden (override is itself a recorded artifact)
- remotes/publishing/budget-cap/deletion of evidence runs — consent-gated (not auto)
</no_touch>
</scope>

<stop_conditions>
- Any UNVERIFIED or BLOCKED row in any gate or RELEASE.md → stop, report honestly; never pad a gate
- Phase gate FAIL → fix real system, re-run from the failed gate's prerequisites; never advance on FAIL
- Prior-phase regression failure at a phase gate → blocks advancement until fixed
- Missing Proofpunk plugin root (no candidate with skills/ + themes/) → stop and report; no substitute doctrine
- Budget cap or evidence-run deletion → requires explicit operator consent first
</stop_conditions>

<evidence_requirements>
- Completion evidence = fresh sealed `e2e-evidence/run-*` dirs produced via the real fresh_evidence.py subprocess (init-run → next-step → seal → validate), cwd pinned to product repo
- Per-phase freshness: each phase's Verify opens its own run; PASS citations cite only that run's artifacts; prior-run artifacts are regression context only
- Real PTY only (`script -qfc`), observe-before-act, screenshots personally read after capture
- Every cited artifact non-empty (>0 bytes) and in a sealed run; empty/missing citation = release-gate FAIL
- Performance numbers only from exported metrics JSON read back from disk (non-empty); live display is not evidence
- Verdict vocabulary: PASS/FAIL/BLOCKED/UNVERIFIED with full-path citations
</evidence_requirements>
