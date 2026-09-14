# `--dir <custom>` still wedged after the first fix
utc : 2026-09-14T21:11:20.438228Z
HEAD: 18b2088

An advisory caught a real hole in 18b2088: the candidate list I added cannot
cover `--dir <custom>` (proofpunk-install.sh:155), because no fixed list can
guess an arbitrary path. Reproduced, not assumed:

    --dir $HOME/somewhere/else/skills --hooks
    helper at custom dir : True
    decision             : block
    "the intent-verification helper is missing"
    looked at            : ~/.proofpunk/skills/...     <- wrong, as before

FIX — record the truth at install time instead of guessing
  proofpunk-install.sh now writes the resolved $DIR to
  ~/.proofpunk/skills-dir during a --hooks install (dry-run only says so).
  stop-guard.sh probes, in precedence order:
    1. $PROOFPUNK_SKILLS_DIR      (operator override)
    2. ~/.proofpunk/skills-dir    (what the installer actually did)
    3. hookdir/../skills, CLAUDE_PLUGIN_ROOT, ~/.claude/skills, omp,
       agents, opencode                                (fallbacks)

GATE — extended to two layouts, because they fail for different reasons
  -- default --dir (platform skills dir)  OK, reached intent branch
  -- custom --dir (unguessable path)      OK, reached intent branch

mutation_test verify-hook-helper-resolution.py custom-dir arm: baseline rc=0 ->
named mutation (recorded-dir probe deleted) -> mutated_rc=1 -> restored
byte-identical (sha256 verified) -> rc=0.

The mutation is precisely discriminating: with only the recorded-dir probe
removed, the DEFAULT arm still passes and ONLY the custom-dir arm fails. The
new coverage is real, not incidental.

All 14 gates rc=0, captured unpiped.
