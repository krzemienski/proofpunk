> Incorporated from the `expo-ios-complete-testing-workflow` skill (skills-ref.zip).

## APPLICABILITY GUARD

This skill is for **Expo React Native apps** being tested on **iOS Simulator**. Requires macOS, Xcode, and EAS CLI. Do not apply to native Swift/Kotlin projects, web apps, or Android-only workflows.

## When NOT to Use

- Native Swift/SwiftUI apps (use Axiom iOS skills instead)
- Android-only testing (use Android emulator tools directly)
- Web apps or PWAs (use `web-testing` or Playwright)
- Expo apps targeting physical devices only (use TestFlight or EAS internal distribution)

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Use `eas build --local` with Xcode 26.x | Known Xcode SDK mismatch causes exit code 70; wastes 10+ minutes before failing | Use EAS cloud build until Expo SDK adds Xcode 26.x local build support |
| Hardcode tap coordinates without taking a screenshot first | Screen layout changes between devices, orientations, and app states; taps miss targets | Always take a screenshot, identify element coordinates, then tap |
| Skip `--clear` flag when starting Metro after code changes | Stale Metro cache serves old bundles; new navigation/native changes don't appear | Always use `bunx expo start --clear` after structural changes |
| Assume `idb-ui-describe` returns complete accessibility tree | Returns minimal data for most React Native apps; leads to missing elements | Use screenshot-based interaction as primary method; accessibility tree as fallback |


## When to Use
- Building Expo apps for iOS Simulator testing
- Testing React Native apps with local backend
- Debugging Metro bundler issues
- Navigating and screenshotting all app screens
- When local `eas build --local` fails with Xcode compatibility errors

## Prerequisites
- macOS with Xcode installed
- EAS CLI authenticated (`eas login`)
- Metro bundler capability (`bunx expo start`)
- Backend server running (if app needs it)
- xc-mcp tools available

## Complete Workflow (Based on Actual Execution 2025-11-14)

### PHASE 1: Start Local Services (2 min)

**1.1 Start Backend:**
```bash
cd backend
bun run dev
# Verify: curl http://localhost:3000/health
```

**1.2 Start Metro:**
```bash
bunx expo start --clear
# Wait for: "Metro Bundler ready"
# Runs on: http://localhost:8081
```

**1.3 Verify Services:**
```bash
lsof -i :3000 | grep LISTEN  # Backend
lsof -i :8081 | grep LISTEN  # Metro
```

### PHASE 2: Boot Simulator (30 sec)

**2.1 List available simulators:**
```
Tool: mcp__xc-mcp__simctl-list
Parameters: {
  "concise": true,
  "deviceType": "iPhone"
}
```

**2.2 Boot chosen simulator:**
```
Tool: mcp__xc-mcp__simctl-boot
Parameters: {
  "deviceId": "<UDID from list>",
  "waitForBoot": true,
  "openGui": true
}
```

### PHASE 3: Build App (Choose One Method)

**Option A: Cloud Build (WORKS - Recommended for Xcode 26.1.1)**

```bash
eas build --platform ios --profile ios_simulator_development
# Time: 15-20 minutes
# Uploads code to EAS servers
# Builds in cloud
# Returns download URL
```

**Option B: Local Build (FAILS with Xcode 26.1.1 as of 2025-11-14)**

```bash
eas build --local --platform ios --profile ios_simulator_development
# Requires: fastlane installed
# Error: "iOS 26.1 is not installed" (SDK mismatch)
# Error: xcodebuild exit code 70
# BLOCKED until Expo SDK supports Xcode 26.x
```

**Recommendation:** Use cloud build until local build Xcode compatibility fixed.

### PHASE 4: Install App to Simulator (1 min)

**4.1 Download and install (if cloud build):**
```bash
eas build:run -p ios --latest
# Auto-downloads .app
# Auto-installs to booted simulator
# Auto-launches app
```

**4.2 Manual install (if you have .app file):**
```
Tool: mcp__xc-mcp__simctl-install
Parameters: {
  "udid": "<simulator-udid>",
  "appPath": "/path/to/YourApp.app"
}
```

### PHASE 5: Launch App (30 sec)

**5.1 Launch with simctl:**
```bash
xcrun simctl launch <udid> <bundle-id>
# Returns process ID
# Example: com.reponexus.app: 69821
```

**5.2 App shows Expo Dev Client launcher**
- Lists Metro servers on network
- Shows "http://localhost:8081" if Metro running
- Shows recently opened projects

**5.3 Connect to Metro:**
Use xc-mcp to tap the Metro server entry:
```
Tool: mcp__xc-mcp__idb-ui-tap
Parameters: {
  "x": 117,  // Screenshot coordinates
  "y": 332,
  "applyScreenshotScale": true,
  "screenshotScaleX": 1.67,
  "screenshotScaleY": 1.66,
  "actionName": "Tap Metro server"
}
```

### PHASE 6: Monitor and Debug (Continuous)

**6.1 Watch Metro console:**
```bash
# Metro shows in foreground, or check background job
# Look for:
# - "Bundled X modules"
# - Console.log output from app
# - Error messages
```

**6.2 Watch backend logs:**
```bash
# Backend terminal shows API requests:
# - GET /api/topics/trending
# - GET /api/user/profile
# - POST /api/simple-auth/login
```

**6.3 System logs (alternative):**
```bash
log stream --predicate 'process == "AppName"' --level debug
# Shows all app logs
# More comprehensive than Metro
```

### PHASE 7: Interact and Test (Iterative)

**7.1 Take screenshot to see current state:**
```
Tool: mcp__xc-mcp__screenshot
Parameters: {
  "size": "half",
  "appName": "YourApp",
  "screenName": "CurrentScreen",
  "state": "Loaded"
}
```

**7.2 Get UI tree (if accessibility available):**
```
Tool: mcp__xc-mcp__idb-ui-describe
Parameters: {
  "operation": "all",
  "screenContext": "HomeScreen"
}
```

**Note:** Often returns minimal data. Fall back to screenshot-based interaction.

**7.3 Tap elements:**
```
Tool: mcp__xc-mcp__idb-ui-tap
Parameters: {
  "x": <from screenshot>,
  "y": <from screenshot>,
  "applyScreenshotScale": true,
  "screenshotScaleX": 1.67,
  "screenshotScaleY": 1.66,
  "actionName": "Descriptive action"
}
```

**7.4 Input text:**
```
Tool: mcp__xc-mcp__idb-ui-input
Parameters: {
  "operation": "text",
  "text": "search query"
}
```

**7.5 Gestures:**
```
Tool: mcp__xc-mcp__idb-ui-gesture
Parameters: {
  "operation": "swipe",
  "direction": "up"
}
```

OR

```
Tool: mcp__xc-mcp__idb-ui-gesture
Parameters: {
  "operation": "button",
  "buttonType": "HOME"
}
```

### PHASE 8: Iterate and Rebuild

**When code changes (JavaScript only):**
- Metro hot reloads automatically
- No rebuild needed
- Refresh with: Shake device → Reload

**When code changes (Navigation, native modules):**
- Need to rebuild app
- Cloud build: `eas build --platform ios --profile X`
- Download: `eas build:run -p ios --latest`
- Launch: `xcrun simctl launch <udid> <bundle-id>`

## Key Findings from Actual Execution

**What Works:**
- ✅ EAS cloud builds (15-20 min)
- ✅ `eas build:run` for install
- ✅ `xcrun simctl launch` for launching
- ✅ Metro console for debugging
- ✅ xc-mcp screenshot (half size recommended)
- ✅ xc-mcp idb-ui-tap for interactions
- ✅ Coordinate transformation (1.67x, 1.66y for half screenshots)

**What Doesn't Work (as of 2025-11-14):**
- ❌ `eas build --local` - Xcode 26.1.1 incompatibility
- ❌ `expo run:ios` - Same Xcode issue
- ❌ idb-ui-describe - Returns minimal accessibility data
- ❌ idb-launch with streamOutput - No output captured

**Workarounds:**
- Use cloud builds instead of local
- Use screenshot-based interaction instead of accessibility tree
- Use Metro console logs instead of idb streaming

## Tools Reference

**simctl tools (Apple native):**
- `simctl-list` - List simulators
- `simctl-boot` - Boot simulator
- `simctl-install` - Install .app
- Launch: Use `xcrun simctl launch` directly
- `simctl-io` - Screenshots/video

**idb tools (Facebook):**
- `idb-ui-tap` - Tap coordinates
- `idb-ui-input` - Type text
- `idb-ui-gesture` - Swipes, buttons
- `idb-ui-describe` - Get UI tree (often limited data)
- `idb-launch` - Launch app
- `idb-terminate` - Kill app

**Debugging:**
- Metro console: Shows console.log from app
- Backend logs: Shows API requests
- `log stream`: System logs (alternative)
- xc-mcp screenshot: Visual verification

## Common Issues

**Issue: "Could not connect to server"**
- Metro not running on 8081
- Solution: `bunx expo start --clear`

**Issue: "iOS 26.1 is not installed"**
- Xcode 26.1.1 incompatibility with Expo SDK 53
- Solution: Use cloud build instead of local

**Issue: App shows old code**
- Navigation changes need rebuild
- Hot reload doesn't work for structural changes
- Solution: Rebuild with `eas build`

**Issue: "Unable to find a destination"**
- xcodebuild can't find simulator
- Solution: Use cloud build (bypasses this issue)

## Success Criteria

✅ Backend running on localhost
✅ Metro running on localhost:8081
✅ Simulator booted
✅ App built (cloud or local)
✅ App installed via eas build:run OR simctl-install
✅ App launches and connects to Metro
✅ Metro logs show successful bundle
✅ Can take screenshots
✅ Can interact with UI via idb-ui-tap
✅ Backend receives API requests

## Time Estimates

- Local services: 2 minutes
- Boot simulator: 30 seconds
- Cloud build: 15-20 minutes
- Local build: 8-12 minutes (when working)
- Install: 1 minute
- Testing per screen: 2-3 minutes
- **Total first run: ~25-35 minutes**
- **Subsequent iterations: ~20 minutes** (rebuild only if native changes)

## Next Steps After App Working

1. Navigate through all screens
2. Screenshot each screen
3. Test key features (search, navigation, etc.)
4. Document any bugs
5. Create test automation scripts

This skill documents the ACTUAL working workflow as of November 2025 with Xcode 26.1.1.
