# D6 + D7 — Canonical counts and installed-vs-repo state

Measured 2026-09-02 against `/Users/nick/proofpunk` @ `a41591a`.

This file supersedes the pre-artifact D6/D7 probes noted as a sequencing
deviation in `../00-baseline/tool-inventory.md`; every value below is
re-derived here from the tree and the live host.

## D6 — Ground-truth counts (canonical for all later phases)

Method: `glob` over the product tree; `hooks.json` parsed with Python stdlib.

| Thing | Count | Derivation |
|---|---|---|
| Skills | **18** | `plugins/proofpunk/skills/*/SKILL.md` |
| Shared references | **13** | `plugins/proofpunk/references/*.md` |
| Commands (Claude Code) | **6** | `plugins/proofpunk/commands/*.md` |
| Commands (OpenCode) | **6** | `plugins/proofpunk/opencode/commands/*.md` |
| Hook files (`.sh`) | **9** | `plugins/proofpunk/hooks/*.sh` |
| Hook config files | **1** | `plugins/proofpunk/hooks/hooks.json` |
| Hook event keys | **7** | `hooks.json` `.hooks` keys |
| Hook script registrations | **11** | every `.hooks[event][].hooks[]` entry |
| Distinct scripts registered | **9** | unique commands across those 11 |
| Agents (`agents/`) | **3** | `end-user-validate.md`, `implement.md`, `scout.md` |
| Agents (`opencode/agents/`) | **4** | adds `proofpunk.md` |
| Agents (`omp/agents/`) | **3** | same three as `agents/` |
| Tools | **10** | `tools/*` excluding `__pycache__` |

Skill names (18): `brainstorm`, `codebase-truth-audit`, `end-user-testing`,
`full-functional-audit`, `implement`, `mobile-validation-runner`,
`plan-hardening`, `production-readiness`, `prompt-forge`, `proofpunk`,
`red-team-eval`, `root-cause-debugging`, `session-intent`, `stack-testing`,
`tui-testing`, `ui-experience-audit`, `validation-plan`, `visual-inspection`.

Hook files (9): `bash-write-notice.sh`, `bash-write-snapshot.sh`,
`capture-guard.sh`, `evidence-guard.sh`, `instructions-loaded.sh`,
`no-test-files.sh`, `post-write-walkthrough.sh`, `session-start.sh`,
`stop-guard.sh`.

Tools (10): `AGENTS.md`, `INSTALL.md`, `build-site.py`, `dry-run-install.sh`,
`generate-themes.py`, `proofpunk-install.sh`, `sdk_probe.py`,
`test-hooks.sh`, `test-installer.sh`, `verify-orchestration.py`.

### D6 findings

- **F-D6-1 — `fresh_evidence.py` is NOT in `tools/`.** The work order and
  HEAD's commit body both cite it; the glob of `tools/*` returns ten entries
  and none is `fresh_evidence.py`. This is exactly the D5 unknown ("referenced
  but not yet seen"). Its true location is D5's task; what is proven here is
  only that `tools/` is not it.
- **F-D6-2 — hook event keys are nested.** `hooks.json` has two top-level
  keys (`description`, `hooks`); the seven event keys live under `.hooks`.
  A naive `keys[]` query returns the wrong thing — recorded because the
  installer derives its registration list from this file.
- **F-D6-3 — agent counts differ per platform** (3 / 4 / 3). The OpenCode
  tree carries a `proofpunk.md` agent the Claude and OMP trees do not. Not
  yet judged correct or incorrect; flagged for the parity lane.

### Hook events and registrations — MEASURED

Parsed from the nested `.hooks` object with Python stdlib (clean run):

| Metric | Measured |
|---|---|
| Event keys | **7** |
| Script registrations | **11** |
| Distinct scripts registered | **9** |

Full registration table:

| Event | Matcher | Timeout | Script |
|---|---|---|---|
| `SessionStart` | `startup\|resume\|clear` | 5 | `session-start.sh` |
| `Stop` | (none) | 10 | `stop-guard.sh` |
| `SubagentStop` | (none) | 10 | `stop-guard.sh` |
| `PreToolUse` | `Write\|Edit` | 5 | `no-test-files.sh` |
| `PreToolUse` | `Write\|Edit` | 5 | `evidence-guard.sh` |
| `PreToolUse` | `Write\|Edit` | 5 | `capture-guard.sh` |
| `PreToolUse` | `Bash` | 10 | `bash-write-snapshot.sh` |
| `InstructionsLoaded` | (none) | 5 | `instructions-loaded.sh` |
| `PostToolUse` | `Write\|Edit` | 5 | `post-write-walkthrough.sh` |
| `PostToolUse` | `Bash` | 10 | `bash-write-notice.sh` |
| `PostToolUseFailure` | `Bash` | 10 | `bash-write-notice.sh` |

All 9 distinct scripts exist on disk (matches the 9 `.sh` files counted
above); every registration is `sh ${CLAUDE_PLUGIN_ROOT}/hooks/...`.

- **F-D6-4 — the work order's "9 script registrations" is wrong; the repo is
  right.** Measured: 7 event keys (correct) but **11 registrations** across
  **9 distinct scripts**. Two scripts are registered twice —
  `stop-guard.sh` (`Stop` + `SubagentStop`) and `bash-write-notice.sh`
  (`PostToolUse/Bash` + `PostToolUseFailure/Bash`). The number 9 is the count
  of distinct hook *files*, not registrations.

  **Correction to an earlier draft of this finding.** I first wrote that the
  repo guidance carried the wrong number too. That was false and is retracted.
  `plugins/proofpunk/docs/architecture.md:497` already states, verbatim,
  "9 hook scripts / 7 events / 11 registrations", and lines 498-500 record the
  derivation and the 7/6/8 → 7/9/11 growth when `bash-write-snapshot.sh` and
  the `PostToolUseFailure` registration landed. The repo measured this
  correctly; only the **v3 work order** (and this session's initial reading of
  it) carries "9 registrations".

  Consequence: the work-order validation criterion "at HEAD: 18 skills, 7
  event keys, 9 script registrations" is **defective as written**. It must
  read 11 registrations / 9 distinct scripts, or any gate encoding it will
  fail spuriously against a correct tree. Phase 3 checks whether any harness
  encodes the wrong number; `architecture.md` does not.

## D7 — True installed-vs-repo state — RESOLVED

### Repo manifest versions (all five agree)

| File | Version |
|---|---|
| `.claude-plugin/marketplace.json` | 2.2.0 |
| `.omp-plugin/marketplace.json` | 2.2.0 |
| `plugins/proofpunk/package.json` | 2.2.0 |
| `plugins/proofpunk/.claude-plugin/plugin.json` | 2.2.0 |
| `plugins/proofpunk/.omp-plugin/plugin.json` | 2.2.0 (uncommitted; was 2.0.1 at HEAD) |

The `.omp-plugin/plugin.json` bump is an uncommitted working-tree change, not
part of `a41591a`. Recorded so no later claim treats it as shipped state.

### Installed state on this host

Three paths under `~/.claude/plugins/` contain the string `proofpunk`:

| Path | Contents | Status |
|---|---|---|
| `cache/proofpunk-marketplace/proofpunk/2.2.0` | full tree, 18 skills, `hooks/hooks.json` | **REGISTERED** |
| `cache/proofpunk-marketplace/proofpunk/1.10.1` | full tree, **19 skills**, `hooks/hooks.json` | orphan on disk, not registered |
| `data/proofpunk-inline` | empty | inert |
| `data/proofpunk-proofpunk-marketplace` | empty | inert |

`installed_plugins.json` holds exactly one entry for
`proofpunk@proofpunk-marketplace`:

```
scope=user  version=2.2.0
installPath=~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/2.2.0
gitCommitSha=a41591aa7a3718990ed1a1a43da017a25c0d49c8
installedAt=2026-09-02T07:02:06.121Z
```

**Verdict: the installed plugin matches the repo at HEAD** — same version
(2.2.0), same commit SHA (`a41591a`), same skill count (18). The `f95ba9d`
failure mode (two *registered* versions both injecting doctrine) is **NOT**
reproducing today: only one version is registered.

### D7 findings

- **F-D7-1 — stale 1.10.1 tree persists on disk.** It is not registered, so
  it does not inject doctrine, but it still ships **19 skills including the
  dead names `cook` and `functional-validation`** and lacks the `proofpunk`
  router head. Any tool that globs the marketplace cache rather than reading
  `installed_plugins.json` will see 19 skills and two names the project
  removed. This is a live instance of the count/name-drift class.
- **F-D7-2 — `~/.claude/settings.json` contains ZERO proofpunk hook
  registrations.** Hooks reach the session through the plugin's own
  `hooks.json`, not through user settings, on this host. Any claim that the
  installer's `settings.json` merge is exercised here is therefore
  UNVERIFIED until an actual `--hooks` install into a clean HOME is driven.
- **F-D7-3 — 625 standalone skills in `~/.claude/skills`** shadow the plugin
  copies by bare name. Confirms the constraint: only `/proofpunk:...`
  namespaced invocation is attributable in any live proof.

## Evidence

All values above were produced by `bash` and `glob` calls in this session
against the live tree and live host state. Raw command transcripts are the
session record; no capture file is cited for a claim it does not contain.
