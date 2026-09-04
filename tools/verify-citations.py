#!/usr/bin/env python3
"""verify-citations.py — repo-tree citation gate for plugins/proofpunk/skills/**.

WHY THIS EXISTS (read before touching)
---------------------------------------
tools/proofpunk-install.sh's --verify pass structurally CANNOT see a broken
repo-level citation. Its install step (lines ~284-322) REWRITES citation
paths (`../../references/X` -> `references/X`) and bundles cited shared
doctrine into the installed skill's own references/ dir using an OPTIONAL
`(references/)?` prefix match (line ~316) — so a citation that is broken IN
THE REPO gets silently repaired by the install/bundle step before verify
(line ~653) ever inspects it. The installed tree then verifies clean and
prints a checkmark for a repo that has broken citations in it. This is a
Class-1 structurally-blind harness: the thing it "verifies" is never the
thing a repo reader (or a fresh `git clone` + read) actually sees.

This script performs NO rewriting and NO bundling. It resolves every
`references/...md` and `../.../references/...md` citation found inside
plugins/proofpunk/skills/** LITERALLY, relative to the citing file, against
the real repo tree on disk — exactly what a human (or an agent) reading the
repo would have to do.

SEVERITY MODEL
--------------
- ERROR: an unresolved citation inside a top-level SKILL.md (the file a user
  or agent reads first, and the only file the installer's --skip-skills-free
  "just read the doctrine" flow guarantees is present). Currently: 0.
- WARN:  an unresolved citation inside a skill's bundled references/ dir.
  These are frequently either (a) provenance-header citations to a FOREIGN
  upstream/donor skill's OWN internal layout (see `--explain-vendor`), or
  (b) genuine local doctrine breakage. This script does not distinguish the
  two automatically — see `--explain-vendor` for the investigated verdict.
  Currently: 29 (frozen baseline below).

EXIT CODE CONTRACT
-------------------
- Default:  exit 1 iff ERROR count > 0. WARN count NEVER affects the default
  exit code (baseline or new) — this keeps the gate adoptable today without
  blocking on the known 29.
- --strict: exit 1 iff (ERROR count > 0) OR (WARN count > 0), including the
  frozen baseline 29. Use this to notice growth or to eventually clear the
  backlog to zero.

Every WARN is printed tagged `(baseline)` or `(NEW)` against the frozen
29-item baseline below, so growth is DISTINGUISHABLE in the report even
though it does not change the default exit code. A CI job that also greps
the report for `(NEW)` (or diffs the WARN total against 29) gets a hard
regression signal without this script needing an extra flag for it.

USAGE
-----
    tools/verify-citations.py                 # default: fail only on ERROR
    tools/verify-citations.py --strict         # fail on ERROR or any WARN
    tools/verify-citations.py --explain-vendor # print the vendored-xc-mcp verdict, no scan
    tools/verify-citations.py --root /path/to/repo
"""
from __future__ import annotations

import argparse
import os
import re
import sys

# Citations this script resolves: `references/X.md` or `../../references/X.md`,
# optionally backticked or bare prose. Anchored so it does not match inside a
# longer path/URL segment (e.g. "foo/references/x.md" mid-word is still fine —
# the lookbehind only rejects an immediately preceding identifier/slash char
# glued directly onto "references", which is what a URL host/path segment
# would produce; a real citation always starts the reference token cleanly).
CITATION_RE = re.compile(
    r'(?<![A-Za-z0-9_/])((?:\.\./)*references/[A-Za-z0-9._/-]+\.md)'
)


def find_citations(skills_root: str):
    """Yield (abs_path, line_no, raw_citation, resolved_bool) for every
    references/*.md citation found under skills_root."""
    for dirpath, _dirnames, filenames in sorted(
        (d, dn, fn) for d, dn, fn in os.walk(skills_root)
    ):
        for fn in sorted(filenames):
            if not fn.endswith('.md'):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding='utf-8') as f:
                    lines = f.readlines()
            except (OSError, UnicodeDecodeError):
                continue
            for lineno, line in enumerate(lines, start=1):
                for m in CITATION_RE.finditer(line):
                    raw = m.group(1)
                    # strip trailing punctuation / markdown fence noise a
                    # prose sentence might glue onto the citation
                    cite = raw.split('#')[0].rstrip('.,;:`)]')
                    if not cite:
                        continue
                    target = os.path.normpath(os.path.join(dirpath, cite))
                    resolved = os.path.exists(target)
                    yield (path, lineno, cite, resolved)


def is_top_level_skill_md(path: str, skills_root: str) -> bool:
    """True iff path is skills_root/<skill-name>/SKILL.md exactly (not a
    nested SKILL.md, of which none currently exist, but the check is
    explicit rather than assumed)."""
    if os.path.basename(path) != 'SKILL.md':
        return False
    skill_dir = os.path.dirname(path)
    return os.path.dirname(skill_dir) == os.path.normpath(skills_root)


# ---------------------------------------------------------------------------
# Frozen baseline: the 29 unresolved bundled-reference citations present on
# the tree at the time this gate was built (v3 Phase 5, HEAD 9963648 + the
# tui-testing/SKILL.md:13 fix that brought ERRORs to 0). Recorded as
# (repo-relative-posix-path, line, citation) so a NEW warn — any tuple not
# in this set — is immediately distinguishable in the report as `(NEW)`
# regardless of whether it is a true regression or a legitimate new vendor
# citation that simply hasn't been triaged yet.
#
# This baseline intentionally does NOT get auto-regenerated by this script.
# Shrinking it (fixing a citation) is always safe. Growing it requires a
# human to update this literal set, which is the whole point: the number
# cannot change without someone noticing the diff.
KNOWN_WARN_BASELINE = frozenset({
    ("plugins/proofpunk/skills/mobile-validation-runner/references/simctl-command-reference.md", 1, "references/reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-accessibility-patterns.md", 1, "references/accessibility-patterns.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-caching-strategy.md", 1, "references/caching-strategy.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-mcp-configuration.md", 1, "references/mcp-configuration.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-operation-enums.md", 1, "references/operation-enums.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-progressive-disclosure.md", 1, "references/progressive-disclosure.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-tool-reference.md", 1, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-app-deployment.md", 16, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-app-deployment.md", 17, "references/operation-enums.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-build-project.md", 16, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-build-project.md", 17, "references/progressive-disclosure.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-configure-caching.md", 16, "references/caching-strategy.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-configure-caching.md", 17, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-debug-failures.md", 17, "references/progressive-disclosure.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-debug-failures.md", 18, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-fresh-install.md", 13, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-fresh-install.md", 14, "references/operation-enums.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-run-tests.md", 16, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-run-tests.md", 17, "references/progressive-disclosure.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-simulator-management.md", 17, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-simulator-management.md", 18, "references/operation-enums.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-ui-automation.md", 16, "references/accessibility-patterns.md"),
    ("plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-ui-automation.md", 17, "references/tool-reference.md"),
    ("plugins/proofpunk/skills/root-cause-debugging/references/expert-debugging-mindset.md", 1, "references/debugging-mindset.md"),
    ("plugins/proofpunk/skills/root-cause-debugging/references/expert-hypothesis-testing.md", 1, "references/hypothesis-testing.md"),
    ("plugins/proofpunk/skills/root-cause-debugging/references/expert-investigation-techniques.md", 1, "references/investigation-techniques.md"),
    ("plugins/proofpunk/skills/root-cause-debugging/references/expert-verification-patterns.md", 1, "references/verification-patterns.md"),
    ("plugins/proofpunk/skills/root-cause-debugging/references/expert-when-to-research.md", 1, "references/when-to-research.md"),
    ("plugins/proofpunk/skills/stack-testing/references/webapp-testing.md", 120, "references/web-validation.md"),
})


VENDOR_VERDICT = """\
VENDORED-VS-BROKEN VERDICT: plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-*.md
======================================================================================================

CLAIM: the 23 unresolved citations in xc-mcp-*.md files are broken PROOFPUNK
doctrine citations that should be fixed by bundling more files.

FINDING: FALSE. They are vendored pass-through content citing a FOREIGN
upstream project's OWN internal directory layout. Rewriting or "fixing"
them by bundling proofpunk-local files at those paths would CORRUPT
correct vendored content, not repair it.

EVIDENCE
--------
1. Every one of the 12 provenance-header hits (line 1 of each xc-mcp-*.md
   and simctl-command-reference.md, and 5 more in root-cause-debugging's
   expert-*.md files) opens with an explicit machine-readable attribution
   line, e.g.:

     xc-mcp-tool-reference.md:1
       > Incorporated from the `xc-mcp` skill (references/tool-reference.md).

     simctl-command-reference.md:1
       > Incorporated from the `ios-simulator-control` skill (references/reference.md).

     expert-debugging-mindset.md:1
       > Incorporated from the `debug-like-expert` skill (references/debugging-mindset.md).

   This is the SAME pattern used by every bundled-content skill in this
   repo (mobile-validation-runner, root-cause-debugging): a one-line
   "Incorporated from `<donor-skill>` (references/<donor-relative-path>)"
   header that documents WHERE the content came from — a citation to the
   DONOR skill's own references/ directory, in the DONOR's namespace, not
   a citation into proofpunk's own doctrine tree. The donor skills
   (`xc-mcp`, `ios-simulator-control`, `debug-like-expert`) do not exist
   anywhere in this repo (confirmed: `git log --all --diff-filter=A` for
   paths matching any of the three donor skill names returns zero commits)
   — they were merged content, never siblings. The provenance path is
   therefore inherently unresolvable in THIS repo by design: it documents
   foreign provenance, not a local link.

2. The remaining 11 hits are `<required_reading>` blocks inside the
   xc-mcp-workflow-*.md files, e.g. xc-mcp-workflow-build-project.md:16-17:

     <required_reading>
     **Read these reference files NOW:**
     1. references/tool-reference.md
     2. references/progressive-disclosure.md
     </required_reading>

   These are INSTRUCTIONS TO THE READER inside vendored workflow content —
   they tell an agent reading the upstream xc-mcp tool "go read
   references/tool-reference.md" using the UPSTREAM PROJECT's OWN relative
   path convention (bare `references/X.md`, sibling to the workflow file,
   exactly matching how `xc-mcp.md`'s own `<reference_index>` describes its
   layout at lines 185-191: "All domain knowledge in `references/` (bundled
   here as `xc-mcp-*.md`)"). The prose is talking about the UPSTREAM tool's
   references/ directory as the upstream tool would have organized it, not
   about proofpunk's local `mobile-validation-runner/references/` bundle.
   The depth-normalization the installer performs (proofpunk-install.sh:297-298,
   the "bare-name inside references/" rewrite) is EXACTLY the mechanism that
   would make these resolve once bundled at install time under the OLD
   (already-suspect) install-time-repair flow — which is precisely the
   behavior this gate exists to stop trusting, because it repairs the
   SYMPTOM (an unresolvable path) without checking whether the citation was
   ever meant to resolve inside THIS repo tree in the first place.

3. Cross-check: `xc-mcp.md`'s own `<reference_index>` (lines 185-191) lists
   the SAME six names (tool-reference.md, operation-enums.md,
   accessibility-patterns.md, progressive-disclosure.md, plus two NOT
   bundled at all: optimal-login-flow.md, testing-patterns.md) as living in
   "references/" — i.e. the xc-mcp skill's own documentation of its own
   layout is the source these citations were copy-pasted from, unedited,
   during incorporation into mobile-validation-runner.

CONCLUSION
----------
Do not fix these 23 by bundling proofpunk-local content at those paths —
there is no proofpunk-local content to bundle; the paths refer to donor
files not present in this repo. Two legitimate remediation paths exist for
a future change (NOT performed by this script, which only reports):
  (a) rewrite the citations to plain prose ("see the upstream xc-mcp tool's
      own tool-reference.md") so they stop looking like resolvable local
      paths, or
  (b) leave them as-is and teach `verify-citations.py --explain-vendor`'s
      reasoning into a permanent allowlist/comment so future readers do not
      re-litigate this.
This script deliberately does NEITHER — it reports them as WARN (not
ERROR) precisely because misclassifying vendored provenance text as a
repo-breaking defect is the wrong failure mode for a gate meant to be
adopted without false alarms.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--root', default=None,
                     help='repo root (default: two dirs up from this script)')
    ap.add_argument('--strict', action='store_true',
                     help='also fail (exit 1) on any WARN, baseline included')
    ap.add_argument('--explain-vendor', action='store_true',
                     help='print the investigated vendored-xc-mcp verdict and exit 0 (no scan)')
    args = ap.parse_args(argv)

    if args.explain_vendor:
        print(VENDOR_VERDICT)
        return 0

    root = args.root or os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    )
    skills_root = os.path.join(root, 'plugins', 'proofpunk', 'skills')
    if not os.path.isdir(skills_root):
        print(f"verify-citations: no such skills root: {skills_root}", file=sys.stderr)
        return 2

    errors = []
    warns = []
    for path, lineno, cite, resolved in find_citations(skills_root):
        if resolved:
            continue
        rel = os.path.relpath(path, root).replace(os.sep, '/')
        if is_top_level_skill_md(path, skills_root):
            errors.append((rel, lineno, cite))
        else:
            warns.append((rel, lineno, cite))

    errors.sort()
    warns.sort()

    baseline_seen = [w for w in warns if w in KNOWN_WARN_BASELINE]
    new_warns = [w for w in warns if w not in KNOWN_WARN_BASELINE]
    fixed_baseline = sorted(KNOWN_WARN_BASELINE - set(warns))

    print(f"verify-citations: scanning {skills_root}")
    print()

    if errors:
        print(f"ERROR ({len(errors)}) — unresolved citation in a top-level SKILL.md:")
        for rel, lineno, cite in errors:
            print(f"  {rel}:{lineno} -> {cite}")
        print()
    else:
        print("ERROR (0) — no unresolved citations in any top-level SKILL.md")
        print()

    print(f"WARN ({len(warns)}) — unresolved citation inside a bundled references/ dir "
          f"[{len(baseline_seen)} baseline, {len(new_warns)} NEW]:")
    for rel, lineno, cite in warns:
        tag = "(baseline)" if (rel, lineno, cite) in KNOWN_WARN_BASELINE else "(NEW)"
        print(f"  {rel}:{lineno} -> {cite}  {tag}")
    if fixed_baseline:
        print(f"  ({len(fixed_baseline)} baseline entries no longer present — fixed since baseline was frozen):")
        for rel, lineno, cite in fixed_baseline:
            print(f"    {rel}:{lineno} -> {cite}")
    print()

    print(f"summary: {len(errors)} ERROR, {len(warns)} WARN "
          f"({len(baseline_seen)} baseline / {len(new_warns)} NEW), "
          f"known baseline size = {len(KNOWN_WARN_BASELINE)}")

    if new_warns:
        print(f"NOTE: {len(new_warns)} WARN(s) not in the frozen baseline of {len(KNOWN_WARN_BASELINE)} "
              f"— review and either fix them or update KNOWN_WARN_BASELINE in this script.")

    fail = bool(errors) or (args.strict and bool(warns))
    print()
    print("RESULT:", "FAIL" if fail else "PASS",
          "(--strict)" if args.strict else "(default: ERROR-only)")
    return 1 if fail else 0


if __name__ == '__main__':
    raise SystemExit(main())
