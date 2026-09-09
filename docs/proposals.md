# Phase 4 — Proposals

Every proposal names the finding it closes, the candidates evaluated, how
it fails, and its proof plan. Nothing here is implemented; adoption gates
implementation, and an ADOPT-WITH-CHANGES verdict is not an adoption until
the changes are specified.

Reviewers were independent subagents. The orchestrator authored P1 and
therefore did not review it.

**Reviewer verdicts — byte-exact original payloads**, captured through the
canonical evidence tool (`fresh_evidence.py init-run` → `next-step` →
`seal` → `validate`, **validate rc=0**), inventory at
`e2e-evidence/run-20260907T232538-phase4-reviewer-verdicts-raw/evidence-inventory.txt`.
Each file is the reviewer's original JSON payload: it parses as JSON from
byte 0 and contains zero read-renderer line prefixes. Every verdict below
was parsed from that payload, 4/4.

| Reviewer | Verdict | Artifact (`path@sha256`) |
|---|---|---|
| ReviewProbeDesign | ADOPT-WITH-CHANGES | `e2e-evidence/run-20260907T232538-phase4-reviewer-verdicts-raw/step-01-phase4-reviewer-verdicts-raw-ReviewProbeDesign.json@sha256:cfac6b93b5af64ee7cee8d5d30392ae8493dd03adf6494c131a73d281eef2c4e` |
| RedTeamEffectProbe | ADOPT-WITH-CHANGES | `e2e-evidence/run-20260907T232538-phase4-reviewer-verdicts-raw/step-02-phase4-reviewer-verdicts-raw-RedTeamEffectProbe.json@sha256:0c118bfaf5b9fa35f1a4b401ed6e5c404250367436d5f08f2ff6b58c4ece1613` |
| HardenProposalPlan | ADOPT-WITH-CHANGES | `e2e-evidence/run-20260907T232538-phase4-reviewer-verdicts-raw/step-03-phase4-reviewer-verdicts-raw-HardenProposalPlan.json@sha256:0a1dacc03e1c38632a876eeef8bf61ddc325c95a5d3802926cb605b96ee0d859` |
| ReviewSequencing | REJECT | `e2e-evidence/run-20260907T232538-phase4-reviewer-verdicts-raw/step-04-phase4-reviewer-verdicts-raw-ReviewSequencing.json@sha256:fe6c84915f6ff8cefba127cbfaa1a7521b2a56f2478dac899bb6a81bb9af6240` |

### Two earlier captures of the same verdicts — provenance, not deletion

Both are retained; neither is cited for verdict text.

1. `evidence/v3-release/04-proposals/reviewers/*.md` — ad-hoc seal;
   hand-written `inventory.json`, never validated by `fresh_evidence.py`.
2. `e2e-evidence/run-20260907T232239-phase4-reviewer-verdicts/*.md` —
   canonical tool, `validate rc=0`, but the **content is rendered, not
   raw**: every file carries read-renderer line prefixes (`1|`, `2|`) and
   `step-01` additionally contains a tool-generated
   "You have received this identical output…" annotation. Its 176 extra
   bytes over capture 1 are renderer metadata, not reviewer content — an
   inference I stated wrongly as "complete" before measuring.

## P1 — Effect-proof for write-effecting slash commands

**Finding closed:** Gauge 4 (L16) reports 4/6. `/proofpunk:install` and
`/proofpunk:verify` score `playbook-recognition`.

**Original proposal (C2, `docs/v3-research/r1-candidates.md`):** add new
write-enabled probes with fresh `--cwd` sandboxes, an outside-marker
canary, and `--no-plugin` control arms; leave the recognition probes
intact.

**Status: NOT ADOPTED — insufficient as written.** Three independent
reviewers returned ADOPT-WITH-CHANGES; the required changes are larger
than the proposal, and one reviewer finding invalidates the proposal's
own stated premise.

### The premise was wrong — measured, not argued

I stated the root cause twice and was wrong both times.

1. *"SDK sessions have no Write tool"* — false framing (host limitation).
2. *"The write block is a deliberate harness choice"* — true but
   incomplete.
3. **Measured truth:** `_SLASH_PLAYBOOK_TOOLS`
   (`tools/sdk_probe.py:190-195`) blocks the tool *names*
   `Write`/`Edit`/`Bash`, but an **ambient host MCP server** is
   unenumerated and wide open. The sealed artifact
   `evidence/v3-release/l16-commands/cmd_slash_install.plugin.log`
   records `mcp__filesystem__write_file` writing `CLAUDE.md` into the
   probe's temp dir, followed by a `Read` confirming the content landed.

**`/proofpunk:install` already executed a real file write at the slash
surface.** The gauge scored it `playbook-recognition` because the probe's
`checks{}` — `{text_matches, slash_registered, slash_expanded,
local_plugin_loaded}` — never inspects the filesystem. The instrument was
blind, not the command inert.

### Three defects this exposed, none of which C2 addresses

**D-A — Write-guard bypass via MCP (new channel).**
`plugins/proofpunk/hooks/hooks.json` scopes the `PreToolUse` guard to
matcher `Write|Edit`. `mcp__filesystem__write_file` does not match, so
proofpunk's own guards did not fire on a real write. The Bash-bypass
defect class, previously documented as open for Bash only, recurs through
a **third** channel. This is a product finding, not a harness finding.

**D-B — Attribution gap.** The probe read its template from the
**marketplace cache** (`~/.claude/plugins/cache/proofpunk-marketplace/
proofpunk/2.2.0/assets/claude-md-template.md`), not this checkout.
Verified this session: cache and local templates are byte-identical
(sha256 prefix `3ce15b0a…`), so the run cannot distinguish them — a
divergence would be invisible. `local_plugin_loaded: True` asserts the
plugin path, not the asset provenance.

**D-C — Causal attribution.** A filesystem delta plus slash expansion does
not prove the *playbook's content* caused the write. `Read` is
unrestricted; the model receives full instructions and could act on
pattern-matching. Closing this needs a playbook-content counterfactual:
neuter `install.md`'s body in a scratch plugin copy, require the effect to
**disappear**, restore byte-identically.

### How P1 fails (stated, per the proposal contract)

- Passes because an ambient MCP server unrelated to the plugin wrote the
  file (host-config-dependent false PASS).
- Passes on content the template already ships rather than content the
  command produced — the template is pre-marked at line 1, which already
  produced one misdiagnosis this run.
- Control arm exits 1 for the wrong reason (crash, auth, missing sandbox)
  and is scored as a correct denial.
- Cannot distinguish did-not-attempt / attempted-and-denied /
  attempted-succeeded-wrong-content.
- Single-line canary proves one line survived, not that the prefix and
  suffix are byte-identical.

### Sequencing hazard found by review

`tools/gauge-report.py` `g_command_surface_proven()` counts rows where
`reached_level == 'c'` and computes `total = len(cmds)`. **Appending two
new command rows makes gauge 4 report 4/8 — worse than today's 4/6.** The
correct schema keeps six rows and promotes the two existing rows to a new
level, extending the gauge predicate. The `_effects` naming in C2 actively
suggests the wrong implementation.

### Proof plan (if P1 is later adopted, revised)

1. Hermetic write channel chosen and asserted by name — not left to
   whatever MCP the host happens to mount.
2. Per-arm fresh `mktemp -d`, asserted outside the repo, with teardown.
3. Byte-identical prefix/suffix comparison against the pre-run original,
   branch-scoped (merge vs create vs `--clobber`).
4. Assertions on the filesystem delta only; model narration never counts.
5. Control arm must complete cleanly and fail by *absence*, with a
   same-session baseline sanity check.
6. Playbook-content counterfactual for causation (D-C).
7. Provenance assertion that this checkout's assets were used (D-B).
8. Mutation proof: break the new check, watch it FAIL naming the command,
   restore byte-identically, seal fresh evidence.

## P2 — Close the MCP write-guard bypass (D-A)

**Finding closed:** proofpunk's `PreToolUse` guard matcher `Write|Edit`
does not cover MCP filesystem writes; a real write bypassed it in sealed
evidence.

**Status: PROPOSED, NOT ADOPTED.** This is a product-behavior change to a
shipped guard. It must not be made from a single orchestrator-authored
memo, and it is out of scope for a run whose front half was reconstructed
rather than executed in order.

**How it fails:** a matcher broadened by pattern risks the exact defect
this repo already retired — the abandoned shell-parsing guard that falsely
blocked `cp -p`, `mv -f`, `touch -c`, `sed -i -e`. Any fix must be
mutation-proven against those four commands plus a normal MCP read.

## What remains unproven

- Gauge 4 stays **UNMET 4/6**. Its target was not lowered.
- P1 and P2 are recorded, reviewed, and **not implemented**.
- The reviewers' full reports are the sealed artifacts cited by
  `path@sha256` in the table at the top of this file. The former
  `agent://` references were ephemeral session handles that expire and do
  not resolve for an independent verifier; they are replaced, not
  supplemented.
