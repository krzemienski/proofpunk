# Proofpunk installer — usage, options, and why they exist

`tools/proofpunk-install.sh` installs the 18 Proofpunk skills as **plain
skills** (not a plugin, not a marketplace) into the skills directory of your
choice, injects the ruling doctrine alongside them, and verifies the result.
Everything below was executed against the real script before shipping — the
outputs shown are the actual behaviors, not aspirations.

## Two installation channels — and why hooks behave differently in each

This is the most common confusion, so it is stated first.

| | **Plain-skills channel** (this script) | **Plugin channel** (marketplace) |
|---|---|---|
| How you install | `bash proofpunk-install.sh …` | `/plugin marketplace add …` then `/plugin install …` |
| Where skills land | your skills dir (`~/.claude/skills`, `~/.omp/agent/skills`, …) | the host's plugin cache |
| Where hooks come from | copied to `~/.proofpunk/hooks/`, **registered into `settings.json`** | read from the plugin's own `hooks/hooks.json` in the cache |
| Does `settings.json` gain hook entries? | **only with `--hooks`** | **never** — and that is correct, not a bug |

Both channels enforce the same doctrine; they differ only in *where the host
reads the hooks from*. If you installed from the marketplace and then looked
in `~/.claude/settings.json` expecting proofpunk entries, finding none is the
expected result — the host loads them from the plugin cache.

**Hooks in this script are opt-in.** `WITH_HOOKS=0` is the default and the
whole copy-and-register block is gated behind `--hooks`. A quick-start command
without that flag installs skills and doctrine but **zero enforcement**. That
is a deliberate default — hooks write to a shared settings file — but it does
mean you have to ask for them.

To confirm hooks actually registered rather than merely landing on disk:

```bash
bash proofpunk-install.sh --target claude-code --hooks
python3 - <<'EOF'
import json, os
h = json.load(open(os.path.expanduser("~/.claude/settings.json"))).get("hooks", {})
n = sum(1 for ev in h for b in h[ev] for e in b.get("hooks", [])
        if "proofpunk" in e.get("command", ""))
print(f"proofpunk hook registrations: {n}")   # expect 11
EOF
```

Eleven registrations across seven event keys is the full set. That count comes
from `plugins/proofpunk/hooks/hooks.json`, the single source of truth for both
which scripts get copied and which events get registered. Re-running with
`--hooks` is idempotent — the second run leaves `settings.json` byte-identical.

## The 60-second version

```bash
# Claude Code user, latest GitHub main, everything included:
bash proofpunk-install.sh --target claude-code

# oh-my-pi user — skills, 20 themes, and the doctrine-guard extension:
bash proofpunk-install.sh --target omp --themes --plugins

# OpenCode user — skills, 20 themes, plugin + commands + 4 agents:
bash proofpunk-install.sh --target opencode --themes --plugins

# Themes only, no skills:
bash proofpunk-install.sh --skip-skills --themes

# Installed already and want the new versions, keeping backups:
bash proofpunk-install.sh --target claude-code --override

# Everything at once — all options selected:
bash proofpunk-install.sh --target claude-code --source github --ref main \
  --themes --plugins --hooks --inject-memory --override
# (skills + themes + platform glue + enforcement hooks merged into
#  ~/.claude/settings.json + the marked rules block in ./CLAUDE.md)

# Offline, one skill, OpenCode's AGENTS.md, nothing else:
bash proofpunk-install.sh --source-dir /path/to/proofpunk --target opencode \
  --only tui-testing --inject-memory --no-verify
```

**Hooks are opt-in.** The quick-start commands above install zero enforcement
hooks. Pass `--hooks` to install the guard scripts and merge them into the
platform's settings file (`~/.claude/settings.json` for Claude Code): the
Stop/SubagentStop unproven-claim guard plus PreToolUse secrets-in-evidence and
immutable-capture guards. Marketplace/plugin installs get their hooks from the
plugin cache's own `hooks/hooks.json` instead — that channel never writes
`settings.json` entries.

## What an install actually produces

```
<target>/
├── brainstorm/            # 18 skill dirs, each SELF-CONTAINED:
│   ├── SKILL.md           #    citations rewritten to references/X
│   └── references/        #    cited doctrine bundled inside the skill
│   ...
├── visual-inspection/
└── proofpunk-doctrine/  # the ruling rules, shared by all skills
    ├── README.md          #   Iron Rule / End-User Actor / remediation / evidence
    ├── end-user-actor.md  #   incl. "test runners are never validation"
    ├── evidence-contract.md
    └── ... (13 ruling references)
```

**Why self-contained copies:** the repo's plugin layout cites shared doctrine
as `../../references/X`, which only resolves inside the plugin directory tree.
In a plain skills directory that path escapes the skill and breaks. The
installer rewrites citations to `references/X` and bundles each cited shared
reference inside the skill — so every installed skill stands alone. (This is
the exact flaw the installer's own `--verify` pass caught during development.)

## Target options — WHERE skills go

| Option | Effect | Why it exists |
|---|---|---|
| `--target claude-code` | Installs to `~/.claude/skills` (default) | The standard Claude Code personal-skills location; zero config |
| `--target omp` | Installs to `${PROOFPUNK_OMP_DIR:-~/.omp/agent/skills}` | oh-my-pi's native skill provider (priority 100 — beats Claude-compat copies); set `PROOFPUNK_OMP_DIR` or use `--dir` for profile installs |
| `--target opencode` | Installs to `~/.config/opencode/skills` | OpenCode's native skill location; note OpenCode also reads `~/.claude/skills`, so one `--target claude-code` install can serve both |
| `--target agents` | Installs to `~/.agents/skills` | The shared agents-compatible location both oh-my-pi and OpenCode discover |
| `--dir PATH` | Installs to exactly `PATH`, beats `--target` | Any other host: project-level skills, a different agent's directory, a sandboxed test (the installer's own test suite uses this) |

## Source options — WHERE skills come from

| Option | Effect | Why it exists |
|---|---|---|
| `--source github` | Downloads `main` tarball from the public repo (default) | No clone needed; always current |
| `--ref REF` | Pins the github source to a branch/tag/sha | Reproducible installs; test a PR before adopting it |
| `--source-dir PATH` | Uses a local Proofpunk checkout | Offline work; installing your own edits before pushing them |

## Selection options

| Option | Effect | Why it exists |
|---|---|---|
| `--only a,b,c` | Installs just those skills (default: all 18) | Surgical updates — e.g. after a doctrine change you only need `--override` on skills that cite it, or you want just `session-intent` today |
| `--list` | Prints skills in the source and exits | Answer "what would I get?" without touching anything |
| `--skip-skills` | Installs no skills (doctrine is skipped too) | Themes-only or plugins-only runs — `--skip-skills --themes` touches nothing but theme directories |

## Theme and plugin options

| Option | Effect | Why it exists |
|---|---|---|
| `--themes` | Copies the 20 flat-black cyberpunk themes into every detected platform: `~/.omp/agent/themes/` (oh-my-pi), `~/.config/opencode/themes/` (OpenCode), and the Hyper modules into `~/.config/proofpunk/hyper-themes/` | One command themes every TUI you run; detection = the platform's config dir exists, its binary is on PATH, or it is the `--target` |
| `--plugins` | Installs the platform glue: OMP doctrine-guard extension to `~/.omp/agent/extensions/proofpunk.ts`; OpenCode plugin + 6 commands + 4 agents into `~/.config/opencode/`; and prints the Claude Code marketplace command | The extension/plugin files live in the repo (`plugins/proofpunk/extensions/`, `plugins/proofpunk/opencode/`); this copies them to the auto-discovery locations |

## Collision options — same-name skill already exists

| Option | Effect | Why it exists |
|---|---|---|
| *(default)* | **SKIP** and report; exit notes the count | Never clobber your existing work silently — a same-name skill might be yours, not ours |
| `--override` | Replace existing same-name skills | Intentional upgrade path |
| `--backup` | Explicitly keep `.bak-TIMESTAMP` copies on `--override` (already the default, `BACKUP=1`) | Named so a caller can restore the default after composing flags |
| `--no-backup` | With `--override`: don't keep `.bak-TIMESTAMP` | Backups are on by default because "replace" should always be reversible; disable only when the target is disposable |

The old copy moves to `.<name>.bak-YYYYMMDD-HHMMSS` next to the skills, so a
bad upgrade is one `mv` away from undone.

## Doctrine options — the ruling rules around everything

| Option | Effect | Why it exists |
|---|---|---|
| *(default: on)* | Installs/refreshes `<target>/proofpunk-doctrine/` | The skills defer to these rulings — the Iron Rule (fix the real system, never mocks), the End-User Actor Mandate (validation is driven: `curl` the running server for JSON backends, browser for UI, simulator for mobile; test runners are regression tooling, NEVER validation), what **remediation** means (reproduce → fix the root cause, never the symptom → re-validate the failure AND its blast radius with fresh evidence), the evidence contract, and the severity model |
| `--no-doctrine` | Skips the doctrine bundle | Only for updates where doctrine is unchanged and you want minimal churn |
| `--with-doctrine` | Explicitly enables the doctrine bundle (this is already the default) | Named so a caller can restore the default after composing flags; `WITH_DOCTRINE=1` in the script |
| `--inject-memory [FILE]` | Appends the rules block to the memory file of `--target`: `CLAUDE.md` for claude-code/omp, `AGENTS.md` for opencode/agents. No value = `auto` (./<memory-file> of the cwd project). An explicit path overrides | The flag the 60-second examples actually pass. Opt-in; the block is marked and re-running never duplicates it |
| `--inject-claude-md FILE` | Legacy alias of `--inject-memory FILE` | Kept so older docs and scripts still run; prefer `--inject-memory` |

## Inspection options

| Option | Effect | Why it exists |
|---|---|---|
| `--hooks` | Copy hook scripts to `~/.proofpunk/hooks` and merge every `hooks.json` registration into the platform settings file (`~/.claude/settings.json` for Claude Code). Default is off (`WITH_HOOKS=0`) | Opt-in because hooks write a shared settings file. Idempotent; expect 12 registrations. OpenCode/OMP get enforcement via plugin/extension glue instead — this flag prints guidance there, it does not merge their settings |
| `--dry-run` | Prints the full plan, changes nothing | See exactly what a command would do — including which skills would SKIP vs INSTALL vs REPLACE — before you let it |
| `--verify` | Explicitly enables post-install checks (already the default, `VERIFY=1`) | Named so a caller can restore the default after composing flags |
| `--no-verify` | Skips post-install checks | The verifier asserts every installed skill has valid SKILL.md frontmatter AND that every cited `references/`,`scripts/`,`assets/`,`examples/` path resolves. It's on by default because an unverified install is an UNVERIFIED install |
| `--quiet` | Minimal output | CI/log-friendly |
| `-h, --help` | Usage summary | |

## Literal examples, with what happens

```bash
# 1) First-time Claude Code install — 18 skills + doctrine, verified:
bash proofpunk-install.sh --target claude-code
#   INSTALL brainstorm … INSTALL visual-inspection
#   doctrine   : ~/.claude/skills/proofpunk-doctrine
#   verify     : all installed skills pass frontmatter + reference checks
#   == summary: 18 installed, 0 replaced, 0 skipped (collision), 0 missing ==

# 2) oh-my-pi, look before you leap — nothing is written:
bash proofpunk-install.sh --target omp --themes --plugins --dry-run
#   target dir : ~/.omp/agent/skills  (omp)
#   [dry-run] would download …/main … INSTALL … for each skill
#   [dry-run] mkdir -p '$HOME/.omp/agent/themes' … extension …

# 3) Routine upgrade, backups kept — existing same-name skills replaced:
bash proofpunk-install.sh --target claude-code --override
#   REPLACE session-intent (old copy -> ~/.claude/skills/.session-intent.bak-20260810-034014)

# 4) Just the new skill from v1.2.0, nothing else touched:
bash proofpunk-install.sh --target claude-code --only session-intent

# 5) Re-run after a full install — everything collides, everything skips:
bash proofpunk-install.sh --target claude-code
#   SKIP brainstorm (already exists; use --override to replace) ×17
#   == summary: 0 installed, 0 replaced, 18 skipped (collision), 0 missing ==

# 6) Offline / dev loop — install your local edits:
git clone https://github.com/krzemienski/proofpunk && cd proofpunk
#   …edit a skill…
bash tools/proofpunk-install.sh --source-dir . --dir /tmp/test-skills
#   verify     : all installed skills pass … (fails loudly if you broke a link)

# 7) Put the rules in the agent's standing instructions (opt-in, idempotent):
bash proofpunk-install.sh --inject-memory ~/.claude/CLAUDE.md
bash proofpunk-install.sh --inject-memory ~/.claude/CLAUDE.md   # second run:
#   already present — left unchanged
# `--inject-claude-md FILE` is a legacy alias of the same flag and still runs.

# 8) CI pin — exact ref, minimal output, non-zero exit on any gap:
#    Live tags on this repo are v2.1.0, v2.2.0, and v3.0.0 (v1.8.0 does not resolve).
bash proofpunk-install.sh --ref v3.0.0 --quiet || exit 1

# 9) Themes only, into whatever TUIs exist on this machine:
bash proofpunk-install.sh --skip-skills --themes
#   themes     : 20 flat-black cyberpunk themes
#     OMP      -> ~/.omp/agent/themes (20) — select via /theme or theme.dark in config.yml
#     OpenCode -> ~/.config/opencode/themes (20) — select via /themes or tui.json
#     Hyper    -> ~/.config/proofpunk/hyper-themes (20 .js modules)

# 10) Full OpenCode setup from a local checkout:
bash tools/proofpunk-install.sh --source-dir . --target opencode --themes --plugins
#   skills + doctrine into ~/.config/opencode/skills, 20 themes,
#   plugin/proofpunk.ts + 6 commands + 4 agents into ~/.config/opencode/
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All selected skills installed (or would-be, with `--dry-run`); `--list` and `--help` also exit 0 |
| 1 | Usage error (`die`), download failure, missing source, missing `tar`/`curl`, or post-install verification failed |
| 3 | A `--only` name doesn't exist in the source (nothing partial is claimed) |

## Requirements

`bash`, plus `curl` (only for `--source github` — the default) and `tar`
(required for all real installs — local copies use tar pipes too).
`python3` is required by `--hooks` (settings.json merge) and otherwise
optional; without it the frontmatter checks in `--verify` still run, but
reference-resolution checks are skipped.

`tools/build-site.py` (regenerating `docs/*.html`, not part of install)
additionally requires **PyYAML** (`pip install pyyaml`) and the **pandoc**
binary (`brew install pandoc`) on `PATH`. It checks both up front and exits
with an actionable message naming whichever is missing.

## After install: using the skills

Invoke as `/skill-name <positional> --flag` in Claude Code — e.g.
`/implement "add billing webhooks" --parallel --auto --mine`,
`/prompt-forge rate prompts/login.md --in-place`,
`/codebase-truth-audit /path/to/repo --label q3-audit`.
Full per-skill usage: `plugins/proofpunk/docs/usage-guide.md`.
