# D5 — Locate every artifact referenced but not yet seen

Measured 2026-09-02 against `/Users/nick/proofpunk` @ `a41591a`.

## D5.1 — `fresh_evidence.py` — RESOLVED

The work order flagged this as cited by HEAD's commit body but absent from
every directory listing read so far. It is **not missing** — it was looked
for in the wrong place.

| Question | Answer |
|---|---|
| Canonical path | `plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py` |
| Tracked at HEAD | YES (`git ls-files` returns it) |
| First added | `20bd199` — "truth-forge: 10-skill evidence-driven delivery plugin + Mood Ring demo" |
| In `tools/` | **NO** — this is why the earlier `tools/*` glob missed it |
| Installed on this host | YES — `~/.claude/plugins/cache/proofpunk-marketplace/proofpunk/2.2.0/skills/end-user-testing/scripts/fresh_evidence.py` |

**Why it is not in `tools/`:** it is skill-owned, not repo-owned. It ships
*inside* the `end-user-testing` skill so an installed tree can run it without
the repo present. That placement is deliberate and correct; the work order's
premise that it "appeared in no directory listing" is explained, not a defect.

Consequence for L3 (I4 evidence attestation): the `attest` /
`verify-attestation` work targets a **skill-bundled script**, not a repo tool.
Any change to it must survive the installer's copy of `skills/**`, and must be
proven in an installed tree, not only in the repo.

### Consumers (15 tracked files reference it)

Harnesses (2): `tools/test-installer.sh`, `tools/verify-orchestration.py`.

Doctrine (1): `plugins/proofpunk/references/evidence-contract.md`.

Skills (3): `end-user-testing/SKILL.md` (owner), `stack-testing/SKILL.md`,
`mobile-validation-runner/SKILL.md`.

Docs (7): `plugins/proofpunk/docs/{architecture,validation-results,
consolidation-decisions,improvements,usage-guide}.md`,
`plugins/proofpunk/README.md`, root `README.md`.

Examples (1): `examples/mood-ring/e2e-evidence/README.md`.

Untracked planning (`.planning/hardening/*.md`) also references it; read for
intent only, never republished.

### Finding

- **F-D5-1 — `__pycache__` ships into the installed tree.** The installed
  2.2.0 tree contains
  `skills/end-user-testing/scripts/__pycache__/fresh_evidence.cpython-311.pyc`.
  A compiled artifact from a build host is being distributed to install
  targets. Two concrete risks: a stale `.pyc` can shadow a corrected `.py`
  under some loader conditions, and the bytecode is host/version-specific
  (`cpython-311`) while the target host's Python may differ. `tools/` has the
  same pollution locally (`tools/__pycache__` exists). This is an installer
  hygiene defect for the L1 lane, and it is **not** covered by any existing
  gate.
- **F-D5-2 — the installer has no `scripts/` copy path of its own.** The only
  `scripts/` mentions in `tools/proofpunk-install.sh` (lines 637-639) are in
  a *citation-resolution comment* about how a bare `scripts/x` reference
  inside `references/` may resolve. The script directory reaches the install
  target only because `skills/**` is copied wholesale. That works today, but
  nothing asserts it: if the skill-tree copy ever narrows to `SKILL.md`,
  `fresh_evidence.py` silently stops shipping and every evidence claim that
  depends on it fails at the target, not in CI. L1 must add an explicit
  assertion that the installed tree contains the script.

## D5.2 — Remaining "referenced but unseen" sweep

Still to enumerate in Phase 3, where every file is read end to end: any
script, reference, or doc named in guidance but not located on disk. The
method that resolved D5.1 is the one to reuse — search the whole tree, not
the directory the name suggests.

## Evidence

Produced by `git ls-files`, `git log --diff-filter=A`, a stdlib `os.walk`
over the working tree and the installed 2.2.0 tree, and `grep -rl` over
tracked source. Raw command transcripts are the session record.
