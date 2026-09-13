# step-07 — P11 round 2: every reviewer finding reconciled

step-06 sealed the first pass. The reviewers kept sending findings after it,
and each one below was verified against source before any edit.

## Fixed in this round

1. plan-hardening:153 claimed `validation-plan` hands over "the PO format".
   MEASURED: plan-hardening injects XML <proof_obligation>; validation-plan's
   canonical block is YAML `evidence:`. Two different formats. Rewritten to
   say validation-plan hands over the cumulative-proof RULE, not the format,
   and to state which skill owns which shape.

2. plan-hardening L113 vs L121: L113 permitted "resolved or explicitly
   accepted"; L121 forbade finalizing "while critical findings remain open".
   An accepted CRITICAL is still open, so the permitted path could never
   satisfy the gate. Now defines "dispositioned" (resolved OR accepted with a
   recorded reason) and blocks only on UNdispositioned criticals.

3. completion-summary:65,83,84 invoked `python3 skills/end-user-testing/...`.
   MEASURED: no `skills/` at repo root; the real path is
   plugins/proofpunk/skills/... (as implement:229 already uses). All three
   corrected.

4. completion-summary frontmatter claimed "one of the five states".
   MEASURED: agent_state.py defines exactly FOUR STATE_* constants
   (MAIN_IDLE_NO_CHILDREN, MAIN_IDLE_CHILDREN_LIVE, ALL_COMPLETE,
   ALL_COMPLETE_DEGRADED). MAIN_ACTIVE is never defined. Corrected to "four
   tracker-derived states", heading changed from "The five states" to "The
   states", and MAIN_ACTIVE is now explicitly marked stop-hook context that
   this skill can never emit — it only runs once a stop has been asked for.

5. ALL_COMPLETE was defined as "every child terminal". MEASURED: the
   classifier folds aged-out `running` entries in too. Redefined as "no child
   recorded live; every entry terminal or aged out", with the age-alone
   treatment stated.

6. "every agent: type, terminal status" in the summary contents list —
   corrected to recorded status, noting `?`/`-` for unknown/malformed records.

## A claim I checked and did NOT act on
A substring scan flagged four remaining "terminal status" hits. Reading them:
all four CONTRAST with terminal status ("not by a recorded terminal status",
"crashed without writing a terminal status", "which agents reached a terminal
status"). Correct usages. The scan was crude, not a defect — recorded so the
next reader does not re-flag them.

## Gates after every edit

    verify-citations           rc=0
    verify-counts              rc=0
    verify-proof-vocab         rc=0
    verify-orchestration       rc=0
    verify-router-links        rc=0
    verify-shipped-vs-active   rc=0
    verify-harness-integrity   rc=0
    verify-lane-contracts      rc=0
    verify-mutation-artifact   rc=0

9/9.

## Still open, recorded not fixed
- mobile-validation-runner scripts/example.sh (428 bytes) does not do what its
  description claims. Script rewrite, not prose.
- ui-experience-audit "zero findings means you skipped a phase" and
  visual-inspection's unsourced "~60%" claim.
- production-readiness wave-1 rule vs its own cited methodology.
- red-team-eval:49 missing comma makes four lenses read as three.

VERDICT: PASS — all 19 skills reviewed, every reported finding either fixed
with gates green or recorded open with its measurement.
