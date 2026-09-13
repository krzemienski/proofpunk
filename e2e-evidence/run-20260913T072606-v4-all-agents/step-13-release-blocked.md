# step-13 — why v4.0.0 is NOT tagged

The operator authorized the tag ("All of the above, then cut v4.0.0"). It is
deliberately not cut. This records the exact reason, so the decision is
auditable rather than an omission.

## Criteria at HEAD ed891ec

    V1   PASS                     Reported PermissionRequest 'if' warning attributed
    V2   IMPOSSIBLE-BY-CONSTRUCTION Cross-agent tracker parity for OMP
    V3   IMPOSSIBLE-BY-CONSTRUCTION Cross-agent tracker parity for OpenCode
    V4   PASS                     Harness executes the OpenCode plugin end to end
    V5   PASS                     P5 router links every non-head skill
    V6   UNVERIFIED               P6 every command proven at the real slash surface
    V7   PASS                     P9 restated against the real hook taxonomy
    V8   PASS                     P10 doctrine enforcement + precedence map
    V9   PASS                     P11 prose-correctness review of all 19 skills
    V10  PASS                     Inherited platform-steer mutation gap closed
    V11  PASS                     P7 improvements ranked and implemented
    V12  PARTIAL-RETRACTED        P8 each improvement individually proven
    V13  UNVERIFIED-RETROACTIVE   P14 clean sealed run
    V14  UNVERIFIED-RETROACTIVE   P15 success measured on an immutable run
    V15  PENDING                  v4.0.0 released and tagged

## Gates are green — and that is not sufficient

From a clean `git archive HEAD` (not the working tree):

    verifiers                 9/9 rc=0
    HOOK TEST FAILS           0
    INTEGRATION TEST PASSES   19

Every gate passes. The release is still blocked, because gates measure the
suite, not the criteria. Four criteria are unproven:

1. **V6 / P6 — UNVERIFIED.** verify-command-surface.py now completes (15 real
   sandboxed arms, ~6 min), but re-running the truth-audit probe alone three
   times gave pass / fail / fail — 1/3. A criterion whose outcome changes with
   no source change is not proven by one green run. Averaging retries into a
   pass is the exact failure this plugin exists to prevent.

2. **V12 / P8 — PARTIAL, retracted from PASS.** 15 improvements map to only 8
   distinct evidence artifacts. A shared artifact proves the batch, not the
   member. Only I1 (the OpenCode filePath guard) is individually proven, by
   mutation test.

3. **V13, V14 / P14, P15 — UNVERIFIED-RETROACTIVE, retracted from PASS.** This
   run satisfies both properties (12 sealed steps, validate OK, 0 post-seal
   mutations verified by SHA-256 recompute) but was already underway before
   they became criteria. It was never DESIGNED to prove them. Observing a
   property afterwards is weaker than running to test it.

Three of those four I downgraded MYSELF after measurement contradicted a PASS
I had already written.

## What a release would additionally require
CHANGELOG.md (absent), a version/count sweep across package.json + README.md +
tools/INSTALL.md + build-site.py page sources (per AGENTS.md), evidence under
evidence/v4-release/, a release-commit gate run, then the tag and push.

## The measured reason this matters here
The installed Claude Code plugin is 3.0.0 while source says 4.0.0. Tagging
4.0.0 now would publish a version whose own status report contains four
unproven criteria — and the first thing this plugin tells its users is that
unproven is never done.

VERDICT: release BLOCKED. Not an omission; a refusal with four named causes.
