# D1, D2, D8 — Session-record findings

Measured 2026-09-02. **Supersedes** the provisional D1/D2 rulings in
`d1-d2-d4-d9-dictation.md`, which were reached from tree absence alone,
before the session stores were searched.

Confidence discipline used here: only text an **operator actually typed or
dictated** counts as primary evidence. Text authored by an assistant and then
delivered to a subagent in a `role=user` envelope is an **agent
interpretation**, not operator confirmation, and is labelled as such.

## Method — and the corrections it forced

Stores scanned, role-gated, injected content excluded:

| Store | Files w/ proofpunk | Operator turns | Verdict |
|---|---|---|---|
| `~/.claude/projects/*proofpunk*` | 97 | 168 | zero genuine hits |
| `~/.omp/agent/sessions/` | 445 | **34,674** | the real record |
| `~/.local/share/opencode/` | 0 | 0 | no proofpunk sessions |

**Correction 1 — role gating alone is insufficient.** The first Claude-store
scan returned 3 "user-role" D8 hits. All three were *skill-injection
payloads* — the `proofpunk` SKILL.md body inside a user envelope, opening
`Base directory for this skill:`. None were operator speech. Filters added
for `Base directory for this skill`, `system-reminder`, `</attachment>`,
`tool_use_id`, `## Run checklist`, `<command-name>`.

**Correction 2 — a masked failure produced an empty artifact.** An extraction
wrote `operator-dictations.txt` at **0 bytes**: Python raised `AttributeError`
on a string-typed `message` payload while a following command reset `$?` to
0. The zero-byte file was deleted, never cited; the re-run used
`set -o pipefail` with the interpreter rc captured separately (`PY_RC=0`,
1106 bytes). This is the repo's own piped-capture defect class reproducing
inside its own discovery work.

**Correction 3 — 768-char display truncation hid the answer.** The decisive
operator sentence sits at chars ~880-1000 of an 1106-char message. Every
in-session display stopped at "all the hooks, how they…". The text had to be
written to a file and printed from an offset to be read at all. That is why
D1 first resolved to a fallback.

**Correction 4 — a `role=user` envelope is not an operator turn.** The
strongest-looking D1/D2 evidence (below) is an assistant-authored task
assignment rendered into a subagent's transcript as `role=user`. It is
downgraded accordingly.

## Primary operator source

`~/.omp/agent/sessions/-proofpunk/2026-08-24T20-31-44-166Z_01a03578-cc26-708f-a910-87211fa560a1.jsonl:11`
Captured verbatim at
`evidence/v3-release/00-discovery/raw/round1-dictation.txt` (1106 chars):

> "So, currently, we need to do a lot of work on it, and we need to fully
> understand the commits and all the different things that go into this
> plugin, as well as just some of the skills, and improve it, and basically,
> it looks like the install script isn't actually properly working correctly,
> and so **you should only have one massive skill that basically the head will
> link with everything else up correctly**. … first gain your full
> understanding of **the food club**, after that, and improve it, and create
> the documentation, correctly install the script, and then explain it and
> actually think through at least 10 major improvements for all of the
> skills, all the hooks, **how they work together**, how, and then measure
> your actual success with such. **Also look for the two e prompt, and also
> that will lead to another lane that needs to be fully verified and
> validated** and always enforce the end-user testing accordingly.
> ultrathink orchestrate --auto --mine --parallel"

## D8 — "one massive skill" — RESOLVED from the operator's own words

**Verdict: strengthen and prove the existing `proofpunk` router head — not a
literal single-file merge.**

This is resolved directly from the dictation, with no agent interpretation in
the chain. The sentence carries its own gloss: "one massive skill that
basically **the head will link with everything else**". A head that *links to*
other things is a router; a merged single file would have nothing left to
link.

Corroboration: across 34,674 OMP operator turns and 168 Claude operator
turns, **no** operator turn asks for skills to be merged, combined, or
reduced to one file. The three apparent "one skill" hits were injected skill
text (Correction 1).

The work order's high-impact assumption is confirmed by the primary source.
L8 may act.

Confidence: **high** (primary operator text).

## D1 — "the two e prompt" — PRIOR-AGENT INTERPRETATION, medium confidence

What the operator said is fixed: "Also look for the two e prompt, and also
that will lead to another lane that needs to be fully verified and
validated." The operator never names a file.

What a prior session concluded: in the **same session** that received the
dictation, a scout was dispatched with this target —

> "# Target `/Users/nick/proofpunk/.planning/proofpunk-agent.prompt.md`
> (61.5KB) and everything under `/Users/nick/proofpunk/.planning/hardening/`.
> … This artifact is the user's 'two e prompt' reference and defines a
> SECOND work lane."
> — `ScoutPlanningPrompt.jsonl:7`, mirrored at `__advisor.jsonl:3`

**Provenance caveat — this is not operator confirmation.** That text was
authored by the parent assistant when dispatching the subagent, and appears
in the subagent's transcript as `role=user` only because that is how task
assignments are delivered. It records what a **prior agent believed**, not
what the operator said.

**Status: the leading hypothesis, held at medium confidence.**

Supporting it: it comes from the session that actually heard the dictation,
so it had context this session lacks; `.planning/proofpunk-agent.prompt.md`
is a genuinely two-part artifact (Part I spec + Part II build prompt), which
fits "two"; and it is the only artifact any session has ever tied to the
phrase.

Against it: no operator turn corroborates the mapping; the same session's
scout output is unusable (`ScoutPlanningPrompt.md` is progress narration, its
last JSONL record is an idle-reminder, and `LaneBPromptAudit.md` is **0
bytes** against a 524 KB `.jsonl`) — so the lane that was supposed to confirm
this never produced a verdict.

Also still true, and unchanged: **no artifact named `2e`, `e2e-prompt`, or
`E2` exists** in the tree, any branch, any tag, or any commit body.

Resolution rule for this run: proceed on the `.planning` reading for L18
scoping, label it an interpretation, and re-test it against any genuine
operator turn found in Phase 1 mining. Do not report D1 as evidence-resolved.

## D2 — "the other lane" — PRIOR-AGENT INTERPRETATION, medium confidence

The dictation binds D1 and D2: the two e prompt "will lead to **another
lane** that needs to be fully verified and validated." Whatever D1 is, D2 is
its consequence — so D2 inherits D1's confidence exactly.

Prior-agent reading: Lane B = the `.planning/` work, scoped to auditing the
prompt rather than building from it. The assignment states —

> "Non-goal, and this is critical: the user explicitly scoped this lane to
> VERIFY/VALIDATE THE PROMPT ONLY — do NOT build, scaffold, or implement the
> product the prompt specifies."
> — `LaneBPromptAudit.jsonl:19`

Same caveat: assistant-authored. The phrase "the user explicitly scoped" is a
**prior agent's claim about** the operator, not a quotation of one. It is
consistent with the dictation ("verified and validated", not "built"), but
consistency is not confirmation.

Independently verifiable fact: `.planning/execution-ledger.json:11-19`
records `C2_lane_b_unblock` as **BLOCKED**, requiring one of three exact
operator tokens (`APPROVE BARRIER DELTA`, `REJECT BARRIER DELTA`, `STOP`),
and notes that delegated judgment was attempted twice in prior sessions and
**RETRACTED as fabricated authority**.

Consequence for this run: Lane B may be **mined** (the work order authorizes
reading `.planning/`) but cannot be **verified or validated** without the
operator token — regardless of how D1 finally resolves. Reported as an honest
open item.

## D4 — corroborated against the primary source

| Heard | Actual text in the record | Status |
|---|---|---|
| "the food club" | "first gain your full understanding of **the food club**" — verbatim | CONFIRMED as a dictation artifact; the "full scope / whole plugin" reading is consistent with the preceding clause ("all the different things that go into this plugin") |
| "now they work together" | dictation reads "**how they work together**" | The corrected form is what the operator said; the mis-hearing was in the work order's transcription, not the source |

Confidence: **high** (primary operator text).

## Open, carried forward

1. **D1/D2 lack operator corroboration.** Phase 1 mining must search for any
   genuine operator turn naming the artifact. Until then both stay medium.
2. **The Lane B audit never produced a report.** `LaneBPromptAudit.md` is 0
   bytes; whether `.planning/lane-b-audit.md` was ever written is unverified.
   An empty lane must not be mistaken for a completed audit.

## Evidence

- `evidence/v3-release/00-discovery/raw/round1-dictation.txt` — full 1106-char
  operator dictation, rc captured separately.
- `evidence/v3-release/00-discovery/raw/operator-turns.json` — per-store
  operator-turn counts and hits, injected content excluded.
- Session artifacts cited inline by path and line, all under
  `~/.omp/agent/sessions/-proofpunk/2026-08-24T20-31-44-166Z_01a03578-…/`.
