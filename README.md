# truth-forge

An evidence-gated validation **plugin marketplace for Claude Code**: 16 skills that
make "done" mean *proven*. The AI drives the real system as an end user — clicking,
typing, submitting via MCP/automation tools — and any claim it did not actually execute
is reported **UNVERIFIED**, never PASS. No mocks, no stubs, no test-mode bypasses.

## Install

```
/plugin marketplace add krzemienski/truth-forge
/plugin install truth-forge@truth-forge-marketplace
```

Or download `truth-forge-marketplace.tar.gz` from this repo's release artifacts and
extract it into your marketplaces directory.

## The skills

| Skill | What it enforces |
|-------|------------------|
| `brainstorm` | Scout-first, exact-requirements, present-before-asking gates; no code before an approved design |
| `prompt-forge` | Prompt AUTHOR / RATE (7-dimension /100 rubric) / OPTIMIZE / PIPELINE modes with quality gates |
| `validation-plan` | BRIEF → ROADMAP → per-phase PLAN/SUMMARY/VALIDATION with blocking **cumulative** gates |
| `plan-hardening` | Confidence-gap scoring, 4 red-team lenses, dispositioned gap register, gate injection |
| `cook` | Gated phase-by-phase execution of validation plans |
| `functional-validation` | Drive the real system end-to-end per platform (web/iOS/API/CLI runbooks) |
| `evidence-gates` | Run-scoped fresh evidence (`fresh_evidence.py`: init-run/next-step/seal/validate), verdict templates |
| `visual-inspection` | Screenshot-driven visual QA with severity model (found a real HIGH defect in the demo) |
| `ui-experience-audit` | 6-phase UX protocol: triage, visual, interactive, content, Nielsen heuristics, synthesis |
| `full-functional-audit` | App-wide interaction inventory → execute → remediate → verdict |
| `stack-testing` | Per-stack real-system test discipline: pytest/Go/C++/Django/Spring gotchas, FastAPI SSE testing, Playwright e2e, condition-based waiting (no sleeps, no new mocks) |
| `mobile-validation-runner` | iOS end-user validation: SETUP→RECORD→ACT→COLLECT→VERIFY, three-facet gates, simctl/XC-MCP/Expo lanes, preflight checks |
| `root-cause-debugging` | Reproduce-first diagnosis, backward call-chain tracing, pollution bisection; symptomatic hacks forbidden |
| `production-readiness` | 8-phase ship-readiness audit + spec-compliance matrix (COVERED/INCOMPLETE/MISSING) + dependency supply-chain health |
| `red-team-eval` | 4-lens hostile review of plans/prompts/artifacts, eval-driven development, QA cycling until measured goal attainment |
| `session-intent` | Reconstruct what was actually ASKED from Claude Code transcripts themselves: per-session intent matrix, session-to-commit alignment, intent-vs-implementation verdicts |

Five were added in v1.1.0 and `session-intent` in v1.2.0 from a second full-universe scan (664 unique skills
across both source archives, classified by usefulness domain) — see
`plugins/truth-forge/docs/consolidation-decisions.md`.

Shared doctrine lives in `plugins/truth-forge/references/` — the Iron Rule (fix the real
system), the End-User Actor Mandate, the evidence contract, severity model, platform
routing, preflight checks, and CI gate classification.

## The proof: `examples/mood-ring/`

A complete live walkthrough on the **Flaskr** tutorial app (from `pallets/flask`, BSD-3):
the **Mood Ring** feature (per-post mood emoji 😀🙂😐😢🔥 + filter bar), built and audited
end-to-end by the original 10 skills in series:

- `.planning/` — brainstorm, BRIEF/ROADMAP, gated phase plans, hardening gap register,
  per-phase SUMMARY+VALIDATION, visual-inspection / UX / full-functional audit reports
- `.prompts/` — the authored build prompt and its 91/100 rating
- `e2e-evidence/run-20260808T202017-mood-ring/` — the sealed evidence run
  (19 artifacts; `validate OK`), including 5 browser screenshots committed as PNGs
  (see the README in that directory for what each one proves).
- `flaskr/`, `tests/` — the implementation: 32/32 tests green (24 baseline + 8 new)

Highlights from the run: a forged `<script>alert(1)</script>` mood POST safely defaults
to 😐 with a flash notice; an invalid `?mood=🦄` returns 200 unfiltered; visual
inspection caught (and the loop fixed) a blue-on-blue invisible "All" filter label.

## Repo layout

```
.claude-plugin/marketplace.json   marketplace manifest
plugins/truth-forge/              the plugin (16 skills + references + docs)
examples/mood-ring/               the live walkthrough (app + plans + evidence)
```

## License

MIT for the truth-forge plugin and documentation (see `LICENSE`). The Flaskr example
under `examples/mood-ring/` is derived from the Flask tutorial and remains BSD-3-Clause
(see `examples/mood-ring/LICENSE.txt`).
