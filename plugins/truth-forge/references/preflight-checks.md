# Preflight Checks (shared)

Pre-session environment checks to catch blockers BEFORE validation or
implementation work begins. Condensed from the `preflight` skill
(project-specific checks removed). Run at the start of any validation or
audit session; fix critical failures before proceeding.

## Step 1 — Detect Project Type

```bash
HAS_IOS=0; HAS_WEB=0; HAS_API=0; HAS_CLI=0
[ -n "$(find . -maxdepth 3 -name '*.xcodeproj' 2>/dev/null | head -1)" ] && HAS_IOS=1
[ -n "$(find . -maxdepth 3 -name '*.tsx' -o -name '*.jsx' -o -name 'next.config*' 2>/dev/null | head -1)" ] && HAS_WEB=1
[ -n "$(find . -maxdepth 3 -name 'routes*' -o -name 'controllers*' 2>/dev/null | head -1)" ] && HAS_API=1
[ -f package.json ] && grep -q '"bin"' package.json 2>/dev/null && HAS_CLI=1
echo "iOS=$HAS_IOS Web=$HAS_WEB API=$HAS_API CLI=$HAS_CLI"
```

## Step 2 — Universal Checks

1. **Git status** — uncommitted changes, detached HEAD, wrong branch
2. **Git worktrees** — `git worktree list`; check each for uncommitted work
3. **Runtime available** — `node --version` / `python3 --version` / toolchain of record
4. **Disk space** — `df -h .` not critically low

## Step 3 — Platform-Specific Checks

### Web / Full-Stack
1. Dev server responds: `curl -sf http://localhost:<port> > /dev/null && echo UP || echo DOWN`
2. Database: `pg_isready -h localhost` (or equivalent)
3. Env file present (`.env.local` / `.env`)
4. Dependencies installed (`node_modules` exists / package env importable)
5. Browser automation available (Playwright / browser MCP / DevTools)
6. Build cache staleness after route/dependency changes

### iOS / macOS
1. Simulator booted: `xcrun simctl list devices booted`
2. Toolchain: `xcodebuild -version`
3. Backend health endpoint reachable (if the app needs one)

### API-only
1. Server: `curl -sf http://localhost:$PORT/health`
2. Database and cache (e.g. `redis-cli ping`) reachable

### CLI
1. Binary exists or build script present
2. `--help` or `--version` exits 0

## Step 4 — Summarize

Report all findings before proceeding. Any critical failure (runtime target
unreachable, missing deps, wrong branch, stale caches) is fixed FIRST —
building validation on a broken foundation compounds every later step.

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Skip preflight and jump straight to work | Undetected blockers waste hours of downstream debugging | Run preflight at the start of every major session |
| Ignore critical failures and proceed | Every later step fails for the same root cause | Fix all critical failures before the main task |
| Treat preflight as feature validation | Environment readiness != behavior proof | After preflight passes, validate with `functional-validation` — the AI driving the system as the end user |
