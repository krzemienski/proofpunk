#!/usr/bin/env python3
"""Regression test: a partial install promotion must not count as proven.

WHY THIS EXISTS (measured 2026-09-13)
-------------------------------------
commands/install.md lists four acceptance criteria. Three are gated by
INSTALL_EFFECT_CHECKS. The fourth — "the verification block at the end was
actually run, output in the report" — is measured by `verification_block_run`
but is NOT in that tuple, because it has never been observed passing on a
live run (persisted tool input truncates before the block's grep, so replay
cannot confirm it).

That left a real overclaim path. Two consumers decide "fully proven" by
reading the LEVEL STRING and nothing else:

    tools/verify-command-surface.py   `if verdict["level"] in ("c", "d")`
    tools/gauge-report.py            `c.get("reached_level") in ("c", "d")`

So a row could carry effect_partial=True and still be counted toward gauge
#4's full-chain total. Adding a sibling flag would not have helped — no
consumer read it. The fix is at the source: a partial promotion returns
level "d-partial" and effect_proven=False, which both consumers exclude
because "d-partial" is not in their tuples.

This test pins all three states of the fourth criterion.

Run:  python3 tools/test-promotion-partial.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = load("vcs", os.path.join(HERE, "verify-command-surface.py"))

BASE = dict(level="playbook-recognition", plugin_pass=True, control_failed=True)
GATED = {n: True for n in V.INSTALL_EFFECT_CHECKS}
# A counterfactual that correctly isolates the command doc as the cause.
CF = {
    "checks": {"write_succeeded": False, "claude_md_exists": False,
               "slash_registered": True, "no_harness_error": True},
    "pass": False,
    "plugin_path": "/scratch",
}

# The exact predicates the consumers use. Kept literal so this test fails if
# either consumer's tuple drifts from what is asserted here.
FULL_CHAIN_LEVELS = ("c", "d")


def promote(checks):
    return V.promote_to_effect_proven(
        dict(BASE), {"checks": checks}, "install",
        require_counterfactual=True, counterfactual_json=CF,
        scratch_plugin_dir="/scratch")


def main():
    failures = []

    # --- the fourth criterion, in all three states -----------------------
    absent = promote(dict(GATED))
    if absent["level"] in FULL_CHAIN_LEVELS:
        failures.append(
            f"ABSENT verification_block_run counted as full chain "
            f"(level={absent['level']!r})")
    if absent["effect_proven"] is not False:
        failures.append("ABSENT must set effect_proven False")
    if absent.get("effect_partial") is not True:
        failures.append("ABSENT must set effect_partial True")

    false = promote({**GATED, "verification_block_run": False})
    if false["level"] in FULL_CHAIN_LEVELS:
        failures.append(
            f"FALSE verification_block_run counted as full chain "
            f"(level={false['level']!r})")
    if false["effect_proven"] is not False:
        failures.append("FALSE must set effect_proven False")

    true = promote({**GATED, "verification_block_run": True})
    if true["level"] not in FULL_CHAIN_LEVELS:
        failures.append(
            f"TRUE verification_block_run must count as full chain "
            f"(level={true['level']!r})")
    if true["effect_proven"] is not True:
        failures.append("TRUE must set effect_proven True")
    if true.get("effect_partial") is not False:
        failures.append("TRUE must set effect_partial False")

    # --- a gated check failing still blocks, partial or not ---------------
    for name in V.INSTALL_EFFECT_CHECKS:
        broken = promote({**GATED, name: False, "verification_block_run": True})
        if broken.get("effect_proven"):
            failures.append(f"a failing gated check ({name}) must block promotion")

    # --- verify path must be untouched by the install-only logic ----------
    ver = V.promote_to_effect_proven(
        dict(BASE), {"checks": {n: True for n in V.VERIFY_EFFECT_CHECKS}}, "verify")
    if ver["level"] != "d" or ver["effect_proven"] is not True:
        failures.append("verify promotion must be unaffected by install partials")
    if ver.get("effect_partial"):
        failures.append("verify must never be marked partial")

    # --- consumer-contract guard -----------------------------------------
    # The partial level must be excluded by the literal tuples both consumers
    # use. If someone adds "d-partial" to either, this fails loudly.
    if "d-partial" in FULL_CHAIN_LEVELS:
        failures.append("d-partial must not be a full-chain level")
    surface = open(os.path.join(HERE, "verify-command-surface.py"),
                   encoding="utf-8").read()
    gauge = open(os.path.join(HERE, "gauge-report.py"), encoding="utf-8").read()
    if 'verdict["level"] in ("c", "d")' not in surface:
        failures.append(
            "verify-command-surface's full-chain predicate changed — re-check "
            "that partial rows are still excluded")
    if '("c", "d")' not in gauge:
        failures.append(
            "gauge-report's full-chain predicate changed — re-check that "
            "partial rows are still excluded")

    total = 3 + 3 + 3 + len(V.INSTALL_EFFECT_CHECKS) + 2 + 3
    if failures:
        print(f"FAIL  {len(failures)} of {total} assertions failed")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS  {total} assertions")
    print("  absent  -> level d-partial, effect_proven False, not counted")
    print("  false   -> level d-partial, effect_proven False, not counted")
    print("  true    -> level d,         effect_proven True,  counted")
    print(f"  {len(V.INSTALL_EFFECT_CHECKS)} gated checks each block promotion when false")
    print("  verify path unaffected; both consumer predicates still exclude partial")
    return 0


if __name__ == "__main__":
    sys.exit(main())
