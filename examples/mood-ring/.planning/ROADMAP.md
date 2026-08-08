# ROADMAP — Mood Ring

| Phase | Increment (verifiable) | Depends on | Gate (proves done) |
|-------|------------------------|------------|---------------------|
| 01 mood-schema-backend | mood persists: create/edit store a validated mood; index query exposes it; migration path documented; tests added and green | — | driven HTTP flow: register→login→create(🔥)→edit(→😢); sqlite3 CLI shows stored values; pytest green |
| 02 mood-ui-filters | mood emoji visible per post; filter links filter via ?mood=; All clears; empty-filter state renders gracefully | 01 | driven browser/HTTP: each emoji filter returns only matching posts (counted); forged mood defaults; cumulative re-run of phase 01 gate |

Foundations before dependents: 02 renders what 01 stores. No shared mutable resources
between phases (sequential execution).
