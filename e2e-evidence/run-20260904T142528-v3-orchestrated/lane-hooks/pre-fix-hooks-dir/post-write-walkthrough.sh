#!/bin/sh
# Proofpunk PostToolUse guard — production-code changes demand an end-user
# walkthrough as the next action.
#
# Matcher: Write|Edit. When a production file changed (not evidence, docs,
# plans, or config), inject a tight reminder as additionalContext. Silent for
# everything else (evidence, docs, .planning, non-code).
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
if not path:
    sys.exit(0)

# Only production code counts. Evidence, docs, plans, memory, hooks themselves → silent.
SKIP = re.compile(
    r"(e2e-evidence/|/evidence/|\.planning/|\.md$|CLAUDE\.md|AGENTS\.md|RULES\.md|"
    r"\.claude/|\.opencode/|/docs?/|/hooks?/|CHANGELOG|README|LICENSE)",
    re.I,
)
if SKIP.search(path):
    sys.exit(0)

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            f"proofpunk: {path} changed. Before any completion claim: drive the real system "
            "as the end user along the path this change serves, capture run-scoped evidence, "
            "cite it by full path."
        ),
    }
}))
PYEOF
