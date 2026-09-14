# step-02 — Corrections to step-01, and the prose-form drift it left ungated

Six advisories landed against `step-01` and the commit that shipped it
(`d2cfac1`). Five were correct and are acted on here. Recording them rather than
quietly folding the fixes in, because two of them correct **claims I made**, not
just code.

---

## Correction 1 — I overstated delegation as "working"

`step-01` said "Delegation is working." That was wrong, and the advisory naming
it was right: both file-based probes returned job status **`failed (exit 1)`**
with `SYSTEM WARNING: Subagent called yield with null data`. Execution worked;
the return channel did not.

But "half-working" was not the whole story either, because the three real audits
in the same session (`DocDriftAudit`, `V6RetryProof`, `BashBypassAudit`) all
returned **`completed`** with full payloads. So the break was not universal, and
neither claim — "working" nor "broken" — was measured.

### Measured, with a discriminating probe

Hypothesis: a very short single-line final message fails to serialize; a longer
structured payload succeeds.

`YieldChannelProbe` was given a read-only task, **forbidden from writing any
file** so no disk artifact could confound the result, and required to return a
multi-line structured answer.

```
status: completed   duration: 28.4s
{
  "answer": "COUNT: 18\nFIRST_FIVE:\n- api-validation.md\n- ci-gates.md\n- cli-validation.md\n- defect-pattern-database.md\n- docs-acquisition.md\nCHANNEL: multi-line payload returned"
}
```

| Payload shape | Job status | Data returned |
|---|---|---|
| single short line (`PROBE_ALIVE 19`) ×2 | **failed** | null |
| multi-line structured ×4 (3 audits + this probe) | **completed** | full |

**Corrected statement:** delegation executes correctly and returns structured
payloads reliably; a single-short-line yield payload does not serialize and
surfaces as `failed`. The practical rule, applied for the rest of this session:
require structured multi-line output from subagents, and treat a lone short line
as a harness limitation rather than a task failure.

---

## Correction 2 — `d2cfac1` shipped an incomplete drift fix

An advisory found two live prose drifts I had **verified and then not fixed**:

| File:line | Wrong | Live |
|---|---|---|
| `architecture.md:109` | "Its `## Skill calls` table has **17** rows" | **18** |
| `architecture.md:117` | "**15** rows, one per file in `references/`" | **18** |

Both verified against source before editing:

```
Skill calls rows: 18
Shared doctrine table lines: 20  ->  data rows: 18
references/*.md on disk: 18
```

A first attempt to count the doctrine rows returned **0** — a vacuous regex that
matched nothing. Recorded because that is the third time this session a
measurement instrument gave a confident wrong reading (see `step-04` of the
prior run).

Three more of the same shape were then found in `plugins/proofpunk/AGENTS.md`:

| Line | Wrong | Live |
|---|---|---|
| 27 | "calls all **17** others" | **18** |
| 28 | "**6** slash commands" (list omitted `acquire`) | **7** |
| 31 | "**15** shared doctrine files" | **18** |

Verified: `ls commands/` shows 7 including `acquire.md`; `ls references/` shows
18 including `enforcement-map.md` and `subagent-aware-stop.md`, both of which the
prose list was missing.

---

## The gate gap this exposes, and why the obvious fix was rejected

`d2cfac1` closed **table-cell** drift. It could not see any of the five above,
because they are prose: the number and its noun are separated by words, or the
noun is absent entirely ("calls all 17 others", "17 rows").

### The general rule was measured and REJECTED

An advisory warned that widening the gate would fire on historical report
tables. I tested that directly with a permissive "number within three words of a
count noun" rule:

```
--- PROSE: 4 hits ---
   CHANGELOG.md:59: '18 files are hook' live=[7, 10, 12]        <- FALSE (4-of-18 references, dated entry)
   README.md:396: '3 unknown skill' live=[18, 19]               <- FALSE (an error-code sentence)
   plugins/proofpunk/AGENTS.md:28: '6 slash commands'           <- REAL
   .../digests/docs-claude.md:293: '4 are all skills'           <- FALSE (unrelated prose)
```

**Three false positives out of four hits.** A count checker that cries wolf gets
muted, and then the real check is gone — the same reasoning already recorded in
this file's own `CLAIM_RE` comment about a general `\w+` gap.

### Three narrow rules instead

Each requires a token that only appears when the plugin's own inventory is being
described:

1. `PROSE_INVENTORY_RE` — `<n> <qualifier> <noun>` where the qualifier is from a
   closed set (`slash`, `shared`, `shared doctrine`, `other`, `delivery`).
2. `ROUTER_EDGE_RE` — `calls all <n> others` / `hands off to <n>`, the router's
   edge count, which has no noun beside the number at all.
3. `TABLE_ROWS_RE` + cues — `<n> rows` only when the line or the one before it
   names the Skill-calls or Shared-doctrine table, so an unrelated "8 rows"
   cannot trigger it.

### Mutation proof — both arms, as the advisory required

Stash scoped to the three doc files so the tool fix stayed in place; otherwise
Arm 2 runs the old gate and proves nothing.

| Arm | Condition | rc | Output |
|---|---|---|---|
| 1 | current tree | **0** | `VERDICT: PASS` — **zero new fails**, no false positive on any historical table |
| 2 | docs stale, tool fix retained | **1** | `VERDICT: FAIL — 5 mismatch(es)`:<br>`AGENTS.md:27: router edge claim 'calls all 17 others' (live router routes to 18)`<br>`AGENTS.md:28: prose '6 slash commands' (live accepts [7, 14])`<br>`AGENTS.md:31: prose '15 shared doctrine files' (live accepts [18])`<br>`architecture.md:109: '17 rows' for the Skill calls table (live 18)`<br>`architecture.md:117: '15 rows' for the Shared doctrine table (live 18)` |
| 3 | restored | **0** | `VERDICT: PASS` |

**All five hand-fixed drifts are gated.** An earlier draft of this file listed
`AGENTS.md:31` among the fixes while Arm 2 named only four — implying coverage
that had not been measured. An advisory caught it. `files?` was then added to
`PROSE_INVENTORY_RE`'s noun group, but only because the qualifier is mandatory:
the rule reaches it solely as `<n> shared [doctrine] files`, a bare `<n> files`
never matches, and the addition was measured at **0 hits across the live tree**
before being adopted. Arm 2 then moved 4 -> 5 and named `:31` explicitly.

Arm 1 is the one the advisory specifically asked for: widening the gate must not
light up the historical report tables whose supersession marker sits in a
heading rather than on each row. It does not.

---

## Advisories acted on, and the one declined

| Advisory | Disposition |
|---|---|
| `architecture.md:27` "other 17" | **Fixed** in `d2cfac1` (was already caught in that pass) |
| `architecture.md:109/117` prose drift still live | **Fixed here** |
| Table rule will false-positive on historical tables | **Tested** — general rule rejected on measurement; narrow rules verified clean (Arm 1) |
| Prose-form drift remains ungated | **Closed** with the three rules above |
| Mislabelled snapshot: BashBypassAudit payload showed V6 content | **Confirmed** — the hub snapshot rendered V6RetryProof's payload under the BashBypassAudit heading. The Bash findings in `step-01` were taken from `agent://BashBypassAudit`'s own report, and the two corrections they drove (`bash-write-notice.sh:18` content-hashing claim; `Write\|Edit only` wording) were each **independently verified against source** before editing — `bash-write-snapshot.sh:111` for the stat signature, `hooks.json:40` for the matcher. |
| Reword line 233 as "Write/Edit/MCP write-family" | **Already shipped** in `d2cfac1` as "Write, Edit and MCP mutation tools - not on Bash" |
| `PROOFPUNK_TEST_TRANSIENT_ONCE` fault-injection seam | **DECLINED.** It is a test-mode bypass in the harness, directly against this repo's no-test-mode-bypasses doctrine. The retry loop stays **UNVERIFIED**: predicate proven by a 10-shape execution matrix, `attempt1 -> attempt2` transition never observed. That is the honest outcome and it is not being engineered around. |

---

## Evidence-handling correction

The immutability gate caught me re-sealing an inventory already committed at
`449dbbe` (`REWRITTEN 744B -> 864B`). An advisory correctly noted that
`git checkout --` on a run's own manifest would make it a **false manifest** if
the run still contained unlisted files.

Resolution chosen, stated explicitly rather than done silently: the new step and
its gate logs were moved into **this** fresh run directory, and
`run-20260914T170056-v4-gate-surface-defects` was restored to byte-identical
with its commit — verified empty `git status` for that path. Nothing was
exempted from the gate.

`gates-round2/` (30 files) and `gates-round3/` (30 files) both live in this run
and are covered by this run's seal.

## Gates

15/15 rc=0 after these changes, each unpiped with rc captured separately.
Logs: `gates-round3/`.
