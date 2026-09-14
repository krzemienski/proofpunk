#!/usr/bin/env python3
"""verify-counts.py — Class-2 detector: live-tree counts vs .md prose.

Walks the canonical plugin sources (skills glob, references/, commands/,
opencode/commands/, hooks.json, agents dirs), computes every count, then
scans every .md file for number-adjacent count words and flags any that
disagree with the live tree.

MUST NOT flag historical provenance prose. Classification follows
evidence/v3-release/00-baseline/drift-inventory.md:

  HISTORICAL (skip): dated release reports, before/after rows, consolidation
  logs, validation-results dated sections, proofpunk-*-report.md, and any
  line that is itself documenting a past count (v1.x, "was 17", "17→19").

  ACTIVE GUIDANCE (flag): live README / AGENTS.md / architecture.md /
  INSTALL.md / usage-guide / plugin README describing the current tree.

Exit 0 on a clean tree. Exit 1 listing file:line of every real mismatch.

Stdlib Python 3 only. Never pipes. Never writes evidence/.
"""
# PP-HARNESS-SUBJECT: kind=python_file_level subjects=SKILL.md,hooks.json keywords=glob,json.load
from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PP = os.path.join(ROOT, "plugins", "proofpunk")

# Count nouns this detector owns. A number immediately before one of these
# words (optionally with a hyphenated qualifier: "shared doctrine files")
# is a candidate claim.
NOUNS = (
    "skills",
    "references",
    "commands",
    "registrations",
    "hooks",
    "agents",
)

# Files that are dated historical artifacts even when they sit at repo root.
HISTORICAL_BASENAMES = {
    "proofpunk-hooks-release-report.md",
    "proofpunk-skills-improvement-report-round2.md",
    "proofpunk-v2-release-report.md",
    # A dated status report, same class as its v2 sibling: it QUOTES the
    # counts a past run measured ("17 delivery skills") as the record of what
    # was wrong at the time. Rewriting those to today's numbers would destroy
    # the finding it exists to preserve.
    "proofpunk-v4-status-report.md",
    "consolidation-decisions.md",
    "validation-results.md",
    "improvements.md",
    "hooks-and-init-design.md",
    "drift-inventory.md",
    "commit-archaeology.md",
    "session-intent-ledger.md",
    "discovery-register.md",
}

# Path prefixes that are never live guidance.
HISTORICAL_PREFIXES = (
    os.path.join(ROOT, "evidence") + os.sep,
    os.path.join(ROOT, "e2e-evidence") + os.sep,
    os.path.join(ROOT, ".debug") + os.sep,
    os.path.join(ROOT, "banks") + os.sep,
    os.path.join(ROOT, "docs") + os.sep,  # generated HTML + dated v3 logs
    os.path.join(ROOT, ".planning") + os.sep,  # dated work-orders, not live doctrine
    os.path.join(ROOT, "examples") + os.sep,
)

# Per-skill NESTED references (skills/<name>/<other>.md) are working notes, not
# plugin inventory, and are excluded. The top-level skills/<name>/SKILL.md files
# are NOT: they are the plugin's live entry points.
#
# Measured 2026-09-14 by mutation: the whole `skills/` subtree was excluded, so
# rewriting the router's own headline "18 delivery skills" -> "11 delivery
# skills" in skills/proofpunk/SKILL.md left this gate at rc=0. Four live count
# claims in the plugin's entry point were entirely unguarded — the exact gap
# step-20 retracted improvement I8 over.
def is_nested_skill_ref(path: str) -> bool:
    skills_root = os.path.join(PP, "skills") + os.sep
    if not path.startswith(skills_root):
        return False
    return os.path.basename(path) != "SKILL.md"

# A line matching any of these is provenance of a past count, not a live claim.
HISTORICAL_LINE = re.compile(
    r"(?:"
    r"\bv1\.\d"                          # dated v1.x release
    r"|\bv2\.(?:0|1)\.\d"                # dated pre-current v2.x
    r"|17\s*→\s*19\s*→\s*18"             # the known drift history
    r"|17→19→18"
    r"|before[-/ ]after"
    r"|was\s+17"
    r"|printed\s+[\"']the 17"
    r"|--help[\"']?\s+said"
    r"|HISTORICAL PROVENANCE"
    r"|dated (?:release|historical|validation)"
    r"|at v1\."
    r"|Round[- ]\d"
    r"|original \d+ skills"              # dated walkthrough ("the original 10")
    r")",
    re.I,
)

# Number before a count noun, with an optional short qualifier between them.
# Captures: (number, noun).
#
# The qualifier slot is load-bearing, not cosmetic. Measured 2026-09-13: the
# pattern previously required the number ADJACENT to the noun, so the router's
# own headline claims — "18 delivery skills", "18 other skill files" — were
# structurally invisible. Mutating them to 17 or 11 produced rc=0: four stale
# counts in the plugin's entry point, entirely unguarded.
#
# Exactly ONE qualifier word is allowed between the number and the noun, and
# only from a closed set. A general `\w+` gap was tried first and produced four
# false positives immediately: "3 unknown skill in --only" (an error-code
# sentence), "6 slash commands" (a real, different count), "4 skills" mid-
# sentence, and a quoted historical string. A count checker that cries wolf
# gets muted, so the qualifier set is explicit and additive.
CLAIM_RE = re.compile(
    r"(?<![A-Za-z0-9./-])(\d+)\s+"
    r"(?:(?:shared\s+(?:doctrine\s+)?|delivery\s+|other\s+|narrow\s+delivery\s+))?"
    r"(skills?|references?|commands?|registrations?|hooks?|agents?)"
    r"\b",
    re.I,
)

# "6+6 commands" and "3/4/3 agents" forms.
PLUS_RE = re.compile(
    r"(?<![A-Za-z0-9./-])(\d+)\s*\+\s*(\d+)\s+commands?\b",
    re.I,
)
SLASH_AGENTS_RE = re.compile(
    r"(?<![A-Za-z0-9./-])(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s+agents?\b",
    re.I,
)

# Markdown table rows put the count and its noun in DIFFERENT COLUMNS, so no
# amount of number-adjacent-to-noun matching can see them. Measured 2026-09-14:
# architecture.md carried `| Commands | commands/*.md | 6 (+6 OpenCode) |` and
# `| Shared references | references/*.md | 15 |` against a live 7+7 and 18, and
# this gate returned rc=0 on both. The noun sits in column 1; CLAIM_RE looks
# beside the digits in column 3 and finds prose.
#
# A row is checked only when its FIRST cell names exactly one known count noun,
# which keeps the rule narrow: a row about something else cannot be dragged in
# by a stray number.
TABLE_ROW_RE = re.compile(r"^\s*\|([^|]+)\|(.*)\|\s*$")
TABLE_NOUN = {
    "skills": "skill",
    "commands": "command",
    "shared references": "reference",
    "references": "reference",
    "hooks": "hook",
    "agents": "agent",
}
# First integer in a cell, ignoring one inside a path/version like `2.2.0`.
CELL_INT_RE = re.compile(r"(?<![A-Za-z0-9./-])(\d+)(?![.\d])")

# Prose-form drift: a count and its noun separated by up to three words, on one
# line. Measured 2026-09-14: this shape carried FOUR live drifts that neither
# CLAIM_RE (needs adjacency) nor the table-row rule (needs the noun in cell 1)
# could see -- "calls all 17 others", "6 slash commands", "17 rows", "15 rows".
#
# A general version of this rule was measured first and REJECTED: it produced
# three false positives out of four hits -- "3 unknown skill" (an error-code
# sentence), "4 are all skills" (unrelated prose), and a dated CHANGELOG line.
# So the gap is closed with two NARROW rules instead, each requiring a word that
# only appears when a real inventory is being described.
#
# Rule 1: "<n> <noun>" where the noun is immediately preceded by a qualifier
# from a closed set that means "of the plugin's own inventory".
PROSE_INVENTORY_RE = re.compile(
    r"(?<![A-Za-z0-9./-])(\d+)\s+"
    r"(?:slash\s+|shared\s+doctrine\s+|shared\s+|other\s+|delivery\s+)"
    r"(skills?|references?|commands?|registrations?|hooks?|agents?|files?)\b",
    re.I,
)
# `files?` is in the noun group ONLY because a qualifier is mandatory: the rule
# can reach it solely as "<n> shared [doctrine] files", which in this repo means
# the reference set. A bare "<n> files" never matches. Measured before adding:
# 0 hits across the whole live tree, and it catches the real stale shape
# `15 shared doctrine files` that AGENTS.md:31 carried.
#
# Rule 2: "calls all <n> others" / "hands off to <n>" -- the router's own edge
# count, which has no noun beside the number at all.
ROUTER_EDGE_RE = re.compile(
    r"(?:calls\s+all\s+|hands\s+off\s+to\s+)(\d+)\s+(?:others?|of\s+them)\b",
    re.I,
)
# Rule 3: "<n> rows" describing one of the router's two tables. Requires the
# table to be named on the same line or the line before, so an unrelated "8
# rows" elsewhere cannot trigger it.
TABLE_ROWS_RE = re.compile(r"(?<![A-Za-z0-9./-])(\d+)\s+rows\b", re.I)
SKILL_TABLE_CUE = re.compile(r"skill\s+calls|one per delivery skill", re.I)
REF_TABLE_CUE = re.compile(r"shared doctrine|one per file in `?references", re.I)


def canon() -> dict:
    """Derive every count from the live tree. Never a literal."""
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

    # DAG edges from the same parse verify-orchestration.py uses.
    n_edges = 0
    router_edges = 0
    for s in skills:
        body = open(os.path.join(PP, "skills", s, "SKILL.md"), encoding="utf-8").read()
        m = re.search(r"## Skill calls\n(.*?)(?=\n## |\Z)", body, re.S)
        if not m:
            continue
        sec = m.group(1)
        if "calls nothing" in sec:
            rows = []
        else:
            rows = re.findall(r"^\| `([a-z0-9-]+)` \|", sec, re.M)
        n_edges += len(rows)
        if s == "proofpunk":
            router_edges = len(rows)

    return {
        "skills": len(skills),
        "references": len(refs),
        "commands": len(cmds),
        "opencode_commands": len(opcmds),
        "hooks": len(hook_sh),          # on-disk .sh files
        "event_keys": len(event_keys),
        "registrations": regs,
        "agents_cc": len(agents_cc),
        "agents_oc": len(agents_oc),
        "agents_omp": len(agents_omp),
        "edges": n_edges,
        "router_edges": router_edges,
        "skill_names": skills,
        "ref_names": refs,
    }


def is_historical_path(path: str) -> bool:
    if os.path.basename(path) in HISTORICAL_BASENAMES:
        return True
    if is_nested_skill_ref(path):
        return True
    for prefix in HISTORICAL_PREFIXES:
        if path.startswith(prefix):
            return True
    # Generated HTML is never live guidance (edit the markdown source).
    if path.endswith(".html"):
        return True
    return False


def expected_for(noun: str, counts: dict) -> set[int]:
    """Acceptable live values for a noun.

    Some nouns have more than one legitimate reading (hooks = 9 scripts
    OR 7 event keys; agents = 3 Claude / 4 OpenCode / 3 OMP; commands =
    6 or 6+6). A claim is a mismatch only when the number is none of
    those live values.
    """
    n = noun.lower().rstrip("s")
    if n == "skill":
        return {counts["skills"], counts["skills"] - 1}  # 19, or 18 delivery
    if n == "reference":
        return {counts["references"]}
    if n == "file":
        # Only reachable through PROSE_INVENTORY_RE's mandatory "shared
        # [doctrine]" qualifier, so this is the reference set by construction.
        return {counts["references"]}
    if n == "command":
        return {counts["commands"], counts["opencode_commands"],
                counts["commands"] + counts["opencode_commands"]}
    if n == "registration":
        return {counts["registrations"]}
    if n == "hook":
        # 9 scripts, 7 event keys, 11 registrations — all live hook counts
        return {counts["hooks"], counts["event_keys"], counts["registrations"]}
    if n == "agent":
        return {counts["agents_cc"], counts["agents_oc"], counts["agents_omp"],
                counts["agents_cc"] + counts["agents_oc"] + counts["agents_omp"]}
    return set()


def iter_md_files() -> list[str]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Do not descend into generated / captured / vcs trees.
        dirnames[:] = [
            d for d in dirnames
            if d not in {".git", "node_modules", "__pycache__", "banks",
                         ".omc", ".omp", ".debug"}
        ]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            if is_historical_path(path):
                continue
            out.append(path)
    return sorted(out)


def check_file(path: str, counts: dict) -> list[str]:
    fails = []
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return fails
    rel = os.path.relpath(path, ROOT)
    for i, line in enumerate(text.splitlines(), 1):
        if HISTORICAL_LINE.search(line):
            continue
        # 6+6 commands
        for m in PLUS_RE.finditer(line):
            a, b = int(m.group(1)), int(m.group(2))
            if a != counts["commands"] or b != counts["opencode_commands"]:
                fails.append(
                    f"{rel}:{i}: {a}+{b} commands "
                    f"(live {counts['commands']}+{counts['opencode_commands']})"
                )
        # 3/4/3 agents
        for m in SLASH_AGENTS_RE.finditer(line):
            got = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            # Accept either CC/OC/OMP or CC/OMP/OC order.
            live_a = (counts["agents_cc"], counts["agents_oc"], counts["agents_omp"])
            live_b = (counts["agents_cc"], counts["agents_omp"], counts["agents_oc"])
            if got not in (live_a, live_b):
                fails.append(
                    f"{rel}:{i}: {'/'.join(map(str, got))} agents "
                    f"(live {counts['agents_cc']}/{counts['agents_oc']}/{counts['agents_omp']} "
                    f"cc/oc/omp)"
                )
        for m in CLAIM_RE.finditer(line):
            n = int(m.group(1))
            noun = m.group(2)
            ok = expected_for(noun, counts)
            if not ok:
                continue
            if n not in ok:
                fails.append(
                    f"{rel}:{i}: {n} {noun} "
                    f"(live accepts {sorted(ok)})"
                )
        # Prose forms: number and noun separated, or no noun at all.
        for m in PROSE_INVENTORY_RE.finditer(line):
            n, noun = int(m.group(1)), m.group(2)
            ok = expected_for(noun, counts)
            if ok and n not in ok:
                fails.append(
                    f"{rel}:{i}: prose '{m.group(0).strip()}' "
                    f"(live accepts {sorted(ok)})"
                )
        for m in ROUTER_EDGE_RE.finditer(line):
            n = int(m.group(1))
            if n != counts["router_edges"]:
                fails.append(
                    f"{rel}:{i}: router edge claim '{m.group(0).strip()}' "
                    f"(live router routes to {counts['router_edges']})"
                )
        for m in TABLE_ROWS_RE.finditer(line):
            n = int(m.group(1))
            ctx = line + " " + (text.splitlines()[i - 2] if i >= 2 else "")
            if SKILL_TABLE_CUE.search(ctx) and n != counts["router_edges"]:
                fails.append(
                    f"{rel}:{i}: '{m.group(0)}' for the Skill calls table "
                    f"(live {counts['router_edges']})"
                )
            elif REF_TABLE_CUE.search(ctx) and n != counts["references"]:
                fails.append(
                    f"{rel}:{i}: '{m.group(0)}' for the Shared doctrine table "
                    f"(live {counts['references']})"
                )
        # Table row whose first cell IS a count noun: check the first integer
        # found in the remaining cells against that noun's live values.
        trow = TABLE_ROW_RE.match(line)
        if trow:
            head = trow.group(1).strip().strip("*` ").lower()
            noun = TABLE_NOUN.get(head)
            if noun:
                ok = expected_for(noun, counts)
                rest = trow.group(2)
                # `6 (+6 OpenCode)` is a commands pair, already reported by
                # PLUS_RE's sibling shape; check both halves explicitly.
                pair = re.search(r"(?<![A-Za-z0-9./-])(\d+)\s*\(\+\s*(\d+)", rest)
                if pair and noun == "command":
                    a, b = int(pair.group(1)), int(pair.group(2))
                    if a != counts["commands"] or b != counts["opencode_commands"]:
                        fails.append(
                            f"{rel}:{i}: table row '{head}' says {a} (+{b}) "
                            f"(live {counts['commands']} (+{counts['opencode_commands']}))"
                        )
                elif ok:
                    cell = CELL_INT_RE.search(rest)
                    if cell and int(cell.group(1)) not in ok:
                        fails.append(
                            f"{rel}:{i}: table row '{head}' says "
                            f"{cell.group(1)} (live accepts {sorted(ok)})"
                        )
    return fails


def main() -> int:
    counts = canon()
    print(
        f"canon: skills={counts['skills']} refs={counts['references']} "
        f"cmds={counts['commands']}+{counts['opencode_commands']} "
        f"hooks.sh={counts['hooks']} events={counts['event_keys']} "
        f"regs={counts['registrations']} "
        f"agents={counts['agents_cc']}/{counts['agents_oc']}/{counts['agents_omp']} "
        f"edges={counts['edges']} (router={counts['router_edges']})"
    )
    fails: list[str] = []
    n_files = 0
    for path in iter_md_files():
        n_files += 1
        fails.extend(check_file(path, counts))
    print(f"scanned {n_files} live .md files")
    if fails:
        print(f"VERDICT: FAIL — {len(fails)} mismatch(es)")
        for f in fails:
            print(f"  {f}")
        return 1
    print("VERDICT: PASS — live .md counts match the tree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
