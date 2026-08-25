# Live inventory — what a session actually sees

Attempting end-user proof for the skill-count fix (#5) surfaced a bigger fact:
**none of this session's repo work is live on this machine.**

## Measured

Live session, asked to list its `proofpunk:` skills:

```
17 skills + 7 commands
  router `proofpunk`      : ABSENT
  command `proofpunk:cook`: PRESENT
  skill `functional-validation`: present (not in the repo's 18)
```

Installed plugin versions under
`~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/`:

```
1.10.0: 19 skills, 7 commands — router absent, cook present
1.10.1: 19 skills, 7 commands — router absent, cook present
```

The repo is v2.0.1: 18 skills, router present, no cook.

## What this means for the fix claims

The session's answer is **correct for what is installed**. The gap is that
v2.0.1 has never been published to the marketplace, so:

- **#5 (skill count 18)** is proven in the repo and in a clean-HOME install,
  but **cannot** be proven in a live session until v2.0.1 ships. Marked
  install-level, not end-user.
- The `proofpunk:cook` command a user can still invoke today comes from the
  installed v1.10.x, not from anything this session left behind.
- The `functional-validation` skill exists in v1.10.x and not in v2.0.1 — a
  removal that shipping will surface.

## Correction to an earlier claim

Earlier I attributed a stale duplicate doctrine injection to "another
marketplace copy" without identifying it. It is this: **two installed versions
(1.10.0 and 1.10.1) both registering hooks.** That is the duplicate, now
identified rather than hand-waved.

Not fixed here: publishing a release and pruning installed versions are both
operator decisions outside this repository.
