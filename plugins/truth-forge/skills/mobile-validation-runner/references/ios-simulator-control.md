> Incorporated from the `ios-simulator-control` skill (skills-ref.zip).

# iOS Simulator Control

## APPLICABILITY GUARD

**macOS with Xcode only.** Requires `xcrun simctl`. Do not apply to Android emulators, web browsers, or non-Apple platforms.

## When to Use

- Booting iOS simulators for testing workflows
- Installing and launching apps on simulator
- Capturing screenshot evidence for validation checkpoints
- Retrieving simulator logs for debugging
- Automating iOS testing lifecycle (boot → install → launch → capture → shutdown)

## When NOT to Use

- Android emulator control (use Android SDK tools)
- Real device testing (use `ios-validation-runner` with device targeting)
- UI interaction automation (use `ios-ui-automation` for tap/swipe/text)
- Web browser testing (use `playwright-skill` or `e2e-testing`)

## Anti-Patterns

| NEVER | WHY | Fix |
|-------|-----|-----|
| Capture screenshot immediately after launch | App needs time to render first frame; screenshot shows splash screen or blank | Wait 3-5 seconds after launch, or poll for specific UI element with `xcrun simctl ui` |
| Use device name string without checking availability | Device names change across Xcode versions (e.g., "iPhone 15 Pro" vs "iPhone 16 Pro") | Run `xcrun simctl list devices available` first and match against available devices |
| Skip `simctl shutdown` after test runs | Leaked simulators consume 2-4GB RAM each; system degrades after 3-4 leaked instances | Always shutdown in a cleanup step, even on test failure (use trap in bash) |
| Install .app bundle built for device architecture | ARM64 device builds won't run on x86_64 simulator (or vice versa) | Build with `xcodebuild -sdk iphonesimulator` to get correct architecture |
| Parse `simctl list` text output with regex | Output format changes between Xcode versions; regex breaks silently | Use `xcrun simctl list devices available -j` (JSON output) and parse with `jq` |


## Command Reference

### Device Lifecycle

```bash
# List available devices (JSON for reliable parsing)
xcrun simctl list devices available -j | jq '.devices | to_entries[] | .value[] | select(.isAvailable) | .name'

# Boot by name (find UDID first for reliability)
UDID=$(xcrun simctl list devices available -j | jq -r '.devices | to_entries[] | .value[] | select(.name == "iPhone 15 Pro") | .udid' | head -1)
xcrun simctl boot "$UDID"

# Shutdown and erase (clean state)
xcrun simctl shutdown "$UDID"
xcrun simctl erase "$UDID"
```

### App Management

```bash
# Install (must be simulator build)
xcrun simctl install "$UDID" path/to/App.app

# Launch (returns immediately)
xcrun simctl launch "$UDID" com.example.app

# Terminate
xcrun simctl terminate "$UDID" com.example.app

# Uninstall
xcrun simctl uninstall "$UDID" com.example.app
```

### Evidence Capture

```bash
# Screenshot (wait for render first)
sleep 3
xcrun simctl io "$UDID" screenshot output.png

# Video recording (stop with Ctrl+C or kill)
xcrun simctl io "$UDID" recordVideo output.mp4 &
RECORD_PID=$!
# ... run test actions ...
kill -INT $RECORD_PID
```

### Log Retrieval

```bash
# Stream logs (filtered by app)
xcrun simctl spawn "$UDID" log stream --predicate 'subsystem == "com.example.app"' --level debug

# Recent log entries
xcrun simctl spawn "$UDID" log show --last 5m --predicate 'subsystem == "com.example.app"'
```

## Reliable Boot Pattern

```bash
#!/bin/bash
# Boot simulator with cleanup trap
DEVICE_NAME="${1:-iPhone 15 Pro}"
UDID=$(xcrun simctl list devices available -j | jq -r ".devices | to_entries[] | .value[] | select(.name == \"$DEVICE_NAME\") | .udid" | head -1)

if [ -z "$UDID" ]; then echo "Device not found: $DEVICE_NAME"; exit 1; fi

trap "xcrun simctl shutdown '$UDID' 2>/dev/null" EXIT
xcrun simctl boot "$UDID" 2>/dev/null || true  # OK if already booted
xcrun simctl bootstatus "$UDID" -b  # Wait until fully booted
```
