> Incorporated from the `xc-mcp` skill (workflows/build-project.md).

# Workflow: Build Xcode Project

## Contents

- [Step 1: Discover Project Configuration](#step-1-discover-project-configuration)
- [Step 2: Build the Project](#step-2-build-the-project)
- [Step 3: Handle Build Results](#step-3-handle-build-results)
- [Step 4: Access Full Logs (If Needed)](#step-4-access-full-logs-if-needed)
- [Step 5: Clean Build (If Needed)](#step-5-clean-build-if-needed)


<required_reading>
**Read these reference files NOW:**
1. references/tool-reference.md
2. references/progressive-disclosure.md
</required_reading>

<process>
## Step 1: Discover Project Configuration

Use `xcodebuild-list` to understand project structure:

```typescript
xcodebuild-list({ projectPath: "./YourProject.xcworkspace" })
// Returns: schemes, targets, configurations (with 1-hour caching)
```

**Smart caching**: Results cached for 1 hour to avoid redundant operations.

## Step 2: Build the Project

Execute build with intelligent defaults:

```typescript
xcodebuild-build({
  projectPath: "./YourProject.xcworkspace",  // required
  scheme: "YourScheme",                       // required
  configuration: "Debug",                     // optional, default: Debug
  // destination auto-selected from usage history
})
```

**Response contains:**
- `buildId`: Cache ID for accessing full logs
- `success`: Boolean build status
- `summary`: Duration, error/warning counts
- `intelligence`: Smart defaults used, learning status

## Step 3: Handle Build Results

**On Success:**
- Build artifacts ready in derived data
- Configuration cached for future builds
- Proceed to install/launch if needed

**On Failure:**
- Use progressive disclosure to get error details:

```typescript
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "errors-only",  // or "warnings-only", "full-log"
  maxLines: 50
})
```

## Step 4: Access Full Logs (If Needed)

Only request full logs when debugging:

```typescript
// Get full build log
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "full-log",
  maxLines: 100
})

// Get just the command that was executed
xcodebuild-get-details({
  buildId: "build-abc123",
  detailType: "command"
})
```

## Step 5: Clean Build (If Needed)

For clean rebuilds:

```typescript
xcodebuild-clean({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme"
})
```

Then re-run build command.
</process>

<build_configuration_options>
**Configuration Parameter:**
- `Debug`: Development builds with debug symbols
- `Release`: Optimized production builds

**SDK Options:**
- `iphonesimulator`: iOS Simulator (default for simulator builds)
- `iphoneos`: Physical iOS device

**Destination:**
- Auto-detected from project history
- Or specify: `platform=iOS Simulator,id=UDID`
</build_configuration_options>

<common_patterns>
**Pattern 1: Quick Debug Build**
```typescript
xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App" })
```

**Pattern 2: Release Build**
```typescript
xcodebuild-build({ 
  projectPath: "./App.xcworkspace", 
  scheme: "App",
  configuration: "Release"
})
```

**Pattern 3: Build with Auto-Install**
```typescript
xcodebuild-build({ 
  projectPath: "./App.xcworkspace", 
  scheme: "App",
  autoInstall: true  // Boots simulator, installs app
})
```
</common_patterns>

<success_criteria>
Build workflow complete when:
- [ ] Project configuration discovered via xcodebuild-list
- [ ] Build executed with appropriate configuration
- [ ] Build success confirmed OR errors retrieved via progressive disclosure
- [ ] Full logs accessed only when debugging (not upfront)
- [ ] Smart defaults leveraged (no manual UDID prompts)
</success_criteria>