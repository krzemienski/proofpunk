> Incorporated from the `xc-mcp` skill (references/operation-enums.md).

# Operation Enum Reference

## Contents

- [simctl-device (7 operations)](#simctl-device-7-operations)
- [simctl-app (4 operations)](#simctl-app-4-operations)
- [idb-app (4 operations)](#idb-app-4-operations)
- [cache (4 operations)](#cache-4-operations)
- [persistence (3 operations)](#persistence-3-operations)
- [idb-targets (4 operations)](#idb-targets-4-operations)
- [Migration from V1.x](#migration-from-v1x)
- [Common Parameter Patterns](#common-parameter-patterns)


<overview>
XC-MCP V2.0+ consolidates related operations into router tools with operation enums. This reduces tool schema overhead while maintaining full functionality.

**Benefits:**
- Fewer tool registrations (21 → 6 routers)
- 40% token reduction in schemas
- Consistent parameter patterns
- Easier discovery and documentation
</overview>

<simctl_device>
## simctl-device (7 operations)

Unified device lifecycle management.

### boot
```typescript
simctl-device({
  operation: "boot",
  deviceId: "UDID"  // or "booted" for auto-select
})
// Boots simulator, tracks performance metrics
```

### shutdown
```typescript
simctl-device({
  operation: "shutdown",
  deviceId: "UDID"  // or "booted" or "all"
})
// Shuts down simulator(s)
```

### create
```typescript
simctl-device({
  operation: "create",
  name: "My Test iPhone",
  deviceType: "iPhone 15 Pro",
  runtime: "iOS 17.0"
})
// Creates new simulator
```

### delete
```typescript
simctl-device({
  operation: "delete",
  deviceId: "UDID"
})
// Permanently deletes simulator
```

### erase
```typescript
simctl-device({
  operation: "erase",
  deviceId: "UDID"
})
// Resets simulator to factory state
```

### clone
```typescript
simctl-device({
  operation: "clone",
  deviceId: "UDID",
  name: "Cloned Device"
})
// Creates copy of simulator
```

### rename
```typescript
simctl-device({
  operation: "rename",
  deviceId: "UDID",
  newName: "New Name"
})
// Renames simulator
```
</simctl_device>

<simctl_app>
## simctl-app (4 operations)

Unified app management.

### install
```typescript
simctl-app({
  operation: "install",
  appPath: "/path/to/App.app",
  deviceId: "booted"  // optional
})
```

### uninstall
```typescript
simctl-app({
  operation: "uninstall",
  bundleId: "com.example.App",
  deviceId: "booted"
})
```

### launch
```typescript
simctl-app({
  operation: "launch",
  bundleId: "com.example.App",
  deviceId: "booted",
  launchArguments: ["--debug"],
  environmentVariables: { "ENV": "dev" }
})
```

### terminate
```typescript
simctl-app({
  operation: "terminate",
  bundleId: "com.example.App",
  deviceId: "booted"
})
```
</simctl_app>

<idb_app>
## idb-app (4 operations)

IDB app management (supports physical devices).

### install
```typescript
idb-app({
  operation: "install",
  appPath: "/path/to/App.app",
  udid: "device-udid"  // optional
})
```

### uninstall
```typescript
idb-app({
  operation: "uninstall",
  bundleId: "com.example.App"
})
```

### launch
```typescript
idb-app({
  operation: "launch",
  bundleId: "com.example.App"
})
```

### terminate
```typescript
idb-app({
  operation: "terminate",
  bundleId: "com.example.App"
})
```
</idb_app>

<cache>
## cache (4 operations)

Cache management.

### get-stats
```typescript
cache({ operation: "get-stats" })
// Returns cache statistics for all layers
```

### get-config
```typescript
cache({
  operation: "get-config",
  cacheType: "simulator"  // or "project", "response", "all"
})
// Returns current configuration
```

### set-config
```typescript
cache({
  operation: "set-config",
  cacheType: "simulator",
  maxAgeHours: 2  // or maxAgeMinutes, maxAgeMs
})
// Updates cache timeout
```

### clear
```typescript
cache({
  operation: "clear",
  cacheType: "response"  // or "simulator", "project", "all"
})
// Clears cached data
```
</cache>

<persistence>
## persistence (3 operations)

Persistence control.

### enable
```typescript
persistence({
  operation: "enable",
  cacheDir: "~/.xc-mcp-cache"  // optional custom path
})
// Enables file-based persistence
```

### disable
```typescript
persistence({
  operation: "disable",
  clearData: true  // optional: also delete stored data
})
// Returns to in-memory only
```

### status
```typescript
persistence({
  operation: "status",
  includeStorageInfo: true
})
// Returns persistence state and storage info
```
</persistence>

<idb_targets>
## idb-targets (4 operations)

Target device management.

### list
```typescript
idb-targets({ operation: "list" })
// Lists all connected devices and simulators
```

### describe
```typescript
idb-targets({
  operation: "describe",
  udid: "device-udid"
})
// Gets detailed device info
```

### connect
```typescript
idb-targets({
  operation: "connect",
  udid: "device-udid"
})
// Connects to device
```

### disconnect
```typescript
idb-targets({
  operation: "disconnect",
  udid: "device-udid"
})
// Disconnects from device
```
</idb_targets>

<migration_from_v1>
## Migration from V1.x

| Old Tool (V1.x) | New Pattern (V2.0+) |
|-----------------|---------------------|
| `simctl-boot` | `simctl-device({ operation: "boot" })` |
| `simctl-shutdown` | `simctl-device({ operation: "shutdown" })` |
| `simctl-create` | `simctl-device({ operation: "create" })` |
| `simctl-delete` | `simctl-device({ operation: "delete" })` |
| `simctl-erase` | `simctl-device({ operation: "erase" })` |
| `simctl-clone` | `simctl-device({ operation: "clone" })` |
| `simctl-rename` | `simctl-device({ operation: "rename" })` |
| `simctl-install` | `simctl-app({ operation: "install" })` |
| `simctl-uninstall` | `simctl-app({ operation: "uninstall" })` |
| `simctl-launch` | `simctl-app({ operation: "launch" })` |
| `simctl-terminate` | `simctl-app({ operation: "terminate" })` |
| `cache-get-stats` | `cache({ operation: "get-stats" })` |
| `cache-get-config` | `cache({ operation: "get-config" })` |
| `cache-set-config` | `cache({ operation: "set-config" })` |
| `cache-clear` | `cache({ operation: "clear" })` |
| `persistence-enable` | `persistence({ operation: "enable" })` |
| `persistence-disable` | `persistence({ operation: "disable" })` |
| `persistence-status` | `persistence({ operation: "status" })` |
</migration_from_v1>

<parameter_patterns>
## Common Parameter Patterns

### Device Identification
- `deviceId`: For simctl operations (UDID, "booted", or "all")
- `udid`: For IDB operations

### App Identification
- `appPath`: Path to .app bundle (for install)
- `bundleId`: Reverse-domain identifier (for other operations)

### Optional Parameters
- Most `deviceId`/`udid` default to "booted" (auto-detect)
- Configuration has sensible defaults
- Use explicit values only when needed
</parameter_patterns>