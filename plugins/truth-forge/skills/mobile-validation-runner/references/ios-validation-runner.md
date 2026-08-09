> Incorporated from the `ios-validation-runner` skill (skills-ref.zip).

## APPLICABILITY GUARD

This skill is for **iOS app validation** on macOS simulators using xcrun simctl, idb, and log streaming. Activates when validating iOS features through simulator evidence collection (screenshots, video, logs). Do not apply to Android, web apps, or unit/mock-based testing.

# iOS Validation Runner

## Before You Start

Ask yourself:
- **What am I validating?** A new feature, a bug fix, or a regression? This determines which screens to screenshot and what logs to grep for.
- **Is the simulator booted?** If not, boot it FIRST — `xcrun simctl boot` takes 5-10s and screenshots during boot show a black screen.
- **Is the backend required?** If the app needs a backend, verify it's healthy BEFORE launching the app. Apps that can't reach the backend show onboarding/error states, not the feature you're validating.
- **What does PASS look like?** Define it BEFORE collecting evidence. "App launches" is not a definition of PASS — "Home screen shows session count > 0 with correct total" is.

## The Five-Phase Protocol

```
SETUP → RECORD → ACT → COLLECT → VERIFY
```

Each phase produces artifacts in `$EVIDENCE_DIR`. The script at `../scripts/validate.sh` automates phases 1-4. **Phase 5 (VERIFY) is always manual** — you MUST visually inspect every screenshot.

### Phase 1: SETUP

**Environment Checklist** (all must be true before proceeding):

| Check | Command | FAIL Action |
|-------|---------|-------------|
| Simulator booted | `xcrun simctl list devices \| grep "$UDID"` | `xcrun simctl boot "$UDID"` then sleep 5 |
| Evidence dir exists | `mkdir -p "$EVIDENCE_DIR"` | Will be created |
| Backend healthy (if needed) | `curl -sf http://localhost:$PORT/health` | Start backend, poll up to 60s |
| Status bar clean | `xcrun simctl status_bar "$UDID" override --time "9:41" ...` | Always override before screenshots |

**Why override the status bar?** Real time, low battery, and carrier name make screenshots non-reproducible and look unprofessional in App Store submissions. Override BEFORE any screenshots.

**Project Configuration:** Set `UDID`, `BUNDLE_ID`, `BACKEND_PORT`, and `EVIDENCE_DIR` per project. Detect from `.xcodeproj`, `Info.plist`, or `CLAUDE.md`. Do not use hardcoded defaults without verifying they match your project.

### Phase 2: RECORD

Start video and log streaming BEFORE launching the app. This captures launch behavior.

**Video recording — the SIGINT rule:**
```bash
xcrun simctl io "$UDID" recordVideo --codec=h264 --force "$EVIDENCE_DIR/recording.mov" &
RECORD_PID=$!
```
- **MUST stop with `kill -SIGINT $RECORD_PID`** — this writes the MOV container index/trailer
- **NEVER use `kill -9`** — produces a corrupt file that won't play (missing container footer)
- **ALWAYS `wait $RECORD_PID`** after SIGINT — finalization takes 1-3 seconds

**Log streaming — the invisible flag trap:**
```bash
xcrun simctl spawn "$UDID" log stream \
  --predicate "subsystem == \"$BUNDLE_ID\"" \
  --info --debug \
  --style compact \
  > "$EVIDENCE_DIR/live-logs.txt" 2>/dev/null &
```
- **`--info --debug` is MANDATORY** — without them, Info/Debug level messages are silently dropped. Your app likely logs at Info level. You will see NOTHING without these flags.
- **`2>/dev/null`** — suppresses the harmless `getpwuid_r` stderr warning that pollutes output
- **Predicate is NSPredicate syntax**: `subsystem == "X"`, `CONTAINS[cd] "X"`, `AND`/`OR` for compound filters

**`log stream` vs `log show` — know the difference:**

| | `log stream` | `log show` |
|---|---|---|
| Direction | Future events (live) | Past events (archive) |
| Blocking | Yes — runs until killed | No — returns immediately |
| `--last` flag | NOT supported | Supported (`60s`, `5m`, `1h`) |
| Use case | Capture during test | Belt-and-suspenders after test |

Run BOTH: `log stream` during the test, `log show --last 120s` after. The stream can miss events at start/stop due to race conditions.

### Phase 3: ACT

Install, launch, interact, screenshot. The order matters:

1. **Terminate existing instance** — `xcrun simctl terminate` (stale state causes false results)
2. **Install fresh build** — `xcrun simctl install "$UDID" "$APP_PATH"` (use DerivedData path, NOT `build/`)
3. **Launch** — `xcrun simctl launch "$UDID" "$BUNDLE_ID"`
4. **Wait for UI settle** — sleep 3 minimum (SwiftUI `onAppear` + data loading + animation)
5. **Screenshot key states** — `xcrun simctl io "$UDID" screenshot "$EVIDENCE_DIR/01-name.png"`
6. **Interact** — deep links (`openurl`), taps (`idb_tap`), text input (`idb ui text`)
7. **Screenshot after each action** — number sequentially: `01-`, `02-`, `03-`

**Deep link gotchas:**
- UUIDs in URLs must be **lowercase** — uppercase silently fails
- App must be **foregrounded** or the OS shows "Open in App?" dialog
- URL scheme must be registered in Info.plist

**Timing gotchas:**
- Too short sleep after launch → black screenshot (app hasn't rendered)
- Too short sleep after deep link → previous screen (navigation hasn't completed)
- **3 seconds** is the safe minimum for most state transitions

### Phase 4: COLLECT

1. Stop log stream (`kill` + `wait`)
2. Capture historical logs (`log show --last 120s`) as belt-and-suspenders
3. Stop video recording (`kill -SIGINT` + `wait`) — finalization takes 1-3s
4. Check for crash reports: `ls -t ~/Library/Logs/DiagnosticReports/*.ips | head -5`
5. Clear status bar override: `xcrun simctl status_bar "$UDID" clear`

### Phase 5: VERIFY — The Critical Phase

**You MUST do all of these. Skipping any one is a violation.**

1. **READ every screenshot** with the Read tool — visually inspect each one
2. **Grep logs for errors**: `grep -ci "error" live-logs.txt`
3. **Check crash reports**: new `.ips` files = app crashed during test
4. **Note the video path** for manual review if needed
5. **Write the verdict**:

```
VERDICT:
- Screenshots: [PASS/FAIL] — [what they show]
- Logs: [PASS/FAIL] — [error count, key entries]
- Crashes: [PASS/FAIL] — [none / details]
- OVERALL: [PASS/FAIL] — [evidence-backed reason]
```

## The `../scripts/validate.sh` Script

**MANDATORY — READ BEFORE FIRST USE**: The `../scripts/validate.sh` script automates phases 1-4. Before running it, read the script to understand its environment variables:

```bash
UDID=<simulator-uuid> \
BUNDLE_ID=com.your.app \
BACKEND_PORT=9999 \
DURATION=10 \
  bash scripts/validate.sh
```

Key env vars: `UDID`, `BUNDLE_ID`, `LOG_SUBSYSTEM`, `BACKEND_PORT`, `EVIDENCE_DIR`, `DURATION`, `SKIP_VIDEO`, `SKIP_LOGS`, `SKIP_STATUS_BAR`.

**Do NOT use this script as a substitute for Phase 5.** The script collects evidence. You must still inspect it.

## NEVER

- **NEVER use `kill -9` on video recording** — produces a corrupt MOV file missing the container footer. Use `kill -SIGINT` and `wait` for the process to finalize. This wastes 10+ minutes re-recording when you realize the video won't play.
- **NEVER omit `--info --debug` from log streaming** — without them, you capture only Error/Fault level logs. Most app logging is at Info level. You will see zero useful entries and waste time wondering why logs are empty.
- **NEVER screenshot without checking the screen first** — if the app shows a loading spinner, error dialog, or onboarding flow, your screenshot is evidence of a PROBLEM, not evidence of a PASS. Don't blindly capture and move on.
- **NEVER claim PASS without reading every screenshot** — this is the #1 validation failure. Sub-agents report "PASS" based on file existence, not content. A screenshot of a crash dialog is still a .png file.
- **NEVER start log streaming AFTER app launch** — you miss all launch-time logs including initialization errors, network connection failures, and first-render issues. Start streaming BEFORE launch.
- **NEVER use `booted` as UDID in multi-session environments** — if other AI sessions have simulators running, `booted` picks a random one. Always use the explicit UDID.
- **NEVER trust sleep timing universally** — 3s is enough for most transitions, but heavy data loads (1000+ items) or slow backends may need 5-10s. If screenshots show loading states, increase sleep.
- **NEVER use the `build/` directory for .app path** — Xcode builds to `~/Library/Developer/Xcode/DerivedData/`, not to a local `build/` directory. Check with `find ~/Library/Developer/Xcode/DerivedData/ -name "*.app" -path "*/Debug-iphonesimulator/*" | head -1`.

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Starting log stream AFTER app launch | Misses all launch-time logs: initialization errors, network failures, first-render issues | Start `log stream` BEFORE `simctl launch` |
| Using `kill -9` on video recording | Produces corrupt MOV file missing container footer — video won't play | Use `kill -SIGINT` then `wait $PID` for finalization |
| Omitting `--info --debug` from log stream | Only captures Error/Fault level; most app logging is at Info level — you see nothing useful | Always include `--info --debug` flags |
| Screenshotting without checking render state | If app shows spinner, error dialog, or onboarding, your screenshot is evidence of a problem, not PASS | Wait 3+ seconds after transitions; verify screen content before capturing |
| Claiming PASS based on file existence | A screenshot of a crash dialog is still a .png file — existence proves nothing | READ every screenshot with the Read tool; describe what you SEE |

## When NOT to Use

- Android or cross-platform mobile validation (iOS simulators only)
- Web application validation (use `agent-browser` or `e2e-validate`)
- Unit or mock-based testing (violates functional validation mandate)
- Projects without an Xcode workspace or iOS target
