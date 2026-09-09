#!/usr/bin/env python3
"""End-user probe: drive a real Claude session with the proofpunk plugin loaded.

This is the instrument the repo was missing. `test-hooks.sh` executes hook
scripts in isolation, which proves a script's output shape and nothing about
whether the host loads the plugin, surfaces its skills, or fires its hooks.
This drives an actual session and observes what really happens.

Usage:
    python3 tools/sdk_probe.py <probe-name> [--cwd DIR] [--no-plugin]

Emits one JSON object on stdout. Exit 0 if the probe's expectation held,
1 if it did not, 2 on harness error (never conflated with a failed probe).
"""
import argparse
import asyncio
import json
import os
import secrets
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Counterfactual support: verify-command-surface.py points this at a scratch
# copy of the plugin with commands/install.md's body neutered, to prove the
# install effect probe's checks disappear when the playbook itself cannot
# act — never set outside that one arm, so every other probe invocation
# resolves to the real tree under test.
PLUGIN = os.environ.get("PROOFPUNK_PLUGIN_DIR") or os.path.join(REPO, "plugins", "proofpunk")

try:
    from claude_agent_sdk import (
        ClaudeAgentOptions,
        SdkPluginConfig,
        query,
        AssistantMessage,
        SystemMessage,
        ResultMessage,
        HookEventMessage,
        TextBlock,
        ToolUseBlock,
        UserMessage,
        ToolResultBlock,
        ResultError,
    )
except ImportError as e:
    print(json.dumps({"error": f"claude-agent-sdk missing: {e}",
                      "fix": "pip install --upgrade claude-agent-sdk"}))
    sys.exit(2)


PROBES = {
    # Does the host actually deliver the SessionStart doctrine into context?
    "doctrine": dict(
        prompt=("Search your session context for a block that begins with the word "
                "'Proofpunk'. If you find one, reply with its first six words "
                "verbatim and nothing else. If there is no such block, reply "
                "exactly NO_SUCH_BLOCK."),
        expect_text="Proofpunk is installed",
        why="SessionStart hook must place doctrine in the live session",
    ),
    # Are the plugin's skills actually loadable FROM THE PLUGIN? All delivery
    # skills also exist standalone in ~/.claude/skills on this host,
    # so a bare name proves nothing — the control arm loaded `end-user-testing` with the
    # plugin absent. Only the namespaced `proofpunk:` form is unambiguous.
    "skills_listed": dict(
        prompt=("Invoke the skill named exactly 'proofpunk:end-user-testing' "
                "using the Skill tool. After it loads, state in one line what it "
                "says the only acceptable form of proof is."),
        expect_text="end-user",
        require_tool="Skill",
        require_tool_arg="proofpunk:end-user-testing",
        why="plugin skills must load from the plugin, not a same-named local copy",
    ),
    # Does the router skill actually LOAD? A self-report can be hallucinated,
    # and the control arm proved the model will read SKILL.md off disk instead.
    # Require an observed `Skill` call plus a successful tool result.
    "router": dict(
        prompt=("Invoke the skill named exactly 'proofpunk' using the Skill tool. "
                "After it loads, quote verbatim the first row of its "
                "'Skill calls' table."),
        expect_text="brainstorm",     # first row of the router's table
        require_tool="Skill",         # must be an observed invocation
        require_tool_arg="proofpunk", # ...of THIS skill, per the real input
        why="the router is the plugin's only entry point; it must actually load",
    ),
    # Does the no-test-files PreToolUse hook actually block a real write?
    # Verified on the filesystem, not by reading the model's narration.
    # Bash/Agent are disallowed so the model cannot route around the Write
    # hook — otherwise an absent file proves nothing about the guard.
    "blocks_test_file": dict(
        prompt=("Use the Write tool, and only the Write tool, to create the file "
                "/tmp/proofpunk_probe/test_example.py with exactly this content: "
                "def test_x(): assert True"),
        expect_blocked=True,
        artifact="/tmp/proofpunk_probe/test_example.py",
        expect_artifact=False,          # hook denies -> file must NOT exist
        require_write_attempt=True,     # model must actually try, else vacuous
        why="PreToolUse hook must deny test-file writes in a real session",
        allowed_tools=["Write"],
        disallowed_tools=["Bash", "Agent", "Task", "Edit", "NotebookEdit"],
    ),
    # Control: a non-test write must still land on disk with the right bytes.
    "allows_normal_file": dict(
        prompt=("Use the Write tool, and only the Write tool, to create the file "
                "/tmp/proofpunk_probe/notes.md with exactly this content: hello"),
        expect_blocked=False,
        artifact="/tmp/proofpunk_probe/notes.md",
        expect_artifact=True,           # guard permits -> file MUST exist
        expect_content="hello",
        require_write_attempt=True,
        why="the guard must not block ordinary writes (false-positive check)",
        allowed_tools=["Write"],
        disallowed_tools=["Bash", "Agent", "Task", "Edit", "NotebookEdit"],
    ),
    # Does proofpunk's OWN Stop hook run? The hook_response record's
    # `hook_name` is the EVENT, not the script — so identity must come from
    # stdout. stop-guard.sh is SILENT unless it blocks, so a clean turn proves
    # only that the Stop event fired and its hooks exited; that is recorded,
    # not overclaimed as proof of proofpunk's script specifically.
    "stop_guard": dict(
        prompt="Reply with exactly: DONE. The work is complete.",
        expect_text="",                # any reply; the hook record is the proof
        require_hook_event="Stop",
        why="the Stop event must fire and its hooks run in a real session",
    ),
    # Does the InstructionsLoaded tap run? Verified by parsing the JSONL lines
    # this run appended, not by byte growth — other hooks write there too.
    "instructions_loaded": dict(
        prompt="Reply with exactly: OK",
        expect_text="",
        require_hook_event="SessionStart",
        loads_append=True,             # parse new lines, attribute to this run
        why="the InstructionsLoaded memory tap must run when the plugin loads",
    ),
}

# Parameterized namespaced skill-load probes. Each listed delivery skill also
# exists standalone in ~/.claude/skills on this host, so only the `proofpunk:`
# form is attributable to the plugin. Each requires an observed Skill call whose
# argument matches AND whose tool result came back successful.
for _sk in ("implement", "validation-plan", "root-cause-debugging",
            "full-functional-audit", "red-team-eval", "visual-inspection",
            "production-readiness", "codebase-truth-audit",
            "brainstorm", "mobile-validation-runner", "plan-hardening",
            "prompt-forge", "session-intent", "stack-testing",
            "tui-testing", "ui-experience-audit"):
    PROBES[f"skill_{_sk.replace('-', '_')}"] = dict(
        prompt=(f"Invoke the skill named exactly 'proofpunk:{_sk}' using the "
                "Skill tool, then state in one line what it is for."),
        expect_text="",
        require_tool="Skill",
        require_tool_arg=f"proofpunk:{_sk}",
        why=f"'{_sk}' must load from the plugin, not a same-named local copy",
    )

# Command-surface probes. These drive the SLASH COMMANDS a user actually types,
# not the scripts underneath — the command file is the user-facing contract, so
# a doc fix is only end-user proven if the loaded surface carries it.
# cmd_truth_audit_flags / cmd_rate_prompt_flag remain skill-load probes (level
# b): they invoke Skill by name. The cmd_slash_* probes below type the real
# `/proofpunk:<name>` surface (level c, or playbook-recognition for install).
PROBES["cmd_truth_audit_flags"] = dict(
    prompt=("Invoke the skill named exactly 'proofpunk:codebase-truth-audit' "
            "using the Skill tool. Then state, in one line, the exact flag "
            "names its bundled init script accepts for bounding history."),
    expect_text="--start",
    require_tool="Skill",
    require_tool_arg="proofpunk:codebase-truth-audit",
    forbid_text="--since",
    why="the loaded skill must carry --start/--end, not the rejected --since",
)
PROBES["cmd_rate_prompt_flag"] = dict(
    prompt=("Invoke the skill named exactly 'proofpunk:prompt-forge' using the "
            "Skill tool. Then state, in one line, the flag that ships a prompt "
            "scoring below threshold."),
    expect_text="--ship-below-threshold",
    require_tool="Skill",
    require_tool_arg="proofpunk:prompt-forge",
    why="the flag documented in rate-prompt must exist in the loaded skill",
)

# Slash-typed surface. The CLI expands the command file ($ARGUMENTS) before
# the model acts. Level (c) full-chain requires: command in init
# slash_commands, THIS tree's plugin path loaded, mapped Skill succeeded
# (when the command doc says Activate the skill), unique marker observed.
# /proofpunk:install has no backing skill/script — see that probe's why.
_SLASH_SKILL_TOOLS = dict(
    allowed_tools=["Skill"],
    disallowed_tools=["Bash", "Agent", "Task", "Write", "Edit", "NotebookEdit",
                      "Workflow", "ListAgents"],
    max_turns=8,
    require_slash=True,
    require_local_plugin=True,
)
_SLASH_PLAYBOOK_TOOLS = dict(
    disallowed_tools=["Bash", "Agent", "Task", "Write", "Edit", "NotebookEdit",
                      "Workflow", "ListAgents"],
    max_turns=8,
    require_slash=True,
    require_local_plugin=True,
)

PROBES["cmd_slash_implement"] = dict(
    prompt=('/proofpunk:implement "surface-probe only — STOP after the skill '
            'loads. Quote the skill heading and the four flags --parallel '
            '--auto --mine --fast. Do not scout, edit, implement, or call '
            'Workflow."'),
    expect_text="--parallel",
    require_tool="Skill",
    require_tool_arg=("proofpunk:implement",),
    require_slash_name="proofpunk:implement",
    why="slash /proofpunk:implement must expand, activate implement, and surface its flags",
    **_SLASH_SKILL_TOOLS,
)
PROBES["cmd_slash_forge_prompt"] = dict(
    prompt=('/proofpunk:forge-prompt "surface-probe only — STOP after the '
            'skill loads. Quote AUTHOR mode and the --depth flag. Do not '
            'write a prompt file or call Workflow."'),
    expect_text="--depth",
    require_tool="Skill",
    require_tool_arg=("proofpunk:prompt-forge", "proofpunk:forge-prompt"),
    require_slash_name="proofpunk:forge-prompt",
    why="slash /proofpunk:forge-prompt must expand and activate prompt-forge AUTHOR",
    **_SLASH_SKILL_TOOLS,
)
PROBES["cmd_slash_rate_prompt"] = dict(
    prompt=('/proofpunk:rate-prompt "surface-probe only — STOP after the '
            'skill loads. Quote --ship-below-threshold and --report-only. '
            'Do not rate a file or call Workflow."'),
    expect_text="--ship-below-threshold",
    require_tool="Skill",
    require_tool_arg=("proofpunk:prompt-forge", "proofpunk:rate-prompt"),
    require_slash_name="proofpunk:rate-prompt",
    why="slash /proofpunk:rate-prompt must expand, pass flags, activate prompt-forge RATE",
    **_SLASH_SKILL_TOOLS,
)
PROBES["cmd_slash_truth_audit"] = dict(
    prompt=('/proofpunk:truth-audit . --start 2026-01-01 --end 2026-08-13 '
            '--label cmdsurface'),
    # Flags are the documented surface. STOP cannot be a positional the
    # playbook will audit. Host may surface the command as skill
    # proofpunk:truth-audit — both names count.
    expect_text="--start",
    forbid_text="unrecognized arguments",
    require_tool="Skill",
    require_tool_arg=("proofpunk:codebase-truth-audit", "proofpunk:truth-audit"),
    require_slash_name="proofpunk:truth-audit",
    why="slash /proofpunk:truth-audit must expand with --start/--end into codebase-truth-audit",
    **_SLASH_SKILL_TOOLS,
)
PROBES["cmd_slash_verify"] = dict(
    prompt=('/proofpunk:verify "STOP. Quote: Unexecuted checks are UNVERIFIED. '
            'There are no flags. Do not start a runtime. Do not call tools."'),
    expect_text="",
    require_slash_name="proofpunk:verify",
    why=("slash /proofpunk:verify is a playbook (no Activate-skill line); "
         "prove expansion + unique command-doc marker"),
    **_SLASH_PLAYBOOK_TOOLS,
)
PROBES["cmd_slash_install"] = dict(
    prompt=("/proofpunk:install --platform claude-code --no-rules"),
    expect_text="",
    require_slash_name="proofpunk:install",
    why=("slash /proofpunk:install is an in-session playbook with NO backing "
         "skill or script; SDK sessions here have no Write tool so the "
         "playbook cannot execute a file merge. This probe proves slash "
         "registration + playbook recognition (doctrine marker quoted), "
         "not file-write execution."),
    **_SLASH_PLAYBOOK_TOOLS,
)

# Effect probes (level "d" — playbook-recognition PLUS the observed real
# effect, not the model's narration of it). install/verify have no backing
# skill/script to reach level (c) via a Skill-tool call, so their higher
# proof bar is: did the documented playbook ACTUALLY produce its effect on
# disk (install) or actually RUN a real command against the sandbox
# (verify)?
#
# Reviewer gap #1: the SEALED cmd_slash_install evidence shows the plugin
# arm writing via an AMBIENT mcp__filesystem__write_file MCP tool
# (command-surface-proof.json:888), not first-party Write — `_SLASH_
# PLAYBOOK_TOOLS`'s `disallowed_tools=[..., "Write", "Edit", ...]` only
# removes THOSE named tools; it does nothing to stop an ambient MCP
# filesystem server (loaded via default `setting_sources` from project
# .mcp.json / user or plugin config) from satisfying the same effect.
# `allowed_tools` only auto-approves tools already present — with
# `permission_mode="bypassPermissions"` every tool is already
# auto-approved regardless, so `allowed_tools` grants nothing here either.
#
# The hermetic fix: `strict_mcp_config=True` with no `mcp_servers` passed
# excludes ALL ambient MCP configuration the CLI would otherwise load
# (project .mcp.json, user/global settings, plugin-provided servers) —
# per ClaudeAgentOptions' own doc for that field. With no MCP server
# reachable, the only way the model can write or run a command is a real
# first-party Write/Edit/Bash call, which the checks below verify landed
# on disk / executed for real rather than being narrated.
_EFFECT_TOOLS_INSTALL = dict(
    disallowed_tools=["Agent", "Task", "NotebookEdit", "Workflow", "ListAgents"],
    strict_mcp_config=True,
    max_turns=12,
)
_EFFECT_TOOLS_VERIFY = dict(
    disallowed_tools=["Write", "Edit", "Agent", "Task", "Workflow", "ListAgents"],
    strict_mcp_config=True,
    max_turns=10,
)
PROBES["cmd_slash_install_effect"] = dict(
    prompt=("/proofpunk:install --platform claude-code --no-rules"),
    expect_text="",
    require_slash_name="proofpunk:install",
    require_local_plugin=True,
    effect_kind="install",
    why=("does /proofpunk:install actually WRITE the memory file via a "
         "real first-party Write/Edit call, not an ambient MCP tool and "
         "not just narration? strict_mcp_config excludes every ambient "
         "MCP server so no mcp__filesystem__write_file substitute is "
         "reachable. The verdict rests on the sandbox filesystem "
         "afterwards — CLAUDE.md exists, both proofpunk:begin/end markers "
         "present, at or under the documented 200-line ceiling, and every "
         "{{PLACEHOLDER}} substituted — never on the model's self-report."),
    **_EFFECT_TOOLS_INSTALL,
)
PROBES["cmd_slash_verify_effect"] = dict(
    prompt=('/proofpunk:verify "use the Bash tool to run `ls -la` in this '
            'directory and report exactly what it prints"'),
    expect_text="",
    require_slash_name="proofpunk:verify",
    require_local_plugin=True,
    effect_kind="verify",
    why=("does /proofpunk:verify actually RUN Bash against the sandbox, "
         "not just recognize the slash command and narrate what it would "
         "do? A per-run cryptographically random sentinel filename is "
         "seeded into the sandbox before the session starts — the model "
         "cannot know or guess it. Verdict rests on that exact sentinel "
         "appearing in a genuinely-executed (is_error is not True, non-empty) "
         "Bash tool_result payload, which only the real host/CLI executing "
         "`ls` against this sandbox can populate; the model's reply text "
         "is never inspected for this check, so narration cannot forge it."),
    **_EFFECT_TOOLS_VERIFY,
)


def _realpath(p):
    try:
        return os.path.realpath(p)
    except OSError:
        return str(p)


def _local_plugin_loaded(plugins):
    """True only if THIS checkout's plugins/proofpunk path is in init plugins.

    A marketplace cache copy (proofpunk@proofpunk-marketplace) must not
    satisfy this — that is ambient host state, not the tree under test.
    """
    want = _realpath(PLUGIN)
    for p in plugins or []:
        if not isinstance(p, dict):
            continue
        path = _realpath(str(p.get("path", "") or ""))
        if path == want or path.startswith(want + os.sep):
            return True
    return False


async def run(name: str, cwd: str, use_plugin: bool) -> dict:
    spec = PROBES[name]

    # Clean the artifact before the arm so a stale file from a prior run can
    # never be mistaken for this run's outcome.
    artifact = spec.get("artifact")
    if artifact:
        os.makedirs(os.path.dirname(artifact), exist_ok=True)
        if os.path.exists(artifact):
            os.remove(artifact)

    # Verify-effect sentinel: an unguessable per-run filename seeded into
    # the sandbox BEFORE the session starts. A model that never actually
    # runs a real command against this cwd has no way to know it — a
    # hallucinated "I see 3 files" narration cannot name it. Only a
    # genuine Bash listing/read against THIS cwd can surface it.
    verify_sentinel = None
    if spec.get("effect_kind") == "verify":
        verify_sentinel = f"pp-sentinel-{secrets.token_hex(8)}.txt"
        try:
            with open(os.path.join(cwd, verify_sentinel), "w", encoding="utf-8") as fh:
                fh.write("proofpunk-verify-effect-sentinel\n")
        except OSError:
            verify_sentinel = None

    opts = dict(
        cwd=cwd,
        permission_mode="bypassPermissions",
        include_hook_events=True,
        max_turns=int(spec.get("max_turns", 8)),
    )
    if use_plugin:
        opts["plugins"] = [SdkPluginConfig(type="local", path=PLUGIN)]
    else:
        # Control arm: exclude ambient user/project settings so a stale
        # duplicate hook elsewhere on the host cannot contaminate the result.
        opts["setting_sources"] = []
    # `allowed_tools` only FILTERS the session's existing tool set; it cannot
    # grant a tool the session lacks.
    if "allowed_tools" in spec:
        opts["allowed_tools"] = spec["allowed_tools"]
    if "disallowed_tools" in spec:
        opts["disallowed_tools"] = spec["disallowed_tools"]
    if spec.get("strict_mcp_config"):
        # Exclude every ambient MCP server (project .mcp.json, user/global
        # settings, plugin-provided servers) so an unnamed MCP tool cannot
        # substitute for the first-party tool under test. No mcp_servers
        # dict is passed, so the effective MCP surface is empty.
        opts["strict_mcp_config"] = True

    text, hooks, tools, denials = [], [], [], []
    hook_runs = []           # identity + outcome of each hook script that ran
    transcript = []          # compact session trace for the command-surface artifact
    init_slash, init_plugins = [], []

    # Snapshot the loads tap by LINE COUNT so only lines this run appended are
    # parsed. Byte growth alone proves nothing — other hooks write here too.
    loads_path = os.path.expanduser("~/.claude/proofpunk-loads.jsonl")
    loads_before = 0
    if spec.get("loads_append") and os.path.exists(loads_path):
        with open(loads_path) as fh:
            loads_before = sum(1 for _ in fh)
    tool_calls = []          # name + real input dict, so arguments are checkable
    result = {}
    session_completed = False  # set ONLY on ResultMessage / ResultError,
                               # never inferred from result being non-empty
    t0 = time.time()

    try:
        try:
            stream = query(prompt=spec["prompt"], options=ClaudeAgentOptions(**opts))
            async for msg in stream:
                if isinstance(msg, AssistantMessage):
                    for b in msg.content:
                        if isinstance(b, TextBlock):
                            text.append(b.text)
                            transcript.append({"kind": "text", "text": b.text[:500]})
                        elif isinstance(b, ToolUseBlock):
                            tools.append(b.name)
                            tool_calls.append({"id": b.id, "name": b.name,
                                               "input": b.input, "result": None,
                                               "is_error": None})
                            transcript.append({"kind": "tool_use", "name": b.name,
                                               "input": json.dumps(b.input)[:300]})
                elif isinstance(msg, UserMessage):
                    # Tool results arrive as user turns. An invocation that returned
                    # "Unknown skill" is an ATTEMPT, not a load — tie each result back
                    # to its call so the verdict can tell those apart.
                    for b in (msg.content if isinstance(msg.content, list) else []):
                        if isinstance(b, ToolResultBlock):
                            for c in tool_calls:
                                if c["id"] == b.tool_use_id:
                                    c["result"] = str(b.content)[:300]
                                    c["is_error"] = b.is_error
                                    transcript.append({
                                        "kind": "tool_result",
                                        "is_error": b.is_error,
                                        "content": str(b.content)[:300],
                                    })
                elif isinstance(msg, HookEventMessage):
                    hooks.append(msg.hook_event_name)
                    data = getattr(msg, "data", {}) or {}
                    # hook_response carries the outcome of a hook that ran. NOTE:
                    # `hook_name` is the EVENT ("Stop", "SessionStart:startup"), not the
                    # script filename — script identity is only visible via stdout.
                    if data.get("subtype") == "hook_response":
                        hook_runs.append({
                            "event": data.get("hook_event"),
                            "name": data.get("hook_name"),
                            "exit_code": data.get("exit_code"),
                            "outcome": data.get("outcome"),
                            "stdout": str(data.get("stdout", ""))[:300],
                        })
                elif isinstance(msg, SystemMessage):
                    data = getattr(msg, "data", {}) or {}
                    if msg.subtype == "init" or data.get("subtype") == "init":
                        init_slash = list(data.get("slash_commands") or [])
                        init_plugins = data.get("plugins") or []
                        transcript.append({
                            "kind": "init",
                            "slash_proofpunk": [c for c in init_slash
                                                if str(c).startswith("proofpunk:")],
                            "local_plugin": _local_plugin_loaded(init_plugins),
                        })
                    if "refusing to create a test artifact" in json.dumps(data):
                        denials.append("no-test-files")
                elif isinstance(msg, ResultMessage):
                    session_completed = True
                    result = {"is_error": msg.is_error, "num_turns": msg.num_turns,
                              "cost_usd": msg.total_cost_usd}
        except ResultError as e:
            # max-turns / CLI terminal error: keep init + partial transcript.
            session_completed = True
            result = {
                "is_error": True,
                "num_turns": None,
                "cost_usd": None,
                "harness_error": f"ResultError: {e}",
            }
            transcript.append({"kind": "result_error", "error": str(e)[:400]})
    finally:
        # The sentinel exists solely to prove real Bash execution DURING
        # this run; leaving it behind could pollute a directory listing a
        # later check inspects (e.g. install's cwd scan) or a reused
        # sandbox. Always attempt cleanup, success or failure.
        if verify_sentinel:
            try:
                os.remove(os.path.join(cwd, verify_sentinel))
            except OSError:
                pass

    joined = "".join(text)
    # A denial shows up either as a system event or as the model reporting it.
    blocked = bool(denials) or "refusing to create a test artifact" in joined

    out = {
        "probe": name, "why": spec["why"], "plugin_loaded": use_plugin,
        # Resolved PLUGIN path this process actually used (module-level
        # constant, which already honors PROOFPUNK_PLUGIN_DIR). Exposed so
        # a caller can assert counterfactual identity precisely — that a
        # scratch/neutered copy, not the real tree, was what loaded —
        # rather than inferring it indirectly from local_plugin_loaded
        # (which is True for ANY plugin whose path matches PLUGIN,
        # including a scratch one under PROOFPUNK_PLUGIN_DIR).
        "plugin_path": PLUGIN,
        "elapsed_s": round(time.time() - t0, 1),
        "reply": joined.strip()[:400],
        "hook_events": sorted(set(hooks)), "tools_used": sorted(set(tools)),
        "hook_runs": hook_runs,
        "tool_calls": [{"name": c["name"], "input": json.dumps(c["input"])[:200]}
                       for c in tool_calls],
        "result": result,
        "transcript": transcript,
        "init_slash_proofpunk": [c for c in init_slash
                                 if str(c).startswith("proofpunk:")],
        "local_plugin_loaded": _local_plugin_loaded(init_plugins),
        "prompt": spec["prompt"],
    }

    if "expect_blocked" in spec:
        # Verdict rests on the filesystem, not on the model's narration.
        exists = os.path.exists(artifact) if artifact else None
        content = None
        if exists:
            with open(artifact) as fh:
                content = fh.read().strip()

        checks = {}
        if spec.get("require_write_attempt"):
            # Without a real Write attempt the probe is vacuous: "permitted"
            # and "never tried" would look identical.
            checks["write_attempted"] = "Write" in tools
        checks["artifact_matches"] = (exists == spec["expect_artifact"])
        if spec.get("expect_content") is not None:
            checks["content_matches"] = bool(exists) and content == spec["expect_content"]
        # An absent file is not proof of a denial — the write could have failed
        # for an unrelated reason. Require the observed block state to match.
        checks["denial_matches"] = (blocked == spec["expect_blocked"])

        out.update({
            "blocked": blocked, "expected_blocked": spec["expect_blocked"],
            "artifact": artifact, "artifact_exists": exists,
            "artifact_content": content, "checks": checks,
        })
        # A harness/API failure (ResultError, auth flap) can coexist with
        # init-level checks reading True — slash registration arrives
        # before the model call fails. No probe passes on a harness error.
        checks["no_harness_error"] = not bool(result.get("harness_error"))
        # And no probe passes when the stream ended with no ResultMessage
        # at all — an empty result means the session died silently, which
        # is UNVERIFIED, not a pass.
        checks["session_completed"] = session_completed
        out["pass"] = all(checks.values())
    else:
        # A text match alone is the model's self-report. When the probe names a
        # required tool, an actual invocation must be observed, its argument
        # must match, AND that same call must have returned successfully —
        # "Unknown skill" is an attempt, not a load.
        checks = {"text_matches": spec["expect_text"].lower() in joined.lower()}
        if spec.get("require_tool"):
            want = spec["require_tool"]
            hits = [c for c in tool_calls if c["name"] == want]
            checks["tool_invoked"] = bool(hits)

            matching = hits
            if spec.get("require_tool_arg"):
                want_arg = spec["require_tool_arg"]
                if isinstance(want_arg, str):
                    want_arg = (want_arg,)
                # Host may surface the slash command as its own skill name
                # (proofpunk:rate-prompt) even when the command doc says
                # Activate `prompt-forge`. Accept every documented alias.
                def _arg_ok(v, names=want_arg):
                    s = str(v).strip()
                    for w in names:
                        if s == w or s.endswith(":" + w) or s.endswith(
                                ":" + w.split(":")[-1]):
                            return True
                    return False
                matching = [c for c in hits
                            if any(_arg_ok(v) for v in (c["input"] or {}).values())]
                checks["tool_arg_matches"] = bool(matching)

            # Scope success to the call that matched the argument, so an
            # unrelated successful tool call cannot satisfy this.
            checks["tool_succeeded"] = any(
                c["result"] is not None
                and c["is_error"] is not True
                and "unknown skill" not in str(c["result"]).lower()
                for c in matching)

        if spec.get("require_slash") or spec.get("require_slash_name"):
            want_slash = spec.get("require_slash_name")
            if want_slash:
                checks["slash_registered"] = want_slash in init_slash
            else:
                checks["slash_registered"] = any(
                    str(c).startswith("proofpunk:") for c in init_slash)
            # UserPromptExpansion fires only when the CLI expanded a slash
            # command. That is the typed-surface event, distinct from Skill.
            checks["slash_expanded"] = "UserPromptExpansion" in hooks

        if spec.get("require_local_plugin"):
            checks["local_plugin_loaded"] = _local_plugin_loaded(init_plugins)

        if spec.get("effect_kind") == "install":
            # Verdict rests on the sandbox filesystem, never the model's
            # self-report. cwd is this arm's fresh per-arm sandbox (see
            # verify-command-surface.py); the memory file the command doc
            # says to write lands there if the playbook actually executed.
            claude_md = os.path.join(cwd, "CLAUDE.md")
            exists = os.path.isfile(claude_md)
            content = ""
            if exists:
                try:
                    with open(claude_md, encoding="utf-8") as fh:
                        content = fh.read()
                except OSError:
                    content = ""
            write_calls = [c for c in tool_calls if c["name"] in ("Write", "Edit")]
            checks["write_attempted"] = bool(write_calls)
            # A call with no result yet (is_error is None, result is None)
            # is an in-flight attempt, not a success — require a REAL
            # non-error result to have actually come back.
            checks["write_succeeded"] = any(
                c["result"] is not None and c["is_error"] is not True
                and str(c["result"] or "").strip()
                for c in write_calls)
            checks["claude_md_exists"] = exists
            checks["markers_present"] = (
                "proofpunk:begin" in content and "proofpunk:end" in content)
            checks["within_200_lines"] = bool(content) and len(content.splitlines()) <= 200
            # Template substitution: the shipped template uses {{NAME}} form
            # placeholders (assets/claude-md-template.md); a genuine merge
            # substitutes or omits every one, never leaves the literal token.
            checks["template_substituted"] = bool(content) and "{{" not in content
            out["install_artifact"] = claude_md
            out["install_artifact_exists"] = exists
            out["install_artifact_lines"] = len(content.splitlines()) if content else 0

        if spec.get("effect_kind") == "verify":
            # Verdict rests on an observed real Bash command execution
            # against THIS sandbox, never narration. bash_attempted alone
            # is not proof — an attempt whose call never got a matched
            # result is indistinguishable from one still in flight.
            bash_calls = [c for c in tool_calls if c["name"] == "Bash"]
            checks["bash_attempted"] = bool(bash_calls)
            executed = [
                c for c in bash_calls
                if c["result"] is not None and c["is_error"] is not True
                and str(c["result"] or "").strip()
            ]
            checks["bash_executed"] = bool(executed)
            # Distinct from sentinel_surfaced below: this only proves the
            # HARNESS successfully seeded the sandbox before the session
            # started. If this is False the run is a harness fault (disk
            # write failed), not evidence about the model's behavior —
            # keeping it a separate check makes that failure mode legible
            # in the artifact instead of silently folded into a False
            # sentinel_surfaced that looks identical to a real narration-
            # only failure.
            checks["sentinel_seeded"] = verify_sentinel is not None
            # sentinel_surfaced is the load-bearing anti-narration check:
            # `verify_sentinel` is a per-run, cryptographically random
            # filename seeded into cwd BEFORE query() ran — the model has
            # no way to know or guess it without a real Bash call actually
            # listing/reading this exact sandbox. Scoping the search to
            # `executed` (Bash-only, is_error is False, non-empty result)
            # means a Read/Glob/Skill result, or the model's own narration
            # of the doctrine text, cannot satisfy this — only a genuine
            # command execution whose real stdout contains the sentinel
            # can.
            checks["sentinel_surfaced"] = bool(
                verify_sentinel and any(
                    verify_sentinel in str(c["result"] or "") for c in executed))
            out["verify_sentinel"] = verify_sentinel
            out["verify_bash_calls"] = len(bash_calls)

        # forbid_text on slash probes only — the older skill-load probes
        # stored forbid_text in the spec but never asserted it; do not change
        # their historical contract.
        if spec.get("forbid_text") and spec.get("require_slash"):
            checks["forbid_absent"] = (
                spec["forbid_text"].lower() not in joined.lower())

        if spec.get("require_hook_event"):
            # `hook_name` is the event label, not the script filename, so this
            # proves the event fired and its hooks exited cleanly — not which
            # script ran. Attribution to proofpunk comes from the loads tap.
            want_ev = spec["require_hook_event"]
            runs = [h for h in hook_runs
                    if str(h.get("event") or "").startswith(want_ev)]
            checks["hook_ran"] = bool(runs)
            checks["hook_ok"] = any(h.get("outcome") == "success" for h in runs)

        if spec.get("loads_append"):
            # Read ONLY the lines this run appended, and require at least one
            # to name this run's cwd. Byte growth is not attribution.
            new_lines = []
            if os.path.exists(loads_path):
                with open(loads_path) as fh:
                    new_lines = fh.readlines()[loads_before:]
            parsed = []
            for ln in new_lines:
                try:
                    parsed.append(json.loads(ln))
                except ValueError:
                    pass
            out["loads_new_lines"] = len(new_lines)
            out["loads_sample"] = parsed[:2]
            checks["loads_appended"] = bool(parsed)
            # macOS resolves /tmp through a symlink, so the tap records
            # /private/tmp/... — compare resolved paths, not raw strings.
            want_cwd = os.path.realpath(cwd)
            checks["loads_this_run"] = any(
                os.path.realpath(str(p.get("cwd", ""))) == want_cwd
                for p in parsed)

        out["checks"] = checks
        out["expect_text"] = spec["expect_text"]
        # Same fail-closed rule as the expect_blocked branch: a harness/API
        # failure voids every check, including init-level ones that arrive
        # before the model call dies.
        checks["no_harness_error"] = not bool(result.get("harness_error"))
        checks["session_completed"] = session_completed
        out["pass"] = all(checks.values())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("probe", choices=sorted(PROBES))
    ap.add_argument("--cwd", default="/tmp")
    ap.add_argument("--no-plugin", action="store_true",
                    help="control arm: run WITHOUT the plugin to prove the "
                         "probe can fail (guards against a vacuous pass)")
    a = ap.parse_args()
    try:
        out = asyncio.run(run(a.probe, a.cwd, not a.no_plugin))
    except Exception as e:
        print(json.dumps({"probe": a.probe, "harness_error": f"{type(e).__name__}: {e}"}))
        sys.exit(2)
    print(json.dumps(out, indent=2))
    sys.exit(0 if out["pass"] else 1)


if __name__ == "__main__":
    main()
