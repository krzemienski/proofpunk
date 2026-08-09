#!/bin/bash

# xc-mcp MCP Tool Wrapper for Claude Skills
# Provides helper functions to call xc-mcp tools from skill scripts
#
# NOTE: When skills are executed by Claude Code, Claude can make MCP calls
# This wrapper provides a clean interface for skills to request MCP operations

XC_MCP_SERVER="xc-mcp"
XC_MCP_CACHE="/tmp/xc-mcp-cache"

mkdir -p "$XC_MCP_CACHE"

# Helper: Call xc-mcp tool via Claude Code MCP system
# When Claude executes this skill, it can intercept these calls and make actual MCP requests
xc_mcp_call() {
  local tool_name="$1"
  local args_json="$2"
  local output_file="${3:-/tmp/xc-mcp-result-$$.json}"

  echo "📡 [xc-mcp] Calling tool: $tool_name" >&2

  # Create MCP call request file
  # Claude Code can monitor for these and execute the MCP calls
  cat > "$output_file" <<EOF
{
  "server": "$XC_MCP_SERVER",
  "tool": "$tool_name",
  "arguments": $args_json,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "requestId": "$$-$(date +%s)"
}
EOF

  # Output the request (Claude can intercept and execute)
  cat "$output_file"

  # Return output file path for caller
  echo "$output_file" >&2
}

# Helper: List simulators with device type filter
xc_list_simulators() {
  local device_type="${1:-iPhone}"

  xc_mcp_call "simctl-list" "{\"deviceType\": \"$device_type\"}"
}

# Helper: Get simulator details from cache
xc_get_simulator_details() {
  local cache_id="$1"
  local detail_type="${2:-available-only}"

  xc_mcp_call "simctl-get-details" "{
    \"cacheId\": \"$cache_id\",
    \"detailType\": \"$detail_type\"
  }"
}

# Helper: Boot simulator by name (auto-UDID detection)
xc_boot_simulator() {
  local device_name="$1"

  xc_mcp_call "simctl-boot" "{\"deviceName\": \"$device_name\"}"
}

# Helper: Boot simulator by UDID
xc_boot_simulator_udid() {
  local udid="$1"

  xc_mcp_call "simctl-boot" "{\"udid\": \"$udid\"}"
}

# Helper: Shutdown simulator
xc_shutdown_simulator() {
  local device_name_or_udid="$1"

  if [[ "$device_name_or_udid" =~ ^[A-F0-9-]+$ ]]; then
    # UDID provided
    xc_mcp_call "simctl-shutdown" "{\"udid\": \"$device_name_or_udid\"}"
  else
    # Device name provided
    xc_mcp_call "simctl-shutdown" "{\"deviceName\": \"$device_name_or_udid\"}"
  fi
}

# Helper: Get smart simulator suggestion
xc_suggest_simulator() {
  local project_path="$1"
  local purpose="${2:-testing}"

  xc_mcp_call "simctl-suggest" "{
    \"projectPath\": \"$project_path\",
    \"purpose\": \"$purpose\",
    \"scoreFactors\": [\"recent\", \"performance\", \"available\"]
  }"
}

# Helper: Take screenshot (vision-optimized base64)
xc_screenshot() {
  local app_name="$1"
  local screen_name="$2"
  local state="${3:-Default}"
  local udid="${4:-auto}"

  xc_mcp_call "simctl-screenshot-inline" "{
    \"udid\": \"$udid\",
    \"appName\": \"$app_name\",
    \"screenName\": \"$screen_name\",
    \"state\": \"$state\"
  }"
}

# Helper: Save screenshot to file
xc_screenshot_file() {
  local output_path="$1"
  local app_name="$2"
  local screen_name="$3"
  local state="${4:-Default}"
  local udid="${5:-auto}"

  xc_mcp_call "simctl-io" "{
    \"udid\": \"$udid\",
    \"operation\": \"screenshot\",
    \"outputPath\": \"$output_path\",
    \"appName\": \"$app_name\",
    \"screenName\": \"$screen_name\",
    \"state\": \"$state\"
  }"
}

# Helper: Query UI elements
xc_query_ui() {
  local bundle_id="$1"
  local predicate="$2"
  local udid="${3:-auto}"

  xc_mcp_call "simctl-query-ui" "{
    \"udid\": \"$udid\",
    \"bundleId\": \"$bundle_id\",
    \"predicate\": \"$predicate\"
  }"
}

# Helper: Tap element at coordinates
xc_tap() {
  local x="$1"
  local y="$2"
  local action_name="$3"
  local udid="${4:-auto}"

  xc_mcp_call "simctl-tap" "{
    \"udid\": \"$udid\",
    \"x\": $x,
    \"y\": $y,
    \"actionName\": \"$action_name\"
  }"
}

# Helper: Type text
xc_type_text() {
  local text="$1"
  local action_name="$2"
  local is_sensitive="${3:-false}"
  local udid="${4:-auto}"

  xc_mcp_call "simctl-type-text" "{
    \"udid\": \"$udid\",
    \"text\": \"$text\",
    \"actionName\": \"$action_name\",
    \"isSensitive\": $is_sensitive
  }"
}

# Helper: Install app to simulator
xc_install_app() {
  local app_path="$1"
  local udid="${2:-auto}"

  xc_mcp_call "simctl-install" "{
    \"udid\": \"$udid\",
    \"appPath\": \"$app_path\"
  }"
}

# Helper: Launch app
xc_launch_app() {
  local bundle_id="$1"
  local udid="${2:-auto}"

  xc_mcp_call "simctl-launch" "{
    \"udid\": \"$udid\",
    \"bundleId\": \"$bundle_id\"
  }"
}

# Helper: Build Xcode project with progressive disclosure
xc_build() {
  local project_path="$1"
  local scheme="$2"
  local configuration="${3:-Debug}"
  local auto_install="${4:-false}"

  xc_mcp_call "xcodebuild-build" "{
    \"projectPath\": \"$project_path\",
    \"scheme\": \"$scheme\",
    \"configuration\": \"$configuration\",
    \"autoInstall\": $auto_install
  }"
}

# Helper: Get build details (for failures)
xc_get_build_details() {
  local build_id="$1"

  xc_mcp_call "xcodebuild-get-details" "{\"buildId\": \"$build_id\"}"
}

# Helper: Health check
xc_health_check() {
  xc_mcp_call "simctl-health-check" "{}"
}

# Helper: Get Xcode version
xc_version() {
  xc_mcp_call "xcodebuild-version" "{}"
}

# Helper: Complete workflow (build + run + screenshot)
xc_workflow_build_and_run() {
  local project_path="$1"
  local scheme="$2"
  local app_name="$3"

  xc_mcp_call "workflow-build-and-run" "{
    \"projectPath\": \"$project_path\",
    \"scheme\": \"$scheme\",
    \"appName\": \"$app_name\"
  }"
}

# Export all functions for use in other scripts
export -f xc_mcp_call
export -f xc_list_simulators
export -f xc_get_simulator_details
export -f xc_boot_simulator
export -f xc_boot_simulator_udid
export -f xc_shutdown_simulator
export -f xc_suggest_simulator
export -f xc_screenshot
export -f xc_screenshot_file
export -f xc_query_ui
export -f xc_tap
export -f xc_type_text
export -f xc_install_app
export -f xc_launch_app
export -f xc_build
export -f xc_get_build_details
export -f xc_health_check
export -f xc_version
export -f xc_workflow_build_and_run

echo "✅ xc-mcp wrapper loaded (18 helper functions available)" >&2
