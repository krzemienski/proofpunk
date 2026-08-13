---
description: Task-level proof contract — every task ends with an end-user test artifact or is reported UNVERIFIED
---

# Proof obligations

Every task carries a proof obligation written before the work starts:
the end-user test to run and the assertion to check.

- A task is done only when its end-user test produced an artifact
  (screenshot, response body, disk read, exit code) in a run-scoped
  directory (`e2e-evidence/run-<timestamp>-<slug>/`).
- Test suites are the regression rail — they protect proven work, they
  never prove it. The end-user test is the only validation.
- Claims without cited artifacts are UNVERIFIED. Never upgrade UNVERIFIED
  to PASS by assumption.
