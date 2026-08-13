---
description: Evidence hygiene for run-scoped proof directories
paths:
  - "e2e-evidence/**"
  - "evidence/**"
---

# Evidence contract

- Fresh evidence per run: timestamped run directory, sequential step names,
  non-empty artifacts, never reused across runs.
- Redact before write: no tokens, cookies, keys, or personal data in any
  evidence file. Key previews are first-7-chars + ellipsis, never more.
- Cite by full path and describe what is SEEN — "see file" is not a citation.
- An artifact whose mtime predates the run start is stale and invalid.
