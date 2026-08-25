# Skill-count fix (#5) — exhaustive live proof against the local v2 plugin

Earlier called "structurally unprovable until a release ships". That was wrong:
the SDK loads the **local** plugin directory, so v2.0.1 is drivable live with no
publishing step.

## Why a listing was not enough

A first attempt asked a live session to list its `proofpunk:` skills. It replied
with 23 names, which a mechanical count reconciled as 6 commands + 17 skills
with zero repo skills missing. That reconciliation is sound but the underlying
evidence is still a **model self-report** — the model could derive names from
filenames without any skill loading.

Replaced with invocation evidence.

## Exhaustive invocation

Every skill in `plugins/proofpunk/skills/` was invoked by its namespaced name
through the `Skill` tool, each requiring three observed checks: the call
happened, its argument matched, and its ToolResult came back successful.

```
skills invoked with successful ToolResult: 18 / 18
missing: NONE
```

Per-probe records are in `../run-sdk-probes/skill_*.json`; each shows

```
{'tool_invoked': True, 'tool_arg_matches': True, 'tool_succeeded': True}
```

`tool_succeeded` is the load-bearing check — a control arm previously invoked
`proofpunk:end-user-testing` successfully *without* the plugin because a
same-named skill exists standalone in `~/.claude/skills/`. Only the tool result
distinguishes a load from a failed attempt the model silently retried.

## Why this proves the fix

Before the router existed the orchestration graph had zero roots. The router
`proofpunk` is among the 18 invoked, and the same query against the **installed**
v1.10.x finds no router at all (`INVENTORY.md`).

| | installed v1.10.x | local v2.0.1 |
|---|---|---|
| router `proofpunk` | absent | **invoked, ToolResult success** |
| `proofpunk:cook` | present | absent |
| skills invoked live | — | **18 / 18, none missing** |

The installed-version gap is a publishing matter, recorded separately in
`INVENTORY.md`. This document proves the fix itself works when v2 is loaded.
