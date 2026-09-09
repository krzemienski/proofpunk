# A7 — Skill CANON: Open Agent Skills Standard + Claude Code Plugin Host

STATUS: COMPLETE

Researched 2026-09-06 against live vendor docs (code.claude.com, agentskills.io, platform.claude.com, github.com/agentskills/agentskills, github.com/anthropics/skills). Where a claim came from a web-search synthesis rather than a directly-read doc page, it is marked `[synth]` and cross-checked against a primary fetch where possible.

---

## C1 — Open Agent Skills specification (agentskills.io)

### Canonical source
Primary: `https://agentskills.io/specification` (rendered) and its raw source `https://raw.githubusercontent.com/agentskills/agentskills/main/docs/specification.mdx` (both fetched and cross-checked — text is byte-identical in substance). Repo: `github.com/agentskills/agentskills` (Apache-2.0 code / CC-BY-4.0 docs, 25k stars, originally authored by Anthropic then released as an open standard — confirmed via repo README: "The Agent Skills format was originally developed by Anthropic, released as an open standard, and has been adopted by a growing number of agent products.").

### Directory structure
```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
```
Source: agentskills.io/specification, "Directory structure" section.

### Frontmatter fields (verbatim table from spec)

| Field | Required | Constraints |
|---|---|---|
| `name` | **Yes** | Max 64 characters. Lowercase letters, numbers, and hyphens only. Must not start or end with a hyphen. |
| `description` | **Yes** | Max 1024 characters. Non-empty. Describes what the skill does and when to use it. |
| `license` | No | License name or reference to a bundled license file. |
| `compatibility` | No | Max 500 characters. Indicates environment requirements (intended product, system packages, network access, etc.). |
| `metadata` | No | Arbitrary key-value mapping for additional metadata (a map from string keys to string values). |
| `allowed-tools` | No | Space-separated string of pre-approved tools the skill may use. **(Experimental)** |

Source: agentskills.io/specification, "Frontmatter" table, verbatim.

#### `name` — full constraint list (spec's "#### `name` field" subsection, not just the table row)
- Must be 1–64 characters
- May only contain unicode lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`)
- Must not start or end with a hyphen (`-`)
- Must not contain consecutive hyphens (`--`)
- Must match the parent directory name

Source: agentskills.io/specification §`name` field.

#### `description`
- Must be 1–1024 characters
- Should describe both what the skill does and when to use it
- Should include specific keywords that help agents identify relevant tasks

Source: agentskills.io/specification §`description` field.

#### `license`, `compatibility`, `metadata`, `allowed-tools`
All confirmed as documented above; `compatibility` examples given in the spec: `"Designed for Claude Code (or similar products)"`, `"Requires git, docker, jq, and access to the internet"`, `"Requires Python 3.14+ and uv"`. Spec explicitly notes: "Most skills do not need the `compatibility` field." `allowed-tools` example: `Bash(git:*) Bash(jq:*) Read`. Source: agentskills.io/specification, respective subsections.

### Authoring constraints beyond field presence — XML tags and reserved words

**Finding — this is NOT stated in the open agentskills.io spec text.** I read the full spec page (both rendered and raw `.mdx` source from the GitHub repo) end to end. Neither the frontmatter table nor any subsection mentions an XML-tag ban or a reserved-word ban ("anthropic", "claude"). The open spec's only `name` constraints are the five bullets above.

**These constraints ARE stated — but on a different, Anthropic-controlled surface**: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` (Claude Platform / Claude API docs), §"Skill structure":
> `name`:
> * Maximum 64 characters
> * Must contain only lowercase letters, numbers, and hyphens
> * **Cannot contain XML tags**
> * **Cannot contain reserved words: "anthropic", "claude"**
>
> `description`:
> * Must be non-empty
> * Maximum 1024 characters
> * **Cannot contain XML tags**

This is corroborated by the Claude Code skills doc itself (`code.claude.com/docs/en/skills`), which draws a hard line between the open-spec fields and the stricter set enforced when packaging/uploading outside Claude Code:
> "If you include any field the spec doesn't allow, packaging or upload fails with a hard error instead of ignoring the field: `Unexpected key(s) in SKILL.md frontmatter: argument-hint. Allowed properties are: allowed-tools, compatibility, description, license, metadata, name`"
> — code.claude.com/docs/en/skills, §"Using skill frontmatter outside Claude Code"

**Conclusion for the work order**: XML-tag-ban and reserved-word-ban are real, currently-documented Anthropic-side authoring constraints, but they live on the Claude Platform / Skills API validation surface (`platform.claude.com`), not in the vendor-neutral open standard text at `agentskills.io/specification`. A validator targeting the *open standard only* has no textual basis to enforce them; a validator targeting Claude API/Platform skill uploads (the `package_skill.py` / Skills API path) must enforce them. Claude Code itself (the plugin host, C2) accepts all six spec fields plus many Claude-Code-only extensions and does not document its own separate XML/reserved-word check — see C2 below.

### Progressive disclosure — three-tier model (verbatim from spec)
1. **Metadata** (~100 tokens): the `name` and `description` fields are loaded at startup for all skills.
2. **Instructions** (< 5000 tokens recommended): the full `SKILL.md` body is loaded when the skill is activated.
3. **Resources** (as needed): files (e.g. those in `scripts/`, `references/`, or `assets/`) are loaded only when required.

"Keep your main `SKILL.md` under 500 lines. Move detailed reference material to separate files."

Source: agentskills.io/specification §"Progressive disclosure", verbatim.

Cross-check against `platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` (Claude API architecture doc) — same three-level model, same numbers, with an added table column for "Token cost": Level 1 ≈100 tokens/skill, Level 2 <5k tokens, Level 3+ "None until accessed." Consistent, no contradiction found.

### File-reference rules
> "When referencing other files in your skill, use relative paths from the skill root... Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains."

Source: agentskills.io/specification §"File references", verbatim.

### Validation tooling — DOES exist
> "Use the [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) reference library to validate your skills: `skills-ref validate ./my-skill` — This checks that your `SKILL.md` frontmatter is valid and follows all naming conventions."

Source: agentskills.io/specification §"Validation", verbatim. The `skills-ref` tool lives inside the same `agentskills/agentskills` monorepo I fetched (confirmed repo exists, Python-language repo per GitHub metadata; did not open the `skills-ref` subdirectory source itself — flagged `[UNVERIFIED: did not inspect skills-ref implementation, only its documented existence and invocation]`).

### Drift check: local copy at `~/.claude/skills/agent_skills_spec.md` vs live spec

I read the local file in full (23 non-blank content lines, "Version History: 1.0 (2025-10-16) Public Launch"). **Verdict: the local copy is stale and materially incomplete relative to the current live spec.** Specific drift, each independently verifiable by diffing local file text against the agentskills.io text quoted above:

| # | Local file says (`~/.claude/skills/agent_skills_spec.md`) | Live spec says | Drift |
|---|---|---|---|
| 1 | `name`: "Restricted to lowercase Unicode alphanumeric + hyphen" — **no max-length stated anywhere in the file** | `name`: max 64 characters (stated twice, in the table and in the field subsection) | Local file omits the 64-char cap entirely |
| 2 | `name`: no mention of leading/trailing hyphen or consecutive-hyphen rules | `name`: "Must not start or end with a hyphen", "Must not contain consecutive hyphens (`--`)" | Local file omits 2 of 5 `name` constraints |
| 3 | Optional properties listed: `license`, `allowed-tools`, `metadata` — **exactly 3** | Optional properties: `license`, `compatibility`, `metadata`, `allowed-tools` — **4** | Local file is missing the entire `compatibility` field (max 500 chars, environment requirements) |
| 4 | No mention of progressive disclosure, file-reference rules, or a validation tool | Live spec documents all three as first-class sections | Local file predates (or never captured) these sections |
| 5 | No mention of XML-tag ban or reserved-word ban | Not in the open spec either (see finding above) — so no drift here, both agree by omission | N/A — consistent |

**Recommendation for the repo**: `~/.claude/skills/agent_skills_spec.md` should be regenerated from `agentskills.io/specification` (or `raw.githubusercontent.com/agentskills/agentskills/main/docs/specification.mdx`) to pick up the `compatibility` field and the three missing `name` constraints. This file is outside `/Users/nick/proofpunk` (it is a personal `~/.claude/skills/` file, not a repo-tracked file), so it is out of scope for a proofpunk commit, but is flagged per the work order's explicit instruction to "read it, but verify against the live spec and record any drift."

---

## C2 — Claude Code as a plugin host

Primary sources: `https://code.claude.com/docs/en/plugins-reference` (plugin manifest, components, hooks summary), `https://code.claude.com/docs/en/hooks` (hooks reference, full 30-event table + decision-control table), `https://code.claude.com/docs/en/skills` (skill discovery, frontmatter reference, `allowed-tools` semantics), `https://code.claude.com/docs/en/sub-agents` (subagent frontmatter), `https://code.claude.com/docs/en/plugin-marketplaces` (marketplace schema).

### Skill discovery in a plugin (auto-discovery, `skills` manifest field, root-`SKILL.md` fallback)

All three claims in the work order are confirmed verbatim from `plugins-reference`:

> "**Location**: `skills/` or `commands/` directory in plugin root, or a single `SKILL.md` file at the plugin root ... Skills and commands are automatically discovered when the plugin is installed."

> "If a plugin has no `skills/` directory and no `skills` manifest field, a `SKILL.md` at the plugin root is loaded as a single skill. Set the frontmatter `name` field to control the skill's invocation name. Without it, Claude Code falls back to the install directory name, which for marketplace-installed plugins is a version string that changes on every update. For plugins that ship more than one skill, use the `skills/` directory layout shown above."

Source: code.claude.com/docs/en/plugins-reference, §"Skills" under "Plugin components reference" — this is a single verbatim paragraph containing both the fallback rule and the critical `name`-must-be-explicit warning.

On the `skills` manifest field specifically — **"unnecessary, and a custom path only overrides discovery" is not quite the live behavior; it is more precise to say the custom path *adds to* the default, it does not replace it**, per the "Path behavior rules" table in `plugins-reference`:

> "**Adds to the default**: `skills`. The default `skills/` directory is always scanned, and directories listed in `skills` are loaded alongside it. **Exception**: for a marketplace entry whose `source` resolves to the marketplace root, declaring specific subdirectories replaces the default `skills/` scan"

So: setting `skills` in `plugin.json` never *disables* the default `skills/` directory scan (it only adds more directories) — except in the one documented "marketplace-root source" exception. The work order's phrasing "a custom path only overrides discovery" is directionally true (it does not replace default discovery in the ordinary case) but the precise mechanic is additive-by-default. Recorded as a nuance, not a contradiction.

**Local repo cross-check**: `plugins/proofpunk/.claude-plugin/plugin.json` (read in full) has **no `skills` field at all** — confirmed by inspection, only `name`, `version`, `description`, `author`, `license`, `keywords` are present (`plugins/proofpunk/.claude-plugin/plugin.json:1-61`). This means proofpunk relies entirely on default `skills/` directory discovery, consistent with the 18-skill count the orchestrator measured on disk.

### Full `plugin.json` manifest schema

Complete schema (verbatim example) from `plugins-reference` §"Plugin manifest schema":

```json
{
  "name": "plugin-name",
  "displayName": "Plugin Name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": { "name": "Author Name", "email": "author@example.com", "url": "https://github.com/author" },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/author/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "metadata": { "catalogId": "cat-123", "tier": "pro" },
  "skills": "./custom/skills/",
  "commands": ["./custom/commands/special.md"],
  "agents": ["./custom/agents/reviewer.md"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./mcp-config.json",
  "outputStyles": "./styles/",
  "lspServers": "./.lsp.json",
  "experimental": { "themes": "./themes/", "monitors": "./monitors.json" },
  "dependencies": ["helper-lib", { "name": "secrets-vault", "version": "~2.1.0" }]
}
```

**Required field**: only `name` ("If you include a manifest, `name` is the only required field."). `name` must be "Unique identifier in kebab-case, with no spaces, control characters, or bidirectional-formatting characters."

Additional fields not in the example block but documented in the same page's tables: `userConfig` (object — user-configurable values prompted at enable time), `channels` (array — message-channel declarations, e.g. Telegram/Slack/Discord bindings to a bundled MCP server), `defaultEnabled` (boolean, default `true` — whether the plugin installs enabled), `$schema` (string, ignored at load time, editor-autocomplete only).

Unrecognized top-level fields are **ignored, not rejected**: "Claude Code ignores top-level fields it does not recognize... `claude plugin validate` reports unrecognized fields as warnings, not errors... Pass `--strict` to treat warnings as errors."

Source: code.claude.com/docs/en/plugins-reference §"Plugin manifest schema" (Complete schema / Required fields / Metadata fields / Component path fields / Unrecognized fields subsections), all verbatim.

**Local repo cross-check**: `plugins/proofpunk/.claude-plugin/plugin.json` sets `name`, `version`, `description`, `author`, `license`, `keywords` — all recognized fields, no custom component paths, no `userConfig`/`channels`/`defaultEnabled`. No schema violations found by inspection.

### Plugin-agent frontmatter fields

Confirmed verbatim, and matches the work order's list **exactly**, field for field:

> "Plugin agents support `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, and `isolation` frontmatter fields. **The only valid `isolation` value is `"worktree"`.** For security reasons, `hooks`, `mcpServers`, and `permissionMode` are not supported for plugin-shipped agents."

Source: code.claude.com/docs/en/plugins-reference §"Agents" under "Plugin components reference", verbatim.

Additional behavior worth recording: a plugin agent loads **even when its frontmatter has no `name` or fails to parse** (unlike project/user/managed agents, which are skipped in that case):
> "No `name`: Claude Code names the agent after the file, so `agents/reviewer.md` in a plugin named `my-plugin` loads as `my-plugin:reviewer`. Frontmatter that doesn't parse: Claude Code names the agent after the file, uses `Agent from my-plugin plugin` as its description, and ignores every field in the file."

Source: same section, verbatim. `claude plugin validate ./my-plugin` (or `./my-plugin/agents` for a manifest-less plugin, requires v2.1.233+) finds agent files whose frontmatter doesn't parse.

**Local repo cross-check**: proofpunk manifest count of "3 agents" measured by the orchestrator was not independently re-verified by this lane (out of scope — A3/A2 own agent counts); no plugin.json `agents` custom path override present, so default `agents/` directory discovery applies.

### Marketplace schema

Confirmed from `code.claude.com/docs/en/plugin-marketplaces` §"Marketplace schema":

**Required top-level fields**: `name` (string, kebab-case marketplace identifier, public-facing), `owner` (object), `plugins` (array). Verbatim: "| `name` | string | Marketplace identifier in kebab-case... | | `owner` | object | Marketplace maintainer information | | `plugins` | array | List of available plugins |"

**`owner` fields**: `name` (string, **required**), `email` (string, optional), `url` (string, optional).

**Per-plugin entry required fields**: `name` (string, kebab-case, public-facing install identifier) and `source` (string|object — where to fetch the plugin). Verbatim: "Each plugin entry needs at minimum a `name` and a `source`."

**Optional per-plugin fields** (partial, matches work order's ask about `strict`): `displayName`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`, `metadata`, `category`, `tags`, `strict`, `relevance`, `defaultEnabled`, `headers`, `headersHelper`, plus component-config overrides (`skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`).

**What `strict` controls** (direct quote, this is the only sentence the docs give for this field on the marketplace-entry table — I did not open the full "Strict mode" subsection body, flagged below): "`strict` | boolean | Controls whether `plugin.json` is the authority for component definitions (default: `true`). See [Strict mode](#strict-mode) below." `[UNVERIFIED: full mechanics of the linked "Strict mode" subsection body were not fetched — only the one-line summary from the field table was read. The summary is sourced and quoted verbatim; the deeper mechanic (what changes when `strict: false`) was not independently confirmed in this pass.]`

Also confirmed: **reserved marketplace names** exist and are enforced — `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `claude-plugins-community`, `claude-community`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `anthropic-agent-skills`, `knowledge-work-plugins`, `life-sciences`, `claude-for-legal`, `claude-for-financial-services`, `financial-services-plugins`, `first-party-plugins`, `healthcare` — "reserved for official Anthropic use and can't be used by third-party marketplaces." (Note: this is a **marketplace-name** reservation, distinct from the platform.claude.com **skill-`name`** reserved-word rule in C1 — different surfaces, different lists, do not conflate.)

Source: code.claude.com/docs/en/plugin-marketplaces §"Marketplace schema", "Required fields", "Optional fields", "Plugin entries" subsections, verbatim.

**Local repo cross-check**: `.claude-plugin/marketplace.json` (read in full) has `name: "proofpunk-marketplace"`, `owner: {name: "Proofpunk maintainers"}`, `metadata: {description, version, pluginRoot}`, `plugins: [{name: "proofpunk", source: "./plugins/proofpunk", description, version, license, keywords, category}]` — no `strict` field set on the single plugin entry (so it defaults to `true`), no reserved-name collision (`proofpunk-marketplace` is not on the reserved list), one plugin entry, `source` is a relative path starting with `./` as required. No schema violations found by inspection.

---

### THE 7 EVENT KEYS — supported/unsupported/unknown verdict for each

Ground truth: `plugins/proofpunk/hooks/hooks.json` (repo file, read in full, 116 lines). Cross-checked against **two independently-fetched current pages** that both carry the identical, complete 30-row hook-event table: `code.claude.com/docs/en/hooks` (main hooks reference) and `code.claude.com/docs/en/plugins-reference` (§"Hooks" under "Plugin components reference" — this page reproduces the *exact same* 30-row table verbatim as its own "Plugin hooks respond to the same lifecycle events as user-defined hooks" section, confirming plugin hooks are not a restricted subset of the general hook-event set).

| # | Event key (local `hooks.json:line`) | Verdict | Evidence |
|---|---|---|---|
| 1 | `SessionStart` (`hooks.json:4`) | **SUPPORTED** | Row in both current event tables: "Fires when a session begins or resumes." Has documented decision control (`additionalContext`, `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills`). |
| 2 | `Stop` (`hooks.json:16`) | **SUPPORTED** | Row in both current event tables: "When Claude finishes responding." Decision control: top-level `decision: "block"` + `reason`, per the decision-control table row "UserPromptSubmit, UserPromptExpansion, PostToolUse, PostToolUseFailure, PostToolBatch, **Stop**, SubagentStop, ConfigChange, PreCompact — Top-level `decision`". |
| 3 | `SubagentStop` (`hooks.json:27`) | **SUPPORTED** | Row in both current event tables: "When a subagent finishes." Same top-level-`decision` control class as `Stop` (same table row). |
| 4 | `PreToolUse` (`hooks.json:38`) | **SUPPORTED** | Row in both current event tables: "Before a tool call executes. Can block it." Decision control: `hookSpecificOutput.permissionDecision` (`allow`/`deny`/`ask`/`defer`) + `permissionDecisionReason`, plus `updatedInput` to rewrite tool arguments. |
| 5 | `InstructionsLoaded` (`hooks.json:70`) | **SUPPORTED — and explicitly documented in full, not renamed, not deprecated.** | Row in both current event tables: "When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session." **Dedicated subsection exists** in `code.claude.com/docs/en/hooks` §"InstructionsLoaded" (lines 1268–1301 of the fetched page) documenting its input schema (`file_path`, `memory_type`, `load_reason`, `globs`, `trigger_file_path`, `parent_file_path`) and its matcher (`load_reason` values: `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact`). **Decision control: NONE.** Verbatim: "The hook doesn't support blocking or decision control. It runs asynchronously for observability purposes." / "InstructionsLoaded hooks have no decision control. They can't block or modify instruction loading. Claude Code discards their JSON output fields, such as `systemMessage` and `continue`. Use this event for audit logging, compliance tracking, or observability." This matches the proofpunk hook's own stated purpose (a doctrine-injection/context hook, fire-and-observe) — the event has zero blocking power by design, so a hook attached to it structurally cannot enforce anything, only log/inject-context. |
| 6 | `PostToolUse` (`hooks.json:81`) | **SUPPORTED** | Row in both current event tables: "After a tool call succeeds." Decision control: top-level `decision: "block"` (same class-row as `Stop`/`SubagentStop` above) which halts the *turn*, plus a `PostToolUse`-specific `updatedToolOutput` field that can rewrite the tool's result. **It has no `permissionDecision` field and cannot appear in `hookSpecificOutput.permissionDecision`** — that mechanism is `PreToolUse`-only per the decision-control table. See dedicated PostToolUse-cannot-deny finding below. |
| 7 | `PostToolUseFailure` (`hooks.json:103`) | **SUPPORTED — not renamed.** | Row in both current event tables: "After a tool call fails." Same top-level-`decision`-block class as `PostToolUse`/`Stop`/`SubagentStop` (explicitly listed together in the single decision-control table row: "UserPromptSubmit, UserPromptExpansion, PostToolUse, **PostToolUseFailure**, PostToolBatch, Stop, SubagentStop, ConfigChange, PreCompact — Top-level `decision`"). |

**Bottom line for the work order's single most important output: all 7 event keys currently present in `plugins/proofpunk/hooks/hooks.json` are current, documented, supported Claude Code hook event names as of the live docs fetched 2026-09-06. None are renamed. None are deprecated. None are unknown/unverifiable.** The two keys flagged by the work order as "most likely to be unsupported or renamed" (`InstructionsLoaded`, `PostToolUseFailure`) are in fact both fully documented with their own dedicated subsections and explicit decision-control classifications — they are not edge cases in the current docs, they are first-class, well-specified events.

### `PostToolUse` cannot deny — confirmed, with the precise mechanism

The work order asks to "Confirm `PostToolUse` cannot deny." **Confirmed, precisely**, from the decision-control reference table in `code.claude.com/docs/en/hooks` §"Decision control":

- The only event/field pair that can produce an `allow`/`deny`/`ask`/`defer` **permission** decision is `PreToolUse`, via `hookSpecificOutput.permissionDecision`. This is the single row in the table for that field: "PreToolUse | `hookSpecificOutput` | `permissionDecision` (allow/deny/ask/defer), `permissionDecisionReason`".
- `PostToolUse` fires "after a tool call succeeds" — by definition, the call has already executed, so there is nothing left to permission-gate. Its only control channel is the shared top-level `decision: "block"` field (same class as `Stop`), which — per the field's own documented semantics — "prevents the prompt from being processed" *for other events* but for `PostToolUse` its documented effect is: "Takes effect even when the tool call fails or completes while Claude is still streaming a response" and halts the *turn*, not the *call*. There is no `PostToolUse`-specific `permissionDecision` field anywhere in the schema.
- `PostToolUse` additionally supports `updatedToolOutput` (rewriting the already-produced result) but this is explicitly a *rewrite*, not a *denial*: "`PostToolUse`: `updatedToolOutput` replaces the tool's result... For redaction or transformation use cases, intercept at PreToolUse for outbound tool inputs and PostToolUse for inbound tool results."

**Conclusion: `PostToolUse` genuinely cannot deny/prevent a tool call — this is confirmed by the schema itself having no `permissionDecision` option for that event, not merely by prose description.** Third-party blog synthesis (`developersdigest.tech`, `scalably.io`, etc., surfaced during a web search) describes this identically: "Unlike PreToolUse, it can't prevent the call — it reacts to what already happened. If a tool call needs to be prevented... it must be caught by a PreToolUse hook." That is consistent with the primary-source schema table above.

### Settings.json hook-merge semantics

Confirmed from `code.claude.com/docs/en/hooks` §"Hook locations" and §"Disable or remove hooks":

- **Merge, not replace, across settings levels**: "Hooks from settings files, managed policy settings, and plugins also run inside subagents." / "Hook entries merge across settings levels rather than replacing each other: user, project, and local settings add their own hooks without removing managed ones, and the `disableAllHooks` setting can't disable managed hooks from outside managed settings."
- **Plugin hooks merge in when the plugin is enabled**: "When a plugin is enabled, its hooks merge with your user and project hooks." (from the "Plugin scripts" tab example under §"Reference scripts by path").
- **Identical-handler dedup**: "All matching hooks run in parallel. If you define the same handler in more than one settings file, it runs once. A plugin's or skill's copy of the same handler stays separate." — i.e. dedup is by exact-handler-definition-in-the-same-settings-file scope, and a plugin's copy of an otherwise-identical handler is treated as a distinct instance from a user/project settings copy (so it is NOT deduped against a user's manually-configured identical hook).
- **Precedence hierarchy for locations**: `~/.claude/settings.json` (all projects) < `.claude/settings.json` (project, committable) < `.claude/settings.local.json` (project, gitignored) < managed policy settings (org-wide, admin-controlled) < plugin `hooks/hooks.json` (when enabled) < skill/subagent frontmatter hooks (session-scoped, cleared on skill/subagent exit or with `once: true`) — all six sources documented in one table, code.claude.com/docs/en/hooks §"Hook locations".
- **`disableAllHooks`**: a boolean settings-file toggle that disables all hooks *except managed-tier hooks*, with normal settings-precedence resolution (a project-level `false` can override a user-level `true`).

Source: code.claude.com/docs/en/hooks §"Hook locations" and §"Disable or remove hooks", verbatim/paraphrase as quoted.

### `allowed-tools` — is it enforced at runtime?

**Yes, but as a pre-approval grant, not a hard sandbox/restriction.** This is a nuance the work order should note precisely. From `code.claude.com/docs/en/skills` §"Frontmatter reference" table (verbatim):

> `allowed-tools`: "Tools Claude can use **without asking permission** during the turn that invokes this skill. **The grant clears when you send your next message.** Accepts a space- or comma-separated string, or a YAML list."

This is corroborated by a separate section, §"Restrict Claude's skill access": "Skills that define `allowed-tools` grant Claude access to those tools **without per-use approval** during the turn that invokes the skill; the grant clears when you send your next message. **Your permission settings still govern baseline approval behavior for all other tools.**"

So the mechanism is: `allowed-tools` **is** enforced at runtime, in the specific sense that Claude Code's permission-prompt system checks it and skips the prompt for listed tool-invocations during the invoking turn — this is a real, live, per-turn grant, not a no-op. But it is **not** a restriction ("only these tools may run") — that job belongs to the separate, distinct field `disallowed-tools`: "Tools **removed** from Claude's available pool while this skill is active... The restriction clears when you send your next message." `allowed-tools` = allow-list grant (permission bypass); `disallowed-tools` = deny-list restriction (tool pool removal). These are two different fields with two different enforcement directions, and the work order's phrasing ("whether `allowed-tools` is enforced at runtime") maps to the *grant* semantics, which is confirmed enforced.

At the **open-standard level** (agentskills.io), the field is marked "Experimental. Support for this field may vary between agent implementations" — i.e. the spec itself disclaims any enforcement guarantee across non-Claude-Code implementations. Claude Code's own enforcement (the permission-bypass grant described above) is a Claude-Code-specific, fully-specified behavior layered on top of that experimental spec field.

---

## Corrections owed to `plugins/proofpunk/docs/invocation-contracts.md`

Read in full (29 lines). Comparing its claims against everything fetched above:

1. **Stale source domain in its own citations.** Its "Sources" section (line 19) cites `https://docs.anthropic.com/en/docs/claude-code/skills · /plugins · /plugins-reference · /hooks · /sub-agents · /memory`. Every one of these topics now canonically resolves at `code.claude.com/docs/en/*` (confirmed: all primary fetches in this report used `code.claude.com/docs/en/{skills,plugins-reference,hooks,sub-agents,plugin-marketplaces}` and returned current, actively-versioned content referencing Claude Code v2.1.190–v2.1.26x). `docs.anthropic.com/en/docs/claude-code/*` is very likely a legacy/redirected domain at this point; the file should be updated to cite `code.claude.com/docs/en/*` directly. `[UNVERIFIED: did not fetch docs.anthropic.com/en/docs/claude-code/* directly to confirm it 404s or redirects — flagging as a citation-domain concern based on the fact that every current doc I fetched lives at code.claude.com, not that the old URL is provably dead.]`
2. **Its Trigger-owners table row "Hooks (hard guarantee)" is accurate as a general claim but incomplete against the current, much richer decision-control matrix.** The file's own caveat at the bottom ("hard guarantees live only in blocking decisions (PreToolUse deny, Stop block)") is directionally correct but out of date: the current docs show a *third* blocking class exists beyond "PreToolUse deny" and "Stop block" — the shared top-level `decision: "block"` class that also covers `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `SubagentStop`, `ConfigChange`, and `PreCompact` (9 events, not 2). This should be corrected/expanded, not because the file is wrong, but because it materially understates how many events actually support blocking.
3. **Its "Plugin = ship unit" row for Claude Code** ("skills+agents+hooks+MCP all activate on enable") omits two component types that current docs confirm also activate on plugin enable: **LSP servers** and **background Monitors** (both documented as first-class plugin components in `plugins-reference` §"LSP servers" / §"Monitors"). Not a contradiction, but an incompleteness worth folding in given the file explicitly enumerates component types.
4. **No factual contradiction found** regarding subagent frontmatter fields, `paths:` lazy-loading of CLAUDE.md/rules, or the general skill-discovery-vs-agent-discovery distinction — those rows check out against the current docs fetched in this pass.

---

## Open questions / things not independently verified in this pass

- Full mechanics of marketplace-entry `strict: false` (only the one-line table summary was fetched, not the linked "Strict mode" subsection body). `[UNVERIFIED]`
- Whether `docs.anthropic.com/en/docs/claude-code/*` (the domain cited in the local invocation-contracts.md) currently 404s, redirects, or still serves stale content — not fetched directly. `[UNVERIFIED]`
- The internal implementation of the `skills-ref` validator tool referenced by the open spec (confirmed the tool is documented and named; did not open its source to confirm exact enforced rules match the prose spec 1:1). `[UNVERIFIED]`

---

STATUS: COMPLETE
