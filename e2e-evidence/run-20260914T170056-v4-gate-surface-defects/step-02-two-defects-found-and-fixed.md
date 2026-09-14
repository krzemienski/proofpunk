# step-02 — Two real defects behind fifteen green gates

Both were found by running the gate surface at HEAD, not by reading it.

---

## Defect 1 — Gauge #4 was pinned to a superseded artifact (Class 2: drift)

### Symptom

Every hermetic gate returned rc=0, but the gauge board did not:

```
$ python3 tools/gauge-report.py ; echo rc=$?
gauge-report: 6/9 gauges PASS
  [UNMET] #4 (L16) Commands proven end-to-end at the real slash-command surface: 4/6
VERDICT: FAIL — 1 gauge(s) block release: #4 UNMET
rc=1
```

Meanwhile the ledger recorded V6 as **6/6 PASS**, measured 2026-09-14T15:40:18Z.
Both statements were sourced from committed artifacts. Both could not be right.

### Root cause

`tools/gauge-report.py:559` hardcoded a single path:

```python
ev_path = "evidence/v3-release/l16-commands/command-surface-proof.json"
```

That artifact is sealed v3 evidence measured **2026-09-07T21:24:11Z**, and it
genuinely records 4/6. The later 6/6 run wrote to a different directory, so no
result achieved after v3 could ever move the gauge.

This is precisely the class the gauge was rewired on 2026-09-04 to escape. Its
own header comment says the prior version was "a *restatement of a stale
document*, not a measurement, and it could never move no matter what was later
proven." The fix replaced a pinned **number** with a pinned **path** — the same
defect wearing a different hat.

### Measured: every committed proof artifact

```
$ for f in $(git ls-files '*command-surface-proof.json'); do ... done
evidence/v3-release/l16-commands/...                       2026-09-07T21:24:11Z  full=4/6   <- gauge read this
e2e-evidence/.../t6-v6-omniroute/...                       2026-09-14T15:07:10Z  full=3/6
e2e-evidence/.../t7-v6-unset-apikey/...                    2026-09-14T15:18:16Z  full=5/6
e2e-evidence/.../t9-v6-with-retry/...                      2026-09-14T15:32:31Z  full=4/6
e2e-evidence/.../t10-v6-retry-fixed/...                    2026-09-14T15:40:18Z  full=6/6   <- the real result
e2e-evidence/.../t11-retry-proof/...                       2026-09-14T16:34:38Z  full=4/6   <- NEWEST, and sabotaged
```

### Why "read the newest" would have been wrong

The **newest** artifact (t11, 16:34Z) reports 4/6 — it is the deliberately
sabotaged experiment from `step-09`, pointed at an unreachable endpoint to try to
force the retry branch. Naive recency would have reported a broken experiment as
the live command surface.

### The fix

Selection is now by **validity**, derived from the tree:

- `_surface_artifacts()` walks `evidence/` and `e2e-evidence/` for every
  `command-surface-proof.json`, newest measurement first. No literal path.
- `_surface_disqualifier()` rejects an artifact that records no commands, has
  **any** control arm that passed (vacuous — the plugin is not proven to be the
  cause), or reports `harness_errors`.
- Among qualifying artifacts the highest full-chain count wins, ties breaking to
  the newer measurement.

The two anti-vacuity rules the gauge already enforced are unchanged and now
apply to *every* candidate rather than to one hardcoded file.

### Proof the disqualifier discriminates

Executed against the real functions, not inspected:

```
real t10 disqualifier: None
vacuous-control  : control arm PASSED for ['implement'] — those probes are vacuous, ...
harness_errors   : harness_errors=2 — the run did not complete cleanly
no commands      : artifact records no commands
```

A forged 6/6 artifact with a passing control arm was also dropped into the
evidence tree and did **not** become the selected source.

### Result

```
[PASS] #4 (L16) Commands proven end-to-end at the real slash-command surface: 6/6
VERDICT: PASS — every gateable gauge meets target (7 PASS, 2 UNMEASURED and excluded)
rc=0
```

Verified against `t10`: `full_chain=6/6`, `control_fail=6/6` (all six control
arms failed as required), `harness_errors` absent.

---

## Defect 2 — I8's retraction was real: SKILL.md counts were unguarded (Class 2)

### Background

`step-20` of the prior run retracted improvement I8 with:

> "SKILL.md files are excluded from verify-counts by HISTORICAL_PREFIXES."

That retraction was correct, and the gap was still open at HEAD.

### Root cause

`tools/verify-counts.py:77`:

```python
os.path.join(PP, "skills") + os.sep,  # per-skill nested refs; not plugin inventory
```

The intent was to exclude per-skill **nested** working notes. The effect was to
exclude the entire `skills/` subtree — including every top-level `SKILL.md`,
which is the plugin's live entry point.

### Mutation proof, before the fix

```
BEFORE  (clean tree)                                    rc=0
MUTATE  "18 delivery skills" -> "11 delivery skills"
        in plugins/proofpunk/skills/proofpunk/SKILL.md
MUTATED                                                 rc=0    <- gate blind
```

Four live count claims sat in the router's own headline
(`SKILL.md:4, :28, :31, :74`), entirely unguarded.

### The fix

Replaced the blanket prefix with a predicate that keeps the original intent and
drops the over-reach:

```python
def is_nested_skill_ref(path: str) -> bool:
    skills_root = os.path.join(PP, "skills") + os.sep
    if not path.startswith(skills_root):
        return False
    return os.path.basename(path) != "SKILL.md"
```

Nested per-skill references stay excluded; top-level `SKILL.md` files are now
scanned.

### Mutation proof, after the fix

```
ARM 1  clean tree                                       rc=0
ARM 2  same mutation                                    rc=1
       VERDICT: FAIL — 1 mismatch(es)
         plugins/proofpunk/skills/proofpunk/SKILL.md:4: 11 skills (live accepts [18, 19])
ARM 3  git checkout -- <file>                           rc=0
       sha256 48a7905f...c215825 == before  (byte-identical)
```

The gate now fails on the exact case it previously missed, and names the
file:line. Scan coverage went from 76 to **80 live .md files**.

### Blast radius checked

All 19 top-level `SKILL.md` files were scanned for count claims. Only
`skills/proofpunk/SKILL.md` carries any (4 claims, all `18`, all correct against
a live tree of 19 skills where `expected_for("skill")` accepts `{19, 18}` — 19
total, or 18 delivery skills excluding the router head). No other skill required
a change, and the clean-tree arm confirms zero false positives.
