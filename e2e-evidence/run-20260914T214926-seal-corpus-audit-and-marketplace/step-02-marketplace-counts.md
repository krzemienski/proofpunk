# Both marketplaces advertised 18 skills; the tree has 19
utc : 2026-09-14T21:49:26.240632Z

    skills with SKILL.md on disk        : 19
    .claude-plugin/marketplace.json     : "18 skills"
    .omp-plugin/marketplace.json        : "18 skills"

Every .md source was already correct and verify-counts.py passed at rc=0. The
drift survived because that gate walks `iter_md_files()` — it structurally
cannot see a .json file. A user reads the marketplace listing before anything
else, so it is the worst place to be wrong and the only place unguarded.

FIX: both catalogs corrected to 19 (JSON re-parsed to confirm validity), and
verify-counts.py gains check_marketplace_counts(), which compares every
`N skills` claim in both catalogs against the live tree count.

mutation_test verify-counts.py marketplace arm: baseline rc=0 -> named mutation
(restore "18 skills" in .claude-plugin/marketplace.json) -> mutated_rc=1 naming
the file and both numbers -> restored byte-identical -> rc=0.

All 14 gates rc=0, captured unpiped.
