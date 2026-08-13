<!-- proofpunk:begin -->
## Proof contract (proofpunk)

- Done means proven by end-user testing: drive the real system as the end
  user, capture run-scoped evidence, cite it by full path. Unexecuted =
  UNVERIFIED, never PASS.
- No mocks, stubs, or placeholder implementations. Malformed input fails
  clearly and safely. Secrets never enter evidence directories.

## Commands

- Test: `{{TEST_COMMAND}}`
- Build: `{{BUILD_COMMAND}}`
- Proof runs: `/proofpunk:verify` before any completion claim;
  `/proofpunk:implement "<goal>"` for multi-step work.

## Project

- {{PROJECT_NAME}} — see @README.md (if present) for overview.
<!-- proofpunk:end -->
