> Incorporated from the `xc-mcp` skill (references/tool-reference.md).

# XC-MCP Tool Reference

## Contents

- [Build & Test Tools (6)](#build--test-tools-6)
- [Simulator Tools (6 routers/tools)](#simulator-tools-6-routerstools)
- [UI Automation Tools (6)](#ui-automation-tools-6)
- [Workflow Tools (2)](#workflow-tools-2)
- [Cache & Persistence Tools (2 routers)](#cache--persistence-tools-2-routers)
- [Other Tools](#other-tools)
- [IDB Tools (Additional)](#idb-tools-additional)


<tool_discovery>
Use `rtfm` for on-demand documentation:

```typescript
// Browse all tools in a category
rtfm({ categoryName: "build" })

// Get comprehensive docs for specific tool
rtfm({ toolName: "xcodebuild-build" })
```

Categories: `build`, `simulator`, `app`, `idb`, `io`, `cache`, `system`, `workflow`
</tool_discovery>

<build_tools>
## Build & Test Tools (6)

### xcodebuild-build
Build Xcode projects with intelligent defaults.

```typescript
xcodebuild-build({
  projectPath: string,     // Required: Path to .xcworkspace or .xcodeproj
  scheme: string,          // Required: Scheme to build
  configuration?: string,  // Default: "Debug"
  destination?: string,    // Auto-detected from usage history
  sdk?: string,            // Optional: iphonesimulator, iphoneos
  derivedDataPath?: string,// Optional: Custom derived data location
  autoInstall?: boolean    // Optional: Install after successful build
})
```

**Returns:** `{ buildId, success, summary, intelligence, nextSteps }`

### xcodebuild-test
Run tests with filtering and test plans.

```typescript
xcodebuild-test({
  projectPath: string,
  scheme: string,
  testPlan?: string,           // Specific test plan
  onlyTesting?: string[],      // Run only these tests
  skipTesting?: string[],      // Skip these tests
  testWithoutBuilding?: boolean, // Skip build phase
  destination?: string
})
```

**Returns:** `{ testId, success, summary, failedTests }`

### xcodebuild-clean
Clean build artifacts.

```typescript
xcodebuild-clean({
  projectPath: string,
  scheme: string,
  configuration?: string
})
```

### xcodebuild-list
List project targets and schemes (1-hour caching).

```typescript
xcodebuild-list({
  projectPath: string,
  outputFormat?: "json" | "text"  // Default: "json"
})
```

### xcodebuild-version
Get Xcode and SDK versions.

```typescript
xcodebuild-version({
  outputFormat?: "json" | "text",
  sdk?: string
})
```

### xcodebuild-get-details
Access cached build/test logs via progressive disclosure.

```typescript
xcodebuild-get-details({
  buildId?: string,  // From xcodebuild-build
  testId?: string,   // From xcodebuild-test
  detailType: "full-log" | "errors-only" | "warnings-only" | "summary" | "command" | "metadata",
  maxLines?: number  // Default: 100
})
```
</build_tools>

<simulator_tools>
## Simulator Tools (6 routers/tools)

### simctl-device (Router - 7 operations)
Unified device lifecycle management.

```typescript
simctl-device({
  operation: "boot" | "shutdown" | "create" | "delete" | "erase" | "clone" | "rename",
  deviceId?: string,    // UDID, "booted", or "all" (for shutdown)
  // For create:
  name?: string,
  deviceType?: string,
  runtime?: string,
  // For rename:
  newName?: string
})
```

### simctl-app (Router - 4 operations)
Unified app management.

```typescript
simctl-app({
  operation: "install" | "uninstall" | "launch" | "terminate",
  deviceId?: string,              // Default: "booted"
  // For install:
  appPath?: string,
  // For launch/terminate/uninstall:
  bundleId?: string,
  // For launch:
  launchArguments?: string[],
  environmentVariables?: Record<string, string>
})
```

### simctl-list
Progressive disclosure simulator listing (96% token reduction).

```typescript
simctl-list({
  concise?: boolean,       // Default: true (summary view)
  deviceType?: string,     // Filter: "iPhone", "iPad"
  runtime?: string,        // Filter: "17", "iOS 17.0"
  availability?: "available" | "unavailable" | "all",
  outputFormat?: "json" | "text"
})
```

**Returns:** `{ cacheId, summary, quickAccess }`

### simctl-get-details
On-demand full simulator data.

```typescript
simctl-get-details({
  cacheId: string,  // From simctl-list
  detailType: "full-list" | "devices-only" | "runtimes-only" | "available-only",
  deviceType?: string,
  maxDevices?: number,  // Default: 20
  runtime?: string
})
```

### simctl-health-check
Validate Xcode environment.

```typescript
simctl-health-check({})
```

**Checks:** Xcode, simctl, simulators, runtimes, disk space.

### simctl-io
Screenshots and video recording.

```typescript
simctl-io({
  deviceId?: string,
  operation: "screenshot" | "recordVideo",
  // For screenshot:
  filename?: string,
  format?: "png" | "jpeg",
  // Semantic naming:
  appName?: string,
  screenName?: string,
  state?: string
})
```
</simulator_tools>

<ui_automation_tools>
## UI Automation Tools (6)

### accessibility-quality-check
**ALWAYS call this first** before any UI interaction.

```typescript
accessibility-quality-check({
  screenContext?: string,  // e.g., "LoginScreen"
  udid?: string           // Default: "booted"
})
```

**Returns:** `{ quality: "rich" | "moderate" | "minimal", recommendation, elementCounts }`

### idb-ui-find-element
Semantic element search by label/identifier.

```typescript
idb-ui-find-element({
  query: string,    // Element label, placeholder, or identifier
  udid?: string     // Default: "booted"
})
```

**Returns:** `{ centerX, centerY, label, type, frame }`

### idb-ui-tap
Coordinate-based tapping.

```typescript
idb-ui-tap({
  x: number,
  y: number,
  udid?: string,
  applyScreenshotScale?: boolean  // Transform coordinates from screenshot size
})
```

### idb-ui-input
Text input and keyboard control.

```typescript
idb-ui-input({
  operation: "text" | "key" | "clear",
  text?: string,     // For "text" operation
  key?: string,      // For "key" operation: "return", "delete", etc.
  udid?: string
})
```

### idb-ui-gesture
Swipes, pinches, rotations.

```typescript
idb-ui-gesture({
  operation: "swipe" | "pinch" | "rotate",
  udid?: string,
  // For swipe:
  direction?: "up" | "down" | "left" | "right",
  // Or explicit coordinates:
  startX?: number, startY?: number,
  endX?: number, endY?: number,
  // For pinch:
  scale?: number,  // <1 pinch in, >1 pinch out
  // For rotate:
  angle?: number
})
```

### idb-ui-describe
Accessibility tree queries.

```typescript
idb-ui-describe({
  operation: "all" | "point",
  udid?: string,
  // For point:
  x?: number,
  y?: number
})
```

**Returns:** Summary + `uiTreeId` for full tree access.
</ui_automation_tools>

<workflow_tools>
## Workflow Tools (2)

### workflow-tap-element
High-level semantic tap combining find + tap.

```typescript
workflow-tap-element({
  elementQuery: string,      // Required: Element to find
  screenContext?: string,    // Screen name for tracking
  inputText?: string,        // Optional: Type after tap
  verifyResult?: boolean,    // Optional: Screenshot after action
  udid?: string
})
```

**Cost:** ~90 tokens (vs 130 separately)
**Latency:** ~300ms (vs ~400ms separately)

### workflow-fresh-install
Clean install workflow for testing.

```typescript
workflow-fresh-install({
  projectPath: string,                  // Required
  scheme: string,                       // Required
  simulatorUdid?: string,               // Auto-detect
  eraseSimulator?: boolean,             // Default: false
  configuration?: "Debug" | "Release",  // Default: "Debug"
  launchArguments?: string[],
  environmentVariables?: Record<string, string>
})
```

**Cost:** ~200 tokens (vs 300+ separately)
**Latency:** ~20s (vs 25+s separately)
</workflow_tools>

<cache_tools>
## Cache & Persistence Tools (2 routers)

### cache (Router - 4 operations)
Cache management.

```typescript
cache({
  operation: "get-stats" | "get-config" | "set-config" | "clear",
  cacheType?: "simulator" | "project" | "response" | "all",
  // For set-config:
  maxAgeMs?: number,
  maxAgeMinutes?: number,
  maxAgeHours?: number
})
```

### persistence (Router - 3 operations)
Persistence control.

```typescript
persistence({
  operation: "enable" | "disable" | "status",
  cacheDir?: string,           // For enable
  clearData?: boolean,         // For disable
  includeStorageInfo?: boolean // For status
})
```
</cache_tools>

<other_tools>
## Other Tools

### simctl-openurl
Open URLs and deep links.

```typescript
simctl-openurl({
  url: string,
  deviceId?: string
})
```

### simctl-get-app-container
Get app container paths.

```typescript
simctl-get-app-container({
  bundleId: string,
  containerType: "bundle" | "data" | "group",
  deviceId?: string
})
```

### simctl-push
Simulate push notifications.

```typescript
simctl-push({
  bundleId: string,
  payload: object,      // APNS payload
  deviceId?: string,
  testName?: string,    // For tracking
  expectedBehavior?: string
})
```

### rtfm
On-demand comprehensive documentation.

```typescript
rtfm({
  categoryName?: string,  // Browse category
  toolName?: string       // Get specific tool docs
})
```
</other_tools>

<idb_tools>
## IDB Tools (Additional)

### idb-app (Router - 4 operations)
IDB app management (supports physical devices).

```typescript
idb-app({
  operation: "install" | "uninstall" | "launch" | "terminate",
  appPath?: string,
  bundleId?: string,
  udid?: string
})
```

### idb-targets (Router - 4 operations)
Target management and discovery.

```typescript
idb-targets({
  operation: "list" | "describe" | "connect" | "disconnect",
  udid?: string
})
```
</idb_tools>