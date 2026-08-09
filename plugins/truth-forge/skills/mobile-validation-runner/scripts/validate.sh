#!/bin/bash
# ──────────────────────────────────────────────────────────────────
# iOS Validation Runner — Automated Evidence Collection
# ──────────────────────────────────────────────────────────────────
# Usage:
#   ./validate.sh                          # Use defaults (booted sim)
#   UDID=<uuid> BUNDLE_ID=com.app ./validate.sh
#   UDID=<uuid> BUNDLE_ID=com.app BACKEND_PORT=9090 ./validate.sh
#
# Environment Variables:
#   UDID            — Simulator UDID (default: "booted")
#   BUNDLE_ID       — App bundle identifier (required)
#   LOG_SUBSYSTEM   — os_log subsystem to filter (default: $BUNDLE_ID)
#   BACKEND_PORT    — Backend port to health-check (default: none/skip)
#   BACKEND_HEALTH  — Health endpoint path (default: /api/v1/health)
#   EVIDENCE_DIR    — Output directory (default: /tmp/validation-evidence/<timestamp>)
#   DURATION        — How long to record after launch, in seconds (default: 10)
#   SKIP_VIDEO      — Set to "1" to skip video recording
#   SKIP_LOGS       — Set to "1" to skip log streaming
#   SKIP_STATUS_BAR — Set to "1" to skip status bar override
# ──────────────────────────────────────────────────────────────────
set -euo pipefail

# ─── Configuration ───
UDID="${UDID:-booted}"
BUNDLE_ID="${BUNDLE_ID:?ERROR: BUNDLE_ID is required. Set BUNDLE_ID=com.your.app}"
LOG_SUBSYSTEM="${LOG_SUBSYSTEM:-$BUNDLE_ID}"
BACKEND_PORT="${BACKEND_PORT:-}"
BACKEND_HEALTH="${BACKEND_HEALTH:-/api/v1/health}"
EVIDENCE_DIR="${EVIDENCE_DIR:-/tmp/validation-evidence/$(date +%Y%m%d-%H%M%S)}"
DURATION="${DURATION:-10}"
SKIP_VIDEO="${SKIP_VIDEO:-0}"
SKIP_LOGS="${SKIP_LOGS:-0}"
SKIP_STATUS_BAR="${SKIP_STATUS_BAR:-0}"

RECORD_PID=""
LOG_PID=""

mkdir -p "$EVIDENCE_DIR"

echo "═══════════════════════════════════════════════"
echo "  iOS Validation Runner"
echo "═══════════════════════════════════════════════"
echo "  UDID:         $UDID"
echo "  Bundle ID:    $BUNDLE_ID"
echo "  Subsystem:    $LOG_SUBSYSTEM"
echo "  Evidence:     $EVIDENCE_DIR"
echo "  Duration:     ${DURATION}s"
[ -n "$BACKEND_PORT" ] && echo "  Backend:      localhost:$BACKEND_PORT"
echo "═══════════════════════════════════════════════"

# ─── Cleanup Trap ───
cleanup() {
  echo ""
  echo "── Cleanup ──"
  if [ -n "$RECORD_PID" ]; then
    echo "  Stopping video recording (SIGINT)..."
    kill -SIGINT "$RECORD_PID" 2>/dev/null || true
    wait "$RECORD_PID" 2>/dev/null || true
    RECORD_PID=""
  fi
  if [ -n "$LOG_PID" ]; then
    echo "  Stopping log stream..."
    kill "$LOG_PID" 2>/dev/null || true
    wait "$LOG_PID" 2>/dev/null || true
    LOG_PID=""
  fi
  if [ "$SKIP_STATUS_BAR" != "1" ]; then
    xcrun simctl status_bar "$UDID" clear 2>/dev/null || true
  fi
  echo "  Cleanup complete."
}
trap cleanup EXIT

# ═══════════════════════════════════════════════
# Phase 1: SETUP
# ═══════════════════════════════════════════════
echo ""
echo "── Phase 1: SETUP ──"

# 1.1 Verify simulator is booted
if [ "$UDID" != "booted" ]; then
  SIM_STATE=$(xcrun simctl list devices | grep "$UDID" | head -1)
  if echo "$SIM_STATE" | grep -q "(Shutdown)"; then
    echo "  Booting simulator $UDID..."
    xcrun simctl boot "$UDID"
    sleep 5
  fi
fi
echo "  Simulator: ready"

# 1.2 Override status bar
if [ "$SKIP_STATUS_BAR" != "1" ]; then
  xcrun simctl status_bar "$UDID" override \
    --time "9:41" \
    --batteryState charged \
    --batteryLevel 100 \
    --wifiBars 3 \
    --cellularBars 4 \
    --operatorName "" 2>/dev/null || true
  echo "  Status bar: overridden (9:41, full battery)"
fi

# 1.3 Backend health check
if [ -n "$BACKEND_PORT" ]; then
  echo "  Checking backend on port $BACKEND_PORT..."
  HEALTHY=0
  for i in $(seq 1 30); do
    if curl -sf "http://localhost:${BACKEND_PORT}${BACKEND_HEALTH}" > /dev/null 2>&1; then
      HEALTHY=1
      break
    fi
    sleep 1
  done
  if [ "$HEALTHY" -eq 1 ]; then
    echo "  Backend: healthy"
  else
    echo "  ERROR: Backend not healthy after 30s on port $BACKEND_PORT"
    echo "  Start your backend and try again."
    exit 1
  fi
fi

# ═══════════════════════════════════════════════
# Phase 2: RECORD
# ═══════════════════════════════════════════════
echo ""
echo "── Phase 2: RECORD ──"

# 2.1 Start video recording
if [ "$SKIP_VIDEO" != "1" ]; then
  xcrun simctl io "$UDID" recordVideo \
    --codec=h264 \
    --force \
    "$EVIDENCE_DIR/recording.mov" &
  RECORD_PID=$!
  sleep 2
  echo "  Video: recording (PID $RECORD_PID)"
else
  echo "  Video: skipped"
fi

# 2.2 Start log streaming
if [ "$SKIP_LOGS" != "1" ]; then
  xcrun simctl spawn "$UDID" log stream \
    --predicate "subsystem == \"$LOG_SUBSYSTEM\"" \
    --info --debug \
    --style compact \
    > "$EVIDENCE_DIR/live-logs.txt" 2>/dev/null &
  LOG_PID=$!
  echo "  Logs: streaming (PID $LOG_PID)"
else
  echo "  Logs: skipped"
fi

# ═══════════════════════════════════════════════
# Phase 3: ACT
# ═══════════════════════════════════════════════
echo ""
echo "── Phase 3: ACT ──"

# 3.1 Terminate and relaunch app
xcrun simctl terminate "$UDID" "$BUNDLE_ID" 2>/dev/null || true
sleep 1
xcrun simctl launch "$UDID" "$BUNDLE_ID"
echo "  App launched: $BUNDLE_ID"

# 3.2 Wait for UI to settle
sleep 3

# 3.3 Screenshot: initial state
xcrun simctl io "$UDID" screenshot "$EVIDENCE_DIR/01-launch.png" 2>/dev/null
echo "  Screenshot: 01-launch.png"

# 3.4 Wait for the configured test duration
echo "  Waiting ${DURATION}s for test actions..."
sleep "$DURATION"

# 3.5 Screenshot: final state
xcrun simctl io "$UDID" screenshot "$EVIDENCE_DIR/02-final.png" 2>/dev/null
echo "  Screenshot: 02-final.png"

# ═══════════════════════════════════════════════
# Phase 4: COLLECT
# ═══════════════════════════════════════════════
echo ""
echo "── Phase 4: COLLECT ──"

# 4.1 Stop log streaming
if [ -n "$LOG_PID" ]; then
  kill "$LOG_PID" 2>/dev/null || true
  wait "$LOG_PID" 2>/dev/null || true
  LOG_PID=""
  echo "  Log stream: stopped"
fi

# 4.2 Capture historical logs
if [ "$SKIP_LOGS" != "1" ]; then
  xcrun simctl spawn "$UDID" log show \
    --predicate "subsystem == \"$LOG_SUBSYSTEM\"" \
    --last 120s \
    --info --debug \
    --style compact \
    > "$EVIDENCE_DIR/historical-logs.txt" 2>/dev/null
  echo "  Historical logs: captured (last 120s)"
fi

# 4.3 Stop video recording
if [ -n "$RECORD_PID" ]; then
  kill -SIGINT "$RECORD_PID" 2>/dev/null || true
  wait "$RECORD_PID" 2>/dev/null || true
  RECORD_PID=""
  echo "  Video: finalized"
fi

# 4.4 Check crash reports
RECENT_CRASHES=$(ls -t ~/Library/Logs/DiagnosticReports/*.ips 2>/dev/null | head -5)
if [ -n "$RECENT_CRASHES" ]; then
  echo "$RECENT_CRASHES" > "$EVIDENCE_DIR/crash-reports.txt"
  echo "  Crash reports: $(echo "$RECENT_CRASHES" | wc -l | tr -d ' ') found"
else
  echo "No recent crash reports" > "$EVIDENCE_DIR/crash-reports.txt"
  echo "  Crash reports: none"
fi

# 4.5 Restore status bar
if [ "$SKIP_STATUS_BAR" != "1" ]; then
  xcrun simctl status_bar "$UDID" clear 2>/dev/null || true
fi

# ═══════════════════════════════════════════════
# Phase 5: SUMMARY
# ═══════════════════════════════════════════════
echo ""
echo "── Phase 5: SUMMARY ──"

# Count log errors
LIVE_ERRORS=$(grep -ci "error" "$EVIDENCE_DIR/live-logs.txt" 2>/dev/null || echo "0")
HIST_ERRORS=$(grep -ci "error" "$EVIDENCE_DIR/historical-logs.txt" 2>/dev/null || echo "0")

# Build summary
cat > "$EVIDENCE_DIR/summary.txt" << SUMMARY
iOS Validation Evidence
=======================
Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
Simulator: $UDID
Bundle ID: $BUNDLE_ID
Duration:  ${DURATION}s

Files:
$(ls -la "$EVIDENCE_DIR/" 2>/dev/null)

Log Analysis:
  Live log errors:       $LIVE_ERRORS
  Historical log errors: $HIST_ERRORS

Crash Reports:
$(cat "$EVIDENCE_DIR/crash-reports.txt")

VERDICT: PENDING — Review screenshots, video, and logs before marking PASS/FAIL
SUMMARY

echo ""
echo "═══════════════════════════════════════════════"
echo "  Evidence collected: $EVIDENCE_DIR"
echo "═══════════════════════════════════════════════"
echo "  Files:"
ls -1 "$EVIDENCE_DIR/"
echo ""
echo "  Log errors (live):       $LIVE_ERRORS"
echo "  Log errors (historical): $HIST_ERRORS"
echo ""
echo "  NEXT: Read screenshots and video to verify behavior."
echo "  DO NOT mark PASS until you visually inspect all evidence."
echo "═══════════════════════════════════════════════"
