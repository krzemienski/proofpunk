# Claude Code Platform Documentation Digest (for proofpunk v4)

Authoritative digest of official Anthropic Claude Code documentation, fetched from `https://docs.claude.com/en/docs/claude-code/` (redirects to `code.claude.com/docs/en/...`) on 2026-09-09. Every claim below cites the specific doc page it came from. This digest exists to ground proofpunk v4 architecture decisions in what the platform *actually* supports today, not in assumption or v3-era memory.

---

## 1. Plugins (structure, marketplace, installation)

Source: https://docs.claude.com/en/docs/claude-code/plugins ("Create plugins"), https://docs.claude.com/en/docs/claude-code/plugin-marketplaces ("Create and distribute a plugin marketplace")

### What a plugin is, today
A plugin is a self-contained directory of skills, agents, hooks, MCP servers, or LSP servers, optionally with a `.claude-plugin/plugin.json` manifest. There are two ways to add custom functionality: **standalone** (`.claude/` directory in a project — commands are unnamespaced, e.g. `/hello`) or **plugin** (namespaced, e.g. `/plugin-name:hello`, shareable via marketplace). [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)

### Manifest and layout — exact locations
- `.claude-plugin/plugin.json` — the manifest. **Only** `plugin.json` goes inside `.claude-plugin/`. Everything else (`skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`, `.lsp.json`, `monitors/`, `bin/`, `settings.json`) lives at the **plugin root**, a sibling of `.claude-plugin/`, never inside it. This is called out explicitly as "Common mistake" in the docs. [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- `plugin.json` required fields: none are strictly required beyond what the schema implies, but the documented core fields are `name` (unique identifier + skill namespace), `description` (shown in plugin manager), `version` (optional; gates whether users get updates when bumped — except for `command`-source plugins), `author` (optional). [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- Directory table (from [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)):
  | Directory | Location | Purpose |
  |---|---|---|
  | `.claude-plugin/` | Plugin root | `plugin.json` manifest |
  | `skills/` | Plugin root | Skills as `<name>/SKILL.md` |
  | `commands/` | Plugin root | Skills as flat `.md` files (legacy form; prefer `skills/`) |
  | `agents/` | Plugin root | Custom agent definitions |
  | `hooks/` | Plugin root | Event handlers in `hooks.json` |
  | `.mcp.json` | Plugin root | MCP server configs |
  | `.lsp.json` | Plugin root | LSP server configs |
  | `monitors/` | Plugin root | Background monitor configs in `monitors.json` |
  | `bin/` | Plugin root | Executables added to Bash tool's `PATH` while plugin enabled (cannot be included in orgs-distributed plugins) |
  | `settings.json` | Plugin root | Default settings applied when plugin enabled — **only `agent` and `subagentStatusLine` keys are currently supported** |
- A plugin shipping exactly one skill can place `SKILL.md` directly at plugin root (no `skills/` dir needed); Claude Code uses the frontmatter `name` for the invocation name. [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- **Skills-directory plugins**: a skill folder under `~/.claude/skills/` or a project's `.claude/skills/` can itself carry a `.claude-plugin/plugin.json` and load as a full plugin named `<name>@skills-dir` — so it can bundle agents/hooks/MCP servers. In a project's `.claude/skills/`, this requires the workspace-trust dialog first. `claude plugin init my-tool` scaffolds this pattern into `~/.claude/skills/my-tool/`. [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)

### Testing locally
`claude --plugin-dir ./my-plugin` loads a plugin directly for one session without installing it — accepts a directory or a `.zip` archive, and can be repeated to load multiple plugins at once. `--plugin-url <url>` fetches and loads a `.zip` archive hosted at a URL, for that session only. `/reload-plugins` picks up plugin changes (skills, agents, hooks, plugin MCP/LSP servers) without a restart; in a non-interactive session, plugin MCP server changes wait for the next session. [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)

### Marketplaces — the distribution mechanism
A **plugin marketplace** is a catalog file, `.claude-plugin/marketplace.json`, at a repository root, listing plugins and where to fetch each from. [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)

Required top-level fields: `name` (kebab-case, public-facing identifier used as `@marketplace-name` in install commands; **reserved names** exist for Anthropic use, e.g. `claude-plugins-official`, `claude-plugins-community`, `claude-community`), `owner` (object with `name` required, `email`/`url` optional), `plugins` (array). Optional: `$schema`, `description`, `version`, `metadata.pluginRoot` (base dir for bare-name plugin sources, requires v2.1.239+), `allowCrossMarketplaceDependenciesOn`, `renames` (map old-name → new-name/null for migration, requires v2.1.193+). [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)

Each plugin entry requires `name` and `source`. `source` can be: a relative path string (`"./plugins/my-plugin"`, resolved against the marketplace root — the directory containing `.claude-plugin/`, **not** where `marketplace.json` sits), or an object with type `github` (`repo`, `ref?`, `sha?`), `url` (git URL, `ref?`, `sha?`), `git-subdir` (sparse clone of a monorepo subdir: `url`, `path`, `ref?`, `sha?`), `npm` (`package`, `version?`, `registry?`), `archive` (zip over HTTPS, `url`, `sha256?`, requires v2.1.224+), or `command` (a local command that produces a plugin directory, re-run once per session, requires v2.1.229+). When both `ref` and `sha` are set on a git-based source, `sha` is the effective pin. [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)

Installed plugins are copied into `~/.claude/plugins/cache` (a **local versioned plugin cache**) except for `command`-source plugins in "link mode," which are used in place. Copied plugins **cannot reference files outside their own directory** (e.g. `../shared-utils`) because those files aren't copied — share files via symlinks instead. [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)

### Install flow (from the marketplace walkthrough) [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)
```
/plugin marketplace add ./my-marketplace       # or a github repo, git URL, etc.
/plugin install quality-review-plugin@my-plugins
/reload-plugins                                 # if the install summary says to
```
Plugin skills are namespaced: `/plugin-name:skill-name`.

Two official public marketplaces exist and are documented: `claude-plugins-official` (curated by Anthropic, auto-registered on first interactive launch) and `claude-community` (community submissions after review, added via `/plugin marketplace add anthropics/claude-plugins-community`). Submission is via a web form (claude.ai admin settings or platform.claude.com), gated by `claude plugin validate ./your-plugin` passing locally first. [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)

### What a plugin CAN control (confirmed by docs)
- Skills (auto-invoked or user-invoked, namespaced) [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins), [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)
- Custom subagents, in an `agents/` directory, recursively scanned; subfolders become part of the scoped identifier (e.g. `agents/review/security.md` in `my-plugin` → `my-plugin:review:security`) [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)
- Hooks, via `hooks/hooks.json`, merged with user/project hooks — **but plugin subagents cannot carry their own `hooks`, `mcpServers`, or `permissionMode` frontmatter fields; those are silently ignored for security reasons** [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents) [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)
- MCP servers (`.mcp.json`) and LSP servers (`.lsp.json`) [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- Background monitors (`monitors/monitors.json`) that watch logs/files and push notifications into the session automatically — no explicit "start watching" instruction needed [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- One default-active "main-thread persona": `settings.json` at plugin root can set `"agent": "<name>"` to make one of the plugin's own custom agents become the main session's system prompt/tools/model when the plugin is enabled [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)

### What a plugin CANNOT control (confirmed gaps/exclusions)
- Cannot place non-manifest directories (`skills/`, `hooks/`, etc.) inside `.claude-plugin/` — explicitly called a common mistake [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- Plugin `settings.json` supports **only** `agent` and `subagentStatusLine` keys today — no other settings can be shipped as plugin defaults [Plugins docs](https://docs.claude.com/en/docs/claude-code/plugins)
- Plugin subagents cannot ship `hooks`, `mcpServers`, or `permissionMode` in their own frontmatter (silently ignored) — a workaround is to copy the agent file into `.claude/agents/` or `~/.claude/agents/` instead [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)
- A plugin distributed through **organization settings** (managed distribution) is restricted to a subset of source types (not detailed exhaustively here; see "Distribute through organization settings" section of [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces), not fully fetched in this session — flagged in Gaps)
- Copied (non-link-mode) plugins cannot reach files outside their own plugin directory [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces)

---

## 2. Skills (SKILL.md spec, frontmatter, progressive disclosure)

Source: https://docs.claude.com/en/docs/claude-code/skills ("Extend Claude with skills")

### The model
A skill is a `SKILL.md` file (YAML frontmatter + markdown body). Claude either auto-invokes it based on `description` matching the conversation, or the user types `/skill-name`. Skills follow the open **Agent Skills** standard (agentskills.io); Claude Code extends it with invocation control, subagent execution (`context: fork`), and dynamic context injection. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

**Custom commands have been merged into skills** as of the current docs generation: a file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both produce `/deploy` and behave the same; old `.claude/commands/` files still work but skills add supporting-file directories, invocation-control frontmatter, and auto-loading. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Exact file locations and load scope (table from [Skills docs](https://docs.claude.com/en/docs/claude-code/skills))
| Location | Path | Loads in |
|---|---|---|
| Enterprise | `.claude/skills/<name>/SKILL.md` inside managed settings dir | All users on org-managed machines |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All projects on this machine, **not** Cowork/cloud sessions |
| Project | `.claude/skills/<name>/SKILL.md` | This repo; commit to share with team |
| Nested | `<subdir>/.claude/skills/<name>/SKILL.md` | Sessions started in/below `<subdir>`; loads lazily the first time Claude touches a file there (or via `/add-dir`, v2.1.257+) |
| Additional directory | `.claude/skills/<name>/SKILL.md` in a `--add-dir` dir | That session only |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Wherever plugin is enabled, as `/plugin-name:skill-name` |
| claude.ai account | Skills enabled in claude.ai settings | Cowork/cloud sessions; local sessions only after explicit sync opt-in |

Name-collision precedence: enterprise > personal > project. A local skill overrides a same-named **bundled** skill but not that bundled skill's aliases. Nested and root skills with the same name both remain invocable (root wins the bare name; nested gets a directory-qualified variant like `/apps/web:deploy`). Plugin skills never collide because they're always namespaced. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

Cloud sessions (Claude Code on the web, routines) do **not** read `~/.claude/skills/` — only project skills committed to the cloned repo's `.claude/skills/`, or skills the user's claude.ai account has enabled. This is a hard architectural constraint for anything proofpunk v4 wants to run in cloud/routine contexts. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Live change detection
Claude Code watches skill directories for file changes (except in `--bare` mode) and picks up edits within the current session **without restart** — but this covers `SKILL.md` text only. A skill folder that is also a plugin needs `/reload-plugins` for changes to `hooks/`, `.mcp.json`, `agents/`, `output-styles/`. Three cases still need a full restart: the watcher only covers directories that existed at session start (so the very first skill in a brand-new `agents`/`skills` directory needs a restart); `--add-dir` directories' `.claude/skills/` are watched, but not their `.claude/commands/`/`.claude/agents/`; and `--disable-slash-commands` sessions don't watch at all. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills), [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Full frontmatter field reference (from [Skills docs](https://docs.claude.com/en/docs/claude-code/skills))
All fields optional; only `description` is *recommended*.
| Field | Notes |
|---|---|
| `name` | Display name; for personal/project skills only affects listing label (invocation name comes from directory name); for plugin skills sets the final command segment |
| `description` | What/when; truncated at 1,536 chars combined with `when_to_use` in the skill listing shown to Claude |
| `when_to_use` | Extra trigger-phrase context, appended to description, counts toward the 1,536-char cap |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]` |
| `arguments` | Named positional args for `$name` substitution |
| `disable-model-invocation` | `true` → only the user can invoke via `/name`; Claude cannot auto-invoke. Also blocks preloading into subagents and blocks scheduled-task auto-fire |
| `user-invocable` | `false` → hidden from `/` menu and can't be typed; only Claude can invoke it (for background knowledge, not actions) |
| `allowed-tools` | Tools pre-approved *for the turn that invokes the skill only* — clears on next user message. Does **not** restrict which tools are available generally |
| `disallowed-tools` | Tools removed from the pool while skill active; clears next message |
| `model` | Model override for the invoking turn only, not saved; `inherit` keeps current; with `context: fork` sets the forked subagent's model instead |
| `effort` | Effort level override while skill active |
| `context: fork` | Runs skill in an isolated forked subagent (see below) |
| `agent` | Which subagent type to use with `context: fork` |
| `background` | Only with `context: fork`; default `true` (backgrounded); `false` blocks the invoking turn until done (v2.1.218+) |
| `hooks` | Hooks registered when skill invoked, persist for rest of session (unless `once: true` set per-hook) |
| `paths` | Glob patterns limiting auto-activation to matching files |
| `shell` | `bash` (default) or `powershell` for inline `!command` injection |
| `metadata` | Free-form map, unused by Claude Code itself |
| `license`, `compatibility` | Agent Skills spec fields, accepted but inert in Claude Code |

**Frontmatter is only parsed if the opening `---` is the file's very first line** — otherwise the whole file (including the `---` markers) is treated as plain skill content. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Portability constraint — Agent Skills spec vs Claude Code extensions
Outside Claude Code (claude.ai skill uploads, the Skills API, `package_skill.py`), **only** `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools` are valid frontmatter keys. Any other field (e.g. `argument-hint`, `context`, `disable-model-invocation`) causes a **hard packaging/upload error**, not a silent drop. This matters for v4 if proofpunk skills are meant to be portable beyond Claude Code. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Progressive disclosure
- Only the `description` (+ `when_to_use`) is kept in context at all times; full `SKILL.md` body loads only on invocation. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)
- Skills can ship supporting files (`reference.md`, `examples.md`, `scripts/helper.py`) alongside `SKILL.md`; these are **not** auto-loaded — `SKILL.md` must explicitly link to them so Claude knows to read them when needed. Recommended: keep `SKILL.md` **under 500 lines**, push detail to separate files. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)
- Once invoked, a skill's rendered content **stays in context for the rest of the conversation** — it is not re-read on later turns, so instructions meant to persist must be written as standing instructions, not one-time steps. Re-invoking with identical rendered content just adds a short "already loaded" note rather than duplicating. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)
- Under auto-compaction, invoked skills are carried forward: the most recent invocation of each skill is re-attached after a summary, capped at the first 5,000 tokens each, with a **combined 25,000-token budget across all re-attached skills** — older skills can be dropped entirely if many were invoked in one session. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Dynamic context injection
Inline `` !`command` `` (must be at start of line or after whitespace) or fenced ` ```! ` blocks run shell commands **before** the skill body reaches Claude; output replaces the placeholder as plain text. Substitution runs once — command output is not re-scanned for further placeholders. A failed command (`bash`: any non-zero exit except the documented read-only-command carveout) **aborts the entire skill invocation**, and Claude never sees any of the skill's content for that call. `disableSkillShellExecution` setting can disable this globally for user/project/plugin/additional-dir skills (bundled/managed skills unaffected); claude.ai-synced skills **never** run these commands on the local machine regardless of that setting. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Running a skill in a subagent (`context: fork`)
The skill body becomes the entire prompt for a forked subagent with no access to conversation history; runs in the background by default (user keeps working), unless `background: false`. This is a **complementary but inverse** mechanism to a subagent's own `skills:` frontmatter field (which preloads full skill content into a *custom subagent's* system context) — table distinguishing the two:
| Approach | System prompt | Task | Also loads |
|---|---|---|---|
| Skill with `context: fork` | From agent type | SKILL.md content | CLAUDE.md (except Explore/Plan) |
| Subagent with `skills:` field | Subagent's markdown body | Claude's delegation message | Preloaded skills + CLAUDE.md |
[Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

---

## 3. Hooks (event types, matchers, input/output contract, exit codes)

Source: https://docs.claude.com/en/docs/claude-code/hooks ("Hooks reference")

### What hooks are
User-defined shell commands, HTTP endpoints, MCP tool calls, LLM prompts, or subagents, executed automatically at specific lifecycle points. Fire the same across every surface (terminal, IDE, Desktop, web). Five handler `type`s: `"command"`, `"http"`, `"mcp_tool"`, `"prompt"`, `"agent"` (agent hooks are explicitly labeled **experimental and may change**). [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

### Full event catalog (from the lifecycle table in [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks))
Once-per-session: `SessionStart`, `Setup`, `SessionEnd`.
Once-per-turn: `UserPromptSubmit`, `UserPromptExpansion`, `Stop`, `StopFailure`, `TeammateIdle`.
Per-tool-call (agentic loop): `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`.
Subagent/task: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`.
Standalone async: `Notification`, `MessageDisplay`, `WorktreeCreate`, `WorktreeRemove`, `ConfigChange`, `InstructionsLoaded`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult`.
[Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

**This is directly relevant to proofpunk's write-guard defect (D-A):** `PreToolUse` matcher input is the tool name (`tool_name` on the JSON input) — a matcher of `"Write|Edit"` does **not** cover MCP filesystem tools, which appear as `mcp__<server>__<tool>` (e.g. `mcp__filesystem__write_file`), matched only via `mcp__<server>__.*` patterns or exact `mcp__filesystem__write_file`. This is exactly the mechanism the current `hooks.json` matcher (`Write|Edit`) fails to cover for the MCP `write_file` tool. [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

### Configuration model — three levels of nesting
1. Hook **event** (e.g. `PreToolUse`)
2. **Matcher group** (`matcher` field) — filters which occurrences fire
3. One or more **hook handlers** in the matcher group's `hooks` array

Hook **locations** and their scope/shareability (table from [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)):
| Location | Scope | Shareable |
|---|---|---|
| `~/.claude/settings.json` | All projects | No (local machine) |
| `.claude/settings.json` | Single project | Yes, committable |
| `.claude/settings.local.json` | Single project | No, gitignored |
| Managed policy settings | Org-wide | Yes, admin-controlled |
| Plugin `hooks/hooks.json` | While plugin enabled | Yes, bundled |
| Skill frontmatter | Rest of session once invoked | Yes, in skill file |
| Subagent frontmatter | While that subagent runs | Yes, in subagent file |

Hook entries **merge across settings levels** (they don't replace each other): user/project/local hooks add to managed hooks without removing them. `disableAllHooks` cannot disable managed-tier hooks unless set at the managed tier itself. [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

### Matcher semantics
Matcher evaluation depends on character content: `"*"`/`""`/omitted matches all; letters/digits/`_`/`-`/spaces/`,`/`|` only → exact-string-or-list match; anything else (including regex metacharacters) → **unanchored JavaScript regex** via `RegExp.prototype.test`. `Edit.*` therefore also matches `NotebookEdit` — anchor with `^...$` for whole-string matching. `FileChanged` and `StopFailure` use a narrower exact-match charset (letters/digits/`_`/`|` only; hyphens/spaces/commas push them onto the regex path). [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

For finer per-tool-call filtering, individual hook **handlers** (not matcher groups) support an `if` field using **permission-rule syntax** (e.g. `"Bash(git *)"`, `"Edit(*.ts)"`) — evaluated only on the five tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`). `if` is a single rule with no `&&`/`||`; combine conditions by defining multiple handlers. [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

MCP tools match on their full name pattern `mcp__<server>__<tool>`; to match every tool from a server you must use `mcp__<server>__.*` — `.*` is **required**, a bare `mcp__memory` (no wildcard) is compared as an exact string and matches nothing. [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

### Input/output contract
Command hooks receive the event's JSON as **stdin**; HTTP hooks receive it as the **POST body**. Common input fields present on (almost) every event: `session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir`, `permission_mode`, `effort`, `hook_event_name`. When running under `--agent` or inside a subagent, two more: `agent_id`, `agent_type`. [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

Output: exit code + stdout/stderr, OR structured JSON on stdout (exit 0 is the intended code for JSON-based control). JSON detection is by stdout shape: starts with `{` and ends with `}` → parsed as JSON; otherwise plain text. Universal JSON fields: `continue` (false halts everything, overrides event-specific decisions), `stopReason`, `suppressOutput` (documented as **inert** — accepted but ignored), `systemMessage` (shown to user), `terminalSequence` (allowlisted OSC escape codes for desktop notifications, since hooks have no controlling TTY). Event-specific control goes in a nested `hookSpecificOutput` object requiring a `hookEventName` field. [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

### Exit codes
- **Exit 0**: success; JSON on stdout parsed for structured control.
- **Exit 2**: blocking error, on events that support blocking (`PreToolUse` blocks the tool call, `UserPromptSubmit` erases the prompt, `Stop`/`SubagentStop` prevent stopping, `ConfigChange` blocks the config change except `policy_settings`, `PreCompact` blocks compaction, `PreModelSwitch` blocks the switch, `Elicitation`/`ElicitationResult` deny/decline, `WorktreeCreate` — **any** non-zero exit fails creation, not just 2). A per-event table (`Exit code 2 behavior per event`) is authoritative for which events this applies to; several events (`PermissionRequest`, `PermissionDenied`, `Notification`, `PostToolUse`, `PostToolUseFailure`, etc.) explicitly **cannot** block via exit 2 (the action already happened, or the event has its own decision channel).
- **Other exit codes**: generally non-blocking; if stdout is valid JSON matching the event's schema, the JSON alone decides the outcome regardless of exit code; if stdout can't be parsed as JSON or is plain text, it's a non-blocking error and the action proceeds, with a `<hook name> hook error` notice.
- **Critical warning explicitly called out in the docs**: for most events, **exit code 1 is a non-blocking no-op**, even though it's the conventional Unix failure code. This does **not** mean exit 2 is the only enforcement path — it means a hook that wants to block by *stderr text alone, with no JSON*, must exit 2 specifically (exit 1 with stderr and no JSON is silently ignored on most events). The two full, first-class enforcement paths are: (a) `exit 2` with a plain-text reason on stderr, or (b) `exit 0` (or any code) with structured JSON on stdout setting `hookSpecificOutput.permissionDecision: "deny"` (or `continue: false` to halt outright) — either is honored regardless of exit code, except that exit 2's block cannot be overridden by a JSON `"allow"`. A `PreToolUse` deny via JSON, exiting 0, looks like:

  ```json
  {
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "MCP filesystem write outside allowed matcher scope"
    }
  }
  ```

  [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

### Timeouts
Default 600s for `command`/`http`/`mcp_tool`, 30s for `prompt`, 60s for `agent`; lowered to 30s on `UserPromptSubmit`/`PreModelSwitch`/`PostModelSwitch`, 10s on `MessageDisplay`; `SessionEnd` hooks share a 1.5s budget (raisable up to 60s if the hook sets a longer per-hook timeout). A **timed-out `command`/`http`/`mcp_tool` hook on `PreToolUse` does NOT block the tool call** — it silently falls through to normal permission flow, so a stalled hook is not a reliable gate. (An Agent SDK callback hook that times out *does* block — that's a distinct, SDK-only mechanism.) [Hooks docs](https://docs.claude.com/en/docs/claude-code/hooks)

---

## 4. Subagents (definition, model routing, tool inheritance)

Source: https://docs.claude.com/en/docs/claude-code/sub-agents ("Create custom subagents")

### What a subagent is
A specialized AI assistant running in its own context window with its own system prompt, tool access, and permissions, delegated to when a task matches its `description`. Subagents work **within a single session** — for many independent parallel sessions use background agents (`/docs/en/agent-view`); for cross-session messaging see `/docs/en/cross-session-messaging`; for a supervised team, see `/docs/en/agent-teams`. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Built-in subagents (exact behavior)
| Agent | Model | Tools | Purpose |
|---|---|---|---|
| `Explore` | Inherits main conversation's model, **capped at Opus on the Claude API** (v2.1.198+; previously always Haiku) | Read-only (Write/Edit denied) | File discovery/search, no changes |
| `Plan` | Inherits main conversation, unless overridden | Read-only | Codebase research during plan mode |
| `general-purpose` | `CLAUDE_CODE_SUBAGENT_MODEL` if set (else main conversation's model) | Every tool available to subagents | Complex multi-step work needing both exploration and edits |
| `claude` (catch-all) | Follows model order | Every tool | Default when no specialized agent fits |
| `statusline-setup` | Sonnet | — | `/statusline` config |
| `claude-code-guide` | Haiku | — | Questions about Claude Code itself |
[Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

A user/project-level custom subagent literally named `Explore` **overrides** the built-in one and keeps its own `model` field, so this is the documented way to force Explore onto a cheaper model. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

To disable built-ins: `permissions.deny: ["Agent(Explore)"]` blocks one; denying the `Agent` tool itself blocks all delegation; `CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1` removes just Explore/Plan (Claude explores directly instead); `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1` in non-interactive/SDK contexts removes all built-ins. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### File locations, priority, and format
| Location | Scope | Priority | 
|---|---|---|
| Managed settings | Org-wide | 1 (highest) |
| `--agents` CLI flag | Current session (not saved to disk) | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All projects | 4 |
| Plugin `agents/` dir | Where plugin enabled | 5 (lowest) |
[Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

Project subagents are discovered by **walking up** from cwd to repo root; when nested `.claude/agents/` dirs share a `name`, the closest to the working directory wins (v2.1.178+). `.claude/agents/` and `~/.claude/agents/` are scanned **recursively** (subfolders organize but don't namespace) except for plugins, where a subfolder path *does* become part of the plugin-scoped identifier (`agents/review/security.md` in `my-plugin` → `my-plugin:review:security`). [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

Subagent file = YAML frontmatter + Markdown system-prompt body. Required frontmatter: **only `name` and `description`**. Full field table (from [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)) includes: `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills` (preload full content at startup, not just discoverable), `mcpServers` (inline or by-reference, scoped to just this subagent — can hide an MCP server's tool descriptions from the main conversation entirely), `hooks` (scoped to while this subagent runs), `memory` (`user`/`project`/`local` — persistent cross-session subagent memory directory), `background`, `effort`, `isolation: worktree` (isolated git worktree copy of the repo), `color`, `initialPrompt`, `experimental.cacheTtl`.

Claude Code **watches** `~/.claude/agents/` and `.claude/agents/` and picks up new/edited subagent files within seconds, no restart — except: the watcher only covers directories that existed at session start (first agent file in a brand-new `agents/` dir needs a restart), `--add-dir` directories aren't watched, and `--disable-slash-commands` sessions don't watch at all. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Model resolution order (authoritative, v2.1.251+)
1. Per-invocation `model` parameter (Claude can pass this when spawning)
2. Subagent's frontmatter `model` field (`inherit` = main conversation's model)
3. `CLAUDE_CODE_SUBAGENT_MODEL` env var
4. Main conversation's model (default fallback)

`CLAUDE_CODE_SUBAGENT_MODEL` alone does **not** override the built-in Explore/Plan subagents. To force literally every subagent (including Explore/Plan, teammates, workflow agents) onto one model, you must **also** set `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` — this is the only documented way to guarantee a fleet-wide model pin, and it disables per-invocation model overrides entirely except for forks and `skills` running with `model: inherit`. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Tool inheritance (exact mechanism — critical for v4 dispatch design)
Subagents inherit the built-in + MCP tools available in the main conversation, narrowed by **two filters**:
1. **Universal removal** (applies regardless of `tools:` field): `Agent` (at depth limit), `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`, `TaskOutput`, `WaitForMcpServers`, `Workflow`.
2. **Background-subagent narrowing** (applies by default, since subagents run in the background unless "fork mode" is off): a background subagent keeps every MCP tool but **only** these built-ins: `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, `Artifact`. Every other built-in tool is stripped even if explicitly listed in `tools:`. **Forks skip both filters** and get the main conversation's exact tool pool. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

This means: a subagent's `tools:` allowlist is evaluated **after** these filters remove things — you cannot grant a background subagent `EnterPlanMode` by listing it. Restriction: `tools:` = allowlist, `disallowedTools:` = denylist; if both set, `disallowedTools` applied first, then `tools` resolved against what remains; a tool in both is removed. If `tools:` resolves to zero tools, the subagent **fails to launch** with a named error (v2.1.208+; before that it silently launched with no tools). Both fields accept MCP server-level patterns: `mcp__<server>` or `mcp__<server>__*`. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Permission modes for subagents
`permissionMode` frontmatter accepts `default`/`acceptEdits`/`auto`/`dontAsk`/`bypassPermissions`/`plan`/`manual` (alias for `default`). If the **parent** session is in `bypassPermissions` or `acceptEdits`, that takes precedence and cannot be overridden by the subagent's frontmatter. If the parent is in **auto mode**, the subagent inherits auto mode and its `permissionMode` frontmatter is **ignored entirely** — the classifier evaluates the subagent's tool calls with the same rules as the parent. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Depth limit
Subagents can spawn their own subagents up to **3 layers below the main conversation by default**, configurable via `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. At the limit, the `Agent` tool is withheld from every subagent except forks (which keep it listed but it errors instead of spawning). [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

### Output scanning (security-relevant for v4's "safeguards in the harness" goal)
Claude Code scans every subagent's final report **before Claude reads it**, because a subagent may have read attacker-controlled content (files, web pages, command output) containing prompt-injection-style text aimed at the main conversation. The scan does two things only: inserts a backslash into text imitating Claude Code's own output format (e.g. fake `<system-reminder>` tags, fake `Human:`/`Assistant:` lines), and prepends a `[harness: subagent output matched instruction-shaped pattern(s):...]` marker line when the report imitates such tags or mentions permission-bypass settings. **It does not judge maliciousness and does not change what a resulting tool call can do** — any action the report leads Claude to take still goes through normal permission checks and sandboxing. Explicitly **not a substitute** for restricting what a subagent can reach via tool/MCP scoping. Requires v2.1.210+. [Subagents docs](https://docs.claude.com/en/docs/claude-code/sub-agents)

---

## 5. Slash commands

Source: https://docs.claude.com/en/docs/claude-code/commands ("Commands"), cross-referenced with https://docs.claude.com/en/docs/claude-code/skills

### Mechanism — four distinct things share the `/` prefix
A command is only recognized **at the start of a message**; trailing text becomes its arguments. The `/` namespace is **not one mechanism** — it's four, and the Commands reference page ([Commands docs](https://docs.claude.com/en/docs/claude-code/commands)) is the authoritative source distinguishing them (note: `https://docs.claude.com/en/docs/claude-code/slash-commands` redirects to the *Skills* page, not a distinct slash-commands page — the Commands reference at `/docs/en/commands` is the correct source for this section):

1. **Genuine built-in commands**, whose logic is coded directly into the CLI binary itself (not prompt-based at all): e.g. `/clear`, `/compact`, `/config`, `/context`, `/cd`, `/add-dir`, `/agents` (as of v2.1.198, `/agents` no longer opens an interactive wizard — it just prints a reminder to ask Claude or edit files directly).
2. **Bundled skills**, marked "Skill" in the reference table: prompt-based commands Anthropic ships as ordinary skills under the hood — e.g. `/doctor`, `/code-review`, `/batch`, `/debug`, `/loop`, `/claude-api`. Claude orchestrates them with its own tools, the exact same mechanism as a skill you author yourself. `disableBundledSkills` turns off all of them except `/doctor`.
3. **Bundled workflows**, marked "Workflow": e.g. `/deep-research` — a "dynamic workflow" that fans work across many subagents in the background, a distinct and more structured orchestration primitive than a plain skill (see Gap 3 below; `/docs/en/workflows` was not independently fetched this session).
4. **User-authored custom commands, which are skills**: this is the one place the merge is explicit and total per the Skills doc — `.claude/commands/deploy.md` (the older, flat-file legacy form, still fully supported) and `.claude/skills/deploy/SKILL.md` (the current form) both create `/deploy` and behave identically; the skill form additionally supports supporting-file directories and invocation-control frontmatter (see §2). [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

Categories 2–4 are all skills under the hood (prompt handed to Claude); only category 1 is compiled CLI logic that a plugin or skill author cannot reproduce or override.

### Skill/command stacking (relevant to a v4 "compose small skills" design)
As of v2.1.199, you can chain up to **6** skill invocations at the start of one message: `/skill-a /skill-b do XYZ` loads both skills and passes `do XYZ` to each as `$ARGUMENTS`. Expansion stops at the first token that is not an inline user-invocable skill — a skill running as `context: fork` (e.g. `/code-review`, which runs as a forked subagent since v2.1.218), or one whose own arguments might start with `/`, ends the chain there; everything from that token onward becomes literal argument text for every skill already expanded. [Commands docs](https://docs.claude.com/en/docs/claude-code/commands) [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Argument substitution (from §2, applies identically to commands-as-skills)
`$ARGUMENTS` (full string), `$ARGUMENTS[N]` / `$N` (indexed, shell-quoted), `$name` (named, via `arguments:` frontmatter list). An indexed placeholder with nothing at that position stays literal; a named placeholder with nothing expands to empty string. `\$1.00` escapes a literal `$`. [Skills docs](https://docs.claude.com/en/docs/claude-code/skills)

### Command menu behavior
`/` opens a fuzzy-filterable list; queued commands run after the current turn finishes for most commands, but several (`/status`, `/tasks`, `/usage`, and fullscreen dialog commands like `/theme`/`/help`) run **immediately without interrupting** the in-flight response (v2.1.234+). [Commands docs](https://docs.claude.com/en/docs/claude-code/commands)

---

## 6. Settings / permissions

Source: https://docs.claude.com/en/docs/claude-code/settings ("Settings files and precedence"), https://docs.claude.com/en/docs/claude-code/permissions ("Configure permissions")

### Settings files — exact locations and scope
| Scope | File | Who it affects |
|---|---|---|
| User | `~/.claude/settings.json` | You, every project on this machine |
| Shared project | `.claude/settings.json` | Everyone in the project folder; commit to share |
| Project local | `.claude/settings.local.json` | You, this project only; Claude Code auto-gitignores it the first time it writes to it (adds `**/.claude/settings.local.json` to global git excludes) — if you hand-create it, gitignore it yourself |
| Managed | `managed-settings.json` / MDM / claude.ai console | Everyone the org deploys to; nothing you set overrides it except a documented short list of security-sensitive exceptions |
Plus a fifth file Claude Code manages itself and you don't hand-edit: `~/.claude.json` (sign-in session, MCP configs, trust decisions, `/config`-written global keys). [Settings docs](https://docs.claude.com/en/docs/claude-code/settings)

**Precedence stack, highest first**: Managed settings → `--settings` CLI flag → Project local (`settings.local.json`) → Shared project (`settings.json`) → User (`~/.claude/settings.json`). Environment variables are **not** a level in this stack — each env-var/setting pair has its own documented precedence rule (e.g. `ANTHROPIC_MODEL` always wins over the `model` key from any file; `ANTHROPIC_DEFAULT_MODEL` only applies when no file sets `model`). [Settings docs](https://docs.claude.com/en/docs/claude-code/settings)

List-type keys (e.g. `permissions.allow`) **merge** across files rather than override — each file's list entries are unioned. Four specific keys (`fallbackModel`, `modelPicker`, `availableModels`, `modelSettings`) are exceptions with their own non-merging resolution rules. [Settings docs](https://docs.claude.com/en/docs/claude-code/settings)

**Cloud sessions** (Claude Code on the web) read only: committed `.claude/settings.json` (part of the clone) and server-managed settings (not local `managed-settings.json`/MDM). They do **not** read `~/.claude/settings.json` or `.claude/settings.local.json` — both stay on the local machine. This is architecturally significant for any proofpunk v4 feature meant to work identically locally and in the cloud. [Settings docs](https://docs.claude.com/en/docs/claude-code/settings)

Settings files are watched and hot-reloaded for most keys (`permissions`, `hooks`, `apiKeyHelper`, etc.) without restart, triggering a `ConfigChange` hook per file change — but **not** for managed settings arriving via MDM/console (those reach a running session on their own delivery schedule, not on save). A short list of keys are read only once at session start (`model` via `/model` instead; `effortLevel`/`modelSettings` via `/effort` instead). [Settings docs](https://docs.claude.com/en/docs/claude-code/settings)

### Permission rule syntax (authoritative reference)
Rule shape: `Tool` (matches all uses) or `Tool(specifier)`. Evaluated in strict order: **deny, then ask, then allow** — first match wins regardless of specificity, so a broad `deny` (`Bash(aws *)`) cannot have narrower `allow` exceptions carved out of it. [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

Wildcard `*` in a Bash specifier stands in for arbitrary text including spaces; put it **after** the subcommand (`Bash(git log *)` not `Bash(git * log)`) — Claude Code even warns at startup about a `*` placed before the rest of the command. `:*` suffix is equivalent to trailing ` *`. Deny/ask rules also accept **glob patterns in the tool-name position itself** (e.g. `mcp__*` denies every MCP tool from every server); allow rules only accept tool-name globs after a literal `mcp__<server>__` prefix (server segment must be glob-free). [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

**Parameter matching** (new, non-content-field matching): deny/ask rules can match a top-level scalar input parameter directly, e.g. `Agent(model:opus)`, `Agent(isolation:worktree)`, `Bash(run_in_background:true)` — but this explicitly **cannot** be used on a tool's primary content field (`command` for Bash, `file_path` for Read/Edit/Write, `url` for WebFetch, etc.) because such rules would be trivially bypassable; Claude Code detects and ignores these with a startup warning. [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

### Permission modes (authoritative table)
| Mode | Behavior |
|---|---|
| `default` (labeled "Manual") | Prompts on first use of each tool |
| `acceptEdits` | Auto-accepts file edits + common filesystem commands in working/additional dirs |
| `plan` | Read-only exploration; no source edits (classifier-approved commands still run if auto mode is available) |
| `auto` | Background classifier reviews and auto-approves actions matching your request |
| `dontAsk` | Auto-denies unless pre-approved via allow rules; `AskUserQuestion` and interaction-required MCP/connector tools are denied even if allowed |
| `bypassPermissions` | Skips prompts entirely, except a documented short list of actions "no mode auto-approves" |
[Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

`permissions.disableBypassPermissionsMode` / `permissions.disableAutoMode` set to `"disable"` in any settings file **hard-blocks** those modes — most useful in managed settings, since it can't be overridden from below. [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

Bash compound-command handling: Claude Code recognizes shell operators (`&&`, `||`, `;`, `|`, `|&`, `&`, newlines) and evaluates deny/ask rules against **each subcommand independently**, including inside subshells, `$()` command substitution, backticks, and control-flow bodies — so a deny rule like `Bash(git clean *)` still fires on `echo "$(git clean -f)"`. A fixed, non-configurable list of process wrappers (`timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin`, zsh `noglob`) is stripped before matching, so `Bash(npm test *)` also matches `timeout 30 npm test`. Development environment runners (`direnv exec`, `devbox run`, `npx`, `docker exec`) are explicitly **not** in that stripped list — a rule like `Bash(devbox run *)` matches the *entire* trailing text including `rm -rf .`, which the docs call out as a real footgun. [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

A built-in, **non-configurable** set of read-only Bash commands (`ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, read-only `git` forms) never prompts in any mode — except several documented edge cases still prompt (unquoted globs on write-capable-flag commands, `docker` pointed at another daemon, `file` with path-opening flags, Windows network/UNC paths, unparseable commands, commands >10,000 chars). [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

Redirections are checked against file rules as if Claude wrote/read the target directly (`> file`, `>> file`, `2> file` checked against Edit rules + protected paths; `< file` checked against Read rules, v2.1.257+) — targets with no real file behind them (`/dev/null`, fd forms, here-docs) are exempt. [Permissions docs](https://docs.claude.com/en/docs/claude-code/permissions)

---

## Gaps

Behaviors proofpunk assumes or references that these docs do **not** confirm, or that this session could not fully verify — flagged for direct verification before v4 architecture locks them in:

1. **The exact write-guard bypass mechanics for proofpunk's D-A defect.** The docs confirm MCP tools are matched by `mcp__<server>__<tool>` name patterns and that a bare `Write|Edit` matcher does not cover them — but this digest does not independently verify against proofpunk's actual `plugins/proofpunk/hooks/hooks.json` file, nor confirm whether the fix is a matcher change (`mcp__filesystem__write_file`) vs. an `if`-condition change vs. denying MCP filesystem tools outright. That is a repo-specific verification task, not a docs gap, but it's the load-bearing claim v3 gauge 4 depends on.

2. **Organization-settings plugin distribution restrictions.** [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) references a "Distribute through organization settings" section restricting allowed source types for org-managed plugin distribution, but this session did not fetch that subsection's content (only its existence, via a cross-reference). Unconfirmed which source types are excluded.

3. **Dynamic workflows (`/docs/en/workflows`) as a distinct orchestration primitive.** The docs reference "dynamic workflows" (`/deep-research` is one) as something structurally different from an ordinary skill or subagent fan-out — described in the overview as "how the Claude Code team uses dynamic workflows to orchestrate many subagents at once" (linked from a Claude.com blog post, not the docs proper) and via a bundled-workflow marker in the commands reference. This session did not fetch `/docs/en/workflows` itself. If proofpunk v4's "parallelize" goal is meant to lean on this primitive rather than hand-rolled subagent fan-out, that page needs a dedicated read.

4. **MCP server documentation (`/docs/en/mcp`) was not fetched in this session** beyond incidental references (elicitation, plugin-provided servers, tool-name scoping). The operator's v4 direction explicitly calls out "how they [plugins, skills, AI orchestration, harnesses] work in tandem" — MCP is a first-class integration surface referenced throughout §1, §3, §4 here but not independently verified as its own topic.

5. **Agent teams (`/docs/en/agent-teams`)** — referenced repeatedly in the subagents doc (teammates keep additional task/cron tools; `permissionMode`/`hooks`/`mcpServers` from a subagent definition partially apply to teammates) but not fetched directly. If v4 wants coordinated multi-agent supervision (distinct from ad hoc subagent fan-out), this is the documented primitive and needs direct verification.

6. **"Guidance-over-measurement" and "safeguards embedded in the harness" as the operator frames v4 has one confirmed hook-side mechanism** (subagent output scanning, §4) that is explicitly **not** a policy enforcement layer — it only defangs prompt-injection-shaped text, and states outright it "doesn't judge whether content is malicious" and "isn't a substitute for restricting what a subagent can reach." Any v4 architecture claiming hooks alone can enforce "follow skills, not scripts measuring after the fact" needs to reconcile with the plain-text/exit-code enforcement path (§3): a hook returning ONLY a stderr message and no JSON must exit 2 specifically, since exit 1 with plain stderr is silently ignored on most events. A hook that instead returns a valid `hookSpecificOutput.permissionDecision` JSON object is honored independent of exit code, so the two paths are not equivalent and a v4 guard author must pick one deliberately — a guidance hook that emits plain stderr on exit 1 (instead of exit 2, or instead of JSON) will silently do nothing, which is precisely the class of failure gauge 4 already ran into with a differently-shaped guard (matcher scope, not exit code, but same root failure mode: a guard that looks present but doesn't fire on the input it needs to catch).

7. **Skill/plugin token-cost limits at scale.** The docs state subagent description totals warn above 15,000 tokens combined, and re-attached-skill budgets cap at 25,000 tokens combined after compaction — but do not state an analogous hard cap for *how many skills a single plugin can ship* before the always-in-context description list itself becomes a budget problem. If v4 plans a much larger skill surface than v2/v3, this ceiling is unconfirmed and worth a direct test rather than an inferred safe number.
