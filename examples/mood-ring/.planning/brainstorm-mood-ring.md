# Brainstorm — "Mood Ring" for Flaskr

Skill: `brainstorm` (truth-forge). Gates honored: scout-first ✓, exact-requirements ✓,
present-before-asking ✓ (options below), no implementation before approval ✓ (cook comes later).

## Codebase-context summary (scout findings)

- Flask tutorial blog ("Flaskr"): Flask 3.1 + SQLite + Jinja, no JS framework.
- `flaskr/schema.sql`: two tables — `user(id, username, password)`, `post(id, author_id, created, title, body)`.
- `flaskr/blog.py`: 4 routes — `index` (list, joins user), `create` (GET/POST form), `update`, `delete`.
- Templates: `base.html` (nav + flash), `blog/index.html` (post loop), `blog/create.html`, `blog/update.html` (forms with `required` on title only).
- `tests/`: 24 pytest cases, all green at baseline (verified 2026-08-09, `24 passed in 0.96s`).
- Conventions: parameterized SQL via `db.execute(?, ...)`; server-side render; flash messages for errors.

## Problem statement

Posts all look the same — a wall of undifferentiated text. There is no at-a-glance
signal of how a post feels, and no way to see only posts of one vibe.

## Exact requirements

1. **Expected output**: posts carry one of 5 moods (😀 stoked / 🙂 good / 😐 meh / 😢 rough / 🔥 on-fire);
   the mood emoji renders next to each post title on the index; emoji filter links above the post list
   show only posts of that mood; "All" clears the filter.
2. **Acceptance criteria** (end-user-executable, per end-user-actor.md):
   - Agent registers a user, logs in, creates a post choosing 🔥 → index shows the post with 🔥 beside its title.
   - Agent clicks the 😐 filter link → only 😐 posts render; clicks "All" → every post renders again.
   - Agent edits a post and changes its mood → index reflects the new mood.
   - `python3 -m pytest tests/` stays green (baseline 24 + new cases).
3. **Scope boundary**: OUT — per-user mood *analytics*, mood on comments (no comments exist), emoji pickers
   beyond a `<select>`, any JS framework, any API endpoint.
4. **Constraints**: keep parameterized SQL; server-rendered Jinja only; match existing template/CSS patterns;
   existing test suite must keep passing; SQLite stays.
5. **Touchpoints**: `schema.sql`, `blog.py` (index/create/update + get_post), `blog/index.html`,
   `blog/create.html`, `blog/update.html`, `static/style.css`, `tests/`.

## Approaches

**A. Column on `post` (recommended)** — add `mood TEXT NOT NULL DEFAULT '😐'`; filter via `WHERE mood = ?`.
Pros: matches existing patterns exactly; trivially testable; one schema touch. Cons: moods hard-coded in one
place (acceptable — 5 values, YAGNI on a mood table).

**B. Separate `mood` lookup table + FK** — pros: referential purity, rename moods centrally. Cons: joins for a
5-value enum; migration ceremony; violates KISS for this scale.

**C. Hashtag-in-body parsing** — parse `#mood:fire` from body text. Pros: zero schema change. Cons: invisible
data, fragile parsing, users must learn syntax — brutal honesty: this is a gimmick, not a feature.

**Recommendation: A.** It is the only option whose acceptance criteria are all directly observable in the
rendered page with the least machinery.

## Risks / implementation considerations

- Existing databases (already-initialized Flaskr instances) lack the column → need an `ALTER TABLE` migration
  note alongside the `schema.sql` change, or `init-db` destroys data (it does — `DROP TABLE`).
- Mood must be validated server-side against the allowed set (hostile form input otherwise lands in the DB
  and renders raw — Jinja escapes it, but garbage moods break filtering semantics).
- Filter links must preserve "no mood = no filter" behavior for the default view.

## Success metrics / validation criteria (each AI-executed as end user)

- C1: driven browser/HTTP flow register → login → create(🔥) → index contains 🔥 adjacent to the new title.
- C2: driven click of each emoji filter → response contains only posts of that mood (counted).
- C3: driven edit changing mood 🔥→😢 → index shows 😢 for that post.
- C4: `pytest` run exits 0 with ≥ baseline count of tests.
- C5: submitting mood `<script>alert(1)</script>` via a forged POST → stored value rejected (falls back to
  default or 400), page renders no script element.

## Next steps

Hand off to `validation-plan` (2 phases: 01 schema+backend, 02 UI+filters), then `plan-hardening`,
then `cook` executes.
