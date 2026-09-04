# L16 Harness Integrity — Mutation-Proof Summary

## Method
Gate under test: `tools/verify-harness-integrity.py`. Never mutated the
real `tools/` files — a full isolated copy of `tools/` + `plugins/` was
built at `evidence/v3-release/l16-harness/mutation-sandbox/` and every
mutation was applied there via `--root <sandbox>`.

Exit codes captured separately from stdout+stderr for every run
(`subprocess.run(..., capture_output=True)`, never a shell pipe), so no
run's exit code could be silently masked by a pipeline stage.

## Arm 1 — baseline (real tree, unmodified)
- Command: `python3 tools/verify-harness-integrity.py`
- Result: **exit 0** (green). Log: `arm1-baseline.log`, rechecked after all
  mutation work in `arm1-baseline-recheck.log` (also exit 0) to prove the
  real tree was never altered by this task.

## Arm 0 — sandbox control (unmodified copy, before any mutation)
- Command: `python3 tools/verify-harness-integrity.py --root <sandbox>`
- Result: **exit 0** (green). Log: `arm0-sandbox-control.log`.
- Confirms the sandbox copy itself is a faithful, unmutated baseline
  before either mutation is applied.

## Mutation 1 — shell_script_subjects harness (test-hooks.sh)
- **Named defect**: replaced the line
  `out=$(sh "$HOOKS/session-start.sh" 2>/dev/null)` in the sandbox copy of
  `tools/test-hooks.sh` with a hardcoded `echo` of the expected JSON shape
  — i.e. the harness stops invoking `session-start.sh` but keeps "passing"
  its own internal assertion against fabricated output.
- **Result: exit 1** — gate goes RED and names the failing harness AND the
  specific missing subject:
  `[FAIL] test-hooks.sh ... declared subject not invoked: session-start.sh`
  Log: `arm2-mutated.log`. All 6 other harnesses still PASS (proves the
  gate is not globally blind — it isolates the one broken harness).
- **Restore**: original `test-hooks.sh` content written back byte-for-byte.
  Re-run: **exit 0**. Log: `arm3-restored.log`.
- **Byte-identical proof**: `arm3-restored.log` == `arm0-sandbox-control.log`
  (verified via Python string equality, both files independently captured):
    - arm0 sha256: `1755ddcb458a7117dd4c3099d46713cb2d1b44be6cfe7299ea129f56353fe685`
    - arm3 sha256: `1755ddcb458a7117dd4c3099d46713cb2d1b44be6cfe7299ea129f56353fe685`
  Also verified the restored sandbox `test-hooks.sh` file itself is
  byte-identical to the real `tools/test-hooks.sh` (same sha256), and that
  the real `tools/test-hooks.sh` was untouched throughout (compared before
  and after the mutation experiment; identical hash both times):
    - real tools/test-hooks.sh sha256 (post-experiment):
      `ef2b9d0b6e1aee4516be759f38b3d73193e947ccd2841c68d6af4eb304d369a6`

## Mutation 2 — python_file_level harness (verify-orchestration.py)
- **Named defect**: in the sandbox copy of `tools/verify-orchestration.py`,
  every literal occurrence of the string `SKILL.md` was renamed to
  `SKILL_RENAMED.md` (3 occurrences: the glob pattern, the body-lookup
  join, and the `HELPER` path is unaffected as it targets a different
  filename) — the harness no longer references its declared subject
  filename anywhere in source.
- **Result: exit 1** — gate goes RED and names the failing harness AND the
  specific missing subject:
  `[FAIL] verify-orchestration.py ... declared subject not invoked: SKILL.md`
  Log: `arm4-mutated-python-level.log`. All 6 other harnesses still PASS.
- **Restore**: original `verify-orchestration.py` content written back
  byte-for-byte. Re-run: **exit 0**. Log: `arm5-restored-python-level.log`.
- **Byte-identical proof**: `arm5-restored-python-level.log` ==
  `arm0-sandbox-control.log` (Python string equality, verified True).
  Restored sandbox `verify-orchestration.py` also verified byte-identical
  to the real `tools/verify-orchestration.py` (same content, compared via
  direct read + equality, and the real file was never opened for writing
  by this task).

## Conclusion
The gate is **not structurally blind**: two independent mutation classes
(shell-indirection-based invocation removal, and literal-token-based
invocation removal) each turned exactly one named harness red while
leaving the other harnesses — including harnesses using the SAME
detection `kind` — green. Both mutations were fully reversible with
byte-identical restoration proven against three independent references
(sandbox control run, real-tree baseline run, real source file hash).

mutation_proven: true
