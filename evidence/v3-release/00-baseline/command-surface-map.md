# Command surface map — all 6 commands x every platform surface

Measured: 2026-09-04T04:44:26Z | Repo HEAD: 9963648 (working tree dirty)
Method: direct read of every command doc under `plugins/proofpunk/commands/`
and `plugins/proofpunk/opencode/commands/`, the OMP/extensions/agents
directories, the three plugin manifests, the four backing scripts
(`init_audit_workspace.py`, `session_intent.py`, `fresh_evidence.py`,
`proofpunk-install.sh`), `tools/test-installer.sh`, `tools/dry-run-install.sh`,
prior git commits `6c560ea`/`207e041`, and prior evidence artifacts under
`e2e-evidence/run-command-surface/`, `e2e-evidence/run-flag-drift/`,
`e2e-evidence/run-sdk-probes/`. This working tree carries no dirty changes to
any file cited below — all citations resolve against the committed HEAD
(9963648) content, verified with `git status --short` scoped to the cited
paths (empty output).

## Platform surface inventory (measured, not assumed)

| Platform | Command docs live at | Script/plugin glue | How it fires |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/*.md` (6 files) | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` | `/proofpunk:<name>` — plugin marketplace install |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-*.md` (6 files) | `plugins/proofpunk/opencode/plugin/proofpunk.ts`, copied by installer to `~/.config/opencode/plugin/` | `/proofpunk-<name>` (flat namespace, hyphen not colon) — installer-copied files, **not** an OpenCode-native command-registration mechanism |
| OMP (oh-my-pi) | **no `omp/commands/` directory exists** — confirmed via `glob plugins/proofpunk/omp/**` returning only `omp/agents/{end-user-validate,implement,scout}.md`, and `git log --all -- plugins/proofpunk/omp/commands` returning empty | `.omp-plugin/plugin.json` (`omp.extensions: ["./extensions/proofpunk.ts"]`), `.omp-plugin/marketplace.json` | Same `/proofpunk:<name>` names reused per `docs/usage-guide.md:18-19` and `docs/invocation-contracts.md:15` ("Claude-registry-compatible" marketplace), but there is **no dedicated OMP command file** — OMP is documented to reuse the Claude-Code-shaped command surface through its Claude-compatible skill provider, not a separate `omp/commands/*.md` set. The one OMP-specific artifact is `extensions/proofpunk.ts`, which registers exactly one command: `pi.registerCommand("proofpunk", {...})` (line 97) — a doctrine-status printer, unrelated to the 6 delivery commands. |

Claim scope: the "6+6" count in `docs/architecture.md:25,491-492` and
`plugins/proofpunk/README.md` refers to Claude Code (6) + OpenCode (6). OMP is
never counted as a third command tier anywhere in the docs I read — it borrows
the Claude-namespaced form. That claim (OMP borrows, does not duplicate) is
**UNRESOLVED at the runtime level**: no artifact in this repo or in
`e2e-evidence/` shows an OMP session actually resolving `/proofpunk:implement`
to the command file rather than falling through to skill auto-invocation. See
"Proof-level" table below.

## `/proofpunk:forge-prompt`

| Surface | File | Documented flags (argument-hint) | Backing skill instruction |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/forge-prompt.md:3` | `<goal> [--out PATH] [--depth core\|advanced]` | Activates `prompt-forge` skill AUTHOR workflow (`forge-prompt.md:6`) |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-forge-prompt.md:3` | `<goal> [--out PATH] [--depth core\|advanced]` — **identical string** | Same activation text, byte-identical body except example numbering (see Divergence #3) |
| OMP | none (no command file) | n/a | Reachable only if the operator relies on skill auto-invocation of `proofpunk:prompt-forge`, or the Claude-compatible command form documented in `docs/usage-guide.md:18-19` |

**Documented vs script-accepted flags.** `prompt-forge` has no standalone CLI
script (`glob plugins/proofpunk/skills/prompt-forge/**/*.py` and `**/*.sh`
both return no files) — the flags are interpreted entirely by the LLM
following `SKILL.md`'s command-surface table
(`plugins/proofpunk/skills/prompt-forge/SKILL.md:157-176`):

```
prompt-forge author "<goal>" [--out PATH] [--depth core|advanced]
```

`--out` and `--depth core|advanced` in the command doc match the skill table
exactly. `SKILL.md:173` states unknown flags are rejected with the flag list
— this is a documented LLM-enforced contract, not a parseable script
argument surface. No divergence found between the two command-doc copies.

**Would the documented examples run?** Example 5 in the Claude surface
(`forge-prompt.md:36-41`) uses the positional subcommand form
`/proofpunk:forge-prompt author "migration plan..."` — this matches
`SKILL.md`'s `prompt-forge author "<goal>"` syntax exactly (the word `author`
is a positional mode selector consumed by the skill, not a flag). The
OpenCode mirror's only example (`proofpunk-forge-prompt.md:12-16`) uses the
identical `author "migration plan..."` form. Both are internally consistent
with the documented skill contract.

## `/proofpunk:implement`

| Surface | File | Documented flags (argument-hint) | Backing skill instruction |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/implement.md:3` | `<goal> [--parallel] [--auto] [--mine] [--fast]` | Activates `implement` skill execution loop |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-implement.md:3` | `<goal> [--parallel] [--auto] [--mine] [--fast]` — identical | Same body, one fewer example (4 examples in Claude doc, only Example 4 kept in OpenCode mirror) |
| OMP | none (no command file); `omp/agents/implement.md` exists as a **pre-configured subagent persona**, a different mechanism from a slash command per `docs/architecture.md:26` | n/a | Spawnable as a Task-tool agent, not a slash command |

**Documented vs script-accepted flags.** No standalone CLI script backs
`implement` (`glob plugins/proofpunk/skills/implement/**/*.py`,`**/*.sh` →
empty). The skill's own command-surface table
(`plugins/proofpunk/skills/implement/SKILL.md:54-65`) documents two forms:

```
implement "<goal>" [--parallel] [--auto] [--mine] [--fast]
implement mine [--project DIR] [--since DATE] [--until DATE] [--json]
```

The `implement mine [...]` sub-form documents `--since`/`--until` — this
maps directly onto `session_intent.py`'s real flags (`--since`, `--until`,
confirmed at `session_intent.py:145-146`), which is the correct pairing (this
sub-form is session-mining delegation, not the truth-audit path). **Neither
command doc (`commands/implement.md` nor
`opencode/commands/proofpunk-implement.md`) documents the `implement mine
[...]` sub-form at all** — both only show the top-level `<goal>
[--parallel] [--auto] [--mine] [--fast]` invocation. This is not a defect
(the `mine` sub-form is an internal/advanced entry point per
`SKILL.md:79-82`), but it means a user reading only the command doc has no
way to discover `implement mine --since/--until` exists.

## `/proofpunk:install`

| Surface | File | Documented flags (argument-hint) | Backing script |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/install.md:3` | `[--platform claude-code\|opencode\|agents\|omp] [--clobber] [--no-rules]` | No script — agent-executed 4-step playbook (Detect / Write-or-merge / Scoped-rules / Verify) |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-install.md:3` | identical string | Same 4-step playbook, byte-identical body (verified: both files' lines 1-41 are line-for-line equal by diff of the read output) |
| OMP | none (no command file); OMP is one of the 4 selectable `--platform` values inside the *installer script*, not a separate command surface | n/a | n/a |

**Important distinction not to conflate**: `/proofpunk:install` (the
in-session command, agent-executed, no script) is a **different artifact**
from `tools/proofpunk-install.sh` (the operator-run bash installer that
*deploys* the plugin/skills onto a machine). They share the word "install"
but are unrelated command surfaces — the slash command sets up a *project's*
memory file (`CLAUDE.md`/`AGENTS.md`); the bash script *deploys the plugin
itself*. Confusing the two is exactly the kind of thing this map exists to
prevent.

**`/proofpunk:install`'s own flags** (`--platform`, `--clobber`, `--no-rules`)
have no backing parser — they are consumed by agent instruction-following per
`install.md:35-36,55,59,72-73`. No divergence between the two command-doc
copies (identical text, verified via read).

**`tools/proofpunk-install.sh`'s real flags** (for contrast, since it is
easily confused with the above): `--target`, `--dir`, `--source`,
`--source-dir`, `--ref`, `--only`, `--skip-skills`, `--list`, `--themes`,
`--plugins`, `--override`, `--backup`, `--no-backup`, `--with-doctrine`,
`--no-doctrine`, `--inject-claude-md`, `--inject-memory[=F]`, `--dry-run`,
`--verify`, `--no-verify`, `--quiet`, `--hooks`, `-h/--help`
(`tools/proofpunk-install.sh:126-149`, exhaustive `case` block). None of
these names overlap with `/proofpunk:install`'s three flags — confirming
these are genuinely two separate command surfaces, not one documented two
ways.

## `/proofpunk:rate-prompt`

| Surface | File | Documented flags (argument-hint) | Backing skill instruction |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/rate-prompt.md:3` | `<prompt-file.md> [--in-place] [--report-only] [--ship-below-threshold] [--out PATH]` | Activates `prompt-forge` RATE workflow |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-rate-prompt.md:3` | identical string | Same body, only the redirected-output example kept (Claude doc has 4 numbered examples, OpenCode keeps only the un-numbered "Example — redirected output" one) |
| OMP | none | n/a | n/a |

**Documented vs script-accepted flags.** `prompt-forge`'s command-surface
table (`SKILL.md:158`):

```
prompt-forge rate NAME.md [--in-place] [--report-only] [--ship-below-threshold] [--out PATH]
```

Matches both command docs exactly. `SKILL.md:174-175` documents the
mutual-exclusivity rule both command docs also state:
`--in-place` + `--out` conflict, and `--report-only` + `--out` conflict, both
fail fast with the conflict named. Verified in prior live evidence
(`e2e-evidence/run-command-surface/rate-prompt-records.json:30`): a live
worker session reasoned about combining `--report-only` and
`--ship-below-threshold` (non-conflicting pair) correctly, but this is a
model-reasoning trace, not a script-level assertion of the conflict rule —
**the mutual-exclusivity check is LLM-enforced instruction-following, not a
parser**, same caveat as forge-prompt/implement above.

**Mutual-exclusivity rules (both surfaces, byte-identical wording):**
- `--in-place` + `--out` → exclusive (same-file edit vs. separate output)
- `--report-only` + `--out` → exclusive (scorecard-only vs. redirected deliverable)
- `--ship-below-threshold` has no stated conflicts; it is a threshold override, combinable with either of the above pairs' surviving member.

## `/proofpunk:truth-audit` — the flag-drift command, now fixed

| Surface | File | Documented flags (argument-hint) | Backing script |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/truth-audit.md:3` | `<repo-path> [--start DATE] [--end DATE] [--label NAME]` | `codebase-truth-audit` skill → `scripts/init_audit_workspace.py` |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-truth-audit.md:3` | identical string | same script |
| OMP | none | n/a | n/a |

**This is the exact defect class named in the assignment.** Prior state
(pre-fix, per `e2e-evidence/run-flag-drift/VERDICT.md:1-15` and commit
`207e041`'s message): both command docs documented `--since`/`--until`, but
`init_audit_workspace.py` only accepted `--start`/`--end`
(`init_audit_workspace.py:176-177`, confirmed by direct read):

```python
parser.add_argument("--start", help="Audit-window start date or commit")
parser.add_argument("--end", help="Audit-window end date or commit")
```

Executed proof of the old defect, captured in `e2e-evidence/run-flag-drift/old.log`:
```
--since 2026-01-01                   -> rc=2  error: unrecognized arguments: --since
--start 2026-01-01 --end 2026-08-13  -> rc=0
```

**The `207e041` commit fixed only the Claude surface on its first pass.**
Direct quote from that commit's own message (captured via `git show 207e041`):
> "Both found by inspecting canonical sources after the first pass claimed
> the flag-drift defect was closed. It was not. 1.
> `plugins/proofpunk/opencode/commands/proofpunk-truth-audit.md` still
> documented `--since/--until`. The first fix only covered the Claude
> surface, so the same defect survived on the second platform."

**Current state (measured, this session):** both command docs now read
`--start DATE] [--end DATE`
(`plugins/proofpunk/commands/truth-audit.md:3,24,39` and
`plugins/proofpunk/opencode/commands/proofpunk-truth-audit.md:3,15`), and
both match the script's real argparse flags exactly. **No `--since`/`--until`
string remains in either truth-audit command doc** — confirmed via targeted
grep across both files plus the skill doc (`codebase-truth-audit/SKILL.md:71,74`)
returning only `--start`/`--end` occurrences. The class of bug (one-platform
fix leaving the mirror stale) is not currently reproduced for this command.

**`--since`/`--until` still legitimately exists elsewhere and must not be
confused with this fix**: `session_intent.py:145-146` genuinely accepts
`--since`/`--until` (a different script, a different skill —
`session-intent`, invoked internally by `codebase-truth-audit` for intent
reconstruction, not by the truth-audit command itself). `docs/usage-guide.md:271-272`
correctly documents `/session-intent --since ... --until ...` as a *separate*
skill-level invocation. This is the source of the historical confusion: two
scripts in the same audit pipeline use different flag names for a
conceptually similar "bound a time window" purpose, and a doc author
transplanting one script's flag names onto the other's command doc is
exactly how `207e041`'s defect was introduced in the first place.

**Would the documented examples run (against the real script)?**
```
init_audit_workspace.py --repo /path/to/repo --start 2026-01-01 --end 2026-08-13 --label fy26-h2-audit -> would exit 0
```
`--repo` is `required=True` (`init_audit_workspace.py:174`) and is supplied
by the command doc's `$ARGUMENTS` substitution of the positional
`<repo-path>` argument (per `truth-audit.md:8`, the skill maps the
positional to `--repo`). `--label`, `--start`, `--end` are all optional with
correct names. The Example 5 full-command invocation
(`truth-audit.md:36-40`) would run cleanly against the real script.

## `/proofpunk:verify`

| Surface | File | Documented flags (argument-hint) | Backing script |
|---|---|---|---|
| Claude Code | `plugins/proofpunk/commands/verify.md:3` | `[scope-or-entry-point]` — single positional, **no flags** | `end-user-testing` skill; `scripts/fresh_evidence.py` for evidence-dir bookkeeping (`init-run`/`next-step`/`seal`/`validate`) |
| OpenCode | `plugins/proofpunk/opencode/commands/proofpunk-verify.md:3` | identical | same |
| OMP | none | n/a | n/a |

Both command docs explicitly state there is nothing to combine
(`verify.md:41`, `proofpunk-verify.md:17`: "there are no flags to combine").
`fresh_evidence.py`'s CLI (`fresh_evidence.py:10-14`) is a 4-subcommand
positional interface (`init-run <slug>`, `next-step <slug>`, `seal`,
`validate`) called internally by the skill's protocol, never exposed as
user-facing flags on the `/proofpunk:verify` command itself. No divergence
possible on a zero-flag surface; verified both docs agree on that zero-flag
claim.

## Divergence list — cross-platform mirror defects

1. **FIXED, historical**: `/proofpunk:truth-audit` (Claude) vs
   `/proofpunk-truth-audit` (OpenCode) — `--since/--until` vs `--start/--end`
   drift, script rejected the documented flag with `rc=2`. Two-commit fix
   (`6c560ea` produced live proof surfacing the gap; `207e041` fixed the
   OpenCode mirror the first pass missed). **Current state: no drift, both
   surfaces agree with the script.** (See detailed section above.)

2. **FIXED, historical, non-command-doc**: `tools/build-site.py:311`
   hardcoded the string `/proofpunk:cook` — a command removed at v2.0.0 — as
   a generated-site literal, and omitted the real `/proofpunk:install`. This
   is not a command-doc divergence between platforms; it is a
   *site-generator* divergence from the real command set, fixed in the same
   `207e041` commit. Not re-verified in this session (out of scope: I did
   not re-run `build-site.py`), noted here only because the same commit
   touched both defect classes and a future auditor should not conflate them.

3. **Example-numbering divergence (cosmetic, all 6 commands, both
   platforms)**: Claude Code command docs use `**N.**`-numbered example
   headers that are **non-contiguous** — `forge-prompt.md` and
   `truth-audit.md` both jump `1, 2, 3, 5` (no example 4 exists in either
   file, confirmed via regex extraction). `verify.md`, `rate-prompt.md`,
   `implement.md` use contiguous `1, 2, 3, 4`. The OpenCode mirrors do not
   reproduce the Claude numbering at all — each OpenCode file keeps only
   *one* example (usually the last, renumbered or unnumbered) rather than
   the full set: `proofpunk-forge-prompt.md` and `proofpunk-truth-audit.md`
   keep only `**5.**`; `proofpunk-verify.md` and `proofpunk-implement.md`
   keep only `**4.**`; `proofpunk-rate-prompt.md` and
   `proofpunk-install.md` drop numbering entirely. This is cosmetic (does
   not affect flag correctness or runnability) but it is a real,
   currently-live divergence between the two command-doc trees that a
   doc-consistency check would flag. Not the `--since/--until` class of
   defect (no functional flag mismatch found in this category), but the
   same *root cause* — the two trees are hand-maintained in parallel rather
   than generated from one source — that produced the `--since/--until`
   defect in the first place.

4. **No divergence found** in `forge-prompt`, `implement`, `install`,
   `rate-prompt`, `verify` argument-hint strings between Claude Code and
   OpenCode — all five are byte-identical strings on line 3 of their
   respective `.md` files (verified via direct read comparison of the
   frontmatter line across all 12 files).

5. **OMP has no independently-maintained command-doc tree to diverge.** It
   cannot exhibit the `--since/--until` defect class because it has no
   command files of its own to drift — it depends entirely on the
   Claude-namespaced surface loading correctly under its Claude-compatible
   skill provider (per `docs/usage-guide.md:18-19`). This is a structural
   difference from OpenCode (which duplicates and can drift) worth flagging
   for anyone assuming a "3 platforms symmetrically" model.

## Proof-level column — what is actually verified where

| Command | Slash-surface proven (live session drove the actual `/proofpunk:*` or `/proofpunk-*` command) | Script-level proven (backing script run directly, bypassing the command doc) | Unproven |
|---|---|---|---|
| forge-prompt | No — no live-session artifact found invoking the slash command itself; only the skill `proofpunk:prompt-forge` was invoked directly via the `Skill` tool (`e2e-evidence/run-sdk-probes/skill_prompt_forge.json:6,344`, `pass: true`), which proves skill delivery, not the command-doc → skill activation path | No backing script exists for prompt-forge (LLM-only contract), so "script-level" does not apply to this command | **Command-doc-to-skill-activation path is unproven.** A worker-agent trace exists (`rate-prompt-records.json`) for the sibling `rate-prompt` command showing an agent reasoning about `/proofpunk:rate-prompt`'s flags, but no equivalent trace exists for `forge-prompt` specifically. |
| implement | No — `skill_implement.json` (`pass: true`) proves the `implement` skill loads and responds via `Skill` tool invocation, but the probe invoked the skill directly (`{"skill": "proofpunk:implement"}`), not through the `/proofpunk:implement` slash command | No standalone script (LLM-only contract) | **Slash-command surface unproven**; skill-load surface proven. |
| install | Unproven at slash-command level in any live session artifact found. | **Proven at script/mechanics level**: `tools/dry-run-install.sh` executes the exact merge/template/rules logic the command doc specifies (`dry-run-install.sh:1-5` states this explicitly: "validates the template/assets/merge logic deterministically... the command doc itself is the agent playbook this script mirrors") and asserts marker presence, ≤200-line limit, user-content preservation, and opencode AGENTS.md conventions — all PASS per script structure (not re-executed in this session; last-known state per script content). This is a **mirror/proxy script**, not the command itself: the agent-executed playbook and the shell script are two independent implementations of the same intent, so this script passing does not prove the LLM-driven command produces the same result. | The actual `/proofpunk:install` command (agent playbook, no script) has never been driven live per any artifact found in `e2e-evidence/`. |
| rate-prompt | **Partial.** `e2e-evidence/run-command-surface/rate-prompt-records.json` shows a live worker-agent session reasoning about and preparing to run `/proofpunk:rate-prompt sample.prompt.md --report-only --ship-below-threshold` (`rate-prompt-records.json:29-31`), but the captured trace ends at "Worker launched" — no ToolResult confirming the command actually executed and produced `sample.rating.md` is present in this JSON. | No standalone script (LLM-only contract) | **Execution outcome unproven** — trace shows intent-to-invoke, not completion. |
| truth-audit | No live slash-command session artifact found. | **Proven at the script's own CLI level**: `e2e-evidence/run-flag-drift/old.log`/`new.log` directly executed `init_audit_workspace.py` with both flag sets and captured real `rc=2` (old, `--since`) vs `rc=0` (new, `--start/--end`) — this is genuine command-line proof of the *script*, run independently of any agent session. Additionally, `skill_codebase_truth_audit.json` (`pass: true`) proves the `Skill` tool successfully loads `proofpunk:codebase-truth-audit` live. | **The chain "user types `/proofpunk:truth-audit --start ...` → agent correctly maps positional+flags into the `--repo`/`--start`/`--end` script invocation" is not proven end-to-end by any single artifact** — the script proof and the skill-load proof are two separate measurements that have not been composed into one live trace. |
| verify | No live slash-command session artifact found. | `end-user-testing`'s `fresh_evidence.py` is exercised transitively by every other skill's validation stage, but no artifact in this repo directly invokes `/proofpunk:verify` itself with a scope argument and shows a completed verdict. | **Fully unproven at both levels for this specific command's own invocation** (its backing skill's helper script is proven in other contexts, but not via this command). |

**Summary claim, scoped honestly**: across all 6 commands, **zero** have a
single artifact proving the full chain "slash command typed → correct
flag/script mapping → real execution → observed result." What exists is: (a)
script-level proof for `truth-audit`'s flag-drift fix specifically (the
narrowest, most load-bearing claim — the exact defect named in the
assignment — and it is genuinely proven at script level with a real rc
delta), (b) skill-load proof (via direct `Skill` tool invocation, bypassing
the command doc) for `implement`, `codebase-truth-audit`/`truth-audit`,
`prompt-forge` (covering both `forge-prompt` and `rate-prompt`'s backing
skill), and (c) mechanics-only proof for `install` via a parallel shell
script that mirrors but does not execute the actual command playbook. This
matches the documented posture in `e2e-evidence/run-sdk-probes/VERDICT.md:16-23`:
"Delivery validation... does not mean 8 things were improved" — skill
delivery and command-doc-driven execution are measured separately in every
artifact I found, never composed into one end-to-end trace for any of the 6
commands.

## Open / UNRESOLVED

- Whether OMP genuinely resolves `/proofpunk:implement` (or any of the other
  5 command names) through its Claude-compatible skill provider, versus
  requiring the operator to fall back to bare skill names or
  `/skill:<name>`, is asserted in `docs/usage-guide.md:18-19` but I found no
  executed OMP-session artifact proving it. Tried: searched
  `e2e-evidence/` for any OMP-specific command-surface probe; found
  `run-command-surface/OPENCODE-BLOCKED.md` (OpenCode, not OMP) and
  `run-sdk-probes/` (all Claude Code SDK sessions, no OMP harness found).
  `tools/sdk_probe.py` targets `claude-agent-sdk` exclusively (confirmed via
  grep of the import block) — no OMP-equivalent probe harness exists in
  `tools/`.
- The full command-doc-to-execution chain (see Proof-level table) is
  UNRESOLVED for every one of the 6 commands — no single artifact composes
  "slash command → flag mapping → script/skill execution → verified
  result" into one trace for any command. This is a gap in the evidence
  base, not a defect claim about the commands themselves — I did not
  attempt to close it in this session (out of scope: read-only assignment).
- `install.md:32` ("Both CLAUDE.md and AGENTS.md exist on opencode" merge
  rule) and the opencode mirror's identical text were read but not
  independently re-verified against `tools/proofpunk-install.sh`'s actual
  merge behavior for that specific dual-file collision case — `test-installer.sh`'s
  groups do not appear to test the case where *both* CLAUDE.md and AGENTS.md
  pre-exist simultaneously (only single-file scenarios were found in he
  script content I read; I did not exhaustively verify every one of its 264
  lines).
- Divergence item #2 (build-site.py's stale `/proofpunk:cook` reference) is
  reported as historically-fixed based on `207e041`'s commit message and
  `run-flag-drift/VERDICT.md`, but I did not re-run `tools/build-site.py` in
  this session to confirm the fix still holds at current HEAD (read-only
  assignment scope; the file was not among the working-tree's dirty files,
  so nothing suggests regression, but this is inference from absence of
  dirty-tree evidence, not a fresh execution).
