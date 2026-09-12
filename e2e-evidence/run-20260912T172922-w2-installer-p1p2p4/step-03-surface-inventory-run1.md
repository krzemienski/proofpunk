# P2 surface inventory — HOME=/tmp/pp-p2-qW8jVh after ONE install

## skills installed (dirs with SKILL.md under $HOME/.claude/skills)
$HOME/.claude/skills/brainstorm/SKILL.md
$HOME/.claude/skills/codebase-truth-audit/SKILL.md
$HOME/.claude/skills/end-user-testing/SKILL.md
$HOME/.claude/skills/full-functional-audit/SKILL.md
$HOME/.claude/skills/implement/SKILL.md
$HOME/.claude/skills/mobile-validation-runner/SKILL.md
$HOME/.claude/skills/plan-hardening/SKILL.md
$HOME/.claude/skills/production-readiness/SKILL.md
$HOME/.claude/skills/prompt-forge/SKILL.md
$HOME/.claude/skills/proofpunk/SKILL.md
$HOME/.claude/skills/red-team-eval/SKILL.md
$HOME/.claude/skills/root-cause-debugging/SKILL.md
$HOME/.claude/skills/session-intent/SKILL.md
$HOME/.claude/skills/stack-testing/SKILL.md
$HOME/.claude/skills/tui-testing/SKILL.md
$HOME/.claude/skills/ui-experience-audit/SKILL.md
$HOME/.claude/skills/validation-plan/SKILL.md
$HOME/.claude/skills/visual-inspection/SKILL.md

skills_count=18

## hook scripts placed
bash-write-notice.sh
bash-write-snapshot.sh
capture-guard.sh
evidence-guard.sh
instructions-loaded.sh
no-test-files.sh
platform-steer.sh
post-write-walkthrough.sh
session-start.sh
stop-guard.sh
hooks_count=10

## commands
$HOME/.config/opencode/commands/proofpunk-acquire.md
$HOME/.config/opencode/commands/proofpunk-forge-prompt.md
$HOME/.config/opencode/commands/proofpunk-implement.md
$HOME/.config/opencode/commands/proofpunk-install.md
$HOME/.config/opencode/commands/proofpunk-rate-prompt.md
$HOME/.config/opencode/commands/proofpunk-truth-audit.md
$HOME/.config/opencode/commands/proofpunk-verify.md
commands_count=7

## agents
$HOME/.config/opencode/agents/end-user-validate.md
$HOME/.config/opencode/agents/implement.md
$HOME/.config/opencode/agents/proofpunk.md
$HOME/.config/opencode/agents/scout.md
agents_count=4

## settings.json hook registrations
InstructionsLoaded: 1 -> instructions-loaded.sh
PostToolUse: 2 -> post-write-walkthrough.sh, bash-write-notice.sh
PostToolUseFailure: 1 -> bash-write-notice.sh
PreToolUse: 5 -> no-test-files.sh, evidence-guard.sh, capture-guard.sh, bash-write-snapshot.sh, platform-steer.sh
SessionStart: 1 -> session-start.sh
Stop: 1 -> stop-guard.sh
SubagentStop: 1 -> stop-guard.sh
registered_total=12

## top-level HOME tree (depth 3)
$HOME
$HOME/.claude
$HOME/.claude/skills
$HOME/.claude/skills/brainstorm
$HOME/.claude/skills/codebase-truth-audit
$HOME/.claude/skills/end-user-testing
$HOME/.claude/skills/full-functional-audit
$HOME/.claude/skills/implement
$HOME/.claude/skills/mobile-validation-runner
$HOME/.claude/skills/plan-hardening
$HOME/.claude/skills/production-readiness
$HOME/.claude/skills/prompt-forge
$HOME/.claude/skills/proofpunk
$HOME/.claude/skills/proofpunk-doctrine
$HOME/.claude/skills/red-team-eval
$HOME/.claude/skills/root-cause-debugging
$HOME/.claude/skills/session-intent
$HOME/.claude/skills/stack-testing
$HOME/.claude/skills/tui-testing
$HOME/.claude/skills/ui-experience-audit
$HOME/.claude/skills/validation-plan
$HOME/.claude/skills/visual-inspection
$HOME/.config
$HOME/.config/opencode
$HOME/.config/opencode/agents
$HOME/.config/opencode/commands
$HOME/.config/opencode/plugin
$HOME/.config/opencode/themes
$HOME/.config/proofpunk
$HOME/.config/proofpunk/hyper-themes
$HOME/.omp
$HOME/.omp/agent
$HOME/.omp/agent/extensions
$HOME/.omp/agent/themes
$HOME/.proofpunk
$HOME/.proofpunk/hooks
