# L1 Citation Gate — Verdict

## Deliverable
`tools/verify-citations.py` — stdlib-only repo-tree citation gate for
`plugins/proofpunk/skills/**`.

## Why this gate exists (structural blindness of `--verify`)
`tools/proofpunk-install.sh` cannot see repo-level broken citations because
its install step:
- `:289-290` rewrites `../../references/X` -> `references/X` (depth
  collapse into the installed skill's own dir)
- `:297-298` further rewrites bare/`../`-prefixed names inside a skill's own
  `references/` dir down to bare sibling names
- `:316` bundles a shared reference into the skill if it matches
  `(references/)?<name>` **anywhere** in the installed tree — the
  `(references/)?` group is optional, so a citation that was broken in the
  *repo* gets silently repaired by bundling before `:653`'s verify pass ever
  runs.

The installed, repaired tree then verifies clean (`:664 bad = find_bad(dst)`
comes back empty) and prints a checkmark for a repo that has real broken
citations sitting in it. `verify-citations.py` does no rewriting and no
bundling — it resolves each citation literally, relative to the citing
file, against the actual repo tree, which is what a `git clone` + human
read would face.

## Result on current tree
- ERROR: **0** (no unresolved citation inside any top-level `SKILL.md`)
- WARN: **29** (all inside a skill's bundled `references/` dir), all 29
  matched against the frozen `KNOWN_WARN_BASELINE`, **0 NEW**
- Default mode: exit **0** (PASS) — evidence:
  `evidence/v3-release/l1-citations/01-baseline-default.log`
- `--strict` mode: exit **1** (FAIL, correctly fails on the 29 baseline
  WARNs) — evidence: `evidence/v3-release/l1-citations/02-baseline-strict.log`

## Mutation proof (all four arms captured to evidence/)
1. **SKILL.md break -> ERROR**: appended an unresolvable citation to
   `tui-testing/SKILL.md`. Gate reported `ERROR (1)` naming the exact
   file:line:citation and exited **1** in default mode (not just
   `--strict`).
   → `04-mutation-skillmd-broken.log`
2. **Restore -> green**: reverted the byte-for-byte backup. Gate returned
   to `ERROR (0)`, exit **0**, identical WARN set (29/29, 0 NEW).
   → `05-restored-default.log`
3. **Bundled-reference break -> WARN, not ERROR, in default mode**:
   appended an unresolvable citation to
   `prompt-forge/references/prompt-patterns.md`. Default mode stayed
   `PASS` (exit **0**) with the new citation reported as `WARN … (NEW)`
   distinguishable from the 29 baseline entries; `--strict` mode on the
   same mutated tree exited **1**.
   → `06-mutation-ref-warn-default.log`, `07-mutation-ref-warn-strict.log`
4. **Restore -> green again**: reverted the second backup. Both default
   and `--strict` runs returned to the exact 29/29-baseline/0-NEW state
   (default PASS/exit 0, `--strict` FAIL/exit 1 on the known baseline as
   expected).
   → `08-restored-final-default.log`, `09-restored-final-strict.log`

`git status --porcelain` on both mutated files after restore shows no
diff introduced by the mutation round-trip (the one file with a
pre-existing diff, `tui-testing/SKILL.md`, carries only the dirty-tree
change that predates this task — the `references/cli-validation.md` ->
`../../references/cli-validation.md` fix noted in the assignment context
— confirmed unaffected because the restore was a byte-for-byte copy from
a backup taken before mutation).

**Conclusion: the gate is NOT structurally blind.** It goes red on both
severity classes when the underlying condition it claims to catch is
introduced, and returns to the identical clean state when reverted.

## Vendored xc-mcp investigation (item 3 — investigate, do not fix)
Full reasoning and evidence: run
`python3 tools/verify-citations.py --explain-vendor`
(captured at `evidence/v3-release/l1-citations/03-explain-vendor.log`).

**Verdict: the 23 `xc-mcp-*.md` warns (plus 6 more of the same shape in
`simctl-command-reference.md` and `root-cause-debugging/references/expert-*.md`
— 29 total) are vendored pass-through citations to a FOREIGN upstream
project's own internal layout, not broken proofpunk doctrine links.**

Evidence:
1. **Provenance headers** — 12 of the 29 warns are line-1
   `> Incorporated from the \`<donor-skill>\` (references/<donor-path>).`
   attribution lines (e.g. `xc-mcp-tool-reference.md:1`,
   `simctl-command-reference.md:1`, and the five
   `root-cause-debugging/references/expert-*.md:1` files). This is the
   repo's standard "merged content" attribution pattern. The three donor
   skills named (`xc-mcp`, `ios-simulator-control`, `debug-like-expert`)
   do not exist anywhere in this repo's git history
   (`git log --all --diff-filter=A` for paths matching any of the three
   names returns zero commits) — they were merged once, never kept as
   siblings, so their own `references/` path is unresolvable in this repo
   *by design*, not by accident.
2. **`<required_reading>` instructional citations** — the remaining 17
   (all 17 non-header warns are inside `xc-mcp-workflow-*.md` files' own
   `<required_reading>` blocks, e.g.
   `xc-mcp-workflow-build-project.md:16-17`) are instructions written FOR
   the upstream xc-mcp tool's own reader, using the upstream tool's own
   relative-path convention (bare `references/X.md`, sibling to the
   workflow file) — the same convention `xc-mcp.md`'s own
   `<reference_index>` (lines 185-191) documents for its own layout. These
   are talking about the upstream project's directory, not proofpunk's.
3. Rewriting these citations to resolve locally (e.g. by bundling a
   proofpunk-authored `tool-reference.md` at that path) would not fix a
   broken link — it would silently swap the upstream tool's real
   documentation for unrelated proofpunk content, corrupting correct
   vendored material.

**Recommendation (not performed by this script): do not "fix" these 29 by
bundling.** Either rewrite to non-path-shaped prose in a future change, or
leave as-is and treat this VERDICT as the permanent record for why they
are WARN, not ERROR, and why `--strict` is opt-in rather than the default.
