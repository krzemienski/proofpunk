> Incorporated from the `xc-mcp` skill (workflows/configure-caching.md).

# Workflow: Configure XC-MCP Caching and Persistence

<required_reading>
**Read these reference files NOW:**
1. references/caching-strategy.md
2. references/tool-reference.md
</required_reading>

<cache_architecture>
XC-MCP uses a 4-layer intelligent caching system:

1. **Simulator Cache**: Device state, usage tracking, boot metrics (1-hour default)
2. **Project Cache**: Build configurations, successful settings per project
3. **Build Settings Cache**: Bundle IDs, deployment targets, capabilities (1-hour default)
4. **Response Cache**: Progressive disclosure data for large outputs (30-minute default)
</cache_architecture>

<process>
## Step 1: View Current Cache Statistics

```typescript
cache({ operation: "get-stats" })
```

**Response includes:**
- Cache hit rates
- Expiry times
- Storage usage
- Performance metrics

## Step 2: View Current Configuration

```typescript
cache({ 
  operation: "get-config",
  cacheType: "all"  // or "simulator", "project", "response"
})
```

**Shows:**
- Cache timeouts
- Cache policies
- Current settings per layer

## Step 3: Configure Cache Timeouts

```typescript
// Set specific cache timeout
cache({
  operation: "set-config",
  cacheType: "simulator",  // which cache layer
  maxAgeHours: 2           // or maxAgeMinutes, maxAgeMs
})

// Configure multiple layers
cache({
  operation: "set-config",
  cacheType: "all",
  maxAgeMinutes: 30
})
```

**Timeout options:**
- `maxAgeMs`: Milliseconds
- `maxAgeMinutes`: Minutes
- `maxAgeHours`: Hours

## Step 4: Clear Caches

```typescript
// Clear specific cache
cache({
  operation: "clear",
  cacheType: "response"  // or "simulator", "project", "all"
})
```

**When to clear:**
- After significant project changes
- When cached data becomes stale
- When debugging cache-related issues
</process>

<persistence>
## Enabling Persistence

By default, caches are in-memory only. Enable persistence for cross-session learning:

### Enable Persistence
```typescript
persistence({ 
  operation: "enable",
  cacheDir: "~/.xc-mcp-cache"  // optional custom directory
})
```

**Benefits:**
- Learns over time (build configs, simulator preferences)
- Survives server restarts
- Project-specific intelligence accumulates

### Disable Persistence
```typescript
persistence({ 
  operation: "disable",
  clearData: false  // Set true to also delete stored data
})
```

### Check Persistence Status
```typescript
persistence({ 
  operation: "status",
  includeStorageInfo: true
})
```

**Response includes:**
- Current state (enabled/disabled)
- Cache directory path
- Disk usage
- Last updated timestamps
- Privacy information
</persistence>

<performance_tuning>
**Performance Optimization:**

| Scenario | Recommendation |
|----------|----------------|
| Long coding session | Longer cache times (2+ hours) |
| Quick iteration | Default times (1 hour) |
| CI/CD pipeline | Shorter times or disabled |
| Debugging issues | Clear caches, fresh data |

**High-Performance Configuration:**
```typescript
// Longer caches for stable development
cache({ operation: "set-config", cacheType: "simulator", maxAgeHours: 4 })
cache({ operation: "set-config", cacheType: "project", maxAgeHours: 8 })

// Enable persistence for learning
persistence({ operation: "enable" })
```

**Fresh Data Configuration:**
```typescript
// Shorter caches for frequent changes
cache({ operation: "set-config", cacheType: "all", maxAgeMinutes: 15 })

// Or disable persistence
persistence({ operation: "disable" })
```
</performance_tuning>

<list_cached_responses>
**View Cached Build/Test Results:**

For progressive disclosure, you may want to see what's cached:

```typescript
// List recent cached responses
list-cached-responses({
  limit: 10,
  tool: "xcodebuild-build"  // optional filter
})
```

**Useful for:**
- Finding buildId/testId for past operations
- Understanding what's in cache
- Debugging progressive disclosure
</list_cached_responses>

<privacy_considerations>
**What Gets Cached:**
- Simulator device lists (UDIDs, names, states)
- Build configurations (scheme, configuration, destination)
- Performance metrics (boot times, build durations)
- Large command outputs (for progressive disclosure)

**What's NOT Cached:**
- Source code
- Credentials or secrets
- Personal data

**Privacy Controls:**
- Persistence is opt-in (disabled by default)
- Clear data anytime with `cache({ operation: "clear", cacheType: "all" })`
- Delete persistence data: `persistence({ operation: "disable", clearData: true })`
</privacy_considerations>

<success_criteria>
Cache configuration complete when:
- [ ] Current cache stats reviewed
- [ ] Cache timeouts set appropriately for workflow
- [ ] Persistence enabled/disabled as needed
- [ ] Cache cleared if starting fresh
- [ ] Performance tuning applied for use case
</success_criteria>
