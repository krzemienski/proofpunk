> Incorporated from the `xc-mcp` skill (workflows/run-tests.md).

# Workflow: Run Tests

## Contents

- [Step 1: Discover Test Targets](#step-1-discover-test-targets)
- [Step 2: Run Tests](#step-2-run-tests)
- [Step 3: Get Test Details (Progressive Disclosure)](#step-3-get-test-details-progressive-disclosure)
- [Step 4: Test Without Building (Fast Iteration)](#step-4-test-without-building-fast-iteration)
- [Step 5: Run Specific Tests](#step-5-run-specific-tests)


<required_reading>
**Read these reference files NOW:**
1. references/tool-reference.md
2. references/progressive-disclosure.md
</required_reading>

<process>
## Step 1: Discover Test Targets

```typescript
xcodebuild-list({ projectPath: "./YourProject.xcworkspace" })
// Shows available schemes and targets
```

## Step 2: Run Tests

```typescript
xcodebuild-test({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  // Optional parameters:
  testPlan: "MyTestPlan",              // specific test plan
  onlyTesting: ["LoginTests"],          // run specific tests
  skipTesting: ["SlowTests"],           // skip specific tests
  testWithoutBuilding: false,           // skip build if already built
  destination: "auto"                   // auto-select simulator
})
```

**Response contains:**
- `testId`: Cache ID for full test logs
- `success`: Overall test status
- `summary`: Pass/fail counts, duration
- `failedTests`: List of failures (if any)

## Step 3: Get Test Details (Progressive Disclosure)

```typescript
// Get summary of test results
xcodebuild-get-details({
  testId: "test-xyz789",
  detailType: "summary"
})

// Get only failed tests
xcodebuild-get-details({
  testId: "test-xyz789",
  detailType: "errors-only"
})

// Get full test log
xcodebuild-get-details({
  testId: "test-xyz789",
  detailType: "full-log",
  maxLines: 100
})
```

## Step 4: Test Without Building (Fast Iteration)

If app is already built:

```typescript
xcodebuild-test({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  testWithoutBuilding: true  // Skip build, run tests directly
})
```

## Step 5: Run Specific Tests

```typescript
// Run only specific test classes
xcodebuild-test({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  onlyTesting: [
    "YourAppTests/LoginTests",
    "YourAppTests/PaymentTests"
  ]
})

// Skip slow or flaky tests
xcodebuild-test({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  skipTesting: [
    "YourAppTests/PerformanceTests",
    "YourAppTests/NetworkTests"
  ]
})
```
</process>

<test_filtering>
**Test Filtering Patterns:**

```typescript
// Run single test class
onlyTesting: ["ModuleTests/ClassTests"]

// Run single test method
onlyTesting: ["ModuleTests/ClassTests/testSpecificMethod"]

// Run multiple test classes
onlyTesting: ["ModuleTests/ClassA", "ModuleTests/ClassB"]

// Skip test class
skipTesting: ["ModuleTests/SlowTests"]

// Skip individual method
skipTesting: ["ModuleTests/ClassTests/testFlaky"]
```
</test_filtering>

<test_plans>
**Using Test Plans:**

```typescript
xcodebuild-test({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  testPlan: "SmokeTests"  // Uses SmokeTests.xctestplan
})
```

Test plans define:
- Which tests to run
- Test configurations
- Environment variables
- Parallel execution settings
</test_plans>

<debugging_failures>
**When Tests Fail:**

1. Get failure summary:
```typescript
xcodebuild-get-details({
  testId: "test-xyz789",
  detailType: "errors-only"
})
```

2. Get specific test output:
```typescript
xcodebuild-get-details({
  testId: "test-xyz789",
  detailType: "full-log",
  maxLines: 200
})
```

3. Re-run only failed tests for faster iteration:
```typescript
xcodebuild-test({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  onlyTesting: ["FailedTestClass/failedTestMethod"]
})
```
</debugging_failures>

<success_criteria>
Test workflow complete when:
- [ ] Test targets discovered via xcodebuild-list
- [ ] Tests executed with appropriate filtering
- [ ] Results accessed via progressive disclosure (testId)
- [ ] Full logs requested only for debugging
- [ ] Test-without-building used for fast iteration when appropriate
</success_criteria>