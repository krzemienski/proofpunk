> Incorporated from the `xc-mcp` skill (skills-ref.zip).


## Contents

- [APPLICABILITY GUARD](#applicability-guard)
- [Anti-Patterns](#anti-patterns)
- [When NOT to Use](#when-not-to-use)

<essential_principles>
This skill provides expertise for iOS development automation via the XC-MCP Model Context Protocol server. XC-MCP wraps `xcodebuild`, `simctl`, and `idb` commands with intelligent caching and progressive disclosure.

<accessibility_first_mandate>
ALWAYS use accessibility-first automation before screenshots.

1. **Check quality first**: `accessibility-quality-check({ screenContext: "ScreenName" })`
2. **Decision branch**:
   - IF `rich` or `moderate`: Use `idb-ui-find-element` + `idb-ui-tap`
   - IF `minimal`: Fall back to `screenshot` as last resort
3. **Performance comparison**:
   - Accessibility: ~50 tokens, ~120ms
   - Screenshots: ~170 tokens, ~2000ms
   - **3-4x cheaper, 16x faster when accessibility sufficient**
</accessibility_first_mandate>

<progressive_disclosure_pattern>
NEVER request full logs upfront. Use progressive disclosure:

1. **Build operations** return `buildId` → use `xcodebuild-get-details` for full logs
2. **Simulator lists** return `cacheId` → use `simctl-get-details` for full data
3. **Test operations** return `testId` → use `xcodebuild-get-details` for results
4. **Large outputs** cached automatically → retrieve via cache IDs when needed
</progressive_disclosure_pattern>

<auto_udid_detection>
NEVER prompt users for simulator UDIDs. XC-MCP auto-detects:

- Tools auto-detect booted simulators
- Use `simctl-list` for discovery when needed
- Pass `udid: "booted"` for currently running simulator
- Smart defaults based on project usage history
</auto_udid_detection>

<tool_discovery_pattern>
Use RTFM for tool documentation discovery:

1. **Browse categories**: `rtfm({ categoryName: "build" })`
2. **Get tool docs**: `rtfm({ toolName: "xcodebuild-build" })`
3. **Execute**: Use discovered parameters with operation enums
</tool_discovery_pattern>

<operation_enum_pattern>
Use consolidated routers with operation enums:

```typescript
// Device lifecycle
simctl-device({ operation: "boot" | "shutdown" | "create" | "delete" | "erase" | "clone" | "rename" })

// App management  
simctl-app({ operation: "install" | "uninstall" | "launch" | "terminate" })

// IDB operations
idb-app({ operation: "install" | "uninstall" | "launch" | "terminate" })

// Cache management
cache({ operation: "get-stats" | "get-config" | "set-config" | "clear" })

// Persistence
persistence({ operation: "enable" | "disable" | "status" })
```
</operation_enum_pattern>

<semantic_context>
ALWAYS include semantic context parameters:

- `screenContext`: Current screen name (e.g., "LoginScreen")
- `appName`: Application name for file naming
- `screenName`: Screen identifier for tracking
- `state`: UI state description (e.g., "Empty", "LoggedIn")
</semantic_context>
</essential_principles>

<mcp_server_requirement>
This skill requires the XC-MCP MCP server. Configuration:

```json
{
  "mcpServers": {
    "xc-mcp": {
      "command": "npx",
      "args": ["-y", "xc-mcp"],
      "cwd": "/path/to/ios/project"
    }
  }
}
```

**Minimal mode** (for clients without defer_loading):
```json
{
  "args": ["-y", "xc-mcp", "--mini"]
}
```

**Build-only mode** (11 tools, no UI automation):
```json
{
  "args": ["-y", "xc-mcp", "--build-only"]
}
```
</mcp_server_requirement>

<intake>
What iOS development task do you need help with?

1. Build and compile an Xcode project
2. Run tests on iOS simulator
3. Automate UI interactions (tap, swipe, input)
4. Manage iOS simulators (boot, create, configure)
5. Install and launch apps on simulator
6. Fresh install workflow (clean state testing)
7. Debug build or test failures
8. Configure XC-MCP caching and persistence

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
|----------|----------|
| 1, "build", "compile", "xcodebuild" | `workflows/build-project.md` |
| 2, "test", "xctest", "unit test" | `workflows/run-tests.md` |
| 3, "tap", "swipe", "ui", "automation", "interact" | `workflows/ui-automation.md` |
| 4, "simulator", "boot", "create", "manage" | `workflows/simulator-management.md` |
| 5, "install", "launch", "app", "deploy" | `workflows/app-deployment.md` |
| 6, "fresh", "clean", "reset", "workflow" | `workflows/fresh-install.md` |
| 7, "debug", "error", "failure", "logs" | `workflows/debug-failures.md` |
| 8, "cache", "config", "persistence" | `workflows/configure-caching.md` |

**Intent-based routing (clear context without selection):**
- "build my app" → `workflows/build-project.md`
- "test the login flow" → `workflows/ui-automation.md`
- "run my unit tests" → `workflows/run-tests.md`
- "boot the simulator" → `workflows/simulator-management.md`
- "install and launch" → `workflows/app-deployment.md`
- "start fresh" → `workflows/fresh-install.md`
- "why did the build fail" → `workflows/debug-failures.md`

**After reading the workflow, follow it exactly.**
</routing>

<tool_categories>
**Build & Test (6 tools)**
- `xcodebuild-build`: Build with progressive disclosure via buildId
- `xcodebuild-test`: Test with filtering, test plans, cache IDs
- `xcodebuild-clean`: Clean build artifacts
- `xcodebuild-list`: List targets/schemes with smart caching
- `xcodebuild-version`: Get Xcode and SDK versions
- `xcodebuild-get-details`: Access cached build/test logs

**Simulator Management (6 routers/tools)**
- `simctl-device`: 7 operations (boot, shutdown, create, delete, erase, clone, rename)
- `simctl-app`: 4 operations (install, uninstall, launch, terminate)
- `simctl-list`: Progressive disclosure simulator listing
- `simctl-get-details`: On-demand full simulator data
- `simctl-health-check`: Xcode environment validation
- `simctl-io`: Screenshots and video recording

**UI Automation (6 tools)**
- `accessibility-quality-check`: Rapid UI richness assessment
- `idb-ui-find-element`: Semantic element search
- `idb-ui-tap`: Coordinate-based tapping
- `idb-ui-input`: Text input with keyboard control
- `idb-ui-gesture`: Swipes, pinches, rotations
- `idb-ui-describe`: Accessibility tree queries

**Workflow Tools (2 high-level)**
- `workflow-tap-element`: High-level semantic tap (find + tap)
- `workflow-fresh-install`: Clean install workflow

**Documentation**
- `rtfm`: On-demand comprehensive documentation
</tool_categories>

<reference_index>
All domain knowledge in `references/` (bundled here as `xc-mcp-*.md`):

**Tools:** tool-reference.md, operation-enums.md
**Patterns:** accessibility-patterns.md, progressive-disclosure.md
**Workflows:** optimal-login-flow.md, testing-patterns.md
**Configuration:** mcp-configuration.md, caching-strategy.md
</reference_index>

<workflows_index>
| Workflow | Purpose |
|----------|---------|
| build-project.md | Build Xcode projects with intelligent defaults |
| run-tests.md | Execute unit and UI tests |
| ui-automation.md | Automate UI interactions accessibility-first |
| simulator-management.md | Boot, create, and configure simulators |
| app-deployment.md | Install and launch apps on simulators |
| fresh-install.md | Clean state testing workflow |
| debug-failures.md | Diagnose build and test failures |
| configure-caching.md | Optimize XC-MCP caching and persistence |
</workflows_index>

<quick_reference>
**Most Common Operations:**

```typescript
// Build project
xcodebuild-build({ projectPath: "./App.xcworkspace", scheme: "App" })

// Boot simulator (auto-selects best match)
simctl-device({ operation: "boot" })

// Install and launch
simctl-app({ operation: "install", appPath: "/path/to/App.app" })
simctl-app({ operation: "launch", bundleId: "com.example.App" })

// Accessibility-first UI tap
accessibility-quality-check({ screenContext: "LoginScreen" })
idb-ui-find-element({ query: "Login" })
idb-ui-tap({ x: 200, y: 400 })

// High-level workflow
workflow-tap-element({ elementQuery: "Login", inputText: "user@example.com" })

// Fresh install
workflow-fresh-install({ projectPath: "./App.xcworkspace", scheme: "App", eraseSimulator: true })
```
</quick_reference>

## APPLICABILITY GUARD

This skill is iOS/macOS-specific and requires the XC-MCP MCP server. Only activate for Xcode projects, iOS/macOS simulator automation, or UI testing via `idb`. Does not cover Android, React Native, Flutter, or web automation.

<success_criteria>
A well-executed XC-MCP workflow:
- Uses accessibility-first automation (checks quality before screenshots)
- Leverages progressive disclosure (summaries first, details on demand)
- Never prompts for simulator UDIDs (auto-detection)
- Uses operation enums for consolidated routers
- Includes semantic context (screenContext, appName, state)
- Handles errors with guidance from tool responses
</success_criteria>

## Anti-Patterns

| Pattern | Why It's Wrong | Do This Instead |
|---------|---------------|-----------------|
| Taking screenshots before checking accessibility quality | Screenshots cost 3-4x more tokens and 16x more time than accessibility queries | Always run `accessibility-quality-check` first; only fall back to screenshots if quality is `minimal` |
| Requesting full build logs upfront | Full logs consume massive context for information you may not need | Use progressive disclosure: get `buildId` first, then `xcodebuild-get-details` only when needed |
| Prompting user for simulator UDID | Users rarely know their UDID; interrupts workflow unnecessarily | Let XC-MCP auto-detect booted simulators or use `simctl-list` for discovery |
| Calling individual simctl commands instead of operation routers | Bypasses XC-MCP's caching, error handling, and progressive disclosure | Use consolidated routers: `simctl-device`, `simctl-app`, `idb-app` with operation enums |
| Omitting `screenContext` and semantic parameters | Loses tracking context, makes debugging harder, reduces cache effectiveness | Always include `screenContext`, `appName`, `screenName`, `state` parameters |

## When NOT to Use

- Android, React Native, or Flutter projects (iOS/macOS only)
- Web browser automation (use `agent-browser` or `chrome-devtools`)
- Projects without an `.xcodeproj` or `.xcworkspace`
- When XC-MCP MCP server is not configured in the client