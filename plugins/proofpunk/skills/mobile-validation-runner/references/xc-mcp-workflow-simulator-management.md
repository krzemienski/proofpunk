> Incorporated from the `xc-mcp` skill (workflows/simulator-management.md).

# Workflow: Simulator Management

<required_reading>
**Read these reference files NOW:**
1. references/tool-reference.md
2. references/operation-enums.md
</required_reading>

<process>
## Step 1: Discover Available Simulators

Use progressive disclosure to get simulator list:

```typescript
simctl-list({
  deviceType: "iPhone",           // optional filter
  availability: "available",      // default: available only
  concise: true                   // default: summary view
})
```

**Response contains:**
- `cacheId`: For accessing full device data
- `summary`: Total, available, booted counts
- `quickAccess`: Booted devices, recently used (prioritized)

## Step 2: Get Full Details (If Needed)

Only request full data when necessary:

```typescript
simctl-get-details({
  cacheId: "sim-abc123",
  detailType: "devices-only",     // or "runtimes-only", "full-list"
  deviceType: "iPhone",           // optional filter
  maxDevices: 10                  // limit results
})
```

## Step 3: Boot a Simulator

Use the `simctl-device` router with `boot` operation:

```typescript
// Boot specific device
simctl-device({
  operation: "boot",
  deviceId: "UDID-from-simctl-list"
})

// Or boot "booted" (auto-selects)
simctl-device({
  operation: "boot",
  deviceId: "booted"
})
```

**Response includes:**
- Boot time performance metrics
- Device state confirmation
- Usage recorded for smart recommendations

## Step 4: Shutdown Simulator

```typescript
// Shutdown specific device
simctl-device({
  operation: "shutdown",
  deviceId: "UDID"
})

// Shutdown all booted simulators
simctl-device({
  operation: "shutdown",
  deviceId: "all"
})
```

## Step 5: Create New Simulator

```typescript
simctl-device({
  operation: "create",
  name: "My Test iPhone",
  deviceType: "iPhone 15 Pro",
  runtime: "iOS 17.0"
})
```

## Step 6: Other Device Operations

```typescript
// Erase simulator (reset to clean state)
simctl-device({
  operation: "erase",
  deviceId: "UDID"
})

// Clone simulator
simctl-device({
  operation: "clone",
  deviceId: "UDID",
  name: "Cloned iPhone"
})

// Rename simulator
simctl-device({
  operation: "rename",
  deviceId: "UDID",
  newName: "New Name"
})

// Delete simulator
simctl-device({
  operation: "delete",
  deviceId: "UDID"
})
```
</process>

<health_check>
**Validate Xcode Environment:**

```typescript
simctl-health-check({})
```

**Checks:**
- Xcode installation and version
- simctl availability
- Available runtimes
- Booted simulators
- Disk space
</health_check>

<auto_detection>
**Smart Defaults:**

XC-MCP tracks simulator usage and recommends based on:
- Recently used simulators (appear first in quickAccess)
- Project-specific preferences
- Successful build history

**Never prompt users for UDIDs** - use `simctl-list` quick access or let tools auto-detect.
</auto_detection>

<common_patterns>
**Pattern 1: Quick Boot for Testing**
```typescript
// List available iPhones
simctl-list({ deviceType: "iPhone" })

// Boot first recommended (from quickAccess)
simctl-device({ operation: "boot", deviceId: "UDID-from-quickAccess" })
```

**Pattern 2: Fresh Testing Environment**
```typescript
// Erase to reset state
simctl-device({ operation: "erase", deviceId: "UDID" })

// Boot fresh
simctl-device({ operation: "boot", deviceId: "UDID" })
```

**Pattern 3: Create Specific Test Device**
```typescript
simctl-device({
  operation: "create",
  name: "iOS 17 Test Device",
  deviceType: "iPhone 15",
  runtime: "iOS 17.4"
})
```
</common_patterns>

<success_criteria>
Simulator management complete when:
- [ ] Simulator list accessed via progressive disclosure (not full dump)
- [ ] Quick access recommendations leveraged
- [ ] Device operations use simctl-device router with operation enum
- [ ] No manual UDID prompts to users
- [ ] Health check run if environment issues suspected
</success_criteria>
