# Code review of 18b2088 + 4d224de (self-review)
utc : 2026-09-14T21:40:06.392598Z
HEAD: 4d224de

Reviewing my own commits, so every concern was EXECUTED rather than reasoned
about. Two candidate defects probed; one real, one correctly dismissed.

## BLOCKING — relative `--dir` wedges the session (same class as the shipped bug)

    install --dir relskills --hooks    (cwd = some working dir)
    helper actually installed to : <cwd>/relskills/end-user-testing/scripts/
    recorded value               : "relskills"   <- relative
    hook reads it from another process with a different cwd
    result                       : WEDGED, "helper is missing"

The helper is ON DISK and the user is blocked by a fail-closed guard. That is
exactly the defect 4d224de was written to eliminate, reintroduced through the
very file added to fix it.

FIX: the installer now absolutizes before recording (`cd -- "$DIR" && pwd`,
falling back to the literal value if that fails). The hook is unchanged; the
bug was in what got written, not in how it is read.

GATE: a third arm drives a relative --dir from a foreign cwd.

mutation_test verify-hook-helper-resolution.py relative arm: baseline rc=0 ->
named mutation (record $DIR verbatim again) -> mutated_rc=1 -> restored
byte-identical -> rc=0. Only the relative arm flips; default and custom stay
green, so the coverage is discriminating.

## DISMISSED — stale record after the skills dir is deleted

Install, then `rm -rf` the skills dir. The hook blocks with "helper is
missing". I probed for the helper anywhere under HOME: NONE. The file genuinely
does not exist, so fail-closed is the correct behavior, not a defect. Recorded
because "looks like a bug, is not" deserves the same evidence as a real one.

## NOT CHANGED, deliberately

- Fail-closed posture, attempt cap, key derivation: untouched.
- The fallback chain order: $PROOFPUNK_SKILLS_DIR > recorded > repo-relative >
  CLAUDE_PLUGIN_ROOT > platform dirs. Operator override first is correct.

All 14 gates rc=0, captured unpiped.
