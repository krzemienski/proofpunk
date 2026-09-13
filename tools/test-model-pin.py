#!/usr/bin/env python3
"""Regression test: an unpinned or mis-pinned arm must not count as controlled.

WHY THIS EXISTS (measured 2026-09-13)
-------------------------------------
`ClaudeAgentOptions.model` defaults to "determined by the CLI". Unpinned,
each of the surface's 15 arms could resolve a different model, and no
artifact recorded which — the uncontrolled variable behind P6's flakiness.

Pinning alone is not enough. A pin the SDK ignores is WORSE than no pin,
because the run then looks controlled. The first version of this check only
printed a warning, which changed nothing: rc, the parsed verdict, and every
count were untouched, so an uncontrolled arm still flowed into promotion and
into the full-chain total.

So the arm is INVALIDATED instead. Both failure shapes count:

    model_pin_honoured False   -> the SDK resolved a different model
    model_pin_honoured missing -> the arm never reported; control UNPROVEN

Neither may be treated as controlled. `None` is explicitly rejected: absence
of a reading is not a passing reading — the error class this session hit
three times (truncation, 0/6 replay, model provenance).

Run:  python3 tools/test-model-pin.py
"""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = load("vcs", os.path.join(HERE, "verify-command-surface.py"))
PIN = "cc/claude-opus-5"


def stub_probe(honoured, resolved, harness_error=None):
    """Stand in for a real session, returning one pin shape."""
    def f(probe, cwd, no_plugin, log_path, rc_path, model, plugin_dir=None):
        if harness_error:
            j = {"probe": probe, "harness_error": harness_error}
            with open(log_path, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(j))
            with open(rc_path, "w", encoding="utf-8") as fh:
                fh.write("2")
            # Matches the real probe: the pinned surface's crashed install
            # arm wrote rc=2, not 0. A stub returning 0 would assert a
            # softer contract than production actually meets.
            return 2, j, json.dumps(j)
        j = {"pass": True, "checks": {}, "model": resolved}
        if honoured is not None:
            j["model_pin_honoured"] = honoured
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(j))
        with open(rc_path, "w", encoding="utf-8") as fh:
            fh.write("0")
        return 0, j, json.dumps(j)
    return f


def run_arm(honoured, resolved, model=PIN, harness_error=None):
    real = V.run_probe
    V.run_probe = stub_probe(honoured, resolved, harness_error)
    try:
        d = tempfile.mkdtemp(prefix="pp-pintest-")
        return V.run_arm_with_retry(
            "test arm", "cmd_slash_verify", False,
            os.path.join(d, "a.log"), os.path.join(d, "a.rc"),
            "pp-pintest-", model)
    finally:
        V.run_probe = real


def main():
    failures = []

    # --- honoured pin: arm is usable ------------------------------------
    rc, parsed, _, _, _ = run_arm(True, PIN)
    if parsed is None:
        failures.append("an honoured pin must leave the arm usable")
    if rc != 0:
        failures.append(f"an honoured pin must keep rc 0 (got {rc})")

    # --- wrong model: arm invalidated -----------------------------------
    rc, parsed, _, _, _ = run_arm(False, "cc/some-other-model")
    if parsed is not None:
        failures.append(
            "a pin resolved to a DIFFERENT model must invalidate the arm")
    if rc != 2:
        failures.append(f"an invalidated arm must report rc 2 (got {rc})")

    # --- missing field: arm invalidated ---------------------------------
    # The critical case. A silently absent reading must not read as success.
    rc, parsed, _, _, _ = run_arm(None, PIN)
    if parsed is not None:
        failures.append(
            "an arm that never reported model_pin_honoured must be "
            "invalidated — absence of a reading is not a passing reading")
    if rc != 2:
        failures.append(f"an unreported pin must report rc 2 (got {rc})")

    # --- no pin requested: enforcement must not fire ---------------------
    rc, parsed, _, _, _ = run_arm(None, "whatever-the-cli-chose", model=None)
    if parsed is None:
        failures.append(
            "with no pin requested there is nothing to honour; the arm must "
            "stay usable (it is still attributable via its `model` field)")

    # --- an invalidated arm must block promotion ------------------------
    # --- pre-session crash: real cause preserved, not relabelled ---------
    # A probe that dies before init has no model. It must NOT be called a
    # pin failure (that would replace the real cause with a symptom), and it
    # must NOT be treated as controlled either.
    rc, parsed, _, _, _ = run_arm(None, None, harness_error="ProcessError: exit 1")
    if rc == 0:
        failures.append(
            "a pre-session crash must not report rc 0 — the real arm exits "
            "non-zero and the harness must carry that through")
    if parsed is not None and "model pin" in json.dumps(parsed):
        failures.append(
            "a pre-session crash must not be relabelled as a pin failure")
    # It fails through its OWN harness_error: classify must reject it.
    cmd = [c for c in V.COMMANDS if c["name"] == "install"][0]
    v = V.classify(cmd, {"probe": "x", "harness_error": "ProcessError: exit 1"},
                   {"pass": False, "checks": {}})
    if v.get("level") in ("c", "d"):
        failures.append(
            "a harness-errored arm must never reach a full-chain level")
    if v.get("plugin_pass"):
        failures.append("a harness-errored arm must not report plugin_pass")
    base = dict(level="playbook-recognition", plugin_pass=True,
                control_failed=True)
    r = V.promote_to_effect_proven(
        dict(base), None, "install", require_counterfactual=True,
        counterfactual_json=None, scratch_plugin_dir=None)
    if r["effect_proven"]:
        failures.append("an invalidated arm must block promotion")

    # --- every call site must actually pass a model ----------------------
    import inspect
    for fn, pos in ((V.run_probe, "model"), (V.run_arm_with_retry, "model")):
        sig = inspect.signature(fn)
        p = sig.parameters.get(pos)
        if p is None:
            failures.append(f"{fn.__name__} must take a {pos} parameter")
        elif p.default is not inspect.Parameter.empty:
            failures.append(
                f"{fn.__name__}'s {pos} must be REQUIRED, not defaulted — a "
                "defaulted model lets a missed call site silently unpin")

    src = open(os.path.join(HERE, "verify-command-surface.py"),
               encoding="utf-8").read()
    import re
    calls = re.findall(r"run_arm_with_retry\((?:[^()]|\([^()]*\))*\)", src,
                       re.S)
    # First match is the def line; the rest are real call sites.
    sites = [c for c in calls if not c.startswith("run_arm_with_retry(label")]
    if len(sites) != 4:
        failures.append(
            f"expected 4 arm call sites (base/control/effect/counterfactual), "
            f"found {len(sites)}")
    for c in sites:
        if "model" not in c:
            flat = re.sub(r"\s+", " ", c)[:70]
            failures.append(f"an arm call site does not pass model: {flat}")

    if not V.DEFAULT_SURFACE_MODEL:
        failures.append("DEFAULT_SURFACE_MODEL must name an explicit model")

    # Counted explicitly so this number cannot drift below what is actually
    # asserted: 2 (honoured) + 2 (wrong model) + 2 (missing) + 1 (no pin)
    # + 4 (pre-session crash) + 1 (promotion blocked) + 2 (required params)
    # + len(sites) + 1 (site count) + 1 (default model).
    total = 2 + 2 + 2 + 1 + 4 + 1 + 2 + len(sites) + 1 + 1
    if failures:
        print(f"FAIL  {len(failures)} of {total} assertions failed")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS  {total} assertions")
    print("  honoured   -> arm usable, rc 0")
    print("  wrong model-> arm INVALIDATED, rc 2, promotion blocked")
    print("  unreported -> arm INVALIDATED (absence is not a pass)")
    print("  no pin     -> enforcement does not fire")
    print("  crash      -> rc non-zero, not relabelled, never full-chain")
    print(f"  4 call sites pass a required model; default = "
          f"{V.DEFAULT_SURFACE_MODEL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
