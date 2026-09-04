# Phase 4 — Sequential reasoning gate (recorded)

Recorded: 2026-09-04 (UTC) | HEAD `9963648` (working tree dirty)

The chain the work order mandates: what the operator wanted → what the hosts
require → what exists today → therefore what must change, and in what order.

---

## Step 1 — What the operator actually wanted

From the primary dictation (`raw/round1-dictation.txt`, 1,106 chars, operator
typed/dictated — not an agent paraphrase):

1. Fully understand the commits and everything feeding the plugin.
2. The install script "isn't actually properly working correctly."
3. "One massive skill that basically **the head will link with everything
   else**" — the sentence carries its own gloss. A head that *links to* other
   things is a router. **D8 resolved: strengthen the router, never merge.**
   Corroborated by absence: zero merge requests across 34,674 OMP + 168
   Claude operator turns.
4. Documentation.
5. ≥10 major improvements with **measured** success.
6. "The two e prompt" → "another lane that needs to be fully verified."

Round 2 supersedes round 1 on *ordering only*: establish what things are
before changing them.

**Revision made at this step.** I initially treated the work order's stated
premise (HEAD `a41591a`, clean tree, "9 registrations") as ground truth. All
three are false today. Every downstream number is therefore derived from
measurement, and the premise is recorded as stale rather than silently
corrected — the work order is an input to verify, not an authority.

## Step 2 — What the hosts actually require

From `docs/skill-canon.md` (current vendor docs, 12 sources cited):

- All 7 event keys in `hooks.json` remain supported, `InstructionsLoaded` and
  `PostToolUseFailure` included.
- **`PostToolUse` cannot deny** — verbatim: "Shows stderr to Claude; the tool
  already ran." No matcher or flag overrides this.
- OpenCode silently ignores unrecognized frontmatter fields.
- `name` must match the parent directory; `description` ≤ 1024 chars.

**Consequence that constrains L5.** The Bash-write bypass cannot be closed at
`PostToolUse` — that layer is structurally incapable of denying. And it cannot
be closed by parsing shell at `PreToolUse`, because that path already falsely
blocked `cp -p`, `mv -f`, `touch -c`, `sed -i -e` and was reverted. Both
obvious closures are eliminated *before* any code is written. What remains is
central enforcement that never reads shell: content-addressed sealing where
the inventory is the authority and mutation is caught at validate time.

## Step 3 — What exists today

Measured, not recalled:

| Fact | Value | Source |
|---|---|---|
| Skills / references / commands | 18 / 13 / 6+6 | `d6-d7-measurement.md` |
| Hook events / registrations / scripts | 7 / **11** / 9 | verified from `hooks.json` |
| Gates green | 4/4 rc=0 | `00-baseline/gates-20260904T051258/` |
| Spec-basic conformance | 18/18 | `description-budget-baseline.md` |
| Descriptions vs listing budget | 13,949 vs 1,536 (**9.1×**) | same |
| Commands proven at slash surface | **0/6** | `command-surface-map.md` |
| Unresolved repo citations | 30 → **29** (top-level: 1 → 0) | `citation-integrity-finding.md` |

Two work-order claims were **refuted** by measurement, and neither should
generate work: the "9 registrations" figure (true: 11), and the supposed risk
that the head's folded description breaches 1024 (it is the *shortest*, 718).
An improvement program that "fixed" either would have been fixing nothing.

## Step 4 — Therefore: what must change, and in what order

The ordering is forced by dependency, not preference.

1. **Correctness of the instrument comes first.** Two false-PASS defects were
   already found *in the enforcement layer itself* — the stop-guard scout
   substring, and the installer's self-healing verify. While an instrument
   lies, every measurement taken with it is void. Both are closed and
   mutation-proven before any gauge is trusted.
2. **Substrate before enforcement.** L4 must query *facts* rather than infer
   from prose, so the trace (L2) and attestation (L3) must exist before the
   guard can consult them. Enforcement built on prose-matching is what
   produced the scout-substring bug in the first place.
3. **Derivation before documentation.** L15's generator must exist before L17
   rewrites docs, or the docs are hand-authored again and drift resumes on the
   next edit. This is defect Class 2, and writing prose first guarantees it.
4. **Gates must be mutation-proven or they are not gates.** This is the
   binding lesson of the whole record: `dry-run-install.sh` never invoked the
   installer; case 23 was renamed to avoid the very hazard it appeared to
   test. An unmutated green is an unmeasured green.

### Branch taken, and why

At Step 4 there were two real alternatives:

- **(a)** Ship the 10 orchestration upgrades in the v3 brief's numbered order.
- **(b)** Fix the instrument first, then ship upgrades against a trustworthy
  measurement surface.

**Chose (b).** Under (a), every gauge would be recorded through an enforcement
layer already proven to emit false PASSes — the numbers would be unfalsifiable
and the release report would restate them as measured fact. That is precisely
defect Class 4, which this repo has had to correct downward four times
(`d433519`, `f95ba9d`, `f8dccf8`, `3fd94ff`). The cost of (b) is that fewer
lanes land in a given run; the benefit is that what does land is measurable.

## Verification of this chain

Each step's conclusion is falsifiable and cites a measurement, not a memory:

- Step 1's D8 ruling would be falsified by any operator turn requesting a
  merge. None exists across 34,842 turns.
- Step 2's `PostToolUse` constraint would be falsified by a documented
  override. The vendor table states none.
- Step 3's counts would be falsified by re-running the derivations. They were
  re-run independently and agreed twice (mine and the canon lane's).
- Step 4's ordering would be falsified by finding a lane whose dependency
  actually runs the other way. None found; L4 genuinely requires L2/L3.

## Open at this gate

- **D1/D2** stand as agent interpretations, not evidence-resolved. L18 runs
  the standing fallback (`/proofpunk:forge-prompt` + `/proofpunk:rate-prompt`).
- **Lane B** stays BLOCKED on an exact operator token. Delegated judgment was
  attempted twice historically and retracted both times as fabricated
  authority; it is not attempted a third time.
- **`shellcheck` absent** on this host — L5's lint lane needs an install, a
  vendored copy, or a recorded exception. Not silently skipped.
