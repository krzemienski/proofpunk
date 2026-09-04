# D1 — "the two e prompt" — RESOLVED as a transcription artifact for "the TUI prompt"

Measured: 2026-09-04 | Repo HEAD: `73e928e` (clean at time of measurement)
Evidence: `e2e-evidence/run-20260904T142528-v3-orchestrated/lane-orchestrator/step-01-d1-tui-hypothesis.log`

**Supersedes** the medium-confidence prior-agent interpretation recorded in
`docs/discovery-register.md` D1 and `d1-d2-d8-transcript-evidence.md` D1.
The *referent* is unchanged — it is still
`.planning/proofpunk-agent.prompt.md`. What changes is that the mapping is
now derived from the operator's own words rather than inherited from an
assistant-authored subagent dispatch, and D1's confidence rises accordingly.

## The reasoning prior sessions did not apply

Every prior session searched the tree for an artifact *named* `2e`, `E2`,
or `e2e-prompt`, found nothing, and fell back to a prior agent's guess.
`d1-d2-d8-transcript-evidence.md:125-126` records that exhaustive absence,
re-verified here (section E: 0 matches across all commit bodies).

But the same document already establishes, at **high** confidence, that this
dictation contains speech-to-text errors — and resolves two of them:

| Heard | Actual | Source |
|---|---|---|
| "the food club" | "the full scope" | `d1-d2-d8-transcript-evidence.md` D4 |
| "now they work together" | "**how** they work together" | same |

`docs/discovery-register.md` D4 rates both **high**. So the record already
proves this specific dictation garbles short phrases. No session then applied
that same established property to the phrase inside the same sentence.

Read aloud, **"the TUI prompt" transcribes to "the two e prompt"** — "TUI"
is spoken as three letters, T-U-I, and a speech-to-text pass renders the
leading "T-U" as "two" and the trailing "I" as "e". This is the same error
class as "full scope" → "food club", in the same 1,106-char utterance.

## Why the TUI reading is the correct referent — five independent checks

Each is a filesystem fact captured in the cited log, not an inference:

1. **`TUI` is established vocabulary in this exact project.** The plugin
   ships a `tui-testing` skill (section A). The operator is not reaching for
   an unfamiliar term.
2. **Exactly one `.planning` artifact is a TUI product prompt.** Of six
   `.planning/*.md` files, `proofpunk-agent.prompt.md` scores **36** matches
   for `Textual|terminal user interface|TUI`; the next highest is **1**, and
   four score **0** (section B). The mapping is unambiguous — there is no
   second candidate to confuse it with.
3. **The artifact declares itself a TUI at its head.** Line 6:
   `**UI framework:** Textual (pinned stable)`. §1.1: "a terminal-native
   mission-control interface" (section C).
4. **It is genuinely a *prompt*, not a spec.** Line 1: "Part II is the
   executable build prompt." The operator's noun is correct.
5. **It genuinely "leads to another lane."** Line 3 declares a separate
   standalone repository, `krzemienski/proofpunk-agent`, consuming this
   plugin read-only (section D). The operator's clause "that will lead to
   another lane that needs to be fully verified and validated" describes
   exactly this: a second repository, downstream of the plugin.

## What this changes, and what it does not

**Changed — D1 confidence: medium → high.** The referent no longer rests on
`ScoutPlanningPrompt.jsonl:7` (an assistant-authored dispatch that
`d1-d2-d8-transcript-evidence.md` Correction 4 correctly downgraded). It now
rests on the operator's own phrase, decoded via a transcription-error class
this repo's own evidence already established at high confidence, and
corroborated by five filesystem facts.

**Changed — D2 inherits the raised confidence.** The dictation binds them:
the prompt "will lead to another lane." D2's referent is the
`proofpunk-agent` build lane.

**NOT changed — Lane B execution stays BLOCKED.** Confidence in *what D1
refers to* is a separate question from *authorization to act on it*.
`.planning/execution-ledger.json:11-19` records `C2_lane_b_unblock` as
BLOCKED pending one of three exact operator tokens (`APPROVE BARRIER DELTA`,
`REJECT BARRIER DELTA`, `STOP`), and notes delegated judgment was attempted
twice in prior sessions and **RETRACTED as fabricated authority**. Resolving
the referent does not supply the token. Building `proofpunk-agent` remains
unauthorized.

## Open / UNRESOLVED

- **No operator turn confirms this decoding**, because none exists to find —
  the operator said the phrase once and never glossed it. This resolution is
  a decoding of primary operator speech, which is a stronger evidence class
  than the prior agent-interpretation, but it is still a decoding. It would
  be falsified by any operator turn using "two e prompt" to mean something
  else, or by a second TUI-prompt artifact appearing in `.planning/`.
- **D9b ("Rebo") and D9c ("Furble's Claude") remain unresolved.** Both are
  plausibly the same transcription-error class, but neither has a candidate
  referent that survives the five-check standard applied above. Recording the
  hypothesis without a referent would be speculation, not resolution.
