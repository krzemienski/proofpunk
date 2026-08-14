# Proofpunk installer — usage, options, and why they exist

`tools/proofpunk-install.sh` installs the 19 Proofpunk skills as **plain
skills** (not a plugin, not a marketplace) into the skills directory of your
choice, injects the ruling doctrine alongside them, and verifies the result.
Everything below was executed against the real script before shipping — the
outputs shown are the actual behaviors, not aspirations.

## The 60-second version

```bash
# Claude Code user, latest GitHub main, everything included:
bash proofpunk-install.sh --target claude-code

# oh-my-pi user — skills, 20 themes, and the doctrine-guard extension:
bash proofpunk-install.sh --target omp --themes --plugins

# OpenCode user — skills, 20 themes, plugin + commands + agent:
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

## What an install actually produces

```
<target>/
├── brainstorm/            # 19 skill dirs, each SELF-CONTAINED:
│   ├── SKILL.md           #    citations rewritten to references/X
│   └── references/        #    cited doctrine bundled inside the skill
│   ...
├── visual-inspection/
└── proofpunk-doctrine/  # the ruling rules, shared by all skills
    ├── README.md          #   Iron Rule / End-User Actor / remediation / evidence
    ├── end-user-actor.md  #   incl. "test runners are never validation"
    ├── evidence-contract.md
    └── ... (9 ruling references)
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
| `--plugins` | Installs the platform glue: OMP doctrine-guard extension to `~/.omp/agent/extensions/proofpunk.ts`; OpenCode plugin + 6 commands + 1 agent into `~/.config/opencode/`; and prints the Claude Code marketplace command | The extension/plugin files live in the repo (`plugins/proofpunk/extensions/`, `plugins/proofpunk/opencode/`); this copies them to the auto-discovery locations |

## Collision options — same-name skill already exists

| Option | Effect | Why it exists |
|---|---|---|
| *(default)* | **SKIP** and report; exit notes the count | Never clobber your existing work silently — a same-name skill might be yours, not ours |
| `--override` | Replace existing same-name skills | Intentional upgrade path |
| `--no-backup` | With `--override`: don't keep `.bak-TIMESTAMP` | Backups are on by default because "replace" should always be reversible; disable only when the target is disposable |

The old copy moves to `.<name>.bak-YYYYMMDD-HHMMSS` next to the skills, so a
bad upgrade is one `mv` away from undone.

## Doctrine options — the ruling rules around everything

| Option | Effect | Why it exists |
|---|---|---|
| *(default: on)* | Installs/refreshes `<target>/proofpunk-doctrine/` | The skills defer to these rulings — the Iron Rule (fix the real system, never mocks), the End-User Actor Mandate (validation is driven: `curl` the running server for JSON backends, browser for UI, simulator for mobile; test runners are regression tooling, NEVER validation), what **remediation** means (reproduce → fix the root cause, never the symptom → re-validate the failure AND its blast radius with fresh evidence), the evidence contract, and the severity model |
| `--no-doctrine` | Skips the doctrine bundle | Only for updates where doctrine is unchanged and you want minimal churn |
| `--inject-claude-md FILE` | Appends the rules block to `FILE` (e.g. `~/.claude/CLAUDE.md`) | Puts the rulings directly in the agent's standing instructions. **Opt-in** because it modifies your file; the block is marked `BEGIN/END PROOFPUNK RULES` and re-running never duplicates it (verified idempotent) |

## Inspection options

| Option | Effect | Why it exists |
|---|---|---|
| `--dry-run` | Prints the full plan, changes nothing | See exactly what a command would do — including which skills would SKIP vs INSTALL vs REPLACE — before you let it |
| `--no-verify` | Skips post-install checks | The verifier asserts every installed skill has valid SKILL.md frontmatter AND that every cited `references/`,`scripts/`,`assets/`,`examples/` path resolves. It's on by default because an unverified install is an UNVERIFIED install; skip only on systems without python3 (frontmatter checks still run, reference checks are skipped with a note) |
| `--quiet` | Minimal output | CI/log-friendly |
| `-h, --help` | Usage summary | | |

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
git clone https://github.com/krzemienski/proofpunk && cd Proofpunk
#   …edit a skill…
bash tools/proofpunk-install.sh --source-dir . --dir /tmp/test-skills
#   verify     : all installed skills pass … (fails loudly if you broke a link)

# 7) Put the rules in the agent's standing instructions (opt-in, idempotent):
bash proofpunk-install.sh --inject-claude-md ~/.claude/CLAUDE.md
bash proofpunk-install.sh --inject-claude-md ~/.claude/CLAUDE.md   # second run:
#   already present — left unchanged

# 8) CI pin — exact ref, minimal output, non-zero exit on any gap:
bash proofpunk-install.sh --ref v1.8.0 --quiet || exit 1

# 9) Themes only, into whatever TUIs exist on this machine:
bash proofpunk-install.sh --skip-skills --themes
#   themes     : 20 flat-black cyberpunk themes
#     OMP      -> ~/.omp/agent/themes (20) — select via /theme or theme.dark in config.yml
#     OpenCode -> ~/.config/opencode/themes (20) — select via /themes or tui.json
#     Hyper    -> ~/.config/proofpunk/hyper-themes (20 .js modules)

# 10) Full OpenCode setup from a local checkout:
bash tools/proofpunk-install.sh --source-dir . --target opencode --themes --plugins
#   skills + doctrine into ~/.config/opencode/skills, 20 themes,
#   plugin/proofpunk.ts + 6 commands + 1 agent into ~/.config/opencode/
```

## Exit codes

| Code | Meaning |
|---|---|
| 0 | All selected skills installed (or would-be, with `--dry-run`) |
| 1 | Usage error, download failure, missing source, or post-install verification failed |
| 2 | No transcripts/source found where expected |
| 3 | A `--only` name doesn't exist in the source (nothing partial is claimed) |

## Requirements

`bash`, plus `curl` and `tar` (only for `--source github` — the default).
`python3` is optional and used only by `--verify`'s reference-resolution
check; without it the frontmatter checks still run.

## After install: using the skills

Invoke as `/skill-name <positional> --flag` in Claude Code — e.g.
`/implement "add billing webhooks" --parallel --auto --mine`,
`/prompt-forge rate prompts/login.md --in-place`,
`/codebase-truth-audit /path/to/repo --label q3-audit`.
Full per-skill usage: `plugins/proofpunk/docs/usage-guide.md`.
