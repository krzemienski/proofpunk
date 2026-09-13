# Changelog

All notable changes to proofpunk are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions are declared in `plugins/proofpunk/package.json` and the two
marketplace manifests; **a version heading here does not imply a git tag**.
Only `v2.1.0` and `v2.2.0` exist as real tags — see README.md:48.

## [Unreleased] — 4.0.0 declared in manifests, NOT tagged

4.0.0 is the version every manifest declares. It is deliberately untagged:
four acceptance criteria are unproven (P6, P8, P14, P15), and this plugin's
first rule is that unproven is never done. The blockers are recorded in
`e2e-evidence/run-20260913T072606-v4-all-agents/step-13-release-blocked.md`.

### Fixed

- **The installer could never install a newly added skill.** `ALL_SKILLS` in
  `tools/proofpunk-install.sh` was a hardcoded 18-name list written before
  `completion-summary` existed. A skill absent from that literal was never
  selected, and the summary line counted the same list — so "18 installed"
  agreed with itself while 19 skill directories sat in source. Both installed
  Claude Code caches (2.2.0 and 3.0.0) lack the skill for this reason: a
  defect that shipped, not a stale cache. `ALL_SKILLS` is now derived from
  the tree.
- **The OpenCode write guard read the wrong argument key.**
  `opencode/plugin/proofpunk.ts` read `args.path ?? args.file_path`, but
  OpenCode sends `filePath` — the key the read guard two branches above
  already used. `TEST_PATH` was therefore matched against `""` on every real
  write, so "the write path never creates test files" silently never fired.
  Mutation-proven: reverting the fix fails the assertion.
- Four stale skill counts in `plugins/proofpunk/docs/architecture.md`,
  invisible until `CLAIM_RE` was widened to see a qualifier between a number
  and its noun ("18 delivery skills").
- Router prose understated its own delivery-skill count in four places
  (it said seventeen; the tree has eighteen plus the router).
- `completion-summary` claimed it "proves agents terminated" while its own
  body documented the opposite. It confirms *recorded* completion only.
- `implement` claimed `rc=0` means every child terminated; it also covers a
  missing tracker (every runtime except Claude Code) and a degraded one.
- Eight shared-runbook citations written as `references/*-validation.md`
  without the `../../` prefix, unresolvable from their skill directories.
- `plan-hardening` permitted accepting a CRITICAL finding while forbidding
  finalization with any open CRITICAL — an unsatisfiable pair.
- `plan-hardening` claimed `validation-plan` owns the proof-obligation format
  it injects. They are different formats; validation-plan owns the rule.
- Gauge #6 compared against a hardcoded `18` inside its own measurement
  function, so correcting the target string alone left it UNMET at 19/19.

### Added

- `tools/test-integrations.mjs` — the first execution coverage of either
  TypeScript runtime integration. 36 assertions: the OpenCode plugin driven
  through both intent-verdict states, and the OMP extension driven through
  every event it actually receives, via an ExtensionAPI recorder that
  captures the shipped handlers.
- `references/enforcement-map.md` — which doctrine is mechanically enforced,
  by what, and in what precedence. 4 of 18 files are hook-enforced, 13 are
  carried by skills/tools/CI, 0 are globally unenforced.
- `references/subagent-aware-stop.md` §10 — cross-runtime reality, proven
  from published type contracts rather than assumed.
- A mutation-test artifact for `platform-steer.sh`, closing an inherited gap
  where one harness had no linked proof.

### Known limitations

- **Subagent-aware stop is Claude Code only.** OMP's `AgentStartEvent`
  declares exactly one field, `type` — no agent id, no session id. OpenCode's
  plugin types contain `subagent` zero times in 26,962 bytes. Neither runtime
  can populate the tracker, so neither can block on a live child. This is
  architecture, not unfinished work.
- **OpenCode cannot block at stop.** `session.idle` is delivered to a handler
  that returns `void`. Its only blocking seam is a throw from
  `tool.execute.before`, which fires on the session's next action.
- **P6 is flaky**, measured 1 pass in 3 runs of the same probe with no source
  change. Retries are not averaged into a pass.
- Two verifier blind spots are recorded rather than silently patched:
  `verify-counts` skips every `SKILL.md` by an explicit `HISTORICAL_PREFIXES`
  entry, and `verify-citations` cannot see a citation removed from its scope.

## [2.2.0] — tagged

See `proofpunk-v2-release-report.md`.

## [2.1.0] — tagged
