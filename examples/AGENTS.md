<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-08-23 | Updated: 2026-08-23 -->

# examples

## Purpose

Dogfooding target for proofpunk: `mood-ring` is a small Flask journaling app that the proofpunk skills (brainstorm → validation-plan → implement → end-user-testing → audits) were executed against end-to-end. It demonstrates the full doctrine on a real codebase, including the evidence runs and planning artifacts those skills produce.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `mood-ring/` | The Flask demo app with its tests, `.planning/` phase plans, `.prompts/` forged prompts, and `e2e-evidence/` run captures |

## For AI Agents

### Working In This Directory

- Treat `mood-ring/` as a consumer of the plugin, not part of the shippable plugin — changes here do not ship to users.
- The `.planning/` and `e2e-evidence/` trees are captured artifacts of real runs; do not regenerate, restyle, or prune them — they are the demo's proof.
- To re-demo a skill against mood-ring, follow the invocation examples in `plugins/proofpunk/docs/usage-guide.md` rather than improvising flags.

### Testing Requirements

- App-level checks: run mood-ring's own `tests/` suite (pytest) inside `mood-ring/`; end-user proof only via a fresh `e2e-evidence/run-*/` capture.

## Dependencies

### Internal

- Exercises the skills in `plugins/proofpunk/skills/` as installed behavior.

### External

- Flask + pytest (see `mood-ring/pyproject.toml`).

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->
