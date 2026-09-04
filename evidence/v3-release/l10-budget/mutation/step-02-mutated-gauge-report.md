# gauge-report — recomputed from sealed artifacts

Generated: 2026-09-04T14:40:14Z | Repo HEAD: `73e928ed8d3b62827018ab8ab2e470c5487d0e2d` (working tree dirty)

Every row is computed fresh by this script from files under
`evidence/v3-release/**` and the live skill tree. No number is copied
from prose. A row whose evidence path does not resolve to a real file
is reported UNVERIFIED, never PASS.

| # | Lane | Gauge (unit) | Baseline | Target | Measured | Status | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | L12 | Skills passing spec basics (name/desc/fields) (skills) | 18/18 | 18/18 | 17/18 | **UNMET** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 7 | L10 | Skills with description+when_to_use under Claude Code's 1,536-char per-skill listing cap (skills) | 18/18 (max 978/1536, implement) | 18/18 | 17/18 (max 1956/1536, visual-inspection) | **UNMET** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 9 | L10 | Aggregate description+when_to_use chars (listing-pressure trend, not a fixed budget) (chars) | 13,949 (description-budget-baseline.md) | UNMEASURED — real budget is skillListingBudgetFraction (~1% of context window); no fixed target exists in any sealed source | 15239 chars | **UNMEASURED** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 8 | L10 | Median skill body size (context-economy proxy) (bytes) | 6,266 | UNMEASURED (no target defined in sealed sources) | 6186 bytes | **UNMEASURED** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |
| 2 | L4 | stop-guard scout-substring false-PASS closed, mutation-proven (cases) | 47 -> 48 cases | mutation-proven (baseline=mutated+1, restored byte-identical to baseline) | baseline=48 mutated=47 restored=48 byte_identical=True | **PASS** | `evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring/VERDICT.md@sha256:43646ce82d6a4d2da30824812ac88cbf465833114b95167e2f70a6ccbb787aeb`<br>`evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring/step-00-root-cause.md@sha256:6aab30d9ceee57b61cd8ee4fa6b60ab3c5a61c67653fd2ce94273b65b53ed791`<br>`evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring/step-01-baseline-fix-present.log@sha256:e12a0e2d4cd0f0a4b1aa60289f9abae03c4306ad38da0ef77761d3b885907dff`<br>`evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring/step-02-mutated-fix-reverted.log@sha256:47ae31b428db297c08369770ce251a19b1c4d34ed0dd5f2d592134c55dd212a9`<br>`evidence/v3-release/l4-enforcement/run-20260904T043559-scout-substring/step-03-restored.log@sha256:e12a0e2d4cd0f0a4b1aa60289f9abae03c4306ad38da0ef77761d3b885907dff` |
| 3 | L1 | Unresolved repo-tree citations (name/desc/fields resolve relative to citing file) (citations) | 30 -> 29 (top-level: 1 -> 0) | 0 | 29 unresolved (top-level: 0) | **UNMET** | `evidence/v3-release/00-baseline/citation-integrity-finding.md@sha256:90969b64df5cc23d260e99b276822a09ff4e0123866730802d0004fa2ac04ec3` |
| 4 | L16 | Commands proven end-to-end at the real slash-command surface (commands) | 0/6 | 6/6 | 0/6 | **UNMET** | `evidence/v3-release/00-baseline/command-surface-map.md@sha256:9d76a58a16eb5246f48818666ba2b7d51a4242be64d8a824150d85636e0d3220` |
| 5 | L2/L3 | Release gates: all exit 0, exit codes captured separately from stdout (gates) | 4/4 rc=0 | 4/4 rc=0 (this is a sealed snapshot — re-run tools/*.sh/py to confirm current tree) | test-hooks.sh=0, test-installer.sh=0, dry-run-install.sh=0, verify-orchestration.py=0 | **PASS** | `evidence/v3-release/00-baseline/gates-20260904T051258/exit-codes.txt@sha256:c6db6b3274cf4ee0b9a51a2b043d8234fb53e8f4a5d837f005a9aa19abc4a947`<br>`evidence/v3-release/00-baseline/gates-20260904T051258/README.md@sha256:e09021a705dccd4e4e03a73d8a054d72cdaa92c132bab404c0bfdf19c64a1c68`<br>`evidence/v3-release/00-baseline/gates-20260904T051258/test-hooks.sh.log@sha256:563d8e2216ca7699b7021916e6ad8ddd98a050c96eb979e7f9dd8f462da4f8e6`<br>`evidence/v3-release/00-baseline/gates-20260904T051258/test-installer.sh.log@sha256:fac80dddb4814f0852bacac17baa97af6f776b7e78b73e6fab02102a19b981f7`<br>`evidence/v3-release/00-baseline/gates-20260904T051258/dry-run-install.sh.log@sha256:78770467d5cdbf18b7eebdf18803af3006ef12e16084beb65002c948470b6d68`<br>`evidence/v3-release/00-baseline/gates-20260904T051258/verify-orchestration.py.log@sha256:16188c448147dbfe97be37d50c88f76ccceeb5e7b1b8d01e7b5e32c205e3cbf3` |
| 6 | L14 | Skill count (ground truth, derived not restated) (skills) | 18 | 18 | 18 | **PASS** | `evidence/v3-release/00-baseline/description-budget-baseline.md@sha256:c6f61b7382ca8f1976782be7019ee536814f82e8bb091441984b72fa621bc8a1` |

## Detail

### Gauge #1 (L12) — Skills passing spec basics (name/desc/fields)
- Status: **UNMET**
- Measured: 17/18
- Detail: failing: ['visual-inspection']

### Gauge #7 (L10) — Skills with description+when_to_use under Claude Code's 1,536-char per-skill listing cap
- Status: **UNMET**
- Measured: 17/18 (max 1956/1536, visual-inspection)
- Detail: over the 1536-char per-skill cap: [('visual-inspection', 1956)]

### Gauge #9 (L10) — Aggregate description+when_to_use chars (listing-pressure trend, not a fixed budget)
- Status: **UNMEASURED**
- Measured: 15239 chars
- Detail: aggregate listing-pressure exposure, trend-tracking only — the real host budget is skillListingBudgetFraction (~1% of the model's context window by default, host/session-dependent per code.claude.com/docs/en/skills); no fixed numeric target exists in any sealed source, so none is invented here

### Gauge #8 (L10) — Median skill body size (context-economy proxy)
- Status: **UNMEASURED**
- Measured: 6186 bytes
- Detail: no numeric target defined in sealed sources — trend-tracking only, does not gate release

### Gauge #2 (L4) — stop-guard scout-substring false-PASS closed, mutation-proven
- Status: **PASS**
- Measured: baseline=48 mutated=47 restored=48 byte_identical=True
- Detail: mutation flips the gate red by name and restore is byte-identical

### Gauge #3 (L1) — Unresolved repo-tree citations (name/desc/fields resolve relative to citing file)
- Status: **UNMET**
- Measured: 29 unresolved (top-level: 0)
- Detail: unresolved: ['plugins/proofpunk/skills/mobile-validation-runner/references/simctl-command-reference.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-accessibility-patterns.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-caching-strategy.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-mcp-configuration.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-operation-enums.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-progressive-disclosure.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-tool-reference.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-app-deployment.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-build-project.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-configure-caching.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-debug-failures.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-fresh-install.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-run-tests.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-simulator-management.md', 'plugins/proofpunk/skills/mobile-validation-runner/references/xc-mcp-workflow-ui-automation.md', 'plugins/proofpunk/skills/root-cause-debugging/references/expert-debugging-mindset.md', 'plugins/proofpunk/skills/root-cause-debugging/references/expert-hypothesis-testing.md', 'plugins/proofpunk/skills/root-cause-debugging/references/expert-investigation-techniques.md', 'plugins/proofpunk/skills/root-cause-debugging/references/expert-verification-patterns.md', 'plugins/proofpunk/skills/root-cause-debugging/references/expert-when-to-research.md', 'plugins/proofpunk/skills/stack-testing/references/webapp-testing.md']

### Gauge #4 (L16) — Commands proven end-to-end at the real slash-command surface
- Status: **UNMET**
- Measured: 0/6
- Detail: no command has a single artifact proving slash-typed -> flag mapping -> real execution -> observed result

### Gauge #5 (L2/L3) — Release gates: all exit 0, exit codes captured separately from stdout
- Status: **PASS**
- Measured: test-hooks.sh=0, test-installer.sh=0, dry-run-install.sh=0, verify-orchestration.py=0
- Detail: all 4 gates rc=0, exit codes captured separately from stdout

### Gauge #6 (L14) — Skill count (ground truth, derived not restated)
- Status: **PASS**
- Measured: 18
- Detail: 18 skill directories with SKILL.md found under plugins/proofpunk/skills/

## Summary: 3/9 gauges PASS

- Gauge #1 (L12): **UNMET** — Skills passing spec basics (name/desc/fields)
- Gauge #7 (L10): **UNMET** — Skills with description+when_to_use under Claude Code's 1,536-char per-skill listing cap
- Gauge #9 (L10): **UNMEASURED** — Aggregate description+when_to_use chars (listing-pressure trend, not a fixed budget)
- Gauge #8 (L10): **UNMEASURED** — Median skill body size (context-economy proxy)
- Gauge #3 (L1): **UNMET** — Unresolved repo-tree citations (name/desc/fields resolve relative to citing file)
- Gauge #4 (L16): **UNMET** — Commands proven end-to-end at the real slash-command surface
