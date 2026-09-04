# Proofpunk Usage Guide — Claude Code, oh-my-pi, and OpenCode

> **Read first:** [architecture.md](architecture.md) — how the 18 skills execute as one delegation DAG: method ownership, the full call graph, execution order per command, and the deferral rules that keep methods unduplicated.


How to actually invoke all 18 skills once the plugin is installed, with real
argument syntax and examples. For the full flag/permutation tables see the
README's Command Reference; this guide is the hands-on "type this" version.

## How invocation works per platform

**Claude Code** — plugin commands are namespaced: `/proofpunk:implement`,
`/proofpunk:verify`, `/proofpunk:truth-audit`,
`/proofpunk:rate-prompt`, `/proofpunk:forge-prompt`. Skills also fire
directly (`/implement`, `/verify`, …) or from natural language. A SessionStart
hook injects the doctrine once per session.

**oh-my-pi (OMP)** — after `omp plugin install proofpunk@proofpunk`, the
same command names work (`/proofpunk:implement`). Skills are discovered from
the plugin's `skills/` directory and load on demand; `/skill:<name>` opens one
interactively. The doctrine-guard extension (`extensions/proofpunk.ts`,
declared in `package.json` `omp.extensions`) blocks destructive commands and
secret-file reads in every session. Plain installs via
`proofpunk-install.sh --target omp` land in `~/.omp/agent/skills` (native
provider, highest precedence).

**OpenCode** — the installer drops `plugin/proofpunk.ts` (doctrine guard),
six commands (`/proofpunk-implement`, `/proofpunk-install`,
`/proofpunk-verify`, `/proofpunk-truth-audit`, `/proofpunk-rate-prompt`,
`/proofpunk-forge-prompt`), and the `proofpunk` primary agent into
`~/.config/opencode/`. Skills load through OpenCode's native `skill` tool —
and because OpenCode reads `~/.claude/skills` too, one
`--target claude-code` install serves both platforms.

## How invocation works in Claude Code

1. **Slash command**: `/skill-name <arguments>` — the arguments string is
   passed to the skill as its input. Positional arguments and CLI-style
   flags work exactly as each skill's command surface defines them.
2. **Natural language**: you can also just describe the task ("rate this
   prompt", "audit this repo for production readiness") — Claude Code
   routes to the skill from its description. Slash commands are the
   deterministic path when you want a specific skill with specific args.
3. **Chaining**: skills delegate to each other per the delegation graph
   (README diagram 3). Invoking `/implement` fires session-intent,
   prompt-forge, validation-plan, plan-hardening, and the proof
   layer in one run — you don't invoke those separately unless you want
   just one layer.

## Orchestration

### `/proofpunk` — router head (pick the right skill)

```
/proofpunk "audit the checkout flow and fix what fails"
/proofpunk "plan and implement offline sync for the mobile app"
```

No flags. Names the single best-fit skill for the ask — or a short
ordered chain for compound asks (`brainstorm` → `validation-plan` →
`implement`) — and hands off without repeating that skill's own
doctrine. Use it when unsure which skill applies or when a request
spans more than one skill's scope.

### `/implement` — the front door (execution loop)

```
/implement <goal> [--parallel] [--auto] [--mine] [--fast]
/implement mine [--project DIR] [--since DATE] [--until DATE]
```

```
/implement "add billing webhooks with signature verification"
/implement "add billing webhooks" --mine
/implement "migrate auth to JWT" --parallel
/implement "rebuild the notification system" --parallel --auto --mine
/implement mine --project my-shop --since 2026-07-01
```

What happens: Stage 0 distills TRUE success criteria (escalates for your
approval if the goal isn't clearly laid out — the only mandatory stop
under `--auto`) → optional session mining → parallel codebase scouts →
prompt-forge forges the build prompt → decomposition into a task graph
where every task carries a written proof obligation → the execution loop:
execute a task, end-user test it immediately, record the proof in the
live execution ledger → the stuck protocol on failures (attempt →
root-cause → split → escalate) → the report rendered from the ledger:
criteria-by-criteria proof table.

## Prompt and plan layer

### `/prompt-forge` — author / rate / optimize / pipeline

```
/prompt-forge author "a code-review prompt for Go services"
/prompt-forge author "a SQL review prompt" --depth advanced --out prompts/sql-review.md
/prompt-forge rate prompts/login.md
/prompt-forge rate prompts/login.md --in-place
/prompt-forge rate prompts/login.md --report-only
/prompt-forge optimize prompts/login.md --evidence captures/bad-output.txt
/prompt-forge pipeline "onboarding revamp" --dir .prompts/onboarding
```

Positionals: `"<goal>"` for author/pipeline, `NAME.md` for rate/optimize.
Ratings always write `NAME.rating.md` + `NAME.remediated.md` unless you
pass `--report-only` or `--in-place`. Optimize refuses to run without
`--evidence` — real failure output is its hard requirement.

### `/brainstorm` — decide the approach

```
/brainstorm "websockets vs SSE for live order updates"
/brainstorm "how should tenant isolation work in the schema"
```

No flags. Output: trade-off analysis with brutal honesty, then a design
you approve before any planning begins.

### `/validation-plan` — proof-carrying plans

```
/validation-plan "the mood-ring feature"
/validation-plan .planning/BRIEF.md
```

No flags. Produces BRIEF → ROADMAP → per-phase PLAN/SUMMARY/VALIDATION
with blocking cumulative proof obligations.

### `/plan-hardening` — red-team a plan or prompt

```
/plan-hardening .planning/phases/02-webhook-endpoint.md
/plan-hardening prompts/sql-review.md
```

No flags. Positional: the plan or prompt file to harden. Output:
confidence-gap scoring, 4-lens red-team, dispositioned gap register,
proof obligations injected into the document.

## Execution layer

### `/stack-testing` — real-server test rigs

```
/stack-testing "run the checkout e2e against the dev server"
```

Natural-language routing to the stack runbooks. The bundled CLI for
lifecycle-managed servers:

```bash
python3 plugins/proofpunk/skills/stack-testing/scripts/with_server.py \
  --server "npm run dev" --port 5173 -- npx playwright test e2e/checkout.spec.ts
```

`--server` starts the real server, `--port` proves readiness by the port
answering (condition-based, no sleeps), the trailing positional after
`--` is your actual check command.

### `/mobile-validation-runner` — iOS end-user validation

```
/mobile-validation-runner "the login screen"
/mobile-validation-runner "full onboarding flow on iPhone 16 Pro simulator"
```

No flags. Lanes (simctl / XC-MCP / Expo-idb) are routed by your
environment and request, not by arguments — say "simctl only" in the
request if you want the bundled lane. Protocol:
SETUP → RECORD → ACT → COLLECT → VERIFY, with three-facet checks.

### `/tui-testing` — terminal UI end-user proof

```
/tui-testing "the dashboard renders, navigates, and saves"
/tui-testing "prove the install wizard works end to end"
```

No flags. Drives the real TUI in a real PTY as the end user: never
pipe a TTY-guarded app, observe-then-act with matched-assertion waits,
three-facet evidence (screen + disk + logs), pixel proof for visual
claims, and a secret scan before sealing. Not for web UIs or
non-interactive CLIs (`references/cli-validation.md`).

## Proof layer

### `/end-user-testing` — fresh evidence lifecycle

```
/end-user-testing "seal the mood-ring run"
```

Natural-language routing; the enforcing CLI (invoked by every verdict):

```bash
python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py init-run mood-ring
python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py next-step mood-ring
python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py seal
python3 plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py validate
```

Positional `<slug>` names the run. Exit 2 = refusal with STALE:/EMPTY:
lines per offending artifact.

### `/visual-inspection` — screenshot QA

```
/visual-inspection evidence/run-20260811/step-03-checkout.png
/visual-inspection "all screenshots in the sealed run"
```

No flags. Positional: a screenshot path or scope. Severity-classified
defect report; never pass a screenshot you haven't actually read.

### `/ui-experience-audit` — deep UX audit

```
/ui-experience-audit "the checkout flow"
/ui-experience-audit screenshots/step-05-settings.png
```

No flags. Six phases: triage → visual → interactive → content → Nielsen
heuristics → synthesis.

### `/full-functional-audit` — app-wide sweep

```
/full-functional-audit
/full-functional-audit "the admin panel"
```

No flags. Inventory every interaction → execute each → remediate →
verdict, batched through end-user testing.

## Deep-analysis layer

### `/root-cause-debugging` — fix the cause, never the symptom

```
/root-cause-debugging "tests pass locally but fail in CI"
/root-cause-debugging "the webhook endpoint 500s only under load"
```

No flags. Reproduce → minimize → hypothesize → instrument; the Iron
Rule: no fix without reproduction, no claim without evidence.

### `/red-team-eval` — hostile review + measured QA cycles

```
/red-team-eval .planning/ROADMAP.md
/red-team-eval prompts/sql-review.md
```

No flags. Positional: the artifact to attack. 4 lenses (security,
scope-creep, evidence-rigor, failure-modes) plus eval-driven scoring.

### `/production-readiness` — ship-readiness audit

```
/production-readiness
/production-readiness "focus on the billing subsystem"
```

No flags. 8-phase audit: cleanup waves, dead code, doc drift,
spec-compliance matrix (COVERED/INCOMPLETE/MISSING), dependency
supply-chain health.

### `/session-intent` — mine Claude Code transcripts

```
/session-intent --project my-shop --since 2026-07-01
/session-intent --since 2026-08-01 --until 2026-08-07 --json out/intent.json
```

Flags map straight onto the bundled CLI:

```bash
python3 plugins/proofpunk/skills/session-intent/scripts/session_intent.py \
  --project my-shop --since 2026-07-01 --md out/intent-matrix.md
```

Exit 2 when no transcripts match — never a silent empty success.

### `/codebase-truth-audit` — repo-wide truth audit

```
/codebase-truth-audit /path/to/repo
/codebase-truth-audit /path/to/repo --start 2026-06-01 --end 2026-08-01 --label q3-audit
```

Positionals: the repository path. Flags map onto the bundled CLI, which
scaffolds the 8-phase audit workspace with captured git evidence:

```bash
python3 plugins/proofpunk/skills/codebase-truth-audit/scripts/init_audit_workspace.py \
  --repo /path/to/repo --label q3-audit --start 2026-06-01 --output-root plans/
```

The audit pauses for explicit approval before any behavior or
destructive change.

## Chaining recipes

| Goal | Sequence |
|------|----------|
| Ship a feature end to end | `/implement "..." --mine` (fires the whole chain) |
| Ship it unattended | `/implement "..." --parallel --auto --mine` |
| Audit an inherited repo | `/codebase-truth-audit /repo` → `/session-intent --project repo` → `/production-readiness` |
| Fix a flaky flow | `/root-cause-debugging "..."` → drive the fixed flow as the end user (shared runbooks in `references/`) |
| Harden a plan before building | `/validation-plan "..."` → `/plan-hardening .planning/...` → `/implement .planning/ROADMAP.md` |
| Perfect a prompt | `/prompt-forge author "..."` → `/red-team-eval prompts/x.md` → `/prompt-forge optimize prompts/x.md --evidence ...` |
| Release check | `/full-functional-audit` → `/production-readiness` |

## After installing with the script

`tools/proofpunk-install.sh` installs the skills as **plain skills**
(not a plugin) into the skills dir of your platform — Claude Code
(`~/.claude/skills`), oh-my-pi (`~/.omp/agent/skills`), OpenCode
(`~/.config/opencode/skills`), or the shared agents location
(`~/.agents/skills`). Post-install invocation is identical to the above;
verify with:

```bash
tools/proofpunk-install.sh --target claude-code --dry-run   # see the full plan
tools/proofpunk-install.sh --target claude-code             # install all 18 + doctrine
```