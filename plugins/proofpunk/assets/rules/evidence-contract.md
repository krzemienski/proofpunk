---
description: Evidence hygiene for run-scoped proof directories
paths:
  - "e2e-evidence/**"
  - "evidence/**"
---

# Evidence contract

Role note: this is the **path-scoped hygiene rule** that `/proofpunk:install`
copies into a project (`.claude/rules/`) — it auto-attaches when you touch
`e2e-evidence/**` or `evidence/**` paths. It is not the doctrine. The full
canonical standard every skill cites is the sibling
`plugins/proofpunk/references/evidence-contract.md` (Iron Rule, verification
loop, PASS criteria, refusal rules).

- Fresh evidence per run: timestamped run directory, sequential step names,
  non-empty artifacts, never reused across runs.
- Redact before write: no tokens, cookies, keys, or personal data in any
  evidence file. Key previews are first-7-chars + ellipsis, never more.
- Cite by full path and describe what is SEEN — "see file" is not a citation.
- An artifact whose mtime predates the run start is stale and invalid.
