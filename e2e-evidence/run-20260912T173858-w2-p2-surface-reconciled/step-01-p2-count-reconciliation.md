# P2 — complete surface on a clean HOME, counts reconciled

## Why the raw numbers differ from the criterion text
P2's threshold (18 skills + 6 commands + 3 agents + 7 hooks) was written
against decision D4's measured v2.2.0 baseline (.planning/plugin-improvement-criteria.md:13).
v4 ships MORE surface than that baseline. The criterion is a floor, so the
test is 'every baseline item present', not 'the count is exactly 6/3/7'.
Both the repo-side truth and the installed truth are stated below so the
delta is explicit rather than silently absorbed.

## Repo-side truth (source of the install)
skills:            18
claude commands:   7  (v2.2.0 baseline was 6; /proofpunk:acquire added in ba97ec6)
opencode commands: 7
claude agents:     3  (matches the baseline of 3)
opencode agents:   4  (adds proofpunk.md router agent)
hook scripts:      10  (v2.2.0 baseline was 7; v4 adds 3)

## Clean-HOME install
cmd: HOME=/tmp/pp-p2b-UhnIem bash tools/proofpunk-install.sh --target claude-code --source local --source-dir $(pwd) --hooks --themes --plugins
unpiped rc=0

## Installed truth
skills with SKILL.md:  18
hook scripts on disk:  10
opencode commands:     7
opencode agents:       4

## Every hook script in the repo is present in the install (set comparison, not a count)
  identical sets — 0 missing, 0 extra

## Every hook is REGISTERED in settings.json (placed-but-unwired is the v1.10.0 defect class)
  registered script names: 10
  on-disk script names:    10
  on disk but NOT registered: none
  registered but NOT on disk: none
  events: InstructionsLoaded, PostToolUse, PostToolUseFailure, PreToolUse, SessionStart, Stop, SubagentStop

## Baseline floor check (the criterion's actual threshold)
  skills   >= 18 : 18  PASS
  commands >= 6  : 7  PASS
  agents   >= 3  : 4  PASS
  hooks    >= 7  : 10  PASS
  hooks registered in settings: yes (set comparison above)
