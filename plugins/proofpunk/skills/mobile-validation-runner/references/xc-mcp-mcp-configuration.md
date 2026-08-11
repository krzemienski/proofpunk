> Incorporated from the `xc-mcp` skill (references/mcp-configuration.md).

# XC-MCP Configuration Reference

## Contents

- [Installation](#installation)
- [MCP Client Configuration](#mcp-client-configuration)
- [Environment Variables](#environment-variables)
- [Prerequisites](#prerequisites)
- [Working Directory](#working-directory)
- [Troubleshooting](#troubleshooting)
- [CLAUDE.md Template](#claudemd-template)
- [Version Compatibility](#version-compatibility)


<installation>
## Installation

```bash
# Global install (recommended for MCP)
npm install -g xc-mcp

# Or run directly without installation
npx xc-mcp

# Or run specific version
npx xc-mcp@3.2.0
```
</installation>

<mcp_configuration>
## MCP Client Configuration

### Claude Desktop
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Standard Configuration:**
```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp"],
      "cwd": "/path/to/your/ios/project"
    }
  }
}
```

**Minimal Mode** (for clients without defer_loading):
```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp", "--mini"]
    }
  }
}
```
Token reduction: ~18.7k → ~540 tokens (97% reduction)

**Build-Only Mode** (11 tools, no UI automation):
```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp", "--build-only"]
    }
  }
}
```
Loads only: xcodebuild tools, simctl-list, cache, system tools

**Combined Minimal + Build-Only:**
```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp", "--mini", "--build-only"]
    }
  }
}
```

### Claude Code
Add to `.mcp.json` in project root:

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp", "--mini"]
    }
  }
}
```

Note: Claude Code may not support defer_loading, so `--mini` is recommended.
</mcp_configuration>

<environment_variables>
## Environment Variables

### XCODE_CLI_MCP_TIMEOUT
Operation timeout in seconds.
```bash
export XCODE_CLI_MCP_TIMEOUT=600  # 10 minutes (default: 300)
```

### XCODE_CLI_MCP_LOG_LEVEL
Logging verbosity.
```bash
export XCODE_CLI_MCP_LOG_LEVEL=debug  # debug | info | warn | error
```

### XCODE_CLI_MCP_CACHE_DIR
Custom cache directory path.
```bash
export XCODE_CLI_MCP_CACHE_DIR=~/.my-xc-mcp-cache
```

### XC_MCP_DEFER_LOADING
Enable/disable deferred tool loading.
```bash
export XC_MCP_DEFER_LOADING=false  # Load all tools at startup (default: true)
```
</environment_variables>

<prerequisites>
## Prerequisites

### Required
- macOS (Xcode CLI tools require macOS)
- Xcode Command Line Tools installed
- Node.js 18+

### Recommended
- Xcode 15+
- iOS Simulators installed
- IDB (for physical device support)

### Verify Installation
```bash
# Check Xcode CLI tools
xcode-select --version

# Check simctl
xcrun simctl --version

# Check Node.js
node --version
```

### Install Xcode CLI Tools
```bash
xcode-select --install
```
</prerequisites>

<working_directory>
## Working Directory

The `cwd` parameter in configuration determines the working directory for relative paths.

**Best Practice:** Set `cwd` to your iOS project root.

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp"],
      "cwd": "/Users/you/Projects/MyiOSApp"
    }
  }
}
```

This allows using relative paths:
```typescript
xcodebuild-build({
  projectPath: "./MyApp.xcworkspace",  // Relative to cwd
  scheme: "MyApp"
})
```
</working_directory>

<troubleshooting>
## Troubleshooting

### Server Won't Start
1. Check Node.js version: `node --version` (need 18+)
2. Check Xcode installation: `xcode-select --version`
3. Try direct run: `npx xc-mcp` to see error messages

### Tools Not Found
1. Verify MCP client connected to server
2. Check for typos in tool names
3. Try `rtfm({})` to list all tools

### Build Failures
1. Check project path exists
2. Verify scheme name with `xcodebuild-list`
3. Use `simctl-health-check` to validate environment

### Simulator Issues
1. Run `simctl-health-check` to diagnose
2. Check simulator is booted: `simctl-list`
3. Try erasing simulator: `simctl-device({ operation: "erase" })`
</troubleshooting>

<claude_md_template>
## CLAUDE.md Template

Add this to your iOS project for optimal XC-MCP usage:

```markdown
# XC-MCP Optimal Usage Patterns

This project uses XC-MCP for iOS development automation.

## Tool Discovery
1. Browse categories: `rtfm({ categoryName: "build" })`
2. Get tool docs: `rtfm({ toolName: "xcodebuild-build" })`
3. Execute: Use discovered parameters

## Accessibility-First Automation (MANDATORY)
ALWAYS assess quality before screenshots:

1. Check quality: `accessibility-quality-check({ screenContext: "LoginScreen" })`
2. Decision branch:
   - IF rich/moderate: Use `idb-ui-find-element` + `idb-ui-tap`
   - IF minimal: Fall back to `screenshot`

## Progressive Disclosure
- Build/test tools return buildId/testId
- Use `xcodebuild-get-details` to drill down
- Never request full logs upfront

## Best Practices
- Let UDID auto-detect
- Use semantic context (screenContext, appName)
- Use operation enums: `simctl-device({ operation: "boot" })`
```
</claude_md_template>

<version_compatibility>
## Version Compatibility

| XC-MCP Version | Features |
|----------------|----------|
| V3.0.0+ | Deferred loading, workflow tools |
| V2.0.0+ | Operation enums, accessibility-first |
| V1.3.0+ | RTFM documentation system |
| V1.0.0+ | Core functionality |

**Current Stable:** V3.2.0
</version_compatibility>