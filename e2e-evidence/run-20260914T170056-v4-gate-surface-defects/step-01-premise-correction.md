# step-01 — The work order's premise was stale, and by how much

## What the work order asserted

> Repository reference: `krzemienski/proofpunk`, default branch `main`,
> HEAD `a41591a` (2026-09-01), language Shell, manifests at `2.2.0`.
> **18 skills**, **13 shared references**, **6 commands**,
> 7 hook event keys / 9 script registrations / 10 files.

It further instructed: run Phases 0–4 (discovery, session mining, documentation
canon, current-state analysis, proposals) **before** any improvement, because
those phases had not been done.

## What is actually true — measured, not restated

```
$ git log --format='%H %ad %s' --date=short -1
3b6a7f9cce6edc84cfb1ea4b3fcd598687f996a7 2026-09-14 wire shellcheck into CI so the injection class cannot return

$ jq -r '.version' plugins/proofpunk/package.json
4.0.0
```

HEAD is **`3b6a7f9`, not `a41591a`** — 13 days and +117 commits newer.
Manifests are at **4.0.0, not 2.2.0**.

| Count | Work order | Measured at HEAD |
|---|---|---|
| Skills | 18 | **19** |
| References | 13 | **18** |
| Commands (Claude) | 6 | **7** |
| Commands (OpenCode) | 6 | **7** |
| Hook event keys | 7 | 7 |
| Hook registrations | 9 | **12** |
| Hook `.sh` files | 10 | 10 |
| Tools | 10 | **28** |

Derived by `tools/verify-counts.py`, which computes each from the live tree:

```
canon: skills=19 refs=18 cmds=7+7 hooks.sh=10 events=7 regs=12 agents=3/4/3 edges=51 (router=18)
```

The work order's numbers are preserved here as the historical record they are.
They are not wrong *for `a41591a`*; they are wrong *for HEAD*. Per the standing
instruction — "Derive present-day counts from D6. Preserve conflicting
historical counts in the record, identify the conflict explicitly" — the
canonical inventory above governs, and the implementation is not bent to satisfy
the stale figures.

## Phases 0–4 were already complete

All five required artifacts exist and are committed:

| Artifact | Bytes |
|---|---|
| `docs/discovery-register.md` | 11142 |
| `docs/session-intent-ledger.md` | 28221 |
| `docs/commit-archaeology.md` | 33601 |
| `docs/skill-canon.md` | 41920 |
| `docs/proposals.md` | 15950 |

`.planning/execution-ledger.json` records this explicitly under
`run_2026-09-14`:

> `"work_order_premise": "STALE — described a41591a/v2.2.0; real HEAD was
> 63727e1/v4.0.0, +114 commits"`
> `"phases_0_4": "ALREADY COMPLETE before this run ...; resumed from ledger
> rather than re-mined"`

A prior session already hit this same stale work order and reconciled it. Re-mining
every session and re-deriving the canon would reproduce artifacts that already
exist, at real cost, and would not change a single downstream decision.

**Therefore this run resumes from the ledger** and spends its effort on the
items the ledger lists as still open — which is where the remaining defects
actually were.

## What this run did NOT do

- Did not re-run session mining (Phase 1). The ledger and the five artifacts
  are the recovered intent; re-deriving them is duplicated work, not verification.
- Did not re-pull the host documentation canon (Phase 2). `docs/skill-canon.md`
  is 41920 bytes and current as of 2026-09-14.
- Did not treat the stale counts as targets.
