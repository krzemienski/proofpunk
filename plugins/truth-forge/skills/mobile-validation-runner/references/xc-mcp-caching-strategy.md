> Incorporated from the `xc-mcp` skill (references/caching-strategy.md).

# XC-MCP Caching Strategy

<cache_architecture>
## 4-Layer Cache Architecture

XC-MCP implements a sophisticated 4-layer caching system:

### 1. Simulator Cache
- **Purpose:** Device state, usage tracking, boot performance
- **Default TTL:** 1 hour
- **Data:** Device lists, boot times, usage frequency
- **Benefit:** Avoids repeated `simctl list` calls (57k tokens each)

### 2. Project Cache
- **Purpose:** Build configurations, successful settings
- **Default TTL:** Session-based (or persistent if enabled)
- **Data:** Schemes, destinations, build settings that worked
- **Benefit:** Smart defaults based on project history

### 3. Build Settings Cache
- **Purpose:** Xcode build settings discovery
- **Default TTL:** 1 hour
- **Data:** Bundle IDs, deployment targets, device families, capabilities
- **Benefit:** Auto-discovers project metadata without parsing

### 4. Response Cache
- **Purpose:** Progressive disclosure for large outputs
- **Default TTL:** 30 minutes
- **Data:** Build logs, test results, simulator details
- **Benefit:** Enables buildId/cacheId pattern without storage overhead
</cache_architecture>

<how_caching_helps>
## How Caching Helps

### Token Savings
| Operation | Without Cache | With Cache | Savings |
|-----------|---------------|------------|---------|
| simctl list | 57,000 tokens | 2,000 tokens | 96% |
| Build log access | Full log each time | Summary + on-demand | 99%+ |
| Repeated builds | Full discovery | Cached settings | 80%+ |

### Performance Gains
| Operation | Without Cache | With Cache | Speedup |
|-----------|---------------|------------|---------|
| List simulators | ~2-5s | ~50ms | 40-100x |
| Get project info | ~1-2s | ~10ms | 100x+ |
| Second build | Full discovery | Cached config | 5-10x |

### Intelligence Features
- **Usage tracking:** Most-used simulators appear first
- **Build learning:** Successful configurations remembered
- **Smart defaults:** Auto-selects optimal simulator
- **Performance metrics:** Boot times, build durations tracked
</how_caching_helps>

<cache_operations>
## Cache Operations

### View Statistics
```typescript
cache({ operation: "get-stats" })
```
Returns:
- Hit/miss rates
- Entry counts
- Storage sizes
- Expiry information

### View Configuration
```typescript
cache({
  operation: "get-config",
  cacheType: "all"  // or specific layer
})
```

### Adjust Timeouts
```typescript
// Longer caches for stable development
cache({
  operation: "set-config",
  cacheType: "simulator",
  maxAgeHours: 4
})

// Shorter caches for CI/CD
cache({
  operation: "set-config",
  cacheType: "all",
  maxAgeMinutes: 15
})
```

### Clear Caches
```typescript
// Clear specific layer
cache({ operation: "clear", cacheType: "response" })

// Clear everything
cache({ operation: "clear", cacheType: "all" })
```
</cache_operations>

<persistence>
## Persistence

By default, caches are in-memory only. Enable persistence for cross-session learning.

### Enable Persistence
```typescript
persistence({
  operation: "enable",
  cacheDir: "~/.xc-mcp-cache"  // optional
})
```

**What gets persisted:**
- Simulator usage patterns
- Successful build configurations
- Performance metrics
- Project preferences

**What's NOT persisted:**
- Source code
- Credentials
- Personal data

### Disable Persistence
```typescript
persistence({
  operation: "disable",
  clearData: true  // Optional: also delete stored files
})
```

### Check Status
```typescript
persistence({
  operation: "status",
  includeStorageInfo: true
})
```
</persistence>

<tuning_strategies>
## Tuning Strategies

### For Long Development Sessions
```typescript
// Maximize cache duration
cache({ operation: "set-config", cacheType: "simulator", maxAgeHours: 8 })
cache({ operation: "set-config", cacheType: "project", maxAgeHours: 24 })

// Enable persistence
persistence({ operation: "enable" })
```

### For CI/CD Pipelines
```typescript
// Shorter caches or disabled
cache({ operation: "set-config", cacheType: "all", maxAgeMinutes: 10 })

// Or clear at start of each run
cache({ operation: "clear", cacheType: "all" })
```

### For Debugging Cache Issues
```typescript
// Clear all caches
cache({ operation: "clear", cacheType: "all" })

// Disable persistence
persistence({ operation: "disable", clearData: true })

// Fresh start
```

### For Testing New Projects
```typescript
// Clear project cache (keep simulator cache)
cache({ operation: "clear", cacheType: "project" })
```
</tuning_strategies>

<cache_invalidation>
## Cache Invalidation

Caches automatically invalidate:
- **On timeout:** Based on configured TTL
- **On file change:** Project modifications detected
- **On environment change:** Xcode version changes
- **On explicit clear:** Manual cache clear

**Force fresh data:**
```typescript
// Clear and refetch
cache({ operation: "clear", cacheType: "simulator" })
simctl-list({ concise: true })
```
</cache_invalidation>

<best_practices>
## Best Practices

1. **Start with defaults** - XC-MCP's default timeouts are optimized for most workflows

2. **Use progressive disclosure** - Don't bypass caching by requesting full data

3. **Enable persistence** for long-running projects - Learning improves over time

4. **Clear caches** when debugging strange behavior

5. **Monitor cache stats** periodically to understand effectiveness

6. **Adjust based on workflow:**
   - Active development: Longer caches
   - CI/CD: Shorter or no caches
   - Debugging: Clear and start fresh
</best_practices>
