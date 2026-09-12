---
description: Acquire and digest authoritative platform docs before scouting, one digest per host
argument-hint: "[host ...]"
---

Activate the `implement` skill and run its Stage 1.5 ACQUIRE step — the docs-first stage that runs *before* any codebase scouting — for:

$ARGUMENTS

With no argument, detect every host the target repo actually touches (Claude Code, oh-my-pi, OpenCode) and acquire all of them. A repo touching no recognizable platform surface produces no digest; say so and stop.

Fetch the **authoritative** documentation for each host this session — vendor doc URLs for Claude Code and OpenCode, `omp://` internal docs for oh-my-pi — and write one digest per host to `.planning/docs-<host>.md`, conforming to `references/docs-acquisition.md`. The contract's six items are mandatory: host, numbered sections per real platform surface, a source on every load-bearing claim, a retrieval date fetched **this session**, an explicit method line, and a `## Gaps` section (an empty one must say so explicitly).

A digest whose claims carry no source is not a digest — it is memory, and memory is exactly what this stage exists to replace. Never date-stamp an inherited digest to make it look current: if an existing `.planning/docs-<host>.md` was retrieved in an earlier session, re-acquire it rather than reusing it.

**4. Scoped — everything you can select**

```
/proofpunk-acquire claude omp opencode
```
`acquire` takes host tokens as positional arguments — `claude`, `omp`, `opencode`, or any host token a future digest adopts by the same pattern. There are no flags. Everything else is the digest contract: this-session retrieval, sourced claims, explicit method, mandatory `## Gaps`.
