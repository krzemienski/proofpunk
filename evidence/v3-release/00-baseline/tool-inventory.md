# Tool Inventory — Setup Artifact

Absence is a code path in this installer (four historical defects appeared
only when `python3` or `tar` was missing), so absent entries below are
findings, not omissions.

Host: darwin 27.0.0, arm64 (Apple M4 Max). Repo: `/Users/nick/proofpunk` @
`a41591a`. Measured 2026-09-02.

**Sequencing deviation — recorded, not concealed.** The work order requires
this artifact to be written before Phase 0 begins and the head skill
`proofpunk` to be activated first. Neither held. Actual order in this
session, from the transcript:

1. `implement` skill read (activated first — the work order's own entry
   directive named `proofpunk` first; this was a deviation).
2. Repo state, ledger, and uncommitted-diff inspection.
3. **D6 count measurement and a partial D7 install-state probe** — Phase 0
   work, executed before this artifact existed.
4. `proofpunk` head skill read (activated late).
5. This artifact written.

Consequence for the release gate: the "Phases 0-4 produce their artifacts
before any Phase 5 edit" criterion is unaffected (no Phase 5 edit exists),
but the narrower setup-before-Phase-0 ordering is **not** satisfiable for
D6 and the first D7 probe. Those two are re-derived from the tree in Phase 0
proper so their recorded values do not depend on this out-of-order pass.
No Phase 0 register row cites this pre-artifact measurement as its evidence.

## 1. Host toolchain — measured, with versions

Measured by `command -v <t> && <t> --version | head -1` for each; PyYAML and
`claude_agent_sdk` measured by import.

| Tool | Present | Version | Relevance |
|---|---|---|---|
| `python3` | YES | 3.11.6 | installer `--hooks` guard; all stdlib tooling |
| `tar` | YES | bsdtar 3.5.3 (libarchive 3.7.4) | local install skill-tree extraction |
| `git` | YES | 2.55.0 | `--ref` resolution; `git show <sha>` before-arms |
| `pandoc` | YES | 3.11 | site generation |
| PyYAML | YES | 6.0.2 | `build-site.py` frontmatter parsing |
| `mmdc` (mermaid-cli) | YES | 11.6.0 | optional diagram pre-render |
| `claude-agent-sdk` (python) | YES | 0.2.144 | `sdk_probe.py` live-session probes |
| `jq` | **SUBSTITUTE** | `jaq 2.3.0` (not GNU jq) | JSON in shell — behavior differences must be verified before any tool depends on it |
| `shellcheck` | **ABSENT** | — | L5 lint lane: must install, vendor, or record as an explicit exception |
| `node` / `npm` | YES | v22.22.3 / 10.9.8 | host runtimes only; no runtime dependency added |

Findings carried into Phase 0/3:
- **F-T1 `shellcheck` ABSENT.** L5's "run shellcheck across all hook scripts"
  cannot execute on this host as written. Records as a gap now so it is not
  silently skipped later.
- **F-T2 `jq` is `jaq`.** `command -v jq` succeeds but the binary is `jaq`.
  Any harness assuming GNU jq semantics is untested here. Note: the first D6
  attempt in this session used `jq -r 'keys[]'` and returned the *top-level*
  keys (`description`, `hooks`) — correct for the file shape, but it proves
  the shell JSON path is live and must be pinned before use.

## 2. Hosts installable on this machine

Phase 2 conformance must be **driven**, not asserted. All three target hosts
are present:

| Host | Present | Version |
|---|---|---|
| Claude Code | YES | 2.1.258 |
| OpenCode | YES | 1.18.26 |
| oh-my-pi (OMP) | YES | omp/18.1.2 |

Consequence: there is no documented excuse for asserting per-host conformance.
Each host is drivable, so C7/L12/L14 must load skills on the real host.

## 3. Installed-vs-repo state (D7 first measurement)

Listing only; version reconciliation is D7's own task in Phase 0.

- **Three proofpunk install roots exist simultaneously** under
  `~/.claude/plugins/`: `cache/proofpunk-marketplace`,
  `data/proofpunk-inline`, `data/proofpunk-proofpunk-marketplace`.
  This is the duplicate-install class that produced duplicate doctrine
  injection at `f95ba9d`. Versions and hook registrations are measured in D7.
- `~/.claude/skills` holds **625** standalone skill directories. Every
  proofpunk skill also exists here as a standalone copy, which is exactly why
  **only namespaced `/proofpunk:...` invocation is attributable** in any live
  proof.
- `~/.config/opencode/skills` holds **143** entries (plural path present).
- `~/.omp/agent/skills` holds 4; `~/.omp/agent/managed-skills` holds 439.

## 4. Automation surfaces available for driving real systems

Recorded because end-user validation is the only proof; a surface that does
not exist bounds what can be proven.

| Surface | Available | Mechanism |
|---|---|---|
| HTTP / API | YES | `curl` via `bash` |
| Browser | YES | `browser` tool (real Chromium, puppeteer) + chrome-devtools MCP |
| Desktop / native UI | YES | `computer` tool (screenshots, AX tree) |
| PTY / TUI | YES | `tmux` 3.7c present; `bash` + `hub` process control |
| Slash-command surface | YES | Claude Code 2.1.258, OpenCode 1.18.26, OMP 18.1.2 all installed |
| Live agent sessions | YES | `claude-agent-sdk` 0.2.144 → `sdk_probe.py` |
| iOS simulator | UNVERIFIED | not probed this session; `mobile-validation-runner` lane must probe before claiming |
| Subagent fan-out | YES (constrained) | `task` tool — see §6 |

## 5. MCP servers, tools, and skills present

**MCP servers connected (4):**

| Server | Tools | Use here |
|---|---|---|
| `chrome-devtools` | 30 (click, fill, navigate, snapshot, screenshot, lighthouse, trace, …) | second browser driver; L17 site verification |
| `context7` | 2 (`resolve-library-id`, `query-docs`) | Phase 2 canon retrieval for host docs |
| `knowledge-graph-memory` | 9 (entities, relations, observations, search) | candidate adapter surface for L9 memory bus |
| `sequential-thinking` | 1 (`sequentialthinking`) | Phase 4 recorded reasoning gate |

**Native tool surfaces present:** `read`, `write`, `edit`, `bash`, `glob`,
`grep`, `task`, `hub`, `todo`, `eval`, `browser`, `computer`, `web_search`,
`ast_grep`, `ast_edit`, `lsp`, `debug`, `checkpoint`/`rewind`, `learn`,
`manage_skill`, Mnemopi memory (`retain`/`recall`/`reflect`/`memory_edit`).

**Notably ABSENT:** no dedicated HTTP-client tool (use `bash` + `curl`); no
iOS-simulator tool (use `bash` + `xcrun simctl`).

**Skills:** the 18 proofpunk skills are loaded and routable. The head
`proofpunk` was read in this session (17 routed skills + 13 doctrine
references, matching the tree), but **after** the first D6/D7 probes, not
first as the work order directs — see the sequencing deviation above.

## 6. Subagent routing constraint — binding on Phase 4 fan-out

This host routes models only through `9router/<provider>/<model>`. Specialist
agent shorthands (`scout`, `researcher`, `Explore`, `docs-manager`) resolve to
`anthropic`, which has **no active credentials**, and fail instantly with a
`404`. That failure is a misconfiguration, never a reason to declare work
blocked.

Rule adopted for every `task` dispatch in this run:
1. Omit `agent` so the worker inherits the session's working 9router route.
2. Never spawn a specialist shorthand whose backing model is unconfirmed.
3. Read-only research needs no subagent — `read`/`grep`/`glob` suffice.

## 7. Selection rationale

- **Stdlib-only holds.** Every capability the work order needs has a present
  stdlib or POSIX path: JSON Lines + `hashlib` (no client library), `git` for
  differential arms, `curl` for API proof. No new runtime dependency is
  required by anything inventoried above.
- **Two browser drivers exist** (`browser`, chrome-devtools MCP). Prefer
  `browser` for scripted proof; page identity must be asserted in the same
  evaluation as any capture regardless of driver.
- **`shellcheck` and iOS-simulator access are the only real gaps.** Both are
  recorded as findings (F-T1, and the UNVERIFIED row in §4) rather than
  assumed available, so no later lane can claim them silently.
