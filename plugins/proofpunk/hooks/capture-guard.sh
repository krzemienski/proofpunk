#!/bin/sh
# Proofpunk PreToolUse capture guard — evidence captures are immutable.
#
# Matcher: ^(Write|Edit|mcp__<server>__<write-ish tool>)$ — first-party
# Write/Edit plus MCP mutation tools. MCP filesystem payloads use `path`
# where first-party tools use `file_path`; both keys are read below.
# If the target file already exists, lives under an evidence directory
# (e2e-evidence/** or evidence/**), and has a raw-capture extension
# (.txt .log .out .err .jsonl .png .har .csv), the write is denied
# (exit 2; stderr is fed back to Claude) — a modified capture is a
# fabricated claim (evidence/AGENTS.md:22). Authored sidecars (.md, .json)
# and brand-new files are always allowed. Everything else passes (exit 0).
# Deterministic, <30ms.
set -eu

input=$(cat)

# Fail open when python3 is unavailable. Without this guard `set -eu` plus
# the python heredoc below exits 127, which PreToolUse/PostToolUse surface
# as a hook error -- breaking every matched tool call on a machine with no
# python3. This hook is documented as "never denies"/"allows everything
# else", so the only contract-correct behaviour is a silent allow.
if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

export PROOFPUNK_CAPTURE_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import json, os, re, sys

try:
    data = json.loads(os.environ["PROOFPUNK_CAPTURE_HOOK_INPUT"])
except Exception:
    sys.exit(0)

ti = data.get("tool_input") or {}
path = str(ti.get("file_path") or ti.get("path") or "")

# The evidence-directory pattern below is mirrored verbatim in
# plugins/proofpunk/hooks/evidence-guard.sh. Any change to it MUST be
# applied to both files — keep the two regex literals textually
# identical or the guards will silently diverge.
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
