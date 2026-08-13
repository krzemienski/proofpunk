---
description: Terminal-UI driving discipline for end-user tests of this project's TUI
paths:
  - "**/*.tsx"
  - "**/ink/**"
  - "**/textual/**"
---

# TUI driving (tui-testing)

When end-user-testing this project's terminal UI, apply the `tui-testing`
skill verbatim:

- Never pipe a TTY-guarded app (`app | tee log` kills it) — capture the
  console via `script -qfc '<cmd>' <logfile>`.
- Observe-then-act: every action follows a matched wait on VISIBLE text;
  automation-envelope `ok` is not a match — assert the condition field.
- Three facets or it didn't happen: screen waits + screenshots, direct disk
  reads, logs (console + app event log).
