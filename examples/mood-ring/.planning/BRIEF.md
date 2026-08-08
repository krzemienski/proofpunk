# BRIEF — Mood Ring for Flaskr

- **Problem**: posts are visually undifferentiated; no vibe signal, no vibe filtering.
  Evidence: `blog/index.html` renders only title/author/date/body; `schema.sql` has no mood storage.
- **Expected output**: `post.mood` (5-value set, default 😐) persisted; index renders mood emoji per post;
  emoji filter links (😀🙂😐😢🔥 + All) filter the list via `GET /?mood=<emoji>`; create/update forms
  include a mood `<select>`.
- **Acceptance criteria**: brainstorm C1–C5 (driven end-user flows + green pytest).
- **Scope boundary**: no analytics, no comments, no JS framework, no API endpoints.
- **Non-negotiable constraints**: parameterized SQL; Jinja escaping; existing 24 tests stay green;
  invalid moods default to 😐 + flash (decision from RATING fix 1); filter is `?mood=` query param on
  index (RATING fix 2); existing SQLite instances migrate via `ALTER TABLE post ADD COLUMN mood TEXT
  NOT NULL DEFAULT '😐'`.
- **Touchpoints**: schema.sql, blog.py, blog/{index,create,update}.html, static/style.css, tests/test_blog.py.
