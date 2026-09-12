#!/bin/sh
# Proofpunk PostToolUse guard — production-code changes demand an end-user
# walkthrough as the next action.
#
# Matcher: ^(Write|Edit|mcp__<server>__<write-ish tool>)$ — first-party
# Write/Edit plus MCP mutation tools. MCP filesystem payloads use `path`
# where first-party tools use `file_path`; both keys are read below.
# When a production file changed (not evidence, docs, plans, or config),
# inject a tight reminder as additionalContext. Silent for everything
# else (evidence, docs, .planning, non-code).
set -eu

input=$(cat)

# Fail open when python3 is unavailable. Without this guard `set -eu` plus
# the python heredoc below exits 127, which the harness surfaces as a hook
# error on every matched tool call. This hook never denies, so it emits an
# observable enforcement-OFF notice and exits 0 -- silence would be
# indistinguishable from a clean run.
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"Proofpunk: post-write-walkthrough enforcement OFF (python3-not-found).\"}}"
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
