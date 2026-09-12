# W4 — every script path cited by a skill, resolved and executed

No skill had ever been read for correctness. The highest-yield class is
a skill that tells the agent to run something that does not exist, or
does not accept the flag named. Those are found by executing, not
reading. Every scripts/ path mentioned in any SKILL.md or skill-local
reference is extracted and resolved below.

## Skill inventory, measured
skill                         bytes ownrefs  stages
brainstorm                     7222       0       0
codebase-truth-audit          15330       1       0
end-user-testing              10894       0       0
full-functional-audit          7346       0       0
implement                     10649       1       9
mobile-validation-runner       5930      22       0
plan-hardening                 6815       0       7
production-readiness           4427       3       0
prompt-forge                  17307       7       0
proofpunk                      5652       0       0
red-team-eval                  4064       4       0
root-cause-debugging           5888       9       0
session-intent                 6316       2       0
stack-testing                  5840      10       0
tui-testing                    7685       0       0
ui-experience-audit           10011       4       0
validation-plan                6765       1       0
visual-inspection              7187       0       0

NOTE: the task text lists 6 skills >6KB with zero own references.
Measured, the two LARGEST skills are prompt-forge (17,307 B) and
codebase-truth-audit (15,330 B) — neither appears in that table.
The debt is larger than stated.

## Every scripts/ reference, resolved

  resolvable script citations: 22
  unresolvable:               0

## Every skill-local script actually executed

### plugins/proofpunk/skills/stack-testing/scripts/with_server.py
   python3 $s --help  -> unpiped rc=0
     usage: with_server.py [-h] --server SERVERS --port PORTS [--timeout TIMEOUT]
                           ...
### plugins/proofpunk/skills/codebase-truth-audit/scripts/init_audit_workspace.py
   python3 $s --help  -> unpiped rc=0
     usage: init_audit_workspace.py [-h] --repo REPO [--label LABEL]
                                    [--start START] [--end END]
### plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py
   python3 $s --help  -> unpiped rc=0
     Usage:
       fresh_evidence.py init-run <slug>
### plugins/proofpunk/skills/session-intent/scripts/session_intent.py
   python3 $s --help  -> unpiped rc=0
     usage: session_intent.py [-h] [--projects-dir PROJECTS_DIR]
                              [--project PROJECT] [--since SINCE] [--until UNTIL]
### plugins/proofpunk/skills/mobile-validation-runner/scripts/example.sh
   sh $s --help  -> unpiped rc=1
     Unknown action: --help
### plugins/proofpunk/skills/mobile-validation-runner/scripts/validate.sh
   sh $s --help  -> unpiped rc=1
     plugins/proofpunk/skills/mobile-validation-runner/scripts/validate.sh: line 26: BUNDLE_ID: ERROR: BUNDLE_ID is required. Set BUNDLE_ID=com.your.app
### plugins/proofpunk/skills/mobile-validation-runner/scripts/simulator.sh
   sh $s --help  -> unpiped rc=1
     ✅ xc-mcp wrapper loaded (18 helper functions available)
     Usage: plugins/proofpunk/skills/mobile-validation-runner/scripts/simulator.sh <action> [args]
### plugins/proofpunk/skills/mobile-validation-runner/scripts/xc_mcp_wrapper.sh
   sh $s --help  -> unpiped rc=0
     ✅ xc-mcp wrapper loaded (18 helper functions available)
### plugins/proofpunk/skills/root-cause-debugging/scripts/hitl-loop.template.sh
   sh $s --help  -> unpiped rc=1
     
     >>> Open the app at http://localhost:3000 and sign in.
### plugins/proofpunk/skills/root-cause-debugging/scripts/find-polluter.sh
   sh $s --help  -> unpiped rc=1
     Usage: plugins/proofpunk/skills/root-cause-debugging/scripts/find-polluter.sh <file_to_check> <test_pattern>
     Example: plugins/proofpunk/skills/root-cause-debugging/scripts/find-polluter.sh '.git' 'src/**/*.test.ts'
### plugins/proofpunk/skills/session-intent/references/scripts/fetch-features.sh
   sh $s --help  -> unpiped rc=0
     -e [0;34mFetching latest Claude Code documentation...[0m
     
### plugins/proofpunk/skills/session-intent/references/scripts/github-discovery.sh
   sh $s --help  -> unpiped rc=0
     -e [0;34mGitHub Claude Code Discovery[0m
     -e [0;34m============================[0m
### plugins/proofpunk/skills/session-intent/references/scripts/analyze.sh
   sh $s --help  -> unpiped rc=0
     -e [0;34mClaude Code History Analyzer[0m
     -e [0;34m=============================[0m
### plugins/proofpunk/skills/session-intent/references/scripts/analyze-claude-md.sh
   sh $s --help  -> unpiped rc=1
     Error: Project path not found: --help
