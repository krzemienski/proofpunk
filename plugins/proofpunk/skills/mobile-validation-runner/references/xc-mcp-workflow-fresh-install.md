> Incorporated from the `xc-mcp` skill (workflows/fresh-install.md).

# Workflow: Fresh Install (Clean State Testing)

## Contents

- [Step 1: Use High-Level Workflow Tool](#step-1-use-high-level-workflow-tool)
- [Step 2: Manual Steps (Alternative)](#step-2-manual-steps-alternative)


<required_reading>
**Read these reference files NOW:**
1. references/tool-reference.md
2. references/operation-enums.md
</required_reading>

<workflow_overview>
The fresh install workflow ensures a completely clean testing environment by:
1. Shutting down the simulator
2. Erasing simulator data (optional)
3. Booting the simulator fresh
4. Building the app
5. Installing the app
6. Launching with test arguments

**Use this for:**
- CI/CD pipeline testing
- Reproducing bugs with clean state
- Testing onboarding flows
- Ensuring no cached data affects tests
</workflow_overview>

<process>
## Step 1: Use High-Level Workflow Tool

**RECOMMENDED:** Use `workflow-fresh-install` for single-step execution:

```typescript
workflow-fresh-install({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  simulatorUdid: "auto",              // optional: auto-detects
  eraseSimulator: true,               // optional: wipe all data
  configuration: "Debug",             // optional
  launchArguments: ["--resetData"],   // optional
  environmentVariables: {             // optional
    "TEST_MODE": "true"
  }
})
```

**Response contains:**
- `success`: Overall workflow status
- `buildTime`: Build duration
- `bootTime`: Simulator boot time
- `launchTime`: App launch time
- `eraseStatus`: Erase operation result (if requested)

## Step 2: Manual Steps (Alternative)

If you need more control, execute steps individually:

### 2a. Shutdown Simulator
```typescript
simctl-device({ 
  operation: "shutdown", 
  deviceId: "UDID" 
})
// Or shutdown all
simctl-device({ 
  operation: "shutdown", 
  deviceId: "all" 
})
```

### 2b. Erase Simulator (Reset to Factory)
```typescript
simctl-device({ 
  operation: "erase", 
  deviceId: "UDID" 
})
```
**Warning:** This removes all app data, settings, and cached content.

### 2c. Boot Simulator Fresh
```typescript
simctl-device({ 
  operation: "boot", 
  deviceId: "UDID" 
})
```

### 2d. Build App
```typescript
xcodebuild-build({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme"
})
```

### 2e. Install App
```typescript
simctl-app({
  operation: "install",
  appPath: "/path/to/YourApp.app"
})
```

### 2f. Launch App
```typescript
simctl-app({
  operation: "launch",
  bundleId: "com.yourcompany.YourApp",
  launchArguments: ["--resetData"]
})
```
</process>

<when_to_use>
**Fresh Install Recommended For:**

1. **Onboarding Flow Testing**
   - First-run experience
   - Permission request flows
   - Account creation

2. **Bug Reproduction**
   - Clean state to isolate issues
   - Consistent reproduction environment

3. **CI/CD Pipelines**
   - Ensure no state pollution between runs
   - Reproducible test results

4. **Data Migration Testing**
   - Testing upgrade paths
   - Database schema changes

5. **Cache-Related Issues**
   - Verifying behavior without cached data
   - Testing cold start performance
</when_to_use>

<erase_vs_uninstall>
**Erase Simulator vs Uninstall App:**

| Action | Scope | Use When |
|--------|-------|----------|
| `erase` | Entire simulator | Need truly clean state, testing system features |
| `uninstall` | Single app | Just need to clear app data |

**Uninstall then reinstall (faster):**
```typescript
simctl-app({ operation: "uninstall", bundleId: "com.example.App" })
simctl-app({ operation: "install", appPath: "/path/to/App.app" })
```

**Full erase (thorough):**
```typescript
simctl-device({ operation: "erase", deviceId: "UDID" })
// Then boot, install, launch
```
</erase_vs_uninstall>

<ci_cd_pattern>
**CI/CD Pipeline Pattern:**

```typescript
// Single command for CI
workflow-fresh-install({
  projectPath: "./MyApp.xcworkspace",
  scheme: "MyApp",
  eraseSimulator: true,
  configuration: "Debug",
  launchArguments: ["-UITesting", "--resetData"],
  environmentVariables: {
    "API_ENVIRONMENT": "staging",
    "MOCK_NETWORK": "true"
  }
})
```

**Benefits:**
- Reproducible across CI runs
- No state pollution from previous builds
- Consistent test environment
- Single tool call vs 5+ separate commands
</ci_cd_pattern>

<success_criteria>
Fresh install workflow complete when:
- [ ] Simulator shutdown (if was running)
- [ ] Simulator erased (if clean state needed)
- [ ] Simulator booted fresh
- [ ] App built successfully
- [ ] App installed
- [ ] App launched with appropriate arguments
- [ ] All steps completed in single workflow-fresh-install call OR manual steps
</success_criteria>