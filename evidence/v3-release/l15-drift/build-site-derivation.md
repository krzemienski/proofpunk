# L15 — `build-site.py` hardcoded skill count, derived

Measured: 2026-09-04 (UTC) | Repo HEAD: `40abc0b` (working tree dirty)
Closes: the ACTIVE GUIDANCE row for `tools/build-site.py:360` in
`evidence/v3-release/00-baseline/drift-inventory.md`.

## The defect

`tools/build-site.py:360` passed a **hardcoded** `"18 skills"` string into the
generated `index.html` page description, three lines below a `write()` call at
line 358 where `N_SKILLS` (computed at line 181 as `len(skills)` from a real
`glob` over `plugins/proofpunk/skills/*/`) was already in scope.

This is the repo's own recurring defect class: a literal that reproduces on
every regeneration, which is exactly how `/proofpunk:cook` survived its own
removal. Every other count on the page — 15 further uses of `N_SKILLS`, plus
`N_CMDS`, `N_REFS`, `N_THEMES`, `N_DOCS` — was already derived. This one string
was the outlier.

## The fix

One line, converting the literal to an f-string over the already-derived value:

```python
# before
"Proofpunk — … OpenCode. 18 skills where end-user testing is the only PASS.",
# after
f"Proofpunk — … OpenCode. {N_SKILLS} skills where end-user testing is the only PASS.",
```

Post-fix measurement: `src.count("18 skills")` in `tools/build-site.py` is now
**0**.

## Proof that the fix is behaviour-neutral

The generator was run before and after. `N_SKILLS` evaluates to 18 today, so a
correct derivation must produce **byte-identical** output for that string —
and it does: `docs/index.html`'s rendered description is unchanged.

`python3 tools/build-site.py` -> rc=0, printed `skills=18 cmds=6+6 refs=14
themes=20 docs=7 v2.2.0`.

## A separate, pre-existing drift this regeneration exposed

The regeneration changed 25 HTML files, which is more than a byte-neutral edit
can explain. Investigated rather than assumed:

`git diff docs/index.html` shows the **only** semantic change is `13 doctrine
refs` -> `14 doctrine refs`, in three places.

Cause: `plugins/proofpunk/references/` contains **14** files on disk
(`run-trace-schema.md` was added by the earlier v3 trace lane), but the
committed site was generated when there were 13 and was never regenerated.
`N_REFS` is derived, so the generator was correct both times — the *committed
artifact* was stale.

This is a real, separate instance of the same defect class (a generated
artifact drifting from its canonical source), and it is now corrected. It was
**not** introduced by this change: the diff is confined to a count this edit
does not touch.

## Proof level

**Script-level.** The generator runs rc=0 and the derived string is measured
absent from source. Not end-user proven: nothing here drives a browser against
the rendered page. Rendering correctness of `docs/*.html` remains ungated (see
`codebase-analysis.md:102`), and that gap is unchanged by this fix.
