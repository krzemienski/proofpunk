# UX Heuristic Evaluation — Phase 4 Method

A systematic application of Jakob Nielsen's 10 usability heuristics (1994, language refinements 2020), supplemented by Don Norman's affordance / signifier framework. These are the most durable usability principles in the field — derived from factor analysis of 249 usability problems and refined across 30+ years of UI evolution.

Use them as an inspection lens, not a quiz. For each screen, ask: *which of these is being violated, and how?*

## How to apply

1. Walk through the screen Phase 1–3 findings already gathered
2. For each heuristic in turn, ask the question(s) below
3. Record violations with: heuristic number + name, what you see, the offending element, and a proposed fix
4. A single defect may violate multiple heuristics — record each separately

Three to five evaluators yield ~75% defect coverage; a single thorough evaluator yields ~30–35% (Nielsen 1994). For solo audits, augment by walking the screen twice — once focused on heuristics 1–5, once on 6–10.

---

## Heuristic 1 — Visibility of system status

> The design should always keep users informed about what is going on, through appropriate feedback within a reasonable amount of time.

Inspection questions:
- After every user action, is there visible feedback (button press state, loading indicator, toast, navigation transition)?
- During async operations, does the user know something is happening (spinner, skeleton, progress bar)?
- Is current location in app communicated (breadcrumbs, selected tab, page title, highlighted nav)?
- Are connection / sync states shown when relevant (online/offline, syncing, saved, unsaved)?

Common violations:
- Form submission with no loading state — user clicks submit twice
- "Save" button with no confirmation — did it save?
- Sidebar nav item not highlighted on current page
- Background sync silent — user doesn't know data is stale or fresh

---

## Heuristic 2 — Match between system and real world

> The design should speak the users' language, with words, phrases, and concepts familiar to the user, rather than internal jargon. Follow real-world conventions.

Inspection questions:
- Does the copy use user vocabulary, not engineering vocabulary?
- Are icons conventional (magnifying glass = search, gear = settings, pencil = edit)?
- Are dates / numbers / currency in the user's locale?
- Do error messages name the user's problem in their terms?

Common violations:
- "401 Unauthorized" instead of "You need to sign in"
- "Container instantiation failed" instead of "Couldn't start the app — try again"
- Engineering term in UI: "POST request failed" exposed to end user
- Calendar in MM/DD when user locale is DD/MM

---

## Heuristic 3 — User control and freedom

> Users often perform actions by mistake. They need a clearly marked "emergency exit" to leave the unwanted action without having to go through an extended process.

Inspection questions:
- Is there a way to undo every reversible action?
- Are destructive actions confirmed?
- Can users cancel long-running operations?
- Can they back out of a flow without losing entered data?
- Is "Cancel" or "Back" always available where it should be?

Common violations:
- Sent email with no undo (Gmail solved this with the 30-second undo)
- Multi-step form loses data on back-navigation
- Modal with no close button or Esc handler
- Destructive action with single-click confirm and no undo

---

## Heuristic 4 — Consistency and standards

> Users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform and industry conventions.

Inspection questions:
- Does the screen follow platform conventions (iOS HIG, Material Design, OS-native patterns)?
- Are similar elements styled consistently across the app (button styles, spacing, type scale)?
- Are terms used consistently? (Don't call it "Profile" on one screen and "Account" on another)
- Are interactions consistent? (If swipe-to-delete works on one list, does it work on all lists?)
- Is iconography consistent? (Same icon means the same thing everywhere)

Common violations:
- "Save" on settings, "Update" on profile, "Apply" on preferences — three names for the same operation
- Modal close buttons in different corners on different modals
- Tab bar present on some screens, hidden on others without clear rule
- New screen breaks design system tokens (custom colors, sizes)

This heuristic is also known as Jakob's Law: *Users spend most of their time on other sites, so they expect yours to work like the others they know.*

---

## Heuristic 5 — Error prevention

> Even better than good error messages is a careful design which prevents a problem from occurring in the first place.

Inspection questions:
- Are easy-to-confuse options separated or distinguished?
- Are destructive actions visually different from constructive?
- Are inputs constrained where possible (date picker, number stepper, select)?
- Are confirmations required for high-stakes actions?
- Are smart defaults provided?

Common violations:
- "Delete" button right next to "Save" button, same style
- Free-text date entry instead of a date picker
- No confirmation on "Delete account"
- Default value missing on a field where most users want a specific value

There are two error subtypes:
- **Slips** — user knew what to do, did the wrong thing (typo, wrong button)
- **Mistakes** — user didn't know what to do, did the wrong thing intentionally

Different prevention strategies for each: slips need constraint and confirmation, mistakes need clarity and guidance.

---

## Heuristic 6 — Recognition rather than recall

> Minimize the user's memory load by making elements, actions, and options visible. The user should not have to remember information from one part of the interface to another.

Inspection questions:
- Are options visible (menu items, toolbar) rather than recalled (keyboard-only)?
- Is context preserved across screens (selected filter shown, current step highlighted)?
- Are recently-used items surfaced (recent searches, recent files)?
- Are field formats shown inline, not buried in help docs?
- Can the user see what they entered before they submit?

Common violations:
- Filter applied on list but no chip / pill showing what filter is active
- Multi-step form doesn't show selections from earlier steps
- Search bar with no recent or suggested searches
- "Enter date in YYYY-MM-DD format" buried in helper text — user has to recall

---

## Heuristic 7 — Flexibility and efficiency of use

> Shortcuts — hidden from novice users — may speed up the interaction for the expert user. Allow users to tailor frequent actions.

Inspection questions:
- Are keyboard shortcuts available for power users?
- Can users customize / save preferences (favorites, saved filters, default views)?
- Are bulk actions available where one-by-one would be tedious?
- Are advanced settings hidden by default but discoverable?
- Are common tasks one click away, complex tasks at most three?

Common violations:
- No keyboard shortcuts in a tool used daily
- No way to save a frequently-used filter combination
- Bulk operations missing (must delete files one at a time)
- Power-user features absent or impossibly buried

---

## Heuristic 8 — Aesthetic and minimalist design

> Interfaces should not contain information that is irrelevant or rarely needed. Every extra unit of information competes with the relevant units and diminishes their relative visibility.

Inspection questions:
- Is every element on the screen earning its place?
- Is visual hierarchy guiding the eye to the primary action?
- Is the screen visually noisy (too many colors, weights, sizes, icons)?
- Are decorative elements adding meaning, or just clutter?
- Could anything be progressively disclosed instead of always-shown?

Common violations:
- Five primary buttons on one screen — none feels primary
- Decorative illustrations that don't communicate
- Information density too high, no whitespace breathing room
- Marketing copy intermixed with functional UI

This heuristic is *not* a mandate for sparseness — domain-rich screens (Bloomberg, Figma, Linear) appropriately have high density. The test is whether the density is *earned*.

---

## Heuristic 9 — Help users recognize, diagnose, and recover from errors

> Error messages should be expressed in plain language (no error codes), precisely indicate the problem, and constructively suggest a solution.

Inspection questions:
- Do error messages avoid jargon and codes (or pair them with plain text)?
- Do they say *what* went wrong and *what to do* about it?
- Are they placed near the cause (inline at the field, not toast across the screen)?
- Is the affected field visually highlighted (color + icon, not color alone)?
- Is the recovery path obvious (button to retry, link to fix the input)?

Common violations:
- "An error occurred" — no useful info
- "Field is required" — but which field?
- Toast that vanishes before user can read it
- Red border on field with no message explaining what's wrong
- Error code only ("E_AUTH_42") with no plain-text guidance

The "three-part error message" formula:
1. *Clearly state the problem*
2. *Explain why it happened* (when relevant)
3. *Suggest a constructive next step*

---

## Heuristic 10 — Help and documentation

> It is best if the design does not need additional explanation. However, it may be necessary to provide documentation to help users understand how to complete their tasks.

Inspection questions:
- Is help available where the user needs it, not only in a separate help center?
- Are tooltips / inline hints provided for complex inputs?
- Is onboarding or first-use guidance present for non-obvious features?
- Is the help searchable and task-oriented?
- Can users find help without leaving their task?

Common violations:
- Help only available via separate "Help" page in nav
- No tooltips on icon-only buttons
- No first-use guidance for complex features (advanced filters, etc.)
- Help docs explain features alphabetically, not by user task

---

## Affordance / signifier alignment

Beyond Nielsen's 10, evaluate every interactive element against Don Norman's affordance framework (covered in detail in `interactive-element-audit.md`):

| Failure | Question | Severity |
|---------|----------|----------|
| False affordance | Does anything *look* interactive that isn't? | HIGH–CRITICAL |
| Hidden affordance | Does anything *do* something but show no signal? | HIGH |
| Conflicting signifier | Do two visual cues suggest different actions on the same element? | MEDIUM |
| Convention violation | Does the signifier conflict with platform / industry convention? (e.g., a hamburger that opens a search) | HIGH |

---

## Output format

```
## Phase 4 — UX Heuristic Evaluation (<screen name>)

### Findings
- [SEVERITY] [Heuristic #N: <name>] — <what you see> — <offending element> — <suggested fix>

Example:
- [HIGH] [Heuristic 1: Visibility of system status] — "Save" button shows no
  loading or confirmation state on tap. — Settings → "Save" button. — Add
  spinner on tap, success toast on completion.

- [MEDIUM] [Heuristic 6: Recognition rather than recall] — Active filter not
  shown after applied — user must remember they filtered by "Open" status. —
  Issues list — Add chip/pill showing active filter with × to clear.
```

---

## Citation

Nielsen, J. (1994). *Enhancing the explanatory power of usability heuristics.* Proc. ACM CHI'94 Conf., 152–158.
Norman, D. (1988). *The Design of Everyday Things.* Basic Books.
