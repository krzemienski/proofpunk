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

SEVERITY MODEL (derived — no frozen count)
------------------------------------------
Classification is computed per citation from two observables, never from a
hand-maintained baseline of N tuples:

1. **Provenance header.** A citing file is VENDORED iff its first non-empty
   line matches `> Incorporated from the \`<donor>\` skill ...`. That is the
   repo's standard merged-content attribution. The donor skill is a foreign
   namespace; its `references/` layout is not this repo's doctrine tree.
2. **Shared-doctrine basename.** `plugins/proofpunk/references/*.md` is the
   live set of proofpunk doctrine files. An unresolved citation whose
   basename is in that set is a broken doctrine link even if the citing
   file is vendored (a foreign file that was later patched to point at
   proofpunk doctrine must use a resolvable relative path).

- ERROR: unresolved citation in a top-level SKILL.md, OR unresolved
  citation whose basename is shared doctrine, OR unresolved citation in a
  file that is NOT vendored. Adding a genuinely broken doctrine link goes
  ERROR without anyone updating a constant.
- WARN:  unresolved citation in a vendored file whose basename is NOT
  shared doctrine. These are pass-through citations to a FOREIGN upstream
  layout. See `--explain-vendor`. Adding another vendored-shaped citation
  in a vendored file stays WARN.

There is no `KNOWN_WARN_BASELINE` and no "known baseline size = N". The
WARN count is whatever the current tree's vendored files actually cite.

EXIT CODE CONTRACT
-------------------
- Default:  exit 1 iff ERROR count > 0. WARN count NEVER affects the
  default exit code — vendored foreign layout is not a repo-breaking
  defect.
- --strict: exit 1 iff (ERROR count > 0) OR (WARN count > 0). Use this to
  notice vendored-warn growth, not as the adoptable default.

USAGE
-----
    tools/verify-citations.py                 # default: fail only on ERROR
    tools/verify-citations.py --strict         # fail on ERROR or any WARN
    tools/verify-citations.py --explain-vendor # print the vendored verdict, no scan
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

# Line-1 (or first non-empty line) provenance header used by every merged
# bundled-content skill in this repo. Matches both the strict form
#   > Incorporated from the `xc-mcp` skill (references/tool-reference.md).
# and the Adaptation-suffixed form
#   > Incorporated from the `trace` skill (skills-ref.zip). **Adaptation:** ...
PROVENANCE_RE = re.compile(
    r'^>\s*Incorporated from the `([^`]+)` skill\b'
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


def first_nonempty_line(path: str) -> str:
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    return stripped
    except (OSError, UnicodeDecodeError):
        return ''
    return ''


def file_is_vendored(path: str) -> bool:
    """True iff the file opens with the repo's merged-content provenance
    header. Derived from the file itself — not from a path glob, skill
    name, or frozen tuple list."""
    return bool(PROVENANCE_RE.match(first_nonempty_line(path)))


def shared_doctrine_basenames(root: str) -> frozenset:
    """Live set of proofpunk shared-doctrine filenames. Adding a file under
    plugins/proofpunk/references/ automatically expands this set; there is
    no parallel constant to update."""
    refs_dir = os.path.join(root, 'plugins', 'proofpunk', 'references')
    names = set()
    if os.path.isdir(refs_dir):
        for fn in os.listdir(refs_dir):
            if fn.endswith('.md') and os.path.isfile(os.path.join(refs_dir, fn)):
                names.add(fn)
    return frozenset(names)


def classify_unresolved(path: str, cite: str, skills_root: str,
                        doctrine_names: frozenset) -> str:
    """Return 'error' or 'warn' for an unresolved citation.

    ERROR when a repo reader would be looking for proofpunk doctrine and
    not find it. WARN when the path is a foreign donor layout documented
    by a provenance header.
    """
    if is_top_level_skill_md(path, skills_root):
        return 'error'
    basename = os.path.basename(cite)
    if basename in doctrine_names:
        return 'error'
    if file_is_vendored(path):
        return 'warn'
    return 'error'


VENDOR_VERDICT = """\
VENDORED-VS-BROKEN VERDICT: plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-*.md
======================================================================================================

CLAIM: the unresolved citations in xc-mcp-*.md files (and the same shape in
simctl-command-reference.md and root-cause-debugging/references/expert-*.md)
are broken PROOFPUNK doctrine citations that should be fixed by bundling
more files.

FINDING: FALSE for foreign-layout citations. They are vendored pass-through
content citing a FOREIGN upstream project's OWN internal directory layout.
Rewriting or "fixing" them by bundling proofpunk-local files at those paths
would CORRUPT correct vendored content, not repair it.

The ONE exception on the tree this gate was rewritten against: a vendored
file that cites a SHARED DOCTRINE basename (`web-validation.md`) is a real
broken doctrine link and is classified ERROR until the relative path is
fixed to the repo's deliberate layout (`../../../references/X` from a
bundled references/ file; `../../references/X` from a SKILL.md). That
classification is DERIVED from the live `plugins/proofpunk/references/`
directory listing, not from a frozen tuple.

EVIDENCE
--------
1. Provenance headers. Every vendored bundled-content file opens with an
   explicit machine-readable attribution line, e.g.:

     xc-mcp-tool-reference.md:1
       > Incorporated from the `xc-mcp` skill (references/tool-reference.md).

     simctl-command-reference.md:1
       > Incorporated from the `ios-simulator-control` skill (references/reference.md).

     expert-debugging-mindset.md:1
       > Incorporated from the `debug-like-expert` skill (references/debugging-mindset.md).

   This is the SAME pattern used by every bundled-content skill in this
   repo: a one-line
   "Incorporated from `<donor-skill>` (references/<donor-relative-path>)"
   header that documents WHERE the content came from — a citation to the
   DONOR skill's own references/ directory, in the DONOR's namespace, not
   a citation into proofpunk's own doctrine tree. The donor skills
   (`xc-mcp`, `ios-simulator-control`, `debug-like-expert`) do not exist
   as sibling skill directories in this repo — they were merged content,
   never siblings. The provenance path is therefore inherently
   unresolvable in THIS repo by design: it documents foreign provenance,
   not a local link.

2. The remaining non-header hits inside xc-mcp-workflow-*.md files are
   `<required_reading>` blocks, e.g. xc-mcp-workflow-build-project.md:16-17:

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
   layout). The prose is talking about the UPSTREAM tool's references/
   directory as the upstream tool would have organized it, not about
   proofpunk's local `mobile-validation-runner/references/` bundle.

3. Cross-check: `xc-mcp.md`'s own `<reference_index>` lists the SAME names
   (tool-reference.md, operation-enums.md, accessibility-patterns.md,
   progressive-disclosure.md) as living in "references/" — i.e. the xc-mcp
   skill's own documentation of its own layout is the source these
   citations were copy-pasted from, unedited, during incorporation.

HOW THE GATE DISTINGUISHES THIS WITHOUT A FROZEN COUNT
------------------------------------------------------
`file_is_vendored(path)` is true iff the citing file's first non-empty line
matches PROVENANCE_RE. `shared_doctrine_basenames(root)` is the live glob
of `plugins/proofpunk/references/*.md`. An unresolved citation is WARN iff
the file is vendored AND the basename is not shared doctrine; otherwise it
is ERROR. Adding a new vendored file with foreign `references/foo.md`
citations does not require editing this script. Adding a broken citation
to a proofpunk-authored file, or pointing at a real doctrine basename with
the wrong relative path, goes ERROR.

Do not fix the foreign-layout citations by bundling proofpunk-local
content at those paths — there is no proofpunk-local content to bundle.
Two legitimate remediation paths exist for a future change (NOT performed
by this script, which only reports WARNs):
  (a) rewrite the citations to plain prose ("see the upstream xc-mcp
      tool's own tool-reference.md") so they stop looking like resolvable
      local paths, or
  (b) leave them as-is; the derived classifier already treats them as WARN.
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--root', default=None,
                     help='repo root (default: two dirs up from this script)')
    ap.add_argument('--strict', action='store_true',
                     help='also fail (exit 1) on any WARN, vendored included')
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

    doctrine_names = shared_doctrine_basenames(root)

    errors = []
    warns = []
    for path, lineno, cite, resolved in find_citations(skills_root):
        if resolved:
            continue
        rel = os.path.relpath(path, root).replace(os.sep, '/')
        kind = classify_unresolved(path, cite, skills_root, doctrine_names)
        row = (rel, lineno, cite)
        if kind == 'error':
            errors.append(row)
        else:
            warns.append(row)

    # The shared-doctrine tree itself. Previously unscanned, which is how a
    # real break (run-trace-schema.md citing `references/severity-model.md`
    # from INSIDE references/, resolving to references/references/) stayed
    # invisible here while failing 7 assertions in tools/test-installer.sh.
    # A doctrine file has no foreign-donor namespace, so any unresolved
    # citation in this tree is ERROR — there is no vendored WARN case.
    doctrine_root = os.path.join(root, 'plugins', 'proofpunk', 'references')
    if os.path.isdir(doctrine_root):
        for path, lineno, cite, resolved in find_citations(doctrine_root):
            if resolved:
                continue
            rel = os.path.relpath(path, root).replace(os.sep, '/')
            errors.append((rel, lineno, cite))

    errors.sort()
    warns.sort()

    print(f"verify-citations: scanning {skills_root}")
    print(f"shared doctrine set ({len(doctrine_names)}): "
          f"{', '.join(sorted(doctrine_names))}")
    print()

    if errors:
        print(f"ERROR ({len(errors)}) — unresolved doctrine citation or SKILL.md citation:")
        for rel, lineno, cite in errors:
            print(f"  {rel}:{lineno} -> {cite}")
        print()
    else:
        print("ERROR (0) — no unresolved doctrine citations, no unresolved SKILL.md citations")
        print()

    print(f"WARN ({len(warns)}) — unresolved foreign-layout citation in a vendored file:")
    for rel, lineno, cite in warns:
        print(f"  {rel}:{lineno} -> {cite}  (vendored)")
    print()

    print(f"summary: {len(errors)} ERROR, {len(warns)} WARN "
          f"(WARN count is derived, not a frozen baseline)")

    fail = bool(errors) or (args.strict and bool(warns))
    print()
    print("RESULT:", "FAIL" if fail else "PASS",
          "(--strict)" if args.strict else "(default: ERROR-only)")
    return 1 if fail else 0


if __name__ == '__main__':
    raise SystemExit(main())
