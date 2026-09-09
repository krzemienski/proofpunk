#!/usr/bin/env python3
"""verify-shipped-vs-active.py — Class 3 permanent detector.

A component present on disk but never wired is this repo's repeating
failure (evidence-guard.sh shipped dead from v1.10.0 through v2.1.0).

This gate enumerates a SHIPPED set from one canonical source and an
ACTIVE set from a *different* canonical source (the thing that consumes
it at runtime), then asserts set-equality with named symmetric difference.

CHECKS
------
1. hooks: plugins/proofpunk/hooks/*.sh  vs  scripts named in hooks.json
2. skills: skills/*/SKILL.md dirs        vs  router Skill-calls table
   (head itself is the router, excluded from the calls column)
3. shared references: references/*.md    vs  citations in any SKILL.md
   of the form `` `../../references/<name>.md` `` or `` `references/<name>.md` ``
   (bundled per-skill references/ files are a different population)
4. commands: commands/*.md stems         vs  opencode/commands/proofpunk-*.md
5. CI wiring: every tools/{test-*.sh,verify-*.py,dry-run-*.sh} except the
   documented live-session exception (sdk_probe.py) must appear as a
   run: line in .github/workflows/gates.yml

Exit 0 = every pair equal. Exit N = N named mismatches.
Stdlib only.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=hooks.json,SKILL.md,gates.yml keywords=json.load,glob,open
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PLUGIN = os.path.join(ROOT, "plugins", "proofpunk")

CI_LIVE_EXCEPTION = frozenset({"sdk_probe.py"})

# Live-session drivers: present under tools/, never a hermetic CI step.
# sdk_probe.py does not match tools_harnesses()'s test-/verify-/dry-run
# pattern (it is *_probe.py); verify-command-surface.py does, and would
# otherwise be reported ci-unwired even though gates.yml documents it as
# a known coverage gap next to sdk_probe.py.
CI_LIVE_DRIVERS = frozenset({"sdk_probe.py", "verify-command-surface.py"})
SHARED_REF_CITE = re.compile(
    r"`(?:\.\./)+references/([a-z0-9-]+\.md)`"
)
ROUTER_CALLS = re.compile(r"^\| `([a-z0-9-]+)` \|", re.M)
WORKFLOW_RUN = re.compile(r"^\s+run:\s+(?:python3|bash)\s+(\S+)", re.M)


def fail_line(msg: str, shipped: set[str], active: set[str]) -> str:
    only_shipped = sorted(shipped - active)
    only_active = sorted(active - shipped)
    parts = [msg]
    if only_shipped:
        parts.append("shipped-not-active: " + ", ".join(only_shipped))
    if only_active:
        parts.append("active-not-shipped: " + ", ".join(only_active))
    return " | ".join(parts)


def hook_scripts_on_disk() -> set[str]:
    return {
        os.path.basename(p)
        for p in glob.glob(os.path.join(PLUGIN, "hooks", "*.sh"))
    }


def hook_scripts_in_json() -> set[str]:
    path = os.path.join(PLUGIN, "hooks", "hooks.json")
    with open(path) as f:
        spec = json.load(f)
    events = spec.get("hooks", spec)
    names: set[str] = set()
    for _ev, arr in events.items():
        if not isinstance(arr, list):
            continue
        for item in arr:
            inner = item.get("hooks", [item]) if isinstance(item, dict) else []
            for h in inner:
                if not isinstance(h, dict):
                    continue
                cmd = h.get("command", "")
                names.update(re.findall(r"([A-Za-z0-9_-]+\.sh)", cmd))
    return names


def skill_dirs() -> set[str]:
    names = set()
    for p in glob.glob(os.path.join(PLUGIN, "skills", "*", "SKILL.md")):
        names.add(os.path.basename(os.path.dirname(p)))
    return names


def router_calls() -> set[str]:
    head = os.path.join(PLUGIN, "skills", "proofpunk", "SKILL.md")
    with open(head) as f:
        body = f.read()
    # Section between "## Skill calls" and the next H2.
    m = re.search(r"^## Skill calls\n(.*?)(?=^## )", body, re.M | re.S)
    if not m:
        return set()
    return set(ROUTER_CALLS.findall(m.group(1)))


def shared_refs_on_disk() -> set[str]:
    return {
        os.path.basename(p)
        for p in glob.glob(os.path.join(PLUGIN, "references", "*.md"))
    }


def shared_refs_cited() -> set[str]:
    cited: set[str] = set()
    for p in glob.glob(os.path.join(PLUGIN, "skills", "*", "SKILL.md")):
        with open(p) as f:
            cited.update(SHARED_REF_CITE.findall(f.read()))
    return cited


def command_stems(kind: str) -> set[str]:
    if kind == "claude":
        return {
            os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(PLUGIN, "commands", "*.md"))
        }
    stems = set()
    for p in glob.glob(os.path.join(PLUGIN, "opencode", "commands", "*.md")):
        name = os.path.splitext(os.path.basename(p))[0]
        if name.startswith("proofpunk-"):
            stems.add(name[len("proofpunk-"):])
        else:
            stems.add(name)
    return stems


def tools_harnesses() -> set[str]:
    names = set()
    tools = os.path.join(ROOT, "tools")
    pat = re.compile(r"^(test-.*\.sh|verify-.*\.py|dry-run-.*\.sh)$")
    for name in os.listdir(tools):
        if pat.match(name):
            names.add(name)
    return names - CI_LIVE_EXCEPTION - CI_LIVE_DRIVERS


def ci_wired() -> set[str]:
    path = os.path.join(ROOT, ".github", "workflows", "gates.yml")
    with open(path) as f:
        text = f.read()
    wired = set()
    for token in re.findall(r"tools/([A-Za-z0-9_.-]+)", text):
        wired.add(token)
    return wired


def main() -> int:
    fails: list[str] = []

    hooks_disk = hook_scripts_on_disk()
    hooks_json = hook_scripts_in_json()
    print(f"hooks disk={len(hooks_disk)} json={len(hooks_json)}")
    if hooks_disk != hooks_json:
        fails.append(fail_line("hooks", hooks_disk, hooks_json))
    else:
        print("PASS hooks")

    skills = skill_dirs()
    calls = router_calls()
    # Router is the head, not a row in its own Calls column.
    expected_calls = skills - {"proofpunk"}
    print(f"skills={len(skills)} router_calls={len(calls)} expected_calls={len(expected_calls)}")
    if calls != expected_calls:
        fails.append(fail_line("skill-router", expected_calls, calls))
    else:
        print("PASS skill-router")

    refs_disk = shared_refs_on_disk()
    refs_cited = shared_refs_cited()
    print(f"refs disk={len(refs_disk)} cited={len(refs_cited)}")
    if refs_disk != refs_cited:
        fails.append(fail_line("shared-references", refs_disk, refs_cited))
    else:
        print("PASS shared-references")

    claude_cmds = command_stems("claude")
    oc_cmds = command_stems("opencode")
    print(f"commands claude={len(claude_cmds)} opencode={len(oc_cmds)}")
    if claude_cmds != oc_cmds:
        fails.append(fail_line("commands", claude_cmds, oc_cmds))
    else:
        print("PASS commands")

    harnesses = tools_harnesses()
    wired = ci_wired()
    print(f"ci harnesses={len(harnesses)} wired_tokens={len(wired)}")
    missing_ci = sorted(harnesses - wired)
    if missing_ci:
        fails.append("ci-unwired: " + ", ".join(missing_ci))
    else:
        print("PASS ci-wiring")

    # Item 11: the two PreToolUse evidence-dir regexes must stay byte-identical.
    eg = os.path.join(PLUGIN, "hooks", "evidence-guard.sh")
    cg = os.path.join(PLUGIN, "hooks", "capture-guard.sh")
    with open(eg) as f:
        eg_text = f.read()
    with open(cg) as f:
        cg_text = f.read()
    eg_rx = re.search(r'in_evidence = bool\(re\.search\(r"([^"]+)"', eg_text)
    cg_rx = re.search(r'in_evidence = bool\(re\.search\(r"([^"]+)"', cg_text)
    if not eg_rx or not cg_rx:
        fails.append("in_evidence-regex: could not extract regex from both guards")
    elif eg_rx.group(1) != cg_rx.group(1):
        fails.append(
            "in_evidence-regex: evidence-guard.sh and capture-guard.sh diverge: "
            f"{eg_rx.group(1)!r} vs {cg_rx.group(1)!r}"
        )
    else:
        print(f"PASS in_evidence-regex {eg_rx.group(1)!r}")

    if fails:
        print("VERDICT: FAIL")
        for f in fails:
            print(f"  {f}")
        return len(fails)
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
