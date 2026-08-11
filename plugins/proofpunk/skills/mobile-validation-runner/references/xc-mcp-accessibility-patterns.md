> Incorporated from the `xc-mcp` skill (references/accessibility-patterns.md).

# Accessibility-First Automation Patterns

<philosophy>
XC-MCP promotes **accessibility-first** automation because:

1. **Encourages inclusive apps**: Building accessible UIs benefits all users (screen readers, voice control, assistive technologies)
2. **Enables precise AI interaction**: Semantic element discovery via accessibility tree vs visual guesswork
3. **Improves efficiency**: 3-4x cheaper token cost, 16x faster execution
4. **Reduces energy usage**: Skip computationally expensive image processing
</philosophy>

<mandatory_workflow>
## The Accessibility-First Workflow

**ALWAYS follow this pattern:**

```typescript
// Step 1: ASSESS (mandatory first step)
accessibility-quality-check({ screenContext: "ScreenName" })

// Step 2: BRANCH based on quality result
if (quality === "rich" || quality === "moderate") {
  // USE ACCESSIBILITY (preferred path)
  idb-ui-find-element({ query: "ElementLabel" })
  idb-ui-tap({ x: centerX, y: centerY })
} else {
  // FALLBACK TO SCREENSHOT (last resort)
  screenshot({ screenName: "ScreenName" })
}
```
</mandatory_workflow>

<quality_levels>
## Quality Level Interpretation

### Rich (>3 tappable elements)
- Full accessibility tree available
- Use `idb-ui-find-element` confidently
- Semantic queries will work reliably
- **Recommendation:** Always use accessibility

### Moderate (2-3 tappable elements)
- Partial accessibility tree
- Basic element discovery works
- May need more specific queries
- **Recommendation:** Try accessibility first, screenshot if needed

### Minimal (≤1 tappable element)
- Very limited accessibility data
- App may not implement accessibility
- Custom UI elements likely
- **Recommendation:** Fall back to screenshot
</quality_levels>

<performance_comparison>
## Performance Data

| Approach | Tokens | Latency | Energy |
|----------|--------|---------|--------|
| **Accessibility** | ~50 | ~120ms | Low |
| **Screenshot** | ~170 | ~2000ms | High |
| **Savings** | **3.4x** | **16x** | **Significant** |

**Why screenshots are expensive:**
- Image encoding (base64)
- Network transfer
- Vision model processing
- Higher token count

**Why accessibility is cheap:**
- Text-based data
- Minimal encoding
- Direct coordinate retrieval
- Lower token count
</performance_comparison>

<element_search_patterns>
## Effective Element Queries

### By Visible Text
```typescript
// Button labels
idb-ui-find-element({ query: "Submit" })
idb-ui-find-element({ query: "Cancel" })
idb-ui-find-element({ query: "Log In" })

// Tab labels
idb-ui-find-element({ query: "Home" })
idb-ui-find-element({ query: "Settings" })
```

### By Placeholder Text
```typescript
idb-ui-find-element({ query: "Enter your email" })
idb-ui-find-element({ query: "Search" })
idb-ui-find-element({ query: "Password" })
```

### By Accessibility Identifier
```typescript
// Developers set these programmatically
idb-ui-find-element({ query: "loginButton" })
idb-ui-find-element({ query: "emailTextField" })
idb-ui-find-element({ query: "profileImage" })
```

### Partial Matching
```typescript
// "Log" matches "Login", "Logout", "Log In"
idb-ui-find-element({ query: "Log" })

// Case insensitive
idb-ui-find-element({ query: "submit" })  // Matches "Submit"
```
</element_search_patterns>

<complete_login_example>
## Example: Complete Login Flow

```typescript
// 1. Quality check (30 tokens, 80ms)
accessibility-quality-check({ screenContext: "LoginScreen" })
// Result: { quality: "rich", tappableElements: 12, textFields: 2 }

// 2. Find email field (40 tokens, 120ms)
idb-ui-find-element({ query: "email" })
// Result: { centerX: 200, centerY: 150, label: "Email", type: "TextField" }

// 3. Tap email field
idb-ui-tap({ x: 200, y: 150 })

// 4. Enter email
idb-ui-input({ operation: "text", text: "user@example.com" })

// 5. Find password field
idb-ui-find-element({ query: "password" })

// 6. Tap password field
idb-ui-tap({ x: 200, y: 250 })

// 7. Enter password
idb-ui-input({ operation: "text", text: "secretpassword" })

// 8. Find login button
idb-ui-find-element({ query: "login" })

// 9. Tap login button
idb-ui-tap({ x: 200, y: 400 })

// 10. Verify result (screenshot ONLY at end)
screenshot({ screenName: "HomeScreen", state: "LoggedIn" })

// Total: ~280 tokens, ~2400ms
// Screenshot-first would be: ~510 tokens, ~6000ms
```
</complete_login_example>

<high_level_workflow>
## Using workflow-tap-element

For common tap patterns, use the high-level workflow tool:

```typescript
// Single call replaces: quality-check + find + tap
workflow-tap-element({
  elementQuery: "Login",
  screenContext: "LoginScreen"
})

// With text input
workflow-tap-element({
  elementQuery: "email",
  screenContext: "LoginScreen",
  inputText: "user@example.com"
})

// With verification
workflow-tap-element({
  elementQuery: "Submit",
  screenContext: "CheckoutScreen",
  verifyResult: true  // Takes screenshot after
})
```

**Benefits:**
- Single tool call vs 3-4 separate calls
- ~90 tokens vs ~130 tokens
- ~300ms vs ~400ms
</high_level_workflow>

<tree_inspection>
## Inspecting the Accessibility Tree

When element queries aren't working:

```typescript
// Get full accessibility tree
idb-ui-describe({ operation: "all" })
// Returns: Summary of all elements + uiTreeId

// Query specific point
idb-ui-describe({ 
  operation: "point", 
  x: 200, 
  y: 400 
})
// Returns: Element at those coordinates
```

**Use tree inspection when:**
- Element queries return nothing
- Need to discover available elements
- Debugging accessibility implementation
- Understanding UI structure
</tree_inspection>

<gestures>
## Accessibility-Compatible Gestures

```typescript
// Swipe (direction-based)
idb-ui-gesture({
  operation: "swipe",
  direction: "up"  // up, down, left, right
})

// Swipe (coordinate-based, more precise)
idb-ui-gesture({
  operation: "swipe",
  startX: 200, startY: 600,
  endX: 200, endY: 200
})

// Pinch
idb-ui-gesture({
  operation: "pinch",
  scale: 0.5  // <1 pinch in, >1 pinch out
})
```
</gestures>

<troubleshooting>
## Troubleshooting Accessibility Issues

### Element Not Found
1. Check if element is visible on screen
2. Try broader search term
3. Inspect full tree: `idb-ui-describe({ operation: "all" })`
4. Check if app implements accessibility labels

### Quality Reports "minimal"
1. App may not implement accessibility
2. Custom UI components without labels
3. Fall back to screenshot approach
4. Consider filing accessibility bug with app developers

### Coordinates Don't Match
1. Ensure using `centerX`/`centerY` from find result
2. Check screen rotation/orientation
3. Verify element is still visible (no animation)
</troubleshooting>

<best_practices>
## Best Practices Summary

1. **Always assess quality first** - Never skip accessibility-quality-check
2. **Use semantic queries** - Search by label, not coordinates
3. **Prefer workflow-tap-element** - Single call for common patterns
4. **Screenshot only at end** - For verification, not interaction
5. **Include screenContext** - Helps tracking and debugging
6. **Handle minimal quality gracefully** - Have fallback ready
7. **Use tree inspection for debugging** - Understand available elements
</best_practices>
