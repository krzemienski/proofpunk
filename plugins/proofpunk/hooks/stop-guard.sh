#!/bin/sh
# Proofpunk Stop/SubagentStop guard — the unproven-completion detector.
#
# Reads the session transcript (JSONL) from the hook input and applies the
# deterministic heuristic documented in docs/hooks-and-init-design.md §2:
#   claim without cited proof artifact  → decision:block (reason feeds back)
#   claim + proof but no scout record   → decision:block (scout is mandatory)
#   anything else                       → SILENT (exit 0, no output)
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
  # nothing to check → stay silent (hook discipline: no output when there is
  # nothing to enforce; doctrine context belongs to SessionStart, not stops)
  exit 0
}

python3 - "$transcript" <<'PYEOF'
import json, re, sys

path = sys.argv[1]
CLAIM = re.compile(r"\b(done|complete|completed|finished|shipped|works now|fixed it)\b", re.I)
PROOF = re.compile(r"(e2e-evidence/|evidence-inventory|step-\d+[-.]|screenshot|verdict|curl\s+\S+\s+200|validate\s+OK)", re.I)
SCOUT = re.compile(r"(scout|context summary|files touched|touchpoints|entry points)", re.I)

try:
    with open(path, errors="ignore") as f:
        lines = f.readlines()[-40:]
except OSError:
    lines = []

claim = False
proof = False
scout = False
for line in lines:
    low = line
    if CLAIM.search(low):
        claim = True
    if PROOF.search(low):
        proof = True
    if SCOUT.search(low):
        scout = True

if claim and not proof:
    reason = ("Proofpunk: a completion was claimed without a cited end-user evidence artifact. "
              "Drive the real system as the end user, capture run-scoped evidence, and cite it by full path — "
              "or downgrade the claim to UNVERIFIED. Unproven is never done.")
    print(json.dumps({"decision": "block", "reason": reason}))
elif claim and proof and not scout:
    reason = ("Proofpunk: evidence is cited, but no codebase scout record appears in this session "
              "(scout/context summary/touchpoints). The write path never edits before scouting the real "
              "codebase — run the scout pass and record its context summary, or state why it was not needed.")
    print(json.dumps({"decision": "block", "reason": reason}))
else:
    # claim-with-proof or no claim: silent. No additionalContext — a stop hook
    # that speaks on every stop is noise in multi-plugin sessions (14+ hooks).
    pass
PYEOF
