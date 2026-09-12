# Runtime contracts, resolved from checked-in vendor digests

step-04 concluded the OMP and OpenCode contracts were unverifiable
because neither SDK is installed. That was wrong in an important way:
absence of TYPES is not absence of DOCUMENTATION. This repo vendors
cited digests of both platforms' docs, written during v4's research
phase, and they answer both questions. step-04 is superseded on this
point.

## OMP — session_stop CAN force continuation, and the cap-8 is real
```
  docs-omp.md:416: - `session_stop` handler: inspects the last ~6000 chars of session state
  docs-omp.md:417:   for a completion claim regex (`done|complete|completed|finished|
  docs-omp.md:418:   shipped|works now|fixed it`) unaccompanied by a proof regex
  docs-omp.md:419:   (`e2e-evidence/|evidence-inventory|step-\d+[-.]|screenshot|verdict|
  docs-omp.md:420:   curl\s+\S+\s+200|validate\s+OK`); if claim-without-proof, returns
  docs-omp.md:421:   `{ continue: true, reason: "...cite it by full path — or downgrade..." }`
  docs-omp.md:422:   — this is the `session_stop` cancelable-continuation contract documented
  docs-omp.md:423:   at `omp://extensions.md` "Prompt and turn lifecycle" (capped at 8
  docs-omp.md:424:   consecutive continuations, never fires for subagent sessions).
  docs-omp.md:425: - `registerCommand("proofpunk", ...)` — a status/notify-only slash command.
```
So the comment at extensions/proofpunk.ts:75-76 claiming 'cap 8 forced
continuations is the runtime's own guard' is CONFIRMED, sourced to
omp://extensions.md. I recorded it as unverified in step-04; it is not.

Also documented there: session_stop NEVER FIRES FOR SUBAGENT SESSIONS.
That is load-bearing — an intent check wired only to session_stop is
silently absent for every subagent, which is where much of this
plugin's work actually happens.

## OpenCode — session.idle exists, but it is OBSERVE-ONLY
```
  Session events: `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated`
```
The only documented BLOCKING mechanism in the OpenCode plugin API is
throwing from tool.execute.before (docs-opencode.md:83). Searching the
digest for continuation vocabulary:
  'continue': 0 lines    'cancel': 0 lines

Conclusion: an OpenCode plugin CANNOT force a session to continue. It
can observe session.idle, and it can refuse a tool call.

## What each surface can therefore actually enforce

| Surface | Mechanism | Can force another turn? |
|---|---|---|
| hooks/stop-guard.sh | decision:block on Stop/SubagentStop | YES — and it DOES cover subagents |
| extensions/proofpunk.ts | {continue:true} from session_stop | YES, capped at 8 by the runtime; NOT for subagents |
| opencode/plugin/proofpunk.ts | throw from tool.execute.before | NO — observe-only at session end |

## The design consequence I did not have before
One mechanism cannot be copied across all three. The OpenCode adapter
must enforce at the TOOL boundary — refuse the write/edit that would
conclude an unverified session — rather than at the session boundary,
because the session boundary there is not refusable.

Writing the same {continue:true} shape into the OpenCode plugin would
have produced a guard that silently does nothing, which is the exact
failure this plugin exists to catch: a green surface enforcing air.
