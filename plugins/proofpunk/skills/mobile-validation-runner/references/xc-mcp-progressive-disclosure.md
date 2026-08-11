> Incorporated from the `xc-mcp` skill (references/progressive-disclosure.md).

# Progressive Disclosure Pattern

## Contents

- [The Pattern](#the-pattern)
- [Tools That Use Progressive Disclosure](#tools-that-use-progressive-disclosure)
- [Detail Type Reference](#detail-type-reference)
- [Best Practices](#best-practices)
- [Cache Lifecycle](#cache-lifecycle)
- [Token Savings Summary](#token-savings-summary)


<overview>
Progressive disclosure is XC-MCP's core pattern for preventing token overflow while maintaining full functionality.

**The Problem:**
- `simctl list`: 57,000+ tokens raw output
- Build logs: 135,000+ tokens
- These exceed MCP protocol limits and waste context

**The Solution:**
- Return concise summaries first
- Provide cache IDs for on-demand detail retrieval
- Only fetch full data when actually needed
</overview>

<pattern>
## The Pattern

```
1. Execute operation → Get summary + cacheId
2. If more detail needed → Use cacheId to retrieve specific data
3. Never request full data upfront
```

**Example Flow:**
```typescript
// Step 1: Get summary
const result = simctl-list({ concise: true })
// Returns: { cacheId: "sim-abc", summary: {...}, quickAccess: {...} }

// Step 2: Only if needed, get details
const details = simctl-get-details({
  cacheId: "sim-abc",
  detailType: "devices-only",
  maxDevices: 10
})
```
</pattern>

<tools_using_progressive_disclosure>
## Tools That Use Progressive Disclosure

### simctl-list → simctl-get-details
- **Initial:** Summary, quick access, cacheId
- **Detail Types:** full-list, devices-only, runtimes-only, available-only
- **Token Reduction:** 57,000 → 2,000 (96%)

```typescript
// Summary (2k tokens)
simctl-list({ deviceType: "iPhone" })

// Full details only when needed
simctl-get-details({
  cacheId: "sim-abc123",
  detailType: "available-only",
  maxDevices: 20
})
```

### xcodebuild-build → xcodebuild-get-details
- **Initial:** Success, summary, buildId
- **Detail Types:** full-log, errors-only, warnings-only, summary, command, metadata
- **Token Reduction:** 135,000+ → ~200 (99%+)

```typescript
// Build (returns summary)
xcodebuild-build({ projectPath: "...", scheme: "..." })
// Returns: { buildId: "build-xyz", success: true, summary: {...} }

// Errors only (if failed)
xcodebuild-get-details({
  buildId: "build-xyz",
  detailType: "errors-only"
})

// Full log (only for deep debugging)
xcodebuild-get-details({
  buildId: "build-xyz",
  detailType: "full-log",
  maxLines: 100
})
```

### xcodebuild-test → xcodebuild-get-details
- **Initial:** Success, failed tests, testId
- **Detail Types:** Same as build

```typescript
// Run tests
xcodebuild-test({ projectPath: "...", scheme: "..." })
// Returns: { testId: "test-abc", success: false, failedTests: [...] }

// Get failure details
xcodebuild-get-details({
  testId: "test-abc",
  detailType: "errors-only"
})
```

### idb-ui-describe → uiTreeId
- **Initial:** Summary, element counts, uiTreeId
- **Full Tree:** Retrieved via uiTreeId

```typescript
// Get summary
idb-ui-describe({ operation: "all" })
// Returns: { summary: {...}, uiTreeId: "ui-xyz" }

// Full tree (if needed)
// Use uiTreeId to access full accessibility data
```
</tools_using_progressive_disclosure>

<detail_types>
## Detail Type Reference

### For simctl-get-details
| Type | Description | When to Use |
|------|-------------|-------------|
| `full-list` | All devices with full details | Need complete device info |
| `devices-only` | Just device list | Browsing available devices |
| `runtimes-only` | Just runtime list | Checking iOS versions |
| `available-only` | Only available devices | Quick device selection |

### For xcodebuild-get-details
| Type | Description | When to Use |
|------|-------------|-------------|
| `full-log` | Complete build/test output | Deep debugging |
| `errors-only` | Just errors | Build/test failed |
| `warnings-only` | Just warnings | Investigating warnings |
| `summary` | Condensed overview | Quick status check |
| `command` | Exact command executed | Reproduction/sharing |
| `metadata` | Build configuration details | Configuration debugging |
</detail_types>

<best_practices>
## Best Practices

### DO:
- ✅ Start with summary responses
- ✅ Use specific detail types (errors-only vs full-log)
- ✅ Limit results (maxDevices, maxLines)
- ✅ Cache IDs are short-lived, use promptly

### DON'T:
- ❌ Request full-log as first step
- ❌ Skip the summary response
- ❌ Ignore detail type options
- ❌ Assume cache IDs persist indefinitely

### Pattern Examples:

**Good: Progressive approach**
```typescript
// 1. Get overview
const build = xcodebuild-build({ ... })

// 2. Check if failed
if (!build.success) {
  // 3. Get just errors
  const errors = xcodebuild-get-details({
    buildId: build.buildId,
    detailType: "errors-only"
  })
}
```

**Bad: Immediate full dump**
```typescript
// DON'T DO THIS
const build = xcodebuild-build({ ... })
const fullLog = xcodebuild-get-details({
  buildId: build.buildId,
  detailType: "full-log"  // Wastes tokens if build succeeded
})
```
</best_practices>

<cache_lifecycle>
## Cache Lifecycle

- **Default Retention:** 30 minutes for response cache
- **Automatic Eviction:** Oldest entries removed when limit reached
- **Manual Clear:** `cache({ operation: "clear", cacheType: "response" })`

**Important:** Cache IDs are session-specific. If you need to reference build results later, store relevant information, not just the cacheId.
</cache_lifecycle>

<token_savings>
## Token Savings Summary

| Operation | Raw Output | With Progressive | Savings |
|-----------|------------|------------------|---------|
| simctl list | 57,000 | 2,000 | 96% |
| Build log | 135,000+ | 200 | 99%+ |
| Test results | 50,000+ | 500 | 99% |
| UI tree | 10,000+ | 200 | 98% |

**Total context budget preserved:** Nearly 100% of context available for actual work instead of tool output.
</token_savings>