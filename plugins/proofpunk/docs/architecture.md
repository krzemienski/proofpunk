# Proofpunk Plugin Architecture

This is the map a new contributor reads first: what each layer of the
plugin is for, how a request flows through them, and how the pieces are
wired to enforce one non-negotiable rule — **end-user testing is the only
PASS**. Every number below was counted from the tree, not remembered; see
"How this was measured" at the end.

This document does not restate `hooks-and-init-design.md` — that file is
the *design rationale* for the hook set as it existed at v1.10.0 (research
citations, the case for command hooks over prompt hooks, the original
4-event/5-script layout). This document describes the **current** system
(v2.2.0) as it actually ships, and calls out where the two have diverged.

## 1. The layers, and what each is for

Proofpunk ships as one plugin directory (`plugins/proofpunk/`) with seven
distinct layers. A request — a user typing `/proofpunk:implement "add
checkout"`, or Claude Code loading the plugin at session start — moves
through a subset of these layers depending on what kind of request it is.

| Layer | Location | Count | Purpose |
|---|---|---|---|
| Skills | `skills/*/SKILL.md` | 18 (17 delivery skills + 1 router) | `skills/proofpunk/SKILL.md` is the single entry point: it classifies a request's *shape* and hands off to exactly one (or a short ordered chain of) delivery skills, never re-executing their logic itself (§2). The other 17 are the actual methods — brainstorming, planning, implementing, auditing, debugging, red-teaming, proving — organized as a DAG so each method is owned by exactly one skill (§3). |
| Commands | `commands/*.md` | 6 (+6 OpenCode) | Slash-command surfaces (`/proofpunk:implement`, `:verify`, `:truth-audit`, `:rate-prompt`, `:forge-prompt`, `:install`) that activate a skill with the user's arguments. One-to-one with the OpenCode variants in `opencode/commands/proofpunk-*.md`, which carry the `proofpunk-` prefix OpenCode's flat command namespace requires. |
| Agents | `agents/*.md` | 3 Claude Code, 3 OMP (`omp/agents/`), 4 OpenCode (`opencode/agents/`) | Pre-configured subagent personas (`implement`, `scout`, `end-user-validate`) that bundle a skill's doctrine into a spawnable role, so a session can delegate a whole implement-and-prove loop to a dedicated agent instead of running it inline. OpenCode carries one extra agent, `proofpunk.md` — the router itself, spawnable as a persona there (Claude Code and OMP route through the skill directly). |
| Hooks | `hooks/*.sh` + `hooks.json` | 7 scripts, 6 events | Deterministic, non-LLM enforcement of the doctrine that skills alone cannot guarantee: blocking test-file writes, blocking secrets in evidence, blocking modification of sealed captures, and blocking an unproven completion claim (§4). |
| Shared references | `references/*.md` | 13 | The doctrine every skill defers to instead of restating: the End-User Actor Mandate, the evidence contract, per-platform validation runbooks (API/CLI/iOS/web), severity model, WCAG/HIG checklists, and more. Skills cite these as `../../references/X`; the installer flattens the citation depth and bundles a self-contained copy per skill (§6). |
| Assets | `assets/` | 5 files (2 templates + 3 scoped rule files) | `claude-md-template.md` and `agents-md-template.md` are the merge templates `/proofpunk:install` injects into a target project's memory file. `rules/{evidence-contract,proof-obligations,tui-driving}.md` are `paths:`-scoped rule fragments for the same install flow. |
| Installer | `tools/proofpunk-install.sh` | 1 script | The only path that turns this repo into an installed skill set on a user's machine, for four target platforms. Not part of the shipped plugin tree itself — it lives at the repo root under `tools/` and consumes `plugins/proofpunk/` as its source (§6). |

**Two other things worth naming alongside these layers, because they
gate everything above:** `tools/verify-orchestration.py` is a script a
contributor runs by hand — `AGENTS.md`'s testing requirement names it,
alongside `test-hooks.sh` and `dry-run-install.sh`, as the trio to run
from the repo root "before claiming any change here done." It proves the
18-skill DAG in §3 is real: it parses every `SKILL.md`'s `## Skill calls`
table directly and fails if the skill tables themselves — not this
document — encode a cycle, an edge to a nonexistent skill, or a
`Called by` line that doesn't match a real edge. It never reads this
document or any other prose file: the DAG's source of truth is the
`SKILL.md` tables, and this document is a description of what those
tables said when it was written, not an input the verifier checks — so
this document, specifically, can still drift from them if a skill's
table changes and this file isn't updated to match. §3's call graph
below was produced by reading those same 18 tables directly, for that
reason. `themes/` (20 flat-black cyberpunk themes, rendered to
OMP/OpenCode/Hyper formats from one `palettes.json` source of truth) is
presentation-only and does not affect any of the above.

### Request flow

```
user request
    │
    ▼
router skill (skills/proofpunk/SKILL.md)          — classify, pick one skill or a short chain
    │
    ▼
delivery skill(s)                                  — the actual method runs; may call other
    │                                                 skills per the DAG (§3), never restates them
    ▼
hooks fire on every tool call the skill makes       — PreToolUse/PostToolUse guard the write path;
    │                                                 Stop/SubagentStop guard the completion claim
    ▼
evidence lifecycle (end-user-testing's helper)      — every proof obligation ends in a sealed,
    │                                                 run-scoped e2e-evidence/ directory (§5)
    ▼
verdict: PASS / FAIL / BLOCKED / UNVERIFIED, cited by full path
```

Installation is orthogonal to this flow — it is how the router, skills,
hooks, and references get onto a machine in the first place (§6).

## 2. The router

`skills/proofpunk/SKILL.md` is the plugin's entry point and is called by
nothing else in the DAG (`Called by: nothing — the entry point for the
whole plugin`, its own last line). Its contract, read directly from the
file:

- **Run checklist**: classify the request (design / build / audit / bug /
  proof ask) → pick the single best-fit skill or the shortest ordered
  chain → hand off by quoting the ask, never restating the target skill's
  method → say so explicitly if nothing fits, rather than forcing a match.
- **Routing rule**: classify by the ask's *shape*, not by keyword-matching;
  on ambiguity, prefer the narrower skill over the broader one; a compound
  ask chains skills left to right, and each named skill still runs its own
  full workflow — the router never shortcuts a downstream skill's process.

Its `## Skill calls` table has 17 rows — one per delivery skill, each with
an explicit **When** (the request shape that routes there) and **What it
hands over** (exactly what context crosses the handoff, e.g. `brainstorm`
gets "the raw ask, unfiltered"; `red-team-eval` gets "the artifact to
attack"). This is the "explicit handoff column" a contributor should read
before anything else in this plugin.

Below the routing table sits a second table, **Shared doctrine — what
every skill defers to**: 13 rows, one per file in `references/`, each with
one line naming what it owns (`evidence-contract.md` → "run-scoped,
sealed, non-empty evidence"; `end-user-actor.md` → "the Actor Mandate —
who drives the system"). This is the doctrine layer from §1 made concrete:
routing tells you *which* skill; this table tells you *which rule* that
skill will apply and where it's canonically defined. The router's own
comment on this table is exact: "the installer rewrites these citations to
self-contained copies, so they resolve both in this repo and in an
installed tree" — see §6.

## 3. The skill call graph

Method ownership in this plugin is a **DAG, not a document**: a method
(the Actor Mandate, the proof-obligation XML format, the scout-first gate,
etc.) lives in exactly one skill, and every other skill that needs it
*calls* the owner — reads its `SKILL.md` at the invocation point and
applies the method verbatim, never restating it in its own body. This
section is derived directly from every skill's own `## Skill calls`
table (18 files read, not summarized from a prior doc), and
`tools/verify-orchestration.py` is the machine check a contributor runs
to confirm this property still holds (parses the same tables, asserts
closure, acyclicity, and that "Called by" claims match real edges) — see
§1 for why this is a manual, not automatic, gate in this repo.

### Call table (18 skills, 47 edges total: 17 from the router to every skill, plus 30 among the 17 delivery skills)

| Skill | Calls | Called by |
|---|---|---|
| `proofpunk` | all 17 other skills | — (entry point) |
| `implement` | `session-intent`, `brainstorm`, `prompt-forge`, `validation-plan`, `end-user-testing`, `tui-testing`, `root-cause-debugging` | `proofpunk` |
| `production-readiness` | `codebase-truth-audit`, `full-functional-audit`, `stack-testing`, `end-user-testing` | `proofpunk` |
| `full-functional-audit` | `end-user-testing`, `ui-experience-audit`, `root-cause-debugging`, `tui-testing` | `production-readiness`, `proofpunk` |
| `codebase-truth-audit` | `session-intent`, `end-user-testing`, `root-cause-debugging` | `production-readiness`, `proofpunk` |
| `plan-hardening` | `red-team-eval`, `validation-plan`, `end-user-testing` | `proofpunk` |
| `mobile-validation-runner` | `end-user-testing`, `visual-inspection` | `proofpunk` |
| `ui-experience-audit` | `visual-inspection`, `end-user-testing` | `full-functional-audit`, `proofpunk` |
| `stack-testing` | `root-cause-debugging` | `production-readiness`, `proofpunk` |
| `validation-plan` | `end-user-testing` | `implement`, `plan-hardening`, `proofpunk` |
| `red-team-eval` | `end-user-testing` | `plan-hardening`, `proofpunk` |
| `root-cause-debugging` | `end-user-testing` | `codebase-truth-audit`, `full-functional-audit`, `implement`, `stack-testing`, `proofpunk` |
| `visual-inspection` | `end-user-testing` | `mobile-validation-runner`, `ui-experience-audit`, `proofpunk` |
| `brainstorm` | — (leaf) | `implement`, `proofpunk` |
| `end-user-testing` | — (leaf) | `codebase-truth-audit`, `full-functional-audit`, `implement`, `mobile-validation-runner`, `plan-hardening`, `production-readiness`, `red-team-eval`, `root-cause-debugging`, `ui-experience-audit`, `validation-plan`, `visual-inspection`, `proofpunk` (12 callers — the most-depended-on skill in the plugin) |
| `prompt-forge` | — (leaf) | `implement`, `proofpunk` |
| `session-intent` | — (leaf) | `codebase-truth-audit`, `implement`, `proofpunk` |
| `tui-testing` | — (leaf) | `implement`, `full-functional-audit`, `proofpunk` |

### Method ownership (what each owner actually owns)

Read straight from the "What it hands over" column of the tables above —
this is the doctrine each caller applies verbatim rather than restating:

| Owner | Method it owns |
|---|---|
| `end-user-testing` | The proof standard: the Actor Mandate, fresh-evidence sealing rules, run-scoped evidence directories, the verdict format. |
| `brainstorm` | The scout-first gate and exact-requirements gate applied before any design is accepted. |
| `validation-plan` | The proof-obligation XML format (one obligation per task, blocking cumulative proof). |
| `prompt-forge` | The build-prompt XML skeleton and the prompt-rating rubric. |
| `session-intent` | Session mining: turning `~/.claude/projects/*.jsonl` transcripts into an intent matrix. |
| `root-cause-debugging` | The root-cause method — no fix without reproduction, ever. |
| `tui-testing` | PTY-driving discipline for terminal apps (observe-then-act, matched waits, three-facet evidence). |
| `visual-inspection` | The screenshot examination protocol — a capture is examined, never assumed correct. |
| `red-team-eval` | The four adversarial lenses used to attack a plan or artifact before it ships. |

### Depth (distance from the leaf owners)

Computed the same way `verify-orchestration.py` computes it —
`depth(u) = 0` for a leaf, else `1 + max(depth(v) for v called by u)`:

```
depth 5  proofpunk                                              (entry point; calls all 17)
depth 4  production-readiness
depth 3  full-functional-audit
depth 2  codebase-truth-audit, implement, mobile-validation-runner,
         plan-hardening, stack-testing, ui-experience-audit
depth 1  red-team-eval, root-cause-debugging, validation-plan, visual-inspection
depth 0  brainstorm, end-user-testing, prompt-forge, session-intent, tui-testing
```

### A contradiction found while writing this section

The previous revision of this file's call graph included the edge
`implement --> stack-testing` in its mermaid diagram. The live
`implement/SKILL.md` "Skill calls" table has **no such row** — a
`grep` for `stack-testing` inside that file returns zero matches.
`implement`'s real callees are the seven listed above; `stack-testing` is
called only by `production-readiness` and the router, matching
`stack-testing/SKILL.md`'s own `Called by:` line. The old doc's *prose*
depth table (which placed `implement` at depth 2, not the depth 3 the
stale edge would force) was actually consistent with the correct graph —
only the diagram carried the stale edge. This section was regenerated
from the 18 live `SKILL.md` files rather than edited from the prior
version, precisely so this kind of drift cannot survive a rewrite.

## 4. The hook system

Configuration lives in one file, `hooks/hooks.json`, read directly for
this section. It declares **6 events** and **7 scripts**, wired into
**8 registrations** (one event fires 3 scripts under a single matcher):

| Event | Matcher | Script(s) | Timeout |
|---|---|---|---|
| `SessionStart` | `startup\|resume\|clear` | `session-start.sh` | 5s |
| `Stop` | (none) | `stop-guard.sh` | 10s |
| `SubagentStop` | (none) | `stop-guard.sh` | 10s |
| `PreToolUse` | `Write\|Edit` | `no-test-files.sh`, `evidence-guard.sh`, `capture-guard.sh` | 5s each |
| `InstructionsLoaded` | (none) | `instructions-loaded.sh` | 5s |
| `PostToolUse` | `Write\|Edit` | `post-write-walkthrough.sh` | 5s |

### Decision surface per script

| Script | Event | Deny path | Otherwise |
|---|---|---|---|
| `session-start.sh` | SessionStart | never denies | always emits `hookSpecificOutput.additionalContext` with the one-paragraph doctrine summary and the six command names |
| `stop-guard.sh` | Stop, SubagentStop | scans the last 40 transcript lines, assistant-authored only; emits `{"decision":"block","reason":...}` if a completion CLAIM appears with no PROOF citation, **or** if CLAIM+PROOF appear with no SCOUT record | silent — exit 0, no output at all (a stop hook that speaks on every stop is noise across a multi-plugin session) |
| `evidence-guard.sh` | PreToolUse | `exit 2` + stderr if the write targets an evidence directory **and** the payload matches a secret-shaped pattern (API keys, GitHub tokens, AWS keys, private-key headers, or a generic `key/secret/token = value` assignment) | `exit 0` (allow) for everything else |
| `capture-guard.sh` | PreToolUse | `exit 2` + stderr if the target is an **already-existing** file, under an evidence directory, with a raw-capture extension (`.txt .log .out .err .jsonl .png .har .csv`) — captures are immutable once written | `exit 0` for new files, sidecar `.md`/`.json` files, and anything outside evidence directories |
| `no-test-files.sh` | PreToolUse | `exit 2` + stderr if the path matches a test-file shape (`*test*`, `*.spec.*`, `*.test.*`, `__tests__/`, etc.) | `exit 0` for everything else |
| `instructions-loaded.sh` | InstructionsLoaded | never denies | always appends one JSONL line (`ts`, `file_path`, `load_reason`, `cwd`) to `~/.claude/proofpunk-loads.jsonl` — this is the measurement tap that proves `/proofpunk:install`'s memory injection actually loads |
| `post-write-walkthrough.sh` | PostToolUse | never denies | if the written path is production code (not evidence, docs, `.planning/`, or config) — emits `additionalContext` reminding the agent to drive the real system and cite evidence before any completion claim; silent otherwise |

### These hooks run in parallel, not in sequence

This is a correction to how the hook set is easy to misdescribe: **all
hooks matching a given event and matcher fire in parallel**, per Claude
Code's own hook execution model — this is not a proofpunk-specific
choice, it's how the host runs any set of matching hooks (proofpunk's own
or another installed plugin's on the same event). When more than one
hook's result must be reconciled, the host resolves it by precedence:
**deny > defer (ask) > allow**. Concretely: the three `PreToolUse`
scripts under the `Write|Edit` matcher (`no-test-files.sh`,
`evidence-guard.sh`, `capture-guard.sh`) are **not** a sequential
pipeline where each one only runs if the last one passed — they all run
against the same tool call at once, and if *any* of them exits 2, the
write is denied regardless of what the other two return. Do not describe
this system as "no-test-files.sh runs, then evidence-guard.sh runs, then
capture-guard.sh runs" — that ordering does not exist and is not how the
guard actually behaves under a plugin ecosystem where other tools may also
be registered on the same event.

### A known gap in current matcher scope

`PreToolUse` in `hooks.json` matches only the tool names `Write` and
`Edit`. All three guard scripts key off `tool_input.file_path` (or the
Bash-tool-agnostic content field), which a `Bash` tool invocation (e.g.
`cat > f <<EOF`, `tee`, `sed -i`, or a Python one-liner that opens and
writes a file) does not populate in the shape these scripts expect. A
write performed through the Bash tool therefore currently bypasses
`no-test-files.sh`, `evidence-guard.sh`, and `capture-guard.sh`
simultaneously — and also bypasses `post-write-walkthrough.sh`, which
matches the same `Write|Edit` set on `PostToolUse`. This is a real,
currently-open limitation of the matcher's scope as configured, not a bug
in any individual script's logic — each script correctly denies what it
can see; it simply cannot see a Bash-mediated write.

**Mitigation shipped, and what it is not.** Two hooks now observe Bash
writes: `bash-write-snapshot.sh` (`PreToolUse`, matcher `Bash`) hashes
protected paths — evidence directories and test-shaped paths — before the
command runs, and `bash-write-notice.sh` (`PostToolUse` and
`PostToolUseFailure`, matcher `Bash`) re-hashes them afterward and reports
what changed. It reports test files written, evidence captures modified or
deleted, and secret-shaped content landing in evidence.

This is **detection, not prevention**, and the distinction is load-bearing:
the write has already happened when the notice fires. Nothing is blocked and
nothing is undone. The bypass above remains open.

It is scoped that way deliberately. An earlier attempt at prevention parsed
shell to decide a deny and falsely blocked `cp -p`, `mv -f`, `touch -c`, and
`sed -i -e` — ordinary commands, refused. That version was reverted. Denying
on a guess at shell semantics is worse than the gap it closes.

So detection works by **effect, never by parsing the command**: a diff of
content hashes taken before and after. A command that changes nothing emits
nothing, whatever it looked like, which means no false positive can interfere
with a working command. Content hashing rather than mtime+size is what
catches `cp -p` (which preserves mtime) and equal-size substitution when the
target is a protected path — a verdict artifact flipped from `PASSED` to
`FAILED` keeps its byte count. A `cp -p` outside the protected set is not
watched at all, and stays silent.
Baselines are keyed per session and tool-use id, written atomically, and
consumed on read, so parallel Bash calls cannot clobber each other. A failed
command still consumes its state, because the notice is registered on
`PostToolUseFailure` as well. State abandoned by a killed session is not
cleaned immediately: the sweep runs inside the notice hook, so it is removed
only once some later detector run fires and finds it older than an hour.
When the pre-command scan hits its cap the baseline is marked incomplete and
the notice says coverage is off for that call rather than silently reporting
nothing.

Closing the gap properly needs central enforcement that does not depend on
reading shell — an operator decision, not something to improvise here.

## 5. The evidence lifecycle

Every proof obligation in this plugin — every `end-user-testing` call, in
practice — is enforced by one small, dependency-free helper:
`skills/end-user-testing/scripts/fresh_evidence.py`. Its docstring states
the contract directly: it enforces "the eight fresh-evidence rules from
the Proofpunk evidence contract: every validation run owns a run-scoped
directory, artifacts are sequentially named, non-empty, fresh (mtime >=
run start), cited by full path, and sealed with an inventory."

All four commands operate against `./e2e-evidence/` **relative to the
current working directory** — there is no global or absolute evidence
root. The **active run** is always "the most recently modified `run-*`
subdirectory" (`max(runs, key=lambda p: p.stat().st_mtime)`) — there is
no explicit "current run" pointer; whichever run directory was touched
last *is* the active one for every subsequent command in the same
session.

| Command | What it does | On success | On refusal |
|---|---|---|---|
| `init-run <slug>` | Creates `e2e-evidence/run-<ISO8601-compact>-<slug>/`, writes an empty `evidence-inventory.txt` and a `.run-meta` file stamped with the run's start time | prints the new `run_id` to stdout, exit 0 | exit 2 if the slug fails `^[A-Za-z0-9_-]+$` |
| `next-step <slug>` | Counts existing `step-*` entries in the active run and prints the next sequential filename prefix (`step-<NN>-<slug>`, zero-padded) | prints the path, exit 0 | exit 2 if no active run exists, or the slug is invalid |
| `seal` | Globs every `step-*` file in the active run, records `<name> <size>` per line, appends a summary line (`sealed=<ISO> count=<N> total_bytes=<N>`), and overwrites `evidence-inventory.txt` with the result | prints the inventory path, exit 0 | exit 2 if there is no active run |
| `validate` | Reads `.run-meta`'s `started=` timestamp, then checks every `step-*` file's mtime against it and its size against zero | exit 0, printing `validate OK: <run_dir>`, when no existing `step-*` file is stale or empty — **a run with zero `step-*` files also passes**, since the check loop never executes | exit 2, printing one `STALE:` or `EMPTY:` line per offending file to stderr, if any artifact fails either check; also exit 2 if `.run-meta` is missing or its timestamp is unparseable |

Three properties worth calling out explicitly because they are easy to
miss reading the commands in isolation. **Staleness is measured against
the run's own recorded start time**, not "now" — an artifact written
before `init-run` ran (a leftover from a prior attempt, copied into the
new run directory) is caught as `STALE` even if its mtime is recent in
absolute terms. **`seal` does not validate** — it always overwrites the
inventory with whatever `step-*` files currently exist; `validate` is a
separate, later call, meaning a caller can seal a run and only discover
staleness/emptiness on the explicit validate step. And **`validate` is
vacuously satisfiable** — its loop is `for f in sorted(run_dir.glob(
"step-*"))`; if that glob matches zero files the loop body never runs,
`bad` stays `0`, and `cmd_validate` returns `"validate OK: <run_dir>"`.
A run with `.run-meta` but no captured `step-*` artifacts at all — i.e.
no evidence was ever captured — still passes `validate`. The command
also never reads `evidence-inventory.txt`, so it does not check that
`seal` was ever called or that the inventory reflects the files
present; `validate` proves only "every step file that exists is fresh
and non-empty," not "evidence was captured" or "the run was sealed."
Invalid command/input, a missing active run or `.run-meta`, stale or
empty step files, and an unparseable start timestamp all produce a
message on stderr and process exit code 2. `cmd_validate` raises
`SystemExit(2)` directly for the stale/empty-file case; every other
refusal path raises `Refusal`, which `main()` catches and converges to
the same stderr-plus-exit-2 contract.

## 6. Installation

`tools/proofpunk-install.sh` is the single script that turns this repo
into an installed skill set. Read directly, its target resolution is:

```
--target claude-code   ->  ~/.claude/skills                          (default)
--target omp           ->  ${PROOFPUNK_OMP_DIR:-~/.omp/agent/skills}
--target opencode      ->  ~/.config/opencode/skills
--target agents        ->  ~/.agents/skills
--dir PATH             ->  any explicit directory (overrides --target entirely)
```

For each of the 18 skills selected (all of them, by default, or a
`--only a,b,c` subset), the installer does more than a file copy: it
**tar-copies the skill directory**, then **rewrites doctrine citations**
(`../../references/X` at repo depth becomes `references/X` at install
depth), then runs a **fixed-point sweep** over `references/` — copying
every file cited anywhere inside the skill (backticked or bare prose,
any citation depth) into the skill's own bundled `references/`
subdirectory, and repeating that sweep until nothing new gets added. This
last step exists because doctrine files cite each other (e.g.
`evidence-contract.md` cites `end-user-actor.md`) — one pass would leave
a dangling reference. The result is what `AGENTS.md` calls "self-
contained copies": an installed skill resolves its own doctrine without
ever reaching outside its own directory, in contrast to this repo's
layout where skills deliberately cite `../../references/` and rely on the
installer to widen those paths.

Doctrine also lands as a standalone bundle at `$DIR/proofpunk-doctrine/`
— a full copy of `references/` plus a generated `README.md` summarizing
the five ruling rules (the Iron Rule, the End-User Actor Mandate,
remediation, fresh evidence, severities) in plain prose, independent of
any single skill.

### Hooks: `hooks.json` is now the single source of truth

With `--hooks` (automatic on plugin installs), the installer no longer
hardcodes which scripts to copy or which events to register — both are
**derived from `hooks/hooks.json` at install time**, via a small inline
Python step that:

1. Parses `hooks.json`, collects every `*.sh` filename referenced across
   every event's every matcher, and hard-fails (`sys.exit(...)`) if any
   named script doesn't actually exist on disk — a name mismatch aborts
   the install rather than silently installing an incomplete set.
2. Copies exactly those scripts (and only those) into `~/.proofpunk/hooks`.
3. Merges an idempotent entry into the target platform's `settings.json`
   for **every** event/matcher/hook combination `hooks.json` declares —
   keyed by **event AND script basename together**, not by event alone.

That last detail is the fix this change protects against regressing: an
earlier version of this merge step matched idempotency on any command
containing the substring `.proofpunk/hooks` within the same event, so
once the *first* `PreToolUse` script installed, every sibling script
sharing that event read as "already present" and was silently skipped —
`evidence-guard.sh` and `capture-guard.sh` shipped copied-to-disk but
never registered in `settings.json` as a result (see §8). Keying on
`(event, script_basename)` instead means three scripts sharing one event
each get their own independent idempotency check and their own entry.

opencode and omp targets don't get this settings-merge path at all —
their enforcement lives in platform-native plugin glue instead
(`opencode/plugin/proofpunk.ts`, `extensions/proofpunk.ts`), which the
installer prints guidance toward rather than trying to merge into a
settings file those platforms don't use the same way.

Collisions default to **skip and report** (`SKIP $skill (already exists;
use --override to replace)`); `--override` replaces with a
`.bak-<timestamp>` copy unless `--no-backup` is also given. A `--only`
name that doesn't exist in the source increments a `MISSING` counter and
the script exits `3` at the end if that counter is nonzero — no partial
install is claimed as success.

## 7. Design invariants

The doctrine every layer above exists to enforce, stated once here and
cited (never restated) by every skill, hook, and reference:

- **The Iron Rule.** If the real system doesn't work, fix the real
  system. Never mocks, stubs, test doubles, fake endpoints, or test-mode
  bypasses — enforced mechanically by `no-test-files.sh` (a `PreToolUse`
  denial, not a suggestion) and stated in every skill's doctrine
  deferral.
- **The End-User Actor Mandate.** Validation is driven, never assumed.
  The AI personally drives the live system as the end user — `curl`
  against a running server for JSON/HTTP backends, a real browser for UI,
  a real simulator for mobile. Test runners are regression tooling that
  runs *after* proof, never a substitute *for* proof.
- **Evidence is fresh, run-scoped, sealed, and immutable.** Owned by
  `end-user-testing`, mechanically enforced by `fresh_evidence.py` (§5)
  and `capture-guard.sh` (§4) together — one produces the artifacts under
  the freshness/sealing rules, the other refuses to let anyone edit them
  afterward. `evidence/AGENTS.md` states the reason plainly: "a modified
  capture is a fabricated claim."
- **Verdicts are PASS / FAIL / BLOCKED / UNVERIFIED, cited by full
  path.** An unexecuted check is UNVERIFIED, never PASS. `stop-guard.sh`
  is the mechanical backstop for this rule at the session level: it reads
  the transcript itself and blocks a completion claim that has no cited
  proof artifact, rather than trusting the claim.

## 8. Known drift — and its mitigation

This repo's single most recurring failure mode, visible across its own
history: **hand-maintained lists drift from their source of truth.**
Two concrete, evidenced instances:

1. **The skill-count string regressed four times.** `docs/improvements.md`
   records it directly: "Count drift has shipped four times (17→19→18;
   commits `2953547`, `c39a0f0`, `f95ba9d`, and this session)." The
   before-arm cited there is exact: `verify-orchestration.py:144` printed
   "the 17 skills" in prose while the script was actually validating 18 —
   a literal string that fell out of sync with a `glob()` result three
   lines away in the same file.
2. **`evidence-guard.sh` shipped registered-but-dead.** It was written at
   v1.10.0 (`docs/hooks-and-init-design.md`'s own title names that
   version) alongside `no-test-files.sh` and `capture-guard.sh`, all
   sharing the `PreToolUse` event — but the installer's settings.json
   merge step keyed idempotency on the event alone, so once
   `no-test-files.sh` installed and matched, every later script sharing
   that event read as "already present" and was never actually merged
   into `settings.json`. The script existed on disk, executable, correct
   — and never once fired in a real install, from the release it shipped
   in through v2.1.0 (the version immediately preceding the fix
   documented in §6). `docs/improvements.md` names this precisely: "A
   hook that is copied but unregistered is indistinguishable, from the
   outside, from a hook that was never written."

**The root cause is the same in both cases**: a number or a check was
typed by hand in one place, describing a fact that lived somewhere else
and could change independently. **The mitigation this repo has converged
on, and the standard this document itself follows, is: derive, don't
restate.** `verify-orchestration.py` now prints `f"the {len(skills)}
skills"`, computed from the same glob that builds the skill list, so the
number is correct by construction rather than by discipline. The
installer's hook copy and hook registration are now both derived from
`hooks/hooks.json` (§6) instead of a second hardcoded list, for the same
reason. This document's own §3 call graph and §1 layer counts were
generated by reading the 18 `SKILL.md` files and running the actual
`glob` patterns listed below — not by editing the previous prose — which
is exactly how it caught the `implement --> stack-testing` drift in §3.

## How this was measured

Every count in this document came from one of these, run against the
live tree while writing it — re-run any of them to re-verify:

- 18 skills: `glob plugins/proofpunk/skills/*/SKILL.md` → 18 directories,
  matching `ALL_SKILLS` in `tools/proofpunk-install.sh` verbatim.
- 6+6 commands: `glob plugins/proofpunk/commands/*.md` → 6;
  `glob plugins/proofpunk/opencode/commands/*.md` → 6.
- 3+3+4 agents: `glob plugins/proofpunk/agents/*.md` → 3;
  `glob plugins/proofpunk/omp/agents/*.md` → 3;
  `glob plugins/proofpunk/opencode/agents/*.md` → 4 (the extra file is
  `proofpunk.md`, the router agent, OpenCode-only).
- 9 hook scripts / 7 events / 11 registrations: read
  `plugins/proofpunk/hooks/hooks.json` directly and counted the events
  object's keys and each event's `hooks[].hooks[]` entries. The count grew
  from 7/6/8 when `bash-write-snapshot.sh` (PreToolUse:Bash) and
  `bash-write-notice.sh` (PostToolUse:Bash and PostToolUseFailure:Bash) were
  added as detection-only mitigation for the Bash write bypass (§4).
- 13 references: `glob plugins/proofpunk/references/*.md` → 13.
- 5 assets: `read plugins/proofpunk/assets/` → 2 top-level template files
  + `rules/` containing 3 files.
- The call graph in §3: `grep '## Skill calls'` (and the table rows under
  it) across all 18 `SKILL.md` files individually — not copied from any
  prior document.
