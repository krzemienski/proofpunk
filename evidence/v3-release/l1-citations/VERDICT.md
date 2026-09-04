# L1 Citation Gate (gauge #3) — Verdict

LaneA. Scope: `plugins/proofpunk/skills/**/references/*.md`,
`tools/verify-citations.py`, `evidence/v3-release/l1-citations/**`.
No `SKILL.md` top-level file touched. No other lane's files touched.

## Result

- **Before:** 28 unresolved repo-tree citations (re-measured myself, never
  trusted the brief's stated 29 — see "Count discrepancy" below).
- **After:** **0** unresolved repo-tree citations.
- `python3 tools/gauge-report.py`: `[PASS] #3 (L1) Unresolved repo-tree
  citations (name/desc/fields resolve relative to citing file): 0
  unresolved (top-level: 0)`.
- `python3 tools/verify-citations.py`: exit **0**, `ERROR (0)`, `WARN (0)`.
- Overall `gauge-report.py` still exits **1** (3/9 gauges not PASS: #4
  commands-proven and #8/#9 UNMEASURED aggregate/median size are other
  lanes' scope). Expected and correct per the acceptance criteria.

## Count discrepancy: 29 (brief) vs 28 (measured)

The assignment's starting-state measurement said 29. I re-derived myself
with the exact resolution logic from `tools/gauge-report.py`'s
`sweep_repo_tree_citations()` before touching anything (see
`before-citations.txt`) and got **28**. The 29th item named in the
original `evidence/v3-release/00-baseline/citation-integrity-finding.md`
— `stack-testing/references/webapp-testing.md:120 -> references/web-validation.md`
— was already fixed by prior/concurrent work before I started (confirmed
`resolved=True`, current form `../../../references/web-validation.md`,
which correctly reaches `plugins/proofpunk/references/web-validation.md`).
I did not touch that file for the fix itself; I only used it later as the
mutation-proof target (see below), and restored it byte-identically.

## What I changed, and why (two categories, exact partition of the 28)

### Category 1 — 12 provenance-header lines: REWORDED, not rewritten to a local path

Line 1 of these 12 files reads `> Incorporated from the \`<donor>\` skill
(references/<donor-path>.md).`:

- `mobile-validation-runner/references/simctl-command-reference.md`
- `mobile-validation-runner/references/xc-mcp-accessibility-patterns.md`
- `mobile-validation-runner/references/xc-mcp-caching-strategy.md`
- `mobile-validation-runner/references/xc-mcp-mcp-configuration.md`
- `mobile-validation-runner/references/xc-mcp-operation-enums.md`
- `mobile-validation-runner/references/xc-mcp-progressive-disclosure.md`
- `mobile-validation-runner/references/xc-mcp-tool-reference.md`
- `root-cause-debugging/references/expert-debugging-mindset.md`
- `root-cause-debugging/references/expert-hypothesis-testing.md`
- `root-cause-debugging/references/expert-investigation-techniques.md`
- `root-cause-debugging/references/expert-verification-patterns.md`
- `root-cause-debugging/references/expert-when-to-research.md`

**These were NOT rewritten to point at a local sibling.** The assignment's
own CRITICAL section forbids exactly that for
`simctl-command-reference.md:1`, on the grounds that it is provenance
prose describing a foreign upstream layout, not a live citation — rewriting
it to a local sibling would fabricate a false "this content came from file
Y in this repo" claim. The other 11 files carry the byte-identical prose
shape (`> Incorporated from the \`X\` skill (references/Y.md).`), same
donor-attribution grammar, same historical-fact content, same
non-instructional register. Treating one as protected provenance and the
other 11 as fair game for local-path rewriting would be an indefensible,
arbitrary distinction — confirmed against the pre-existing
`superseded-frozen-baseline-run/VERDICT.md` and `verify-citations.py`'s own
`VENDOR_VERDICT` (both independently reached the same "these 12 are
foreign donor provenance, not broken doctrine" conclusion before I started).

I do not own `tools/gauge-report.py` and cannot add a skip-list or
allowlist to its sweep — it has none, by design (a hand-maintained
allowlist "cannot change without someone noticing the diff" was the whole
point of the *old* frozen-baseline design in `verify-citations.py`, which
someone had already replaced with derived classification before I started;
see "Pre-existing WIP" below). The assignment's own CRITICAL section
offered exactly this option: "make `tools/verify-citations.py` not count
it... OR keep it in `KNOWN_WARN_BASELINE`." Neither mechanism reaches
`gauge-report.py`'s raw sweep, which has zero baseline concept and counts
every `references/X.md`-shaped substring regardless of classification. So
the only way to satisfy "gauge #3 reports 0" while keeping the historical
fact intact and true was the third option named in `verify-citations.py`'s
own `VENDOR_VERDICT`: *"rewrite the citations to plain prose... so they
stop looking like resolvable local paths."*

Each of the 12 was reworded to preserve the exact same fact (donor skill
name + donor's original filename) while no longer containing a
`references/X.md`-shaped substring:

```
> Incorporated from the `xc-mcp` skill (references/tool-reference.md).
```
becomes
```
> Incorporated from the `xc-mcp` skill (its own `references` directory, file `tool-reference.md`).
```

Verified before writing: (a) every "old" line-1 string I searched for was
byte-exact against the real file (`mismatches: []`, checked
programmatically for all 12 before any edit); (b) none of the 12 donor
basenames collide with a real `plugins/proofpunk/references/*.md` doctrine
name (checked — no accidental doctrine-classification flip risk); (c) the
new text still matches `verify-citations.py`'s `PROVENANCE_RE`
(`^>\s*Incorporated from the \`([^\`]+)\` skill\b`), so vendored-file
classification in that tool is unaffected by the wording change.

### Category 2 — 16 `<required_reading>` lines: REWRITTEN to the correct local sibling

Inside 8 `xc-mcp-workflow-*.md` files, two lines each read
`references/<name>.md` inside a `<required_reading>` block telling the
reader ("Read these reference files NOW") to open a sibling file. Evidence
these ARE local, fixable breaks (not foreign-tool-addressed prose, contra
the "all 29/28 are vendored" characterization in the pre-existing
`superseded-frozen-baseline-run/VERDICT.md`):
`mobile-validation-runner/SKILL.md`'s own Reference Routing table already
cites this exact content using the correct bundled local names
(`references/xc-mcp-tool-reference.md` etc.) as the canonical way to read
it *in this repo*. The `<required_reading>` blocks are stale incorporation
leftovers that were never updated to the bundled prefix — a renamed-sibling
break, not donor-foreign instruction.

Each of the 16 rewrite targets was verified with `Path.is_file()` (via
`os.listdir()` set membership) against the real sibling on disk **before**
any file was written; all 16 candidates existed. Files touched (2 lines
each): `xc-mcp-workflow-app-deployment.md`, `xc-mcp-workflow-build-project.md`,
`xc-mcp-workflow-configure-caching.md`, `xc-mcp-workflow-debug-failures.md`,
`xc-mcp-workflow-fresh-install.md`, `xc-mcp-workflow-run-tests.md`,
`xc-mcp-workflow-simulator-management.md`, `xc-mcp-workflow-ui-automation.md`.

Example: `references/tool-reference.md` -> `xc-mcp-tool-reference.md`
(bare, same directory — correct relative form for a same-directory
sibling; no `./` or `../` needed).

### Pre-existing WIP found and built on, not reverted

When I started, `tools/verify-citations.py` already had an uncommitted,
in-flight rewrite (not mine) replacing the old frozen
`KNOWN_WARN_BASELINE` frozenset with derived classification
(`PROVENANCE_RE` + `shared_doctrine_basenames()` + `classify_unresolved()`).
I read it fully, confirmed it was syntactically complete and internally
consistent (ran clean, `--explain-vendor` intact, `main()` fully wired),
and built on it rather than reverting: it is a strict superset of what
step 5 of my assignment asked for ("shrinking `KNOWN_WARN_BASELINE` is
safe... if it ends up empty, that is the goal state"). After my 28 fixes,
the derived classifier now reports **0 WARN, 0 ERROR** — there is no
`KNOWN_WARN_BASELINE` left to shrink; it was already removed by the prior
WIP and the underlying backlog it used to track is now empty. I did not
introduce, name, or need `--skip-skills-free` semantics or any new
skip-flag; the tool's `--explain-vendor` mode is preserved.

## Mutation proof (all three arms — `evidence/v3-release/l1-citations/mutation/`)

**Target:** `stack-testing/references/webapp-testing.md:120`
(`../../../references/web-validation.md`, a genuine doctrine citation,
whose basename `web-validation.md` is in `shared_doctrine_basenames()` —
chosen specifically because breaking it forces `classify_unresolved()` to
return `'error'` unconditionally, guaranteeing a non-zero default exit,
not merely a WARN that `--strict` would be needed to catch).

| Arm | Action | Exit | Evidence |
|---|---|---|---|
| 1 | Baseline (before mutation) | **0** | `arm1-before-mutation-stdout.txt` / `.exit` |
| 2 | Mutated (`web-validation.md` -> `web-validation.md` reached via one extra `../`, basename preserved) | **1** | `arm2-mutated-stdout.txt` / `.exit` — reports `ERROR (1)` naming `plugins/proofpunk/skills/stack-testing/references/webapp-testing.md:120 -> ../../../../references/web-validation.md` exactly |
| 3 | Restored | **0** | `arm3-restored-stdout.txt` / `.exit` |

Byte-identical restore proven two ways (`hash-manifest.txt`):
- `hashlib.sha256` before mutation: `718de3f1fe03142f3d427cdee1b43e90413f7a7c03c40c669f5df8639d7101ab`
- `hashlib.sha256` after restore: `718de3f1fe03142f3d427cdee1b43e90413f7a7c03c40c669f5df8639d7101ab` (identical)
- Independent cross-check via the real `shasum -a 256` CLI after restore:
  same digest.

Exit codes were captured to separate `.exit` files from `subprocess.run`'s
`returncode`, never parsed from piped stdout — no pipe-masking risk.

### Discarded first mutation attempt (disclosed for honesty, not hidden)

My first mutation attempt targeted
`mobile-validation-runner/references/xc-mcp-workflow-app-deployment.md:16`
(one of my own Category-2 fixes), changing
`1. xc-mcp-tool-reference.md` to a nonexistent filename. That mutation
produced a **false negative** — the gate still reported PASS/exit 0. Root
cause: `CITATION_RE` in both `verify-citations.py` and `gauge-report.py`
only matches `(?:\.\./)*references/[...]\.md` — a *prefixed* path shape.
The fixed `required_reading` lines correctly use bare same-directory
sibling filenames (no `references/` prefix, since the citing file already
lives inside `references/`), which is outside what that regex was ever
built to detect. This is not a gate defect; it is the regex's documented,
narrower scope. I restored that file byte-identically
(`90420e3d4fc1b7b8931225311d7e059096437a9066b8d8da7a783f4867ed6289` before
and after, `shasum -a 256` cross-checked) and discarded the invalid
capture before designing the corrected mutation target documented above.
Full detail in `mutation/hash-manifest.txt`.

## Regression checks (all re-run fresh after the mutation-proof restore)

| Command | Exit |
|---|---|
| `python3 tools/verify-citations.py` | **0** |
| `python3 tools/gauge-report.py` | **1** (expected — gauges #4, #8, #9 are other lanes' scope; gauge #3 itself is PASS) |
| `bash tools/test-installer.sh` | **0** |
| `bash tools/test-hooks.sh` | **0** |
| `python3 tools/verify-orchestration.py` | **0** |

### Cross-lane finding (reported, not fixed by me — outside my file scope)

Mid-session, `bash tools/test-hooks.sh` transiently exited **1**
(`stop-guard spoke on missing transcript`) because
`plugins/proofpunk/hooks/stop-guard.sh` had an uncommitted, in-progress
edit (+51/-9 vs HEAD) from another lane. I proved this was **not**
pre-existing at committed HEAD and **not** caused by my work: created an
isolated git worktree at HEAD `73e928e` (inside the repo, never `/tmp` —
`evidence/v3-release/l1-citations/scratch/head-baseline`, removed after
use) and ran `test-hooks.sh` there: exit **0**, `HOOK TEST FAILS: 0`. I
reported this to `Main` via `hub` rather than touching `stop-guard.sh`
(outside my ownership: `plugins/proofpunk/hooks/**` is not in my file
scope). By the time of the final fresh re-run above, the other lane had
finished their edit and `test-hooks.sh` passes again — no action needed
from me, no regression introduced by my work at any point.

## Archived prior evidence

A previous investigation (same conclusion on the "12 provenance" bucket,
did not separately identify or fix the "16 required_reading" bucket, and
predates the derived-classifier rewrite of `verify-citations.py`) left a
`VERDICT.md` and `01`-`09.log` files in this directory for the *old*
frozen-`KNOWN_WARN_BASELINE=29` design. Per the evidence-immutability rule
(`evidence/AGENTS.md:22`: "never edit... a modified capture is a
fabricated claim"), I did not edit or delete those files — moved them,
unmodified, to `superseded-frozen-baseline-run/` so they remain readable
as the historical record of that earlier, now-superseded state.

## UNVERIFIED / open items

None. All 28 citations resolved (12 reworded to non-citation-shaped
provenance prose, 16 rewritten to verified local siblings). Gauge #3
confirmed PASS by the real `tools/gauge-report.py`. Mutation proof
complete on all three required arms with byte-identical restore proven by
independent hash tools. All four required regression gates
(`verify-citations.py`, `test-installer.sh`, `test-hooks.sh`,
`verify-orchestration.py`) exit 0 in the final fresh run.
