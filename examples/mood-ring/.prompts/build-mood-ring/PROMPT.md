<task>
Implement the "Mood Ring" feature in the Flaskr blog (Flask 3.1 + SQLite + Jinja,
server-rendered, no JS): every post carries one mood from {😀 stoked, 🙂 good,
😐 meh, 😢 rough, 🔥 on-fire}; the index shows each post's mood emoji beside its
title and offers emoji filter links (plus "All") that filter the list by mood.
</task>

<context>
Approved design: .planning/brainstorm-mood-ring.md (Approach A — `mood` column on
`post`, default '😐'). Plan: .planning/ROADMAP.md with phases 01 (schema+backend)
and 02 (UI+filters). Touchpoints: flaskr/schema.sql, flaskr/blog.py,
flaskr/templates/blog/{index,create,update}.html, flaskr/static/style.css, tests/.
Baseline: 24 pytest cases green. Existing instances need: ALTER TABLE post ADD
COLUMN mood TEXT NOT NULL DEFAULT '😐'.
</context>

<skills_to_activate>
- cook — execute the two phases in order, honoring their validation gates
- functional-validation — drive the running app over HTTP as an end user
- evidence-gates — capture run-scoped fresh evidence and emit the verdict
</skills_to_activate>

<mcp_tools>
- shell / python3 (pytest, flask CLI, curl) — start the app, drive HTTP flows
- browser_* suite (visit/click/input/screenshot) — drive the UI as an end user
</mcp_tools>

<constraints>
- Prefer existing patterns: parameterized SQL only, Jinja `{{ }}` escaping, flash
  for errors, `required` attribute usage as in current forms.
- Validate mood server-side against the 5-value set; reject or default anything else.
- Keep all baseline tests green; add tests covering mood create/edit/filter/invalid.
- Aim for the smallest diff that satisfies the acceptance criteria.
</constraints>

<output_contract>
- Modified files listed with one-line rationale each
- `pytest` output (must exit 0)
- Gate verdicts per phase with cited evidence paths under e2e-evidence/run-*/
</output_contract>

<example>
Input: POST /create with form fields title="Launch day", body="We shipped",
mood="🔥" by an authenticated user.
Expected: 302 redirect to /; GET / then contains an article whose header shows
"Launch day" together with 🔥; clicking the 😐 filter yields a page NOT containing
"Launch day"; clicking "All" shows it again.
</example>

<validation>
Validate by actually operating the running system as the end user: drive real HTTP
requests and/or browser clicks (register, log in, create with each mood, click each
filter, edit a mood, forge an invalid mood). Never report success from code reading,
from test mocks, or from assumed behavior. Any criterion not actually executed is
reported UNVERIFIED. No mocks, no stubs, no test-mode bypasses — fix the real system.
</validation>
