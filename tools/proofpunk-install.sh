#!/usr/bin/env bash
# proofpunk-install.sh — install the 19 Proofpunk skills as PLAIN skills
# (not a plugin/marketplace) into a target skills directory of your choice,
# with collision safety, doctrine injection, and post-install verification.
# Optionally also installs the 20-theme flat-black cyberpunk pack and the
# platform plugin glue (oh-my-pi extension, OpenCode plugin/commands/agents).
#
# Quick start:
#   bash proofpunk-install.sh --target claude-code
#   bash proofpunk-install.sh --target omp --themes --plugins
#   bash proofpunk-install.sh --target opencode --themes --plugins --dry-run
# Full docs with literal examples and per-flag rationale: tools/INSTALL.md
# in the repo (https://github.com/krzemienski/proofpunk).

set -euo pipefail

# ---------------------------------------------------------------- defaults --
TARGET="claude-code"            # claude-code | omp | opencode | agents
DIR=""                          # explicit install dir (wins over --target)
SOURCE="github"                 # github | local
SOURCE_DIR=""                   # local Proofpunk repo checkout
REF="main"                      # git ref for --source github
ONLY=""                         # comma-separated skill filter
LIST=0
OVERRIDE=0
BACKUP=1
WITH_DOCTRINE=1
INJECT_CLAUDE_MD=""             # legacy alias of --inject-memory
INJECT_MEMORY=""                # '' | 'auto' | explicit file path
DRY_RUN=0
VERIFY=1
QUIET=0
WITH_HOOKS=0                    # install enforcement hooks into platform settings
SKIP_SKILLS=0                   # themes/plugins only
WITH_THEMES=0                   # install the 20-theme pack into detected TUIs
WITH_PLUGINS=0                  # install OMP extension + OpenCode plugin glue

REPO_TARBALL="https://codeload.github.com/krzemienski/proofpunk/tar.gz/refs/heads"
SKILLS_SUBPATH="plugins/proofpunk/skills"
REFS_SUBPATH="plugins/proofpunk/references"
THEMES_SUBPATH="plugins/proofpunk/themes"
OPENCODE_SUBPATH="plugins/proofpunk/opencode"
EXTENSIONS_SUBPATH="plugins/proofpunk/extensions"
DOCTRINE_DIRNAME="proofpunk-doctrine"

ALL_SKILLS="brainstorm codebase-truth-audit cook end-user-testing full-functional-audit functional-validation implement mobile-validation-runner plan-hardening production-readiness prompt-forge red-team-eval root-cause-debugging session-intent stack-testing tui-testing ui-experience-audit validation-plan visual-inspection"

# ------------------------------------------------------------------- utils --
say()  { [ "$QUIET" -eq 0 ] && printf '%s\n' "$*" || true; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run()  { if [ "$DRY_RUN" -eq 1 ]; then say "  [dry-run] $*"; else eval "$@"; fi; }

usage() { sed -n '2,12p' "$0"; cat <<'EOF'

USAGE: bash proofpunk-install.sh [options]

TARGET (where skills go):
  --target claude-code   ~/.claude/skills                     (default; also
                         read by OpenCode and OMP via their Claude-compatible
                         skill providers)
  --target omp           ${PROOFPUNK_OMP_DIR:-~/.omp/agent/skills}
                         (oh-my-pi native skill provider)
  --target opencode      ~/.config/opencode/skills            (OpenCode native)
  --target agents        ~/.agents/skills                     (shared OMP +
                         OpenCode agents-compatible location)
  --dir PATH             any explicit directory (beats --target)

SOURCE (where skills come from):
  --source github        latest tarball from GitHub           (default)
  --ref REF              branch/tag for github source         (default: main)
  --source-dir PATH      local Proofpunk checkout (offline / dev)

SELECTION:
  --only a,b,c           install just these skills (default: all 19)
  --skip-skills          install no skills (use with --themes/--plugins)
  --list                 print skills available in the source, then exit

THEMES & PLUGINS:
  --themes               install the 20 flat-black cyberpunk themes into
                         every detected TUI (oh-my-pi ~/.omp/agent/themes,
                         OpenCode ~/.config/opencode/themes) and the Hyper
                         modules into ~/.config/proofpunk/hyper-themes
  --plugins              install platform glue: OMP doctrine-guard extension
                         (~/.omp/agent/extensions) and the OpenCode plugin,
                         commands, and agents (~/.config/opencode); also
                         prints the Claude Code marketplace install command

COLLISIONS (same-name skill already exists):
  (default)              SKIP it and report — nothing is clobbered silently
  --override             replace existing same-name skills
  --no-backup            with --override: don't keep a .bak-TIMESTAMP copy

DOCTRINE (the ruling rules):
  --no-doctrine          skip installing the proofpunk-doctrine/ bundle
  --inject-memory [F]    append the rules block to the memory file of the
                         --target platform: CLAUDE.md for claude-code/omp,
                         AGENTS.md for opencode/agents (researched
                         conventions, see INSTALL.md). F overrides the file.
                         No value = auto: ./<memory-file> of the cwd project
  --inject-claude-md F   legacy alias of '--inject-memory F'

HOOKS (deterministic enforcement — plugin installs get them automatically):
  --hooks                copy hook scripts to ~/.proofpunk/hooks and merge them
                         into the platform's settings file (claude-code:
                         ~/.claude/settings.json — Stop/SubagentStop unproven-
                         claim guard + PreToolUse secrets-in-evidence guard).
                         Idempotent; opencode/omp get enforcement via their
                         plugin/extension glue (printed guidance instead).

INSPECTION:
  --dry-run              print the full plan, change nothing
  --no-verify            skip post-install SKILL.md/reference checks
  --quiet                minimal output
  -h, --help             this help
EOF
}

# ------------------------------------------------------------------ args --
while [ $# -gt 0 ]; do
  case "$1" in
    --target)            TARGET="${2:?--target needs a value}"; shift 2;;
    --dir)               DIR="${2:?--dir needs a value}"; shift 2;;
    --source)            SOURCE="${2:?--source needs a value}"; shift 2;;
    --source-dir)        SOURCE="local"; SOURCE_DIR="${2:?--source-dir needs a value}"; shift 2;;
    --ref)               REF="${2:?--ref needs a value}"; shift 2;;
    --only)              ONLY="${2:?--only needs a value}"; shift 2;;
    --skip-skills)       SKIP_SKILLS=1; shift;;
    --list)              LIST=1; shift;;
    --themes)            WITH_THEMES=1; shift;;
    --plugins)           WITH_PLUGINS=1; shift;;
    --override)          OVERRIDE=1; shift;;
    --backup)            BACKUP=1; shift;;
    --no-backup)         BACKUP=0; shift;;
    --with-doctrine)     WITH_DOCTRINE=1; shift;;
    --no-doctrine)       WITH_DOCTRINE=0; shift;;
    --inject-claude-md)  INJECT_CLAUDE_MD="${2:?--inject-claude-md needs a file}"; shift 2;;
    --inject-memory)     if [ $# -gt 1 ] && [ "${2#--}" = "$2" ]; then INJECT_MEMORY="$2"; shift 2; else INJECT_MEMORY="auto"; shift; fi;;
    --inject-memory=*)   INJECT_MEMORY="${1#*=}"; shift;;
    --dry-run)           DRY_RUN=1; shift;;
    --verify)            VERIFY=1; shift;;
    --no-verify)         VERIFY=0; shift;;
    --quiet)             QUIET=1; shift;;
    --hooks)             WITH_HOOKS=1; shift;;
    -h|--help)           usage; exit 0;;
    *) die "unknown option: $1 (try --help)";;
  esac
done

# ----------------------------------------------------------------- target --
if [ -z "$DIR" ]; then
  case "$TARGET" in
    claude-code) DIR="$HOME/.claude/skills";;
    omp)         DIR="${PROOFPUNK_OMP_DIR:-$HOME/.omp/agent/skills}";;
    opencode)    DIR="$HOME/.config/opencode/skills";;
    agents)      DIR="$HOME/.agents/skills";;
    *) die "--target must be claude-code, omp, opencode, or agents (got '$TARGET')";;
  esac
fi
say "== Proofpunk installer =="
say "target dir : $DIR  ($TARGET)"

# ----------------------------------------------------------------- source --
WORK=""
cleanup() { if [ -n "$WORK" ]; then rm -rf "$WORK"; fi; return 0; }
trap cleanup EXIT

if [ "$SOURCE" = "github" ]; then
  command -v curl >/dev/null || die "curl required for --source github (or use --source-dir)"
  command -v tar  >/dev/null || die "tar required for --source github (or use --source-dir)"
  WORK="$(mktemp -d)"
  say "source     : github tarball (ref: $REF)"
  if [ "$DRY_RUN" -eq 0 ]; then
    curl -fsSL "$REPO_TARBALL/$REF" -o "$WORK/repo.tar.gz" || die "download failed (check --ref $REF)"
    tar -xzf "$WORK/repo.tar.gz" -C "$WORK"
    # GitHub codeload tarballs contain exactly one top-level directory named
    # <repo>-<ref>: the repo name lowercased, tag refs lose their leading 'v',
    # branch names keep slashes flattened. Do NOT pattern-match the name —
    # any repo rename or ref form must keep working. The skills-path check
    # below is the authoritative layout validation.
    SRC_ROOT="$(find "$WORK" -maxdepth 1 -mindepth 1 -type d | head -1)"
    [ -n "$SRC_ROOT" ] || die "unexpected tarball layout (no root dir)"
    [ "$(find "$WORK" -maxdepth 1 -mindepth 1 -type d | wc -l)" -eq 1 ] || die "unexpected tarball layout (multiple root dirs)"
  else
    say "  [dry-run] would download $REPO_TARBALL/$REF"
    SRC_ROOT="(github:$REF)"
  fi
else
  [ -d "$SOURCE_DIR" ] || die "--source-dir '$SOURCE_DIR' is not a directory"
  SRC_ROOT="$SOURCE_DIR"
  say "source     : local checkout $SRC_ROOT"
fi

SKILLS_SRC="$SRC_ROOT/$SKILLS_SUBPATH"
REFS_SRC="$SRC_ROOT/$REFS_SUBPATH"
if [ "$DRY_RUN" -eq 0 ]; then
  [ -d "$SKILLS_SRC" ] || die "skills not found at $SKILLS_SRC"
fi

# ------------------------------------------------------------- selection --
if [ "$SKIP_SKILLS" -eq 1 ]; then
  SELECTED=""
elif [ -n "$ONLY" ]; then
  SELECTED="$(printf '%s' "$ONLY" | tr ',' ' ')"
else
  SELECTED="$ALL_SKILLS"
fi

if [ "$LIST" -eq 1 ]; then
  if [ "$DRY_RUN" -eq 0 ] && [ -d "$SKILLS_SRC" ]; then
    say "skills available in source:"
    for d in "$SKILLS_SRC"/*/; do
      [ -f "$d/SKILL.md" ] && printf '  %s\n' "$(basename "$d")"
    done
  else
    say "skills that would be available: $ALL_SKILLS"
  fi
  exit 0
fi

# --------------------------------------------------------------- install --
INSTALLED=0; SKIPPED=0; REPLACED=0; MISSING=0
if [ -n "$SELECTED" ]; then
say "installing : $(printf '%s' "$SELECTED" | wc -w | tr -d ' ') skill(s)"
run "mkdir -p '$DIR'"

for skill in $SELECTED; do
  src="$SKILLS_SRC/$skill"
  dst="$DIR/$skill"
  if [ "$DRY_RUN" -eq 0 ] && [ ! -f "$src/SKILL.md" ]; then
    warn "source has no skill named '$skill' — skipped"
    MISSING=$((MISSING+1)); continue
  fi
  if [ -d "$dst" ]; then
    if [ "$OVERRIDE" -eq 0 ]; then
      say "  SKIP    $skill (already exists; use --override to replace)"
      SKIPPED=$((SKIPPED+1)); continue
    fi
    if [ "$BACKUP" -eq 1 ]; then
      bak="$DIR/.${skill}.bak-$(date +%Y%m%d-%H%M%S)"
      run "mv '$dst' '$bak'"
      say "  REPLACE $skill (old copy -> $bak)"
    else
      run "rm -rf '$dst'"
      say "  REPLACE $skill (no backup)"
    fi
    REPLACED=$((REPLACED+1))
  else
    say "  INSTALL $skill"
  fi
  run "mkdir -p '$dst'"
  if [ "$DRY_RUN" -eq 0 ]; then
    (cd "$src" && tar cf - .) | (cd "$dst" && tar xf -)
    # Make the installed copy SELF-CONTAINED: the repo layout cites shared
    # doctrine as ../../references/X (plugin structure). In a plain skills
    # dir that path escapes the skill — so rewrite citations to references/X
    # and bundle each cited shared reference INSIDE the skill.
    find "$dst" -name '*.md' -exec sed -i.bak \
      -e 's|\.\./\.\./\.\./references/|../references/|g' \
      -e 's|\.\./\.\./references/|references/|g' {} \;
    find "$dst" -name '*.bak' -delete
    if [ -d "$REFS_SRC" ]; then
      mkdir -p "$dst/references"
      for ref in "$REFS_SRC"/*; do
        name="$(basename "$ref")"
        if grep -rq "references/$name" "$dst" --include='*.md'; then
          [ -f "$dst/references/$name" ] || cp "$ref" "$dst/references/$name"
        fi
      done
    fi
  fi
  INSTALLED=$((INSTALLED+1))
done
else
  say "installing : no skills (--skip-skills)"
fi

# ----------------------------------------------------------------- themes --
if [ "$WITH_THEMES" -eq 1 ]; then
  THEMES_SRC="$SRC_ROOT/$THEMES_SUBPATH"
  if [ "$DRY_RUN" -eq 0 ] && [ ! -d "$THEMES_SRC/omp" ]; then
    die "themes not found at $THEMES_SRC (bad source?)"
  fi
  say "themes     : 20 flat-black cyberpunk themes"
  # oh-my-pi: detected by ~/.omp or an omp binary on PATH
  if [ -d "$HOME/.omp" ] || command -v omp >/dev/null 2>&1 || [ "$TARGET" = "omp" ]; then
    run "mkdir -p '$HOME/.omp/agent/themes'"
    if [ "$DRY_RUN" -eq 0 ]; then cp "$THEMES_SRC/omp/"*.json "$HOME/.omp/agent/themes/"; fi
    say "  OMP      -> ~/.omp/agent/themes (20) — select via /theme or theme.dark in config.yml"
  fi
  # OpenCode: detected by ~/.config/opencode or an opencode binary on PATH
  if [ -d "$HOME/.config/opencode" ] || command -v opencode >/dev/null 2>&1 || [ "$TARGET" = "opencode" ]; then
    run "mkdir -p '$HOME/.config/opencode/themes'"
    if [ "$DRY_RUN" -eq 0 ]; then cp "$THEMES_SRC/opencode/"*.json "$HOME/.config/opencode/themes/"; fi
    say "  OpenCode -> ~/.config/opencode/themes (20) — select via /themes or tui.json"
  fi
  # Hyper terminal modules: copy + show how to activate (Hyper has no theme dir)
  run "mkdir -p '$HOME/.config/proofpunk/hyper-themes'"
  if [ "$DRY_RUN" -eq 0 ]; then cp "$THEMES_SRC/hyper/"*.js "$HOME/.config/proofpunk/hyper-themes/"; fi
  say "  Hyper    -> ~/.config/proofpunk/hyper-themes (20 .js modules)"
  say "           activate: require one from a local plugin, or merge its COLORS into ~/.hyper.js"
fi

# ---------------------------------------------------------------- plugins --
if [ "$WITH_PLUGINS" -eq 1 ]; then
  say "plugins    : platform glue"
  # OMP doctrine-guard extension (native auto-discovery at ~/.omp/agent/extensions)
  if [ -d "$HOME/.omp" ] || command -v omp >/dev/null 2>&1 || [ "$TARGET" = "omp" ]; then
    run "mkdir -p '$HOME/.omp/agent/extensions'"
    if [ "$DRY_RUN" -eq 0 ]; then cp "$SRC_ROOT/$EXTENSIONS_SUBPATH/proofpunk.ts" "$HOME/.omp/agent/extensions/"; fi
    say "  OMP extension      -> ~/.omp/agent/extensions/proofpunk.ts"
    say "  OMP full plugin    : omp plugin marketplace add krzemienski/proofpunk && omp plugin install proofpunk@proofpunk"
  fi
  # OpenCode plugin + commands + agents
  if [ -d "$HOME/.config/opencode" ] || command -v opencode >/dev/null 2>&1 || [ "$TARGET" = "opencode" ]; then
    run "mkdir -p '$HOME/.config/opencode/plugin' '$HOME/.config/opencode/commands' '$HOME/.config/opencode/agents'"
    if [ "$DRY_RUN" -eq 0 ]; then
      cp "$SRC_ROOT/$OPENCODE_SUBPATH/plugin/proofpunk.ts" "$HOME/.config/opencode/plugin/"
      cp "$SRC_ROOT/$OPENCODE_SUBPATH/commands/"*.md "$HOME/.config/opencode/commands/"
      cp "$SRC_ROOT/$OPENCODE_SUBPATH/agents/"*.md "$HOME/.config/opencode/agents/"
    fi
    say "  OpenCode plugin    -> ~/.config/opencode/plugin/proofpunk.ts (+6 commands, 1 agent)"
    say "  OpenCode skills    : shared from ~/.claude/skills — re-run with --target claude-code if missing"
  fi
  # Claude Code full plugin = marketplace install (skills alone are plain)
  say "  Claude Code plugin : /plugin marketplace add krzemienski/proofpunk && /plugin install proofpunk@proofpunk-marketplace"
fi

# ------------------------------------------------------------------ hooks --
if [ "$WITH_HOOKS" -eq 1 ]; then
  HOOKS_SRC="$SRC_ROOT/plugins/proofpunk/hooks"
  HOOK_HOME="$HOME/.proofpunk/hooks"
  say "hooks      : enforcement hooks (Stop/SubagentStop + PreToolUse)"
  if [ "$TARGET" = "claude-code" ] || [ "$TARGET" = "omp" ] || [ "$TARGET" = "agents" ]; then
    run "mkdir -p '$HOOK_HOME'"
    if [ "$DRY_RUN" -eq 0 ]; then
      cp "$HOOKS_SRC/stop-guard.sh" "$HOOKS_SRC/evidence-guard.sh" "$HOOKS_SRC/instructions-loaded.sh" "$HOOKS_SRC/no-test-files.sh" "$HOOKS_SRC/post-write-walkthrough.sh" "$HOOK_HOME/"
      chmod +x "$HOOK_HOME/"*.sh
      # Idempotent settings.json merge (user-level for claude-code).
      SETTINGS="$HOME/.claude/settings.json"
      [ "$TARGET" = "agents" ] && SETTINGS="$HOME/.agents/settings.json"
      python3 - "$SETTINGS" "$HOOK_HOME" <<'PYEOF'
import json, os, shutil, sys, time

settings_path, hook_home = sys.argv[1], sys.argv[2]
os.makedirs(os.path.dirname(settings_path), exist_ok=True)
settings = {}
if os.path.exists(settings_path):
    with open(settings_path) as f:
        try:
            settings = json.load(f)
        except json.JSONDecodeError:
            backup = settings_path + ".corrupt-" + str(int(time.time()))
            shutil.copy2(settings_path, backup)
            print(f"  WARN: existing settings.json was corrupt; backed up to {backup}")
            settings = {}
hooks = settings.setdefault("hooks", {})

def ensure(event, command, matcher=None, timeout=10):
    entries = hooks.setdefault(event, [])
    for e in entries:
        for h in e.get("hooks", []):
            if ".proofpunk/hooks" in h.get("command", ""):
                return "already present"
    entry = {"hooks": [{"type": "command", "command": command, "timeout": timeout}]}
    if matcher is not None:
        entry["matcher"] = matcher
    entries.append(entry)
    return "added"

results = [
    ("Stop", ensure("Stop", f"sh {hook_home}/stop-guard.sh")),
    ("SubagentStop", ensure("SubagentStop", f"sh {hook_home}/stop-guard.sh")),
    ("PreToolUse:no-test-files", ensure("PreToolUse", f"sh {hook_home}/no-test-files.sh", matcher="Write|Edit", timeout=5)),
    ("PreToolUse:evidence-guard", ensure("PreToolUse", f"sh {hook_home}/evidence-guard.sh", matcher="Write|Edit", timeout=5)),
    ("PostToolUse", ensure("PostToolUse", f"sh {hook_home}/post-write-walkthrough.sh", matcher="Write|Edit", timeout=5)),
]
if os.path.exists(settings_path):
    shutil.copy2(settings_path, settings_path + ".bak")
with open(settings_path, "w") as f:
    json.dump(settings, f, indent=2)
for ev, r in results:
    print(f"  {ev}: {r}")
print(f"  settings: {settings_path}")
PYEOF
    else
      say "  [dry-run] would install 3 hook scripts to $HOOK_HOME and merge Stop/SubagentStop/PreToolUse into the platform settings.json"
    fi
  else
    say "  opencode: enforcement lives in the plugin glue (install with --plugins; see opencode/plugin/proofpunk.ts)"
    say "  omp     : enforcement lives in the doctrine-guard extension (--plugins; extensions/proofpunk.ts)"
  fi
fi

# --------------------------------------------------------------- doctrine --
if [ "$WITH_DOCTRINE" -eq 1 ] && [ "$SKIP_SKILLS" -eq 0 ]; then
  DD="$DIR/$DOCTRINE_DIRNAME"
  say "doctrine   : $DD (the ruling rules every skill defers to)"
  run "mkdir -p '$DD'"
  if [ "$DRY_RUN" -eq 0 ]; then
    [ -d "$REFS_SRC" ] || die "doctrine references not found at $REFS_SRC"
    (cd "$REFS_SRC" && tar cf - .) | (cd "$DD" && tar xf -)
    cat > "$DD/README.md" <<'DEOF'
# Proofpunk doctrine — the ruling rules

Every Proofpunk skill defers to these shared rulings. Read
`end-user-actor.md` first. The short version:

1. **The Iron Rule** — if the real system doesn't work, fix the real system.
   Never mocks, stubs, test doubles, fake endpoints, or test-mode bypasses.
2. **End-User Actor Mandate** — validation is driven, never assumed. The AI
   personally drives the live system as the end user: `curl` to the running
   server for JSON/HTTP backends, the browser for UI, the simulator for
   mobile. Test runners (pytest et al.) are REGRESSION tooling, never
   validation. Unexecuted validation is UNVERIFIED, never PASS.
3. **Remediation** means: reproduce first, fix the ROOT CAUSE in the real
   system (never the symptom — no retries, sleeps, swallowed exceptions),
   then re-validate the original failure AND its blast radius as the end
   user, with fresh evidence sealed per `evidence-contract.md`.
4. **Fresh evidence** — run-scoped, sequential, non-empty, cited by full
   path with a description of what is SEEN. See `evidence-contract.md`.
5. **Severities** — every finding carries one; HIGH/CRITICAL block.
   See `severity-model.md`.
DEOF
  fi
fi

# Legacy alias folds into the unified flag.
if [ -z "$INJECT_MEMORY" ] && [ -n "$INJECT_CLAUDE_MD" ]; then
  INJECT_MEMORY="$INJECT_CLAUDE_MD"
fi

if [ -n "$INJECT_MEMORY" ]; then
  # Target-aware memory file (verified 2026-08-13: Claude Code reads
  # CLAUDE.md + .claude/rules/*; OpenCode reads AGENTS.md project +
  # ~/.config/opencode/AGENTS.md global and falls back to CLAUDE.md only
  # when no AGENTS.md exists; Codex-style agents read AGENTS.md; OMP reads
  # the Claude-compatible memory chain).
  case "$TARGET" in
    opencode|agents) MEMFILE_DEFAULT="AGENTS.md";;
    *)               MEMFILE_DEFAULT="CLAUDE.md";;
  esac
  if [ "$INJECT_MEMORY" = "auto" ]; then
    MEMFILE="$PWD/$MEMFILE_DEFAULT"
  else
    MEMFILE="$INJECT_MEMORY"
  fi
  say "rules block: $MEMFILE (platform default for $TARGET: $MEMFILE_DEFAULT; idempotent)"
  if [ "$DRY_RUN" -eq 0 ]; then
    touch "$MEMFILE"
    if grep -q 'BEGIN PROOFPUNK RULES' "$MEMFILE"; then
      say "  already present — left unchanged"
    else
      # OpenCode/AGENTS.md has no automatic @path loading — the block tells
      # the agent to load the doctrine on demand instead (per opencode docs).
      if [ "$MEMFILE_DEFAULT" = "AGENTS.md" ]; then
        cat >> "$MEMFILE" <<'CEOF'

<!-- BEGIN PROOFPUNK RULES (installed by proofpunk-install.sh) -->
## Proofpunk operating rules
- Iron Rule: fix the real system; never mocks, stubs, test doubles, or
  test-mode bypasses.
- End-User Actor Mandate: validate by driving the live system as the end
  user. Test runners are regression tooling, never validation.
  Unexecuted = UNVERIFIED, never PASS.
- Remediation = reproduce, fix the root cause (never the symptom),
  re-validate the original failure and its blast radius with fresh evidence.
- Evidence: fresh, run-scoped, non-empty, cited by full path.
- On first use of a proofpunk skill, load its bundled doctrine from
  proofpunk-doctrine/README.md on a need-to-know basis (AGENTS.md has no
  automatic @-imports — load files explicitly, do not preload).
<!-- END PROOFPUNK RULES -->
CEOF
      else
        cat >> "$MEMFILE" <<'CEOF'

<!-- BEGIN PROOFPUNK RULES (installed by proofpunk-install.sh) -->
## Proofpunk operating rules
- Iron Rule: fix the real system; never mocks, stubs, test doubles, or
  test-mode bypasses.
- End-User Actor Mandate: validate by driving the live system as the end
  user (curl the running server for JSON/HTTP backends, browser for UI,
  simulator for mobile). Test runners are regression tooling, never
  validation. Unexecuted = UNVERIFIED, never PASS.
- Remediation = reproduce, fix the root cause (never the symptom),
  re-validate the original failure and its blast radius with fresh evidence.
- Evidence: fresh, run-scoped, non-empty, cited by full path.
<!-- END PROOFPUNK RULES -->
CEOF
      fi
      say "  appended (marked block; safe to re-run)"
    fi
  else
    say "  [dry-run] would append the marked rules block to $MEMFILE"
  fi
fi

# ----------------------------------------------------------------- verify --
if [ "$VERIFY" -eq 1 ] && [ "$DRY_RUN" -eq 0 ]; then
  FAIL=0
  for skill in $SELECTED; do
    dst="$DIR/$skill"
    [ -d "$dst" ] || continue
    if [ ! -f "$dst/SKILL.md" ]; then
      warn "verify: $dst/SKILL.md missing"; FAIL=1; continue
    fi
    if command -v python3 >/dev/null 2>&1; then
      python3 - "$dst" <<'PYEOF' || FAIL=1
import re, sys, os
dst = sys.argv[1]
text = open(os.path.join(dst, 'SKILL.md'), encoding='utf-8').read()
assert text.startswith('---'), 'no frontmatter'
fm = re.match(r'^---\n(.*?)\n---', text, re.DOTALL).group(1)
assert re.search(r'^name:\s*\S+', fm, re.M), 'no name'
assert re.search(r'^description:', fm, re.M), 'no description'
# every cited references/ path inside the skill must resolve
bad = []
for dp, _, fns in os.walk(dst):
    for fn in fns:
        if not fn.endswith('.md'): continue
        p = os.path.join(dp, fn)
        for m in re.finditer(r'`((?:\.\./)*(?:references|scripts|assets|examples)/[^`\s]+)`',
                             open(p, encoding='utf-8').read()):
            t = m.group(1).split('#')[0]
            if '<' in t or '{' in t or '*' in t: continue
            if not os.path.exists(os.path.normpath(os.path.join(dp, t))):
                bad.append(f'{fn} -> {t}')
if bad:
    print('verify BROKEN refs:', bad[:5]); sys.exit(1)
PYEOF
    fi
  done
  [ "$FAIL" -eq 0 ] && say "verify     : all installed skills pass frontmatter + reference checks" \
                    || die "verification failed (see WARN lines)"
fi

# ---------------------------------------------------------------- summary --
say "== summary: $INSTALLED installed, $REPLACED replaced, $SKIPPED skipped (collision), $MISSING missing =="
[ "$SKIPPED" -gt 0 ] && say "   re-run with --override to replace skipped skills"
[ "$MISSING" -gt 0 ] && exit 3 || true
exit 0
