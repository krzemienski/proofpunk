#!/bin/sh
# Proofpunk PreToolUse evidence guard — secrets never enter evidence dirs.
#
# Matcher: Write|Edit. If the target file lives under an evidence directory
# (e2e-evidence/** or evidence/**) and the payload matches known secret
# shapes, the write is denied (exit 2; stderr is fed back to Claude).
# Everything else passes (exit 0). Deterministic, <30ms.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import json, os, re, sys

try:
    data = json.loads(os.environ["PROOFPUNK_HOOK_INPUT"])
except Exception:
    sys.exit(0)

ti = data.get("tool_input") or {}
path = str(ti.get("file_path") or "")
content = str(ti.get("content") or ti.get("new_string") or "")

in_evidence = bool(re.search(r"(^|/)(e2e-evidence|evidence)(/|$)", path))
if not in_evidence:
    sys.exit(0)

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_-]{16,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY",
    r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}",
]
for pat in SECRET_PATTERNS:
    if re.search(pat, content):
        sys.stderr.write(
            "Proofpunk: refusing to write probable secret material into an evidence directory. "
            "Evidence is committed and public — redact keys/tokens first "
            "(see references/evidence-contract.md: redact, never commit).\n"
        )
        sys.exit(2)
sys.exit(0)
PYEOF
