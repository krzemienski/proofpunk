# Doctrine enforcement map

Which doctrine is mechanically enforced, which is advisory, and which is a
runbook that cannot be enforced by construction. P10 asked for exactly this:
every rule either has hook enforcement or a stated gap. Nothing here is
aspirational — each row was measured from source on 2026-09-13.

## The hook taxonomy (measured, not assumed)

`plugins/proofpunk/hooks/` holds **10 scripts**. They are not interchangeable:
only four can stop anything.

| Script | Mechanism | Can it block? |
|---|---|---|
| `capture-guard.sh` | `exit 2` | **BLOCK** |
| `evidence-guard.sh` | `exit 2` | **BLOCK** |
| `no-test-files.sh` | `exit 2` | **BLOCK** |
| `stop-guard.sh` | top-level `{"decision":"block"}` | **BLOCK** |
| `bash-write-notice.sh` | `additionalContext` | advise |
| `platform-steer.sh` | `additionalContext` | advise |
| `post-write-walkthrough.sh` | `additionalContext` | advise |
| `session-start.sh` | `additionalContext` | advise |
| `bash-write-snapshot.sh` | emits no decision | observe |
| `instructions-loaded.sh` | emits no decision | observe |

**4 block-capable, 6 non-blocking.** This corrects the P9 criterion, which
assumed "7 hooks, each with a block case = 14 cases". The count 14 survives;
the reasoning does not. The honest arithmetic is 4 blockers × (block + allow)
+ 6 allow-only = 14.

Note `stop-guard.sh` emits `additionalContext` **only** on its fail-open paths
(missing python3, unreadable transcript). Its enforcement path is
`decision:block`. A classifier that greps for `exit 2` alone will misfile it as
advisory — mine did, and the source corrected it.

## Enforcement edges

A hook enforces a doctrine file when it cites that file — the citation is what
makes the rule traceable from the code that applies it.

| Doctrine | Enforced by | Kind |
|---|---|---|
| `evidence-contract.md` | `evidence-guard.sh` | **BLOCK** (`exit 2`) |
| `intent-verification.md` | `stop-guard.sh` | **BLOCK** (`decision:block`) |
| `subagent-aware-stop.md` | `stop-guard.sh` | **BLOCK** (`decision:block`) |
| `platform-routing.md` | `platform-steer.sh` | advise |

**4 of 17** doctrine files have a hook that names them.

## Hook-unenforced is NOT unenforced

Hooks are one surface of four. Counting only hook citations understates
coverage badly, so every doctrine file was measured against all four:
**hooks**, **skills** (the SKILL.md that applies the rule), **tools** (the
verifier that checks it), and **CI**.

| Doctrine | hooks | skills | tools | Kind |
|---|---|---|---|---|
| `evidence-contract.md` | 1 | 10 | 5 | rule, widely enforced |
| `end-user-actor.md` | 0 | 12 | 2 | stance, carried by skills |
| `severity-model.md` | 0 | 6 | 2 | vocabulary |
| `defect-pattern-database.md` | 0 | 3 | 0 | catalogue |
| `ios-hig-checklist.md` | 0 | 3 | 0 | checklist |
| `web-wcag-checklist.md` | 0 | 3 | 0 | checklist |
| `platform-routing.md` | 1 | 3 | 0 | routing rule |
| `ios-validation.md` | 0 | 3 | 1 | runbook |
| `run-trace-schema.md` | 0 | 2 | 2 | schema |
| `ci-gates.md` | 0 | 2 | 0 | CI contract |
| `cli-validation.md` | 0 | 2 | 0 | runbook |
| `web-validation.md` | 0 | 2 | 1 | runbook |
| `preflight-checks.md` | 0 | 2 | 0 | procedure |
| `api-validation.md` | 0 | 1 | 0 | runbook |
| `docs-acquisition.md` | 0 | 1 | 1 | procedure |
| `intent-verification.md` | 1 | 1 | 0 | rule |
| `subagent-aware-stop.md` | 1 | 1 | 0 | rule |

**Globally unenforced: zero.** Every doctrine file is carried by at least one
surface. Thirteen have no hook, and for runbooks and checklists that is the
correct shape — a runbook describes how to drive a platform as the end user,
and there is no proposition a `PreToolUse` hook could evaluate.

An earlier draft of this map claimed those thirteen were "without enforcement"
because it counted hook citations only. That was wrong: `end-user-actor.md`
alone is applied by a dozen separate skills (see its row above). The lesson is
recorded rather than quietly fixed — a narrow edge definition produced a
confident, false gap count.

Two rows could still carry *mechanical* enforcement and do not:

- `run-trace-schema.md` — a schema is checkable, but nothing validates emitted
  traces against it; today's two tool references consume traces, they do not
  verify shape.
- `severity-model.md` — severity vocabulary could be linted in verdict
  artifacts the way `verify-proof-vocab.py` lints completion words.

Both are open mechanisation gaps, not coverage gaps.

## Precedence

Hooks do not negotiate. When several fire on one tool call:

1. **Any `exit 2` denies.** `capture-guard`, `evidence-guard`, and
   `no-test-files` are independent; the first to deny ends the call. They do
   not consult each other, so their order is irrelevant to the outcome.
2. **`decision:block` at stop is separate.** `stop-guard.sh` runs on `Stop`
   and `SubagentStop`, never on a tool call, so it cannot race the deniers.
3. **Advisory output never overrides a deny.** `additionalContext` is context,
   not a decision. A hook that emits both has a bug.
4. **Fail-open is announced, never silent.** `stop-guard.sh` prints
   "enforcement OFF" and exits 0 when it cannot read what it needs. A clean
   stop is the *absence* of that notice — so "nothing printed" means the
   heuristic actually ran, not that it was skipped.

## Cross-runtime reality

This map describes **Claude Code**, where hooks exist. The other runtimes are
not equivalent and the doctrine does not pretend otherwise:

- **OMP** — enforcement lives in `extensions/proofpunk.ts`. It blocks on
  `tool_call` (destructive commands, secret reads, test-file writes) and can
  request one continuation on `session_stop`.
- **OpenCode** — enforcement lives in `opencode/plugin/proofpunk.ts`, and the
  only blocking seam is a `throw` from `tool.execute.before`. `session.idle`
  is observe-only: its handler returns void, so a stop cannot be blocked
  there. This is a property of the plugin API, not an omission.

Neither runtime can populate the subagent tracker: no extension or plugin
event carries a child agent identity. See `subagent-aware-stop.md`.
