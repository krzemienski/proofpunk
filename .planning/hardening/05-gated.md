# 05-gated — proofpunk-agent v1.0 (loop-6 revision; loops 2–5 findings + drill-sync advisories addressed; barrier = PROPOSED delta, agent RECOMMENDS approval — awaiting explicit operator token)

Loop-6 changes (loop-5 findings + two drill-sync advisories): trust drills DISCRIMINATING with BARRIER SYNCHRONIZATION — the INVOCATION BARRIER is a PROPOSED SPEC DELTA; the agent RECOMMENDS APPROVAL (rationale in consensus-verdict.md) but no approval is recorded and none is implied — drills 6a–6c remain CONDITIONAL/BLOCKED until an explicit operator token; proposed accounting: barrier in P3's bridge/evidence.py (no new file), `B` binding in P1's app.py help stub, HUD held-state render, default-off, README docs in P11 (its owning phase), validation folded into VG-P3; if approved: refreeze, re-slice P1/P3, RE-RUN VG-P1→VG-P2→VG-P3 (regression rail) before later phases; harness-tracing alternatives rejected on record (exec-entry breakpoints too late; no symbols in release builds); canary no-marker rule; SIGSTOP failed-resume drill ends with SIGKILL + reap re-assert; VG-P6M 4-replay protocol (a/b × merged/pristine); VG-P8 burst held within offered-load envelope (overload owned by VG-P3); timeout-ladder EXCEPT-VG-P8 clause in both copies; manifest sequence pinned a1..a5, b, c1..c4, d (G-15 for more). Earlier loops: trust invariant T1–T5, product-guard refusal owner, before-seal bridge drill, expected-refusal row, 12-slot VG-P3 template, per-extension min-sizes, init-run-first lifecycle, four-state verdict rows, VG-P6M merge gate, registration-only checkpoint_bindings.

<title>
proofpunk-agent v1.0 — gated build plan. Authority: Part I (in 00-draft) > 04-remediated > this file.
</title>

<phases count="13">

- P0 register-resolution: PHASE0.md resolves all 12 ⚠ rows via installed SDK source + real smoke session; pin SDK; degradation decisions; records operator-blessed plugin root + framed digest, `--max-budget` default. 1 file.

<validation_gate id="VG-P0" blocking="true" phase="P0">
  <prerequisites>Python 3.10+ venv; claude-agent-sdk importable; operator has explicitly blessed the plugin root path for this build (first-bind trust — no silent discovery)</prerequisites>
  <execute>init-run FIRST; then read SDK types.py/client.py/changelog; one real smoke session with Proofpunk loaded; write PHASE0.md as a next-step artifact inside the run; compute the framed digest (defined in plugin_root_resolution) over the blessed root; seal; validate</execute>
  <evidence>
    <type>log</type>
    <path_template>e2e-evidence/run-p0-{nn}/{seq}-phase0.md</path_template>
    <min_size_bytes>256</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>PHASE0.md inside the sealed run shows 12 rows each `| item | PASS/FAIL/BLOCKED/UNVERIFIED | <run-id>/<artifact> |` (four-state, full citation); pin line present; plugin root + FRAMED DIGEST (the same construction VG-P3 re-verifies) + operator blessing line; budget default; validate output artifact cited in the verdict row</assertion>
  </evidence>
  <review>Read PHASE0.md from disk; spot-verify 3 cited file:line pairs against installed SDK source; recompute the framed digest independently and compare</review>
  <verdict>Row format `| obligation | PASS/FAIL/BLOCKED/UNVERIFIED | run-id/artifact |`; PASS → P1; root mismatch → BLOCKED</verdict>
  <mock_guard>No synthetic SDK source; no fabricated citations — BLOCKED if unverifiable</mock_guard>
</validation_gate>

- P1 scaffold: pyproject, __init__, __main__, app.py (chrome, bindings incl. help stub + n/w tooltip, placeholder screen), theme.py. 5 files.

<validation_gate id="VG-P1" blocking="true" phase="P1">
  <prerequisites>VG-P0 PASS; venv; deps installed</prerequisites>
  <execute>init-run FIRST; then boot via the PTY driver's inline platform detection (BSD vs Linux `script` form chosen at runtime — no external README dependency at this phase); boot at ≥100×28; `t`×3; resize below 100×28; `?`; every capture exported as a next-step artifact inside the run; seal; validate</execute>
  <evidence>
    <type>screenshot</type>
    <path_template>e2e-evidence/run-p1-{nn}/{seq}-{boot,theme,resize,help}.png</path_template>
    <min_size_bytes>2048</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Four PNG captures (PNG magic bytes verified) produced inside the run; chrome per §6.1; three distinct palettes; blocking resize notice below 100×28; help lists §6.2 bindings; validate output cited</assertion>
  </evidence>
  <review>Personally read all four PNGs; `file` each to confirm PNG magic; assert palette names differ</review>
  <verdict>Row format four-state + run-id/artifact; PASS → P2</verdict>
  <mock_guard>Real PTY captures only; PNG export from Textual, not PIL mocks</mock_guard>
</validation_gate>

- P2 state core: events.py, reducers/__init__, tree.py, ledger.py + tests_dev/replay_rail.py (named contributor rail — G-14). 4 product files + 1 named rail file.

<validation_gate id="VG-P2" blocking="true" phase="P2">
  <prerequisites>VG-P1 PASS</prerequisites>
  <execute>init-run FIRST; then run the replay rail twice over the recorded P1-boot event log, each pass written as a next-step artifact inside the run; seal; validate</execute>
  <evidence>
    <type>diff</type>
    <path_template>e2e-evidence/run-p2-{nn}/{seq}-rail-pass{1,2}.log</path_template>
    <min_size_bytes>128</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Both rail artifacts produced inside the sealed run; diff empty; REGRESSION label; tree reducer applies §4 order (asserted in rail output); validate output cited</assertion>
  </evidence>
  <review>Diff the two artifacts on disk; read the empty-diff result</review>
  <verdict>Row format four-state; PASS → P3</verdict>
  <mock_guard>Rail replays a REAL recorded log; synthetic events forbidden</mock_guard>
</validation_gate>

- P3 bridges: bridge/sdk.py (own asyncio-task receive loop; crash backoff 1s/2s/4s max 3 → freeze + resume-session; orphan reap via SDK teardown; queued-command replay/drop decision events; 10k queue cap, coalesce deltas, drop-oldest deltas, control events never dropped) + bridge/evidence.py (explicit argv array with the absolute pinned script path resolved once at startup — no glob at invoke; scrubbed env = PATH=/usr/bin:/bin, HOME=repo/.evidence-home, LANG=C.UTF-8 only; watcher confined realpath + symlink-reject + name-sanitize). 2 files.

<validation_gate id="VG-P3" blocking="true" phase="P3">
  <prerequisites>VG-P2 PASS; trust invariant satisfied at invocation (see plugin_root_resolution — framed digest + fail-closed swap closure)</prerequisites>
  <execute>init-run FIRST; then (1) real smoke session through the bridge; (2) crash drill: kill the SDK child mid-session → backoff ×3 → freeze + resume offered → resume succeeds → orphan reaped (pgrep = 0 after exit); (2b) failed-resume drill: induce resume-unavailability through the REAL system (SIGSTOP the CLI child so the socket stays half-open and resume attempts time out) → backoff ×3 exhausts → FROZEN give-up event, no zombie loop — the drill ENDS with SIGKILL of the stopped child and the reap check re-run (pgrep = 0; no stopped orphan survives); (3) queue-fate drill: enqueue Interrupt during the crash window → decision event carrying `replayed|dropped` XOR AND a reason field; (4) mixed delta+control burst past the 10k cap through the real bridge; (5) invocation-capture drill: argv array, argv[0] identity, execfd provenance line, child env; (6) trust adversarial drills per the plugin_root_resolution INVARIANT, synchronized via the INVOCATION BARRIER — CONDITIONAL: drills (6a) leaf swap, (6b) ancestor-dir swap, (6c) in-tree symlink REQUIRE the SPEC DELTA (barrier) to be approved by an EXPLICIT operator token; if rejected or untokened, these drills are BLOCKED pending the operator's chosen alternative; (7) init-run-dir via bridge — every drill's log lands as a next-step artifact inside the run; seal; validate</execute>
  <evidence>
    <type>log</type>
    <path_template>e2e-evidence/run-p3-{nn}/{seq}-{smoke,crash,giveup,resume,reap,queuefate,burst,invocation,trust-leaf,trust-ancestor,trust-symlink,rundir}.log</path_template>
    <min_size_bytes>128</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Twelve logs inside the sealed run, one per named drill slot: smoke events in log; crash log shows 3 backoffs then freeze; giveup log shows the FROZEN give-up event after backoff exhaustion (no zombie loop, SIGSTOP child SIGKILLed and pgrep = 0 re-asserted at drill end); resume log shows session resumed same id; reap log asserts pgrep count = 0; queuefate log shows replayed|dropped XOR with reason; burst log shows ≥1 BACKPRESSURE_DROP AND dropped CONTROL count = 0 (mixed stream — non-vacuous); invocation log shows argv array with argv[0] = absolute pinned path, an execfd provenance line (hashed bytes = executed bytes), exactly three scrubbed env vars; EACH trust drill (leaf, ancestor, symlink) is DISCRIMINATING and BARRIER-SYNCHRONIZED — PASS requires all four: (i) refusal event logged, (ii) the canary marker file does NOT exist after the drill (zero execution of planted bytes — a TOCTOU-blind impl that re-resolves the path would exec the canary and leave the marker → FAIL), (iii) the drill log proves the barrier protocol in order: BARRIER_ARMED (operator) → INVOCATION_HELD (runner parked post-digest, pre-exec) → swap applied (harness fs-op logged) → BARRIER_RELEASED → exec attempt → refusal — with timestamps; a mutation outside the held window voids the drill (re-run, never count), (iv) the held state is observable in the runner log (INVOCATION_HELD … BARRIER_RELEASED bracket); rundir listing shows e2e-evidence/ inside repo only. Every SDK launch line shows cwd = repo root AND --project = repo root</assertion>
  </evidence>
  <review>Read all twelve logs from disk; run the pgrep orphan check yourself; verify argv[0], the execfd provenance line, and env on the invocation log; for each trust drill verify the full barrier bracket (BARRIER_ARMED → INVOCATION_HELD → swap → BARRIER_RELEASED → refusal) with timestamps and the absent canary marker; verify --project on launch lines</review>
  <verdict>Row format four-state; PASS → P4</verdict>
  <mock_guard>No stubbed SDK client; kill drill uses the REAL child process; no fake run dirs</mock_guard>
</validation_gate>

- P4 reducers: hooks.py, metrics.py. 2 files.

<validation_gate id="VG-P4" blocking="true" phase="P4">
  <prerequisites>VG-P3 PASS</prerequisites>
  <execute>init-run FIRST; then replay the P3 smoke log through hooks+metrics reducers twice and export metrics JSON, all written as next-step artifacts inside the run; seal; validate</execute>
  <evidence>
    <type>diff</type>
    <path_template>e2e-evidence/run-p4-{nn}/{seq}-{rail1,rail2,metrics}.log|.json</path_template>
    <min_size_bytes>256</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Rail artifacts identical; metrics JSON parses with all five budget fields; provenance-badge state machine covered; validate output cited</assertion>
  </evidence>
  <review>Parse metrics JSON from disk; diff rails</review>
  <verdict>Row format four-state; PASS → P5</verdict>
  <mock_guard>Real recorded log only</mock_guard>
</validation_gate>

- P5 Screen 1: screens/session.py (replaces P1 placeholder — G-31; contains inspector widget, ALL global modal widgets, AND the rewind-confirm wiring as classes within session.py — single file, sole modal owner) + scenario_session.py + validation/e2e/README.md (BSD/Linux driver flag map + timeout/resync conventions — the portability reference later gates cite; VG-P1 used inline detection until this lands). 3 files; phase cap intact.

<validation_gate id="VG-P5" blocking="true" phase="P5">
  <prerequisites>VG-P4 PASS</prerequisites>
  <execute>init-run FIRST; then real session: stream; expand tool card; `i` interrupt; permission prompt answered manually; `?`/`q` overlays; escape-filter drill (CSI/OSC payload tool result renders inert in stream and Inspector); symlink drill (pre-created symlinked artifact path → watcher rejects, logged); every capture/log lands as a next-step artifact inside the run; seal; validate</execute>
  <evidence>
    <type>screenshot</type>
    <path_template>e2e-evidence/run-p5-{nn}/{seq}-{streaming,toolcard,modal,escfilter}.png + {seq}-interrupt.log + {seq}-symlink-reject.log</path_template>
    <min_size_bytes>2048</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>PNG captures (magic verified) inside the run show spinner mid-delta, expanded card, modal; interrupt log round-trips interrupting…→terminal reason; modal gates tool (executed only after allow) and owns focus during `i` (queued); escape-filter capture shows payload rendered inert; symlink-reject log shows the rejected path; validate output cited</assertion>
  </evidence>
  <review>Read every capture + log from disk; confirm escape payload visible as text, not executed</review>
  <verdict>Row format four-state; PASS → P6</verdict>
  <mock_guard>Real session; no scripted responses; human-only allow</mock_guard>
</validation_gate>

- P6 Screens 2+3 parallel lanes on separate app instances AND separate SDK/evidence sessions (workspace-isolated): lane A tools.py + scenario_tools.py; lane B hooks.py + scenario_hooks.py + checkpoint_bindings.py (pure key-binding REGISTRATION only — binds c/r keys and invokes the P5-owned modal/rewind APIs from session.py; owns no modal or confirm wiring itself). 5 files total across both lanes.

<validation_gate id="VG-P6A" blocking="true" phase="P6-laneA">
  <prerequisites>VG-P5 PASS; lane A runs in its own repo workspace with its own SDK + evidence session</prerequisites>
  <execute>init-run FIRST (lane-A workspace); then real session ≥5 distinct tools incl. one failure; filters; `f` jump; full-output modal; `x` export; subagent spawn for tree evidence; all artifacts via next-step inside the lane-A run; seal; validate</execute>
  <evidence>
    <type>log</type>
    <path_template>e2e-evidence/run-p6a-{nn}/{seq}-{ledger.jsonl,tree.png,failure.png}</path_template>
    <min_size_bytes>2048</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>JSONL row count == ledger row count (both read from disk); tree PNG shows nested attribution per §4 (no unlabeled timing guesses); failure row error-colored; validate output cited</assertion>
  </evidence>
  <review>wc -l JSONL; read tree capture; verify attribution labels</review>
  <verdict>Row format four-state; PASS (A) → merge gate</verdict>
  <mock_guard>Real tools; app's own export</mock_guard>
</validation_gate>

<validation_gate id="VG-P6B" blocking="true" phase="P6-laneB">
  <prerequisites>VG-P5 PASS; lane B in its own workspace/session</prerequisites>
  <execute>init-run FIRST (lane-B workspace); then real session with Proofpunk loaded; hook lane events; one block decision; provenance badge; checkpoint/rewind keys registered via checkpoint_bindings.py driving P5-owned modals (or tooltip-disabled per PHASE0 row 12); all artifacts via next-step inside the lane-B run; seal; validate</execute>
  <evidence>
    <type>screenshot</type>
    <path_template>e2e-evidence/run-p6b-{nn}/{seq}-{hookblock,badge,ckeys}.png</path_template>
    <min_size_bytes>2048</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Block decision rendered + pinned; badge honest (in-band or source:logs — if logs, tailed file read to confirm real fallback); checkpoint keys match PHASE0 row 12 AND route through session.py modal APIs (no local confirm wiring); MCP health row; validate output cited</assertion>
  </evidence>
  <review>Read captures; read the tailed log when badge=logs</review>
  <verdict>Row format four-state; PASS (B) → merge gate</verdict>
  <mock_guard>No synthesized HookEventMessage</mock_guard>
</validation_gate>

- P6M lane merge (no new files): reconcile lane A and lane B workspaces into the main workspace.

<validation_gate id="VG-P6M" blocking="true" phase="P6-merge">
  <prerequisites>VG-P6A PASS AND VG-P6B PASS</prerequisites>
  <execute>init-run FIRST (main workspace); then merge lane A and lane B source trees into the main workspace; for EACH lane, replay the lane's recorded event log TWICE — once through the MERGED reducer stack and once through a PRISTINE single-lane checkout (the lane's own branch, freshly checked out into a scratch dir) — producing four replay outputs (a-merged, a-pristine, b-merged, b-pristine); the divergence report diffs merged-vs-pristine per lane; all artifacts via next-step inside the run; seal; validate</execute>
  <evidence>
    <type>diff</type>
    <path_template>e2e-evidence/run-p6m-{nn}/{seq}-{merge,a-merged,a-pristine,b-merged,b-pristine,divergence}.log</path_template>
    <min_size_bytes>128</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Merged tree imports clean (both lanes' screens mount); BOTH baselines are computed fresh inside THIS gate: each lane's recorded event log is replayed twice — once through the MERGED reducer stack and once through a PRISTINE single-lane checkout (the lane's own branch) — and the divergence report diffs those two fresh replay outputs per lane (merged-vs-pristine, never self-compared, no dependence on lane-gate artifacts); divergence must be empty; no lane overwrote the other's files (merge manifest shows per-file provenance); validate output cited</assertion>
  </evidence>
  <review>Read the divergence report from disk; verify per-file provenance manifest; import-check the merged tree yourself</review>
  <verdict>Row format four-state; PASS → P7; divergence = FAIL → reconcile lanes, re-run THIS gate only</verdict>
  <mock_guard>Replays use the lanes' REAL recorded logs; no hand-merged fake state</mock_guard>
</validation_gate>

- P7 Screen 4: screens/evidence.py, validation/plans/session.md, scenario_evidence.py. 3 files.

<validation_gate id="VG-P7" blocking="true" phase="P7" runs="1-sealed-plus-1-preserved">
  <prerequisites>VG-P6M PASS</prerequisites>
  <execute>RUN 1 — blocked-attempt (preserved, never sealed): init-run; ≥3 `g` captures; inject canary secret; attempt seal → the PRODUCT's own pre-seal secret-scan guard (the refusal owner — fresh_evidence.py's seal writes but never scans; the product wrapper refuses to invoke it on a dirty scan and records the refusal) blocks the attempt; refusal + scan findings recorded as next-step artifacts; run directory PRESERVED unsealed. RUN 2 — clean (sealed): init-run; ≥3 `g` captures; bridge drill FIRST (kill the SDK bridge mid-session → bridge-down badge, seal/next-step disabled, watcher-heartbeat death logged, resume reconciles — all captured BEFORE sealing); then capture run-1's refusal INTO RUN 2 as run-2's OWN fresh artifacts (in-app screenshot of the Screen 4 refusal state + re-read of run-1's refusal log recorded at capture time — fresh mtimes, not copies); seal SUCCEEDS; validate covers run 2 (the tool validates the ACTIVE run only). Multi-run exemption (restated): exactly ONE sealed run (run 2) plus ONE preserved blocked-attempt run (run 1)</execute>
  <evidence>
    <type>log</type>
    <path_template>e2e-evidence/run-p7a-{nn}/{seq}-blocked.log|scan.md (preserved) AND run-p7b-{nn}/{seq}-clean.md|refusal.png|bridgedown.log (sealed)</path_template>
    <min_size_bytes>per-extension: .png→2048, .log/.md→256</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Run 1: product guard refused seal + finding file:line recorded + preserved (no seal marker). Run 2: sealed + validate passes over run-2's corpus, which CONTAINS run-2's fresh refusal-documenting captures (refusal .png + re-read log, mtime-fresh in run 2). Bridge-down: badge shown, actions disabled (captured BEFORE seal), reconciliation logged. Screen 4 renders artifact METADATA only — raw-untrusted-bytes attempt logged and shown inert (G-08)</assertion>
  </evidence>
  <review>Read both run dirs from disk; confirm run 1 has NO seal marker; confirm run 2's corpus contains its own fresh refusal-documenting captures (screenshot + re-read log, both mtime ≥ run-2 start); confirm metadata-only render</review>
  <verdict>Row format four-state: run-2 row (PASS only if sealed+validated), blocked-attempt row (PASS means the guard refused AS DESIGNED — an expected-refusal row, distinct from a gate BLOCKED), bridge row; all PASS → P8</verdict>
  <mock_guard>Real fresh_evidence lifecycle; no fabricated runs; no sealing of the blocked run</mock_guard>
</validation_gate>

- P8 Screen 5: screens/performance.py, validation/perf/driver.py. 2 files.

<validation_gate id="VG-P8" blocking="true" phase="P8">
  <prerequisites>VG-P7 PASS</prerequisites>
  <execute>init-run FIRST; then a ≥30-minute ACTIVE real session (driver-enforced streaming/tool traffic — idle time does not count); one induced burst (parallel subagent fan-out) held WITHIN the offered-load envelope — the driver caps total sustained event rate below the 10k coalesce threshold for the entire run INCLUDING the burst window (burst = sub-cap spike; beyond-cap overload is owned solely by VG-P3's burst drill); `b` export at 5-minute intervals → seven exports t0..t30, each a next-step artifact inside the run; seal; validate</execute>
  <evidence>
    <type>api_response</type>
    <path_template>e2e-evidence/run-p8-{nn}/{seq}-metrics-{t0,t5,t10,t15,t20,t25,t30}.json</path_template>
    <min_size_bytes>256</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Seven exports inside the sealed run, each parses; from the FILES: frame p95 ≤16ms; event→paint p95 ≤120ms; sustained ≥1500 tok/s; dropped stream events = 0 AT THE DRIVER'S OFFERED LOAD (driver caps sustained input below the 10k coalesce threshold — beyond-threshold overload behavior is owned and gated by VG-P3's burst drill, so the pair is satisfiable and non-vacuous); RSS growth t30−t0 ≤10MB; startup→paint ≤2000ms; budget-agg spend within cap in t30. Stall rule: any permission/rate-limit/driver-loop stall >5min = BLOCKED (not hang); ≤2 infra-flake re-runs as fresh sealed runs. Any budget breach = FAIL (fix product)</assertion>
  </evidence>
  <review>Parse all seven JSONs from disk; recompute every budget incl. RSS delta; never cite dashboard</review>
  <verdict>Row format four-state; PASS → P9</verdict>
  <mock_guard>Real instrumentation only; 30 active minutes enforced by driver traffic log</mock_guard>
</validation_gate>

- P9 fuzz + traversal: fuzz_paste.py, fuzz_keys.py, fuzz_resize.py, traversal script. ≤5 files (README landed in P5).

<validation_gate id="VG-P9" blocking="true" phase="P9">
  <prerequisites>VG-P8 PASS; driver timeouts configured from the P5 README map</prerequisites>
  <execute>init-run FIRST; then paste bomb; rapid keys during streaming; resize storm mid-tool-call; keyboard traversal (Tab/1–5/[/]/Space/?/q); modal storm — flood `a`/`A` at a pending permission modal; every invariant log/capture via next-step inside the run; seal; validate</execute>
  <evidence>
    <type>log</type>
    <path_template>e2e-evidence/run-p9-{nn}/{seq}-{paste,keys,resize,traverse,modalstorm}.log|.png</path_template>
    <min_size_bytes>per-extension: .log→128, .png→2048</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Invariants hold (alive, log consistent, no focus trap); modal STILL pending after `a`/`A` flood — never auto-approved; no wrapper death; SIGWINCH resync verified; validate output cited</assertion>
  </evidence>
  <review>Read invariant logs + modal-storm capture from disk</review>
  <verdict>Row format four-state; PASS → P10</verdict>
  <mock_guard>Fuzz drives the REAL PTY; corpus bans wrapper-kill signals (enforced by corpus generator assertion)</mock_guard>
</validation_gate>

- P10 evidence program — sub-phases each independently blockable; one sealed run per unit; matrix cells EXACTLY c1..c4 (≥3 emulators incl. one 256-color and one SSH — add cells only by the G-15 overflow rule) with ONE sealed run PER CELL: (a) S1–S5 obligation runs [a1..a5, one run per screen]; (b) 30-min perf [b]; (c) terminal matrix [c1..c4]; (d) self-hosted [d]. NEW FILES beyond the ≤10 cap = stop and open a new phase with operator approval (G-15, binding). SSH cell: operator consents via explicit target-host argument recorded as an audit artifact BEFORE any connection; denial BLOCKS cell (c) only.

<validation_gate id="VG-P10" blocking="true" phase="P10" runs="per-unit-per-cell">
  <prerequisites>VG-P9 PASS; per-unit: (c4) SSH consent artifact (target host + operator ack) exists BEFORE connect</prerequisites>
  <execute>Per unit and per matrix cell: init-run FIRST → work with artifacts via next-step inside that run → seal → validate. Units and cells run serially; each is independently gated. Multi-run exemption: one sealed run per unit AND per matrix cell, itemized (a1,a2,a3,a4,a5 per screen; b; c1,c2,c3,c4; d)</execute>
  <evidence>
    <type>screenshot</type>
    <path_template>e2e-evidence/run-p10-{unit-or-cell}-{nn}/{seq}-{slug}.png|.json|.md</path_template>
    <min_size_bytes>per-extension: .png→2048, .json→256, .log/.md→128</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>Every §7 obligation row has verdict + same-run artifact; budgets ✔ across (b) exports; 256/16-color degradation captured in (c3)/(c1-2); self-hosted sealed+validated through UI; ZERO cross-unit cross-cell capture reuse — the checker artifact enumerates EVERY run id (a1..a5, b, c1..c4, d) and asserts pairwise-disjoint artifact sets; per-unit retry ≤2 infra re-runs, stall = BLOCKED unit only; SSH consent artifact timestamp precedes connection timestamp</assertion>
  </evidence>
  <review>Read every verdict row; recompute budgets from files; verify per-cell run-id disjointness yourself; view one capture per tier</review>
  <verdict>Row per unit/cell; all PASS → P11; unit FAIL → re-run that unit only</verdict>
  <mock_guard>No replayed events as evidence; SSH renders LOCAL product only</mock_guard>
</validation_gate>

- P11 docs and release: LICENSE, README.md, RELEASE.md. 3 files.

<validation_gate id="VG-P11" blocking="true" phase="P11">
  <prerequisites>VG-P10 all units/cells PASS</prerequisites>
  <execute>init-run FIRST; then write LICENSE (full MIT), README, RELEASE.md (only P10/P11-run artifacts) as next-step artifacts; full-artifact secret scan across every sealed run (all types incl. typescripts/PNGs/SSH captures); ANY finding = release FAIL until remediated AND re-scanned; git commits land only after this scan passes; seal; validate</execute>
  <evidence>
    <type>log</type>
    <path_template>e2e-evidence/run-p11-{nn}/{seq}-{scan,release}.md|.log</path_template>
    <min_size_bytes>256</min_size_bytes>
    <freshness>same_run</freshness>
    <assertion>RELEASE.md covers every §7+§10.3 obligation; every cited artifact integrity-checked (PNG magic/JSON parse/log ≥128B) by an in-run checker whose output is itself an artifact; scan clean; zero UNVERIFIED/BLOCKED rows</assertion>
  </evidence>
  <review>Spot-verify 5 cited artifacts personally; read scan report</review>
  <verdict>Row format four-state; PASS → release-ready</verdict>
  <mock_guard>No verdict without personally-driven artifact</mock_guard>
</validation_gate>

</phases>

<plugin_root_resolution precedence="binding">
1. explicit `--proofpunk-path` (operator-provided at invocation)
2. `$PROOFPUNK_HOME`
3. dev checkout sibling `plugins/proofpunk/`
4. versioned cache `~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/<version>/` (semver-highest first, deterministic sort)
5. marketplace `~/.claude/plugins/marketplaces/proofpunk-marketplace/plugins/proofpunk/`

First match wins. Candidate root valid iff: `skills/` + `themes/` + `.claude-plugin/plugin.json` naming `proofpunk`, AND the resolved path contains no symlink component (realpath == lexical path), AND — first bind only — the OPERATOR explicitly blesses the resolved path (interactive confirm; blessing recorded in PHASE0.md). Trust anchor = operator blessing, not tree contents.

Trust invariant (binding on the implementation; mechanism is implementation-owned — the plan pins the CLOSURE PROPERTIES and the adversarial drills that prove them, not the syscalls): every evidence invocation must satisfy, on BOTH supported platforms (Darwin and Linux) — (T1) executed bytes = hashed bytes: the exact file content covered by the recorded digest is the content executed, with no pathname re-resolution between hash and exec (fd-passing or equivalent held-descriptor execution); (T2) component-swap closure: swapping ANY component — leaf file, in-tree symlink plant, or ancestor directory rename+replant — between bind and invocation fails closed (refusal event, zero execution); (T3) single construction: the digest recorded at VG-P0 bind and re-verified at every invocation is ONE framed SHA-256 — per file, len(relative_path) ‖ relative_path ‖ len(bytes) ‖ bytes, sorted-path order, over the pinned set (every file under skills/, themes/, hooks.json, .claude-plugin/plugin.json) — computed by the same code both times; (T4) first-bind trust = operator blessing of the resolved root (interactive confirm, recorded in PHASE0.md) — tree contents are never self-trusting; (T5) fail-closed, no fallthrough: any check failure aborts the invocation; never retry an alternate candidate mid-session. PROOF obligations: VG-P0 records the blessed root + digest; VG-P3 drills (6a) leaf swap, (6b) ancestor swap, (6c) in-tree symlink — each MUST fail closed with a refusal event and no execution; the implementation (bridge/evidence.py) chooses the portable mechanism (e.g., per-component O_NOFOLLOW|O_DIRECTORY walk from an anchored fd with all component fds held, inode/dev pinning via fstat, or openat2 where available) and must pass the drills on BOTH Darwin and Linux before VG-P3 can PASS.

Drill synchronization — INVOCATION BARRIER (PROPOSED SPEC DELTA — AGENT RECOMMENDS APPROVAL; NO APPROVAL RECORDED — an explicit operator token is required to enact it): Part I is binding and conflict-report-only; this plan cannot amend it, and operator delegation of judgment does not itself constitute spec-amendment authority. The following delta is PROPOSED; the agent's reasoned RECOMMENDATION (approve) is recorded in consensus-verdict.md with the full evaluation of alternatives. Proposal: add ONE v1.0 feature — the invocation barrier on trust-sensitive evidence invocations (the operator-facing control point the trust invariant's T1/T5 require; a verified digest with fail-closed release is incomplete without an inspectable hold). Alternatives rejected on record: harness-owned tracing (an OS-level exec* breakpoint fires at exec ENTRY — after every swap opportunity, too late by construction; a debugger mid-function breakpoint needs symbol/line info a release CPython build lacks) and invariant re-scoping (would leave the planted-checkout/TOCTOU lineage ungated). Proposed accounting (within existing file lists, no cap changes): (a) barrier logic in P3's bridge/evidence.py (same file as verified-exec; NO new file); (b) `B` binding registered in P1's app.py with the help stub; (c) held state rendered in the existing Status HUD (§6.1 chrome, no new screen); (d) DEFAULT OFF — ordinary invocations byte-identical; (e) README §6.2 table documentation lands in P11 (README's owning phase); (f) validation folded into VG-P3's trust drills (no new gate). If a token of approval is given, PHASE0.md records the operator's decision verbatim and the refreeze rule executes: re-freeze the capability contract, re-slice P1 (app.py gains the `B` binding + help entry) and P3 (barrier logic in bridge/evidence.py), then RE-RUN VG-P1 → VG-P2 → VG-P3 in order (regression rail — prior-phase re-verify mandatory) before any later phase. Protocol: (S1) operator arms BEFORE the invocation; (S2) runner computes digest, emits `INVOCATION_HELD`, parks — cannot exec until released; (S3) harness applies the canary swap while provably parked; (S4) release; (S5) exec attempt → fail-closed refusal; mutation outside the held bracket voids the drill — re-run, never count. IF THE OPERATOR REJECTS: choose harness-owned tracing (accepted limitations documented) or re-scoping the trust invariant, recorded as further spec decisions.
</plugin_root_resolution>

<refreeze_rule>
A Phase 0 verdict that invalidates a design assumption: return, re-freeze, re-slice the affected phases, present the delta for operator approval before resuming. Never code around an unresolved ⚠.
</refreeze_rule>

<scope>
<touch>
- files explicitly listed per phase in `<phases>` above — nothing else (no blanket repo write)
- local venv; pinned deps
- real SDK sessions within recorded `--max-budget` (90% suspend / 100% halt — asserted in VG-P8 t30 export)
- the pinned fresh_evidence.py via verified-exec explicit argv (invocation only)
- sub-PTYs (documented BSD/Linux driver forms; escape-filtered capture); git init/commit locally — commits only AFTER VG-P11 scan passes
</touch>
<no_touch>
- the Proofpunk checkout/plugin in ANY form (read-only; violations reported)
- product code: no mocks/stubs/test-doubles; tests_dev/ = contributor tooling only
- permission prompts: never auto-allow (asserted VG-P5/P9)
- failed secret scans: never silently overridden; finding = FAIL until remediated + re-scanned
- v1.0 CEILING: no session tabs, no product replay, no remote/shared stores
- remotes/publishing/budget-raise/evidence-run deletion — explicit operator consent
</no_touch>
</scope>

<stop_conditions>
- Any UNVERIFIED/BLOCKED verdict row → stop, report honestly
- Gate FAIL → fix real system, re-run from failed gate prerequisites
- Prior-phase regression failure blocks advancement
- Timeout ladder: per-observe ≤30s; per-phase ≤60min EXCEPT VG-P8 (30 active minutes driver-enforced + up to 45min wall-clock beyond = ≤75min total, stall >5min = BLOCKED); P10 units ≤90min each; SDK connect ≤60s — expiry = BLOCKED, never hang
- Verified-exec failure (digest mismatch / symlink-open failure / missing blessing) → stop, never fall through
- Budget hard-stop (100%) → BLOCKED; consent to raise
- Wait-for-state miss inside bound → BLOCKED, not retry-storm
</stop_conditions>

<evidence_requirements>
- EVERY gate: init-run FIRST → work artifacts via next-step INSIDE the run → seal → validate; PASS predicate = four-state verdict row `| obligation | PASS/FAIL/BLOCKED/UNVERIFIED | <run-id>/<artifact> |` citing the validate output
- One sealed run per gate EXCEPT declared multi-run gates: VG-P7 (one sealed + one preserved blocked-attempt) and VG-P10 (one per unit AND per matrix cell)
- Regression rail: each gate re-runs its predecessor's verify, emitting `regression-prior-phase` in the CURRENT run; absence blocks PASS
- Artifact integrity: non-empty + type-consistent per extension — .png → PNG magic + min 2048B; .json → parses + min 256B; .log/.md → min 128B; all visual captures PNG; mixed-template gates apply the per-extension floors (VG-P10's rule generalized)
- Real PTY, observe-before-act, escape-filtered rendering (drilled VG-P5)
- Performance/budget numbers only from exported JSON read from disk (VG-P8 seven-export series)
- RELEASE.md cites only P10/P11 runs
</evidence_requirements>

<gate_manifest>
  <total_gates>14</total_gates>
  <sequence>VG-P0 → VG-P1 → VG-P2 → VG-P3 → VG-P4 → VG-P5 → VG-P6A ∥ VG-P6B → VG-P6M → VG-P7 → VG-P8 → VG-P9 → VG-P10 (units a1..a5, b, c1..c4, d — additional cells only via G-15 overflow) → VG-P11</sequence>
  <policy>All gates BLOCKING. P6 lanes parallel (separate workspaces/sessions), merged by VG-P6M before P7. P10 units/cells independently blockable. No advancement on FAIL.</policy>
  <evidence_dir>e2e-evidence/run-{phase}-{nn}/</evidence_dir>
  <regression>regression-prior-phase artifact per gate; ANY FAIL → fix real system → re-run from failed gate; never skip</regression>
  <timeout_ladder>per-observe ≤30s; per-phase ≤60min EXCEPT VG-P8 (30 active minutes driver-enforced + up to 45min wall-clock beyond = ≤75min total, stall >5min = BLOCKED); P10 units ≤90min each; SDK connect ≤60s — expiry = BLOCKED, never hang</timeout_ladder>
</gate_manifest>
