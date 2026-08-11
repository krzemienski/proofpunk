> Incorporated from the `xc-mcp` skill (workflows/ui-automation.md).

# Workflow: UI Automation (Accessibility-First)

## Contents

- [Step 1: Assess Accessibility Quality](#step-1-assess-accessibility-quality)
- [Step 2: Branch Based on Quality](#step-2-branch-based-on-quality)
- [Step 3: Text Input](#step-3-text-input)
- [Step 4: Gestures (Swipe, Pinch, Scroll)](#step-4-gestures-swipe-pinch-scroll)
- [Step 5: Verify Result (Optional)](#step-5-verify-result-optional)


<required_reading>
**Read these reference files NOW:**
1. references/accessibility-patterns.md
2. references/tool-reference.md
</required_reading>

<critical_principle>
**ALWAYS use accessibility-first automation.**

Screenshots are expensive (170 tokens, 2000ms) and should be a LAST RESORT.
Accessibility queries are cheap (50 tokens, 120ms) and should be FIRST CHOICE.

This promotes inclusive app development while being 3-4x cheaper and 16x faster.
</critical_principle>

<process>
## Step 1: Assess Accessibility Quality

**ALWAYS start here** before any UI interaction:

```typescript
accessibility-quality-check({ screenContext: "LoginScreen" })
```

**Response indicates:**
- `quality`: "rich" | "moderate" | "minimal"
- `recommendation`: "accessibility-ready" | "consider-screenshot"
- `elementCounts`: { total: 12, tappable: 8, textFields: 2 }

## Step 2: Branch Based on Quality

### IF quality is "rich" or "moderate" → Use Accessibility Path

```typescript
// Find element by semantic query
idb-ui-find-element({ query: "Login" })
// Returns: { centerX: 200, centerY: 400, label: "Login", type: "Button" }

// Tap at returned coordinates
idb-ui-tap({ x: 200, y: 400 })
```

### IF quality is "minimal" → Fall Back to Screenshot

```typescript
// Only when accessibility insufficient
screenshot({ 
  screenName: "LoginScreen", 
  state: "Initial",
  size: "half"  // Optimized for token efficiency
})
```

## Step 3: Text Input

After tapping a text field:

```typescript
idb-ui-input({ 
  operation: "text", 
  text: "user@example.com" 
})
```

**Input operations:**
- `text`: Type text string
- `key`: Send specific key (e.g., "return", "delete")
- `clear`: Clear current input

## Step 4: Gestures (Swipe, Pinch, Scroll)

```typescript
// Swipe gesture
idb-ui-gesture({
  operation: "swipe",
  direction: "up",  // up, down, left, right
  // Or use explicit coordinates:
  // startX: 200, startY: 600, endX: 200, endY: 200
})

// Pinch gesture
idb-ui-gesture({
  operation: "pinch",
  scale: 0.5  // <1 pinch in, >1 pinch out
})
```

## Step 5: Verify Result (Optional)

Take verification screenshot only at workflow end:

```typescript
screenshot({ 
  screenName: "HomeScreen", 
  state: "LoggedIn" 
})
```
</process>

<high_level_workflow_tool>
**Use `workflow-tap-element` for common patterns:**

Combines accessibility check + find + tap + optional input + optional verify:

```typescript
workflow-tap-element({
  elementQuery: "Login",
  screenContext: "LoginScreen",
  inputText: "user@example.com",  // optional: type after tap
  verifyResult: true               // optional: screenshot after action
})
// Cost: ~90 tokens (vs 130 tokens separately)
// Latency: ~300ms (vs ~400ms separately)
```
</high_level_workflow_tool>

<optimal_login_flow>
**Example: Complete Login Automation**

```typescript
// 1. Quality check (30 tokens, 80ms)
accessibility-quality-check({ screenContext: "LoginScreen" })

// 2. Find and tap email field (40 tokens, 120ms)
idb-ui-find-element({ query: "email" })
idb-ui-tap({ x: 200, y: 150 })

// 3. Enter email
idb-ui-input({ operation: "text", text: "user@example.com" })

// 4. Find and tap password field
idb-ui-find-element({ query: "password" })
idb-ui-tap({ x: 200, y: 250 })

// 5. Enter password
idb-ui-input({ operation: "text", text: "secretpassword" })

// 6. Find and tap login button
idb-ui-find-element({ query: "login" })
idb-ui-tap({ x: 200, y: 400 })

// 7. Verify with screenshot only at end (170 tokens, 2000ms)
screenshot({ screenName: "HomeScreen", state: "LoggedIn" })

// Total: ~280 tokens, ~2400ms
// vs Screenshot-first: ~510 tokens, ~6000ms
```
</optimal_login_flow>

<element_queries>
**Effective Element Queries:**

```typescript
// By visible label
idb-ui-find-element({ query: "Submit" })
idb-ui-find-element({ query: "Cancel" })

// By placeholder text
idb-ui-find-element({ query: "Enter your email" })

// By accessibility identifier (if set by developer)
idb-ui-find-element({ query: "loginButton" })

// Partial matching works
idb-ui-find-element({ query: "Log" })  // Matches "Login", "Logout"
```
</element_queries>

<accessibility_tree_inspection>
**For Complex UIs - Inspect Full Tree:**

```typescript
// Get accessibility tree summary
idb-ui-describe({ operation: "all" })
// Returns: Summary + uiTreeId for full data

// Get full tree if needed
idb-ui-describe({ 
  operation: "all",
  // Use uiTreeId from previous call for full tree
})

// Query specific point
idb-ui-describe({ 
  operation: "point", 
  x: 200, 
  y: 400 
})
```
</accessibility_tree_inspection>

<success_criteria>
UI automation workflow complete when:
- [ ] Accessibility quality checked FIRST (before any screenshots)
- [ ] Semantic element search used when quality is rich/moderate
- [ ] Screenshots used only as fallback for minimal accessibility
- [ ] Text input handled via idb-ui-input
- [ ] Gestures use correct operation and direction parameters
- [ ] Verification screenshot taken only at end (if needed)
- [ ] Total token cost significantly lower than screenshot-first approach
</success_criteria>