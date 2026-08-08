# PLAN 02 — mood UI + filters

**Objective**: moods are visible on the index and the list is filterable by mood as an end user experiences it.

## Tasks (owner surface)

1. `flaskr/templates/blog/create.html` + `update.html` — `<select name="mood">` rendered from
   `moods`, preselecting the post's current mood on update.
2. `flaskr/blog.py` — `index` reads `request.args.get("mood")`; when it is a valid mood,
   add `WHERE p.mood = ?`; invalid/None → no filter. Pass `moods` + active `mood` to the template.
3. `flaskr/templates/blog/index.html` — mood emoji beside each post title; filter bar of emoji
   links (`?mood=<emoji>`) + an "All" link (`/`); active filter visually marked; empty result
   renders a friendly "no posts with this mood yet" line.
4. `flaskr/static/style.css` — minimal styling for the filter bar and active state, matching
   the existing stylesheet's look.
5. `tests/test_blog.py` — add: index shows mood emoji; `?mood=😢` filters; `?mood=🦄` does not
   error and does not filter (or filters-to-empty — assert whichever behavior is implemented,
   per the contract below).

## Contracts

- Filter mechanism: **query param `?mood=` on `/`** only (RATING fix 2). Invalid `?mood=` values
  are ignored (no filter applied) — deterministic, tested.
- Flash notice on defaulted mood: one `flash("Mood not recognized — saved as 😐")` in create/update
  when `validate_mood` had to default.

## Validation gate block

```yaml
evidence:
  assertion: "each emoji filter returns only posts of that mood (counted); All returns all; invalid ?mood= does not 500; forged POST mood defaults to 😐; phase-01 gate still green"
  type: api-response
  path_template: "e2e-evidence/run-<id>/step-NN-<action>.<ext>"
  min_size_bytes: 256
  covers_phases: ["01-mood-schema-backend"]
  actor: ai-end-user
```

Gate actions are DRIVEN: the AI clicks/types via the browser_* tools (or curl where a browser
cannot reach localhost — recorded honestly either way) and captures every response to the
run-scoped evidence dir.
