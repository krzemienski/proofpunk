# Skill Canon — Multi-Host Conformance Matrix

Measured: 2026-09-04T04:47:50Z | Repo HEAD: 9963648 (working tree dirty — 18
modified files, adopted by the operator as "Phase 5 pre-work"; this document
touches none of them)
Method: web fetch of current vendor documentation (URLs cited per claim) +
`read`/`grep`/`eval` (Python `yaml.safe_load`) against the 18 on-disk
`SKILL.md` files under `plugins/proofpunk/skills/*/SKILL.md` + `omp://skills.md`
local loader docs read via the `read` tool + the repo's own `hooks.json`,
`plugin.json`, `marketplace.json`, and `tools/proofpunk-install.sh`.

All web sources retrieved 2026-09-04 (today), superseding the 2026-09-02
retrieval date recorded in `evidence/v3-release/00-discovery/a8-canon-opencode.md`
(that file's product-tree reads were pinned to a41591a; this document's canon
research is redone fresh against current vendor docs, and its C7 section reads
the current HEAD 9963648 tree directly).

---

## 0. Sources (canonical list, cited inline below)

1. Open Agent Skills specification — https://agentskills.io/specification
   (retrieved 2026-09-04)
2. Claude Code — Extend Claude with skills — https://code.claude.com/docs/en/skills
   (retrieved 2026-09-04)
3. Claude Code — Skill authoring best practices —
   https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
   (retrieved 2026-09-04)
4. Claude Code — Using Agent Skills with the API —
   https://platform.claude.com/docs/en/build-with-claude/skills-guide (retrieved 2026-09-04)
5. Claude Code — Plugins reference — https://code.claude.com/docs/en/plugins-reference
   (retrieved 2026-09-04)
6. Claude Code — Create and distribute a plugin marketplace —
   https://code.claude.com/docs/en/plugin-marketplaces (retrieved 2026-09-04)
7. Claude Code — Hooks reference — https://code.claude.com/docs/en/hooks
   (retrieved 2026-09-04)
8. OpenCode — Agent Skills (V1 docs) — https://opencode.ai/docs/skills/
   (retrieved 2026-09-04; content byte-consistent with the 2026-09-02 capture
   already recorded in `evidence/v3-release/00-discovery/a8-canon-opencode.md`)
9. OpenAI Codex — Build skills — https://learn.chatgpt.com/docs/build-skills
   (retrieved 2026-09-04; `learn.chatgpt.com` is OpenAI's official ChatGPT/Codex
   documentation domain, cross-linked from `developers.openai.com` and
   `openai.com/codex`)
10. OpenAI Codex — Custom instructions with AGENTS.md —
    https://learn.chatgpt.com/docs/agent-configuration/agents-md (retrieved 2026-09-04)
11. Local OMP loader docs — `omp://skills.md` (read via the `read` tool against
    this session's OMP installation; not a public URL — see §3.4 for what this is)
12. This repo: `plugins/proofpunk/hooks/hooks.json`, `plugins/proofpunk/.claude-plugin/plugin.json`,
    `.claude-plugin/marketplace.json`, `plugins/proofpunk/agents/implement.md`,
    `tools/proofpunk-install.sh`, and all 18 `plugins/proofpunk/skills/*/SKILL.md` files.

---

## 1. Conformance matrix

### 1.1 SKILL.md frontmatter fields × host

Legend: **R** = required, **O** = recognized/optional, **I** = silently
ignored (parsed but not acted on, or not read at all), **E** = enforced at
package/upload time (hard error if present and not on the allowed list),
**Ext** = host-specific extension beyond the open spec, **—** = field does
not exist / not applicable for that host.

| Field | Open Agent Skills spec [1] | Claude Code (local skill, any level) [2] | Claude Code (claude.ai upload / Skills API / `package_skill.py`) [2][4] | OpenCode V1 [8] | Codex [9] | OMP [11] |
|---|---|---|---|---|---|---|
| `name` | **R** — 1–64 chars | **O** — sets display name shown in listings; directory name is the invocation name regardless (see §1.2 "Must equal parent directory name") [2] | **E** — allowed | **R** [8] | **R** (frontmatter `name`/`description`, per [9]) | **O** — defaults to directory name if absent; runtime only requires `name` + `path` for *validity* [11] |
| `description` | **R** — 1–1024 chars | **O**/Recommended — if omitted, uses first paragraph of body; combined with `when_to_use` and truncated at 1,536 chars in the skill listing [2] | **E** — allowed, required non-empty | **R** in V1 docs [8]; optional at V2 runtime per the repo's own A8 evidence (out of scope here — V1 is this canon's target) | **R** [9] | **O** at runtime, but **required** (`requireDescription: true`) for the native `.omp` provider, the `omp-plugins` extension-package provider, and the `github` provider; NOT required for claude/codex/agents/opencode/claude-plugins providers or `skills.customDirectories` scans, per [11] |
| `license` | **O** — license name or bundled-file reference | **O** — accepted, not acted on; part of spec passthrough [2] | **E** — allowed | **O** [8] | not documented in [9]/[10] | **I** — not in the OMP frontmatter field list at all [11] |
| `compatibility` | **O** — 1–500 chars | **O** — accepted, not acted on [2] | **E** — allowed, ≤500 chars | **O** [8] | not documented | **I** — not in the OMP frontmatter field list [11] |
| `metadata` | **O** — string→string map | **O** — read by the skill's own tooling; Claude Code drops a non-map value; don't reuse other frontmatter names as keys [2] | **E** — allowed | **O** — string→string map [8] | not documented as a top-level `SKILL.md` field (Codex instead uses a separate `agents/openai.yaml` for UI/policy/tool-dependency metadata — see §3.3) [9] | **I** — not in the OMP frontmatter field list; unknown keys are "preserved as unknown metadata" generically, not a typed `metadata` map [11] |
| `allowed-tools` | **O**, Experimental — space-separated tool list | **O** — pre-approves tools for the invoking turn only; grant clears on next message [2] | **E** — allowed (experimental, per spec) | not documented in V1 [8] | not documented as a `SKILL.md` field (Codex's `agents/openai.yaml` has a separate `dependencies.tools` mechanism, not the same as `allowed-tools`) | **I** — not in the OMP field list [11] |
| `disable-model-invocation` (kebab) / `disableModelInvocation` (camel, this repo's runtime) | — (not spec) | **Ext** — `disable-model-invocation: true` hides description from Claude's context, user-only invocation [2] | **E** — **rejected**; upload/packaging hard-fails with "Unexpected key(s)…" if present [2] | not documented | not documented | **Ext** — `disableModelInvocation?: boolean`, "Agent Skills equivalent of `hide`"; normalized from kebab-case `disable-model-invocation` on input [11] |
| `hide` | — (not spec) | not a recognized Claude Code field name (Claude Code uses `disable-model-invocation` / `user-invocable` instead) | **E** — rejected | not documented | not documented | **Ext** — `hide?: boolean`; hides from system-prompt listing but skill stays loaded and reachable via `skill://<name>` / `/skill:<name>` [11] |
| `when_to_use`, `argument-hint`, `arguments`, `user-invocable`, `context`, `background`, `hooks`, `paths`, `shell`, `model`, `effort`, `disallowed-tools` | — (not spec) | **Ext** — all recognized Claude Code-only extensions [2] | **E** — every one of these **rejected**; only the 6 spec fields survive upload [2] | not documented | not documented | **I** — none in the OMP field list [11] |
| `globs`, `alwaysApply` | — (not spec) | not documented as Claude Code fields | **E** — rejected | not documented | not documented | **Ext** — `globs?: string[]`, `alwaysApply?: boolean` [11] |
| Any other unrecognized key | — | Claude Code (local): not itemized in the field table but the frontmatter is YAML — unrecognized keys are simply not acted on by the six documented mechanisms; **no hard-fail** locally, only on upload/packaging | **E** hard error naming the offending key(s) [2] | **I** — "Unknown frontmatter fields are ignored" (V1 docs, verbatim) [8] | not documented | **I** — "additional keys are preserved as unknown metadata" [11] |

Key normative quotes:

- Open spec, field table (verbatim): "`name` … Max 64 characters. Lowercase
  letters, numbers, and hyphens only. Must not start or end with a hyphen."
  and "`description` … Max 1024 characters. Non-empty." [1]
- Claude Code upload/packaging hard-fail (verbatim): `Unexpected key(s) in
  SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools,
  compatibility, description, license, metadata, name` [2]
- OpenCode V1 (verbatim): "Only these fields are recognized: `name`
  (required), `description` (required), `license` (optional), `compatibility`
  (optional), `metadata` (optional, string-to-string map)… Unknown frontmatter
  fields are ignored." [8]
- OMP (verbatim, local doc): "Supported frontmatter fields on the skill type:
  `name?: string`, `description?: string`, `globs?: string[]`,
  `alwaysApply?: boolean`, `hide?: boolean`, `disableModelInvocation?:
  boolean` … additional keys are preserved as unknown metadata." [11]

### 1.2 `name` field: character/length rules × host

| Rule | Open spec [1] | Claude Code (local) [2][3] | Claude Code (upload/API) [4] | OpenCode V1 [8] | OMP [11] |
|---|---|---|---|---|---|
| Max length | 64 | 64 (same regex family via the open-standard inheritance stated in [2]'s intro) | 64 [3] | 64 [8] | not documented as a hard limit; runtime treats `name` as advisory display text, defaulting to directory name |
| Charset | lowercase `a`–`z`, `0`–`9`, `-` only | same (Claude Code "follows the Agent Skills open standard" [2]) | same, enforced | same; regex `^[a-z0-9]+(-[a-z0-9]+)*$` given verbatim [8] | not enforced by the loader (`runtime only requires name and path for validity` [11]) |
| No leading/trailing hyphen | **Yes** | inherited from spec | enforced | **Yes** [8] | not enforced |
| No consecutive hyphens (`--`) | **Yes** | inherited from spec | enforced | **Yes** [8] | not enforced |
| Must equal parent directory name | **Yes**, spec-mandated ("Crucially, it must exactly match the name of the skill's parent folder") [1] | For Claude Code *local* skills, the **directory name is the actual invocation key** regardless of what `name:` says — `name` in frontmatter instead sets the *display name*, and only affects the last path segment for **plugin** skills (`my-plugin/skills/review/SKILL.md` with `name: fancy` → `/my-plugin:fancy`) [2] | enforced per spec (name must match parent folder when packaged via `package_skill.py`) | **Yes**, one of the "Validate names" rules, verbatim [8] | not enforced; `name` "defaults to the skill directory name" when absent, implying mismatch is tolerated when a `name` is explicitly given [11] |
| XML tags (`<`/`>`) banned in `name` | not stated in the open spec text itself | **Yes** — "Cannot contain XML tags" [3], verbatim | same, hard-enforced | not documented | not documented |
| XML tags (`<`/`>`) banned in `description` | not stated in the open spec text itself | **Yes** — "Cannot contain XML tags" [3], verbatim (a rule the open spec text does not itself state for `description`) | same, hard-enforced | not documented | not documented |
| Reserved words `anthropic`, `claude` banned in `name` | not stated in the open spec text itself | **Yes** — "Cannot contain reserved words: 'anthropic', 'claude'" [3], verbatim | same, hard-enforced (also stated in [3]'s naming-conventions "Avoid: Reserved words: `anthropic-helper`, `claude-tools`" list) | not documented | not documented |

Verbatim source of both rules — directly read from [3]'s "YAML Frontmatter"
callout box: `**YAML Frontmatter:** The SKILL.md frontmatter requires two
fields: name: * Maximum 64 characters * Must contain only lowercase letters,
numbers, and hyphens * Cannot contain XML tags * Cannot contain reserved
words: "anthropic", "claude" description: * Must be non-empty * Maximum
1,024 characters * Cannot contain XML tags * Should describe what the Skill
does and when to use it.` This confirms the `description` field also bans
XML tags, in addition to `name` — a fact not carried in the open spec text
itself (§1.1/§1.3), and not previously in the repo's local canon evidence.

### 1.3 `description` field: length rules × host

| Host | Hard limit | Notes |
|---|---|---|
| Open spec [1] | 1–1024 chars | "Must be 1-1024 characters" |
| Claude Code (local skill) [2] | No fixed per-field cap on `description` alone; the **combined** `description` + `when_to_use` text is **truncated at 1,536 characters** in the system-prompt skill listing (a display-time truncation, not a validation error) | Verbatim: "the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage" [2] |
| Claude Code (upload/API, Skills API, `package_skill.py`) [3] | 1024 chars, non-empty, enforced as a hard validation rule | "Must be non-empty… Maximum of 1,024 characters" |
| OpenCode V1 [8] | 1–1024 chars | "`description` must be 1-1024 characters" |
| OMP [11] | not documented as a hard limit | Required only for specific providers (native `.omp`, `omp-plugins`, `github`); otherwise optional; no stated max |

### 1.4 Directory layout & discovery paths × host

| Host | Discovery path(s) | Recursion | Source |
|---|---|---|---|
| Open spec [1] | `skill-name/SKILL.md` (+ optional `scripts/`, `references/`, `assets/`) | Non-recursive layout is implied by the directory example; the spec doesn't itself define a multi-root scan, since that's a host concern | [1] |
| Claude Code, local | `~/.claude/skills/<name>/SKILL.md` (personal), `.claude/skills/<name>/SKILL.md` (project, walks up to repo root), `<plugin>/skills/<name>/SKILL.md` (plugin), enterprise via managed settings; nested `.claude/skills/` below cwd load lazily on first file touch in that subdirectory | One level under `skills/`; nested `.claude/skills/` directories are a *separate* discovery mechanism (directory-qualified names like `apps/web:deploy`), not recursive scanning of one `skills/` tree | [2] |
| Claude Code, plugin | `<plugin>/skills/<name>/SKILL.md`, or a single root `SKILL.md` if the plugin has no `skills/` dir and no `skills` manifest field; `plugin.json`'s `skills` field can add custom paths (`"./custom/skills/"`) | Non-recursive per directory, but multiple custom directories can be listed | [5] |
| Claude Code, skills-directory plugin | Any `<skills-dir>/foo/.claude-plugin/plugin.json` loads that folder as a plugin `foo@skills-dir` | N/A — one manifest per named skill folder | [5] |
| OpenCode V1 [8] | 6 documented paths: `.opencode/skills/<name>/SKILL.md` (project), `~/.config/opencode/skills/<name>/SKILL.md` (global), `.claude/skills/<name>/SKILL.md` (project Claude-compat), `~/.claude/skills/<name>/SKILL.md` (global Claude-compat), `.agents/skills/<name>/SKILL.md` (project agent-compat), `~/.agents/skills/<name>/SKILL.md` (global agent-compat) | Non-recursive per directory; project paths walk up to the git worktree root | [8], corroborated by the repo's own A8 evidence at `evidence/v3-release/00-discovery/a8-canon-opencode.md:32-42` |
| Codex [9] | `$CWD/.agents/skills` (scanned in every directory from cwd up to repo root — repo scope), `$HOME/.agents/skills` (user scope), `/etc/codex/skills` (admin scope), bundled system skills (`github.com/openai/skills`) | Each location is `.agents/skills/<name>/SKILL.md`-shaped; walking is up the directory tree, not recursive within one `skills/` folder. Codex does **not merge** same-named skills across locations — "If two skills share the same `name`, Codex doesn't merge them; both can appear in skill selectors" [9] | [9] |
| OMP [11] | `<skills-root>/<skill-name>/SKILL.md`, one level under `skills/`, across 7 priority-ordered providers (native `.omp` priority 100, `omp-plugins` 90, `claude` 80, `{claude-plugins, agents, codex}` 70, `opencode` 55, `github` 30, `omp-managed` 5) | Explicitly non-recursive: "Nested patterns like `<skills-root>/group/<skill>/SKILL.md` are not discovered by provider loaders." `skills.customDirectories` scanning is also non-recursive (same `*/SKILL.md` glob) | [11] |

### 1.5 Auto-discovery vs explicit listing

| Host | Behavior |
|---|---|
| Claude Code | Full auto-discovery from the paths in 1.4; no explicit per-skill registration needed beyond placing `SKILL.md` in a recognized directory [2][5] |
| OpenCode | Full auto-discovery from the 6 documented paths [8]; an additional opt-in `skills.paths` / `skills.urls` (V1) config array can add non-standard sources, but the 6 default paths themselves need no listing |
| Codex | Full auto-discovery within the 5 scope directories, **but** the initial system-prompt skill listing also includes **each skill's file path** (not just name/description) and is capped at 2% of context window or 8,000 characters when the window is unknown — Codex "may omit some skills from the initial list and show a warning" under budget pressure. This is closer to explicit-listing-with-paths than the other hosts' pure name+description advertisement, though it is still automatic, not manually curated. [9] |
| OMP | Full auto-discovery via provider precedence; system-prompt inclusion is itself conditional — the discovered list is only injected "if `read` tool is available", otherwise omitted entirely [11] |

**Verdict on the assignment's framing ("whether skills need explicit listing
with full paths rather than auto-discovery"):** No host in this canon
requires **manual/explicit** per-skill listing for standard discovery.
Codex is the partial exception: it auto-discovers, but its system-prompt
*advertisement* format is name+description+**path**, and that combined
listing is subject to a hard character budget that can silently drop skills
from the initial list on large installs — the closest thing to "explicit
listing" behavior among the four hosts, but it is not something the skill
author does; it is a Codex-side prompt-construction detail. [9]

### 1.6 Progressive disclosure model (open spec, adopted by Claude Code and Codex)

| Tier | Token budget | Loaded when |
|---|---|---|
| 1. Metadata (`name` + `description`) | ~100 tokens per skill | At startup, for every installed skill [1][3] |
| 2. Instructions (`SKILL.md` body) | <5,000 tokens recommended; hard practical ceiling "under 500 lines" | When the skill is activated (explicit or implicit match) [1][3] |
| 3. Resources (`scripts/`, `references/`, `assets/`) | As needed | Only when the loaded instructions reference them [1] |

Codex explicitly documents the same three-tier model plus its own extra
budget gate on tier 1: "the initial list also includes each skill's file
path… this list uses at most 2% of the model's context window, or 8,000
characters when the context window is unknown" [9]. Claude Code's tier-1
gate is the 1,536-character `description` + `when_to_use` cap per skill,
not a whole-listing budget [2].

### 1.7 File-reference rules (open spec)

Verbatim: "When referencing other files in your skill, use relative paths
from the skill root… Keep file references one level deep from `SKILL.md`.
Avoid deeply nested reference chains." [1] Claude Code's `${CLAUDE_SKILL_DIR}`
substitution and OMP's `skill://<name>/<relative-path>` URL protocol both
implement this "relative-to-skill-root, one level deep, no traversal" model
as host-specific mechanisms — OMP's is guard-enforced at the protocol level
(rejects absolute paths, rejects `..` traversal, rejects any resolved path
escaping `baseDir`) [11].

---

## 2. Claude Code plugin & hooks canon (this repo's runtime)

### 2.1 `plugin.json` schema — fields this repo uses

`plugins/proofpunk/.claude-plugin/plugin.json` uses: `name`, `version`,
`description`, `author` (`{name}`), `license`, `keywords` (array). All six
are documented **Metadata fields** in the plugin manifest schema; `name` is
the only *required* field if a manifest is present at all [5]. This repo's
manifest omits `displayName`, `homepage`, `repository`, `metadata`,
`defaultEnabled`, and every **Component path field** (`skills`, `commands`,
`agents`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`,
`experimental.*`, `userConfig`, `channels`, `dependencies`) — all optional,
so their absence just means auto-discovery + default `hooks/hooks.json`
apply, which matches this repo's actual layout (`skills/`, `agents/`,
`hooks/hooks.json` present at default paths, no `plugin.json` component
overrides). [5]

### 2.2 `marketplace.json` schema — fields this repo uses

`.claude-plugin/marketplace.json` uses: `name` (marketplace id, required),
`owner` (`{name}`, required), `metadata.description`, `metadata.version`,
`metadata.pluginRoot`, and one `plugins[]` entry with `name`, `source`,
`description`, `version`, `license`, `keywords`, `category`. Both `name` and
`source` are documented **Required fields** on a plugin entry [6]. This
repo's use of `metadata.description`/`metadata.version` instead of top-level
`description`/`version` on the marketplace object is explicitly supported:
"`description` and `version` are also accepted under `metadata` for
backward compatibility" [6]. `metadata.pluginRoot: "./plugins"` requires
Claude Code v2.1.239+ per the same doc [6] — this repo does not pin a
minimum Claude Code version anywhere in the manifest, so this is a soft
compatibility risk, not a conformance violation, and out of this document's
scope to resolve.

### 2.3 Plugin-agent frontmatter fields

Per [5]: "Plugin agents support `name`, `description`, `model`, `effort`,
`maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`,
and `isolation` frontmatter fields. The only valid `isolation` value is
`"worktree"`. For security reasons, `hooks`, `mcpServers`, and
`permissionMode` are not supported for plugin-shipped agents." This repo's
`plugins/proofpunk/agents/implement.md` uses `name`, `description`,
`skills` (array of 3), `tools` (comma-separated string: `Read, Write, Edit,
Bash, Glob, Grep, WebFetch`) — all four are on the recognized list; none of
the disallowed (`hooks`, `mcpServers`, `permissionMode`) fields are present.
Conformant.

### 2.4 Hook event names — the 7 keys used in this repo's `hooks.json`, checked against current support

`plugins/proofpunk/hooks/hooks.json` declares exactly these 7 top-level
event keys (line numbers from a raw read of the file): `SessionStart` (L4),
`Stop` (L16), `SubagentStop` (L27), `PreToolUse` (L38), `InstructionsLoaded`
(L70), `PostToolUse` (L81), `PostToolUseFailure` (L103).

All 7 are present, verbatim, in the current official event table at [5] and
[7] (both pages list the identical table). Specific verification of the two
event names the assignment flagged:

- **`InstructionsLoaded`**: **still supported**, unchanged semantics from
  what this repo assumes. Verbatim from current docs: "Fires when a
  `CLAUDE.md` or `.claude/rules/*.md` file is loaded into context. This
  event fires at session start for eagerly-loaded files and again later
  when files are lazily loaded… The hook doesn't support blocking or
  decision control… It runs asynchronously for observability purposes." [7]
  This repo's registration (`no matcher`, so fires on every `load_reason`)
  is a valid no-op-safe configuration — `InstructionsLoaded` cannot block or
  modify anything regardless of matcher, matching this plugin's stated intent
  ("context injection plus deterministic enforcement" — this specific hook
  is pure observability/context-injection, never enforcement, and the docs
  confirm it structurally cannot enforce).
- **`PostToolUseFailure`**: **still supported**. Verbatim: "Runs when a tool
  that started executing fails: the tool threw an error, or an MCP tool
  returned an error result… This event doesn't fire for tool calls rejected
  before execution: an unknown tool name, input that fails schema or
  tool-specific validation, or a permission denial." [7] This repo's
  registration matches `Bash` only (L105), consistent with its stated use
  (`bash-write-notice.sh`, presumably surfacing failed write-attempting Bash
  commands).

### 2.5 PostToolUse cannot deny — confirmed

Verbatim, decision-control table: `PostToolUse` → Can block? **No** — "Shows
stderr to Claude; the tool already ran." [7] Also stated narratively:
"`PostToolUse` hooks fire after a tool has already executed successfully… To
surface a warning to Claude from a `PostToolUse` or `PostToolUseFailure`
hook, exit 2 instead so Claude sees the stderr even though the tool already
ran." [7] This is unconditional — there is no configuration flag or matcher
that grants `PostToolUse` blocking power; `hookSpecificOutput.decision:
"block"` on `PostToolUse` ends the current turn (or, with
`continueOnBlock: true`, feeds the reason back and continues) but never
prevents the tool call itself, since it has already completed by the time
the hook runs. [7] This repo's two `PostToolUse` registrations
(`post-write-walkthrough.sh` on `Write|Edit`, `bash-write-notice.sh` on
`Bash`) are therefore structurally incapable of blocking the write/command
they observe — any enforcement this plugin performs on writes must happen
in `PreToolUse` (which this repo does separately register for `Write|Edit`
with `no-test-files.sh`, `evidence-guard.sh`, `capture-guard.sh`, and for
`Bash` with `bash-write-snapshot.sh`), not `PostToolUse`. The repo's own
`hooks.json` top-level `description` field states the intent correctly:
"context injection plus deterministic enforcement of the proof contract" —
the enforcement half lives entirely in the `PreToolUse` block (L38-69), and
`PostToolUse`/`PostToolUseFailure` (L81-114) are consistent with a
notification-only role given the API's constraints.

### 2.6 `settings.json` hook-merge semantics

Verbatim: "Hook entries merge across settings levels rather than replacing
each other: user, project, and local settings add their own hooks without
removing managed ones, and the `disableAllHooks` setting can't disable
managed hooks from outside managed settings." [7] Applied to this repo: a
plugin's `hooks/hooks.json` is one more layer that **merges** with
`~/.claude/settings.json`, `.claude/settings.json`, and
`.claude/settings.local.json` — it does not override or replace hooks
declared at those other levels; "If you define the same handler in more
than one settings file, it runs once. A plugin's or skill's copy of the
same handler stays separate." [7] This means a project or user
`settings.json` PreToolUse hook on the same matcher (`Write|Edit`) as this
plugin's `no-test-files.sh` would run **in addition to**, not instead of,
the plugin hook — both fire in parallel ("All matching hooks run in
parallel" [7]).

---

## 3. Codex / AGENTS.md surface

### 3.1 Skill discovery is automatic, not manual-path listing

Per [9] and [10]: Codex discovers `AGENTS.md` via a strict override/merge
precedence chain (`AGENTS.override.md` > `AGENTS.md` > configured fallback
filenames, one file per directory, concatenated root-to-leaf) that is
**entirely separate** from `SKILL.md` skill discovery. `AGENTS.md` files are
persistent instruction context, always loaded and merged; `SKILL.md` skills
are on-demand capability packs, advertised as name+description(+path) and
loaded in full only on activation. The two systems do not share a
directory convention (`AGENTS.md` lives at arbitrary directory roots;
`SKILL.md` lives one level under `.agents/skills/`).

### 3.2 Does Codex require explicit full-path listing?

No — see §1.5. Codex auto-scans the 5 documented scope locations. The only
"listing" a user or repo maintainer does is placing the skill directory in
one of those locations, or (for team distribution beyond a single repo)
packaging as a **plugin**, which is Codex's explicit-declaration mechanism —
distinct from and higher-friction than plain skill folders: "Plugins can
include one or more skills… ship a skill alongside a connector, package
them as a plugin" [9]. Plugins are the closest Codex analog to Claude Code's
`marketplace.json` + `plugin.json` two-file model, but this repo does not
currently ship a Codex plugin — its `tools/proofpunk-install.sh --target
opencode/agents` paths write to `.agents/skills`-style locations directly,
which is the plain-skill-folder path, not the plugin path. This is a design
choice already made by the repo, not a gap this document identifies.

### 3.3 `agents/openai.yaml` — the one Codex-specific metadata surface

Per [9], an optional `agents/openai.yaml` inside a skill folder configures
UI display metadata (`interface.display_name`, `icon_small`, etc.),
invocation policy (`policy.allow_implicit_invocation`, default `true`), and
tool dependencies (`dependencies.tools[]`, e.g. declaring an MCP server the
skill needs). This has no equivalent in the open spec, Claude Code, or
OMP — it is entirely additive and lives in a sibling file, not in
`SKILL.md` frontmatter, so it does not collide with or violate the shared
`name`/`description` contract.

### 3.4 What "OMP" is, for the record

Distinct from OpenAI Codex. OMP ("oh-my-pi") is the local coding-agent
runtime this session itself is running under (see the workstation
identity line and the `omp://` internal URL scheme available to this
agent). Its skill-loading behavior is documented in a local, non-public
resource at `omp://skills.md`, read directly via the `read` tool per the
assignment's instruction — not a public vendor URL, so no external
citation URL exists for it. All OMP claims in this document are sourced
from that local document, cited as [11] throughout.

---

## 4. C7 — conformance read of the current 19 skills (FINDINGS ONLY, no fixes applied)

Method: parsed the YAML frontmatter block (`---` … `---`) of every
`plugins/proofpunk/skills/*/SKILL.md` with Python's `yaml.safe_load` (via
the `eval` tool), which correctly resolves the folded scalar (`description:
>`) into its single-line, space-joined, chomped string — the same
resolution any real Claude Code/OpenCode YAML frontmatter parser performs.
This measures the **RESOLVED** string per the assignment's instruction, not
a naive newline count of the raw indented lines (spot-checked on 3 files:
naive raw-line-join and YAML-fold-resolved character counts were identical
for the plain-prose bodies in this repo, since none contain embedded
newlines the fold would otherwise collapse differently — folded scalars
replace line breaks with spaces and strip the trailing newline by default
`clip` chomping, confirmed no skill's description ends with `\n`).

All 19 skills use `>` folded-scalar description blocks except none deviate
— every file in this repo follows the identical `name: <slug>` +
`description: >` two-field pattern.

| # | Skill (directory) | `name` field | `name` == dir? | `description` resolved length | ≤1024 (open spec / OpenCode V1 / Claude Skills-API) | ≤1536 combined w/ `when_to_use` (Claude Code local listing budget — no `when_to_use` present, so this column == description length) | Charset OK (`^[a-z0-9]+(-[a-z0-9]+)*$`) | No leading/trailing/consecutive hyphen | XML tags (`<`/`>`) in name or description | Reserved words (`anthropic`/`claude`) in name | Frontmatter fields present (beyond `name`+`description`) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `brainstorm` | `brainstorm` | Yes | 833 | PASS | PASS | PASS | PASS | None | None | none |
| 2 | `codebase-truth-audit` | `codebase-truth-audit` | Yes | 759 | PASS | PASS | PASS | PASS | None | None | none |
| 3 | `end-user-testing` | `end-user-testing` | Yes | 838 | PASS | PASS | PASS | PASS | None | None | none |
| 4 | `full-functional-audit` | `full-functional-audit` | Yes | 811 | PASS | PASS | PASS | PASS | None | None | none |
| 5 | `implement` | `implement` | Yes | 978 | PASS | PASS | PASS | PASS | None | None | none |
| 6 | `mobile-validation-runner` | `mobile-validation-runner` | Yes | 727 | PASS | PASS | PASS | PASS | None | None | none |
| 7 | `plan-hardening` | `plan-hardening` | Yes | 745 | PASS | PASS | PASS | PASS | None | None | none |
| 8 | `production-readiness` | `production-readiness` | Yes | 737 | PASS | PASS | PASS | PASS | None | None | none |
| 9 | `prompt-forge` | `prompt-forge` | Yes | 887 | PASS | PASS | PASS | PASS | None | None | none |
| 10 | `proofpunk` | `proofpunk` | Yes | 718 | PASS | PASS | PASS | PASS | None | None | none |
| 11 | `red-team-eval` | `red-team-eval` | Yes | 761 | PASS | PASS | PASS | PASS | None | None | none |
| 12 | `root-cause-debugging` | `root-cause-debugging` | Yes | 731 | PASS | PASS | PASS | PASS | None | None | none |
| 13 | `session-intent` | `session-intent` | Yes | 805 | PASS | PASS | PASS | PASS | None | None | none |
| 14 | `stack-testing` | `stack-testing` | Yes | 746 | PASS | PASS | PASS | PASS | None | None | none |
| 15 | `tui-testing` | `tui-testing` | Yes | 746 | PASS | PASS | PASS | PASS | None | None | none |
| 16 | `ui-experience-audit` | `ui-experience-audit` | Yes | 807 | PASS | PASS | PASS | PASS | None | None | none |
| 17 | `validation-plan` | `validation-plan` | Yes | 648 | PASS | PASS | PASS | PASS | None | None | none |
| 18 | `visual-inspection` | `visual-inspection` | Yes | 672 | PASS | PASS | PASS | PASS | None | None | none |
| 19 | `completion-summary` | `completion-summary` | Yes | 658 | PASS | PASS | PASS | PASS | None | None | none |

Name length: every `name` value is well under the 64-char ceiling (longest
is `mobile-validation-runner` at 24 chars, `full-functional-audit` at 21).
Not tabulated as a separate column since all 19 pass trivially — the
longest is 24/64.

Description-length distribution: min 649 (`validation-plan`), max 979
(`implement`), mean ≈ 770. **Every one of the 19 is comfortably under the
1024-char open-spec/OpenCode/Claude-Skills-API ceiling** — the closest is
`implement` at 979/1024 (95.6% of budget, 45 chars of headroom) and
`end-user-testing` at 839/1024. None exceed, none are within a rounding
error of overflowing.

Frontmatter-field-outside-recognized-set: **zero** findings. All 19 files
carry exactly `name` + `description` and nothing else — no `license`, no
`compatibility`, no `metadata`, no `allowed-tools`, no Claude-Code-only
extensions (`disable-model-invocation`, `context`, `hooks`, etc.), no OMP
extensions (`hide`, `globs`, `alwaysApply`). This means:

- **Zero risk** of the Claude Code upload/Skills-API hard-fail path (§1.1
  row "Any other unrecognized key"), since the only two fields present are
  exactly the two fields every single host in this canon recognizes.
  These 19 skills would package cleanly for claude.ai upload / Skills API
  as-is, with no field stripping needed.
- **Zero risk** of OpenCode's "unknown fields ignored" silent-drop behavior,
  since there are no unknown fields to drop.
- **No use** of any Claude-Code invocation-control extensions
  (`disable-model-invocation`, `user-invocable`) — every skill in this
  plugin is, per the frontmatter alone, invocable both by the user
  (`/skill-name`) and automatically by Claude, with no skill hidden from
  the model-facing listing. (Note: `agents/implement.md`'s `skills:` array
  lists `implement`, `end-user-testing`, `tui-testing` as *preloaded* into
  that specific subagent — a different mechanism from frontmatter
  `disable-model-invocation`, and out of scope for this file-by-file
  frontmatter table, which covers only the `SKILL.md` files themselves.)

Name/directory match: **18/18 exact matches**, satisfying every host's
name-matches-directory rule (open spec [1], Claude Code local display-name
convention [2], OpenCode's explicit "Validate names" rule [8]) uniformly.

XML-tag and reserved-word scan: **zero hits** across all 36 checked strings
(18 names + 18 descriptions) for `<`, `>`, `anthropic`, or `claude`
(case-insensitive substring check on `name`; the word "Claude" appears
inside **body text**, not frontmatter, in several skills — e.g.
`session-intent`'s body discusses "Claude Code JSONL transcripts" — but
that is body prose, which no host's reserved-word rule restricts; the rule
applies only to the `name` field).

---

## Open / UNRESOLVED

1. **RESOLVED, not actually unresolved** — the XML-tag and reserved-word
   rules for `name`/`description` (§1.2) were independently re-fetched
   verbatim from a second, later-offset `read` of
   `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices`
   (the "YAML Frontmatter" callout box, reached at output lines 175-190 of
   that fetch), not merely inferred from `web_search`. The exact quote is
   reproduced in §1.2 immediately under the two rule rows. This item is
   listed here only to record that the assignment's original ask (verify
   the reserved-word/XML-tag rules) was satisfied with a primary-source
   verbatim citation, superseding an earlier draft of this document that
   understated its own evidence.

2. **Codex's own `SKILL.md` frontmatter field list is not published as a
   discrete "recognized vs ignored" table anywhere found.** [9] and [10]
   both describe `name` and `description` as the two fields Codex reads,
   and describe `agents/openai.yaml` as the separate metadata surface, but
   neither page gives an explicit "these fields are ignored if present in
   SKILL.md frontmatter" statement the way OpenCode's V1 docs do verbatim.
   Row entries for Codex reading `license`/`compatibility`/`metadata`/
   `allowed-tools` in §1.1 are marked "not documented" rather than
   affirmatively "ignored" or "recognized" — this is an honest gap in
   Codex's public documentation, not a gap in this research. Tried:
   reading [9] and [10] in full (both returned complete, non-paginated
   content); searching `developers.openai.com` for a Codex skill-frontmatter
   schema page — none found (site returned no dedicated skills schema page
   under that domain; skill documentation lives entirely under
   `learn.chatgpt.com`).

3. **OMP's exact name-length/charset enforcement (if any) beyond "runtime
   only requires name and path for validity" is not fully specified** in
   the portion of `omp://skills.md` read. The doc states validity
   requirements loosely and does not give a regex or numeric ceiling for
   `name`, unlike the open spec, Claude Code, and OpenCode. Tried: reading
   the entire `omp://skills.md` document across three sequential reads
   (offsets 1–100, 101–160, 161–236, confirmed as the full 236-line
   document by the tool's own "[Showing lines… ]" pagination footer
   disappearing on the final read) and grepping it specifically for
   `valid|regex|lowercase|hyphen|64 char|1024|length` — the only hit was
   the generic "runtime only requires `name` and `path` for validity"
   sentence already quoted in §1.1/§1.2. No numeric length ceiling or
   character-class regex for OMP's `name` field exists in this local
   document as read.

4. **This document does not verify OMP's exact frontmatter field list
   against a second independent source** (e.g. OMP's own source code),
   since the assignment scoped OMP verification to "the LOCAL loader docs
   available via the `read` tool at `omp://` … OR record UNRESOLVED" and
   explicitly said not to invent OMP behavior beyond that. `omp://skills.md`
   was successfully read in full (see item 3), so this is not itself an
   UNRESOLVED item under the assignment's stated fallback condition — it is
   noted here only for completeness, since the task's own contract
   (`evidence/v3-release/00-discovery/a8-canon-opencode.md`) shows that a
   prior agent independently verified OMP-adjacent OpenCode behavior by
   reading OpenCode's actual TypeScript source (`skill/index.ts`) rather
   than relying on docs alone; this document was not asked to, and did not,
   perform the equivalent source-level verification for OMP itself.

5. **`plugins/proofpunk/hooks/hooks.json` hook-COUNT cross-check against
   the work order's stated "11 registrations across 9 distinct scripts"
   was performed opportunistically while reading the file for the event-key
   task (§2.4), and is reported here as a courtesy, not as this document's
   primary deliverable** (the assignment's ground-truth section already
   states this fact as settled; C7's canon task did not ask this document
   to re-derive it). **This item is now stale relative to the current repo
   state and is corrected here rather than deleted, to preserve the audit
   trail.** At the time that cross-check was performed, reading the raw
   file showed 9 distinct script basenames and 11 total hook-handler
   objects, consistent with the work order's then-stated ground truth (11
   registrations / 9 distinct scripts, with `stop-guard.sh` and
   `bash-write-notice.sh` each registered twice). **As measured against the
   current repo (`hooks.json`, 10 hook files under `plugins/proofpunk/hooks/`),
   this has since changed: there are now 12 total hook-handler objects
   across 10 distinct script basenames** (`session-start.sh`,
   `stop-guard.sh` ×2, `no-test-files.sh`, `evidence-guard.sh`,
   `capture-guard.sh`, `bash-write-snapshot.sh`, `instructions-loaded.sh`,
   `post-write-walkthrough.sh`, `bash-write-notice.sh` ×2, and
   `platform-steer.sh` — the added script), registered across the file's 7
   top-level event keys (`SessionStart`, `PreToolUse`, `PostToolUse`,
   `PostToolUseFailure`, `Stop`, `SubagentStop`, `InstructionsLoaded`).
   Canonical totals measured at HEAD `63727e1` (2026-09-14): **12
   registrations, 10 distinct scripts, 11 hook files, 7 event keys, 18
   shared references under `plugins/proofpunk/references/`, and 19
   skills.** (HISTORICAL PROVENANCE: this document was authored at
   `9963648` against 10 hook files, 15 shared references, and 18 skills;
   `completion-summary` became the 19th skill afterwards.
   That drift went unguarded because `verify-counts.py`
   excluded `docs/` wholesale. **Closed 2026-09-14:** the exclusion is now
   scoped to generated assets and dated logs only, so this file's live
   count claims are gated like any other doctrine.)
