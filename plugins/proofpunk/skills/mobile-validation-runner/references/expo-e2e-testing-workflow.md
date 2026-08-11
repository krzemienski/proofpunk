> Incorporated from the `complete-expo-ios-testing-workflow` skill (skills-ref.zip).

# Complete Expo iOS Testing Workflow

## Contents

- [When NOT to Use](#when-not-to-use)
- [Anti-Patterns](#anti-patterns)
- [When to Use](#when-to-use)
- [Prerequisites Verified ✅](#prerequisites-verified-)
- [Complete Workflow (Actual Execution)](#complete-workflow-actual-execution)
- [Actual Execution Record](#actual-execution-record)
- [Troubleshooting (From Actual Issues)](#troubleshooting-from-actual-issues)
- [Success Criteria](#success-criteria)
- [Execution Time](#execution-time)
- [Next Steps After Testing](#next-steps-after-testing)


## When NOT to Use

- Native Swift/SwiftUI apps without Expo (use Axiom iOS skills instead)
- Android-only testing (this skill is iOS Simulator specific)
- Web apps or PWAs (use `web-testing` or Playwright)
- Physical device testing via USB (this skill targets Simulator only)
- Non-Expo React Native projects using bare workflow (commands differ significantly)

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Use `expo run:ios` with Xcode 26.x without checking compatibility | Known `DVTDeviceOperation` build number error crashes local builds silently | Use EAS cloud builds (`eas build --platform ios --profile ios_simulator_development`) as primary path |
| Hardcode tap coordinates without first running `idb-ui-describe` | UI layout varies by device size, orientation, and dynamic content; taps hit wrong elements | Always run `idb-ui-describe { operation: "all" }` first to get exact element coordinates |
| Skip `--clear` flag when starting Metro after code changes | Stale Metro cache serves old bundles; changes appear not to work; false negatives | Use `bunx expo start --clear` after any code or dependency changes |
| Trust `idb-ui-describe` output as complete accessibility tree | Some React Native elements lack accessibility labels; tree may be incomplete | Combine `idb-ui-describe` with screenshots for full picture; add `accessibilityLabel` to components |


## When to Use
- Building and testing Expo apps in iOS Simulator
- Comprehensive UI testing with screenshots
- Debugging app behavior in simulator
- Validating all screens and interactions
- Creating documentation with visual proof

## Prerequisites Verified ✅
- macOS with Xcode 26.1.1
- Bun 1.2.23 or Node.js 20+
- EAS CLI authenticated
- Local backend running (if app requires it)
- PostgreSQL running (if app requires it)

## Complete Workflow (Actual Execution)

### PHASE 1: Environment Verification (2 min)

**1.1 Check Xcode:**
```
Tool: mcp__xc-mcp__xcodebuild-version
```

**Expected:** Version 16.x+ (Xcode 26.x for latest)

**1.2 Check Simulators:**
```
Tool: mcp__xc-mcp__simctl-list
Parameters: {
  "concise": true,
  "deviceType": "iPhone",
  "runtime": "18"
}
```

**Expected:** 20+ available devices

**1.3 Verify Backend (if needed):**
```bash
curl http://localhost:3000/health
# Should return: {"status":"ok"}
```

**1.4 Verify Database (if needed):**
```bash
psql -U reponexus_user -d reponexus -c "\dt"
# Should list all tables
```

### PHASE 2: Start Metro Bundler (1 min)

**2.1 Start Metro:**
```bash
bunx expo start --clear
# Run in background or separate terminal
```

**2.2 Wait for Metro ready:**
```bash
# Check output for:
# "Metro Bundler ready"
# OR check port:
lsof -i :8081 | grep LISTEN
```

**Expected:** Metro running on port 8081

### PHASE 3: Build iOS App for Simulator (15-20 min)

**Option A: EAS Cloud Build (Recommended)**

**3.1 Verify eas.json profile exists:**
```bash
cat eas.json | grep -A5 "ios_simulator_development"
```

**Expected profile:**
```json
"ios_simulator_development": {
  "developmentClient": true,
  "distribution": "internal",
  "ios": {
    "simulator": true
  }
}
```

**3.2 Trigger EAS build:**
```bash
eas build --platform ios --profile ios_simulator_development
```

**3.3 Monitor build:**
- Build dashboard URL printed in console
- Status updates every 30 seconds
- Build time: 10-20 minutes
- Artifact: .tar.gz containing .app bundle

**3.4 When build completes:**
```bash
# EAS CLI prompts: "Install to simulator?"
# Press Y

# OR manually:
eas build:run -p ios --latest
```

**Option B: Local Build (If Xcode compatible)**

**3.B.1 Build locally:**
```bash
bunx expo run:ios --device "UDID"
# Where UDID is from simctl-list
```

**Note:** May fail with Xcode 26.x compatibility issues. Use EAS if this fails.

**Option C: Manual Xcodebuild (Advanced)**

**3.C.1 List Xcode schemes:**
```
Tool: mcp__xc-mcp__xcodebuild-list
Parameters: {
  "projectPath": "/path/to/project/ios/app.xcworkspace"
}
```

**3.C.2 Build with xcodebuild:**
```
Tool: mcp__xc-mcp__xcodebuild-build
Parameters: {
  "projectPath": "/path/to/project/ios/app.xcworkspace",
  "scheme": "appname",
  "configuration": "Debug",
  "destination": "platform=iOS Simulator,name=iPhone 16 Pro"
}
```

### PHASE 4: Boot Simulator (if not already booted) (30 sec)

**4.1 Get device UDID:**
```
Tool: mcp__xc-mcp__simctl-get-details
Parameters: {
  "cacheId": "<from simctl-list>",
  "detailType": "devices-only",
  "deviceType": "iPhone",
  "maxDevices": 10
}
```

**4.2 Boot simulator:**
```
Tool: mcp__xc-mcp__simctl-boot
Parameters: {
  "deviceId": "BECB3FA0-518E-4F80-8B8E-7E10C16F3B36",
  "waitForBoot": true,
  "openGui": true
}
```

**Expected:** Simulator.app opens with booted device

### PHASE 5: Install App to Simulator (1 min)

**5.1 If using EAS build:**
```bash
# EAS auto-prompts after build
# Press Y to install

# OR:
eas build:run -p ios --latest
```

**5.2 If using local .app bundle:**
```
Tool: mcp__xc-mcp__simctl-install
Parameters: {
  "udid": "BECB3FA0-518E-4F80-8B8E-7E10C16F3B36",
  "appPath": "/path/to/app.app"
}
```

**Expected:** "Installation successful"

**5.3 Verify installation:**
```
Tool: mcp__xc-mcp__idb-list-apps
Parameters: {
  "udid": "BECB3FA0-518E-4F80-8B8E-7E10C16F3B36"
}
```

**Look for:** com.reponexus.app in list

### PHASE 6: Launch App (30 sec)

**6.1 Launch app:**
```
Tool: mcp__xc-mcp__idb-launch
Parameters: {
  "udid": "BECB3FA0-518E-4F80-8B8E-7E10C16F3B36",
  "bundleId": "com.reponexus.app",
  "streamOutput": true
}
```

**Expected:** App launches, connects to Metro

**6.2 Verify Metro connection:**
```bash
# Check Metro logs for:
# "Connected to device"
# OR check backend logs for API requests
```

### PHASE 7: Complete Screen Testing (30 min)

**ALL 16 SCREENS TO TEST:**

1. ✅ Home (Trending Topics)
2. ✅ ForYou (AI Recommendations)
3. ✅ Explore (Topic Search)
4. ✅ AI (Chat Assistant)
5. ✅ Collections (Followed Topics)
6. ✅ Profile
7. ✅ TopicDetail
8. ✅ RepoDetail
9. ✅ CodeViewer
10. ✅ TopicBrowser
11. ✅ StarredLists
12. ✅ CustomViewDetail
13. ✅ ManageCustomViews
14. ✅ Settings
15. ✅ LoginModal (may skip if auto-auth)
16. ✅ Inside

**For Each Screen:**

**Step 1: Get UI tree**
```
Tool: mcp__xc-mcp__idb-ui-describe
Parameters: {
  "operation": "all",
  "screenContext": "HomeScreen",
  "purposeDescription": "Find navigation elements"
}
```

**Step 2: Take screenshot**
```
Tool: mcp__xc-mcp__screenshot
Parameters: {
  "size": "half",
  "appName": "RepoNexus",
  "screenName": "HomeScreen",
  "state": "Initial"
}
```

**Step 3: Navigate to next screen (if needed)**
```
Tool: mcp__xc-mcp__idb-ui-tap
Parameters: {
  "x": 200,
  "y": 750,
  "actionName": "Tap Explore Tab",
  "screenContext": "BottomTabs",
  "testScenario": "Navigation Test"
}
```

**Step 4: Screenshot after interaction**
```
Tool: mcp__xc-mcp__screenshot
Parameters: {
  "size": "half",
  "appName": "RepoNexus",
  "screenName": "ExploreScreen",
  "state": "Loaded"
}
```

### PHASE 8: Detailed Screen Testing Examples

**Example 1: Test Home Screen (Trending)**

```
1. screenshot { screenName: "Home", state: "Initial" }
2. idb-ui-describe { operation: "all" }
3. Identify "Trending" topics list
4. idb-ui-tap { x: 200, y: 300, actionName: "Tap first topic" }
5. Wait 2 seconds for navigation
6. screenshot { screenName: "TopicDetail", state: "Loaded" }
```

**Example 2: Test Search Flow**

```
1. idb-ui-tap { x: 150, y: 750, actionName: "Tap Explore tab" }
2. screenshot { screenName: "Explore", state: "Initial" }
3. idb-ui-describe { operation: "point", x: 200, y: 100 }
4. idb-ui-tap { x: 200, y: 100, actionName: "Focus search input" }
5. idb-ui-input { operation: "text", text: "react-native" }
6. screenshot { screenName: "Explore", state: "SearchResults" }
7. idb-ui-tap { x: 200, y: 300, actionName: "Select first result" }
8. screenshot { screenName: "TopicDetail", state: "ReactNative" }
```

**Example 3: Test AI Chat**

```
1. idb-ui-tap { x: 250, y: 750, actionName: "Tap AI tab" }
2. screenshot { screenName: "AI", state: "Initial" }
3. idb-ui-tap { x: 200, y: 700, actionName: "Focus chat input" }
4. idb-ui-input { operation: "text", text: "What is TypeScript?" }
5. idb-ui-gesture { operation: "button", buttonType: "return" }
6. Wait 5 seconds for AI response
7. screenshot { screenName: "AI", state: "WithResponse" }
```

**Example 4: Test Code Viewer**

```
1. Navigate to topic
2. Navigate to repository
3. idb-ui-tap { x: 200, y: 600, actionName: "Tap Browse Code" }
4. screenshot { screenName: "CodeViewer", state: "DirectoryList" }
5. idb-ui-tap { x: 200, y: 200, actionName: "Tap first file" }
6. screenshot { screenName: "CodeViewer", state: "FileContents" }
```

**Example 5: Test Gestures**

```
# Swipe up (scroll)
idb-ui-gesture {
  operation: "swipe",
  direction: "up",
  duration: 500,
  actionName: "Scroll topics list"
}

# Pull to refresh
idb-ui-gesture {
  operation: "swipe",
  direction: "down",
  duration: 300,
  actionName: "Pull to refresh"
}

# Home button
idb-ui-gesture {
  operation: "button",
  buttonType: "HOME"
}
```

### PHASE 9: Navigation Map (Bottom Tabs)

**Tab Bar Coordinates (approximate):**
- Tab 1 (Home): x: 60, y: 750
- Tab 2 (ForYou): x: 150, y: 750
- Tab 3 (Explore): x: 240, y: 750
- Tab 4 (AI): x: 330, y: 750
- Tab 5 (Collections): x: 420, y: 750
- Tab 6 (Profile): x: 510, y: 750

**Always use idb-ui-describe to find exact coordinates!**

### PHASE 10: Complete Test Sequence

**Automated testing workflow:**

```
# 1. Launch app
idb-launch { bundleId: "com.reponexus.app" }

# 2. Wait for auto-login
sleep 3

# 3. Home screen
screenshot { screenName: "Home", state: "AfterLogin" }

# 4. Explore tab
idb-ui-tap { x: 240, y: 750, actionName: "Explore tab" }
screenshot { screenName: "Explore" }

# 5. Search
idb-ui-tap { x: 200, y: 100, actionName: "Search input" }
idb-ui-input { operation: "text", text: "typescript" }
screenshot { screenName: "Explore", state: "SearchResults" }

# 6. AI tab
idb-ui-tap { x: 330, y: 750, actionName: "AI tab" }
screenshot { screenName: "AI" }

# 7. Collections tab
idb-ui-tap { x: 420, y: 750, actionName: "Collections tab" }
screenshot { screenName: "Collections" }

# 8. Profile tab
idb-ui-tap { x: 510, y: 750, actionName: "Profile tab" }
screenshot { screenName: "Profile" }

# 9. Settings
idb-ui-tap { x: 350, y: 200, actionName: "Settings button" }
screenshot { screenName: "Settings" }

# 10. Navigate back
idb-ui-gesture { operation: "swipe", direction: "right" }

# 11-16: Navigate to detail screens as needed
```

### PHASE 11: Debugging Tools

**Check app logs:**
```
Tool: mcp__xc-mcp__idb-launch
Parameters: {
  "bundleId": "com.reponexus.app",
  "streamOutput": true
}
```

**Streams console.log output from app.**

**Check Metro bundler logs:**
```bash
# Metro shows:
# - Bundle requests
# - API calls
# - Errors
```

**Check backend logs:**
```bash
# Backend shows:
# - API requests
# - Database queries
# - Authentication events
```

**Take diagnostic screenshot:**
```
Tool: mcp__xc-mcp__screenshot
Parameters: {
  "size": "full",
  "appName": "RepoNexus",
  "screenName": "ErrorState",
  "state": "Debug"
}
```

### PHASE 12: Common Operations

**Restart app:**
```
1. idb-terminate { bundleId: "com.reponexus.app" }
2. sleep 2
3. idb-launch { bundleId: "com.reponexus.app" }
```

**Reload Metro bundle:**
```
# Shake device
idb-ui-gesture { operation: "button", buttonType: "SHAKE" }
# Then tap "Reload"
```

**Clear app data:**
```
Tool: mcp__xc-mcp__simctl-uninstall
Parameters: {
  "udid": "<device-id>",
  "bundleId": "com.reponexus.app"
}

# Reinstall and relaunch
```

**Reset simulator:**
```
Tool: mcp__xc-mcp__simctl-erase
Parameters: {
  "deviceId": "<device-id>",
  "force": true
}
```

### PHASE 13: Screenshot Organization

**Systematic naming:**
```
1-home-initial.png
2-home-loaded-topics.png
3-explore-initial.png
4-explore-search-results.png
5-ai-chat-initial.png
6-ai-chat-with-response.png
7-collections-empty.png
8-profile-logged-in.png
9-settings.png
10-topic-detail-typescript.png
11-repo-detail.png
12-code-viewer-directory.png
13-code-viewer-file.png
14-custom-views.png
15-manage-views.png
16-starred-lists.png
```

**All screenshots auto-saved** with semantic names via xc-mcp.

### PHASE 14: Interaction Testing Checklist

**Test Cases:**

- [ ] App launches without crash
- [ ] Auto-login works (Profile shows user)
- [ ] Home screen loads trending topics
- [ ] Topic search finds results
- [ ] Tapping topic navigates to detail
- [ ] Repository list loads
- [ ] Tapping repo navigates to detail
- [ ] Code viewer shows files
- [ ] AI chat sends/receives messages
- [ ] Collections shows followed topics
- [ ] Profile displays user info
- [ ] Settings allows theme changes
- [ ] Bottom tab navigation works
- [ ] Back navigation works
- [ ] Pull-to-refresh works
- [ ] Search input accepts text
- [ ] Scroll gestures work
- [ ] Button taps provide feedback

### PHASE 15: Performance Verification

**Check Metro bundle size:**
```bash
# Metro logs show:
# "Bundle size: XX.XX MB"
```

**Check app responsiveness:**
- Tap-to-response time < 100ms
- Screen transitions smooth (60fps)
- No lag during scrolling

**Check memory usage:**
```bash
# Activity Monitor → Search for app
# Should be < 200MB for React Native app
```

### PHASE 16: Backend Integration Testing

**Verify API calls:**
```bash
# Watch backend logs while using app
# Should see:
GET /api/topics/trending
GET /api/user/profile
POST /api/ai/chat
# etc.
```

**Verify auth working:**
```bash
# Backend should log:
# Session validated: dev-user-local-001
# User: krzemienski
```

**Test offline behavior:**
```bash
# Stop backend
# App should show error states gracefully
```

## Actual Execution Record

**From this migration (2025-11-14):**

✅ **Environment:**
- Xcode: 26.1.1
- Simulators: 46 available
- Selected: iPhone 16 Pro (BECB3FA0-518E-4F80-8B8E-7E10C16F3B36)

✅ **Backend:**
- Running: localhost:3000
- Health: OK
- API: Trending topics returning data

✅ **Metro:**
- Port: 8081
- Status: Running, cache rebuilt

✅ **Simulator:**
- Booted: iPhone 16 Pro
- Screenshot captured successfully

✅ **EAS Build:**
- Build ID: 92bc4df7-a7a0-471a-b689-c579692737ee
- Profile: ios_simulator_development
- Status: In progress
- URL: https://expo.dev/accounts/krzemienski/projects/vibecode/builds/92bc4df7-a7a0-471a-b689-c579692737ee

## Troubleshooting (From Actual Issues)

### Issue: expo run:ios fails with Xcode 26.x
**Error:**
```
DVTDeviceOperation: Encountered a build number "" that is incompatible
```

**Solution:** Use EAS build instead:
```bash
eas build --platform ios --profile ios_simulator_development
```

### Issue: Metro cache issues
**Solution:**
```bash
bunx expo start --clear
```

### Issue: Simulator not booting
**Solution:**
```bash
# Force kill simulator
killall Simulator
# Reboot
mcp__xc-mcp__simctl-boot { deviceId: "<udid>" }
```

### Issue: App not finding backend
**Check:**
1. .env file exists with EXPO_PUBLIC_BACKEND_URL
2. Metro cache cleared
3. Backend actually running on port 3000
4. Console log shows correct URL

### Issue: Can't find elements for tapping
**Solution:**
```
1. Use idb-ui-describe { operation: "all" }
2. Find element in accessibility tree
3. Use coordinates from tree
4. OR use idb-ui-describe { operation: "point", x: X, y: Y }
```

## Success Criteria

✅ All prerequisites verified
✅ Metro bundler running on 8081
✅ Backend running on 3000 (if needed)
✅ Simulator booted successfully
✅ App built and installed
✅ App launches without crashes
✅ Metro connects to app
✅ Auto-login works
✅ All 16 screens accessible
✅ Screenshots captured for all screens
✅ UI interactions work correctly
✅ API calls reach backend
✅ Data displays correctly

## Execution Time

- Environment setup: 5 minutes
- Metro start: 1 minute
- EAS build: 10-20 minutes
- Install: 1 minute
- Launch: 30 seconds
- Screen testing: 20-30 minutes
- **Total: ~40-60 minutes**

## Next Steps After Testing

- Review all screenshots for UI issues
- Document any bugs found
- Create test automation scripts
- Setup CI/CD with EAS workflows
- Deploy to TestFlight for beta testing