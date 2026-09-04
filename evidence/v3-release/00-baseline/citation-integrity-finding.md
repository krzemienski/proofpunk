# F-L1-1 — 30 unresolved repo-tree citations, invisible to the installer's own verify

Measured: 2026-09-04 (UTC) | Repo HEAD: `9963648` (working tree dirty)
Method: every `references/…md` and `../…/references/…md` citation inside
`plugins/proofpunk/skills/**` extracted by regex, then resolved with
`Path.is_file()` **relative to the citing file**. Not a grep count — each
citation was resolved as a real filesystem object. Independently re-derived
after a subagent lane reported 12 instances; the true count is higher.

## Result: 30 unresolved (file, citation) pairs

| Skill | Unresolved | Severity |
|---|---:|---|
| `mobile-validation-runner` | 23 | inside bundled `references/` |
| `root-cause-debugging` | 5 | inside bundled `references/` |
| `stack-testing` | 1 | inside bundled `references/` |
| **`tui-testing`** | **1** | **top-level `SKILL.md:13`** |

`tui-testing` is the severe one: it is the only skill whose **`SKILL.md`
itself** carries a citation that does not resolve. Every other break is one
level down, inside a bundled reference. A user reading the skill hits this
one directly.

```
plugins/proofpunk/skills/tui-testing/SKILL.md:13
  … or non-interactive CLIs (use `references/cli-validation.md`).
```

`tui-testing/` contains exactly one entry — `SKILL.md`. There is no
`references/` directory, so the citation cannot resolve. The correct repo
form is `../../references/cli-validation.md`, as used by sibling skills.

## Why every gate is green anyway — defect Class 1

Two-arm proof, run against a `mktemp -d` target, never the product tree:

| Arm | Command | Result |
|---|---|---|
| Repo | resolve `tui-testing/references/cli-validation.md` | **BROKEN** — file absent, dir absent |
| Installed | `proofpunk-install.sh --source-dir . --dir $TMP/skills --only tui-testing` | rc=0, `✓ tui-testing`, **"all skills pass"**, and `references/cli-validation.md` **is bundled and resolves** |

The installer *repairs the defect while installing it*, then verifies the
repaired output:

- `tools/proofpunk-install.sh:290` rewrites `../../references/` → `references/`
  so the installed skill is self-contained.
- `:298` strips the `references/` prefix inside bundled `references/` dirs.
- `:316` decides what to bundle with
  `(^|[^A-Za-z0-9._/-])(\./)*(\.\./)*(references/)?$name` — the prefix is
  **optional**, so a repo-broken `references/X` matches exactly as well as a
  correct `../../references/X` and gets bundled either way.
- `:653` then runs `--verify` against that rewritten, self-healed tree.

So the checkmark is truthful about the installed artifact and blind to the
source. Nothing in the repo asserts that a citation resolves *in the repo*.

This is the repo's own defect Class 1 (see
`docs/commit-archaeology.md`): a harness whose green state cannot fail for
the property a reader assumes it covers. Same shape as `dry-run-install.sh`
never invoking the installer (`5e5150b`).

## Consequence — binding on L1

1. Fix the 30 citations at source. `tui-testing/SKILL.md:13` is the only one
   that changes user-visible behavior today; the other 29 are latent, and
   become live the moment anyone reads the repo tree rather than an install.
2. Add a **repo-tree** citation gate — resolution relative to the citing
   file, run before any rewrite. The existing installed-tree check stays; it
   answers a different question and must not be conflated with this one.
3. Mutation-prove the new gate: break one citation, gate goes red naming it;
   restore, green byte-identically. Per Class 1's own detector, an unmutated
   gate is not yet trusted.

## Open / UNRESOLVED

- Whether any of the 29 bundled-reference breaks are *also* wrong in the
  installed tree is **not established here**. Arm 2 proved self-healing for
  `tui-testing` only; the other 29 were not individually installed and
  checked. Do not generalize the self-heal result without measuring it.
- `mobile-validation-runner`'s 23 breaks are concentrated in vendored
  `xc-mcp-*` files that cite a *foreign* upstream layout
  (`references/tool-reference.md` etc.). These may be intentional
  pass-through references to an external MCP server's own docs rather than
  proofpunk doctrine. Classify before fixing — mass-rewriting them could
  corrupt correct vendored content.
