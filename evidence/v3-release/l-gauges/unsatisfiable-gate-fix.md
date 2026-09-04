# L-gauges — the release gate could never exit 0

Measured: 2026-09-04 (UTC) | Repo HEAD: `40abc0b` (working tree dirty)

## The defect

`tools/gauge-report.py:700-704` computed the release verdict as:

```python
if passing != total:
    print(f"VERDICT: FAIL — {total - passing}/{total} gauge(s) not PASS")
    sys.exit(1)
```

`passing` counts only `status == "PASS"`. `total` counts every gauge —
including rows deliberately marked **UNMEASURED**.

Two rows are permanently UNMEASURED by design (#8 median body size, #9
aggregate listing pressure). Neither has a numeric target in any sealed
source, and inventing one would be a fabricated number. So both are correctly
reported as measured-but-not-gated.

The consequence: `passing != total` was **always true**, so the tool could
only ever `sys.exit(1)`. The v3 release gate — "v3.0.0 ships only when every
gate exits 0" — was **unsatisfiable no matter how much real work was
completed**.

## Why this is the same class of defect the work order warns about

The work order's own rule: *"A gauge the red-team agent can satisfy without
doing the work is a failed gauge — redesigned, not accepted."* The inverse is
equally disqualifying: a gate that **cannot** be satisfied **by** doing the
work measures nothing about the work. It reports FAIL identically whether
every lane succeeded or every lane failed — the same "cannot fail / cannot
pass" shape as defect Class 1.

It also directly contradicted the repo's own written contract. Both the
gauge definitions in this file (#8, #9: *"does not gate release"*) and
`docs/v3-gauges.md` (*"reported for trend tracking only, does not gate
release"*) state UNMEASURED is excluded. Only the exit computation disagreed.

## The fix

Gate on what can actually be satisfied, and say so out loud:

- **UNMET** and **UNVERIFIED** block release, reported separately by number
  and status so an unresolved citation is never mistaken for a below-target
  measurement.
- **UNMEASURED** is excluded from the gate and announced explicitly on its own
  line, so exclusion is visible rather than silent.

## Mutation proof — four arms

| Arm | Condition | rc | Verdict |
|---|---|---:|---|
| 1 | current tree (#4 genuinely UNMET) | 1 | `FAIL — 1 gauge(s) block release: #4 UNMET` |
| 2 | UNMET temporarily removed from the blocking set | **0** | `PASS — every gateable gauge meets target (6 PASS, 2 UNMEASURED and excluded)` |
| 3 | every gauge forced to UNVERIFIED | 1 | `FAIL — 9 gauge(s) block release: #1 UNVERIFIED … #6 UNVERIFIED` |
| 4 | restored | 1 | `FAIL — 1 gauge(s) block release: #4 UNMET` |

Restore is byte-identical (sha256 compared before/after in the same
evaluation).

What each arm establishes:

- **Arm 2 is the load-bearing one**: it proves `rc=0` is *reachable at all*.
  Before this fix no arm could produce it. That is the exact property the
  release depends on.
- **Arm 3** proves the fix did not weaken the gate — an unresolvable evidence
  citation still blocks, which is the property that stops a gauge passing on
  evidence that does not exist.
- **Arm 1 == Arm 4** proves the change is otherwise inert on the real tree.

## Proof level

**Script-level.** The real tool was executed across four arms with real exit
codes captured separately from stdout. Not end-user proven — nothing here
drives a host session.

## Open

- Gauge **#4 remains genuinely UNMET** (0/6 commands proven end-to-end at the
  real slash surface). That is real outstanding work, not a gate artifact, and
  it correctly blocks release today.
