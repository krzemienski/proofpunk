#!/usr/bin/env bash
# Drive the REAL tools/proofpunk-install.sh against isolated HOME/dir.
# Unpiped rc capture: cmd > log 2>&1; echo $? > log.rc
set -u
EV="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$EV/../../../.." && pwd)"
# e2e-evidence/run-.../lane-installer -> repo is 4 up? 
# /Users/nick/proofpunk/e2e-evidence/run-.../lane-installer
# dirname x4: lane-installer, run, e2e-evidence, proofpunk. Yes 3 up from EV:
REPO="$(cd "$EV/../../.." && pwd)"
INSTALLER="$REPO/tools/proofpunk-install.sh"
SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/pp-install-drive.XXXXXX")"
echo "$SCRATCH" > "$EV/scratch.path"
echo "REPO=$REPO"
echo "INSTALLER=$INSTALLER"
echo "SCRATCH=$SCRATCH"
echo "EV=$EV"

run_install() {
  local step="$1"; shift
  local logfile="$EV/${step}.log"
  local rcfile="$EV/${step}.rc"
  # Intentionally unpiped.
  "$@" > "$logfile" 2>&1
  echo $? > "$rcfile"
  echo "  ran $step rc=$(cat "$rcfile")"
}

# ------------------------------------------------------------------ source truth
python3 - "$REPO" "$EV/step-00-source-truth.txt" <<'PY'
import json, os, sys
from pathlib import Path
repo = Path(sys.argv[1])
out = Path(sys.argv[2])
skills = sorted(p.name for p in (repo/"plugins/proofpunk/skills").iterdir()
                if p.is_dir() and (p/"SKILL.md").is_file())
refs = sorted(p.name for p in (repo/"plugins/proofpunk/references").iterdir() if p.is_file())
cmds = sorted(p.name for p in (repo/"plugins/proofpunk/commands").iterdir() if p.is_file())
hook_scripts = sorted(p.name for p in (repo/"plugins/proofpunk/hooks").iterdir()
                      if p.suffix == ".sh")
spec = json.loads((repo/"plugins/proofpunk/hooks/hooks.json").read_text())
events = spec.get("hooks", spec)
named = set()
regs = []
for ev, arr in events.items():
    for m in arr:
        for h in m.get("hooks", []):
            cmd = h.get("command", "")
            import re
            for s in re.findall(r"([A-Za-z0-9_-]+\.sh)", cmd):
                named.add(s)
                regs.append((ev, s, m.get("matcher")))
lines = []
lines.append(f"skill_count={len(skills)}")
lines.append("skills=" + " ".join(skills))
lines.append(f"ref_count={len(refs)}")
lines.append("refs=" + " ".join(refs))
lines.append(f"cmd_count={len(cmds)}")
lines.append("cmds=" + " ".join(cmds))
lines.append(f"hook_script_count={len(hook_scripts)}")
lines.append("hook_scripts=" + " ".join(hook_scripts))
lines.append(f"hooks_json_named_count={len(named)}")
lines.append("hooks_json_named=" + " ".join(sorted(named)))
lines.append(f"hooks_json_reg_count={len(regs)}")
for ev, s, matcher in regs:
    lines.append(f"reg {ev} {s} matcher={matcher}")
# pycache in source
pyc = list((repo/"plugins/proofpunk/skills").rglob("__pycache__"))
pycf = list((repo/"plugins/proofpunk/skills").rglob("*.pyc"))
lines.append(f"source_pycache_dirs={len(pyc)}")
lines.append(f"source_pyc_files={len(pycf)}")
fe = repo/"plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py"
lines.append(f"source_fresh_evidence={fe.is_file()}")
out.write_text("\n".join(lines) + "\n")
print(out.read_text())
PY
echo 0 > "$EV/step-00-source-truth.rc"

# ------------------------------------------------------------------ (a) default full install
HOME_A="$SCRATCH/home-a"
DIR_A="$SCRATCH/dir-a"
mkdir -p "$HOME_A"
export HOME="$HOME_A"
run_install step-01-default-full-install \
  bash "$INSTALLER" --source-dir "$REPO" --dir "$DIR_A"

# ------------------------------------------------------------------ (b) --hooks on CLEAN HOME, no prior settings.json
HOME_B="$SCRATCH/home-b"
mkdir -p "$HOME_B"
export HOME="$HOME_B"
# prove no settings.json beforehand
if [ -f "$HOME_B/.claude/settings.json" ]; then
  echo "PRECONDITION FAIL: settings.json already exists" > "$EV/step-02-hooks-clean-home.prefail"
fi
run_install step-02-hooks-clean-home \
  bash "$INSTALLER" --source-dir "$REPO" --target claude-code --hooks --only proofpunk

# ------------------------------------------------------------------ (c) --hooks TWICE into same HOME (idempotency)
# second run uses HOME_B
run_install step-03-hooks-idempotent-second \
  bash "$INSTALLER" --source-dir "$REPO" --target claude-code --hooks --only proofpunk

# ------------------------------------------------------------------ (d) --only <skill>
HOME_D="$SCRATCH/home-d"
DIR_D="$SCRATCH/dir-d"
mkdir -p "$HOME_D"
export HOME="$HOME_D"
run_install step-04-only-skill \
  bash "$INSTALLER" --source-dir "$REPO" --dir "$DIR_D" --no-doctrine --only end-user-testing

# ------------------------------------------------------------------ (e) install over EXISTING install (collision, then override)
HOME_E="$SCRATCH/home-e"
DIR_E="$SCRATCH/dir-e"
mkdir -p "$HOME_E"
export HOME="$HOME_E"
run_install step-05a-existing-first \
  bash "$INSTALLER" --source-dir "$REPO" --dir "$DIR_E" --no-doctrine --only brainstorm
echo "canary-untouched" > "$DIR_E/brainstorm/CANARY-marker"
run_install step-05b-collision \
  bash "$INSTALLER" --source-dir "$REPO" --dir "$DIR_E" --no-doctrine --only brainstorm
run_install step-05c-override \
  bash "$INSTALLER" --source-dir "$REPO" --dir "$DIR_E" --no-doctrine --only brainstorm --override

# persist paths for inventory
{
  echo "SCRATCH=$SCRATCH"
  echo "DIR_A=$DIR_A"
  echo "HOME_A=$HOME_A"
  echo "HOME_B=$HOME_B"
  echo "DIR_D=$DIR_D"
  echo "DIR_E=$DIR_E"
} > "$EV/scratch.vars"

echo "DRIVE DONE"
