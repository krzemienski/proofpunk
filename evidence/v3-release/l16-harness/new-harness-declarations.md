# L16 — the harness-integrity meta-gate caught two undeclared harnesses

Measured: 2026-09-04 (UTC) | Repo HEAD: `40abc0b` (working tree dirty)

## The gate did its job

Mid-session, `python3 tools/verify-harness-integrity.py` went from rc=0 to
**rc=2**:

```
[FAIL] verify-command-surface.py — add a `# PP-HARNESS-SUBJECT:` tag or a MANIFEST entry
[FAIL] verify-router-links.py — add a `# PP-HARNESS-SUBJECT:` tag or a MANIFEST entry
HARNESS INTEGRITY FAILS: 2
```

Cause: the L16 command-surface lane authored two **new** harnesses in `tools/`.
`HARNESS_NAME_RE` matches `verify-.*\.py`, so the meta-gate picked them up
immediately and refused to let an undeclared harness exist.

This is the meta-gate working exactly as designed. Its whole purpose is
retiring the `dry-run-install.sh` defect class — a harness that looks like it
covers a subject but never invokes it. A new harness that declares nothing
cannot be distinguished from that, so it fails closed.

## A method correction worth recording

The first tag I wrote used invented `kind=` values (`command-surface`,
`router-graph`). The gate rejected them precisely:

```
[FAIL] does NOT invoke its declared subject:
       - unknown declaration kind: command-surface
```

`kind` is not free text — it is a closed set read from
`tools/verify-harness-integrity.py:430-460`
(`shell_script_subjects`, `shell_file_subjects`, `python_file_level`,
`python_file_level_literal`). Both harnesses are Python that reference their
subject at file level, so `python_file_level` is the correct kind.

Note the near-miss: the run **immediately after** the bad tags still printed
`HARNESS INTEGRITY FAILS: 2`, which looks identical to "my edit did nothing."
It was not — the failure *reason* had changed from "undeclared" to "unknown
declaration kind." A count alone would have hidden that. The reason line is
what distinguished them.

## Final declarations

| Harness | Declared subject | Keywords |
|---|---|---|
| `verify-command-surface.py` | `sdk_probe.py` | `--no-plugin`, `full_chain` |
| `verify-router-links.py` | `SKILL.md` | `Skill calls`, `Shared doctrine` |

Both are honest: `verify-command-surface.py` genuinely drives `sdk_probe.py`
with a `--no-plugin` control arm and reports a `full_chain` count;
`verify-router-links.py` genuinely globs `SKILL.md` files and parses the
router's `## Skill calls` and `## Shared doctrine` tables.

## Mutation proof

| Arm | Action | rc | Result |
|---|---|---:|---|
| 1 baseline | tags correct | 0 | `HARNESS INTEGRITY FAILS: 0` |
| 2 mutated | `subjects=SKILL.md` -> `subjects=nonexistent-subject.md` in `verify-router-links.py` | 1 | `HARNESS INTEGRITY FAILS: 1` |
| 3 restored | original bytes rewritten | 0 | `HARNESS INTEGRITY FAILS: 0` |

Restore is byte-identical (sha256 compared before/after in the same
evaluation). The gate detects a false declaration, so the tag is not
decorative — it is checked against the harness's real source text.

## Proof level

**Script-level.** The real gate was executed across three arms with real exit
codes. Not end-user proven — no live host session was driven.
