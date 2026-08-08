# PLAN 01 — mood schema + backend

**Objective**: a post's mood is stored, validated server-side, and returned by the index query.

## Tasks (owner surface)

1. `flaskr/schema.sql` — add `mood TEXT NOT NULL DEFAULT '😐'` to `post`; note the
   `ALTER TABLE post ADD COLUMN mood TEXT NOT NULL DEFAULT '😐';` migration for existing DBs
   (comment in schema.sql + MIGRATION note in this phase's SUMMARY).
2. `flaskr/blog.py` — module-level `MOODS = ["😀","🙂","😐","😢","🔥"]`; helper
   `validate_mood(value)` returning the value if in MOODS else "😐"; use it in `create` and
   `update`; extend both SELECTs and INSERT/UPDATE to carry mood.
3. ~~`flaskr/blog.py` — pass `moods=MOODS` to create/update template rendering.~~
   **Amendment (cook, phase 01)**: moved to phase 02 — passing `moods` to templates
   is only meaningful once the `<select>` exists; keeping it in 01 would ship a
   dead template variable. Reason recorded per gate discipline.
4. `tests/test_blog.py` — add: create stores mood; create with invalid mood stores "😐";
   update changes mood. (Tests drive the real app via the Flask test client — no mocks,
   per the Iron Rule.)

## Contracts

- `MOODS` is the single source of truth for the 5 values (phase 02 renders from it).
- Invalid mood behavior: **default to '😐'** (flash notice is phase 02's template concern;
  backend behavior is silent-default + tested).
- DB shape after phase: `post(..., mood TEXT NOT NULL DEFAULT '😐')`.

## Validation gate block

```yaml
evidence:
  assertion: "register→login→create(mood=🔥)→update(mood=😢) persists 😢; sqlite3 SELECT shows it; pytest exits 0"
  type: cli-output
  path_template: "e2e-evidence/run-<id>/step-NN-<action>.<ext>"
  min_size_bytes: 256
  covers_phases: []
  actor: ai-end-user
```

Gate actions are DRIVEN: the AI runs the dev server, issues real HTTP POSTs via curl
with a cookie jar, and queries the real SQLite file — never a code-read verdict.
