# OMP session_stop driven through its REAL registered handler

## Registration proven, not assumed
The harness passes a stub ExtensionAPI to the module's factory and
captures what it registers:
```
  registered events: session_start, tool_call, session_stop
```
That is the registration contract itself -- the handler under test is
the one the runtime would receive, not a copy of its logic.

## Six branches
```
  claim, no proof              CONTINUE  (evidence guard)
  claim + proof, intent UNMET  CONTINUE  (intent gate)
  claim + proof, intent MET    allowed to stop
  no claim at all              allowed to stop
  UNMET but stop_hook_active   allowed to stop
  no session_id                CONTINUE  (fails closed)
```
Rows 4 and 5 matter as much as the blocks. Row 4 shows the gate does
not fire on ordinary turns -- the defect an advisory caught before this
shipped. Row 5 shows the re-fired pass after a forced continuation is
not re-gated, so continue:true cannot re-enter itself forever.

## Three fixture failures getting here
1. import ext from ... -> 'ext is not a function'.
2. Rewrote as mod.default ?? mod. Same error: I changed the code
   without checking the shape, so I fixed nothing.
3. Probed instead of guessing: keys ['default'], default type OBJECT.
   tsx double-wraps under ESM/CJS interop, so the factory is at
   mod.default.default. The harness now unwraps until a function
   appears rather than assuming any single shape.

Eighth, ninth and tenth bad fixtures this session. The pattern held
again: two guesses, then one measurement that answered it immediately.

## Committed source is what was driven
sha256 of the committed files vs the copies driven:
```
  OpenCode  committed=c281e4cf3775a789  driven=c281e4cf3775a789  IDENTICAL
  OMP       committed=27c7dde5b672440a  driven=27c7dde5b672440a  IDENTICAL
```

## Still not proven
No live runtime has loaded either plugin. These drives invoke the
registered handlers directly, which is strictly stronger than the
helper matrix but weaker than an actual OMP or OpenCode session. The
harness also has zero coverage of both files, so the next change to
either is unguarded.
