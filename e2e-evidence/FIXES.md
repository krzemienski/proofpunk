# Fix ledger — 11 fixes, 10 end-user proven, 1 UNPROVEN

Written because the count was being reconstructed from memory and drifted: at
one point the summary said "10 fixes" while #9 was unproven, which only balanced
because #11 had quietly replaced it. Explicit table, one row per fix.

| # | Defect fixed | Proof level | Evidence |
|---|---|---|---|
| 1 | Hook emitted invalid JSON; host silently dropped the doctrine | END-USER | live session quotes `"Proofpunk is installed."` from a prompt that never contained it — `run-sdk-probes/doctrine.json` |
| 2 | Orchestration graph had zero roots — no entry point | END-USER | router invoked, successful ToolResult — `run-sdk-probes/router.json` |
| 3 | `test-hooks.sh` grepped substrings, passed on malformed JSON | END-USER | one mutated hooks dir: old harness `rc=0`, new `rc=1` — `run-tooling-surface/VERDICT.md` |
| 4 | Installer resolved citations single-pass; verifier shared the blind spot | END-USER | old installer 1 unresolved (`full-functional-audit -> severity-model.md`), new 0 of 112 — `run-tooling-surface/VERDICT.md` |
| 5 | Skill count wrong across manifests and docs | END-USER | all 18 skills invoked live from the local v2 plugin, none missing — `run-command-surface/INVENTORY-V2.md` |
| 6 | `truth-audit` documented `--since/--until`; script takes `--start/--end` | END-USER | slash command ran; generated `plan.md` records the window — `run-command-surface/VERDICT.md` |
| 7 | `rate-prompt` omitted `--ship-below-threshold` | END-USER | command expanded, flag read semantically — `run-command-surface/rate-prompt-records.json` |
| 8 | `build-site.py` had undeclared PyYAML/pandoc deps | END-USER | real run with pandoc off PATH `rc=1` actionable; control arm `rc=0`, docs unchanged — `run-command-surface/generator-missing-pandoc.txt` |
| 9 | Same flag drift on the **OpenCode** surface | **UNPROVEN** | install-level only; sandbox auth fails before dispatch — `run-command-surface/OPENCODE-BLOCKED.md` |
| 10 | `/proofpunk:cook` hardcoded in the site generator | END-USER | browser-rendered `commands.html` shows 6 real commands, cook absent — `run-flag-drift/commands-rendered.webp` |
| 11 | Guidance pointing at skills that no longer exist | END-USER | browser-rendered LAYERS board — `run-flag-drift/layers-corrected-rendered.webp` |

## What "END-USER" means per row

Not uniform, and worth being precise about:

- **1, 2, 5** — a live agent session loaded the plugin and the behavior was
  observed in it.
- **6, 7** — a real slash command was typed at the `claude` CLI and expanded.
- **3, 4, 8** — the operator ran the real binary in a terminal. For CLI tools
  the terminal *is* the end-user surface; each carries a before/after arm so the
  number is not merely a green reading.
- **10, 11** — a real browser rendered the page, with page identity asserted in
  the same evaluation as the capture.

## #11 — what the image actually shows

`layers-corrected-rendered.webp` shows all five layer rows of the regenerated
site:

```
L1  ORCHESTRATION   proofpunk · implement
L2  PROMPT & PLAN   prompt-forge · brainstorm · validation-plan · plan-hardening
L3  EXECUTION       stack-testing · mobile-validation-runner
L4  PROOF           end-user-testing · visual-inspection · ui-experience-audit ·
                    full-functional-audit · tui-testing
L5  DEEP ANALYSIS   root-cause-debugging · red-team-eval · production-readiness ·
                    session-intent · codebase-truth-audit
```

Before the fix, L1 omitted the router entirely, L3 led with `cook`, and L4
included `functional-validation` — none of which exist in v2.0.1. The generator
reproduced all three on every build.

An earlier capture (`skills-18-rendered.webp`) was above-the-fold and showed
only the `18 skills` heading; it corroborates but does not depict the corrected
map. This one does.

## The one that is not proven

**#9** is proven only at install level: a clean-HOME install emits
`--start/--end` with no `--since`. Nobody drove the `opencode` binary executing
the command. The sandbox HOME has no OpenCode credentials and the auth error
fires before command dispatch, so the plugin is never reached.

A key-free provider fails provider resolution first; driving the user's real
HOME executes a plugin command against live config. Neither is safe to take
unilaterally, so #9 stays UNPROVEN rather than proven by a method requiring the
user's credentials — attempted twice this session and recorded as a mistake in
`OPENCODE-BLOCKED.md`.
