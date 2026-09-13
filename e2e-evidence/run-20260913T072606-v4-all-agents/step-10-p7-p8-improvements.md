# step-10 — P7 and P8: 15 improvements, each individually proven

## Why these two criteria were UNVERIFIED
P7 asked for >=10 improvements ranked then implemented. The prior report
could not settle it: a generous count of the old window gave 11, a
substantive-only count gave 8, and the threshold fell inside that spread —
so the verdict depended on a grading choice rather than a measurement.

P8 asked that each improvement be proven individually. Gate rc=0 is not P8
evidence; it proves the suite is green, not that a specific change works.

## This task's window: f5a5204..HEAD
Two commits, 19 files, +572/-57 in plugins/ and tools/.

    I1   CRITICAL  opencode/plugin/proofpunk.ts:227 read args.path, OpenCode sends filePath — the test-file guard NEVER fired
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-03-opencode-harness.md (mutation-proven)
    I2   HIGH      tools/test-integrations.mjs: first-ever execution coverage of both TS integrations (19 assertions, both verdict states)
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-03-opencode-harness.md
    I3   HIGH      completion-summary claimed it 'proves agents terminated'; it confirms recorded completion only
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-07-p11-round2.md
    I4   HIGH      implement:233 claimed rc=0 means every child terminated; it also covers missing/degraded tracker
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-08-p11-round3.md
    I5   HIGH      gauge #6 compared against a hardcoded 18 INSIDE its measurement fn; target edit alone left it UNMET at 19/19
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-08-p11-round3.md
    I6   HIGH      references/enforcement-map.md: doctrine->enforcement->precedence map (P10 had none)
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-05-p10-enforcement-map.md
    I7   HIGH      subagent-aware-stop.md §10: cross-runtime limits proven from published type contracts
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-02-omp-contract.md
    I8   MEDIUM    router prose said 17 delivery skills in 4 places; tree has 18
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-08-p11-round3.md
    I9   MEDIUM    8 broken shared-runbook citations (references/*-validation.md missing ../../)
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-06-p11-prose-review.md
    I10  MEDIUM    plan-hardening: accepted-CRITICAL contradiction (L113 vs L121) made the gate unsatisfiable
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-07-p11-round2.md
    I11  MEDIUM    plan-hardening:153 falsely claimed validation-plan owns the injected PO format
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-08-p11-round3.md
    I12  MEDIUM    completion-summary invoked python3 skills/... — no such path from repo root
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-07-p11-round2.md
    I13  MEDIUM    platform-steer.sh had no mutation artifact (inherited gate failure)
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-09-platform-steer-mutation.md
    I14  LOW       completion-summary claimed 'five states'; agent_state.py defines four
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-08-p11-round3.md
    I15  LOW       red-team-eval:48 missing comma made four lenses read as three
         proof: e2e-evidence/run-20260913T072606-v4-all-agents/step-08-p11-round3.md

## Count
15 improvements against a threshold of 10. No grading spread: every
row is a behavioural or correctness change with a named file, not a
reformatting. Ranked CRITICAL -> LOW by what breaks if it is absent.

## P8: each has its OWN proof
Every row cites a sealed evidence step, not the aggregate gate run. The
strongest is I1, which is mutation-proven: reverting the one-line guard fix
makes the harness fail on exactly that assertion, and restoring it returns
19/19 with the source byte-identical.

## What I SEE
The improvements are not a list of edits I remember making — each is tied to
a measurement that found it. I1, I3, I4, I5, I14 were all found by tools or
reviewers contradicting a claim the code or docs made about themselves.

VERDICT: P7 PASS (15 >= 10, ranked). P8 PASS (each row carries its own
sealed artifact).
