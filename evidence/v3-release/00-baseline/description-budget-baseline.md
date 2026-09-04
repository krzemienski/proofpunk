# Description budget + C7 spec-basics baseline

Measured: 2026-09-04 (UTC) | Repo HEAD: `9963648` (working tree dirty)
Method: YAML frontmatter parsed per skill with `yaml.safe_load`; description
length measured on the **resolved** string (so folded `description: >` blocks
are measured as the loader sees them, not as raw lines).

## Result: 18/18 conform on every spec basic

| Check | Result |
|---|---|
| `name` matches parent directory | **18/18** |
| `description` ≤ 1024 chars | **18/18** (max 978, `implement`) |
| Unrecognized frontmatter fields | **none** across all 18 |

| Skill | desc chars | body bytes |
|---|---:|---:|
| brainstorm | 833 | 6266 |
| codebase-truth-audit | 759 | 14464 |
| end-user-testing | 838 | 9720 |
| full-functional-audit | 811 | 6411 |
| implement | **978** | 10690 |
| mobile-validation-runner | 727 | 5080 |
| plan-hardening | 745 | 5953 |
| production-readiness | 737 | 3593 |
| prompt-forge | 887 | 16199 |
| proofpunk (head) | **718** | 4729 |
| red-team-eval | 761 | 3209 |
| root-cause-debugging | 731 | 5048 |
| session-intent | 805 | 5396 |
| stack-testing | 746 | 5002 |
| tui-testing | 746 | 6824 |
| ui-experience-audit | 807 | 9030 |
| validation-plan | 648 | 5967 |
| visual-inspection | 672 | 6417 |

## Finding F-C7-1 — a work-order risk that does not exist

The work order flags the head's folded `description: >` block as "a genuine
risk" against the 1024 ceiling. **Refuted by measurement**: `proofpunk` has
the *shortest* description of all 18 (718 chars, 70% of ceiling). No skill is
within 46 chars of the limit. No remediation is needed, and none should be
proposed on this basis.

## Finding F-C7-2 — the real constraint is the aggregate, not the individual

Total description text across 18 skills: **13,949 chars**.
Claude Code's skill-listing budget: **1,536 chars**.

> **13,949 / 1,536 = 9.1× over budget.**

Every description conforms individually while the set cannot fit a listing
surface. Whatever the host does under pressure — truncate, drop, or rank —
is not controlled by this repo today, and nothing measures it. This is the
binding constraint for L10 (adaptive router), not the per-skill ceiling.

Consequence for L10: any rewrite that improves per-skill discrimination while
holding total length constant does not fix the aggregate problem. The gauge
must measure routing accuracy **under the real listing budget**, not in
isolation.

## Gauge baselines established

| Gauge | Metric | Baseline |
|---|---|---|
| #7 (L10) | Median skill body size (context economy proxy) | **6,266 bytes** |
| #7 (L10) | Total description chars vs 1,536 budget | **13,949 (9.1×)** |
| #13 (L12) | Skills passing spec basics (name/desc/fields) | **18/18** |

Note: gauge #13's full target is conformance against the complete Phase 2
per-host matrix, which is broader than these three basics. This measures the
spec-basic subset only; `docs/skill-canon.md` owns the full matrix.

## Open / UNRESOLVED

- Host behavior when the aggregate exceeds the listing budget (truncate vs
  drop vs rank) is **not measured here** — it requires driving a live host,
  not reading files. Carried to L10 / L14.
- Per-host recognized-field enforcement (OpenCode silently ignores unknown
  fields; other hosts may differ) is owned by `docs/skill-canon.md`.
