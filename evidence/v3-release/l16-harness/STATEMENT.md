# L16 Harness Integrity — CAN/CANNOT OBSERVE statement

Generated as part of the L16 harness-integrity meta-gate build. Source of
truth: `tools/verify-harness-integrity.py` MANIFEST (each entry's
`can_observe`/`cannot_observe` fields, printed on every gate run).

## test-hooks.sh
- **Subject**: every hook script under `plugins/proofpunk/hooks/*.sh` (9 scripts).
- **CAN observe**: each hook script's stdout/decision/exit-code behavior
  against realistic hand-built JSON stdin, run in isolation via `sh`.
- **CANNOT observe**: whether the HOST (Claude Code) actually wires these
  scripts to the declared hook events at runtime, or delivers real (not
  hand-built) transcript/tool_input payloads. That requires driving a live
  session — see `sdk_probe.py`'s `stop_guard`/`instructions_loaded`/
  `blocks_test_file` probes.

## test-installer.sh
- **Subject**: the real installer binary `tools/proofpunk-install.sh`.
- **CAN observe**: real exit codes and on-disk state produced by actually
  running the installer against scratch source/target directories and an
  isolated HOME (happy path, collision default, `--override`, `--only`,
  malformed-skill/no-frontmatter detection, `--hooks` registration with
  settings.json parity, and idempotent re-runs).
- **CANNOT observe**: behavior against a user's real home directory,
  interactive prompts, or an install performed by an agent following
  `commands/install.md` rather than a direct binary invocation.

## dry-run-install.sh
- **Subject**: the `/proofpunk:install` command's template + scoped-rules
  assets (`plugins/proofpunk/assets/*.md` and `assets/rules/*.md`) — **NOT**
  `tools/proofpunk-install.sh`, which this harness never invokes. This is
  the corrected, honest declaration; the historical label in
  `tools/AGENTS.md` implied installer coverage that this harness never had.
- **CAN observe**: whether the command playbook's template substitution
  (`{{PLACEHOLDER}}` -> value), marker-preserving CLAUDE.md/AGENTS.md merge
  (existing user content survives, markers found and replaced idempotently),
  and scoped `.claude/rules`/`.opencode/rules` copy logic behave correctly
  against a sandbox fixture, for both claude-code and opencode platform
  shapes.
- **CANNOT observe**: whether an actual agent executing the
  `/proofpunk:install` slash command performs these same steps in the same
  order — this harness models the documented playbook in shell, it does
  not drive an agent session through the real command; it also proves
  nothing about `tools/proofpunk-install.sh`.

## verify-orchestration.py
- **Subject**: every `SKILL.md` under `plugins/proofpunk/skills/*/SKILL.md`
  (18 skills).
- **CAN observe**: structural properties of the skill-call graph parsed
  from every SKILL.md body — closure (every callee exists, no self-calls),
  acyclicity + topological depth, "Called by" claims match real edges,
  `implement`'s stage order matches the DAG, and a 12-word shingle
  duplication sweep.
- **CANNOT observe**: whether the Skill tool actually loads these files at
  runtime, whether a live agent follows the documented call order, or
  whether the plugin (not a same-named local copy) is the thing that
  loaded — those require `sdk_probe.py`'s `router`/`skill_*` probes.

## verify-citations.py
- **Subject**: every `*.md` file under `plugins/proofpunk/skills/**`
  (top-level SKILL.md files and bundled `references/*.md` files), read
  directly off disk via `os.walk` + `open` — deliberately bypassing the
  installer's citation-rewrite/bundle step.
- **CAN observe**: every `references/*.md` citation actually present in
  repo source text, resolved literally relative to the citing file against
  the real on-disk tree, split by severity (ERROR: unresolved in a
  top-level SKILL.md; WARN: unresolved in a bundled references/ file) with
  a frozen baseline so new WARNs are distinguishable from the known 29.
- **CANNOT observe**: whether a citation resolves correctly in an
  INSTALLED tree (that is the installer's own `--verify` pass, a different
  subject entirely — this harness exists precisely because that pass is
  structurally blind to repo-level breakage); also does not distinguish a
  genuine local doctrine break from a donor-skill provenance citation
  without `--explain-vendor`.

## sdk_probe.py
- **Subject**: a live Claude Agent SDK session with the proofpunk plugin
  loaded (`query()` driven by `ClaudeAgentOptions`).
- **CAN observe**: whether hooks actually fire (by `hook_event_name` in the
  observed message stream), whether skills actually load (by an observed
  Skill tool call plus successful result), and whether guarded writes
  actually land or are actually blocked on disk, in a real running session
  with the plugin config passed to the SDK.
- **CANNOT observe**: determinism across SDK/model versions — probes rely
  on live model behavior for prompt-following and are the least
  reproducible harness in `tools/`; a probe FAIL can mean the model did
  not attempt the requested action rather than the guard being broken
  (`require_write_attempt` distinguishes these two failure modes).

## verify-harness-integrity.py (this gate, self-declared)
- **Subject**: the `tools/` directory's harness source files themselves —
  this gate's subject is every other declared harness in `tools/`.
- **CAN observe**: static source-level co-occurrence of a declared
  subject basename/token with an invocation keyword inside each other
  harness's source — proves a harness's source CONTAINS an invocation,
  not that running the harness succeeds.
- **CANNOT observe**: runtime behavior of any harness (whether it actually
  passes when run); dataflow between a discovery call site and a
  consumption call site in `python_file_level` mode; and correctness of a
  harness's assertions — only whether it reaches its subject at all.
