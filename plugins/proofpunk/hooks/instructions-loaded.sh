#!/bin/sh
# Proofpunk InstructionsLoaded tap — makes memory loading observable.
#
# Appends one JSONL line per loaded memory file to
# ~/.claude/proofpunk-loads.jsonl. This is the measurement tap that proves
# /proofpunk:install output actually loads into sessions. Always exit 0.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import datetime
import json
import os

try:
    data = json.loads(os.environ["PROOFPUNK_HOOK_INPUT"])
except Exception:
    raise SystemExit(0)

home = os.path.expanduser("~/.claude")
os.makedirs(home, exist_ok=True)
line = {
    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "file_path": data.get("file_path") or data.get("filePath") or "",
    "load_reason": data.get("load_reason") or data.get("loadReason") or "",
    "cwd": data.get("cwd", ""),
}
with open(os.path.join(home, "proofpunk-loads.jsonl"), "a") as f:
    f.write(json.dumps(line) + "\n")
PYEOF
exit 0
