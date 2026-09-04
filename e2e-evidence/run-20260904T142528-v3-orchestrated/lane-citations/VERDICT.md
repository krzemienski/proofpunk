# LaneCitations VERDICT — derived vendored classification

Script-level. Live-session UNVERIFIED (this lane does not drive sdk_probe).
Install-level UNVERIFIED (LaneInstaller owns the installer).

## What changed

| File | Change |
|---|---|
| `tools/verify-citations.py` | Deleted `KNOWN_WARN_BASELINE` (29-tuple frozen set) and the "known baseline size = N" summary. Classification is now derived: provenance-header detection + live glob of `plugins/proofpunk/references/*.md`. sha256=`d6ea7bf2299e036dce04022b5789277b327ddc416d51c5c3a8c8b48f144a3107` (15264 bytes). |
| `plugins/proofpunk/skills/stack-testing/references/webapp-testing.md:120` | Class (b) doctrine fix: `` `references/web-validation.md` `` → `` `../../../references/web-validation.md` ``. Deliberate layout (`CLAUDE.md:9-12`); not localized. sha256=`718de3f1fe03142f3d427cdee1b43e90413f7a7c03c40c669f5df8639d7101ab`. |

No other citation text rewritten. Prior lane's "do not mass-rewrite" recommendation is **honored for 28/29** and **overturned for 1/29 with evidence** (item 29's basename is live shared doctrine).

## What I drove

```
python3 tools/verify-citations.py                # rc=0  ERROR(0) WARN(28)
python3 tools/verify-citations.py --strict       # rc=1  (WARNs remain, expected)
python3 tools/verify-citations.py --explain-vendor  # rc=0
```

Unpiped; each run has a sibling `.rc` holding the bare exit code.

## Gauge #3 honest target (recommendation only — Lane E owns the gauge)

**Recommend: 0 ERROR with a DERIVED vendored classification. Do not target 0 unresolved-of-any-kind.**

Reasoning:

- `tools/gauge-report.py:396-411` currently live-sweeps every unresolved citation (vendored foreign layout included) and targets `0`. After this lane that sweep still measures **28 unresolved**, so gauge #3 stays UNMET until Lane E redefines the measured predicate. I did not edit `gauge-report.py`.
- Targeting 0-of-any-kind forces one of two defects this repo already burned on: (1) mass-rewriting foreign donor paths into proofpunk files (corrupting correct vendored content — prior L1 verdict), or (2) a frozen allowlist whose size is a hand-typed number (defect class #1, four prior regressions).
- Targeting 0 ERROR, with WARN = unresolved citation in a provenance-headered file whose basename is **not** in `plugins/proofpunk/references/`, is the classification this gate now computes. Adding a broken doctrine citation still goes ERROR without anyone bumping a constant. Adding a new vendored file with foreign `references/foo.md` stays WARN without anyone bumping a constant.

Suggested measured value for Lane E to wire, once it re-points evidence: `ERROR=0 WARN=28 (derived)`. Evidence for that number: `e2e-evidence/run-20260904T142528-v3-orchestrated/lane-citations/step-01-clean-default.log` sha256=`8103c5222fa9279ccee4aae47d095257cb50ff412577fee9c789c3c05b58ca41` rc=0 at `step-01-clean-default.rc`.

I did **not** silently redefine the gauge.

## Prior-verdict claim audit: "12 of 29 carry line-1 provenance headers"

**PASS — the claim is true, and slightly understated.** Re-derived from disk this session, not inherited.

- 12 of 29 unresolved citations **are themselves** the line-1 provenance header (items 01–07, 24–28 below). That is exactly the prior wording.
- The other 17 unresolved citations sit later in the same files; **every one of those 17 files also has a line-1 provenance header**. So 29/29 citing files are vendored; 12/29 citations are the header line.
- Donor skills `xc-mcp`, `ios-simulator-control`, `debug-like-expert`, `webapp-testing` do **not** exist as sibling skill directories. `git log --all --diff-filter=A` on those exact sibling paths returns empty. The names appear only as merged content (first landing: `16f8d19`).

## Per-item classification of the original 29

Legend: **(a)** genuine vendored foreign layout — do not rewrite. **(b)** broken proofpunk doctrine link — fix at source with `../../references/X` (or `../../../references/X` from a bundled `references/` file). **(c)** ambiguous.

Provenance regex used: first non-empty line matches `^>\s*Incorporated from the \`([^`]+)\` skill\b`. Shared-doctrine set (14, live glob): `api-validation.md, ci-gates.md, cli-validation.md, defect-pattern-database.md, end-user-actor.md, evidence-contract.md, ios-hig-checklist.md, ios-validation.md, platform-routing.md, preflight-checks.md, run-trace-schema.md, severity-model.md, web-validation.md, web-wcag-checklist.md`.

### mobile-validation-runner (23) — all (a)

| # | File:line | Citation | Line-1 provenance (donor) | Class | Evidence |
|---|---|---|---|---|---|
| 01 | `simctl-command-reference.md:1` | `references/reference.md` | `ios-simulator-control` (citation IS the header) | (a) | basename `reference.md` not in shared doctrine; donor not a sibling |
| 02 | `xc-mcp-accessibility-patterns.md:1` | `references/accessibility-patterns.md` | `xc-mcp` (header) | (a) | same |
| 03 | `xc-mcp-caching-strategy.md:1` | `references/caching-strategy.md` | `xc-mcp` (header) | (a) | same |
| 04 | `xc-mcp-mcp-configuration.md:1` | `references/mcp-configuration.md` | `xc-mcp` (header) | (a) | same |
| 05 | `xc-mcp-operation-enums.md:1` | `references/operation-enums.md` | `xc-mcp` (header) | (a) | same |
| 06 | `xc-mcp-progressive-disclosure.md:1` | `references/progressive-disclosure.md` | `xc-mcp` (header) | (a) | same |
| 07 | `xc-mcp-tool-reference.md:1` | `references/tool-reference.md` | `xc-mcp` (header) | (a) | same |
| 08 | `xc-mcp-workflow-app-deployment.md:16` | `references/tool-reference.md` | `xc-mcp` (`workflows/app-deployment.md`); citing line is `<required_reading>` item 1 | (a) | foreign workflow required-reading; basename not shared doctrine |
| 09 | `xc-mcp-workflow-app-deployment.md:17` | `references/operation-enums.md` | same file | (a) | same |
| 10 | `xc-mcp-workflow-build-project.md:16` | `references/tool-reference.md` | `xc-mcp` (`workflows/build-project.md`) | (a) | same |
| 11 | `xc-mcp-workflow-build-project.md:17` | `references/progressive-disclosure.md` | same file | (a) | same |
| 12 | `xc-mcp-workflow-configure-caching.md:16` | `references/caching-strategy.md` | `xc-mcp` (`workflows/configure-caching.md`) | (a) | same |
| 13 | `xc-mcp-workflow-configure-caching.md:17` | `references/tool-reference.md` | same file | (a) | same |
| 14 | `xc-mcp-workflow-debug-failures.md:17` | `references/progressive-disclosure.md` | `xc-mcp` (`workflows/debug-failures.md`) | (a) | same |
| 15 | `xc-mcp-workflow-debug-failures.md:18` | `references/tool-reference.md` | same file | (a) | same |
| 16 | `xc-mcp-workflow-fresh-install.md:13` | `references/tool-reference.md` | `xc-mcp` (`workflows/fresh-install.md`) | (a) | same |
| 17 | `xc-mcp-workflow-fresh-install.md:14` | `references/operation-enums.md` | same file | (a) | same |
| 18 | `xc-mcp-workflow-run-tests.md:16` | `references/tool-reference.md` | `xc-mcp` (`workflows/run-tests.md`) | (a) | same |
| 19 | `xc-mcp-workflow-run-tests.md:17` | `references/progressive-disclosure.md` | same file | (a) | same |
| 20 | `xc-mcp-workflow-simulator-management.md:17` | `references/tool-reference.md` | `xc-mcp` (`workflows/simulator-management.md`) | (a) | same |
| 21 | `xc-mcp-workflow-simulator-management.md:18` | `references/operation-enums.md` | same file | (a) | same |
| 22 | `xc-mcp-workflow-ui-automation.md:16` | `references/accessibility-patterns.md` | `xc-mcp` (`workflows/ui-automation.md`) | (a) | same |
| 23 | `xc-mcp-workflow-ui-automation.md:17` | `references/tool-reference.md` | same file | (a) | same |

### root-cause-debugging (5) — all (a)

| # | File:line | Citation | Line-1 provenance (donor) | Class | Evidence |
|---|---|---|---|---|---|
| 24 | `expert-debugging-mindset.md:1` | `references/debugging-mindset.md` | `debug-like-expert` (header) | (a) | basename not shared doctrine; donor not a sibling |
| 25 | `expert-hypothesis-testing.md:1` | `references/hypothesis-testing.md` | `debug-like-expert` (header) | (a) | same |
| 26 | `expert-investigation-techniques.md:1` | `references/investigation-techniques.md` | `debug-like-expert` (header) | (a) | same |
| 27 | `expert-verification-patterns.md:1` | `references/verification-patterns.md` | `debug-like-expert` (header) | (a) | same |
| 28 | `expert-when-to-research.md:1` | `references/when-to-research.md` | `debug-like-expert` (header) | (a) | same |

### stack-testing (1) — (b), fixed

| # | File:line | Citation | Line-1 provenance (donor) | Class | Evidence |
|---|---|---|---|---|---|
| 29 | `webapp-testing.md:120` | was `references/web-validation.md` | `webapp-testing` (`skills-ref.zip`) — header is real, **citation is not the header** | **(b)** | basename `web-validation.md` **is** in `plugins/proofpunk/references/` (live glob). Sibling skills cite it as `../../references/web-validation.md` from SKILL.md (`proofpunk/SKILL.md:90`). From a bundled `references/` file the matching layout is `../../../references/web-validation.md` (same shape as `validation-plan/references/task-file-format.md:60`). This is a proofpunk doctrine patch applied *into* vendored prose, not a donor-layout path. Left as `references/web-validation.md` it cannot resolve in the repo tree and the installer would silently bundle it — the exact Class-1 blindness this gate exists to catch. |

**Counts: (a)=28, (b)=1, (c)=0.** After the (b) fix, clean-tree gate: ERROR=0, WARN=28.

## Derived classifier (replaces the frozen 29)

```
ERROR if:
  - citing file is a top-level SKILL.md, OR
  - citation basename ∈ live glob plugins/proofpunk/references/*.md, OR
  - citing file's first non-empty line does NOT match PROVENANCE_RE
WARN if:
  - citing file is provenance-headered AND basename is not shared doctrine
```

No `frozenset` of (path, line, cite) tuples. No "known baseline size = 29". The WARN count is whatever vendored files currently cite.

## Mutation proof (three arms, separate `.rc`)

Mutations applied to owned files only (`stack-testing/references/playwright-api-reference.md` has no provenance header; `mobile-validation-runner/references/xc-mcp-tool-reference.md` has one). Restores were `shutil.copy2` from pre-mutation backups; sha256 matched.

| Arm | What | Gate | Evidence |
|---|---|---|---|
| i | Appended `` `references/evidence-contract.md` `` to non-vendored `playwright-api-reference.md` | **ERROR**, names `playwright-api-reference.md:655 -> references/evidence-contract.md`, default rc=**1** | `step-02-mutation-broken-doctrine.log` sha256=`1e2ee769bece84304841a9778a152df8d7f7ba8540d31b87cc460d3ce12a8cb0` / `.rc` = `1` |
| ii | Appended `` `references/foreign-vendor-layout.md` `` to vendored `xc-mcp-tool-reference.md` | default **PASS** rc=**0**, WARN 28→**29**, names the new cite as `(vendored)` not ERROR; `--strict` rc=**1** | `step-03-mutation-vendored-warn.log` sha256=`1991d83574eb8fcc1514ef577f1d76c9c5064e7bff3354838e0cd397a11608e4` / `.rc` = `0`; `step-04-mutation-vendored-warn-strict.log` sha256=`bcc9e364290db6008da0634eedb07fdd3a1c56f3911e7242f120f9db973b9d40` / `.rc` = `1` |
| iii | Restore both files byte-identical | ERROR(0) WARN(28) rc=**0**, identical to clean baseline (sha256 of step-05 log == step-01 log = `8103c5222fa9279ccee4aae47d095257cb50ff412577fee9c789c3c05b58ca41`) | `step-05-restored-clean.log` / `.rc` = `0`. Restore sha256: playwright=`269d89b1e519666be2f15587f77c2b7796f5a57c2a1bac7a712adf4a882ac456`, xc-mcp-tool-reference=`3feb83bf66c7cd7a7f8f2a5418aa88db453e7a6518d8fda54f962a7a3202aae0` |

Clean `--strict` still exits 1 because 28 vendored WARNs remain: `step-06-clean-strict.rc` = `1`. That is the contract, not a regression.

## Claims

| Claim | Verdict | Proof level | Citation |
|---|---|---|---|
| `python3 tools/verify-citations.py` exits 0 on the clean tree | **PASS** | script-level | `.../lane-citations/step-01-clean-default.rc` contains `0` |
| No hardcoded baseline count remaining (`KNOWN_WARN_BASELINE =` absent; no 29-tuple frozenset) | **PASS** | script-level | `tools/verify-citations.py` — AST walk of assignments has no `KNOWN_WARN_BASELINE`; grep `KNOWN_WARN_BASELINE\s*=` is empty. Docstring *mentions* the removed name once to say it is gone. |
| All 29 classified individually | **PASS** | script-level | this file, tables above |
| Three mutation arms distinguish broken-doctrine ERROR from vendored WARN | **PASS** | script-level | step-02 / step-03 / step-05 + sibling `.rc` |
| Item 29 doctrine path uses the repo layout, not a localized copy | **PASS** | script-level | `webapp-testing.md:120` cites `../../../references/web-validation.md`; that path `Path.is_file()`-resolves to `plugins/proofpunk/references/web-validation.md` |
| Do-not-mass-rewrite honored | **PASS** | script-level | git-owned citation text in the 28 (a) files is untouched; only item 29 rewritten |
| Gauge #3 now PASS in `gauge-report.py` | **UNVERIFIED** / will stay **UNMET** | n/a | Lane E owns that file; its live sweep still counts 28 unresolved of any kind against target 0 |
| Installer still rewrites `../../../references/X` correctly for item 29 | **UNVERIFIED** | install-level | `proofpunk-install.sh:289` rewrites `../../../references/` → `../references/`; `:298` then strips to the bare name inside `references/`. Not driven this lane (LaneInstaller owns the installer). |
| End-user session sees the new classifier | **UNVERIFIED** | live-session | not driven |

## Open / UNRESOLVED

- Gauge #3 remains UNMET until Lane E changes its measured predicate from "0 unresolved of any kind" to "0 ERROR under the derived classifier". Recommendation is above; I did not edit the gauge.
- Install-time rewrite of the new `../../../references/web-validation.md` citation is reasoned from `proofpunk-install.sh:288-298` but not executed. LaneInstaller owns that surface.
- `--strict` still fails on the 28 vendored WARNs by design. If a future lane wants `--strict` green, the remediation is prose-rewriting foreign paths (prior verdict option a), not bundling.
- `PROVENANCE_RE` is first-non-empty-line only. A file that is vendored in substance but missing that header will classify its unresolved citations as ERROR. That is fail-closed and intended.
- Adaptation-suffixed headers (`> Incorporated from the \`trace\` skill (skills-ref.zip). **Adaptation:** ...`) match the prefix regex. None of those files currently carry unresolved citations.
