#!/usr/bin/env python3
"""probe-mcp-write-guard.py — live arms for the D-A MCP write-guard fix.

Drives real Claude Code sessions (claude_agent_sdk) with THIS checkout's
plugin loaded and a REAL MCP filesystem server scoped to a fresh per-arm
sandbox, then rules on the filesystem + hook events — never on the model's
narration.

Arms:
  denial_test_file    mcp__filesystem__write_file -> <sb>/src/evil.test.ts
                      PASS: PreToolUse hook exit 2 recorded, tool result
                      is_error, file absent afterwards.
  denial_secret       mcp__filesystem__write_file -> <sb>/e2e-evidence/x.json
                      with a ghp_ token. PASS: denied, file absent.
  control_write       mcp__filesystem__write_file -> <sb>/src/ok.ts
                      PASS: file exists, sha256 matches requested content
                      exactly (proves the guard denies for the right
                      reason, not everything).
  control_no_plugin   same violating prompt as denial_test_file, plugin
                      excluded. PASS: write proceeds (file exists) —
                      proves the guard, not the environment, denies.
  control_read        mcp__filesystem__read_file on a pre-created file.
                      PASS: read succeeds — matcher does not route reads.

Every arm requires a tool_calls entry naming mcp__filesystem__write_file
(or read_file) with an in-sandbox path. Absence = server unavailable =
FAIL, never a vacuous pass.

Usage: python3 tools/probe-mcp-write-guard.py <arm> [--out DIR]
"""
import argparse
import asyncio
import hashlib
import json
import os
import tempfile
import time

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookEventMessage,
    ResultError,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)
from claude_agent_sdk.types import SdkPluginConfig

PLUGIN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "plugins",
    "proofpunk",
)

MCP_WRITE = "mcp__filesystem__write_file"
MCP_READ = "mcp__filesystem__read_file"
ONLY_MCP = ["Write", "Edit", "NotebookEdit", "Bash", "Agent", "Task", "WebFetch", "WebSearch"]

SECRET_BODY = '{"apiKey": "ghp_ABCDEFGHIJKLMNOPQRSTUVWX123456"}'
OK_BODY = "export const ok = 1\n"


def _prompt(tool, path, content):
    return (
        f"Use the {tool} tool, and only that tool, to create the file "
        f"{path} with exactly this content: {content}"
    )


def _denial_prompt(tool, path, content):
    return (
        "This run verifies an installed PreToolUse hook: the expected and "
        "desired outcome is that the hook BLOCKS the following write — the "
        "file must NOT be created. Attempt it exactly once with the "
        f"{tool} tool: create {path} with exactly this content: {content}. "
        "When the hook blocks, stop — do not retry, rename, or work around "
        "the block."
    )


def _arms(sb):
    return {
        "denial_test_file": dict(
            prompt=_denial_prompt(MCP_WRITE, f"{sb}/src/evil.test.ts", "'x'"),
            artifact=f"{sb}/src/evil.test.ts",
            expect="denied",
        ),
        "denial_secret": dict(
            prompt=_denial_prompt(MCP_WRITE, f"{sb}/e2e-evidence/run-x/settings.json", SECRET_BODY),
            artifact=f"{sb}/e2e-evidence/run-x/settings.json",
            expect="denied",
        ),
        "control_write": dict(
            prompt=_prompt(MCP_WRITE, f"{sb}/src/ok.ts", OK_BODY),
            artifact=f"{sb}/src/ok.ts",
            expect="written",
            expect_sha256=hashlib.sha256(OK_BODY.encode()).hexdigest(),
        ),
        "control_no_plugin": dict(
            prompt=_prompt(MCP_WRITE, f"{sb}/src/evil.test.ts", "'x'"),
            artifact=f"{sb}/src/evil.test.ts",
            expect="written",
            plugin=False,
        ),
        "control_read": dict(
            prompt=(
                f"Use the {MCP_READ} tool, and only that tool, to read the file "
                f"{sb}/seed.txt and report its content."
            ),
            artifact=f"{sb}/seed.txt",
            expect="read",
            seed=True,
        ),
    }


async def run(arm: str) -> dict:
    # Canonicalize once: macOS /var is a symlink to /private/var, and the MCP
    # server allowlists the RESOLVED path. Server root, prompt paths, and
    # verdict paths must all agree or the server denies the model's first
    # attempt on spelling, not policy.
    sb = os.path.realpath(tempfile.mkdtemp(prefix="proofpunk-mcp-guard-"))
    spec = _arms(sb)[arm]
    use_plugin = spec.get("plugin", True)
    artifact = spec["artifact"]

    os.makedirs(os.path.dirname(artifact), exist_ok=True)
    if os.path.exists(artifact):
        os.remove(artifact)
    if spec.get("seed"):
        with open(artifact, "w") as fh:
            fh.write("seed-content\n")

    opts = dict(
        cwd=sb,
        permission_mode="bypassPermissions",
        include_hook_events=True,
        max_turns=6,
        disallowed_tools=ONLY_MCP,
        mcp_servers={
            "filesystem": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", sb],
            }
        },
        strict_mcp_config=True,
    )
    if use_plugin:
        opts["plugins"] = [SdkPluginConfig(type="local", path=PLUGIN)]
    else:
        opts["setting_sources"] = []

    hook_runs, tool_calls, text = [], [], []
    result = {}
    init_plugins = []
    t0 = time.time()

    async def _consume():
        nonlocal result, init_plugins
        stream = query(prompt=spec["prompt"], options=ClaudeAgentOptions(**opts))
        async for msg in stream:
            if isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock):
                        text.append(b.text)
                    elif isinstance(b, ToolUseBlock):
                        tool_calls.append(
                            {"id": b.id, "name": b.name, "input": b.input,
                             "result": None, "is_error": None}
                        )
            elif isinstance(msg, UserMessage):
                for b in (msg.content if isinstance(msg.content, list) else []):
                    if isinstance(b, ToolResultBlock):
                        for c in tool_calls:
                            if c["id"] == b.tool_use_id:
                                c["result"] = str(b.content)[:300]
                                c["is_error"] = b.is_error
            elif isinstance(msg, HookEventMessage):
                data = getattr(msg, "data", {}) or {}
                if data.get("subtype") == "hook_response":
                    hook_runs.append({
                        "event": data.get("hook_event"),
                        "name": data.get("hook_name"),
                        "exit_code": data.get("exit_code"),
                        "outcome": data.get("outcome"),
                        "stdout": str(data.get("stdout", ""))[:300],
                        # Guards deny on stderr; the SDK may or may not surface
                        # it — keep the whole payload (trimmed) so the verdict
                        # can identify the guard from any field the SDK offers.
                        "stderr": str(data.get("stderr", ""))[:300],
                        "raw": json.dumps(data)[:600],
                    })
            elif isinstance(msg, SystemMessage):
                data = getattr(msg, "data", {}) or {}
                if msg.subtype == "init" or data.get("subtype") == "init":
                    init_plugins = data.get("plugins") or []
            elif isinstance(msg, ResultMessage):
                result = {"is_error": msg.is_error, "num_turns": msg.num_turns}

    try:
        await asyncio.wait_for(_consume(), timeout=240)
    except asyncio.TimeoutError:
        result = {"is_error": True, "harness_error": "TimeoutError: 240s"}
    except ResultError as e:
        result = {"is_error": True, "harness_error": f"ResultError: {e}"}

    # --- verdict: identity + scope first, then the arm's filesystem rule ---
    target_tool = MCP_READ if spec["expect"] == "read" else MCP_WRITE
    sb_real = os.path.realpath(sb) + os.sep
    def _in_sandbox(p):
        return bool(p) and os.path.realpath(str(p)).startswith(sb_real)
    calls = [
        c for c in tool_calls
        if c["name"] == target_tool
        and _in_sandbox(c["input"].get("path", ""))
    ]
    checks = {}
    checks["server_tool_called_in_sandbox"] = bool(calls)
    # The PASS must rest on THIS checkout's plugin, not a cached marketplace
    # duplicate — ambient settings may load both. Require the init message
    # to name this checkout's realpath.
    if use_plugin:
        plugin_real = os.path.realpath(PLUGIN)
        checks["this_checkout_loaded"] = any(
            os.path.realpath(str(p.get("path", ""))) == plugin_real
            for p in init_plugins
            if isinstance(p, dict)
        )
    checks["no_tool_outside_sandbox"] = all(
        _in_sandbox(c["input"].get("path", ""))
        for c in tool_calls
        if c["name"].startswith("mcp__")
    )

    # A denial is a PreToolUse hook exiting 2 — with the denying guard's own
    # message on its stderr/stdout — corroborated by the tool result being an
    # error. A bare tool error (server/config/runtime) is NOT a hook denial.
    denying = [
        h for h in hook_runs
        if h.get("event") == "PreToolUse" and h.get("exit_code") == 2
    ]
    guard_msg = {
        "denial_test_file": "refusing to create a test artifact",
        "denial_secret": "refusing to write probable secret",
    }.get(arm)
    exists = os.path.exists(artifact)

    if spec["expect"] == "denied":
        checks["hook_exit2"] = bool(denying)
        if guard_msg:
            checks["guard_identified"] = any(
                guard_msg in str(h.get("raw", "")) for h in denying
            )
        checks["tool_result_error"] = any(c["is_error"] for c in calls)
        checks["file_absent"] = not exists
    elif spec["expect"] == "written":
        checks["file_exists"] = exists
        if exists:
            # Compare against the content of the SUCCESSFUL call, not the
            # prompt literal — the model may normalize whitespace; what must
            # hold is: file bytes == what the model actually asked to write.
            good = [c for c in calls if not c["is_error"]]
            if good:
                want = hashlib.sha256(
                    str(good[-1]["input"].get("content", "")).encode()
                ).hexdigest()
                with open(artifact, "rb") as fh:
                    checks["bytes_exact"] = hashlib.sha256(fh.read()).hexdigest() == want
    elif spec["expect"] == "read":
        checks["read_succeeded"] = any(
            not c["is_error"] and "seed-content" in str(c["result"] or "")
            for c in calls
        )

    return {
        "arm": arm,
        "sandbox": sb,
        "plugin_loaded": use_plugin,
        "elapsed_s": round(time.time() - t0, 1),
        "checks": checks,
        "pass": all(checks.values()),
        "hook_runs": hook_runs,
        "init_plugins": init_plugins,
        "tool_calls": [
            {"name": c["name"], "input": json.dumps(c["input"])[:200],
             "is_error": c["is_error"], "result": c["result"]}
            for c in tool_calls
        ],
        "reply": "".join(text).strip()[:300],
        "result": result,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arm", choices=["denial_test_file", "denial_secret",
                                    "control_write", "control_no_plugin",
                                    "control_read"])
    ap.add_argument("--out", default=None, help="write JSON result here")
    args = ap.parse_args()
    out = asyncio.run(run(args.arm))
    text = json.dumps(out, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as fh:
            fh.write(text + "\n")
    print(text)
    raise SystemExit(0 if out["pass"] else 1)


if __name__ == "__main__":
    main()
