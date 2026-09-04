#!/usr/bin/env python3
"""Capture the skill listing the model actually sees, plus CLI stderr.

Does not edit tools/sdk_probe.py. Evidence-only driver.
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import time

from claude_agent_sdk import (
    ClaudeAgentOptions,
    SdkPluginConfig,
    query,
    AssistantMessage,
    SystemMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    ToolResultBlock,
)

REPO = "/Users/nick/proofpunk"
PLUGIN = os.path.join(REPO, "plugins", "proofpunk")
EVID = os.path.dirname(os.path.abspath(__file__))

PROMPT = (
    "Do not invoke any skill. Reply with a single JSON object and nothing else, "
    "using these keys:\n"
    "  proofpunk_names: array of every skill name you can see that starts with "
    "'proofpunk:' or equals 'proofpunk'\n"
    "  implement_present: boolean, true iff you can see a skill named "
    "'proofpunk:implement' or 'implement' in the listing\n"
    "  listing_truncated: boolean, true iff you saw any warning that skill "
    "descriptions were truncated or dropped\n"
    "  warning_verbatim: the warning text if any, else null\n"
    "  description_chars: object mapping each proofpunk skill name you can see "
    "to the character count of its listing description (0 if name only)\n"
    "  sample_head_description: the exact listing description text for the "
    "skill named proofpunk or proofpunk:proofpunk, or null if unseen\n"
    "Quote listing text; do not invent names."
)


async def run() -> dict:
    stderr_buf = io.StringIO()
    opts = ClaudeAgentOptions(
        cwd="/tmp",
        permission_mode="bypassPermissions",
        include_hook_events=True,
        max_turns=3,
        plugins=[SdkPluginConfig(type="local", path=PLUGIN)],
        allowed_tools=["Skill"],
        disallowed_tools=["Bash", "Write", "Edit", "Agent", "Task"],
        debug_stderr=stderr_buf,
        extra_args={"debug-to-stderr": None},
    )
    text, tools, tool_calls, systems = [], [], [], []
    result = {}
    t0 = time.time()
    async for msg in query(prompt=PROMPT, options=opts):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    text.append(b.text)
                elif isinstance(b, ToolUseBlock):
                    tools.append(b.name)
                    tool_calls.append({"name": b.name, "input": b.input})
        elif isinstance(msg, UserMessage):
            pass
        elif isinstance(msg, SystemMessage):
            data = getattr(msg, "data", {}) or {}
            rec = {
                "subtype": getattr(msg, "subtype", None),
                "data_keys": sorted(data.keys()) if isinstance(data, dict) else type(data).__name__,
            }
            if rec["subtype"] == "init" and isinstance(data, dict):
                rec["skills"] = data.get("skills")
                rec["slash_commands_proofpunk"] = [
                    s for s in (data.get("slash_commands") or [])
                    if "proofpunk" in str(s).lower()
                ]
                rec["n_skills"] = len(data.get("skills") or [])
                rec["claude_code_version"] = data.get("claude_code_version")
                rec["model"] = data.get("model")
            systems.append(rec)
        elif isinstance(msg, ResultMessage):
            result = {
                "is_error": msg.is_error,
                "num_turns": msg.num_turns,
                "cost_usd": msg.total_cost_usd,
            }
    stderr = stderr_buf.getvalue()
    joined = "".join(text)
    return {
        "elapsed_s": round(time.time() - t0, 1),
        "reply": joined,
        "tools_used": sorted(set(tools)),
        "tool_calls": tool_calls,
        "result": result,
        "stderr_len": len(stderr),
        "stderr": stderr[-80000:],
        "system_init": next((s for s in systems if s.get("subtype") == "init"), None),
        "n_system": len(systems),
    }


def main() -> int:
    out = asyncio.run(run())
    path = os.path.join(EVID, "step-15-listing-content.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2, default=str)
    stderr_path = os.path.join(EVID, "step-15-listing-content.stderr.log")
    with open(stderr_path, "w") as fh:
        fh.write(out.get("stderr") or "")
    print("wrote", path, "elapsed", out["elapsed_s"], "stderr_len", out["stderr_len"])
    print("reply_head", (out.get("reply") or "")[:800])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
