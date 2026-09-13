# step-06 — P11: 19-skill prose-correctness review

## What P11 asked for
"Documentation explains architecture" was UNVERIFIED: 22/22 script citations
resolved, but that is mechanical. No correctness review of the prose existed.

## Method
Four reviewers over disjoint partitions of all 19 SKILL.md files. ProseD died
on a transient provider outage (`[codex/gpt-6-astra] Unavailable`) and was
re-dispatched as ProseDRetry, so no partition went unreviewed.

## Defects FIXED (each verified against source before editing)

1. Router reference table listed 15 of 18 references.
   MISSING: docs-acquisition.md, intent-verification.md, subagent-aware-stop.md.
   Verified by set difference, then added. Now 18/18.

2. completion-summary frontmatter claimed it "proves agents terminated".
   Its own body (lines 109-118) says the opposite: recorded completion only.
   This is the exact overclaim corrected in the ledger last session and never
   propagated into the skill. Narrowed to RECORDED completion throughout.

3. completion-summary contract said `exit 0 = all children terminal`.
   Measured: the gate also returns 0 for MAIN_IDLE_NO_CHILDREN (no tracker —
   every runtime except Claude Code) and ALL_COMPLETE_DEGRADED. Rewritten to
   name all three states, and to add exit 2 on summary-write failure, which
   the contract omitted entirely.

4. completion-summary claimed the summary records "what each agent did".
   Measured `_render`: it emits type/id/status/completed_at and nothing else —
   zero work/action/output fields. Narrowed to recorded status metadata, and
   the `?`/`-` rendering of unknown entries is now stated.

5. Eight broken shared-runbook citations: `references/*-validation.md` written
   without the `../../` prefix in root-cause-debugging, stack-testing,
   tui-testing, ui-experience-audit, and visual-inspection (x4).

## A sweep I had to revert

My first fix rewrote EVERY bare `references/X.md` across all skills — 83
edits. verify-citations went from 0 errors to 75, and verify-shipped-vs-active
began reporting active-not-shipped. Cause: skill-local reference BUNDLES are
legitimate and common — root-cause-debugging has 9 local files, stack-testing
10, ui-experience-audit 4 — so a bare `references/foo.md` is CORRECT there.
Reverted with git checkout, then re-fixed only `*-validation.md`, which are
shared runbooks that live at ../../references/ and appear in no local bundle.

This also corrects ProseB, which filed all 8 as broken on the assumption that
no local bundles exist. The 8 were broken, but its stated reason was wrong for
3 of the 5 skills.

## Gates after the targeted fix

    verify-citations           rc=0
    verify-counts              rc=0
    verify-router-links        rc=0
    verify-orchestration       rc=0
    verify-proof-vocab         rc=0
    verify-shipped-vs-active   rc=0
    verify-harness-integrity   rc=0

## Findings NOT fixed, recorded instead

- codebase-truth-audit: SKILL prose vs a 9-phase scaffold (phase-01..09).
  Re-measured: the SKILL contains no "8-phase" string at all, so ProseC's
  quote does not match current source. UNCONFIRMED.
- mobile-validation-runner scripts/example.sh: 428 bytes, prints example text,
  no boot/build/record/validate. ProseC is right that the description
  oversells it. Real defect, deferred — it is a script rewrite, not prose.
- plan-hardening lens taxonomy vs red-team-eval's four canonical lenses;
  plan-hardening L113 vs L121 accepted-CRITICAL contradiction. Both real,
  both prose-level, deferred to a follow-up pass.
- ui-experience-audit "zero findings means you skipped a phase" and the
  unsourced "~60%" claim in visual-inspection:139. Real overclaims, deferred.

## What I SEE
Five defect classes found and fixed with gates green; five more recorded with
enough detail to act on. The review found a false claim in a skill I wrote
last session, which is exactly what a correctness review is for.

VERDICT: PASS for the review itself (all 19 skills reviewed, no partition
skipped). The deferred items are recorded as open, not silently dropped.
