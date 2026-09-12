### P2 drive: first install into clean HOME=/tmp/pp-home-6PrNzM
### cmd: HOME=/tmp/pp-home-6PrNzM bash tools/proofpunk-install.sh --target claude-code --source local --source-dir . --hooks --themes --plugins
== Proofpunk installer ==
target dir : /tmp/pp-home-6PrNzM/.claude/skills  (claude-code)
source     : local checkout /Users/nick/proofpunk
version    : installed=none → source=4.0.0 (source is always the newest main)
installing : 18 skill(s)
  INSTALL brainstorm
  INSTALL codebase-truth-audit
  INSTALL end-user-testing
  INSTALL full-functional-audit
  INSTALL implement
  INSTALL mobile-validation-runner
  INSTALL plan-hardening
  INSTALL production-readiness
  INSTALL prompt-forge
  INSTALL proofpunk
  INSTALL red-team-eval
  INSTALL root-cause-debugging
  INSTALL session-intent
  INSTALL stack-testing
  INSTALL tui-testing
  INSTALL ui-experience-audit
  INSTALL validation-plan
  INSTALL visual-inspection
themes     : 20 flat-black cyberpunk themes
  OMP      -> ~/.omp/agent/themes (20) — select via /theme or theme.dark in config.yml
  OpenCode -> ~/.config/opencode/themes (20) — select via /themes or tui.json
  Hyper    -> ~/.config/proofpunk/hyper-themes (20 .js modules)
           activate: require one from a local plugin, or merge its COLORS into ~/.hyper.js
plugins    : platform glue
  OMP extension      -> ~/.omp/agent/extensions/proofpunk.ts
  OMP full plugin    : omp plugin marketplace add krzemienski/proofpunk && omp plugin install proofpunk@proofpunk
  OpenCode plugin    -> ~/.config/opencode/plugin/proofpunk.ts (+6 commands, 4 agents)
  OpenCode skills    : shared from ~/.claude/skills — re-run with --target claude-code if missing
  Claude Code plugin : /plugin marketplace add krzemienski/proofpunk && /plugin install proofpunk@proofpunk-marketplace
hooks      : enforcement hooks (Stop/SubagentStop + PreToolUse)
  copied: 10 hook scripts (bash-write-notice.sh, bash-write-snapshot.sh, capture-guard.sh, evidence-guard.sh, instructions-loaded.sh, no-test-files.sh, platform-steer.sh, post-write-walkthrough.sh, session-start.sh, stop-guard.sh)
  SessionStart: added
  Stop: added
  SubagentStop: added
  PreToolUse:no-test-files: added
  PreToolUse:evidence-guard: added
  PreToolUse:capture-guard: added
  PreToolUse:bash-write-snapshot: added
  PreToolUse:platform-steer: added
  InstructionsLoaded: added
  PostToolUse:post-write-walkthrough: added
  PostToolUse:bash-write-notice: added
  PostToolUseFailure: added
  settings: /tmp/pp-home-6PrNzM/.claude/settings.json
doctrine   : /tmp/pp-home-6PrNzM/.claude/skills/proofpunk-doctrine (the ruling rules every skill defers to)
verify     : per-skill frontmatter + reference checks (auto-fix on broken refs)
  ✓ brainstorm
  ✓ codebase-truth-audit
  ✓ end-user-testing
  ✓ full-functional-audit
  ✓ implement
  ✓ mobile-validation-runner
  ✓ plan-hardening
  ✓ production-readiness
  ✓ prompt-forge
  ✓ proofpunk
  ✓ red-team-eval
  ✓ root-cause-debugging
  ✓ session-intent
  ✓ stack-testing
  ✓ tui-testing
  ✓ ui-experience-audit
  ✓ validation-plan
  ✓ visual-inspection
verify     : all skills pass (see ✓ lines above)
== summary: 18 installed, 0 replaced, 0 skipped (collision), 0 missing ==
### unpiped rc follows
rc_run1=0
