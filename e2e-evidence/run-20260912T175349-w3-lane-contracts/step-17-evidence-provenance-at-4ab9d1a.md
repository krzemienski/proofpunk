# Which criteria rest on which commit — provenance, stated exactly

HEAD is now 4ab9d1a. Several criteria cite runs
captured BEFORE it. That is not automatically wrong — a criterion about
installer idempotency does not become false because a later commit
edited a status report — but the claim 'every PASS cites an archive of
HEAD' was too broad, and this artifact replaces it with the real map.

## Commit each PASS was actually captured against

| Criterion | Evidence captured at | Does later work affect it? |
|---|---|---|
| P1 installer defects | a2fdeb9 (pre-fix tree) | No. The 8 hostile conditions exercise tools/proofpunk-install.sh, untouched by every commit since. |
| P2 complete surface | a2fdeb9 | No. Same installer, same skills/hooks counts — and step-15 re-confirms 18 skills / 10 hooks in an archive of HEAD. |
| P3 citations resolve | c2e4734 archive | Current. |
| P4 idempotency | a2fdeb9 | No. Installer unchanged since. |
| P12 counts accurate | c2e4734 archive | Current. |
| P13 harnesses pass | c2e4734 archive | Current. |
| P14 sealed run | seals predate 4ab9d1a | See below. |

## Verifying the 'installer unchanged' claim rather than asserting it
```
$ git log --oneline a2fdeb9..HEAD -- tools/proofpunk-install.sh
(empty = the installer has not changed since P1/P2/P4 were captured)

$ git log --oneline a2fdeb9..HEAD -- plugins/proofpunk/skills plugins/proofpunk/hooks
ba16393 Add --run targeting to fresh_evidence; make its parser strict
c169831 Fix: fresh_evidence validate under-enforced its own min-size rule
adcee4b Fix: deny-capable hooks lost enforcement silently without python3
```
The hooks and one skill script DID change after P1/P2/P4 were taken.
Neither affects those three criteria — P1 drives installer failure
modes, P2 counts installed surface, P4 diffs settings.json — and
step-15 re-confirms the surface counts from an archive of HEAD.
Stated so a reader can check the reasoning rather than accept it.

## P14: the seal problem, stated plainly
P14 asks for an evidence run sealed via the real fresh_evidence.py.
This run has been sealed repeatedly, but every seal necessarily
precedes the artifact written after it — including this one. A run
cannot contain a sealed inventory that covers its own last artifact
unless sealing is the final act.

So this is the final artifact. The seal that follows it covers every
step including this one, and nothing is appended afterwards.

## Current gate state at HEAD, for the record
  python3 tools/verify-counts.py           rc=0
  python3 tools/verify-citations.py        rc=0
  python3 tools/verify-orchestration.py    rc=0
  python3 tools/verify-lane-contracts.py   rc=0

## What remains UNVERIFIED, unchanged
  P5  router links 17 — inherited, not re-driven
  P6  router routes live — verify-command-surface.py never completed
  P7  >=10 improvements — 11 or 8 depending on classification
  P8  per-item proof — none for the v4 window's own commits
  P10 precedence map — not produced
  P11 skill prose correctness — THE blocker; not done

## A correction inside this artifact

The second git log above was originally captured with `| head -5`. This
repo's doctrine says never pipe a command whose exit code is reported
(.planning/plugin-improvement-criteria.md:40). The output was
informational rather than a reported rc, so nothing here was wrong --
but a rule applied only where it is convenient is not a rule, and the
command listed exactly three commits anyway, so the pipe bought nothing.
Re-run unpiped, the output is identical and complete.
