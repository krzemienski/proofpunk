# v3 Phase-4 Dispositions

Status of the four Phase-4 reviewer verdicts after the gauge-4 remediation
(commit `90bf91d`, 2026-09-09). Verdict payloads:
`e2e-evidence/run-20260907T232538-phase4-reviewer-verdicts-raw/`.

**Nothing on this page is reviewer approval of the remediation.** The
reviewers evaluated proposals, not this implementation. "Applied" below
means the named change exists in the committed tree; the live full-chain
run and mutation artifact that would prove it are **BLOCKED on the gateway
OAuth 401 flap (2026-09-09 ~19:00Z→)** and are reported UNVERIFIED until
they land. See `e2e-evidence/run-20260909T190000-v3b-gauge4/` (preserved
failed run).

## ReviewSequencing — REJECT — HONORED AS WRITTEN

Verdict (`step-04-...-ReviewSequencing.json`): implementing proposal C2 as
written, at that point in the sequence, with the Phases 0-4 gate not
genuinely satisfied, was incorrect. Disposition: C2-as-written was never
implemented — no commit descends from `r1-candidates.md:41-49` as proposed,
and the self-approval language the reviewers caught was retracted by the
prior session itself (`.planning/v3-execution-ledger.json:105-110`). The
gauge-4 work that eventually landed descends from this run's
operator-approved v3-spec (`.planning/v4-architecture/v3-spec.md`, work
item b) and the other three reviewers' named changes — a different
artifact from the rejected proposal, built after the gate conditions the
REJECT named were addressed (D-A fixed and proven first).

## ReviewProbeDesign — ADOPT-WITH-CHANGES — MECHANICS IN TREE, RUNTIME UNPROVEN

Named changes and where they landed (all in commit `90bf91d`). Items 1–3
below are *implemented*; items 4–7 in the Open list are NOT — they remain
deferred to a separately approved task. Everything on this page, applied
or open, is *unproven at runtime* until the blocked live run lands — read
"landed" as "the code exists", never as "the behavior is verified".

1. **Root cause accepted at the literal level**: `_SLASH_PLAYBOOK_TOOLS`
   disallowed the very tools its level required — the level-c ceiling was by
   probe construction. → New effect probes carry their own tool dicts
   (`_EFFECT_TOOLS_INSTALL` / `_EFFECT_TOOLS_VERIFY`,
   `tools/sdk_probe.py:296-310`) that do NOT disallow Write/Edit/Bash.
2. **Ambient-MCP false-PASS closed** (sealed evidence showed
   `cmd_slash_install`'s effect produced by an ambient
   `mcp__filesystem__write_file`, not first-party Write): →
   `strict_mcp_config=True` with no `mcp_servers` excludes every ambient MCP
   server; the effect can only come from a first-party call.
3. **Filesystem-only verdicts**: install checks read the sandbox file
   (`claude_md_exists`, `markers_present`, `within_200_lines`,
   `template_substituted`); verify checks read Bash `tool_result` payloads.
   The model's reply text is never a check input.

**Open (named by this verdict, NOT yet implemented):**

4. **Merge-branch byte-canary** (`ReviewProbeDesign.json` §3): for the
   merge-into-existing-file branch, the canary must be the FULL
   pre-existing file body with byte-identical prefix/suffix comparison
   against the pre-run original — not a single-line substring check. The
   current effect probe exercises only the no-existing-file branch (fresh
   sandbox with a bare package.json); the merge branch is untested.
5. **Scoped-rules criterion and ≤200-line cap** (same §3, citing
   `install.md:59-73` and `install.md:25`): the ≤200-line cap IS checked
   (`within_200_lines`); scoped rules are not — the probe runs with
   `--no-rules`, so that criterion is currently out of the probe's scope
   by construction and must either be added as a second arm or declared
   out of scope explicitly.
6. **Template-read provenance** (§2, "content without provenance"):
   nothing in the current checks proves the model actually READ
   `assets/claude-md-template.md` rather than pattern-inventing plausible
   markers. A template-read ToolUseBlock assertion is required.
7. **Template's pre-existing markers ambiguity** (§4):
   `claude-md-template.md` itself ships `proofpunk:begin`/`end` markers —
   the marker-presence check must distinguish "file created from the
   template" from "file that merely contains marker strings", e.g. via
   the provenance assertion in (6) plus content-shape checks.

## RedTeamEffectProbe — ADOPT-WITH-CHANGES — MECHANICS IN TREE, RUNTIME UNPROVEN (top 4 vectors)

1. **Causal attribution** → playbook-content counterfactual:
   `build_neutered_install_plugin()` (`tools/verify-command-surface.py:508`)
   copies the real plugin, replaces `commands/install.md`'s body with a no-op
   preserving frontmatter byte-for-byte, and refuses to produce a byte-
   identical mutation. The counterfactual arm must show `pass` explicitly
   False, `write_succeeded` False, `claude_md_exists` False, slash
   registration still True, and `plugin_path` realpath-equal to the scratch
   copy (`promote_to_effect_proven`, `:420-488`) — otherwise promotion to
   level "d" is blocked with every failing condition named.
2. **Narration-only PASS** → the checks{} dicts above; for verify, the
   per-run cryptographic sentinel (`secrets.token_hex(8)`) must surface in a
   genuinely-executed Bash result — the model cannot know the filename
   without running a real command.
3. **Non-determinism** → three states distinguished:
   `write_attempted`/`bash_attempted` (ToolUseBlock present) vs
   `write_succeeded`/`bash_executed` (result present, `is_error is not True`)
   vs content checks (`template_substituted`, `sentinel_surfaced`).
4. **Remaining 8 of 12 vectors** — delivered in chat only, never persisted
   (`evidence/v3-release/04-proposals/reviewers/RedTeamEffectProbe.md:11`).
   Status: UNVERIFIED gap, carried as a risk in the v3-spec §6 and re-stated
   here: a fresh red-team pass against the post-remediation implementation
   is the closure path.

## HardenProposalPlan — ADOPT-WITH-CHANGES — MECHANICS IN TREE, RUNTIME UNPROVEN

1. **Write-tool mechanism named**: first-party Write/Edit granted explicitly
   (portable, hermetic) — not the ambient MCP server.
2. **Verify contract distinguished**: separate `cmd_slash_verify_effect`
   (Bash-execution sentinel proof), not a copy of install's file-merge shape.
3. **Per-arm sandbox isolation**: fresh `tempfile.mkdtemp()` per command per
   arm (`run_arm_with_retry`, `:241-297`), replacing the shared `work` dir.
4. **Teardown specified**: `shutil.rmtree` in `finally` after every attempt;
   checks are computed inside the probe subprocess before teardown.
5. **Byte-match semantics**: `template_substituted` + `markers_present`
   acknowledge the memory file is template-substituted (no `{{` literals
   remain) rather than byte-comparing against the template.
6. **Implementation sequence** (`:18`): steps 0-5 and the synthetic
   regression suite are complete and committed; the live full-chain run,
   mutation artifact, and fresh gates are **BLOCKED on the gateway 401 flap
   (2026-09-09 ~19:00Z→)** — see `.planning/v4-architecture/` run ledger and
   `e2e-evidence/run-20260909T190000-v3b-gauge4/` (preserved failed run).

## What remains open

- Live full-chain verification of level "d" (blocked: gateway OAuth 401).
- Mutation artifact for the new effect-check logic (same blocker).
- RedTeamEffectProbe vectors 5-12 (unpersisted; needs a fresh red-team pass).
