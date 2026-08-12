# Proofpunk Skills — Measured Improvement Report (Round 2, 2026-08-12)

Basis: the aperant-tui build (krzemienski/aperant-tui), where the proofpunk
skills ran the whole delivery. Every improvement below cites the defect or
false-result that measured the gap. Eleven gate-caught defects (D1–D11) and
seven harness failures fed this round.

## Improvements (6)

| # | Skill | Change | Measured basis |
|---|-------|--------|----------------|
| 1 | end-user-testing | Transport envelope ≠ assertion (`ok:true` ≠ `result.matched`); three-facet proof (screen + disk + logs); verdict numbers must come from sealed artifacts | D8 (false-green waits); VALIDATION doc drift 1,807-vs-275 caught by consistency audit |
| 2 | functional-validation | TTY/TUI target rules: `script -qfc` not pipes (D7), runtime-floor probes (Node ≥22 / Promise.withResolvers), daemon PATH inheritance, 300 s cold-boot budgets | Two zero-app gate runs; stale-daemon withResolvers failures; 120 s boot timeout on cold cache |
| 3 | root-cause-debugging | Verify contracts against emitters not names (D5: 'task-started' never existed); typecheck-green ≠ correct after SDK majors (D11: v7 usage rename → silent zeros); ESM/`__dirname` stub trap (D6) | Three defects whose common shape was "compiles, assumed, wrong" |
| 4 | cook | Never mutate a running driver (mid-run edit corruption); one driver per mutable target (double-launch cross-contamination of disk assertions); push after every verified unit + harness in `tools/` | Corrupted gate run; RESUME check passing on the wrong run's file; two /tmp wipes costing full reconstructions |
| 5 | **tui-testing (NEW)** | Full TUI proof discipline: observe-then-act, matched waits, three facets, TTY guards, pixel proof for visual claims, per-run secret scans, harness-in-repo | Codifies all eleven defects + the agent-tty driving manual that emerged from the aperant gates |
| 6 | marketplace/plugin manifests | 18 → 19 skills; version 1.8.1 → 1.9.0 | registration of #5 |

## Defect inventory that fed this round (all gate-caught, all fixed)

D1 clipped panel titles · D2 overlay bleed-through · D3 burst-type mount
race · D4 stale keybinding closures · D5 phantom event contract ·
D6 `__dirname` under ESM · D7 pipe vs TTY guard · D8 envelope ok≠match ·
D9 fixture data-dir mismatch (.aperant vs .auto-claude) · D10 bridge event
forward missing · D11 SDK v7 usage-shape rename.

## Verification

- end-user-testing/functional-validation/root-cause-debugging/cook edits
  read back: sections present, frontmatter intact.
- tui-testing frontmatter parses (name + description); iron rules reference
  the measured defect ids.
- manifests: zero stale "1.8.1" / "18 skills" strings (grep-verified).
