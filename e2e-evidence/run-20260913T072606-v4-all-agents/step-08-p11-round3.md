# step-08 — P11 round 3: ProseA + late reviewer findings

Sealed after step-07 because findings kept arriving. Each verified against
source before editing; two were refuted by measurement.

## Fixed

1. ROUTER COUNTS STALE IN FOUR PLACES. skills/proofpunk/SKILL.md said
   "17 delivery skills" (L4), "17 narrow delivery skills — 18 counting this
   router" (L28), "17 other skill files" (L31), "these 17 skills" (L74).
   MEASURED: 19 directories, so 18 delivery + 1 router. All four corrected.
   The router's TABLE was already complete — this was prose drift only, which
   is why verify-router-links passed throughout.

2. completion-summary:23 still said "the five states" after step-07 changed
   the heading and frontmatter. My own edit was incomplete. Now "the state
   set".

3. implement:233 claimed `rc=0` — every child reached a terminal status.
   FALSE for the same reason the completion-summary contract was: rc=0 also
   covers a missing tracker (every runtime except Claude Code) and a degraded
   one. Rewritten to say rc=0 means no child is RECORDED live, and to require
   carrying the degraded/no-tracker qualification into the report.

4. implement:293 cited the runbooks as `api/web/cli/ios-validation.md` — a
   path shape that matches no file. Now names all four individually.

5. red-team-eval:48 enumerated "security, scope-creep, evidence-rigor
   failure-modes" — a missing comma makes four lenses read as three. Fixed.

## Findings REFUTED by measurement

- ProseA HIGH: "implement:207,221 cite references/execution-loop.md which does
  not exist at plugins/proofpunk/references/". MEASURED: the file exists at
  plugins/proofpunk/skills/implement/references/execution-loop.md — a
  skill-LOCAL bundle, where a bare `references/` path is correct. Same class
  of error as my own reverted 83-file sweep: local bundles are legitimate.
  No change made.

- A substring scan of "terminal status" in completion-summary flagged four
  hits. Reading them, all four CONTRAST with terminal status rather than
  claiming it. Correct usages; no change.

## Gates

    verify-citations  verify-counts  verify-proof-vocab  verify-orchestration
    verify-router-links  verify-shipped-vs-active  verify-harness-integrity
    verify-lane-contracts  verify-mutation-artifact

    9/9 rc=0

## Still open (unchanged from step-07)
mobile-validation-runner example.sh; ui-experience-audit zero-findings claim;
visual-inspection "~60%"; production-readiness wave-1 vs its methodology;
end-user-testing three-facet rule vs stateless API/CLI targets (ProseA HIGH,
real, needs a doctrine decision); validation-plan's JWT example and `test-run`
proof type (ProseA HIGH, real).

VERDICT: PASS — all 19 skills reviewed across three rounds; every finding
fixed, refuted with measurement, or recorded open.
