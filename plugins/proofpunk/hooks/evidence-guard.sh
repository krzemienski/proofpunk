#!/bin/sh
# Proofpunk PreToolUse evidence guard — secrets never enter evidence dirs.
#
# Matcher: ^(Write|Edit|mcp__<server>__<write-ish tool>)$ — first-party
# Write/Edit plus MCP mutation tools. MCP filesystem payloads use `path`
# where first-party tools use `file_path`; both keys are read below.
# If the target file lives under an evidence directory (e2e-evidence/**
# or evidence/**) and the payload matches known secret shapes, the write
# is denied (exit 2; stderr is fed back to Claude). Everything else
# passes (exit 0). Deterministic, <30ms.
set -eu

input=$(cat)

# Fail open when python3 is unavailable. Without this guard `set -eu` plus
# the python heredoc below exits 127, which PreToolUse surfaces as a hook
# error -- breaking every matched tool call on a machine with no python3.
#
# Fail-open is correct; a SILENT fail-open is not. This hook DOES deny
# (exit 2 below), so a bare `exit 0` makes an unenforced machine look
# identical to an approved write -- and here the lost policy is secret
# hygiene in committed evidence. Announce the loss on stderr the way
# stop-guard.sh:37-46 already does, then allow.
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "Proofpunk: evidence-guard enforcement OFF (python3-not-found) — secret material in evidence writes is NOT being blocked on this machine." >&2
  exit 0
fi

export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import json, os, re, sys

try:
    data = json.loads(os.environ["PROOFPUNK_HOOK_INPUT"])
except Exception:
    sys.exit(0)

ti = data.get("tool_input") or {}
path = str(ti.get("file_path") or ti.get("path") or "")
content = str(ti.get("content") or ti.get("new_string") or "")

# The evidence-directory pattern below is mirrored verbatim in
# plugins/proofpunk/hooks/capture-guard.sh. Any change to it MUST be
# applied to both files — keep the two regex literals textually
# identical or the guards will silently diverge.
in_evidence = bool(re.search(r"(^|/)(e2e-evidence|evidence)(/|$)", path))
if not in_evidence:
    sys.exit(0)

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_-]{16,}",
    r"ghp_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"BEGIN (RSA|OPENSSH|EC|PGP) PRIVATE KEY",
]
GENERIC_SECRET = re.compile(
    r"(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}",
    re.I,
)
for pat in SECRET_PATTERNS:
    if re.search(pat, content):
        hit = pat
        break
else:
    hit = None
if hit is None and GENERIC_SECRET.search(content):
    hit = "generic-credential-assignment"

if hit:
    sys.stderr.write(
        "Proofpunk: refusing to write probable secret material into an evidence directory. "
        "Evidence is committed and public — redact keys/tokens first "
        "(see references/evidence-contract.md: redact, never commit).\n"
    )
    sys.exit(2)
sys.exit(0)
PYEOF
