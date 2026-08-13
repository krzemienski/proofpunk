#!/bin/sh
# Proofpunk Stop/SubagentStop guard — the unproven-completion detector.
#
# Reads the session transcript (JSONL) from the hook input and applies the
# deterministic heuristic documented in docs/hooks-and-init-design.md §2:
#   claim without cited proof artifact  → decision:block (reason feeds back)
#   anything else                       → non-blocking additionalContext
#
# Contract (per Claude Code hooks reference):
#   - top-level {"decision":"block","reason":"..."} — the turn continues with
#     reason as Claude's next instruction
#   - hookSpecificOutput.additionalContext — soft, non-blocking context
# Always <50ms, never reads more than the last 40 transcript lines.
set -eu

input=$(cat)
transcript=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('transcript_path', ''))
except Exception:
    print('')
" 2>/dev/null || true)

[ -n "$transcript" ] && [ -f "$transcript" ] || {
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"proofpunk: done = proven by end-user testing — cite run-scoped evidence by full path."}}
JSON
  exit 0
}

python3 - "$transcript" <<'PYEOF'
import json, re, sys

path = sys.argv[1]
CLAIM = re.compile(r"\b(done|complete|completed|finished|shipped|all tests pass|works now|fixed it)\b", re.I)
PROOF = re.compile(r"(e2e-evidence/|evidence-inventory|step-\d+[-.]|screenshot|verdict|curl\s+\S+\s+200|validate\s+OK)", re.I)

try:
    with open(path, errors="ignore") as f:
        lines = f.readlines()[-40:]
except OSError:
    lines = []

claim = False
proof = False
for line in lines:
    low = line
    if CLAIM.search(low):
        claim = True
    if PROOF.search(low):
        proof = True

if claim and not proof:
    reason = ("Proofpunk: a completion was claimed without a cited end-user test artifact. "
              "Drive the real system as the end user, capture run-scoped evidence, and cite it by full path — "
              "or downgrade the claim to UNVERIFIED. Unproven is never done.")
    print(json.dumps({"decision": "block", "reason": reason}))
else:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": "proofpunk: done = proven by end-user testing — cite run-scoped evidence by full path."
        }
    }))
PYEOF
