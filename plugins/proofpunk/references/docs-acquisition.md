# ACQUIRE-Stage Digest Contract (shared)

Defines what a v4 ACQUIRE-stage digest must contain to be citable by a
scout subagent, a `--parallel` lane contract, or a steering-guard verdict.
Closes the gap `v4-spec.md` §2a names: `implement`'s research sub-step had
no positive definition anywhere in the skill body before v4. This document
is that definition's *output shape* — not the stage's own procedure (that
belongs to the ACQUIRE stage text in
`plugins/proofpunk/skills/implement/SKILL.md`, inserted between Stage 1
MINE and Stage 2 SCOUT per `v4-spec.md` §2a/§3), and not *which* end-user
validation runbook applies once a target application's platform is known
(that is `platform-routing.md`'s job — see "Host vs. Platform" below).

## The Anti-Pattern

**A digest whose claims carry no source is not a digest — it is memory,
and memory is exactly what the ACQUIRE stage exists to replace.**
`v4-spec.md` §2a's cited gap is the reason this matters: the scout
subagent was granted `WebFetch`
(`plugins/proofpunk/agents/scout.md:6`) but nothing told it to use it, so
platform facts came from training-data recall — discovered wrong
mid-scout, or never discovered at all. A digest that restates what the
model already believed, with no URL or doc path attached to each claim,
reproduces that exact failure one layer earlier. Such a document may not
be treated as satisfying this contract, no matter how confident or
plausible its claims read.

## Required Contents

A conforming digest states, at minimum, all six of the following. The
three worked examples below satisfy all six, in this order or folded
together per the patterns shown:

1. **Host** — which platform-*documentation source* this digest covers:
   `Claude Code`, `oh-my-pi (OMP)`, `OpenCode`, or another host a future
   task targets. One digest per host, never a merged multi-host file.
   (See "Host vs. Platform" below — this is not the same axis as
   `platform-routing.md`'s iOS/Web/API/CLI table.)
2. **One numbered section per platform surface the host actually has.**
   There is no fixed template across hosts — the section list mirrors
   each host's real capability set, not a checklist forced onto every
   host. See the table below for the three real lists on file; none of
   them matches another exactly, and that is correct, not a defect.
3. **A source on every load-bearing claim** — a vendor doc URL
   (`https://...`) or a local path (`omp://...`, `~/.omp/...`, a repo
   `path:line`) the claim was actually read from in this session. A
   claim with no citation is not load-bearing content and does not
   belong in the digest, hedged or not.
4. **A retrieval date** — the date the cited web docs were actually
   fetched *this session*, not inherited from a prior digest.
5. **An explicit method line** stating how the docs were obtained: web
   fetch of live vendor pages, a local `omp://`/config read, or a mix —
   and if a source turned out to be unauthoritative (a third-party page,
   a compatibility shim), that it was excluded from the body and moved
   to Gaps rather than kept with a caveat. Items 4 and 5 are usually one
   sentence, not two separate lines — see the worked examples.
6. **A mandatory `## Gaps` section.** Lists what the author could not
   confirm from the sources read: an assumption the docs did not settle,
   a claim needing dynamic testing the author could not run, or a fact
   two sources contradict. **An empty Gaps section must say so
   explicitly** — e.g. "No unconfirmed claims in this digest; every
   assertion above cites a source read this session." An omitted heading
   reads as "not written," not "nothing to report," and a reviewer
   cannot tell the two apart from a missing section.

## Worked Examples (this repo)

Three digests already meet this contract, written during `v4-spec.md`'s
own research phase and cited by its §4 table:
`.planning/v4-architecture/docs-claude.md`,
`.planning/v4-architecture/docs-omp.md`,
`.planning/v4-architecture/docs-opencode.md`.

| Digest | Numbered sections (item 2) | Extra sections beyond the floor |
|---|---|---|
| `docs-claude.md` | 6: Plugins, Skills, Hooks, Subagents, Slash commands, Settings/permissions | — |
| `docs-omp.md` | 5: Skill discovery, Rules system, Hooks/extensions/plugin surface, Subagent/model routing, proofpunk's OMP-specific glue | — |
| `docs-opencode.md` | 5: Agents, Commands, Plugins, Config, MCP/tools surface | Mismatches summary (shipped files vs. current docs) |

Every row ends in a `## Gaps` section (item 6) — the one section present
in all three regardless of how differently the rest are shaped. A digest
may add sections beyond the floor (`docs-opencode.md`'s "Mismatches
summary" is a real example) — the six items above are a minimum, not a
ceiling.

`docs-omp.md`'s own header is a worked example of item 5's discipline in
practice, not just compliance with it: *"Web search was used once during
drafting and has been removed as evidence — third-party/compatibility-
package material is not an authoritative OMP source; that uncertainty is
now confined to the Gaps section."* The author didn't cite an
unauthoritative source with a caveat; they retracted it from the body
entirely and named the retraction in Gaps.

This repo's citation discipline predates the ACQUIRE stage:
`docs/skill-canon.md:1-16` is the same "dated retrieval, sourced URL
list, explicit method line" pattern, applied to a different artifact (a
committed multi-host conformance matrix, not a per-run ACQUIRE digest) —
named as the discipline model by `v4-spec.md` §5's W2 item, not as
another `docs-<host>.md` instance.

## File Naming and Location

- **Filename**: `docs-<host>.md`, lowercase host token matching the
  filenames `v4-spec.md` §4's own table already establishes: `claude`,
  `omp`, `opencode` (and whatever token a future host's digest adopts,
  by the same pattern).
- **Location for a live ACQUIRE run**: `.planning/docs-<host>.md` —
  sibling of `.planning/execution-ledger.json`
  (`plugins/proofpunk/skills/implement/SKILL.md:205`) and
  `validation-plan`'s own `.planning/BRIEF.md`/`.planning/ROADMAP.md`
  siblings
  (`plugins/proofpunk/skills/validation-plan/SKILL.md:36-37`). Flat, not
  run-slug-namespaced — the execution ledger itself isn't namespaced per
  run either.
- The three worked examples above live under
  `.planning/v4-architecture/` instead of `.planning/` directly because
  that directory is this architecture proposal's own research output,
  not an `implement` run. The naming convention (`docs-<host>.md`) is
  identical either way; only the parent directory differs by context.

## Host vs. Platform — do not conflate

This document's "host" (item 1) is the AI coding harness whose own
documentation the digest summarizes: Claude Code, OMP, OpenCode.
`platform-routing.md`'s "Platform" column is a different axis entirely —
the *target application's* platform (iOS/macOS, Web, Flutter, API,
CLI) that a validation runbook routes against. A steering-guard verdict
(`v4-spec.md` §2d) may need both at once — the digest for the harness
running the task, and `platform-routing.md`'s detection table for the
app being built — but they are never the same lookup, and a digest
citation is never a substitute for a `platform-routing.md` citation or
vice versa.

## Who Cites a Digest

Per `v4-spec.md` §2b–§2d, a digest is consumed, never re-derived, by:

- **The scout subagent** — already wired, not hypothetical:
  `plugins/proofpunk/agents/scout.md:23-29` instructs the scout to read a
  digest named in its spawn context before scouting and treat its
  platform facts as given, falling back to `WebFetch` only for a fact
  the digest doesn't cover (and naming the URL and fact produced, so the
  digest can be extended next time rather than silently re-fetched).
- **A `--parallel` lane contract** — the extended schema (`v4-spec.md`
  §2c) binds which digest a lane consumes, so two lanes building for
  different hosts don't cross-pollinate assumptions.
- **A steering-guard verdict** — the `PreToolUse` guard (`v4-spec.md`
  §2d) cross-checks a validation-shaped Bash call against the digest for
  the task's target host(s), in addition to `platform-routing.md`'s
  detection table (see "Host vs. Platform" above).

A citation into a digest that does not meet this contract — no source
on a claim, no retrieval date, no `## Gaps` section — is not valid
grounding for any of the three consumers above. Treat it the same as no
digest at all: the consumer must re-fetch or escalate, never proceed on
an uncited claim because a file happened to exist at the expected path.
