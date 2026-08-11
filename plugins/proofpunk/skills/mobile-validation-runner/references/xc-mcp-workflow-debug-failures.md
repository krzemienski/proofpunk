> Incorporated from the `xc-mcp` skill (workflows/debug-failures.md).

# Workflow: Debug Build and Test Failures

<required_reading>
**Read these reference files NOW:**
1. references/progressive-disclosure.md
2. references/tool-reference.md
</required_reading>

<process>
## Step 1: Identify the Failure Type

**Build failures** return `buildId` with error information.
**Test failures** return `testId` with failure details.

Check the initial response for:
- `success: false`
- `summary.errorCount > 0`
- `failedTests` array (for test failures)

## Step 2: Get Error Summary First

**Never request full logs upfront.** Use progressive disclosure:

### For Build Failures:
```typescript
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "errors-only"  // Just the errors
})
```

### For Test Failures:
```typescript
xcodebuild-get-details({
  testId: "test-xyz789",
  detailType: "errors-only"
})
```

## Step 3: Get Warnings (If Relevant)

```typescript
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "warnings-only"
})
```

Warnings can provide context for errors (deprecations, implicit conversions, etc.)

## Step 4: Get Full Logs (When Needed)

Only request full logs when error summary is insufficient:

```typescript
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "full-log",
  maxLines: 100  // Limit output size
})
```

## Step 5: Get Build Command (For Reproduction)

```typescript
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "command"
})
// Returns: The exact xcodebuild command that was executed
```

Useful for:
- Manual reproduction
- CI/CD debugging
- Sharing with team members

## Step 6: Check Environment

```typescript
// Validate Xcode environment
simctl-health-check({})

// Check Xcode version
xcodebuild-version({})

// List available SDKs
xcodebuild-list({ projectPath: "./Project.xcworkspace" })
```
</process>

<common_build_errors>
**Common Build Error Patterns:**

1. **Missing Dependencies**
   - Check Podfile/Package.swift
   - Run `pod install` or `swift package resolve`

2. **Code Signing Issues**
   - Check team ID and provisioning profiles
   - Use `CODE_SIGN_IDENTITY=""` for simulator builds

3. **SDK Version Mismatches**
   - Check deployment target vs Xcode version
   - Update minimum iOS version if needed

4. **Swift Version Conflicts**
   - Check Swift language version in build settings
   - Ensure all dependencies support same Swift version

5. **Module Not Found**
   - Clean build folder: `xcodebuild-clean`
   - Rebuild: `xcodebuild-build`
</common_build_errors>

<common_test_failures>
**Common Test Failure Patterns:**

1. **Timeout Failures**
   - Tests taking too long
   - Network calls not mocked
   - Infinite loops

2. **Assertion Failures**
   - Expected vs actual value mismatch
   - UI element not found

3. **Setup/Teardown Issues**
   - State not properly reset
   - Shared state between tests

4. **Simulator Issues**
   - Simulator not booted
   - Wrong simulator selected
   - Simulator out of memory
</common_test_failures>

<debugging_workflow>
**Systematic Debugging Approach:**

```typescript
// 1. Get error summary
const errors = xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "errors-only"
})

// 2. If errors point to specific file, focus there
// 3. If unclear, get more context
const context = xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "full-log",
  maxLines: 50  // Around the error
})

// 4. Check environment if nothing else works
simctl-health-check({})
xcodebuild-version({})

// 5. Clean and retry
xcodebuild-clean({ projectPath: "...", scheme: "..." })
xcodebuild-build({ projectPath: "...", scheme: "..." })
```
</debugging_workflow>

<cache_issues>
**When Caching Causes Problems:**

If build succeeds but app behaves unexpectedly:

```typescript
// Clear all caches
cache({ operation: "clear", cacheType: "all" })

// Clean build artifacts
xcodebuild-clean({ projectPath: "...", scheme: "..." })

// Fresh build
xcodebuild-build({ projectPath: "...", scheme: "..." })
```

For simulator state issues:
```typescript
// Erase simulator
simctl-device({ operation: "erase", deviceId: "UDID" })
```
</cache_issues>

<success_criteria>
Debug workflow complete when:
- [ ] Failure type identified (build vs test)
- [ ] Error summary retrieved first (not full logs)
- [ ] Progressive disclosure used (errors-only → warnings → full-log)
- [ ] Root cause identified from error messages
- [ ] Environment validated if needed
- [ ] Clean rebuild attempted if necessary
- [ ] Issue resolved or clearly understood
</success_criteria>
