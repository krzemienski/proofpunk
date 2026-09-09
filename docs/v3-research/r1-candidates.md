# r1 — Candidate evaluation: proving a write-effecting slash command

Scope: the single capability gap this run measured. Gauge 4 (L16) reports
4/6 because `/proofpunk:install` and `/proofpunk:verify` reach only
`playbook-recognition`. Evaluated against the repo's standing constraint:
**no new runtime dependencies** (stdlib Python 3 + POSIX shell only).

## The measured problem

`tools/sdk_probe.py:190-193` defines `_SLASH_PLAYBOOK_TOOLS` with:

```
disallowed_tools=["Bash", "Agent", "Task", "Write", "Edit", "NotebookEdit",
                  "Workflow", "ListAgents"]
```

`cmd_slash_install` and `cmd_slash_verify` both inherit it. The probe's own
`why` field previously described this as "SDK sessions here have no Write
tool" — that phrasing reads as a host limitation. It is not. It is a
deliberate harness design choice in this repo's own source.

Consequence: gauge 4 cannot exceed 4/6 **by construction of its own
probe**. The measurement is bounded by the instrument, not by the product.

This is the repo's own recurring defect class #1 from the archaeology —
*a harness that structurally cannot fail* — appearing here as its mirror:
a harness that structurally cannot pass.

## Candidates

### C1 — Grant Write/Edit to the existing playbook probes
Flip `disallowed_tools` for `cmd_slash_install` / `cmd_slash_verify`.

- **Pro:** smallest diff; no new probe names.
- **Con:** destroys the existing measurement. Today those probes prove
  *recognition without side effects* — a real property worth keeping. A
  probe that may write can no longer prove a playbook was recognised
  without touching disk.
- **Verdict: REJECTED.** Overwrites a passing signal to obtain a new one.

### C2 — Add write-enabled variant probes alongside the existing ones
New `cmd_slash_install_effects` / `cmd_slash_verify_effects`, each with a
fresh `--cwd` sandbox, an outside-marker canary, and a `--no-plugin`
control arm. Existing recognition probes untouched.

- **Pro:** preserves the current gate's meaning; adds a strictly new
  assertion level; control arm keeps it non-vacuous; stdlib only.
- **Con:** two more probes to maintain; sandbox lifecycle to manage.
- **Verdict: NOT ADOPTED — candidate only.** This memo is
  orchestrator-authored; an author cannot adopt its own proposal. The word
  "ADOPTED" appeared here before any independent review and was a
  self-approval defect, corrected after `ReviewSequencing` returned
  REJECT. Independent review found the premise itself wrong (an ambient
  MCP write channel, not a missing Write tool) and the schema hazardous
  (appending rows makes gauge 4 report 4/8, worse than 4/6). See
  `docs/proposals.md` P1 for the reviewed status and required changes.

### C3 — Drive the command through a real interactive host, captured by hand
Run the slash command in a live Claude Code / OpenCode session and capture
the resulting tree.

- **Pro:** highest fidelity — the actual end-user surface.
- **Con:** not reproducible in a gate; cannot be re-derived by an
  independent verifier from sealed artifacts; the repo's release contract
  requires machine-recomputable gauges.
- **Verdict: REJECTED as the gate mechanism.** Retained as a valid
  one-off confirmation, not as the measurement.

### C4 — Assert the playbook's steps by executing them in shell
What I attempted earlier this run.

- **Pro:** trivial to write.
- **Con:** proves the steps are executable, not that the *slash surface*
  executes them. It also produced a false marker-nesting finding traced to
  my driver, not the product. Substituting script execution for slash
  proof is exactly what the acceptance criterion forbids.
- **Verdict: REJECTED.** Recorded as a failed script-level attempt at
  `evidence/v3-release/l16-commands/run-20260907T213538Z-install-effects/`.

## Selected

**None selected.** C2 was the strongest candidate of the four, but
independent review rejected it as written:

- `ReviewSequencing` — **REJECT**: implementing now violates the run's own
  Phase 0-4 gate, and this memo self-approved before review.
- `ReviewProbeDesign` — ADOPT-WITH-CHANGES: the stated root cause is false
  at the framing level; `/proofpunk:install` already wrote a file through
  an ambient `mcp__filesystem__write_file` channel the harness neither
  controls nor observes.
- `RedTeamEffectProbe` — ADOPT-WITH-CHANGES, 12 bypass vectors; a
  filesystem delta does not establish that the playbook caused the write.
- `HardenProposalPlan` — ADOPT-WITH-CHANGES: the literal implementation
  makes gauge 4 report **4/8**, worse than today's 4/6.

Nothing is implemented from this memo. `docs/proposals.md` P1 carries the
reviewed status and the revised proof plan; P2 records the MCP
write-guard bypass that this review surfaced as a product defect.
