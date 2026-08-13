#!/usr/bin/env bash
# test-hooks.sh — execute every proofpunk hook with realistic JSON input and
# assert the decision behavior. Every case prints PASS/FAIL; exit 1 on any FAIL.
set -u
HOOKS="${1:-$(cd "$(dirname "$0")/../plugins/proofpunk/hooks" && pwd)}"
TMP=$(mktemp -d)
FAILS=0

case_ok() { echo "  PASS: $1"; }
case_fail() { echo "  FAIL: $1"; FAILS=$((FAILS+1)); }

echo "== bash -n syntax check"
for f in "$HOOKS"/*.sh; do
  if bash -n "$f" 2>/dev/null; then case_ok "syntax $(basename "$f")"; else case_fail "syntax $(basename "$f")"; fi
done

echo "== session-start.sh emits doctrine context"
out=$(sh "$HOOKS/session-start.sh" 2>/dev/null)
if printf '%s' "$out" | grep -q "additionalContext" && printf '%s' "$out" | grep -q "end-user testing is the only PASS"; then
  case_ok "session-start doctrine context"
else
  case_fail "session-start doctrine context — got: $out"
fi

echo "== stop-guard.sh"
# Case 1: claim without proof → block
mkdir -p "$TMP"
cat > "$TMP/t1.jsonl" <<'EOF'
{"role":"assistant","text":"All done — the feature is complete and shipped."}
{"role":"user","text":"thanks"}
EOF
out=$(printf '{"session_id":"s1","transcript_path":"%s","cwd":"/tmp"}' "$TMP/t1.jsonl" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_ok "stop-guard blocks unproven claim"; else case_fail "stop-guard should block — got: $out"; fi

# Case 2: claim WITH proof → no block
cat > "$TMP/t2.jsonl" <<'EOF'
{"role":"assistant","text":"All done — complete. Evidence in e2e-evidence/run-2026-x/step-03-shot.png"}
EOF
out=$(printf '{"session_id":"s2","transcript_path":"%s","cwd":"/tmp"}' "$TMP/t2.jsonl" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard false-blocked proven claim — got: $out"; else case_ok "stop-guard allows proven claim"; fi

# Case 3: no claim at all → no block
cat > "$TMP/t3.jsonl" <<'EOF'
{"role":"assistant","text":"I am still investigating the failing test."}
EOF
out=$(printf '{"session_id":"s3","transcript_path":"%s","cwd":"/tmp"}' "$TMP/t3.jsonl" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard blocked a non-claim — got: $out"; else case_ok "stop-guard silent on non-claim"; fi

# Case 4: missing transcript → non-blocking
out=$(printf '{"session_id":"s4","transcript_path":"/nonexistent/x.jsonl","cwd":"/tmp"}' | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q "additionalContext"; then case_ok "stop-guard tolerates missing transcript"; else case_fail "stop-guard missing-transcript — got: $out"; fi

echo "== evidence-guard.sh"
# Case 5: secret into evidence dir → denied (exit 2). JSON via heredoc —
# printf would eat the inner-quote escapes and produce invalid JSON.
out=$(sh "$HOOKS/evidence-guard.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"e2e-evidence/run-x/settings.json","content":"{\"apiKey\": \"ghp_ABCDEFGHIJKLMNOPQRSTUVWX123456\"}"}}
EOF
)
rc=$?
if [ "$rc" -eq 2 ]; then case_ok "evidence-guard denies secret into evidence"; else case_fail "evidence-guard secret deny — rc=$rc out=$out"; fi

# Case 6: clean content into evidence dir → allowed (exit 0)
out=$(sh "$HOOKS/evidence-guard.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"e2e-evidence/run-x/step-01-note.txt","content":"wait matched TASKS at 110x32"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "evidence-guard allows clean evidence write"; else case_fail "evidence-guard clean write — rc=$rc"; fi

# Case 7: secret OUTSIDE evidence dir → allowed (exit 0, not our lane)
out=$(sh "$HOOKS/evidence-guard.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/config.json","content":"{\"apiKey\": \"ghp_ABCDEFGHIJKLMNOPQRSTUVWX123456\"}"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "evidence-guard ignores non-evidence paths"; else case_fail "evidence-guard non-evidence path — rc=$rc"; fi

echo "== instructions-loaded.sh"
# Case 8: writes a JSONL log line, exits 0
export HOME="$TMP/home"
mkdir -p "$HOME/.claude"
out=$(printf '{"file_path":"/proj/CLAUDE.md","load_reason":"session_start","cwd":"/proj"}' | sh "$HOOKS/instructions-loaded.sh"; echo "rc=$?")
if [ -f "$HOME/.claude/proofpunk-loads.jsonl" ] && grep -q "CLAUDE.md" "$HOME/.claude/proofpunk-loads.jsonl"; then
  case_ok "instructions-loaded logs load event"
else
  case_fail "instructions-loaded log — out=$out"
fi

echo
echo "HOOK TEST FAILS: $FAILS"
rm -rf "$TMP"
exit "$FAILS"
