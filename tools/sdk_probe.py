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
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO, "plugins", "proofpunk")

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
    # Are the plugin's skills actually loadable FROM THE PLUGIN? Every one of
    # the 17 also exists standalone in ~/.claude/skills on this host, so a bare
    # name proves nothing — the control arm loaded `end-user-testing` with the
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
}


async def run(name: str, cwd: str, use_plugin: bool) -> dict:
    spec = PROBES[name]

    # Clean the artifact before the arm so a stale file from a prior run can
    # never be mistaken for this run's outcome.
    artifact = spec.get("artifact")
    if artifact:
        os.makedirs(os.path.dirname(artifact), exist_ok=True)
        if os.path.exists(artifact):
            os.remove(artifact)

    opts = dict(
        cwd=cwd,
        permission_mode="bypassPermissions",
        include_hook_events=True,
        max_turns=8,
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

    text, hooks, tools, denials = [], [], [], []
    tool_calls = []          # name + real input dict, so arguments are checkable
    result = {}
    t0 = time.time()

    async for msg in query(prompt=spec["prompt"], options=ClaudeAgentOptions(**opts)):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    text.append(b.text)
                elif isinstance(b, ToolUseBlock):
                    tools.append(b.name)
                    tool_calls.append({"id": b.id, "name": b.name,
                                       "input": b.input, "result": None,
                                       "is_error": None})
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
        elif isinstance(msg, HookEventMessage):
            hooks.append(msg.hook_event_name)
        elif isinstance(msg, SystemMessage):
            blob = json.dumps(getattr(msg, "data", {}))
            if "refusing to create a test artifact" in blob:
                denials.append("no-test-files")
        elif isinstance(msg, ResultMessage):
            result = {"is_error": msg.is_error, "num_turns": msg.num_turns,
                      "cost_usd": msg.total_cost_usd}

    joined = "".join(text)
    # A denial shows up either as a system event or as the model reporting it.
    blocked = bool(denials) or "refusing to create a test artifact" in joined

    out = {
        "probe": name, "why": spec["why"], "plugin_loaded": use_plugin,
        "elapsed_s": round(time.time() - t0, 1),
        "reply": joined.strip()[:400],
        "hook_events": sorted(set(hooks)), "tools_used": sorted(set(tools)),
        "tool_calls": [{"name": c["name"], "input": json.dumps(c["input"])[:200]}
                       for c in tool_calls],
        "result": result,
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
            "pass": all(checks.values()),
        })
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
                # Skill args are namespaced "<plugin>:<skill>". Accept the bare
                # name or a qualified form ending in it, nothing looser.
                matching = [c for c in hits
                            if any(str(v).strip() == want_arg
                                   or str(v).strip().endswith(f":{want_arg}")
                                   for v in (c["input"] or {}).values())]
                checks["tool_arg_matches"] = bool(matching)

            # Scope success to the call that matched the argument, so an
            # unrelated successful tool call cannot satisfy this.
            checks["tool_succeeded"] = any(
                c["result"] is not None
                and c["is_error"] is not True
                and "unknown skill" not in str(c["result"]).lower()
                for c in matching)
        out["checks"] = checks
        out["expect_text"] = spec["expect_text"]
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
