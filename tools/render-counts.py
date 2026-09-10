#!/usr/bin/env python3
"""render-counts.py — canonical count renderer + marker-region enforcer.

Owns the single tree-walk computation already partially duplicated inside
verify-counts.py's own inventory pass (verify-counts.py:1-46: skills glob,
references, commands, hooks.json registrations). This is the mechanism that
structurally prevents count drift: every skill/reference/command/hook/
agent/theme/router count that README.md or tools/INSTALL.md displays lives
inside a `<!-- proofpunk:counts:begin -->` ... `:end -->` marker region, and
this script is the ONLY writer of that region. Every OTHER mention of those
nouns in those two files is worded so no number needs to agree with it.

Exposes:
  render(target) -> str   the marker-region text for target in
                           {"readme", "install"} — no marker comment lines,
                           just the body between them.
  --check                  regenerate every marker region from the live
                            tree, diff against what is committed, print the
                            diff (file, line), exit 1 on ANY byte
                            difference, exit 0 when every region is
                            byte-identical to a fresh render.
  (default, no flag)       rewrite the marker regions in place. Prints one
                            line per file actually changed.

Stdlib only. Deterministic: every set-derived count is sorted before use,
so the same tree always renders the same bytes. Never shells out, never
pipes a command whose exit code matters.
"""
from __future__ import annotations

import difflib
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PP = os.path.join(ROOT, "plugins", "proofpunk")

MARKER_BEGIN = "<!-- proofpunk:counts:begin -->"
MARKER_END = "<!-- proofpunk:counts:end -->"

TARGETS = {
    "readme": os.path.join(ROOT, "README.md"),
    "install": os.path.join(ROOT, "tools", "INSTALL.md"),
}


def canon() -> dict:
    """Derive every count from the live tree. Never a literal.

    Mirrors verify-counts.py's inventory pass (skills glob, references/,
    commands/, opencode/commands/, hooks.json, agents dirs), plus two
    counts verify-counts.py does not need but the README/INSTALL marker
    regions do: the theme-pack size (themes/palettes.json, the same
    source generate-themes.py renders from) and the router-edge count
    (the proofpunk router skill's own "## Skill calls" table, the same
    parse tools/verify-orchestration.py uses).
    """
    skills = sorted(
        os.path.basename(os.path.dirname(p))
        for p in glob.glob(os.path.join(PP, "skills", "*", "SKILL.md"))
    )
    refs = sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(PP, "references", "*.md"))
    )
    cmds = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(PP, "commands", "*.md"))
    )
    opcmds = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(PP, "opencode", "commands", "*.md"))
    )
    hook_sh = sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(PP, "hooks", "*.sh"))
    )
    agents_cc = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(PP, "agents", "*.md"))
    )
    agents_oc = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(PP, "opencode", "agents", "*.md"))
    )
    agents_omp = sorted(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(PP, "omp", "agents", "*.md"))
    )

    hooks_path = os.path.join(PP, "hooks", "hooks.json")
    with open(hooks_path, encoding="utf-8") as f:
        raw = json.load(f)
    hk = raw.get("hooks", raw)
    event_keys = list(hk.keys())
    regs = 0
    for _ev, blocks in hk.items():
        for b in blocks:
            regs += len(b.get("hooks", []))

    # Router edges: the `proofpunk` router skill's own "## Skill calls"
    # table — how many of the other skills it hands off to.
    router_edges = 0
    router_path = os.path.join(PP, "skills", "proofpunk", "SKILL.md")
    if os.path.exists(router_path):
        body = open(router_path, encoding="utf-8").read()
        m = re.search(r"## Skill calls\n(.*?)(?=\n## |\Z)", body, re.S)
        if m and "calls nothing" not in m.group(1):
            router_edges = len(
                re.findall(r"^\| `([a-z0-9-]+)` \|", m.group(1), re.M)
            )

    # Theme-pack size: same source generate-themes.py renders from.
    themes_path = os.path.join(PP, "themes", "palettes.json")
    with open(themes_path, encoding="utf-8") as f:
        palette_doc = json.load(f)
    themes = len(palette_doc["themes"])

    return {
        "skills": len(skills),
        "references": len(refs),
        "commands": len(cmds),
        "opencode_commands": len(opcmds),
        "hooks_sh": len(hook_sh),
        "event_keys": len(event_keys),
        "registrations": regs,
        "agents_cc": len(agents_cc),
        "agents_oc": len(agents_oc),
        "agents_omp": len(agents_omp),
        "router_edges": router_edges,
        "themes": themes,
    }


def _render_readme(c: dict) -> str:
    return (
        "An execution-first delivery **plugin for Claude Code, oh-my-pi (OMP), and OpenCode**:\n"
        f'{c["skills"]} skills that make "done" mean *proven by end-user testing*. '
        "The AI drives the real system as an end user — clicking,\n"
        "typing, submitting via MCP/automation tools — and any claim it did not actually execute\n"
        "is reported **UNVERIFIED**, never PASS. No mocks, no stubs, no test-mode bypasses.\n"
        "\n"
        f'The `proofpunk` entry router hands off to {c["router_edges"]} of them; '
        f'`references/` holds {c["references"]} shared\n'
        f'doctrine files cited across the set; `--themes` ships {c["themes"]} flat-black cyberpunk\n'
        f'variations. Every skill has a Claude Code command ({c["commands"]} command files) mirrored by an\n'
        f'OpenCode command ({c["opencode_commands"]} files); {c["hooks_sh"]} hook scripts register '
        f'{c["registrations"]} hooks across\n'
        f'{c["event_keys"]} lifecycle events. Plugin-bundled agents: {c["agents_cc"]} on Claude Code, '
        f'{c["agents_oc"]} on\n'
        f'OpenCode, {c["agents_omp"]} on OMP.'
    )


def _render_install(c: dict) -> str:
    return (
        "To confirm hooks actually registered rather than merely landing on disk:\n"
        "\n"
        "```bash\n"
        "bash proofpunk-install.sh --target claude-code --hooks\n"
        "python3 - <<'EOF'\n"
        "import json, os\n"
        'h = json.load(open(os.path.expanduser("~/.claude/settings.json"))).get("hooks", {})\n'
        'n = sum(1 for ev in h for b in h[ev] for e in b.get("hooks", [])\n'
        '        if "proofpunk" in e.get("command", ""))\n'
        'print(f"proofpunk hook registrations: {n}")   # expect '
        f'{c["registrations"]}\n'
        "EOF\n"
        "```\n"
        "\n"
        f'{c["hooks_sh"]} hook scripts register {c["registrations"]} registrations across '
        f'{c["event_keys"]} event keys —\n'
        "the full set. That count comes from `plugins/proofpunk/hooks/hooks.json`, the\n"
        "single source of truth for both which scripts get copied and which events get\n"
        "registered. Re-running with `--hooks` is idempotent — the second run leaves\n"
        "`settings.json` byte-identical.\n"
        "\n"
        f'This installer ships {c["skills"]} skills backed by {c["references"]} shared doctrine references in\n'
        f'`plugins/proofpunk/references/`; `--themes` copies {c["themes"]} flat-black cyberpunk\n'
        f'variations. The OpenCode/OMP `--plugins` glue adds {c["opencode_commands"]} commands and '
        f'{c["agents_oc"]}\n'
        f'agents to `~/.config/opencode/` (the plugin bundles {c["agents_cc"]} agents for Claude Code and\n'
        f'{c["agents_omp"]} for OMP overall).'
    )


def render(target: str) -> str:
    """Return the marker-region text for `target` in {"readme", "install"}."""
    c = canon()
    if target == "readme":
        return _render_readme(c)
    if target == "install":
        return _render_install(c)
    raise ValueError(f"unknown render target: {target!r}")


def _extract_marker(text: str, path: str) -> tuple[str, int, int]:
    """Return (committed marker text, begin line index, end line index).

    Line indices are 0-based positions of the MARKER_BEGIN/MARKER_END
    lines themselves within text.split("\\n").
    """
    lines = text.split("\n")
    begin_idx = end_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == MARKER_BEGIN:
            if begin_idx is not None:
                raise SystemExit(
                    f"{path}: multiple {MARKER_BEGIN!r} markers "
                    "(exactly one counts region is required)"
                )
            begin_idx = i
        elif stripped == MARKER_END:
            if end_idx is not None:
                raise SystemExit(
                    f"{path}: multiple {MARKER_END!r} markers "
                    "(exactly one counts region is required)"
                )
            end_idx = i
    if begin_idx is None or end_idx is None:
        raise SystemExit(f"{path}: missing counts marker region")
    if end_idx <= begin_idx:
        raise SystemExit(f"{path}: {MARKER_END!r} precedes {MARKER_BEGIN!r}")
    committed = "\n".join(lines[begin_idx + 1:end_idx])
    return committed, begin_idx, end_idx


def _rewrite(path: str, target: str) -> bool:
    """Overwrite the marker region in `path` with a fresh render.

    Returns True if the file's bytes changed.
    """
    text = open(path, encoding="utf-8").read()
    committed, begin_idx, end_idx = _extract_marker(text, path)
    fresh = render(target)
    if committed == fresh:
        return False
    lines = text.split("\n")
    new_lines = lines[:begin_idx + 1] + fresh.split("\n") + lines[end_idx:]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    return True


def check() -> int:
    any_fail = False
    for target, path in TARGETS.items():
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding="utf-8").read()
        committed, begin_idx, _end_idx = _extract_marker(text, path)
        fresh = render(target)
        if committed != fresh:
            any_fail = True
            diff = difflib.unified_diff(
                committed.split("\n"),
                fresh.split("\n"),
                fromfile=f"{rel}:{begin_idx + 2} (committed)",
                tofile=f"{rel}:{begin_idx + 2} (fresh render)",
                lineterm="",
            )
            print(f"{rel}: counts marker region does not match a fresh render")
            print("\n".join(diff))
    if any_fail:
        print("VERDICT: FAIL — regenerate with `python3 tools/render-counts.py`")
        return 1
    print("VERDICT: PASS — every counts marker region matches a fresh render")
    return 0


def main() -> int:
    if "--check" in sys.argv[1:]:
        return check()
    changed = []
    for target, path in TARGETS.items():
        if _rewrite(path, target):
            changed.append(os.path.relpath(path, ROOT))
    if changed:
        for rel in changed:
            print(f"rendered {rel}")
    else:
        print("no changes — marker regions already match the live tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
