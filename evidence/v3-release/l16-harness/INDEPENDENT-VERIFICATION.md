# L16 harness-integrity gate — independent verification

Verified: 2026-09-04 (UTC) | HEAD `9963648` (working tree dirty)
Verifier: orchestrating session, re-running the gate directly rather than
accepting the building lane's `"mutation_proven": true` claim.

## Result: the gate discriminates, with one documented blind spot

| Arm | Mutation | rc | Named? |
|---|---|---:|---|
| baseline (real tree) | none | **0** | — |
| weak mutation | `$HOOKS/` → `/dev/null/` in `test-hooks.sh` | **0** | **NO — missed** |
| true neuter | `$HOOKS/<name>.sh` → `true` (basename removed) | **1** | **yes, names `test-hooks.sh`** |

The gate catches the defect it is designed for. It does **not** catch a
harness that invokes correct basenames at a wrong path.

## Why the weak mutation escaped — and why that is by design, not a bug

`per_line_invoked` (`tools/verify-harness-integrity.py:376`) matches a subject
basename preceded by `/`, quote, paren, or whitespace:

```
b_re = re.compile(r"(?:^|[\s\"'/(])" + re.escape(basename) + r"(?=$|[\s\"')/])")
```

Rewriting `$HOOKS/` to `/dev/null/` leaves the line as
`sh "/dev/null/stop-guard.sh"` — keyword `sh` in command position, basename
still preceded by `/`. Co-occurrence holds, so the gate passes even though the
harness now executes nothing.

This is the deliberate cost of indirection-safety. The gate must accept
`sh "$HOOKS/x.sh"`, `bash "$V/x.sh"`, and `bash "$(dirname "$0")/x.sh"`,
because keying on the full literal path is exactly the mistake that produced a
false finding earlier in this project (a literal-string count reported 0 for a
harness that genuinely invokes all 9 hook scripts). Prefix-blindness is what
buys that correctness.

The gate's own docstring already states the boundary:

> "this gate is a coverage-presence check, not a correctness check"

## Consequence — what this gate may and may not be cited for

**May be cited for:** a harness whose source no longer references its declared
subject at all — the `dry-run-install.sh` defect class from `5e5150b`, where a
harness was labelled the installer's test but never invoked it (literal count:
0). That is the historical defect, and it is now caught by name.

**May NOT be cited for:** proof that a harness executes its subject
*successfully*, reads the result, or points at a real path. A harness invoking
correct basenames under a wrong root passes this gate. Closing that would
require executing each harness under instrumentation and observing the subject
actually open — out of scope here, and recorded as open rather than implied.

## Note on my own first attempt

My initial mutation run reported `rc=2` and I nearly recorded it as a pass.
It was argparse rejecting an unrecognized `--tools-dir` flag — the gate never
ran. A non-zero exit is not evidence the gate detected anything; the exit code
had to be attributed to the right cause before it could be cited. Recorded
here because attributing a red gate to the wrong reason is the same error
class this gate exists to catch.

## Open

- Wrong-path invocation with correct basenames is undetected (above).
- The building lane grandfathered 6 harness declarations into a central
  `MANIFEST` because file-ownership boundaries forbade adding inline
  `PP-HARNESS-SUBJECT` tags to files another lane owned. Any future lane
  touching those files should migrate the declaration inline and delete the
  MANIFEST entry.
- `verify-citations.py` was found to be a 6th pre-existing harness absent from
  the work order's list of 5. The work order's enumeration was incomplete; the
  gate covers it.
