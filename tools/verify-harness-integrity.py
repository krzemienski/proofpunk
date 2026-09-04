#!/usr/bin/env python3
"""verify-harness-integrity.py — L16 meta-gate: proves every harness in
tools/ actually INVOKES the subject it claims to test, instead of trusting
its label or docstring.

WHY THIS EXISTS (the defect it retires)
----------------------------------------
`tools/dry-run-install.sh` was labelled the installer dry-run harness in
`tools/AGENTS.md` but never invoked `tools/proofpunk-install.sh` at all
(a literal grep for "proofpunk-install.sh" inside it returned 0 hits).
Three gates showed green (test-hooks.sh, dry-run-install.sh,
verify-orchestration.py) alongside five real installer defects, because
nothing checked whether the harness *claiming* installer coverage actually
exercised the installer (commit 5e5150b). This script is that check.

DECLARATION CONVENTION (how a harness tells this gate what it covers)
-----------------------------------------------------------------------
Two ways a harness in tools/ can be "declared", checked in this order:

  1. INLINE TAG — a single-line comment anywhere in the first 60 lines of
     the harness source, of the form:

     start the line with `#`, then the literal token `PP-HARNESS-SUBJECT`
     followed by a colon, then space-separated `key=value` pairs for
     `kind`, `subjects` (comma-joined basenames/tokens), and `keywords`
     (comma-joined invocation-keyword tokens). (Deliberately not shown as
     a literal matching example line in this docstring — this file is
     itself scanned by HARNESS_NAME_RE/TAG_RE and a literal example line
     here would self-tag with a bogus `kind`. See the real declaration
     for this file's own subject a few lines below the MANIFEST list.)

     `kind` is one of: shell_script_subjects | shell_file_subjects |
     python_file_level | python_file_level_literal (see DETECTION METHOD
     below for what each means). `subjects` is a comma-separated list of
     literal basenames/tokens the harness must invoke. `keywords` is a
     comma-separated list of invocation-keyword tokens (command names for
     shell kinds, call-site substrings for python kinds); may be empty for
     python_file_level_literal, where the subjects themselves double as
     the invocation markers.

     This is the self-declaring path: any NEW harness dropped into tools/
     can carry this tag with no edit to this script required.

  2. GRANDFATHERED MANIFEST — the six harnesses that existed before this
     gate was built (test-hooks.sh, test-installer.sh, dry-run-install.sh,
     verify-orchestration.py, sdk_probe.py, verify-citations.py) are
     declared in the MANIFEST constant below instead of carrying an inline
     tag, because this task's file-ownership boundary forbids editing
     those six files. The next
     lane to touch any of them should migrate its declaration to the
     inline-tag form and delete its MANIFEST entry.

  A harness file matching the naming convention `test-*.sh`, `verify-*.py`,
  `dry-run-*.sh`, or `*_probe.py` under tools/ that has NEITHER an inline
  tag NOR a MANIFEST entry is reported UNDECLARED and fails the gate by
  name — a brand-new harness with zero declared coverage is exactly the
  historical defect class, so it must be loud, not silently skipped.

DETECTION METHOD (how "invokes" is decided — and why not filename grep)
-------------------------------------------------------------------------
A naive check greps the harness source for the subject's FULL PATH (e.g.
"plugins/proofpunk/hooks/session-start.sh") and counts hits. That is the
exact mistake that produced a false finding on this repo before: real
harnesses resolve their subject directory through a shell variable first
(`HOOKS="$(cd ... && pwd)"`, then `"$HOOKS/session-start.sh"`), so a
full-path grep against the literal source returns 0 even though the
harness genuinely invokes all nine hook scripts.

This gate instead keys on BASENAME co-occurrence with an invocation
keyword, which is invariant to whatever variable prefixes the path:

  shell_script_subjects / shell_file_subjects (per-line, indirection-safe):
    1. Merge backslash line-continuations into one logical line (a
       multi-line `sed ... "$PP/assets/x.md"` invocation is one command).
    2. Drop pure-comment lines (first non-whitespace char `#`) so a
       comment merely *mentioning* a subject's name cannot count as
       invoking it — comments narrating what a script does are common in
       this repo's headers and must not manufacture a false PASS.
    3. For each required subject basename, require SOME logical line to
       contain BOTH: an invocation keyword in command position (preceded
       by start-of-line/whitespace/`;`/`&`/`|`/`(` AND followed by
       whitespace — this specifically excludes a keyword like "sh" merely
       matching the ".sh" suffix of a filename, which a naive `\bsh\b`
       word-boundary regex would NOT exclude) AND the basename as a
       path component (preceded by `/`, quote, paren, or whitespace).
    This is indirection-safe: `sh "$HOOKS/x.sh"`, `bash "$V/x.sh"`, and
    `bash "$(dirname "$0")/x.sh"` all match on the basename regardless of
    what resolves the prefix.

  python_file_level (co-occurrence anywhere in file, not same line):
    Python discovery and consumption of a subject population are usually
    two different call sites (a glob() that finds files, and a separate
    open() inside a helper that reads them) — see LIMITATIONS below. This
    mode requires the subject token AND every keyword to each appear
    somewhere in non-comment source, without asserting they are on the
    same line or connected by dataflow.

  python_file_level_literal (literal substring presence):
    Used when the "subject" is itself a call token (e.g. `query(`,
    `ClaudeAgentOptions`) rather than a file being read — presence of the
    literal token IS the invocation.

LIMITATIONS — what this gate can and cannot prove (read before trusting it)
-----------------------------------------------------------------------------
- Static-only. It never executes a harness or its subject; it proves the
  harness SOURCE contains an invocation, not that a run succeeds. A
  harness that invokes its subject and then ignores the result would
  still PASS here — this gate is a coverage-presence check, not a
  correctness check.
- python_file_level is file-level co-occurrence, not verified dataflow.
  It cannot distinguish "the open() call reads what the glob() found"
  from "the file happens to contain an unrelated open() call somewhere
  else." The mutation-proof run for this gate exercises this exact
  boundary (see evidence/v3-release/l16-harness/).
- Per-harness CAN/CANNOT OBSERVE statements (printed for every harness on
  every run, and captured in evidence/v3-release/l16-harness/STATEMENT.md)
  describe what the *harness itself* can prove about its subject, which is
  a separate and narrower claim than what this gate proves about the
  harness.

Exit 0 = every declared harness's subject is invoked. Exit N = N harnesses
failed (printed by name and missing subject). Stdlib only.
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(HERE)

TAG_RE = re.compile(r"^\s*#\s*PP-HARNESS-SUBJECT:\s*(.+?)\s*$")
COMMENT_RE = re.compile(r"^\s*#")
HARNESS_NAME_RE = re.compile(r"^(test-.*\.sh|verify-.*\.py|dry-run-.*\.sh|.*_probe\.py)$")


# ---------------------------------------------------------------------------
# Grandfathered declarations for the six pre-existing harnesses. See the
# DECLARATION CONVENTION section in the module docstring for why these are
# centralized here instead of carried as inline tags in the harness files.
# ---------------------------------------------------------------------------
def _hook_basenames(root):
    return sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(root, "plugins", "proofpunk", "hooks", "*.sh"))
    )


def _install_asset_basenames(root):
    # dry-run-install.sh's TRUE subject is the /proofpunk:install command's
    # template + scoped-rules assets, NOT proofpunk-install.sh (which it
    # never invokes — that is the exact historical mislabeling this gate
    # exists to catch). See tools/test-installer.sh's own header comment,
    # which correctly distinguishes the two: "dry-run-install.sh tests the
    # /proofpunk:install slash-command template merge instead — it never
    # invokes this installer."
    return sorted(
        os.path.basename(p)
        for p in (
            glob.glob(os.path.join(root, "plugins", "proofpunk", "assets", "*.md"))
            + glob.glob(os.path.join(root, "plugins", "proofpunk", "assets", "rules", "*.md"))
        )
    )


MANIFEST = [
    dict(
        harness="verify-citations.py",
        kind="python_file_level",
        subject_desc=(
            "every *.md file under plugins/proofpunk/skills/** (top-level "
            "SKILL.md files and bundled references/*.md files), read "
            "directly off disk via os.walk + open — deliberately bypassing "
            "the installer's citation-rewrite/bundle step (see this "
            "harness's own header: the installer's --verify pass structurally "
            "cannot see a repo-level broken citation because install "
            "rewrites+repairs it before verify ever inspects it)"
        ),
        subjects=lambda root: ["SKILL.md", "references"],
        keywords=["os.walk", "open"],
        file_exists_check=False,
        can_observe=(
            "every references/*.md citation actually present in repo source "
            "text, resolved literally relative to the citing file against "
            "the real on-disk tree, split by severity (ERROR: unresolved in "
            "a top-level SKILL.md; WARN: unresolved in a bundled "
            "references/ file) with a frozen baseline so new WARNs are "
            "distinguishable from the known 29"
        ),
        cannot_observe=(
            "whether a citation resolves correctly in an INSTALLED tree "
            "(that is the installer's own --verify pass, a different "
            "subject entirely — this harness exists because that pass is "
            "structurally blind to repo-level breakage); also does not "
            "distinguish a genuine local doctrine break from a donor-skill "
            "provenance citation without --explain-vendor"
        ),
    ),
    dict(
        harness="test-hooks.sh",
        kind="shell_script_subjects",
        subject_desc="every hook script under plugins/proofpunk/hooks/*.sh",
        subjects=_hook_basenames,
        keywords=["sh", "bash", "source"],
        file_exists_check=True,
        can_observe=(
            "each hook script's stdout/decision/exit-code behavior against "
            "realistic hand-built JSON stdin, run in isolation via `sh`"
        ),
        cannot_observe=(
            "whether the HOST (Claude Code) actually wires these scripts to "
            "the declared hook events at runtime, or delivers real (not "
            "hand-built) transcript/tool_input payloads — that requires "
            "driving a live session (sdk_probe.py's stop_guard/instructions_"
            "loaded/blocks_test_file probes)"
        ),
    ),
    dict(
        harness="test-installer.sh",
        kind="shell_script_subjects",
        subject_desc="the real installer binary tools/proofpunk-install.sh",
        subjects=lambda root: ["proofpunk-install.sh"],
        keywords=["sh", "bash"],
        file_exists_check=True,
        can_observe=(
            "real exit codes and on-disk state produced by actually running "
            "the installer against scratch source/target directories and an "
            "isolated HOME (happy path, collision default, --override, "
            "--only, malformed-skill/no-frontmatter detection, --hooks "
            "registration with settings.json parity, and idempotent re-runs)"
        ),
        cannot_observe=(
            "behavior against a user's real home directory, interactive "
            "prompts, or an install performed by an agent following "
            "commands/install.md rather than a direct binary invocation"
        ),
    ),
    dict(
        harness="dry-run-install.sh",
        kind="shell_file_subjects",
        subject_desc=(
            "the /proofpunk:install command's template + scoped-rules assets "
            "(plugins/proofpunk/assets/*.md and assets/rules/*.md) — NOT "
            "tools/proofpunk-install.sh, which this harness never invokes"
        ),
        subjects=_install_asset_basenames,
        keywords=["sed", "cp", "cat"],
        file_exists_check=True,
        can_observe=(
            "whether the command playbook's template substitution "
            "({{PLACEHOLDER}} -> value), marker-preserving CLAUDE.md/AGENTS.md "
            "merge (existing user content survives, markers found and "
            "replaced idempotently), and scoped .claude/rules or "
            ".opencode/rules copy logic behave correctly against a sandbox "
            "fixture, for both claude-code and opencode platform shapes"
        ),
        cannot_observe=(
            "whether an actual agent executing the /proofpunk:install slash "
            "command performs these same steps in the same order — this "
            "harness models the documented playbook in shell, it does not "
            "drive an agent session through the real command; it also "
            "proves nothing about tools/proofpunk-install.sh"
        ),
    ),
    dict(
        harness="verify-orchestration.py",
        kind="python_file_level",
        subject_desc="every SKILL.md under plugins/proofpunk/skills/*/SKILL.md",
        subjects=lambda root: ["SKILL.md"],
        keywords=["glob", "open"],
        file_exists_check=False,
        can_observe=(
            "structural properties of the skill-call graph parsed from every "
            "SKILL.md body: closure (every callee exists, no self-calls), "
            "acyclicity + topological depth, 'Called by' claims match real "
            "edges, implement's stage order matches the DAG, and a 12-word "
            "shingle duplication sweep"
        ),
        cannot_observe=(
            "whether the Skill tool actually loads these files at runtime, "
            "whether a live agent follows the documented call order, or "
            "whether the plugin (not a same-named local copy) is the thing "
            "that loaded — those require sdk_probe.py's router/skill_* probes"
        ),
    ),
    dict(
        harness="sdk_probe.py",
        kind="python_file_level_literal",
        subject_desc=(
            "a live Claude Agent SDK session with the proofpunk plugin loaded "
            "(query() driven by ClaudeAgentOptions)"
        ),
        subjects=lambda root: ["query(", "ClaudeAgentOptions"],
        keywords=[],
        file_exists_check=False,
        can_observe=(
            "whether hooks actually fire (by hook_event_name in the observed "
            "message stream), whether skills actually load (by an observed "
            "Skill tool call plus successful result), and whether guarded "
            "writes actually land or are actually blocked on disk, in a real "
            "running session with the plugin config passed to the SDK"
        ),
        cannot_observe=(
            "determinism across SDK/model versions — probes rely on live "
            "model behavior for prompt-following and are the least "
            "reproducible harness in tools/; a probe FAIL can mean the model "
            "did not attempt the requested action rather than the guard "
            "being broken (require_write_attempt distinguishes these)"
        ),
    ),
    dict(
        # This file matches its own HARNESS_NAME_RE (`verify-*.py`), so it
        # must declare itself or it would fail its own UNDECLARED check —
        # a meta-gate that exempted itself from the rule it enforces would
        # be exactly the kind of unproven-coverage claim it exists to catch.
        harness="verify-harness-integrity.py",
        kind="python_file_level",
        subject_desc=(
            "the tools/ directory's harness source files themselves — this "
            "gate's subject is every other declared harness in tools/"
        ),
        subjects=lambda root: ["MANIFEST", "check_harness"],
        keywords=["per_line_invoked", "file_level_present"],
        file_exists_check=False,
        can_observe=(
            "static source-level co-occurrence of a declared subject "
            "basename/token with an invocation keyword inside each other "
            "harness's source — proves a harness's source CONTAINS an "
            "invocation, not that running the harness succeeds"
        ),
        cannot_observe=(
            "runtime behavior of any harness (whether it actually passes "
            "when run); dataflow between a discovery call site and a "
            "consumption call site in python_file_level mode (see "
            "LIMITATIONS in the module docstring); and correctness of a "
            "harness's assertions, only whether it reaches its subject"
        ),
    ),
]


# ---------------------------------------------------------------------------
# Detection primitives
# ---------------------------------------------------------------------------
def merge_continuations(text):
    """Join backslash line-continuations into single logical lines so a
    multi-line shell command counts as one line for keyword+basename
    co-occurrence (e.g. a 4-line `sed ... "$PP/assets/x.md"` invocation)."""
    out, buf = [], ""
    for ln in text.splitlines():
        stripped = ln.rstrip()
        if stripped.endswith("\\"):
            buf += stripped[:-1] + " "
        else:
            buf += ln
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return out


def non_comment_lines(lines):
    return [ln for ln in lines if not COMMENT_RE.match(ln)]


def per_line_invoked(lines, basename, keywords):
    """shell_script_subjects / shell_file_subjects detection: basename as a
    path component, co-occurring on the same logical line with an
    invocation keyword in command position (see module docstring)."""
    if not keywords:
        return any(basename in ln for ln in lines)
    esc_kw = "|".join(re.escape(k) for k in keywords)
    kw_re = re.compile(r"(?:^|[\s;&|(])(?:" + esc_kw + r")\s")
    b_re = re.compile(r"(?:^|[\s\"'/(])" + re.escape(basename) + r"(?=$|[\s\"')/])")
    return any(kw_re.search(ln) and b_re.search(ln) for ln in lines)


def file_level_present(lines, token):
    return any(token in ln for ln in lines)


def find_inline_tag(text):
    for ln in text.splitlines()[:60]:
        m = TAG_RE.match(ln)
        if m:
            return parse_tag_body(m.group(1))
    return None


def parse_tag_body(body):
    fields = {}
    for part in body.split():
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        fields[k] = v
    kind = fields.get("kind", "")
    subjects = [s for s in fields.get("subjects", "").split(",") if s]
    keywords = [k for k in fields.get("keywords", "").split(",") if k]
    return dict(kind=kind, subjects=lambda root, _s=subjects: _s, keywords=keywords,
                file_exists_check=False, subject_desc="(inline-declared)",
                can_observe="(inline-declared; see harness source)",
                cannot_observe="(inline-declared; see harness source)")


# ---------------------------------------------------------------------------
# Per-harness check
# ---------------------------------------------------------------------------
def check_harness(entry, root, report):
    path = os.path.join(root, "tools", entry["harness"])
    if not os.path.isfile(path):
        report.append((entry["harness"], False, ["harness file itself does not exist: " + path]))
        return False

    text = open(path, encoding="utf-8").read()
    subjects = entry["subjects"](root)
    kind = entry["kind"]
    keywords = entry["keywords"]

    missing = []
    missing_files = []

    if kind in ("shell_script_subjects", "shell_file_subjects"):
        lines = non_comment_lines(merge_continuations(text))
        for subj in subjects:
            if entry.get("file_exists_check"):
                subj_dir = None
                if kind == "shell_script_subjects" and entry["harness"] != "test-installer.sh":
                    subj_dir = os.path.join(root, "plugins", "proofpunk", "hooks")
                elif entry["harness"] == "test-installer.sh":
                    subj_dir = os.path.join(root, "tools")
                elif kind == "shell_file_subjects":
                    for cand in (
                        os.path.join(root, "plugins", "proofpunk", "assets"),
                        os.path.join(root, "plugins", "proofpunk", "assets", "rules"),
                    ):
                        if os.path.isfile(os.path.join(cand, subj)):
                            subj_dir = cand
                            break
                if subj_dir is not None and not os.path.isfile(os.path.join(subj_dir, subj)):
                    missing_files.append(subj)
            if not per_line_invoked(lines, subj, keywords):
                missing.append(subj)
    elif kind == "python_file_level":
        lines = non_comment_lines(text.splitlines())
        for subj in subjects:
            if not file_level_present(lines, subj):
                missing.append(subj)
        for kw in keywords:
            if not file_level_present(lines, kw):
                missing.append(f"keyword:{kw}")
    elif kind == "python_file_level_literal":
        lines = non_comment_lines(text.splitlines())
        for subj in subjects:
            if not file_level_present(lines, subj):
                missing.append(subj)
    else:
        report.append((entry["harness"], False, [f"unknown declaration kind: {kind}"]))
        return False

    reasons = []
    if missing_files:
        reasons.append("subject file(s) do not exist on disk: " + ", ".join(missing_files))
    if missing:
        reasons.append("declared subject not invoked: " + ", ".join(missing))
    ok = not reasons
    report.append((entry["harness"], ok, reasons))
    return ok


def discover_harnesses(root):
    tools_dir = os.path.join(root, "tools")
    found = []
    for name in sorted(os.listdir(tools_dir)):
        if HARNESS_NAME_RE.match(name):
            found.append(name)
    return found


def build_effective_manifest(root):
    """MANIFEST entries take precedence for their named harness; any
    harness-shaped file in tools/ carrying an inline tag but no MANIFEST
    entry is added from the tag; anything else is UNDECLARED."""
    by_name = {e["harness"]: e for e in MANIFEST}
    undeclared = []
    for name in discover_harnesses(root):
        if name in by_name:
            continue
        path = os.path.join(root, "tools", name)
        text = open(path, encoding="utf-8").read()
        tag = find_inline_tag(text)
        if tag is None:
            undeclared.append(name)
        else:
            tag["harness"] = name
            by_name[name] = tag
    return list(by_name.values()), undeclared


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Assert every harness in tools/ actually invokes the subject it "
            "claims to test. See the module docstring (python3 -m pydoc, or "
            "read the top of this file) for the full declaration convention "
            "and detection method."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument(
        "--root",
        default=DEFAULT_ROOT,
        help="repo root to check (default: parent of this script's tools/ dir); "
        "point this at a sandbox copy to run a mutation test without touching "
        "the real tools/ files",
    )
    args = ap.parse_args()
    root = os.path.abspath(args.root)

    manifest, undeclared = build_effective_manifest(root)
    report = []
    print(f"== harness-integrity: checking {len(manifest)} declared harness(es) under {root}/tools")
    for entry in sorted(manifest, key=lambda e: e["harness"]):
        print(f"\n-- {entry['harness']}")
        print(f"   SUBJECT:        {entry['subject_desc']}")
        print(f"   CAN OBSERVE:    {entry['can_observe']}")
        print(f"   CANNOT OBSERVE: {entry['cannot_observe']}")
        ok = check_harness(entry, root, [])
        report.append((entry["harness"], ok, None))
        # re-run to capture reasons (check_harness appends to a report list
        # passed by reference; call again cleanly to get reasons for print)
        reasons_holder = []
        check_harness(entry, root, reasons_holder)
        _, _, reasons = reasons_holder[0]
        if ok:
            print(f"   [PASS] invokes its declared subject")
        else:
            print(f"   [FAIL] does NOT invoke its declared subject:")
            for r in reasons:
                print(f"          - {r}")

    fails = [name for name, ok, _ in report if not ok]

    if undeclared:
        print(f"\n-- UNDECLARED harness(es) in tools/ (no inline tag, no MANIFEST entry):")
        for name in undeclared:
            print(f"   [FAIL] {name} — add a `# PP-HARNESS-SUBJECT:` tag or a MANIFEST entry")
        fails.extend(undeclared)

    print(f"\nHARNESS INTEGRITY FAILS: {len(fails)}")
    if fails:
        print("FAILING: " + ", ".join(fails))
    sys.exit(len(fails))


if __name__ == "__main__":
    main()
