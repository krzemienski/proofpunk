## Prompt Rating — build-mood-ring (PROMPT.md v1)

Overall: **91/100 — production-ready**

| Dimension        | Score | Notes |
|------------------|-------|-------|
| Clarity          | 19/20 | Task is one sentence with the exact mood set enumerated; "filter links (plus 'All')" pins the UI contract. -1: "reject or default anything else" (<constraints>) leaves two valid behaviors — test expectations must pick one. |
| Specificity      | 14/15 | File-level touchpoints, ALTER TABLE for existing DBs, baseline test count stated. -1: mood emoji set given but label strings ("stoked" etc.) not mandated for the select options — minor rendering freedom. |
| Structure        | 15/15 | XML tags balanced (task/context/skills_to_activate/mcp_tools/constraints/output_contract/example/validation); each tag single-purpose. |
| Output contract  | 14/15 | Modified-files list + pytest exit 0 + gate verdicts with cited evidence paths. -1: no explicit format for the modified-files list (table vs bullets). |
| Edge-case cover  | 14/15 | Invalid mood, existing-DB migration, unauthenticated flow implied by Flaskr's login_required. -1: empty-database filter view (filter with zero matching posts) not called out. |
| Testability      | 10/10 | Success observable via HTTP/browser actions; example gives exact expected strings; validation clause forbids unexecuted PASS. |
| Token efficiency |  5/10 | ~430 tokens; context block duplicates brainstorm content an executor could read from the linked files. Acceptable for self-containment but noted. |

## Failure modes predicted

1. Executor picks "reject" while a test asserts "default" (ambiguity above) → contradiction.
2. Executor adds the emoji set to schema.sql but forgets the migration note for live DBs → runtime
   `sqlite3.OperationalError: no such column: mood` on existing instances.
3. Filter implemented as a separate route instead of a query param → "All" semantics drift.

## Test cases

1. register u1 → login → POST /create {title:"T1", body:"B", mood:"🔥"} → GET / contains "T1" and 🔥 adjacent.
2. Create posts with moods 🔥 and 😐 → GET /?mood=😐 contains the 😐 post and NOT the 🔥 post → GET / (no param) contains both.
3. POST /1/update changing mood 🔥→😢 → GET / shows 😢 for post 1.
4. POST /create {mood:"<script>alert(1)</script>"} → stored mood is not the script string (rejected or defaulted); GET / renders no alert markup.
5. GET /?mood=🦄 (not in set) → no crash; either empty list or ignored filter — behavior must be deterministic and tested.

## Top 3 fixes, ordered by impact

1. Pick ONE invalid-mood behavior (chosen: **default to '😐' and flash a notice**) — applied to plan phase 01.
2. State the filter mechanism explicitly (**query param `?mood=` on index**) — applied to plan phase 02.
3. Trim context block to pointers where executor has file access (deferred: self-containment preferred for this run).

## Re-measurement

Fixes 1–2 applied to the gated plan (.planning/phases/*). Prompt itself re-scored after
executor feedback would go here — v1 ships at 91/100.
