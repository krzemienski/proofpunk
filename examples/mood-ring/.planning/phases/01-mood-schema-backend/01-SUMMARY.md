# SUMMARY 01 — mood schema + backend

Done: schema.sql gained `mood TEXT NOT NULL DEFAULT '😐'` + ALTER TABLE migration comment
(for existing DBs; init-db drops data). blog.py gained `MOODS`, `DEFAULT_MOOD`,
`validate_mood`, mood in both SELECTs and in INSERT/UPDATE. 4 new tests
(create stores mood / invalid defaults / update changes mood / missing field defaults).

Deviations: PLAN task 3 (pass `moods` to templates) moved to phase 02 — amendment
recorded in 01-PLAN.md; shipping an unused template variable in 01 served no purpose.

Migration note for existing instances: `ALTER TABLE post ADD COLUMN mood TEXT NOT NULL DEFAULT '😐';`
