> Incorporated from the `preflight` skill (skills-ref.zip).

# Preflight Check

Run before starting any major work session to catch common blockers early.

## Step 1: Detect Project Type

```bash
# Auto-detect platform
HAS_IOS=0; HAS_WEB=0; HAS_API=0; HAS_CLI=0
[ -n "$(find . -maxdepth 3 -name '*.xcodeproj' 2>/dev/null | head -1)" ] && HAS_IOS=1
[ -n "$(find . -maxdepth 3 -name '*.tsx' -o -name '*.jsx' -o -name 'next.config*' 2>/dev/null | head -1)" ] && HAS_WEB=1
[ -n "$(find . -maxdepth 3 -name 'routes*' -o -name 'controllers*' 2>/dev/null | head -1)" ] && HAS_API=1
[ -f package.json ] && grep -q '"bin"' package.json 2>/dev/null && HAS_CLI=1
echo "iOS=$HAS_IOS Web=$HAS_WEB API=$HAS_API CLI=$HAS_CLI"
```

## Step 2: Universal Checks

1. **Git status**: `git status` — check for uncommitted changes, detached HEAD
2. **Git worktrees**: `git worktree list` — check each for uncommitted changes
3. **Node/Bun available**: `node --version && bun --version 2>/dev/null`
4. **Disk space**: `df -h .` — ensure not critically low

## Step 3: Platform-Specific Checks

### Web / Full-Stack (Next.js)
1. **Dev server**: `curl -sf http://localhost:3000 > /dev/null && echo "UP" || echo "DOWN"`
2. **Database**: `pg_isready -h localhost 2>&1 || echo "DB DOWN"`
3. **Env file**: `[ -f .env.local ] && echo "ENV: exists" || echo "ENV: MISSING"`
4. **Dependencies**: `[ -d node_modules ] && echo "DEPS: installed" || echo "DEPS: run bun install"`
5. **Build cache**: Check if Turbopack cache is stale after route changes
6. **Playwright**: `npx playwright --version 2>/dev/null || echo "Playwright: NOT INSTALLED"`

### iOS / macOS
1. **Simulator**: `xcrun simctl list devices booted`
2. **Xcode**: `xcodebuild -version`
3. **Backend**: `curl -sf http://localhost:9090/api/v1/health 2>/dev/null`

### API-only
1. **Server**: `curl -sf http://localhost:$PORT/health`
2. **Database**: `pg_isready`
3. **Redis**: `redis-cli ping 2>/dev/null || echo "Redis: DOWN (degraded mode)"`

### CLI
1. **Binary exists**: Check for compiled binary or build script
2. **Dependencies**: Language-specific package manager check

## Step 4: SessionForge-Specific Checks

When working on SessionForge (bun monorepo with Turbo — `apps/dashboard`):
1. **Package manager**: `bun --version` — project requires bun (see `packageManager` in root package.json)
2. **Workspace deps**: `bun install` from monorepo root — installs all workspace dependencies
3. **Turbo**: `bunx turbo --version` — build orchestration for monorepo
4. **Agent SDK auth**: Verify `claude auth status` — SDK inherits from CLI (zero API keys)
5. **CLAUDECODE env**: Will be handled by `delete process.env.CLAUDECODE` in code
6. **Neon DB**: Check `DATABASE_URL` is set in `apps/dashboard/.env.local`
7. **Redis**: Upstash placeholders in local dev — degraded but functional
8. **Dev server mode**: Use `next dev` NOT `next dev --turbopack` (drizzle-orm relation bugs with Turbopack)
9. **Dev server start**: `cd apps/dashboard && bun run dev` or `bun run dev` from monorepo root (Turbo routes to workspace)

## Step 5: Summarize

Report all findings before proceeding. If any critical check fails, fix it before starting the main task.

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Skip preflight and jump straight to coding | Undetected blockers (missing deps, wrong branch, stale cache) waste hours of debugging time | Run preflight at the start of every major work session |
| Ignore critical check failures and proceed anyway | Building on a broken foundation compounds errors — every subsequent step may fail for the same root cause | Fix all critical failures before starting the main task |
| Run `next dev --turbopack` on SessionForge | Turbopack has known bugs with drizzle-orm relations resolving to undefined | Use `next dev` without `--turbopack` flag |

## When NOT to Use

- Validating feature functionality after implementation (use `end-user-testing`)
- Running structured end-to-end validation flows (use `full-functional-audit`)
- Verifying completion evidence (use `end-user-testing`)
- Debugging specific build errors (use `root-cause-debugging`)
