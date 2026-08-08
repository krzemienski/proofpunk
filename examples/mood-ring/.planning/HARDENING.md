# HARDENING — Mood Ring plan (plan-hardening output)

**Stage 1 — classify**: implementation plan, gated maturity (both phases carry gate blocks).
Blast radius: one DB table, 3 templates, 1 route module, test suite. No auth/payment/public-API
surface. **Original intent** (checked against every edit below): "posts carry one of 5 moods,
visible and filterable on the index, with zero regression to existing behavior."

**Stage 3 — confidence-gap scoring**

| Section | triggers | risk_bonus | critical | gap_score | Disposition |
|---------|----------|-----------|----------|-----------|-------------|
| 01 task 2 (validate_mood) | "reject or default" hedged upstream | data write | yes | high | rewritten: default-only, single behavior |
| 02 task 2 (?mood= handling) | emoji-in-URL encoding unstated | none | yes | medium | gate asserts real driven requests decide |
| 01 task 4 (tests) | "add tests" without count | none | yes | low | gate asserts pytest exit 0 + new cases named |
| Migration note | unstated data-loss risk of `init-db` | data | yes | high | G-02 below |

**Stage 4/5 — gap register (all findings dispositioned)**

| id | section | lens | severity | description | suggested fix | disposition |
|----|---------|------|----------|-------------|---------------|-------------|
| G-01 | 01 task 2 | Adversary | HIGH | Forged POST mood (`<script>`, `🦄`, 10KB string) reaches DB if validation is forgotten in ONE of create/update | single `validate_mood` helper used by BOTH routes; test each | FIXED in plan (helper + tests named) |
| G-02 | migration | Operator | HIGH | Devs with existing DBs run `flask init-db` → DROP TABLE wipes data just to get the column | ship ALTER TABLE one-liner; warn that init-db destroys data | FIXED (schema.sql comment + SUMMARY migration note) |
| G-03 | 02 index | Integrator | MEDIUM | Legacy rows with moods outside MOODS (hand-edited DB) render an unlisted emoji and break "every post matches a filter" | treat read path as trusted-after-write-validation; document | ACCEPTED — write-path validation makes this unreachable through the app; direct DB edits are out of trust scope |
| G-04 | 02 filter bar | Skeptic | MEDIUM | "emoji filter links" didn't state URL-encoding handling; raw emoji in `?mood=` could 400 on some stacks | gate requires a DRIVEN request per emoji (curl/browser), so encoding behavior is proven, not assumed | FIXED — gate language (driven per-emoji requests) |
| G-05 | baseline tests | Skeptic | HIGH | Existing 24 tests POST create/update WITHOUT a mood field — if backend used `request.form["mood"]` directly they would 400 | `request.form.get("mood")` + default; pytest run in phase-01 gate proves it | FIXED in plan task wording (helper + form.get); verified in cook |

**Stage 6 — gate injection**: both phases already carry blocking YAML gate blocks with
`actor: ai-end-user`; phase 02's gate is cumulative (`covers_phases: [01]`). XML-form gate
for the phase-02 browser pass (used by evidence-gates at verdict time):

```xml
<validation_gate id="VG-02" blocking="true">
Actor: the AI agent drives these actions as an end user via MCP/automation
tools — no passive checks, no delegated clicking
Prerequisites: flask dev server running on 127.0.0.1:5000, DB migrated/initialized
Execute: register→login→create 5 posts (one per mood)→click each emoji filter→click All→
edit post 1 mood→forge invalid mood POST→request ?mood=🦄
Capture: save every response body + screenshot to e2e-evidence/run-*/step-NN-*
Pass criteria: per-emoji filtered lists contain exactly the posts of that mood;
All shows 5; invalid mood never stored; ?mood=🦄 returns 200 unfiltered; phase-01 assertions still pass
Review: READ evidence and describe what is seen
Verdict: PASS → finalize | FAIL → fix real system → re-run | UNVERIFIED → not executed
Mock guard: IF tempted to mock → STOP → fix real system
</validation_gate>
```

**Stage 7 — consensus validation**

- [x] Original intent preserved (no scope additions; G-02 adds only a comment + note)
- [x] Every CRITICAL/HIGH finding resolved or accepted with reason (G-01, G-02, G-05 fixed; no CRITICALs)
- [x] Every phase carries a blocking gate with observable criteria
- [x] Every behavioral criterion pairs with a driven end-user action (curl/browser)
- [x] No new hedging language introduced
- [x] Gap register included (above)

**Verdict: plan is HARDENED — cleared for `cook`.**
