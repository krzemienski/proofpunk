---
name: session-intent
description: >
  Reconstruct what was actually ASKED from the sessions themselves — parses
  Claude Code JSONL transcripts into a per-session intent matrix (first user
  prompt = stated intent, subsequent prompts = steering, tool calls, files
  touched, commits made), aligns sessions to git history, and builds
  intent-vs-implementation matrices where every row cites its session intent
  source or is marked intent-unrecoverable. Use when auditing what a
  codebase was supposed to become versus what it became; when session
  summaries, CLAUDE.md, or commit messages are the only stated rationale;
  when building commit-to-intent provenance; or when asked 'why was this
  change made' and the answer must come from evidence, not memory. Not for
  live repo audits (use codebase-truth-audit) or planning future work (use
  validation-plan).
---

# Session Intent Reconstruction

## Run checklist

Copy this checklist and track your progress:

- [ ] Locate and parse session JSONL transcripts
- [ ] Build the per-session intent matrix (stated intent + steering)
- [ ] Align sessions to git history (commits, files touched)
- [ ] Build the intent-vs-implementation matrix
- [ ] Cite the intent source per row, or mark intent-unrecoverable

The key difference from every other audit lane in this plugin: the input is
**the sessions themselves**, not summaries of them. A session summary is a
claim about intent, written after the fact, possibly about a tree that has
since moved. The transcript is the intent — the literal prompt the user typed
at that timestamp, on that branch. Per `../../references/evidence-contract.md`
this skill treats transcripts as evidence and everything downstream
(summaries, docs, commit messages) as claims to be checked against it.

## Doctrine

1. **First user prompt = stated intent.** Subsequent user prompts in the same
   session are steering — intent *revisions*, and they matter just as much.
   A session where the user said "actually, hold off on X" at 15:00 explains
   why X is absent from the tree at HEAD.
2. **Intent unrecoverable is a valid finding.** If no transcript covers a
   commit, mark the row "intent unrecoverable" and keep it open. Never
   backfill intent from the commit message alone — the assistant may have
   written that message, making it a claim about itself.
3. **Alignment is probabilistic, disclosure is exact.** Sessions align to
   commits by time window, branch, and file overlap — state which signals
   matched. A commit with no overlapping file and no session in its window
   is NOT silently merged into a nearby session's row.
4. **The matrix is the deliverable.** Every commit in the audited window gets
   a row: commit ref, files changed, session intent source (transcript path +
   session id), and a match verdict.

## Workflow

1. **Inventory** — locate transcripts (`~/.claude/projects/<slug>/*.jsonl` by
   default; confirm the slug for the audited repo — it derives from the
   project path). If the directory is absent or empty, STOP: report the
   intent lane as BLOCKED (transcripts unavailable), do not substitute
   summaries.
2. **Extract** — run the parser:

   ```bash
   python3 scripts/session_intent.py \
     --project yt-transition-shorts-detector \
     --since 2026-07-08 --until 2026-08-07 \
     --json evidence/session-intent.json --md evidence/session-intent.md
   ```

   Per session it records: first prompt (intent), steering prompts, tool
   counts, files touched, `git commit` invocations observed, branch, models
   and exact time bounds. Null intent means the transcript contained no real
   user prompt (e.g. tool-only session) — it stays null.
3. **Align** — for each commit in the window (`git log --since/--until
   --name-only`): candidate sessions are those whose window contains the
   commit timestamp; rank by branch match, then file-path overlap between
   `files_touched` and the commit's file list; sessions that ran
   `git commit` during their window outrank those that didn't.
4. **Verdict per commit** — INTENT-MATCHED (session found, intent explains
   the diff), INTENT-PARTIAL (session found, diff exceeds stated intent —
   list the excess files), INTENT-UNRECOVERABLE (no session evidence).
5. **Seal** — the parser output and the matrix are evidence; seal them with
   the `end-user-testing` skill before any downstream ruling cites them.

## Companion Reference

`references/claude-code-analyzer.md` (its original jq-based scripts preserved
under `references/scripts/`) — usage-pattern analytics over the same
transcripts (tool frequency, model distribution, project activity). Use it
for workflow-optimization questions; use THIS skill's parser for intent
questions. Do not confuse the two outputs: usage counts say what the tools
did; first prompts say what the user asked.

## Anti-Patterns

- Reconstructing intent from commit messages or PR titles → claims, not
  evidence; the assistant often authors them.
- Trusting "as discussed in session X" in a doc without opening X's
  transcript → verify or mark unverified.
- Merging a commit into the nearest session because the dates are close →
  alignment requires file or branch overlap, stated per row.
- Declaring a window fully covered while transcripts for part of it are
  missing → coverage gap is a finding, not a footnote.


## Bundled resources

Run these discovery scripts (from the skill directory) instead of hand-writing the same crawls:

- `references/scripts/analyze.sh` — primary session-analysis driver; run first.
- `references/scripts/analyze-claude-md.sh` — extracts stated rationale from CLAUDE.md files.
- `references/scripts/github-discovery.sh` — run to align sessions to git history via the GitHub API.
- `references/scripts/fetch-features.sh` — run to fetch feature/issue context for intent rows.

## Example

**Input:** User: 'Why was auth refactored in March? Answer from evidence.'

**Output:** JSONL transcripts parsed: session 2026-03-14's first prompt asked for 'session-intent provenance', 3 steering prompts follow; commit a1b2c3 aligned; the matrix row cites the session file, not memory.

## Skill calls

Leaf skill — owns canonical methods; calls nothing.

Called by: `codebase-truth-audit`, `implement`, `proofpunk`.
