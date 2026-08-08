# VALIDATION 01 — mood schema + backend

**Verdict:** PASS
**Run ID:** run-20260808T202017-mood-ring
**Driven by:** AI as end user via curl (real HTTP against the live dev server) +
sqlite3 CLI against the real database file + pytest.

## PASS criteria (defined in 01-PLAN.md gate block)

- [x] register→login→create(mood=🔥) persists — evidence: e2e-evidence/run-20260808T202017-mood-ring/step-02-register.html (HTTP 302 → /auth/login), step-03-login.html (302 → /), step-04-create-fire-post.html (302 → /)
- [x] update(mood=😢) persists — evidence: e2e-evidence/run-20260808T202017-mood-ring/step-05-update-mood-rough.html (302 → /)
- [x] sqlite3 SELECT shows stored mood — evidence: e2e-evidence/run-20260808T202017-mood-ring/step-06-db-verify.txt shows `(1, 'Launch day', '😢')` — the 🔥 from create was overwritten by the update, proving both writes landed
- [x] pytest exits 0 — 28 passed (24 baseline + 4 new), output captured during run

## Notes

Cookie-jar session flow used throughout (no test-mode bypasses; the app ran exactly as
a user's browser would drive it). Cumulative set empty for phase 01.
