# Ten Improvements — measured, not asserted

Every row below came from walking the real tree this session (six scout
subagents across skills, hooks, installer, and the command/manifest
surface) and from reproducing each defect against the real installer
before changing a line. No item here is a guess about what "could be
better"; each names a defect that was observed, the measurement that
proves it, and the threshold that decides success.

The organising discovery: **all three published gates were green while the
installer was broken.** That is the shape of every problem below — the
measuring instrument agreed with itself and disagreed with reality.

---

## 1. Give the installer an actual harness  (CRITICAL)

`tools/AGENTS.md:16` called `dry-run-install.sh` the "Installer dry-run
harness — run before any installer change." It never invokes
`tools/proofpunk-install.sh`. It exercises the `/proofpunk:install`
slash-command template merge — a different artifact entirely.

- **Before-arm**: `grep -c proofpunk-install tools/dry-run-install.sh` → `0`
- **Fix**: add `tools/test-installer.sh`, which runs the real installer;
  correct the `AGENTS.md` row so neither file is mislabelled.
- **Measure**: the harness invokes the installer by path and asserts on
  exit codes plus real filesystem state.
- **Threshold**: a deliberately malformed skill makes the harness FAIL.
  A harness that cannot fail is not a harness.

## 2. Stop the verifier certifying broken skills  (HIGH)

`proofpunk-install.sh:621-623` printed `✓ $skill (frontmatter only …)`
without performing any check when `python3` was absent.

- **Before-arm**: the **pristine committed installer** (`git show
  e890bc5:tools/proofpunk-install.sh` — syntax-valid, not regex-edited)
  installing a `SKILL.md` with no frontmatter at all, `python3` absent:
  `rc=0`, printing `✓ brainstorm` and `all skills pass`. Unpiped.
  (`e2e-evidence/run-20260827T161126-verify-arm-gitorig/verdict.json`)
- **Fix**: validate in plain shell on that branch — first line `---`,
  plus `name:` and `description:` — and set `FAIL=1` on violation.
- **Measure**: install the same malformed skill again.
- **Threshold**: non-zero exit and a `✗` line naming the skill.

## 3. Make `--ref` reach tags and commits  (HIGH)

`REPO_TARBALL` hardcoded `…/tar.gz/refs/heads` (line 38), so every `--ref`
resolved as a branch — while `--help` and `INSTALL.md:162` advertised
tags, using `--ref v1.8.0` as the documented example.

- **Before-arm** (differential, both arms unpiped): the original `v2.0.1`
  capture proved nothing — that tag does not exist upstream, so it 404s
  under old *and* new code. Replaced with a **real commit SHA**
  (`e890bc52…`) driven against both versions of the installer:

  | Arm | rc | installed |
  |-----|----|-----------|
  | old code (`refs/heads` hardcoded, single curl) | **1** | no |
  | new code (3-form fallback) | **0** | yes |

  `e2e-evidence/run-20260827T162405-ref-differential-pristine/verdict.json`
- **Fix**: try `refs/heads/$REF`, then `refs/tags/$REF`, then bare `$REF`.
- **Measure**: install pinned to a branch, a bare SHA, and a tag.
- **Threshold**: exit 0 with skills present for each form.
- **Result**: all three forms **PASS**. Branch and bare SHA were proven
  differentially (`e2e-evidence/run-20260827T162405-ref-differential-pristine/verdict.json`). The `refs/tags/` arm was **UNVERIFIED at the
  time of the fix** — upstream had zero tags to drive — and was reported as
  such rather than assumed. Cutting the `v2.1.0` release tag made it
  drivable: `--ref v2.1.0` resolves and installs, rc=0, unpiped
  (`e2e-evidence/run-20260827T163500-ref-tag-arm/verdict.json`). Unknown refs still fail honestly with rc=1.

## 4. Never leave hooks half-registered  (HIGH)

`--hooks` copies and `chmod +x`s the hook scripts, then calls bare
`python3` to merge `settings.json`. Without `python3` the files land
executable but unregistered — enforcement silently does not exist, which
is the worst failure mode in a plugin whose entire value is enforcement.

- **Before-arm** (measured, worse than first described): with `python3`
  off `PATH`, five hook scripts landed in `~/.proofpunk/hooks/`,
  `settings.json` was never created, `python3: command not found` printed
  raw — and the installer still **exited 0**. The user is told the
  install succeeded while enforcement does not exist.
  `e2e-evidence/run-20260827T141645-installer-defects-before/step-05-hooks-without-python3.txt`
- **Measure**: run `--hooks` with `python3` off `PATH`.
- **Threshold**: non-zero exit, failing *before* writing anything, naming
  the dependency.

## 5. Check `tar` for local installs too  (HIGH)

The `curl`/`tar` guard sits inside the `SOURCE = github` branch, but the
per-skill copy (`:266`) and doctrine copy (`:438`) use `tar` pipes on
every real run — so the documented offline path dies mid-loop with a raw
pipefail error and a partial install.

- **Before-arm** (measured): with `tar` off `PATH`, a `--source-dir`
  install created an empty `brainstorm/` directory containing **no
  SKILL.md**, printed `tar: command not found`, and **exited 0** — a
  silent partial install reported as success.
  `e2e-evidence/run-20260827T141645-installer-defects-before/step-06-local-install-without-tar.txt`
- **Measure**: `--source-dir` install with `tar` unavailable.
- **Threshold**: non-zero exit, one clear `die` before the loop, no
  partial tree left behind.

## 6. Derive the skill count instead of typing it  (recurring)

Count drift has shipped **four** times (17→19→18; commits `2953547`,
`c39a0f0`, `f95ba9d`, and this session). Prose cannot hold a number that
changes.

- **Before-arm**: `verify-orchestration.py:144` printed "the 17 skills"
  while validating 18.
- **Fix**: `f"…the {len(skills)} skills…"`, derived from the globbed list.
- **Measure**: run the gate.
- **Threshold**: prints 18 today and the true number after any change —
  verified: `VERDICT: PASS — the 18 skills …`

## 7. One truth about the flag surface  (HIGH)

`README.md` documented `--no-test` and `--tdd` with invented semantics at
line 117 and in two tables, while line 235 of the same file said those
flags do not exist — and `implement/SKILL.md:65-68` had removed them.

- **Measure**: grep the README for live advertisements.
- **Threshold**: zero, with only the negative statement remaining. ✓

## 8. Delete the ghost tree's last references

`plugins/truth-forge/` no longer exists, but two example files still
cited it — one pointing at a `fresh_evidence.py` path that is gone.

- **Measure**: grep `truth-forge` outside generated `docs/`.
- **Threshold**: zero hits, and any replacement path must exist on disk.
  ✓ (`plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py`
  confirmed present before it was cited.)

## 9. Test the branches that guard, not just the ones that pass

Scout mapped every hook's block/silent condition. Real gaps: the
`GENERIC_SECRET` fallback in `evidence-guard.sh` is never exercised, and
`no-test-files.sh`'s empty-path branch has no case. A guard whose blocking
path is untested is a guard nobody has seen fire.

- **Measure**: per hook, a case for the blocking path *and* the silent one.
- **Threshold**: both present for all six hooks (currently 4 of 6).

## 10. Protect what the docs promise to protect

Skills get SKIP/`--override`/backup handling; themes and plugins are plain
`cp` with no existence check, so user edits vanish silently. `--override`
also accumulates unbounded `.bak-TIMESTAMP` directories with no pruning
and no mention in the docs.

- **Measure**: install themes over a locally edited theme file.
- **Threshold**: either preserved and reported, or the overwrite is
  documented as intended behaviour. Silence is the defect.


---

## After-arms — measured results

Authoritative verdicts cited below are unpiped, so each exit code is the
command's own. Five captures elsewhere in `e2e-evidence/` are piped and
their `rc` fields are invalid; they are listed, with superseding artifacts,
in `e2e-evidence/run-20260827T160741-evidence-integrity-audit/`.

| # | Before | After | Artifact |
|---|--------|-------|----------|
| 1 | harness never called the installer (`grep -c` = 0) | `test-installer.sh` runs it; 7 groups; `INSTALLER TEST FAILS: 0` | `e2e-evidence/run-20260827T150627-installer-fixed-after/final-test-installer.txt` |
| 2 | **pristine old code** (`git show e890bc5`), unpiped: malformed `SKILL.md` → `✓ brainstorm`, rc=**0** | **current code, same input**: rc=**1**, `✗ brainstorm`, no false tick | `e2e-evidence/run-20260827T161126-verify-arm-gitorig/verdict.json` |
| 3 | **pristine old code** (`git show e890bc5`, sha256-matched, syntax-checked) on a real SHA: rc=**1**, not installed — unpiped | current code, same SHA: rc=**0**, installed. Branch form also PASS. `refs/tags/` **PASS** against the real `v2.1.0` tag (`e2e-evidence/run-20260827T163500-ref-tag-arm/verdict.json`) | `e2e-evidence/run-20260827T162405-ref-differential-pristine/verdict.json` |
| 4 | rc=**0**, 5 hook scripts orphaned, no `settings.json` | rc=**1**, `hook_dir_exists: false` — not even the directory is created (guard moved above `mkdir` after an audit found it ran first) | `e2e-evidence/run-20260827T160133-hooks-guard-mkdir/verdict.json` |
| 5 | rc=**0**, empty skill dir, no `SKILL.md` | rc=**1**, `skill_dirs: 0` — no partial tree | `e2e-evidence/run-20260827T150627-installer-fixed-after/step-03-verdicts.json` |
| 6 | verdict printed "the 17 skills"; `--help` said "all 17" | installed product: `--help` contains no `17`, installer reports `18 installed`, gate prints `the 18 skills` | `e2e-evidence/run-20260827T151017-items-9-10/step-04-rows-6-8-installed.txt` |
| 7 | README + `usage-guide.md:55` advertised `--no-test` / `--tdd` | post-edit check: installed `implement/SKILL.md` **and** `usage-guide.md` both carry zero advertisements | `e2e-evidence/run-20260827T151613-row7-postedit/step-01-row7-postedit.txt` |
| 8 | two `truth-forge` ghost paths | installed tree: 0 files mention `truth-forge`, 0 unresolved head references | `e2e-evidence/run-20260827T151017-items-9-10/step-04-rows-6-8-installed.txt` |
| 9 | `GENERIC_SECRET` + empty-path branches had no harness case | 2 cases added, 24 PASS; **mutation-tested in a sandbox copy** — disabling the generic-secret branch takes the harness to rc=**1**/23 PASS with the case failing by name, and restoring it returns rc=0/24 | `e2e-evidence/run-20260827T160908-hook-mutation/verdict.json` |
| 10 | theme edit destroyed silently (the only "collision" in output was the skills summary `0 skipped`) | `WARN: ! overwriting locally modified theme: /tmp/pp-theme-after/.omp/agent/themes/acid-rain.json` | `e2e-evidence/run-20260827T151017-items-9-10/step-02-theme-warning-after.txt` |


### Evidence-integrity audit (adversarial sweep)

An independent read-only audit swept **every** `.txt` in `e2e-evidence/`
for piped command captures. It found **5** files whose `rc=` header records
the exit code of `tail`, not of the command under test — where this session
had admitted only 1. Two were *after-arms* printing `ERROR:` above `rc=0`.

The captures themselves are **left untouched**. `evidence/AGENTS.md:22`
makes captures read-only — "a modified capture is a fabricated claim" — so
the invalidation is recorded in a separate manifest,
`e2e-evidence/run-20260827T160741-evidence-integrity-audit/invalid-rc-captures.json`,
which lists each file, its sha256, and the unpiped artifact that supersedes
it. (An earlier pass annotated these files in place; that was a violation of
the same rule and has been reverted byte-for-byte.)

Authoritative exit codes live in the `verdict.json` files. Each was captured
by an unpiped invocation with the exit code read directly from the command
itself — never through a pipeline, so no `rc` belongs to a downstream stage.

The audit also found `step-03-verify-green-on-malformed-skill.txt` shows
only a degraded-mode note rather than a malformed skill passing verify, and
that `step-04-after-verdict-count-derived.txt` is a `verify-orchestration.py`
PASS snippet misfiled into a `-before-` run. Both are discredited as proof.
Improvement 2's claim rests on the **pristine-installer arm**
(`run-20260827T161126-verify-arm-gitorig/verdict.json`) and improvement 3's
on the **pristine SHA differential**
(`run-20260827T162405-ref-differential-pristine/verdict.json`). Both old-code arms are the
committed installer extracted verbatim via
`git show e890bc5:tools/proofpunk-install.sh` — sha256-matched against
`git show` output and `bash -n` syntax-checked before use. Neither is a
reconstruction. Both are unpiped.

This matters because two earlier attempts in this session *did* reconstruct
old code by editing the current script, and both failed silently: one left a
dangling `FM_ERR` reference and died with `unbound variable` after printing
the very tick it was meant to demonstrate; the other produced a `bash`
syntax error and never reached the code under test. Reconstructed arms are
therefore not accepted as evidence here — the committed file is.

Before-arm provenance by row: rows 1, 4, 5 draw on
`e2e-evidence/run-20260827T141645-installer-defects-before/`; rows 2 and 3
draw on the two differential runs named above, which supersede the
corresponding captures in that directory.

Regression posture after every change: `test-hooks` 24 PASS (was 19 — two
new guard cases), `test-installer` 0 fails, `dry-run-install` 0 fails,
`verify-orchestration` PASS at 18, and a clean-HOME install of 18 skills
with 0 unresolved references.

---

## How success is measured overall

**Status: 10 of 10 proven.** All ten improvements carry a before-arm that
reproduced the defect and an after-arm that shows it fixed, each captured
from an unpiped run of the real installer or harness.

Improvement 3 was the last exception. Its branch and bare-SHA arms passed,
but its stated threshold — "install pinned to a real tag" — could not be met
while upstream had no tags, so it was reported **UNVERIFIED** rather than
PASS. Cutting the `v2.1.0` release tag made the arm drivable and it now
resolves (`e2e-evidence/run-20260827T163500-ref-tag-arm/verdict.json`). Writing the code and driving it are different things;
only the second counts, which is why this was not graded PASS until a real
tag existed. The tag points at the product commit; this closure evidence
lands in the follow-up commit, which is why the two are separate.

A trap worth recording: piping the installer through `tail` reports the
pipe's exit code, not the installer's. An adversarial sweep of every
capture found **five** files recorded that way, and two of them were
*after-arms* printing `ERROR:` above `rc=0`. Their `rc` fields are invalid.
The originals are immutable and remain untouched
(`evidence/AGENTS.md:22`); authoritative unpiped verdicts supersede them,
and each is listed with its hash and superseding artifact in
`e2e-evidence/run-20260827T160741-evidence-integrity-audit/invalid-rc-captures.json`.
Every verdict cited in the table above comes from an unpiped invocation
whose exit code was read directly from the command under test.

Item 9 is the strongest of the set: rather than asserting the new cases
pass, the guard was deliberately broken and the harness was shown to fail
because of it. A case that cannot fail proves nothing.

The three existing gates remain a regression concern only. They were green
throughout the period the installer was broken, which is precisely why
they are not accepted as proof here.
