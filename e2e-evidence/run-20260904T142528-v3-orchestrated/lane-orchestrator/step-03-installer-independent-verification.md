# Orchestrator independent verification — LaneInstaller

Every claim below was re-driven by the orchestrator against the real system,
not accepted from the lane's report. Where my finding differs from the lane's,
the difference is stated.

## Claims verified

| Lane claim | My verification | Verdict |
|---|---|---|
| Installer has **no net change** | `git diff --stat tools/proofpunk-install.sh` → empty | **CONFIRMED** |
| Harness grew 10 → 12 groups | `git show 73e928e:tools/test-installer.sh \| grep -c 'echo "== group'` = **10**; current = **12** | **CONFIRMED** |
| New groups exist at named lines | `test-installer.sh:264` (group 11), `:286` (group 12) | **CONFIRMED** |
| `bash tools/test-installer.sh` rc=0 | re-run independently → rc=0, `INSTALLER TEST FAILS: 0` | **CONFIRMED** |
| Installer derives hooks from `hooks.json` | read `proofpunk-install.sh:409,416,468`; guard at `:426` exits if a named script is missing; **no hardcoded list found** | **CONFIRMED** |
| `--hooks` clean-HOME merge works | `step-02-settings.json` parsed: valid JSON, **7 event keys**, **11 registrations**, **0 duplicates** | **CONFIRMED** |
| Idempotency, no duplicate registrations | `step-03-hooks-idempotent-second.log` — second run reports all 11 as "already present"; rc=0 | **CONFIRMED** |
| F-D5-1 `__pycache__` NOT REPRODUCING | **I drove the installer myself**: source has 2 bytecode entries, installed tree has **0**, rc=0. Exclude present at `proofpunk-install.sh:283` (`tar --exclude='__pycache__' --exclude='*.pyc'`) | **CONFIRMED** |
| F-D5-2 harness gap fixed | restore arm shows `PASS: F-D5-2: installed fresh_evidence.py --help exits 0` | **CONFIRMED** |

## Correction to the lane's framing — mutation arm quality is not equal

The lane reported both mutations as satisfying doctrine 5. They are not of
equal quality, and the difference matters:

- **Arm 1 (F-D5-1)** is surgical and correct. `step-11-mutation-f-d5-1.rc=1`,
  and group 11 fails **by name** with its own diagnostic:
  `FAIL: F-D5-1 pycache leak — installer copied host bytecode; rc=0 source_pyc=3 dest_pyc=3`.
  Exactly one named assertion flipped. This is the standard.

- **Arm 2 (F-D5-2)** is blunt. `step-12-mutation-f-d5-2.rc=6` — **six** failures,
  including `clean install`, `collision default`, and `--override`, which are
  unrelated to `fresh_evidence.py`. The mutation broke the installer broadly
  rather than isolating the property group 12 asserts.

  What arm 2 **does** prove: the assertion is load-bearing and the harness is
  not vacuous. What it **does not** prove: that group 12 fails *specifically
  and only* when `fresh_evidence.py` is unavailable. A surgical arm (remove
  only the installed script, leave the installer intact) would have proven the
  narrower claim.

  Recorded as **PARTIAL** rather than restated as a clean mutation proof.

## Finding raised during verification — not a defect

My own install produced **19** directories against 18 source skills. Traced
rather than assumed: the 19th is `proofpunk-doctrine`, the doctrine bundle the
installer ships by design (`proofpunk-install.sh:44` `DOCTRINE_DIRNAME`,
`:95` `--no-doctrine` opt-out). 18 skills + 1 doctrine bundle = 19. **Correct
by design, not count drift.**

Worth recording because in a repo whose #1 recurring defect is count drift,
an unexplained 18-vs-19 is exactly the shape of a false finding — and would
have been one had I reported it without tracing it.

## Carried forward as open

- **`--plugins`/commands install path is UNVERIFIED.** The default `--dir`
  install does not copy `plugins/proofpunk/commands/` (6 files). The lane
  correctly declined to call this a defect without driving it. It is not
  driven yet, so it stays UNVERIFIED — not PASS, not FAIL.
- **Source tree still contains `plugins/proofpunk/skills/stack-testing/scripts/__pycache__`.**
  Harmless to installs (proven excluded above), but it is committed host
  bytecode. Outside LaneInstaller's ownership; noted for the release sweep.

## Evidence

All artifacts under
`e2e-evidence/run-20260904T142528-v3-orchestrated/lane-installer/`
(37 files, 12 `.rc` sidecars, every exit code captured unpiped).
My own reproduction runs are recorded in this lane-orchestrator directory.
