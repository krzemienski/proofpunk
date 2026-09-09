# r2 — Patterns: what makes an effect-probe non-vacuous

Prior art consulted from this repo's own record, since it has already
produced and corrected each failure mode below.

## Pattern 1 — Control arm is mandatory, not optional

`sdk_probe.py --no-plugin` exists because a probe that only ever passes
proves nothing. Measured this run: the `router` probe returned
`plugin_loaded: True, tools_used: ['Skill']` with the plugin, and
`plugin_loaded: False, rc=1` without it. That delta is the proof; the
rc=0 alone is not.

**Applies to C2:** every new effect probe ships its control arm in the
same commit, and the arm must fail for the right reason (no plugin), not
by crashing.

## Pattern 2 — Canary the region you are NOT supposed to touch

`install.md` promises "nothing outside the markers was edited." A probe
that only asserts the marked block appeared cannot detect a playbook that
clobbered surrounding user content.

**Applies to C2:** the sandbox seeds a unique user line before invocation
and asserts it survives byte-identically after. This repo already lost a
claim to exactly this gap (`--override` needed a canary file to prove
replacement actually happened, `test-installer.sh` group 3).

## Pattern 3 — Fresh sandbox per arm, never the working tree

The `cmd_slash_install` probe defaulted to `/private/tmp`. Harmless here
(verified: repo tracked-file count unchanged), but a write-enabled probe
pointed at a real tree can silently mutate user work.

**Applies to C2:** `--cwd` into `mktemp -d` per arm, asserted non-empty
and outside the repo before the session starts. No credentials copied in
— that error is documented twice in this repo's history.

## Pattern 4 — Distinguish "did not run" from "ran and did nothing"

A playbook that recognises the command, then stops before writing, is
indistinguishable from one that wrote nothing — unless the probe records
*why*. The current `cmd_slash_install` log says "Detection complete.
Stopping before write," which is only legible because the session narrated
it.

**Applies to C2:** the probe asserts on the filesystem delta, not on the
model's narration. Absence of the expected file is FAIL, never "the model
explained itself."

## Pattern 5 — Additive gauges, never redefined ones

Gauge 7 in this repo was already redesigned once after its target was
found unsatisfiable (`gauge7-defect-analysis.md`). The correction was
documented rather than silently re-targeted.

**Applies to C2:** the new probes add a *level*, they do not restate
gauge 4's target downward. Gauge 4 stays 6/6-targeted; the effect probes
are how the remaining 2 become reachable, not an excuse to lower the bar.

## Pattern 6 — Mutation-prove the new gate before trusting it

Every gate added this run was mutation-proven: break it, watch it fail by
name, restore byte-identically.

**Applies to C2:** neuter the effect assertion, confirm the probe flips to
FAIL naming the specific command, restore and confirm byte-identical.
