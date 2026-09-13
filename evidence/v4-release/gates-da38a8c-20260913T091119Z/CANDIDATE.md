# Release-gate capture

    candidate SHA : da38a8ce799932f7e28efdddc88a9c22f6fb5d53
    short         : da38a8c
    captured (UTC): 20260913T091119Z
    tag           : NONE — v4.0.0 is declared in manifests, not tagged
    release_ready : false

## Why this is a capture, not a release
Four criteria are unproven (P6 flaky 1/3, P8 at 2 of 15, P14/P15
retroactive). See
e2e-evidence/run-20260913T072606-v4-all-agents/step-13-release-blocked.md.

## Gate results at this SHA
    test-hooks-output.txt              HOOK TEST FAILS: 0
    test-installer-output.txt          INSTALLER TEST FAILS: 0
    dry-run-install-output.txt         INSTALL DRY-RUN FAILS: 0
    verify-orchestration-output.txt    documented order, with methods owned exactly once.
    test-integrations-output.txt       INTEGRATION TEST FAILS: 0

Prior-run material in evidence/v4-release/ (run-20260911T234909Z, the
allowlist and boundary notes) predates this capture and is untouched.
