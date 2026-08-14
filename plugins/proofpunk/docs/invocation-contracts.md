# Invocation Contracts — how skills, hooks, agents, and plugins actually fire

Researched 2026-08-13 from official/vendor sources only. This table is the
trigger-owner map the v2.0.0 revamp was built against.

## Trigger owners per platform

| Behavior | Claude Code | OpenCode | OMP (oh-my-pi) |
|---|---|---|---|
| Skill auto-invoke | model judgment over name+description listing (1,536 chars/skill budget, 1% of context); `paths:` narrows | model invokes `skill` tool on description match; six discovery roots incl. `~/.claude/skills` fallback | name+description in system prompt; body via `read` on `skill://<name>`; `/skill:<name>` |
| Slash command | `/plugin:command` (user) | `/<name>` in TUI (user) | `registerCommand` in extensions |
| Hooks (hard guarantee) | `hooks/hooks.json` merges on enable; command/http/mcp_tool/prompt/agent types | plugin TS module; `tool.execute.before` throws to block | extension `pi.on(...)`: `tool_call` can `{block, reason}`; `session_stop` can force continuation (cap 8) |
| Subagents | `agents/*.md` (name+description required; `skills:` preloads full skill bodies); Agent tool spawns by description match; NOT automatic at install | `agents/*.md` with `permission:` map (`tools:` deprecated); Task tool auto-invokes by description | `task` tool; agents in `~/.omp/agent/agents/`, `.omp/agents/`, extension roots; `autoloadSkills` frontmatter |
| Memory | CLAUDE.md + `.claude/rules/*.md` (`paths:` lazy-load); concatenation model | AGENTS.md > CLAUDE.md fallback; no `@`-imports; `instructions[]` globs in opencode.json | `.omp/AGENTS.md` + sticky `RULES.md`; CLAUDE.md via claude provider; AGENTS.md walked up |
| Plugin = ship unit | skills+agents+hooks+MCP all activate on enable; `/reload-plugins` for the current session | plugins are TS hook modules; agents/commands via config (unofficial) | `omp plugin install` (npm/git) + marketplace (Claude-registry-compatible, `.omp-plugin/marketplace.json`) |

## Sources

- https://docs.anthropic.com/en/docs/claude-code/skills · /plugins · /plugins-reference · /hooks · /sub-agents · /memory
- https://opencode.ai/docs/plugins/ · /agents/ · /skills/ · /commands/ · /rules/
- https://github.com/can1357/oh-my-pi docs/{extensions,skills,task-agent-discovery,context-files,marketplace}.md (verified against source @ ffd53ff)

## What the docs DON'T answer (recorded, not assumed)

- No deterministic skill-match metric anywhere — auto-invocation is model
  judgment over the description. Specific descriptions are the only lever.
- CLAUDE.md conflict precedence is explicitly undefined.
- Hook execution is guaranteed; model compliance with soft context is not —
  hard guarantees live only in blocking decisions (PreToolUse deny, Stop block).
