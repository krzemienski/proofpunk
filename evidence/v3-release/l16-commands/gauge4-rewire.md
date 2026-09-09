# Gauge #4 rewired — from stale prose to a measured artifact

Measured: 2026-09-04 (UTC) | Repo HEAD: `40abc0b` (working tree dirty)

## The defect

`tools/gauge-report.py`'s gauge #4 did not measure anything. It opened the
Phase-3 baseline **prose** (`00-baseline/command-surface-map.md`), regex-matched
the phrase *"**zero** have a single artifact proving the full chain"*, and
hard-returned `("0/6", "UNMET")`.

That was truthful when written — nothing had been driven at the time. But it is
a **restatement of a document**, not a derivation from an artifact, so it could
never move regardless of what was subsequently proven. Had the regex stopped
matching (a prose edit), the gauge would have flipped to UNVERIFIED rather than
re-measuring.

This is the repo's own recurring defect class: a number read from prose instead
of derived from the thing it describes.

## What actually exists now

A real live-session run — `tools/verify-command-surface.py` driving
`tools/sdk_probe.py` — produced
`evidence/v3-release/l16-commands/command-surface-proof.json`
(`measured_at: 2026-09-04T15:34:08Z`), plus 12 on-disk `.log`/`.rc` sidecars,
one pair per command per arm.

Independently verified from the artifact **and** cross-checked against the
sidecar `.rc` files on disk (not just the JSON's own flags):

| command | reached level | plugin arm | control arm rc | vacuous? |
|---|---|---|---:|---|
| implement | **c** full-chain | pass (rc=0) | 1 | no |
| forge-prompt | **c** full-chain | pass (rc=0) | 1 | no |
| rate-prompt | **c** full-chain | pass (rc=0) | 1 | no |
| truth-audit | **c** full-chain | pass (rc=0) | 1 | no |
| verify | playbook-recognition | pass (rc=0) | 1 | no |
| install | playbook-recognition | pass (rc=0) | 1 | no |

All 6 plugin arms passed; **all 6 control (`--no-plugin`) arms failed**, which
is what makes the probes non-vacuous.

## The honest number is 4/6, not 6/6

`verify` and `install` are capped at **playbook-recognition** by their own
nature, not by a test shortfall:

- `install` is an in-session agent playbook with **no backing skill or script**
  (distinct from `tools/proofpunk-install.sh`), and SDK sessions here have no
  Write tool, so its file-merge step is unreachable.
- `verify` has no Activate-skill line and no flags.

Reporting 6/6 because "every plugin arm passed" would inflate the softer
plugin-arm-passed count into a full-chain claim. The gauge deliberately reports
**full-chain only**: **4/6**.

## The rewired gauge enforces two anti-vacuity rules

1. **Any command whose control arm PASSED forces the whole gauge to
   UNVERIFIED**, naming the offenders — a passing control means the plugin was
   not demonstrably what produced the result.
2. **Only `reached_level == "c"` counts.** Playbook-recognition commands are
   listed with their honest maximum and excluded from the numerator.

## Mutation proof — four arms

| Arm | Condition | Gauge #4 |
|---|---|---|
| 1 baseline | artifact as produced | `UNMET 4/6` |
| 2 | one command's control arm forced to `pass: true` | **`UNVERIFIED`** — vacuity caught |
| 3 | all six forced to `reached_level: c` | **`PASS 6/6`** — target reachable |
| 4 restored | original bytes rewritten | `UNMET 4/6` |

Restore is byte-identical (sha256 compared before/after in the same
evaluation).

Arm 3 matters: it proves 6/6 is *achievable*, so this is not a second
unsatisfiable gate. Arm 2 proves the vacuity guard is real, not decorative.

## Proof level

**End-user level for the 4 full-chain commands** — real Claude Code SDK
sessions, slash command typed, registration and expansion observed, mapped
skill invoked with a successful `ToolResult`, unique marker seen, and a control
arm that fails without the plugin.

**Playbook-recognition for `verify` and `install`** — slash registered and the
command-doc marker observed, but no backing skill/script executes. Stated as
their honest maximum, not counted as full-chain.

## Open

- Gauge #4 correctly remains **UNMET** and blocks release at 4/6 against a 6/6
  target. Whether 6/6 is the right target, given two commands cannot
  structurally reach full-chain in this environment, is a **decision for the
  operator** — it is not resolved here, and the gauge has not been quietly
  retargeted to make itself pass.
