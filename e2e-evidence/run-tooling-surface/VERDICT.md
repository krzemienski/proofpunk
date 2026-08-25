# Tooling fixes (#3, #4) — operator-surface proof

Both are CLI tools. The terminal IS their end-user surface, so the proof is an
operator running the real binary and observing the outcome, with a before/after
arm so the number means something.

## #3 test-hooks.sh — old harness could not detect the defect

One mutated hooks directory (the SessionStart comma removed, reproducing the
original SEV1), run against two harness versions:

```
OLD harness (96d91d6) -> rc=0   [structurally could not detect it]
NEW harness (HEAD)    -> rc=1   [detects it]
```

The old harness grepped for substrings, so malformed JSON still matched. The new
one parses with json.load and asserts on hookSpecificOutput. Same input, opposite
verdict — that is the fix.

## #4 installer citation resolution — before/after into clean HOMEs

Both installers run into throwaway HOMEs from the same source tree:

```
OLD installer (a431dcc): 17 skills, 1 UNRESOLVED citation
    full-functional-audit -> severity-model.md
NEW installer (HEAD)   : 18 skills, 112 citation targets checked, 0 UNRESOLVED
```

The old bundler resolved citations in a single pass, so transitively-included
references were missed — and its verifier shared the same blind spot, reporting
clean. The new one iterates to a fixed point and verifies independently.

## Scope

These are operator-CLI proofs, not agent-session proofs. Both tools have no
agent-facing surface: nothing in a Claude session invokes test-hooks.sh or the
installer. Running the real binary as the operator is the end-user path.

Sandboxes were throwaway HOMEs, removed and verified absent. No credentials were
involved in either arm.
