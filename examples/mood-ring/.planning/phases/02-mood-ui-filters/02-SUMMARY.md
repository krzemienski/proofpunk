# SUMMARY 02 — mood UI + filters

Done: index filters via `?mood=` (valid moods only; invalid ignored); mood emoji rendered
beside each post title; filter nav bar (All + 5 emoji, active state); empty-filter state
("No posts with this mood yet — write one!"); mood `<select>` on create/update with
current-mood preselect on update; flash "Mood not recognized — saved as 😐" when a provided
mood is invalid; filter-bar + select CSS matching the existing stylesheet. 4 new tests
(index shows mood / filter by mood / invalid param ignored / invalid-mood flash).

Deviations: absorbed phase-01 task 3 (passing `moods` to templates) as planned by the
recorded amendment. Tool note: the browser automation tools cannot option-click a native
`<select>`; per-mood form submissions were driven via real HTTP POSTs (identical bytes to
what the form sends), and the limitation is recorded in VALIDATION.md.
