#!/usr/bin/env python3
"""Drive live routing + listing-budget observation via the same SDK as
tools/sdk_probe.py. Read-only of that harness; this file lives in the
lane evidence dir and is not a repo gate.

Does not edit tools/sdk_probe.py.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

REPO = "/Users/nick/proofpunk"
PLUGIN = os.path.join(REPO, "plugins", "proofpunk")
sys.path.insert(0, os.path.join(REPO, "tools"))

from claude_agent_sdk import (  # noqa: E402
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

# Six shapes required by the lane brief. Expected skill is the router's
# own table / "Routes to nothing" section — recorded as expected, never
# used to retune the prompt after a miss.
GOALS = [
    {
        "id": "build",
        "expected": "implement",
        "ask": (
            "Build a CLI that converts markdown files to HTML end to end. "
            "Scope is known: one command, real files on disk, no design debate."
        ),
    },
    {
        "id": "audit",
        "expected": "full-functional-audit",
        "ask": (
            "Audit this entire running web app at http://127.0.0.1:3999 — "
            "click through every screen, button, form, and endpoint."
        ),
    },
    {
        "id": "bug",
        "expected": "root-cause-debugging",
        "ask": (
            "The login form submits twice and I cannot find why. Symptom "
            "fixes keep failing. Reproduction: click Submit, the browser "
            "fires two POSTs to /login."
        ),
    },
    {
        "id": "proof",
        "expected": "end-user-testing",
        "ask": (
            "Prove the export button actually works as an end user. Capture "
            "run-scoped evidence before marking the feature done."
        ),
    },
    {
        "id": "planning",
        "expected": "validation-plan",
        "ask": (
            "I need a written multi-phase roadmap before any code for adding "
            "OAuth to this existing app. Do not write code yet."
        ),
    },
    {
        "id": "nothing",
        "expected": "ROUTES_TO_NOTHING",
        "ask": "Explain what this function does",
    },
]


def skill_name_from_input(inp) -> str | None:
    if not isinstance(inp, dict):
        return None
    for v in inp.values():
        s = str(v).strip()
        if s:
            return s
    return None


def normalize_skill(name: str | None) -> str | None:
    if not name:
        return None
    name = name.strip()
    if ":" in name:
        # proofpunk:implement -> implement
        return name.split(":", 1)[-1]
    return name


async def dump_listing(out_path: str) -> dict:
    """One cheap session whose only job is to surface the host's skill listing."""
    opts = ClaudeAgentOptions(
        cwd="/tmp",
        permission_mode="bypassPermissions",
        include_hook_events=True,
        max_turns=2,
        plugins=[SdkPluginConfig(type="local", path=PLUGIN)],
        allowed_tools=["Skill"],
        disallowed_tools=["Bash", "Write", "Edit", "Agent", "Task"],
    )
    systems = []
    text = []
    t0 = time.time()
    async for msg in query(
        prompt="Reply with exactly: LISTING_PROBE_OK",
        options=opts,
    ):
        if isinstance(msg, SystemMessage):
            data = getattr(msg, "data", {}) or {}
            # Keep the whole payload; listing fields are host-defined.
            systems.append({
                "subtype": getattr(msg, "subtype", None),
                "data_keys": sorted(data.keys()) if isinstance(data, dict) else type(data).__name__,
                "data": data,
            })
        elif isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    text.append(b.text)
        elif isinstance(msg, ResultMessage):
            result = {
                "is_error": msg.is_error,
                "num_turns": msg.num_turns,
                "cost_usd": msg.total_cost_usd,
            }
        else:
            result = {}
    elapsed = round(time.time() - t0, 1)
    payload = {
        "elapsed_s": elapsed,
        "reply": "".join(text)[:400],
        "system_messages": systems,
        "result": result if "result" in dir() else {},
    }
    # result may be unbound if no ResultMessage
    if "result" not in payload or not payload["result"]:
        payload["result"] = locals().get("result", {})
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=2, default=str)
    return payload


async def drive_goal(goal: dict) -> dict:
    prompt = (
        "The proofpunk plugin is loaded. Follow the proofpunk router skill. "
        "For the user ask below, invoke the Skill tool for the SINGLE best-fit "
        "proofpunk delivery skill (prefer the namespaced proofpunk:<name> form). "
        "If the router's own 'Routes to nothing' section applies, do NOT invoke "
        "any delivery skill; reply with exactly ROUTES_TO_NOTHING and nothing else. "
        "Do not implement the ask. Do not write files.\n\n"
        f"User ask: {goal['ask']}"
    )
    opts = ClaudeAgentOptions(
        cwd="/tmp",
        permission_mode="bypassPermissions",
        include_hook_events=True,
        max_turns=8,
        plugins=[SdkPluginConfig(type="local", path=PLUGIN)],
        allowed_tools=["Skill"],
        disallowed_tools=["Bash", "Write", "Edit", "Agent", "Task", "NotebookEdit"],
    )
    text, tools, tool_calls, systems = [], [], [], []
    result = {}
    t0 = time.time()
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    text.append(b.text)
                elif isinstance(b, ToolUseBlock):
                    tools.append(b.name)
                    tool_calls.append({
                        "id": b.id,
                        "name": b.name,
                        "input": b.input,
                        "result": None,
                        "is_error": None,
                    })
        elif isinstance(msg, UserMessage):
            for b in (msg.content if isinstance(msg.content, list) else []):
                if isinstance(b, ToolResultBlock):
                    for c in tool_calls:
                        if c["id"] == b.tool_use_id:
                            c["result"] = str(b.content)[:500]
                            c["is_error"] = b.is_error
        elif isinstance(msg, SystemMessage):
            data = getattr(msg, "data", {}) or {}
            systems.append({
                "subtype": getattr(msg, "subtype", None),
                "data_keys": sorted(data.keys()) if isinstance(data, dict) else type(data).__name__,
            })
        elif isinstance(msg, ResultMessage):
            result = {
                "is_error": msg.is_error,
                "num_turns": msg.num_turns,
                "cost_usd": msg.total_cost_usd,
            }

    joined = "".join(text)
    skill_calls = [c for c in tool_calls if c["name"] == "Skill"]
    reached = []
    for c in skill_calls:
        raw = skill_name_from_input(c.get("input") or {})
        reached.append({
            "raw": raw,
            "normalized": normalize_skill(raw),
            "is_error": c.get("is_error"),
            "unknown": "unknown skill" in str(c.get("result") or "").lower(),
            "result_head": str(c.get("result") or "")[:200],
        })

    # Delivery skill = any Skill call that is not the router head itself.
    delivery = [
        r for r in reached
        if r["normalized"] and r["normalized"] != "proofpunk"
    ]
    nothing = "ROUTES_TO_NOTHING" in joined
    if goal["expected"] == "ROUTES_TO_NOTHING":
        actual = "ROUTES_TO_NOTHING" if (nothing and not delivery) else (
            delivery[0]["normalized"] if delivery else (
                "ROUTES_TO_NOTHING" if nothing else "NO_SKILL_AND_NO_NOTHING"
            )
        )
        match = actual == "ROUTES_TO_NOTHING" and not delivery
    else:
        actual = delivery[0]["normalized"] if delivery else (
            "ROUTES_TO_NOTHING" if nothing else "NO_DELIVERY_SKILL"
        )
        match = actual == goal["expected"]

    return {
        "id": goal["id"],
        "ask": goal["ask"],
        "expected": goal["expected"],
        "actual": actual,
        "match": match,
        "reached": reached,
        "delivery": delivery,
        "reply": joined.strip()[:600],
        "tools_used": sorted(set(tools)),
        "elapsed_s": round(time.time() - t0, 1),
        "result": result,
        "system_message_count": len(systems),
        "system_keys_sample": systems[:3],
    }


async def main() -> int:
    evid = os.path.dirname(os.path.abspath(__file__))
    listing_path = os.path.join(evid, "step-07-listing-dump.json")
    print("LISTING dump ->", listing_path, flush=True)
    listing = await dump_listing(listing_path)
    print("listing elapsed", listing.get("elapsed_s"),
          "sysmsgs", len(listing.get("system_messages") or []),
          "cost", (listing.get("result") or {}).get("cost_usd"),
          flush=True)

    results = []
    for i, goal in enumerate(GOALS, start=8):
        stem = f"step-{i:02d}-live-{goal['id']}"
        print(f"DRIVE {stem} expected={goal['expected']}", flush=True)
        out = await drive_goal(goal)
        path = os.path.join(evid, f"{stem}.json")
        with open(path, "w") as fh:
            json.dump(out, fh, indent=2, default=str)
        print(
            f"  actual={out['actual']} match={out['match']} "
            f"elapsed={out['elapsed_s']}s cost={(out.get('result') or {}).get('cost_usd')}",
            flush=True,
        )
        results.append(out)

    summary = {
        "n": len(results),
        "matches": sum(1 for r in results if r["match"]),
        "rows": [
            {
                "id": r["id"],
                "expected": r["expected"],
                "actual": r["actual"],
                "match": r["match"],
                "elapsed_s": r["elapsed_s"],
                "cost_usd": (r.get("result") or {}).get("cost_usd"),
            }
            for r in results
        ],
    }
    summary_path = os.path.join(evid, "step-14-live-routing-summary.json")
    with open(summary_path, "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
