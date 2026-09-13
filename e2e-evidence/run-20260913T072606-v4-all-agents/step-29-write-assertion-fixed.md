# step-29 — write assertion fixed; provenance settled

## Provenance: ambient file or in-session write?

Read from the recorded run, not inferred:

    Bash call 1  pwd && ls -la ... ls -la CLAUDE.md AGENTS.md   -> sandbox
                 listed, no CLAUDE.md present
    Bash call 5  cd <sandbox> && cat > CLAUDE.md <<'EOF'
                 <!-- proofpunk:begin -->
                 ## Proof contract (proofpunk)

A fresh per-arm sandbox, empty at call 1, written at call 5 with the exact
marker the check greps for. NOT an ambient preexisting file. The
counterfactual independently agrees: no file, no markers.

## The defect was the checker

    write_calls = [c for c in tool_calls if c["name"] in ("Write","Edit")]

The probe asks "was the memory file installed" and measured "was the Write
tool used". Its own `why` says the intent: "a real first-party Write/Edit
call, not an ambient MCP tool and not just narration". Bash is first-party
and its effect is on disk. The check contradicted its documented contract.

## Fix, with a safety boundary

Credits Write/Edit, or a Bash command whose text actually redirects into
THIS artifact. Rejected: ls, cat <file>, grep, wc, writes to another path,
and merely naming the file in an echo. Mechanism recorded separately
(write_tool_used, write_mechanism) so contract and mechanism stop being
conflated; neither gates the verdict.

## Two defects caught by replaying BEFORE claiming

1. `import re` was missing — 0 occurrences in the file. The first patch
   would have raised NameError on the first install effect arm. A read-only
   review would not have caught this; executing it did.

2. Representation mismatch. sdk_probe stores the LIVE DICT at runtime
   (line ~522 `"input": b.input`) but `json.dumps(b.input)[:200]` when
   serializing (line ~612) — deliberately truncated, therefore invalid
   JSON. My first version called json.loads and returned False on failure,
   which silently reads a CLIPPED record as "no write happened". That is
   the same class of error as the bug being fixed: absence of evidence
   treated as evidence of absence. Now falls back to raw-text scan.

The 0/6 replay result was itself caused by defect 2 — I fed the persisted
truncated string to a parser expecting valid JSON. The checker was not
wrong about the run; my test harness was wrong about the shape.

## Regression test
tools/test-write-assertion.py — 29 assertions:
  6 write forms x 2 serializations (runtime dict, persisted truncated str)
  7 non-write forms x 2 serializations
  Write/Edit always count; Read never counts
  MUTATION GUARD: asserts the OLD predicate FAILS on the real observed
  command, so the test provably exercises the regression it exists for.

## Verifiers at this HEAD
    verify-counts          PASS
    verify-orchestration   PASS
    test-hooks             PASS
    test-integrations      36/36

test-integrations first reported FAIL under `node`. Cause: it uses
`import.meta.dir`, which is Bun-only and undefined in Node — it crashed in
its own path resolution at line 42, before touching any Python. Sixth
instrument error this session. Under bun: 36/36.

## Status
P6 remains UNVERIFIED. This removes a wrong question from the surface; it
does not make the surface pass. The model is still unpinned and unrecorded,
which stays the gating experiment.

VERDICT: apparatus defect fixed and regression-pinned. Install was never
broken.
