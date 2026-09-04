#!/usr/bin/env python3
"""gauge-report.py — recompute every Proofpunk v3 Gauge Board row directly
from sealed evidence artifacts under evidence/v3-release/, never from
scrollback or prose. Writes gauge-report.md + gauge-report.json.

Every gauge cites its evidence artifact by `path@sha256`. If the cited path
does not resolve to a real file on disk, the gauge is reported UNVERIFIED —
never PASS — and UNVERIFIED counts as a failing gauge for the exit code.

Exit code contract (binding, see docs/v3-gauges.md and .planning/v3-criteria.md
C6): exit 0 ONLY when every gauge's status is PASS. Any UNMET or UNVERIFIED
gauge is a non-zero exit. This is the honest state today — the tool is
expected to fail until the v3 release actually closes every gauge.

stdlib only. No new runtime dependencies.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
EVID = os.path.join(ROOT, "evidence", "v3-release")
SK = os.path.join(ROOT, "plugins", "proofpunk", "skills")

# ---------------------------------------------------------------------------
# Evidence-artifact resolution — every gauge's evidence must go through this.
# ---------------------------------------------------------------------------


def sha256_of(path):
    """Return sha256 hex digest of path, or None if path is not a real file."""
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cite(rel_path):
    """Resolve rel_path (repo-root-relative) to a path@sha256 citation.

    Returns (citation_string, resolved_bool). An unresolved path yields a
    citation string that still names the path, but resolved=False — callers
    MUST treat that as UNVERIFIED, never as a passing measurement.
    """
    abspath = os.path.join(ROOT, rel_path)
    digest = sha256_of(abspath)
    if digest is None:
        return (f"{rel_path}@UNRESOLVED", False)
    return (f"{rel_path}@sha256:{digest}", True)


# ---------------------------------------------------------------------------
# Gauge result record
# ---------------------------------------------------------------------------

GAUGES = []


def gauge(num, lane, name, unit, baseline, target, measured_fn):
    """Run measured_fn() -> (value, status, evidence_citations:list[str],
    all_resolved:bool, detail:str). Record a gauge row.

    status is one of: "PASS", "UNMET", "UNVERIFIED", "UNMEASURED".
    An UNVERIFIED evidence citation always forces status to "UNVERIFIED"
    regardless of what measured_fn concluded about the raw number — a gauge
    cannot be PASS on evidence that does not resolve to a real sealed file.
    """
    try:
        value, status, citations, all_resolved, detail = measured_fn()
    except Exception as e:  # noqa: BLE001 — a broken gauge is UNVERIFIED, not a crash
        value, status, citations, all_resolved, detail = (
            None,
            "UNVERIFIED",
            [],
            False,
            f"gauge computation raised: {e!r}",
        )
    if not all_resolved and status != "UNMEASURED":
        status = "UNVERIFIED"
    GAUGES.append(
        {
            "num": num,
            "lane": lane,
            "name": name,
            "unit": unit,
            "baseline": baseline,
            "target": target,
            "measured": value,
            "status": status,
            "evidence": citations,
            "detail": detail,
        }
    )


# ---------------------------------------------------------------------------
# Frontmatter description-length parser (stdlib only — no PyYAML dependency
# at runtime; verified byte-for-byte against yaml.safe_load for all 18 skills
# during authoring, see evidence/v3-release/l-gauges/).
# ---------------------------------------------------------------------------


def _fold_block(block_lines):
    while block_lines and block_lines[-1] == "":
        block_lines.pop()
    out = []
    prev_blank = False
    for l in block_lines:
        if l == "":
            out.append("\n")
            prev_blank = True
        else:
            if out and not prev_blank:
                out.append(" ")
            out.append(l)
            prev_blank = False
    return "".join(out)


def parse_frontmatter_fields(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    lines = m.group(1).split("\n")
    fields = {}
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        mm = re.match(r"^([A-Za-z0-9_]+):\s?(.*)$", line)
        if mm and not line.startswith(" "):
            key, val = mm.group(1), mm.group(2)
            if val.strip() in (">", ">-", ">+"):
                i += 1
                block = []
                indent = None
                while i < n:
                    l = lines[i]
                    if l.strip() == "":
                        block.append("")
                        i += 1
                        continue
                    if not l.startswith(" "):
                        break
                    ind = len(l) - len(l.lstrip(" "))
                    if indent is None:
                        indent = ind
                    block.append(l[indent:])
                    i += 1
                fields[key] = _fold_block(block)
                continue
            fields[key] = val.strip()
            i += 1
            continue
        i += 1
    return fields


def load_skills():
    dirs = sorted(
        d
        for d in os.listdir(SK)
        if os.path.isfile(os.path.join(SK, d, "SKILL.md"))
    )
    out = {}
    for s in dirs:
        p = os.path.join(SK, s, "SKILL.md")
        text = open(p, encoding="utf-8").read()
        fields = parse_frontmatter_fields(text)
        m = re.match(r"^---\n.*?\n---\n", text, re.S)
        body = text[m.end() :] if m else text
        out[s] = {
            "fields": fields,
            "body_bytes": len(body.encode("utf-8")),
            "path": p,
        }
    return out


# ---------------------------------------------------------------------------
# Citation resolver (repo-tree, resolved relative to the citing file) — the
# same method used to produce citation-integrity-finding.md.
# ---------------------------------------------------------------------------

CITE_RE = re.compile(r"(?:\.\./)*references/[A-Za-z0-9_.\-/]+\.md")


def sweep_repo_tree_citations():
    results = []
    for dirpath, _dirnames, filenames in os.walk(SK):
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            text = open(full, encoding="utf-8", errors="replace").read()
            for m in CITE_RE.finditer(text):
                cited = m.group(0)
                resolved_path = os.path.normpath(
                    os.path.join(os.path.dirname(full), cited)
                )
                results.append(
                    {
                        "citing_file": os.path.relpath(full, ROOT),
                        "cited": cited,
                        "resolved": os.path.isfile(resolved_path),
                        "top_level": os.path.basename(full) == "SKILL.md",
                    }
                )
    return results


# ---------------------------------------------------------------------------
# Gauge #1 (L1) — description budget: 18/18 skills conform to spec basics.
# ---------------------------------------------------------------------------


def g_spec_basics():
    ev_path = "evidence/v3-release/00-baseline/description-budget-baseline.md"
    citation, resolved = cite(ev_path)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed baseline artifact missing")
    skills = load_skills()
    total = len(skills)
    passing = 0
    detail_fails = []
    for name, info in skills.items():
        f = info["fields"]
        ok_name = f.get("name") == name
        desc = f.get("description", "")
        ok_len = len(desc) <= 1024
        # unrecognized frontmatter fields
        m = re.match(r"^---\n(.*?)\n---\n", open(info["path"], encoding="utf-8").read(), re.S)
        top_keys = set(
            re.match(r"^([A-Za-z0-9_]+):", l).group(1)
            for l in m.group(1).split("\n")
            if re.match(r"^[A-Za-z0-9_]+:", l)
        )
        ok_fields = top_keys <= {"name", "description"}
        if ok_name and ok_len and ok_fields:
            passing += 1
        else:
            detail_fails.append(name)
    status = "PASS" if passing == total else "UNMET"
    val = f"{passing}/{total}"
    detail = "all skills pass name/description-length/field-set basics" if not detail_fails else f"failing: {detail_fails}"
    return (val, status, [citation], True, detail)


gauge(
    num=1,
    lane="L12",
    name="Skills passing spec basics (name/desc/fields)",
    unit="skills",
    baseline="18/18",
    target="18/18",
    measured_fn=g_spec_basics,
)


# ---------------------------------------------------------------------------
# Gauge #7 (L10) — description chars vs Claude Code's listing budget.
# ---------------------------------------------------------------------------


def g_description_budget():
    ev_path = "evidence/v3-release/00-baseline/description-budget-baseline.md"
    citation, resolved = cite(ev_path)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed baseline artifact missing")
    skills = load_skills()
    total_chars = sum(len(info["fields"].get("description", "")) for info in skills.values())
    budget = 1536
    ratio = total_chars / budget
    status = "PASS" if total_chars <= budget else "UNMET"
    val = f"{total_chars} vs {budget} ({ratio:.1f}x)"
    detail = "aggregate description text exceeds the Claude Code listing budget" if status == "UNMET" else "within budget"
    return (val, status, [citation], True, detail)


gauge(
    num=7,
    lane="L10",
    name="Total description chars vs 1,536-char listing budget",
    unit="chars",
    baseline="13,949 (9.1x)",
    target="<=1,536 (1.0x)",
    measured_fn=g_description_budget,
)


# ---------------------------------------------------------------------------
# Gauge #8 (L10) — median skill body size (context-economy proxy).
# ---------------------------------------------------------------------------


def g_median_body_size():
    ev_path = "evidence/v3-release/00-baseline/description-budget-baseline.md"
    citation, resolved = cite(ev_path)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed baseline artifact missing")
    skills = load_skills()
    sizes = sorted(info["body_bytes"] for info in skills.values())
    n = len(sizes)
    if n == 0:
        return (None, "UNVERIFIED", [citation], True, "no skills found")
    median = sizes[n // 2] if n % 2 == 1 else (sizes[n // 2 - 1] + sizes[n // 2]) / 2
    # This gauge is a context-economy PROXY with no numeric target defined
    # anywhere in the sealed baseline or v3-criteria.md — report the measured
    # number and mark it UNMEASURED against target rather than inventing a
    # threshold. Reported for trend tracking only; never counts as passing.
    return (
        f"{median:.0f} bytes",
        "UNMEASURED",
        [citation],
        True,
        "no numeric target defined in sealed sources — trend-tracking only, does not gate release",
    )


gauge(
    num=8,
    lane="L10",
    name="Median skill body size (context-economy proxy)",
    unit="bytes",
    baseline="6,266",
    target="UNMEASURED (no target defined in sealed sources)",
    measured_fn=g_median_body_size,
)


# ---------------------------------------------------------------------------
# Gauge #2 (L4) — stop-guard scout-substring false-PASS: mutation-proven fix.
# ---------------------------------------------------------------------------


def g_scout_substring_fix():
    run_dir = "evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring"
    verdict_rel = f"{run_dir}/VERDICT.md"
    citation, resolved = cite(verdict_rel)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed VERDICT.md missing")
    citations = [citation]
    all_resolved = True
    for fn in (
        "step-00-root-cause.md",
        "step-01-baseline-fix-present.log",
        "step-02-mutated-fix-reverted.log",
        "step-03-restored.log",
    ):
        c, r = cite(f"{run_dir}/{fn}")
        citations.append(c)
        all_resolved = all_resolved and r
    if not all_resolved:
        return (None, "UNVERIFIED", citations, False, "one or more three-arm logs missing from sealed run")
    verdict_text = open(os.path.join(ROOT, verdict_rel), encoding="utf-8").read()
    baseline_m = re.search(r"baseline\s+rc=0\s+PASS=(\d+)", verdict_text)
    mutated_m = re.search(r"mutated\s+rc=1\s+PASS=(\d+)", verdict_text)
    restored_m = re.search(r"restored\s+rc=0\s+PASS=(\d+)", verdict_text)
    if not (baseline_m and mutated_m and restored_m):
        return (None, "UNVERIFIED", citations, True, "three-arm mutation proof pattern not found in VERDICT.md")
    baseline_n, mutated_n, restored_n = baseline_m.group(1), mutated_m.group(1), restored_m.group(1)
    # byte-identical baseline vs restored logs
    b_hash = sha256_of(os.path.join(ROOT, run_dir, "step-01-baseline-fix-present.log"))
    r_hash = sha256_of(os.path.join(ROOT, run_dir, "step-03-restored.log"))
    byte_identical = b_hash == r_hash
    discriminates = mutated_n != baseline_n and byte_identical and baseline_n == restored_n
    status = "PASS" if discriminates else "UNMET"
    val = f"baseline={baseline_n} mutated={mutated_n} restored={restored_n} byte_identical={byte_identical}"
    detail = "mutation flips the gate red by name and restore is byte-identical" if discriminates else "mutation proof does not discriminate"
    return (val, status, citations, True, detail)


gauge(
    num=2,
    lane="L4",
    name="stop-guard scout-substring false-PASS closed, mutation-proven",
    unit="cases",
    baseline="47 -> 48 cases",
    target="mutation-proven (baseline=mutated+1, restored byte-identical to baseline)",
    measured_fn=g_scout_substring_fix,
)


# ---------------------------------------------------------------------------
# Gauge #3 (L1) — repo-tree citation integrity.
# ---------------------------------------------------------------------------


def g_citation_integrity():
    ev_path = "evidence/v3-release/00-baseline/citation-integrity-finding.md"
    citation, resolved = cite(ev_path)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed finding artifact missing")
    rows = sweep_repo_tree_citations()
    unresolved = [r for r in rows if not r["resolved"]]
    top_level_unresolved = [r for r in unresolved if r["top_level"]]
    total_unresolved = len(unresolved)
    status = "PASS" if total_unresolved == 0 else "UNMET"
    val = f"{total_unresolved} unresolved (top-level: {len(top_level_unresolved)})"
    detail = (
        "all citations resolve" if total_unresolved == 0
        else f"unresolved: {sorted(set(r['citing_file'] for r in unresolved))}"
    )
    return (val, status, [citation], True, detail)


gauge(
    num=3,
    lane="L1",
    name="Unresolved repo-tree citations (name/desc/fields resolve relative to citing file)",
    unit="citations",
    baseline="30 -> 29 (top-level: 1 -> 0)",
    target="0",
    measured_fn=g_citation_integrity,
)


# ---------------------------------------------------------------------------
# Gauge #4 (L16) — commands proven at the real slash-command surface.
# ---------------------------------------------------------------------------


def g_command_surface_proven():
    ev_path = "evidence/v3-release/00-baseline/command-surface-map.md"
    citation, resolved = cite(ev_path)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed command-surface-map.md missing")
    text = open(os.path.join(ROOT, ev_path), encoding="utf-8").read()
    m = re.search(r"\*\*zero\*\* have a\s*\nsingle artifact proving the full chain", text)
    if not m:
        return (None, "UNVERIFIED", [citation], True, "expected 'zero' summary claim not found verbatim in sealed artifact")
    return ("0/6", "UNMET", [citation], True, "no command has a single artifact proving slash-typed -> flag mapping -> real execution -> observed result")


gauge(
    num=4,
    lane="L16",
    name="Commands proven end-to-end at the real slash-command surface",
    unit="commands",
    baseline="0/6",
    target="6/6",
    measured_fn=g_command_surface_proven,
)


# ---------------------------------------------------------------------------
# Gauge #5 (L2/L3) — release gates: all 4 exit 0, exit codes captured
# separately from stdout.
# ---------------------------------------------------------------------------


def g_gates_green():
    run_dir = "evidence/v3-release/00-baseline/gates-20260904T051258"
    ec_rel = f"{run_dir}/exit-codes.txt"
    citation, resolved = cite(ec_rel)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed exit-codes.txt missing")
    citations = [citation]
    all_resolved = True
    for fn in (
        "README.md",
        "test-hooks.sh.log",
        "test-installer.sh.log",
        "dry-run-install.sh.log",
        "verify-orchestration.py.log",
    ):
        c, r = cite(f"{run_dir}/{fn}")
        citations.append(c)
        all_resolved = all_resolved and r
    ec_text = open(os.path.join(ROOT, ec_rel), encoding="utf-8").read()
    rcs = dict(re.findall(r"(\S+)\s+rc=(\d+)", ec_text))
    if len(rcs) != 4:
        return (None, "UNVERIFIED", citations, all_resolved, f"expected 4 gate exit codes, found {len(rcs)}")
    all_zero = all(v == "0" for v in rcs.values())
    status = "PASS" if (all_zero and all_resolved) else ("UNVERIFIED" if not all_resolved else "UNMET")
    val = ", ".join(f"{k}={v}" for k, v in rcs.items())
    detail = "all 4 gates rc=0, exit codes captured separately from stdout" if all_zero else f"non-zero gate(s): {[k for k,v in rcs.items() if v!='0']}"
    return (val, status, citations, all_resolved, detail)


gauge(
    num=5,
    lane="L2/L3",
    name="Release gates: all exit 0, exit codes captured separately from stdout",
    unit="gates",
    baseline="4/4 rc=0",
    target="4/4 rc=0 (this is a sealed snapshot — re-run tools/*.sh/py to confirm current tree)",
    measured_fn=g_gates_green,
)


# ---------------------------------------------------------------------------
# Gauge #6 (L14) — 18/18 skills present, ground-truth counts.
# ---------------------------------------------------------------------------


def g_skill_count():
    ev_path = "evidence/v3-release/00-baseline/description-budget-baseline.md"
    citation, resolved = cite(ev_path)
    if not resolved:
        return (None, "UNVERIFIED", [citation], False, "sealed baseline artifact missing")
    skills = load_skills()
    n = len(skills)
    status = "PASS" if n == 18 else "UNMET"
    return (f"{n}", status, [citation], True, f"{n} skill directories with SKILL.md found under plugins/proofpunk/skills/")


gauge(
    num=6,
    lane="L14",
    name="Skill count (ground truth, derived not restated)",
    unit="skills",
    baseline="18",
    target="18",
    measured_fn=g_skill_count,
)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def status_symbol(s):
    return {"PASS": "PASS", "UNMET": "UNMET", "UNVERIFIED": "UNVERIFIED", "UNMEASURED": "UNMEASURED"}.get(s, s)


def write_report():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except Exception:
        head = "UNKNOWN"
    try:
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True
            ).stdout.strip()
        )
    except Exception:
        dirty = None

    lines = []
    lines.append("# gauge-report — recomputed from sealed artifacts")
    lines.append("")
    lines.append(f"Generated: {now} | Repo HEAD: `{head}` (working tree {'dirty' if dirty else 'clean' if dirty is False else 'UNKNOWN'})")
    lines.append("")
    lines.append("Every row is computed fresh by this script from files under")
    lines.append("`evidence/v3-release/**` and the live skill tree. No number is copied")
    lines.append("from prose. A row whose evidence path does not resolve to a real file")
    lines.append("is reported UNVERIFIED, never PASS.")
    lines.append("")
    lines.append("| # | Lane | Gauge (unit) | Baseline | Target | Measured | Status | Evidence |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for g in GAUGES:
        ev = "<br>".join(f"`{e}`" for e in g["evidence"]) if g["evidence"] else "(none)"
        lines.append(
            f"| {g['num']} | {g['lane']} | {g['name']} ({g['unit']}) | {g['baseline']} | {g['target']} | "
            f"{g['measured']} | **{status_symbol(g['status'])}** | {ev} |"
        )
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    for g in GAUGES:
        lines.append(f"### Gauge #{g['num']} ({g['lane']}) — {g['name']}")
        lines.append(f"- Status: **{g['status']}**")
        lines.append(f"- Measured: {g['measured']}")
        lines.append(f"- Detail: {g['detail']}")
        lines.append("")

    passing = sum(1 for g in GAUGES if g["status"] == "PASS")
    total = len(GAUGES)
    lines.append(f"## Summary: {passing}/{total} gauges PASS")
    lines.append("")
    for g in GAUGES:
        if g["status"] != "PASS":
            lines.append(f"- Gauge #{g['num']} ({g['lane']}): **{g['status']}** — {g['name']}")

    md = "\n".join(lines) + "\n"
    md_path = os.path.join(ROOT, "gauge-report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    payload = {
        "generated": now,
        "head": head,
        "dirty": dirty,
        "gauges": GAUGES,
        "summary": {"passing": passing, "total": total},
    }
    json_path = os.path.join(ROOT, "gauge-report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return md_path, json_path, passing, total


def main():
    md_path, json_path, passing, total = write_report()
    print(f"gauge-report: {passing}/{total} gauges PASS")
    print(f"  wrote {os.path.relpath(md_path, ROOT)}")
    print(f"  wrote {os.path.relpath(json_path, ROOT)}")
    for g in GAUGES:
        marker = "PASS" if g["status"] == "PASS" else g["status"]
        print(f"  [{marker}] #{g['num']} ({g['lane']}) {g['name']}: {g['measured']}")
    if passing != total:
        print(f"VERDICT: FAIL — {total - passing}/{total} gauge(s) not PASS")
        sys.exit(1)
    print("VERDICT: PASS — every gauge meets target")
    sys.exit(0)


if __name__ == "__main__":
    main()
