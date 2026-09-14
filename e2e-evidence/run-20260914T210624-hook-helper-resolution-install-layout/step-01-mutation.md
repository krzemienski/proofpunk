# mutation test — tools/verify-hook-helper-resolution.py

harness under test: `tools/verify-hook-helper-resolution.py`
mutation subject  : `plugins/proofpunk/hooks/stop-guard.sh` helper resolver
utc : 2026-09-14T21:06:24.275804Z
HEAD: 1924d02

A gate that cannot fail proves nothing, so this one was mutation-tested
against the exact defect it exists to catch.

| # | hook state | gate rc | meaning |
|---|---|---|---|
| 1 | FIXED (candidate-probe resolver) | 0 | passes on good code |
| 2 | MUTATED back to the single-line `$_hookdir/../skills/...` resolver | **1** | **fails on the real defect** |
| 3 | restored | 0 | byte-identical hook (sha256 match verified) |

Mutation (2) output, verbatim:

    FAIL: the installed hook cannot resolve its helper.
          Every --hooks user would be wedged by a fail-closed
          guard. Reason emitted:
            Proofpunk: a completion was claimed but the intent-verification
            helper is missing (skills/end-user-testing/scripts/intent_verdict.py)

mutation_test verify-hook-helper-resolution.py: baseline green -> named mutation (single-line `$_hookdir/../skills` resolver restored) -> mutated_rc=1 naming it -> restored byte-identical (sha256 verified) -> green.

The gate is load-bearing, not decorative.

## Vacuity guard

The driven transcript must clear the claim, proof AND scout branches before the
intent branch is reached. An earlier draft of this probe tripped the scout gate
and would have reported success while proving nothing, so the gate now FAILS
explicitly if `intent verdict` is absent from the block text.
