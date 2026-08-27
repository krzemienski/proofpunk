#!/bin/sh
# Proofpunk PreToolUse capture guard — evidence captures are immutable.
#
# Matcher: Write|Edit. If the target file already exists, lives under an
# evidence directory (e2e-evidence/** or evidence/**), and has a raw-capture
# extension (.txt .log .out .err .jsonl .png .har .csv), the write is denied
# (exit 2; stderr is fed back to Claude) — a modified capture is a
# fabricated claim (evidence/AGENTS.md:22). Authored sidecars (.md, .json)
# and brand-new files are always allowed. Everything else passes (exit 0).
# Deterministic, <30ms.
set -eu

input=$(cat)
export PROOFPUNK_CAPTURE_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import json, os, re, sys

try:
    data = json.loads(os.environ["PROOFPUNK_CAPTURE_HOOK_INPUT"])
except Exception:
    sys.exit(0)

ti = data.get("tool_input") or {}
path = str(ti.get("file_path") or "")

in_evidence = bool(re.search(r"(^|/)(e2e-evidence|evidence)(/|$)", path))
if not in_evidence:
    sys.exit(0)

ext = os.path.splitext(path)[1].lower()

SIDECAR_EXTS = {".md", ".json"}
if ext in SIDECAR_EXTS:
    sys.exit(0)

CAPTURE_EXTS = {".txt", ".log", ".out", ".err", ".jsonl", ".png", ".har", ".csv"}
if ext not in CAPTURE_EXTS:
    sys.exit(0)

if not os.path.exists(path):
    sys.exit(0)

sys.stderr.write(
    "Proofpunk: refusing to modify an existing evidence capture — a "
    "modified capture is a fabricated claim (see evidence/AGENTS.md:22). "
    "Captures are read-only once written; write a NEW run directory "
    "instead of editing or overwriting this file.\n"
)
sys.exit(2)
PYEOF
