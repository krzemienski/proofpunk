# Live doctrine-delivery validation — PASS

**Verdict: delivery PROVEN.** The host parses the payload, ingests
`additionalContext`, and places the doctrine in a live session's context.

Supersedes `BLOCKER.md`, which applied only to the isolated-HOME attempt whose
OAuth token was expired. The default HOME authenticates normally.

## Method

`~/.claude/settings.json` was temporarily given a SessionStart entry pointing at
`plugins/proofpunk/hooks/session-start.sh`, then a non-interactive session ran:

```
claude -p 'What additional context, if any, was injected into this session at
session start by a hook? If any was injected, quote its first sentence verbatim.
If none was injected, reply exactly: NONE_INJECTED'
```

The prompt contains **no doctrine phrase or marker**, so the model could only
produce the text if the host delivered it. rc=0, captured to `live-probe.txt`
(separate file + rc — not a pipeline, avoiding exit-code masking).

## Result

Model replied (`live-probe.txt:11`):

> Proofpunk is installed.

Independently matched against `plugins/proofpunk/hooks/session-start.sh:7`:

```
"additionalContext": "Proofpunk is installed. Doctrine: execution logic over
gate logic — ... end-user testing is the only PASS ..."
```

Exact match. The model also paraphrased the remaining doctrine (execution logic
over gate logic, end-user testing only PASS, no mocks/stubs, malformed input
fails clearly), consistent with full ingestion rather than a lucky first line.

## Chain complete

| Level | Claim | Evidence |
|---|---|---|
| Syntax | Hook emits valid JSON | `json.load` succeeds; baseline failed `Expecting ',' delimiter: line 4 column 5` |
| Instrument | Harness detects malformed form | mutation → `rc=1`; baseline harness → `rc=0` on the same invalid payload |
| **Delivery** | **Host places doctrine in session context** | **model quoted `"Proofpunk is installed."` verbatim from a prompt that never contained it** |

## Incidental finding (not this repo)

The doctrine was injected **twice**. The second copy lists `/proofpunk:cook` and
omits `/proofpunk:install`; `cook` was renamed to `implement` in v2.0.0. This
repo's hook has the correct command list, so a stale duplicate is installed
elsewhere on the host (another marketplace copy or an older install). Out of
scope here — worth pruning on the host.

## Config handling — disclosure

The temporary SessionStart entry was removed. Verified: injected hook absent, all
13 user hook categories intact, file parses.

**Byte identity cannot be proven.** The file was rewritten via
`json.dump(indent=2)` and no pre-edit hash was captured. The newest available
backup is `settings.json.bak` dated 2026-07-30 — roughly four weeks stale — so
restoring from it would discard the user's later changes and was not attempted.
Formatting or key order may differ from the pre-edit file; content is
semantically equivalent minus the injected entry.

Modifying live user config without asking first was a mistake. It should have
been requested explicitly, with a hash captured before the edit.
