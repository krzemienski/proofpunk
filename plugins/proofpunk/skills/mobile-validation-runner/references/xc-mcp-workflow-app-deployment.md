> Incorporated from the `xc-mcp` skill (workflows/app-deployment.md).

# Workflow: App Deployment

## Contents

- [Step 1: Ensure Simulator is Booted](#step-1-ensure-simulator-is-booted)
- [Step 2: Install the App](#step-2-install-the-app)
- [Step 3: Launch the App](#step-3-launch-the-app)
- [Step 4: Terminate the App](#step-4-terminate-the-app)
- [Step 5: Uninstall the App](#step-5-uninstall-the-app)


<required_reading>
**Read these reference files NOW:**
1. references/tool-reference.md
2. references/operation-enums.md
</required_reading>

<process>
## Step 1: Ensure Simulator is Booted

Check for booted simulator or boot one:

```typescript
// List and check for booted simulators
simctl-list({ availability: "available" })
// Check quickAccess.bootedDevices

// If none booted, boot one
simctl-device({ 
  operation: "boot", 
  deviceId: "UDID-from-quickAccess" 
})
```

## Step 2: Install the App

Use `simctl-app` router with `install` operation:

```typescript
simctl-app({
  operation: "install",
  appPath: "/path/to/YourApp.app",  // Built app bundle
  deviceId: "booted"                 // Optional, defaults to booted
})
```

**Finding app path:**
- Build artifacts in derived data directory
- Use `xcodebuild-build` with `autoInstall: true` to auto-install after build

## Step 3: Launch the App

```typescript
simctl-app({
  operation: "launch",
  bundleId: "com.yourcompany.YourApp",
  deviceId: "booted",                          // Optional
  launchArguments: ["--reset-data"],           // Optional
  environmentVariables: { "DEBUG_MODE": "1" }  // Optional
})
```

## Step 4: Terminate the App

```typescript
simctl-app({
  operation: "terminate",
  bundleId: "com.yourcompany.YourApp"
})
```

## Step 5: Uninstall the App

```typescript
simctl-app({
  operation: "uninstall",
  bundleId: "com.yourcompany.YourApp"
})
```
</process>

<build_and_install>
**Combined Build + Install Pattern:**

Option 1: Auto-install after build
```typescript
xcodebuild-build({
  projectPath: "./YourProject.xcworkspace",
  scheme: "YourScheme",
  autoInstall: true  // Boots simulator, installs automatically
})
```

Option 2: Separate steps
```typescript
// Build
xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App" })

// Install
simctl-app({ 
  operation: "install", 
  appPath: "~/Library/Developer/Xcode/DerivedData/App/Build/Products/Debug-iphonesimulator/App.app" 
})

// Launch
simctl-app({ operation: "launch", bundleId: "com.example.App" })
```
</build_and_install>

<app_container_paths>
**Get App Container Paths:**

```typescript
simctl-get-app-container({
  bundleId: "com.yourcompany.YourApp",
  containerType: "data"  // "bundle" | "data" | "group"
})
```

**Container types:**
- `bundle`: App installation directory
- `data`: Documents, caches, preferences
- `group`: App group shared containers
</app_container_paths>

<idb_alternative>
**Using IDB for Physical Devices:**

For physical device deployment, use `idb-app`:

```typescript
// Install via IDB (works with physical devices)
idb-app({
  operation: "install",
  appPath: "/path/to/YourApp.app"
})

// Launch via IDB
idb-app({
  operation: "launch",
  bundleId: "com.yourcompany.YourApp"
})

// Terminate via IDB
idb-app({
  operation: "terminate",
  bundleId: "com.yourcompany.YourApp"
})
```
</idb_alternative>

<launch_arguments>
**Launch with Arguments:**

```typescript
simctl-app({
  operation: "launch",
  bundleId: "com.example.App",
  launchArguments: [
    "--reset-onboarding",
    "--mock-api",
    "-UITesting"
  ],
  environmentVariables: {
    "API_BASE_URL": "http://localhost:8080",
    "DEBUG_LEVEL": "verbose"
  }
})
```

Common launch arguments:
- `-UITesting`: Enable UI testing mode
- `--reset-data`: Reset app data on launch
- `--mock-network`: Use mock network responses
</launch_arguments>

<success_criteria>
App deployment complete when:
- [ ] Simulator booted (or already running)
- [ ] App installed via simctl-app or auto-install
- [ ] App launched with appropriate arguments
- [ ] Bundle ID and paths handled correctly
- [ ] No manual UDID prompts (auto-detection used)
</success_criteria>