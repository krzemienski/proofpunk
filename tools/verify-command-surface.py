#!/usr/bin/env python3
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=sdk_probe.py keywords=--no-plugin,full_chain
"""Drive all six /proofpunk:* slash commands through sdk_probe.py.

Each command runs at least twice: plugin loaded, then --no-plugin (control
arm). The control MUST fail or the probe is vacuous. install and verify
additionally run a third EFFECT arm (does the playbook actually WRITE the
memory file / actually RUN a real command, not just recognize the slash
and narrate?), and install runs a fourth COUNTERFACTUAL arm (does the
effect DISAPPEAR when the command doc's own body is neutered, proving the
effect is attributable to the playbook's documented steps rather than
ambient host behavior?).

Proof levels (from evidence/v3-release/00-baseline/command-surface-map.md):
  (a) script-level — backing script invoked directly (not this harness)
  (b) skill-load   — Skill tool by name, bypassing the command doc
  (c) full-chain   — slash typed → registered → mapped skill/script ran →
                     unique marker observed
  playbook-recognition — slash registered + unique command-doc marker,
                     but the command has no backing skill/script (install)
                     or no Activate-skill line (verify)
  (d) effect-proven — playbook-recognition PLUS an OBSERVED real effect on
                     disk (install: CLAUDE.md written with markers, under
                     the line cap, placeholders substituted) or a real
                     command execution (verify: a harness-seeded sentinel
                     surfaced in genuine, non-error Bash tool_result
                     output) — never the model's narration of having done
                     so. install additionally requires the counterfactual:
                     the SAME effect probe against a scratch plugin copy
                     whose install.md body is neutered must show the
                     effect ABSENT, proving the real command doc (not
                     ambient host behavior) produces it.

(c) and (d) both count toward the 6/6 full-chain gauge — see
tools/gauge-report.py's g_command_surface_proven(), which accepts
reached_level in ("c", "d"). install/verify cannot reach (c): they have
no backing skill/script for a Skill-tool call to succeed against. (d) is
their honest ceiling, reached by proving the real effect instead.

Writes ONE artifact:
  evidence/v3-release/l16-commands/command-surface-proof.json

Exit 0 only if every command reaches its own honest maximum level (c for
the four skill-backed commands, d for install/verify) AND every control
arm failed. That is 6/6 at each command's honest maximum, not an inflated
6/6 full-chain by fiat. The artifact's full_chain field is the gauge
number gauge-report.py reads.

Each arm (plugin, control, effect, counterfactual) runs in its OWN fresh
tempfile.mkdtemp() sandbox, torn down (shutil.rmtree) immediately after
its artifacts (log, rc, sha256) are captured — no arm can see another
arm's leftover state, and a fresh-sandbox claim in this file's own header
is no longer contradicted by a shared `work` directory.

Transient host auth/rate-limit failures (429 rate_limit_error, "OAuth
session expired and could not be refreshed", "OAuth access token has
expired") are retried up to RETRY_MAX times per arm with RETRY_BACKOFF_S
seconds between attempts, since these are host-contention noise, not a
probe failure — but a harness error that survives every retry is recorded
as harness_error, never silently reported as a passing/failing probe
result, and NEVER promoted to a green artifact.

Stdlib only. Never pipes a command whose exit code is recorded.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PROBE = os.path.join(HERE, "sdk_probe.py")
# PP_CMDSURFACE_OUT_DIR scopes every output (logs, rc files, the artifact)
# to a fresh run directory. Without it, the canonical l16-commands path is
# used — but a partial/failed run against the canonical path overwrites
# sealed logs from the last green run, so full verification runs use the
# override and promote to canonical ONLY on a complete green run, as a
# deliberate act. ARTIFACT and all per-arm log/rc paths derive from
# OUT_DIR, so one override moves everything consistently.
OUT_DIR = os.environ.get("PP_CMDSURFACE_OUT_DIR") or os.path.join(
    ROOT, "evidence", "v3-release", "l16-commands")
ARTIFACT = os.path.join(OUT_DIR, "command-surface-proof.json")
REAL_PLUGIN = os.path.join(ROOT, "plugins", "proofpunk")

# Honest maximum per command. Derived from the command docs, not hoped.
# implement/forge-prompt/rate-prompt/truth-audit: "Activate the `X` skill"
# verify: playbook, no Activate-skill line, no flags, fresh_evidence.py is
#         internal to end-user-testing not exposed on the command
# install: in-session playbook, no skill, no script (distinct from
#          tools/proofpunk-install.sh)
COMMANDS = [
    dict(name="implement", probe="cmd_slash_implement",
         slash="/proofpunk:implement", skill="proofpunk:implement",
         max_level="c",
         note="command doc activates implement; flags --parallel --auto --mine --fast"),
    dict(name="forge-prompt", probe="cmd_slash_forge_prompt",
         slash="/proofpunk:forge-prompt", skill="proofpunk:prompt-forge",
         max_level="c",
         note="command doc activates prompt-forge AUTHOR; flag --depth"),
    dict(name="rate-prompt", probe="cmd_slash_rate_prompt",
         slash="/proofpunk:rate-prompt", skill="proofpunk:prompt-forge",
         max_level="c",
         note="command doc activates prompt-forge RATE; flag --ship-below-threshold"),
    dict(name="truth-audit", probe="cmd_slash_truth_audit",
         slash="/proofpunk:truth-audit", skill="proofpunk:codebase-truth-audit",
         max_level="c",
         note="command doc activates codebase-truth-audit; flags --start/--end"),
    dict(name="verify", probe="cmd_slash_verify",
         slash="/proofpunk:verify", skill=None,
         max_level="d",
         effects_probe="cmd_slash_verify_effect",
         effect_kind="verify",
         require_counterfactual=False,
         note=("playbook: no Activate-skill line, no flags; marker "
               "UNVERIFIED. Honest max is (d) effect-proven: a harness-"
               "seeded sentinel must surface in a genuinely-executed Bash "
               "tool_result, never the model's narration.")),
    dict(name="install", probe="cmd_slash_install",
         slash="/proofpunk:install", skill=None,
         max_level="d",
         effects_probe="cmd_slash_install_effect",
         effect_kind="install",
         require_counterfactual=True,
         note=("in-session playbook, NO backing skill or script — distinct "
               "from tools/proofpunk-install.sh; the earlier 'SDK has no "
               "Write tool' premise was disproven 2026-09-09 (Write was "
               "merely disallowed by _SLASH_PLAYBOOK_TOOLS); the effect "
               "probe grants first-party Write/Edit "
               "explicitly with strict_mcp_config=True excluding ambient "
               "MCP servers. Honest max is (d) effect-proven: CLAUDE.md "
               "must actually exist with markers, under 200 lines, "
               "placeholders substituted, PLUS a counterfactual against a "
               "neutered install.md must show the effect gone — proving "
               "the command doc itself is the cause, not ambient host "
               "behavior.")),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


ARM_TIMEOUT_S = 180

# Transient host auth/rate-limit contention (multiple parallel SDK
# sessions racing a token refresh, or a provider-side 429 backoff window)
# is noise, not a probe result — retrying these specific error shapes is
# NOT the same as retrying a genuine probe failure. Anything else
# (a wrong check, a missing marker, a real ResultError from the model
# itself) is reported as-is on the first attempt, never silently retried.
RETRY_MAX = 3
RETRY_BACKOFF_S = 90
_TRANSIENT_RE = re.compile(
    r"(rate_limit_error|429|OAuth session expired|"
    r"OAuth access token|authentication_error|Re-authenticate|"
    r"could not be refreshed)",
    re.IGNORECASE,
)


def is_transient_harness_error(rc, parsed, raw_body):
    """True only for the specific host-contention shapes Main confirmed
    today (429 rate_limit_error backoff window; OAuth refresh racing
    parallel sessions) — never for a genuine probe/check failure. A
    parsed probe JSON with pass=False from real checks is NOT transient
    even if it also happens to contain one of these substrings somewhere
    in an unrelated field; scope the search to the harness-level fields
    that actually carry an auth/rate-limit failure (reply, harness_error,
    and — only when no probe JSON parsed at all — the raw process output).
    """
    if parsed:
        harness_err = str(parsed.get("harness_error") or "")
        result_err = str((parsed.get("result") or {}).get("harness_error") or "")
        # reply is deliberately NOT searched: it is model text, and a
        # genuine probe outcome may quote these same words (e.g. a model
        # explaining an error class). Only structured harness-level fields
        # and — below — raw output with no parsed JSON at all carry the
        # transient shape authoritatively.
        return bool(_TRANSIENT_RE.search(harness_err)
                    or _TRANSIENT_RE.search(result_err))
    # No JSON parsed at all (rc=2 harness crash, or a CLI-level failure
    # that never reached sdk_probe.py's own json.dumps) — the raw process
    # output is the only place a transient signature could be.
    return bool(_TRANSIENT_RE.search(raw_body))


def _parse_probe_json(body):
    """First complete JSON object in body. Warning prefixes and extra
    concatenated objects (CLI bg-wait ceiling reprint) must not drop it.
    """
    dec = json.JSONDecoder()
    i = body.find("{")
    while i >= 0:
        try:
            obj, end = dec.raw_decode(body, i)
        except ValueError:
            i = body.find("{", i + 1)
            continue
        if isinstance(obj, dict) and "probe" in obj:
            return obj
        i = body.find("{", end)
    return None


def run_probe(probe, cwd, no_plugin, log_path, rc_path, plugin_dir=None):
    """Run one sdk_probe arm. Capture stdout+stderr to log_path, rc to rc_path.

    Never pipes: Popen with files, wait, write rc from the process itself.
    Kill at ARM_TIMEOUT_S so a wandering plugin arm cannot burn minutes.

    plugin_dir, when set, is passed via PROOFPUNK_PLUGIN_DIR so the probe
    loads a scratch/neutered plugin copy instead of the real tree — used
    solely by the install counterfactual arm.
    """
    cmd = [sys.executable, PROBE, probe, "--cwd", cwd]
    if no_plugin:
        cmd.append("--no-plugin")
    with open(log_path, "w", encoding="utf-8") as out:
        env = os.environ.copy()
        # Do not wait 600s for background workflows the probe already forbade.
        env["CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS"] = "5000"
        if plugin_dir:
            env["PROOFPUNK_PLUGIN_DIR"] = plugin_dir
        else:
            # Belt-and-suspenders: never let an ambient env var from the
            # calling shell silently redirect a normal arm to a scratch
            # copy it did not ask for.
            env.pop("PROOFPUNK_PLUGIN_DIR", None)
        proc = subprocess.Popen(
            cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT, env=env)
        try:
            rc = proc.wait(timeout=ARM_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            rc = 124
            out.write("\nTIMEOUT after %ss\n" % ARM_TIMEOUT_S)
    with open(rc_path, "w", encoding="utf-8") as fh:
        fh.write(str(rc))
    body = open(log_path, encoding="utf-8").read()
    return rc, _parse_probe_json(body), body


def run_arm_with_retry(label, probe, no_plugin, log_path, rc_path,
                        sandbox_prefix, plugin_dir=None):
    """Run one arm in its OWN fresh per-arm sandbox, retrying up to
    RETRY_MAX times on a transient host-auth/rate-limit shape with
    RETRY_BACKOFF_S seconds between attempts. Tears the sandbox down
    (shutil.rmtree) after EVERY attempt including the last — sdk_probe.py
    computes every effect check (CLAUDE.md existence, markers, sentinel
    surfaced, etc.) INSIDE its own subprocess and writes them into the
    parsed JSON before that subprocess exits, so this caller never needs
    to inspect the sandbox filesystem itself afterward. A retry gets a
    FRESH sandbox, never a reused one that might carry a partial prior
    write from the attempt that failed.

    Returns (rc, parsed_json, raw_body, attempts, still_transient).
    still_transient=True means every retry hit the host-contention shape —
    the arm's checks are NOT a genuine authenticated probe result and must
    be reported UNVERIFIED, never a real model-behavior failure.
    """
    attempts = 0
    rc, parsed, body = None, None, ""
    log_base, log_ext = os.path.splitext(log_path)
    rc_base, rc_ext = os.path.splitext(rc_path)
    still_transient = False
    while attempts < RETRY_MAX:
        attempts += 1
        sandbox = tempfile.mkdtemp(prefix=sandbox_prefix)
        # Each attempt gets its OWN log/rc so a retry never overwrites the
        # prior attempt's evidence of the transient failure — auditable
        # per-attempt history, not a silently erased log.
        attempt_log = f"{log_base}.attempt{attempts}{log_ext}"
        attempt_rc = f"{rc_base}.attempt{attempts}{rc_ext}"
        try:
            print(f"== {label} (attempt {attempts}/{RETRY_MAX}, sandbox={sandbox})",
                  flush=True)
            rc, parsed, body = run_probe(probe, sandbox, no_plugin, attempt_log,
                                         attempt_rc, plugin_dir=plugin_dir)
        finally:
            shutil.rmtree(sandbox, ignore_errors=True)
        # Mirror the CURRENT attempt to the canonical (unsuffixed) path so
        # any downstream artifact "log" field keeps working — this is
        # overwritten each attempt, but the .attemptN files preserve every
        # attempt's own evidence untouched.
        shutil.copyfile(attempt_log, log_path)
        shutil.copyfile(attempt_rc, rc_path)
        still_transient = is_transient_harness_error(rc, parsed, body)
        if not still_transient:
            break
        if attempts < RETRY_MAX:
            print(f"   transient host error on {label}, "
                  f"backing off {RETRY_BACKOFF_S}s before retry", flush=True)
            time.sleep(RETRY_BACKOFF_S)
        else:
            print(f"   RETRY_MAX ({RETRY_MAX}) exhausted for {label} — still "
                  f"transient (host auth/rate-limit contention did not clear "
                  f"within {(RETRY_MAX - 1) * RETRY_BACKOFF_S}s of backoff). "
                  f"This arm's checks are NOT a genuine authenticated probe "
                  f"result and must be reported UNVERIFIED, never as a real "
                  f"model-behavior failure.", flush=True)
    return rc, parsed, body, attempts, still_transient


def classify(cmd, plugin, control):
    """Name the proof level from observed checks. Never inflate."""
    # A harness/API failure on the plugin arm (auth flap, ResultError,
    # CLI exit 2) contaminates every downstream field — init data like
    # slash_registered arrives BEFORE the model call fails, so checks can
    # read as satisfied on a session that never executed. No proof level
    # may be derived from it: this is FAIL with the reason named, and the
    # retry wrapper classifies the same shape as transient and re-runs it.
    if plugin:
        p_harness_err = bool(
            plugin.get("harness_error")
            or (plugin.get("result") or {}).get("harness_error"))
        if p_harness_err:
            return dict(
                level="FAIL",
                plugin_pass=False,
                control_failed=not bool(control and control.get("pass")),
                reason=("plugin arm recorded a harness error (auth/API "
                        "failure) — init-level fields are not execution "
                        "proof"),
            )
    p_ok = bool(plugin and plugin.get("pass"))
    c_fail = not bool(control and control.get("pass"))
    p_checks = (plugin or {}).get("checks") or {}
    if not p_ok or not c_fail:
        return dict(
            level="FAIL",
            plugin_pass=p_ok,
            control_failed=c_fail,
            reason="plugin arm did not pass or control arm did not fail",
        )
    slash_ok = bool(p_checks.get("slash_registered"))
    local_ok = bool(p_checks.get("local_plugin_loaded"))
    expanded = bool(p_checks.get("slash_expanded"))
    skill_ok = bool(p_checks.get("tool_succeeded")) if cmd["skill"] else None
    text_ok = bool(p_checks.get("text_matches"))
    if (cmd["max_level"] == "c" and slash_ok and local_ok and expanded
            and skill_ok and text_ok):
        return dict(
            level="c",
            plugin_pass=True,
            control_failed=True,
            reason=("slash typed+expanded, local plugin, Skill succeeded, "
                    "marker observed"),
        )
    if slash_ok and local_ok and expanded:
        return dict(
            level="playbook-recognition",
            plugin_pass=True,
            control_failed=True,
            reason=("slash typed+expanded + local plugin; no backing "
                    "skill/script executed (or Skill not required)"),
        )
    return dict(
        level="partial",
        plugin_pass=True,
        control_failed=True,
        reason="probe checks passed but required chain pieces missing",
        checks=p_checks,
    )


# The exact named checks sdk_probe.py's effect_kind branches write into
# checks{} — see cmd_slash_install_effect / cmd_slash_verify_effect in
# tools/sdk_probe.py. Gating on these explicit names (rather than trusting
# the probe's aggregate `pass`) means a future unrelated check added to
# the same probe cannot silently satisfy this promotion, and a check
# renamed/removed there fails LOUD here instead of vacuously passing.
INSTALL_EFFECT_CHECKS = (
    "write_attempted", "write_succeeded", "claude_md_exists",
    "markers_present", "within_200_lines", "template_substituted",
)
# SEMANTICS (revised 2026-09-13, name deliberately unchanged):
# `write_attempted` means "a first-party write TARGETING THIS ARTIFACT was
# attempted" — not "the SDK Write tool was used". It is satisfied by Write,
# Edit, or a Bash redirect, and in every case only when the resolved target
# equals this arm's CLAUDE.md. commands/install.md says "Write or merge the
# memory file" and its acceptance criteria constrain the RESULT (exists,
# <=200 lines, correct platform name, marker-delimited, nothing outside the
# markers edited) without mandating a tool, so mechanism is not the contract.
#
# The name is kept because this tuple is the promotion gate: renaming a check
# here fails LOUD, which is the point. Mechanism is still visible in the
# probe's `write_tool_used` and `write_mechanism` fields, which are RECORDED
# and never gate.
#
# FOURTH CRITERION — commands/install.md requires "the verification block at
# the end was actually run, output in the report". sdk_probe now emits
# `verification_block_run`: a Bash call that references THIS arm's artifact
# (resolved against the effective cwd, not by basename) AND runs both of the
# block's distinguishing probes (`wc -l` plus `grep -c proofpunk:begin`),
# with a completed non-error result.
#
# It is deliberately NOT in the tuple above yet. Adding a check here changes
# the promotion verdict, and this one has not been observed passing on a live
# run: the only recorded evidence truncates tool input at 200 chars
# (sdk_probe ~612), which severs the command BEFORE its grep, so replay
# cannot confirm it. At runtime the predicate reads the live dict and would
# match, but "would" is not evidence.
#
# Promote it into INSTALL_EFFECT_CHECKS once a live install arm reports
# verification_block_run=True. Until then it is RECORDED, not gating, and the
# fourth criterion stays UNVERIFIED — a known gap, not a silent pass.
VERIFY_EFFECT_CHECKS = (
    "bash_attempted", "bash_executed", "sentinel_seeded", "sentinel_surfaced",
)


def promote_to_effect_proven(base_verdict, effect_json, effect_kind,
                              require_counterfactual=False,
                              counterfactual_json=None,
                              scratch_plugin_dir=None):
    """Upgrade a 'playbook-recognition' base verdict to 'd' (effect-proven)
    when EVERY named effect check for `effect_kind` is explicitly True in
    the effect probe's own checks{} dict, and — when
    require_counterfactual is True (install only) — the SAME effect probe
    run against a scratch plugin
    whose command doc body is neutered shows the effect gone while slash
    registration still works.

    NEVER promotes a verdict that is not already 'playbook-recognition':
    a base FAIL/partial stays exactly what it was, regardless of what the
    effect probe reports — the base arm's own anti-vacuity property (its
    control arm failed) is the prerequisite, not a substitute, for this
    promotion.

    NEVER promotes on a harness error: effect_json (or, for install,
    counterfactual_json) being None — a parse failure or an error that
    survived every retry — is reported as-is, never silently treated as
    passing.

    Trusting the effect probe's aggregate `pass` field alone would also
    accept a probe whose `checks` dict silently dropped a named key (a
    missing key reads as falsy under .get(), so this still fails closed
    even then) — but gating on the EXPLICIT named list additionally
    means the row's effect_reason names exactly which check failed,
    rather than a bare "pass=False".
    """
    if base_verdict["level"] != "playbook-recognition":
        out = dict(base_verdict)
        out["effect_proven"] = False
        out["effect_reason"] = (
            f"base level is {base_verdict['level']!r}, not "
            f"'playbook-recognition' — promotion requires that prerequisite")
        return out

    if effect_json is None:
        out = dict(base_verdict)
        out["effect_proven"] = False
        out["effect_reason"] = "effect probe produced no parseable result (harness error)"
        return out

    e_checks = effect_json.get("checks") or {}
    if effect_kind == "install":
        required = INSTALL_EFFECT_CHECKS
    elif effect_kind == "verify":
        required = VERIFY_EFFECT_CHECKS
    else:
        raise ValueError(
            f"promote_to_effect_proven: unknown effect_kind {effect_kind!r} "
            "— must be exactly 'install' or 'verify', never silently "
            "defaulted")
    failed_names = [n for n in required if e_checks.get(n) is not True]
    if failed_names:
        out = dict(base_verdict)
        out["effect_proven"] = False
        out["effect_reason"] = (
            f"effect probe named checks not all True: failed={failed_names} "
            f"observed={ {n: e_checks.get(n) for n in required} }")
        return out

    # SCOPE OF THIS PROMOTION (install): the gate above proves the ARTIFACT
    # and its content. commands/install.md also requires that the command ran
    # its own verification block. That criterion is measured by
    # `verification_block_run`, which is NOT in the gate (see the note above
    # INSTALL_EFFECT_CHECKS: it has never been observed passing live, because
    # persisted tool input truncates before the block's grep).
    #
    # Promotion therefore must NOT claim the command doc is fully satisfied.
    # Record the criterion's observed state on the row so a reader sees the
    # gap instead of inferring completeness from level 'd'. A comment alone
    # would not do this — the row is what downstream reporting reads.
    if effect_kind == "install":
        vbr = e_checks.get("verification_block_run")
        if vbr is not True:
            unproven = ("verification_block_run" if vbr is False
                        else "verification_block_run (not reported)")
        else:
            unproven = None

    if require_counterfactual:
        # counterfactual_json arriving as None (harness error on the
        # counterfactual arm itself — build failure, retry exhaustion)
        # is DISTINCT from "no counterfactual required" (verify's path,
        # where require_counterfactual is False and this block never
        # runs at all) — a required-but-missing counterfactual MUST block
        # promotion, never be silently treated as satisfied.
        if counterfactual_json is None:
            out = dict(base_verdict)
            out["effect_proven"] = False
            out["effect_reason"] = (
                "counterfactual arm required but produced no parseable "
                "result (harness error) — cannot confirm the effect is "
                "attributable to the command doc")
            return out
        cf_checks = counterfactual_json.get("checks") or {}
        # A crash before the mutation could even be exercised (auth
        # failure, CLI-level error, timeout) must NOT be mistaken for the
        # mutation working as intended — require the counterfactual arm
        # actually ran to completion (no harness_error recorded) rather
        # than inferring this indirectly from slash_registered alone.
        cf_no_harness_error = not bool(
            counterfactual_json.get("harness_error")
            or (counterfactual_json.get("result") or {}).get("harness_error"))
        # Plugin IDENTITY: local_plugin_loaded is True for ANY plugin
        # whose resolved path matches sdk_probe.py's PLUGIN constant —
        # including a scratch copy under PROOFPUNK_PLUGIN_DIR, since
        # PLUGIN itself resolves that env var. So local_plugin_loaded
        # alone cannot distinguish "loaded the scratch mutation" from
        # "loaded the real tree" (e.g. if PROOFPUNK_PLUGIN_DIR failed to
        # propagate to the subprocess). plugin_path (added to
        # sdk_probe.py's output specifically for this) is the resolved
        # PLUGIN the probe process actually used — require it EQUALS the
        # scratch dir this caller built, realpath-compared so a /var vs
        # /private/var symlink difference cannot false-negative.
        cf_reported_path = counterfactual_json.get("plugin_path")
        cf_identity_ok = bool(
            scratch_plugin_dir and cf_reported_path
            and os.path.realpath(str(cf_reported_path))
            == os.path.realpath(scratch_plugin_dir)
            and os.path.realpath(str(cf_reported_path))
            != os.path.realpath(REAL_PLUGIN))
        # The counterfactual's own probe-level `pass` MUST be explicitly
        # False — the mutation (neutered install.md body) is EXPECTED to
        # break write_succeeded/claude_md_exists, so if `pass` somehow
        # came back True the counterfactual did not actually mutate
        # anything (a no-op neutering, or the probe ran against the real
        # tree by mistake) and proves nothing.
        cf_pass_is_false = (counterfactual_json.get("pass") is False)
        # write_succeeded absent (not just claude_md_exists) proves the
        # WRITE ITSELF never happened, not merely that some other check
        # in the chain incidentally failed while a write still landed.
        cf_write_absent = (cf_checks.get("write_succeeded") is False)
        cf_effect_absent = (cf_checks.get("claude_md_exists") is False)
        cf_slash_still_ok = bool(cf_checks.get("slash_registered"))
        if not (cf_no_harness_error and cf_identity_ok and cf_pass_is_false
                and cf_write_absent and cf_effect_absent and cf_slash_still_ok):
            out = dict(base_verdict)
            out["effect_proven"] = False
            out["effect_reason"] = (
                "counterfactual did not isolate the command doc as the "
                f"cause: harness_error_present={(not cf_no_harness_error)!r} (want False), "
                f"plugin_identity_ok={cf_identity_ok!r} (want True; "
                f"reported_path={cf_reported_path!r} scratch={scratch_plugin_dir!r}), "
                f"pass={counterfactual_json.get('pass')!r} (want False), "
                f"write_succeeded={cf_checks.get('write_succeeded')!r} (want False), "
                f"claude_md_exists={cf_checks.get('claude_md_exists')!r} (want False), "
                f"slash_registered={cf_checks.get('slash_registered')!r} (want True)")
            return out

    # `d` means the gated checks held — NOT that every acceptance criterion
    # in the command doc is satisfied. When a criterion is measured but not
    # gated, say so ON THE ROW: downstream reporting reads the row, not the
    # source comments, and a bare "effect-proven" would overclaim.
    partial_of = unproven if effect_kind == "install" else None
    return dict(
        # A PARTIAL promotion gets its own level string. Labelling a row
        # while leaving level="d" is not enough: gauge-report.py counts
        # `reached_level in ("c","d")` and this module's own full-chain
        # counter tests `level in ("c","d")` — both read the LEVEL, never a
        # sibling flag, so a partial would have counted as fully proven.
        # "d-partial" is deliberately NOT in those tuples, so it fails closed
        # everywhere until the missing criterion is actually gated.
        level=("d-partial" if partial_of else "d"),
        plugin_pass=True,
        control_failed=True,
        # effect_proven stays FALSE while any measured acceptance criterion
        # is unproven: the name means "the command's effect is proven", and
        # that is not true when install.md's fourth criterion is unverified.
        effect_proven=not partial_of,
        effect_partial=bool(partial_of),
        effect_unproven_criteria=([partial_of] if partial_of else []),
        effect_reason=(
            "playbook-recognition base verdict + effect probe checks all "
            "held" + (" + counterfactual isolated the command doc as cause"
                      if require_counterfactual else "")
            + (f" — PARTIAL vs commands/install.md: {partial_of} is measured "
               "but not gated, so this level does NOT claim the command's "
               "fourth acceptance criterion (verification block actually "
               "run) was satisfied" if partial_of else "")),
        reason=("slash typed+expanded, local plugin, playbook-recognition "
                "PLUS observed real effect on disk/execution (never "
                "narration)" + (" — counterfactual confirms the neutered "
                "command doc removes the effect" if require_counterfactual
                else "")),
    )


def build_neutered_install_plugin(dest_dir):
    """Copy the REAL plugin tree to dest_dir, then replace
    commands/install.md's BODY (everything after the frontmatter) with a
    single no-op statement — frontmatter (description, argument-hint) is
    preserved byte-for-byte so slash registration still works identically;
    only the documented STEPS that tell the model to write a file are
    removed.

    This is the counterfactual's whole mechanism: if the effect probe
    still shows claude_md_exists=True against THIS mutated copy, the
    effect was never actually caused by the command doc's steps — it
    would be ambient host behavior masquerading as command-doc-driven
    proof, exactly the class of false positive the reviewer's gap #2
    (write-tool mechanism unnamed) was about.

    Raises on any failure — a counterfactual that silently fails to
    mutate would produce a false 'd' promotion, which is worse than a
    loud crash.
    """
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    shutil.copytree(REAL_PLUGIN, dest_dir)

    install_md = os.path.join(dest_dir, "commands", "install.md")
    with open(install_md, encoding="utf-8") as fh:
        original = fh.read()

    parts = original.split("---", 2)
    if len(parts) != 3:
        raise RuntimeError(
            f"build_neutered_install_plugin: {install_md} does not have "
            f"the expected '---\\nfrontmatter\\n---\\nbody' shape "
            f"(split produced {len(parts)} parts, want 3) — refusing to "
            f"guess at a mutation that might not actually neuter anything")
    frontmatter = parts[1]
    neutered_body = (
        "\n\n# /proofpunk:install — NEUTERED FOR COUNTERFACTUAL TESTING\n\n"
        "This command's documented steps have been deliberately removed. "
        "Do nothing. Do not write, create, or modify any file. Reply with "
        "exactly: NEUTERED_NO_OP\n"
    )
    mutated = f"---{frontmatter}---{neutered_body}"
    with open(install_md, "w", encoding="utf-8") as fh:
        fh.write(mutated)

    if mutated == original:
        raise RuntimeError(
            f"build_neutered_install_plugin: mutation produced byte-"
            f"identical output to the original — this would be a no-op "
            f"counterfactual, which cannot prove anything")
    return install_md


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    n_plugin_pass = 0
    n_control_fail = 0
    n_full_chain = 0
    n_honest_max = 0
    scratch_root = tempfile.mkdtemp(prefix="pp-cmdsurface-scratch-")

    try:
        for i, cmd in enumerate(COMMANDS, 1):
            plug_log = os.path.join(OUT_DIR, f"{cmd['probe']}.plugin.log")
            plug_rc_p = os.path.join(OUT_DIR, f"{cmd['probe']}.plugin.rc")
            ctrl_log = os.path.join(OUT_DIR, f"{cmd['probe']}.control.log")
            ctrl_rc_p = os.path.join(OUT_DIR, f"{cmd['probe']}.control.rc")

            p_rc, p_json, _, p_attempts, p_trans = run_arm_with_retry(
                f"{cmd['slash']} plugin arm", cmd["probe"], False,
                plug_log, plug_rc_p, f"pp-cmdsurface-{cmd['name']}-plugin-")
            c_rc, c_json, _, c_attempts, c_trans = run_arm_with_retry(
                f"{cmd['slash']} --no-plugin control", cmd["probe"], True,
                ctrl_log, ctrl_rc_p, f"pp-cmdsurface-{cmd['name']}-control-")

            verdict = classify(cmd, p_json, c_json)

            row = {
                "command": cmd["name"],
                "slash": cmd["slash"],
                "probe": cmd["probe"],
                "max_honest_level": cmd["max_level"],
                "reached_level": verdict["level"],
                "note": cmd["note"],
                "plugin": {
                    "rc": p_rc,
                    "pass": bool(p_json and p_json.get("pass")),
                    "checks": (p_json or {}).get("checks"),
                    "elapsed_s": (p_json or {}).get("elapsed_s"),
                    "cost_usd": ((p_json or {}).get("result") or {}).get("cost_usd"),
                    "reply": (p_json or {}).get("reply"),
                    "init_slash_proofpunk": (p_json or {}).get("init_slash_proofpunk"),
                    "local_plugin_loaded": (p_json or {}).get("local_plugin_loaded"),
                    "tool_calls": (p_json or {}).get("tool_calls"),
                    "transcript": (p_json or {}).get("transcript"),
                    "log": os.path.relpath(plug_log, ROOT),
                    "attempts": p_attempts,
                    "transient_exhausted": p_trans,
                },
                "control": {
                    "rc": c_rc,
                    "pass": bool(c_json and c_json.get("pass")),
                    "checks": (c_json or {}).get("checks"),
                    "elapsed_s": (c_json or {}).get("elapsed_s"),
                    "cost_usd": ((c_json or {}).get("result") or {}).get("cost_usd"),
                    "reply": (c_json or {}).get("reply"),
                    "init_slash_proofpunk": (c_json or {}).get("init_slash_proofpunk"),
                    "local_plugin_loaded": (c_json or {}).get("local_plugin_loaded"),
                    "tool_calls": (c_json or {}).get("tool_calls"),
                    "transcript": (c_json or {}).get("transcript"),
                    "log": os.path.relpath(ctrl_log, ROOT),
                    "attempts": c_attempts,
                    "transient_exhausted": c_trans,
                },
                "classify": verdict,
            }

            effects_probe = cmd.get("effects_probe")
            if effects_probe:
                eff_log = os.path.join(OUT_DIR, f"{effects_probe}.plugin.log")
                eff_rc_p = os.path.join(OUT_DIR, f"{effects_probe}.plugin.rc")
                e_rc, e_json, _, e_attempts, e_trans = run_arm_with_retry(
                    f"{cmd['slash']} EFFECT arm", effects_probe, False,
                    eff_log, eff_rc_p, f"pp-cmdsurface-{cmd['name']}-effect-")
                row["effect"] = {
                    "rc": e_rc,
                    "pass": bool(e_json and e_json.get("pass")),
                    "checks": (e_json or {}).get("checks"),
                    "elapsed_s": (e_json or {}).get("elapsed_s"),
                    "cost_usd": ((e_json or {}).get("result") or {}).get("cost_usd"),
                    "reply": (e_json or {}).get("reply"),
                    "plugin_path": (e_json or {}).get("plugin_path"),
                    "tool_calls": (e_json or {}).get("tool_calls"),
                    "transcript": (e_json or {}).get("transcript"),
                    "log": os.path.relpath(eff_log, ROOT),
                    "attempts": e_attempts,
                    "transient_exhausted": e_trans,
                }
                if cmd["effect_kind"] == "install":
                    row["effect"]["install_artifact_lines"] = (
                        (e_json or {}).get("install_artifact_lines"))
                else:
                    row["effect"]["verify_sentinel"] = (e_json or {}).get("verify_sentinel")
                    row["effect"]["verify_bash_calls"] = (e_json or {}).get("verify_bash_calls")

                cf_json = None
                cf_attempts = 0
                scratch_plugin_dir = None
                if cmd.get("require_counterfactual"):
                    scratch_plugin_dir = os.path.join(
                        scratch_root, f"{cmd['name']}-neutered-plugin")
                    cf_log = os.path.join(OUT_DIR, f"{effects_probe}.counterfactual.log")
                    cf_rc_p = os.path.join(OUT_DIR, f"{effects_probe}.counterfactual.rc")
                    try:
                        build_neutered_install_plugin(scratch_plugin_dir)
                        cf_rc, cf_json, _, cf_attempts, cf_trans = run_arm_with_retry(
                            f"{cmd['slash']} COUNTERFACTUAL arm", effects_probe,
                            False, cf_log, cf_rc_p,
                            f"pp-cmdsurface-{cmd['name']}-counterfactual-",
                            plugin_dir=scratch_plugin_dir)
                    except Exception as e:
                        cf_rc = 2
                        cf_json = None
                        with open(cf_log, "a", encoding="utf-8") as fh:
                            fh.write(f"\nCOUNTERFACTUAL BUILD ERROR: {type(e).__name__}: {e}\n")
                        with open(cf_rc_p, "w", encoding="utf-8") as fh:
                            fh.write("2")
                    row["counterfactual"] = {
                        "rc": cf_rc,
                        "pass": bool(cf_json and cf_json.get("pass")),
                        "checks": (cf_json or {}).get("checks"),
                        "plugin_path": (cf_json or {}).get("plugin_path"),
                        "scratch_plugin_dir": scratch_plugin_dir,
                        "reply": (cf_json or {}).get("reply"),
                        "log": os.path.relpath(cf_log, ROOT),
                        "attempts": cf_attempts,
                        "transient_exhausted": cf_trans,
                    }

                promoted = promote_to_effect_proven(
                    verdict, e_json, cmd["effect_kind"],
                    require_counterfactual=bool(cmd.get("require_counterfactual")),
                    counterfactual_json=cf_json,
                    scratch_plugin_dir=scratch_plugin_dir,
                )
                row["reached_level"] = promoted["level"]
                row["classify"] = promoted
                verdict = promoted

            if verdict["plugin_pass"]:
                n_plugin_pass += 1
            if verdict["control_failed"]:
                n_control_fail += 1
            if verdict["level"] in ("c", "d"):
                n_full_chain += 1
            if verdict["level"] == cmd["max_level"]:
                n_honest_max += 1

            rows.append(row)
    finally:
        shutil.rmtree(scratch_root, ignore_errors=True)

    harness_errors = []
    for row in rows:
        for arm_name in ("plugin", "control", "effect", "counterfactual"):
            arm = row.get(arm_name)
            if arm is None:
                continue
            # rc=2 is sdk_probe.py's own harness-error exit code (see its
            # main(): "harness_error" printed, sys.exit(2)) — DISTINCT
            # from rc=1, which is an ordinary, EXPECTED probe failure (a
            # control arm is SUPPOSED to fail its checks with rc=1; that
            # is not a harness error). A None checks dict with rc=2 is a
            # harness failure that survived every retry, never a probe
            # result — must be visible at the top level, not buried in a
            # per-row reply.
            if arm.get("rc") == 2 or arm.get("checks") is None:
                harness_errors.append({
                    "command": row["command"], "arm": arm_name,
                    "rc": arm.get("rc"), "attempts": arm.get("attempts"),
                    "log": arm.get("log"),
                })

    summary = {
        "measured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness": "tools/sdk_probe.py + tools/verify-command-surface.py",
        "levels": {
            "a": "script-level (not this harness)",
            "b": "skill-load via Skill tool by name (cmd_truth_audit_flags / cmd_rate_prompt_flag)",
            "c": "slash typed -> registered -> mapped skill ran -> marker observed",
            "playbook-recognition": "slash registered + command-doc marker; no skill/script",
            "d": ("effect-proven — playbook-recognition + an OBSERVED real "
                  "effect on disk/execution (never narration); install "
                  "additionally requires a counterfactual proving the "
                  "effect is attributable to the command doc, not ambient "
                  "host behavior"),
        },
        "full_chain": f"{n_full_chain}/6",
        "plugin_pass": f"{n_plugin_pass}/6",
        "control_fail": f"{n_control_fail}/6",
        "honest_max_reached": f"{n_honest_max}/6",
        "harness_errors": harness_errors,
        "install_verify_honest_max_is_d": True,
        "install_reason": next(c["note"] for c in COMMANDS if c["name"] == "install"),
        "verify_reason": next(c["note"] for c in COMMANDS if c["name"] == "verify"),
        "commands": rows,
    }
    tmp = ARTIFACT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, ARTIFACT)
    digest = sha256_of(ARTIFACT)
    print(f"ARTIFACT {os.path.relpath(ARTIFACT, ROOT)} sha256:{digest}")
    print(f"full_chain={summary['full_chain']} "
          f"plugin_pass={summary['plugin_pass']} "
          f"control_fail={summary['control_fail']} "
          f"honest_max={summary['honest_max_reached']}")
    if harness_errors:
        print(f"HARNESS ERRORS ({len(harness_errors)}): "
              f"{[(h['command'], h['arm']) for h in harness_errors]}")

    # 6/6 at each command's own honest maximum (c for the four
    # skill-backed commands, d for install/verify) + every control
    # arm failed. A harness error on any required arm (plugin,
    # control, effect, or install's counterfactual) prevents that
    # command's verdict from reaching its max_level, so it already
    # fails n_honest_max without any separate special-case here —
    # this is intentionally NOT an inflated 6/6 by counting playbook-
    # recognition or FAIL as if it were c/d. harness_errors is checked
    # explicitly too, as defense in depth — a green artifact must never
    # coexist with a recorded harness error on any required arm.
    ok = (n_plugin_pass == 6 and n_control_fail == 6 and n_honest_max == 6
          and not harness_errors)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
