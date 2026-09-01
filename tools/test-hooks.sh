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

echo "== session-start.sh emits valid JSON with doctrine context"
out=$(sh "$HOOKS/session-start.sh" 2>/dev/null)
if printf '%s' "$out" | python3 -c '
import json, sys
d = json.load(sys.stdin)["hookSpecificOutput"]
assert d["hookEventName"] == "SessionStart", "wrong hookEventName"
assert "end-user testing is the only PASS" in d["additionalContext"], "doctrine missing"
' 2>/dev/null; then
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

# Case 2: claim WITH proof AND scout record → silent
cat > "$TMP/t2.jsonl" <<'EOF'
{"role":"assistant","text":"Scout context summary: entry points src/main.ts, touchpoints src/cart.ts"}
{"role":"assistant","text":"All done — complete. Evidence in e2e-evidence/run-2026-x/step-03-shot.png"}
EOF
mkdir -p "$TMP/e2e-evidence/run-2026-x" && echo shot > "$TMP/e2e-evidence/run-2026-x/step-03-shot.png"
out=$(printf '{"session_id":"s2","transcript_path":"%s","cwd":"%s"}' "$TMP/t2.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard false-blocked proven claim — got: $out"; elif [ -n "$out" ]; then case_fail "stop-guard spoke on a proven claim (must be silent) — got: $out"; else case_ok "stop-guard silent on proven claim"; fi

# Case 3: no claim at all → no block
cat > "$TMP/t3.jsonl" <<'EOF'
{"role":"assistant","text":"I am still investigating the failing test."}
EOF
out=$(printf '{"session_id":"s3","transcript_path":"%s","cwd":"/tmp"}' "$TMP/t3.jsonl" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard blocked a non-claim — got: $out"; elif [ -n "$out" ]; then case_fail "stop-guard spoke on a non-claim (must be silent) — got: $out"; else case_ok "stop-guard silent on non-claim"; fi

# Case 4: missing transcript → non-blocking
out=$(printf '{"session_id":"s4","transcript_path":"/nonexistent/x.jsonl","cwd":"/tmp"}' | sh "$HOOKS/stop-guard.sh")
if [ -z "$out" ]; then case_ok "stop-guard silent on missing transcript"; else case_fail "stop-guard spoke on missing transcript (must be silent) — got: $out"; fi

echo "== evidence-guard.sh"
# Case 5: secret into evidence dir → denied (exit 2). JSON via heredoc —
# printf would eat the inner-quote escapes and produce invalid JSON.
out=$(sh "$HOOKS/evidence-guard.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"e2e-evidence/run-x/settings.json","content":"{\"apiKey\": \"ghp_ABCDEFGHIJKLMNOPQRSTUVWX123456\"}"}}
EOF
)
rc=$?
if [ "$rc" -eq 2 ]; then case_ok "evidence-guard denies secret into evidence"; else case_fail "evidence-guard secret deny — rc=$rc out=$out"; fi

# Case 5b: a credential that matches NO vendor prefix, only the generic
# assignment fallback. Without this the GENERIC_SECRET branch could be
# deleted and every other case would still pass.
out=$(sh "$HOOKS/evidence-guard.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"e2e-evidence/run-x/config.txt","content":"access_token = Zm9vYmFyYmF6cXV4MTIzNDU2Nzg5"}}
EOF
)
rc=$?
if [ "$rc" -eq 2 ]; then case_ok "evidence-guard denies generic credential assignment"; else case_fail "evidence-guard generic-secret deny — rc=$rc out=$out"; fi

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

echo "== capture-guard.sh"
# Case 16: existing .txt capture under e2e-evidence/ → denied (exit 2).
# Modifying a committed capture is a fabricated claim (evidence/AGENTS.md:22).
mkdir -p "$TMP/e2e-evidence/run-x"
echo "original capture output" > "$TMP/e2e-evidence/run-x/existing.txt"
out=$(sh "$HOOKS/capture-guard.sh" 2>&1 <<EOF
{"tool_name":"Write","tool_input":{"file_path":"$TMP/e2e-evidence/run-x/existing.txt","content":"tampered banner\noriginal capture output"}}
EOF
)
rc=$?
if [ "$rc" -eq 2 ]; then case_ok "capture-guard denies edit of existing evidence capture"; else case_fail "capture-guard existing-capture deny — rc=$rc out=$out"; fi

# Case 16b: existing .json sidecar under e2e-evidence/ → allowed (exit 0).
# Manifests/verdicts are authored and legitimately revised.
echo '{"status":"pass"}' > "$TMP/e2e-evidence/run-x/verdict.json"
out=$(sh "$HOOKS/capture-guard.sh" 2>&1 <<EOF
{"tool_name":"Write","tool_input":{"file_path":"$TMP/e2e-evidence/run-x/verdict.json","content":"{\"status\":\"pass\",\"note\":\"updated\"}"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "capture-guard allows editing existing json sidecar"; else case_fail "capture-guard json sidecar edit — rc=$rc out=$out"; fi

# Case 17: NEW (nonexistent) .txt path under e2e-evidence/ → allowed (exit 0).
# Creating a fresh capture is normal; only existing captures are protected.
out=$(sh "$HOOKS/capture-guard.sh" 2>&1 <<EOF
{"tool_name":"Write","tool_input":{"file_path":"$TMP/e2e-evidence/run-x/new-capture.txt","content":"fresh output"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "capture-guard allows new evidence capture"; else case_fail "capture-guard new-capture write — rc=$rc out=$out"; fi

# Case 18: .txt path OUTSIDE any evidence dir → allowed (exit 0, not our lane).
mkdir -p "$TMP/src"
echo "not evidence" > "$TMP/src/notes.txt"
out=$(sh "$HOOKS/capture-guard.sh" 2>&1 <<EOF
{"tool_name":"Write","tool_input":{"file_path":"$TMP/src/notes.txt","content":"editing outside evidence"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "capture-guard ignores non-evidence paths"; else case_fail "capture-guard non-evidence path — rc=$rc"; fi

echo "== no-test-files.sh"
# Case 9: test file path → denied (exit 2)
out=$(sh "$HOOKS/no-test-files.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/checkout.test.ts","content":"import {describe} from 'vitest'"}}
EOF
)
rc=$?
if [ "$rc" -eq 2 ]; then case_ok "no-test-files blocks *.test.* creation"; else case_fail "no-test-files test-file deny — rc=$rc out=$out"; fi

# Case 10: __tests__ dir → denied
out=$(sh "$HOOKS/no-test-files.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/__tests__/checkout.ts","content":"x"}}
EOF
)
rc=$?
if [ "$rc" -eq 2 ]; then case_ok "no-test-files blocks __tests__ dir"; else case_fail "no-test-files __tests__ deny — rc=$rc"; fi

# Case 11: production path → allowed
out=$(sh "$HOOKS/no-test-files.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/checkout.ts","content":"export const x = 1"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "no-test-files allows production code"; else case_fail "no-test-files production write — rc=$rc"; fi

# Case 11b: empty file_path → fail open (exit 0), never a spurious block.
# This branch had no case, so a regression turning it into a deny would
# have blocked unrelated tool calls with nothing catching it.
out=$(sh "$HOOKS/no-test-files.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"content":"no path at all"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ]; then case_ok "no-test-files fails open on empty path"; else case_fail "no-test-files empty path — rc=$rc out=$out"; fi

echo "== post-write-walkthrough.sh"
# Case 12: production change → walkthrough reminder
out=$(sh "$HOOKS/post-write-walkthrough.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/checkout.ts","content":"export const x = 1"}}
EOF
)
if printf '%s' "$out" | grep -q "drive the real system"; then case_ok "post-write walkthrough reminder on production change"; else case_fail "post-write reminder — got: $out"; fi

# Case 13: evidence/docs write → silent
out=$(sh "$HOOKS/post-write-walkthrough.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"e2e-evidence/run-x/step-01.md","content":"note"}}
EOF
)
if [ -z "$out" ]; then case_ok "post-write silent on evidence writes"; else case_fail "post-write spoke on evidence write — got: $out"; fi

echo "== stop-guard scout requirement"
# Case 14: claim + proof + no scout → blocked with scout reason
cat > "$TMP/t5.jsonl" <<'EOF'
{"role":"assistant","text":"All done. Evidence in e2e-evidence/run-x/step-01.png"}
EOF
mkdir -p "$TMP/e2e-evidence/run-x" && echo shot > "$TMP/e2e-evidence/run-x/step-01.png"
out=$(printf '{"session_id":"s5","transcript_path":"%s","cwd":"%s"}' "$TMP/t5.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q "scout"; then case_ok "stop-guard blocks claim+proof without scout record"; else case_fail "stop-guard scout requirement — got: $out"; fi

# Case 15: claim + proof + scout → silent
cat > "$TMP/t6.jsonl" <<'EOF'
{"role":"assistant","text":"Scout context summary: files touched src/a.ts, touchpoints src/b.ts"}
{"role":"assistant","text":"All done. Evidence in e2e-evidence/run-x/step-01.png"}
EOF
mkdir -p "$TMP/e2e-evidence/run-x" && echo shot > "$TMP/e2e-evidence/run-x/step-01.png"
out=$(printf '{"session_id":"s6","transcript_path":"%s","cwd":"%s"}' "$TMP/t6.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if [ -z "$out" ]; then case_ok "stop-guard silent on claim+proof+scout"; else case_fail "stop-guard spoke on fully-proven claim — got: $out"; fi

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

echo "== bash-write detector (Bash bypass mitigation)"
BW=$(mktemp -d); mkdir -p "$BW/e2e-evidence/run-1" "$BW/src"
echo ORIGINAL > "$BW/e2e-evidence/run-1/step-01.txt"; echo x > "$BW/src/a.ts"
bw_case() {  # id, command, expect NOTICE|SILENT, label
  printf '{"hook_event_name":"PostToolUse","tool_name":"Bash","cwd":"%s","session_id":"h","tool_use_id":"%s","tool_input":{"command":"c"}}' "$BW" "$1" > "$BW/in.json"
  sh "$HOOKS/bash-write-snapshot.sh" < "$BW/in.json" >/dev/null 2>&1
  ( cd "$BW" && eval "$2" ) >/dev/null 2>&1
  out=$(sh "$HOOKS/bash-write-notice.sh" < "$BW/in.json" 2>&1)
  got=SILENT; [ -n "$out" ] && got=NOTICE
  if [ "$got" = "$3" ]; then case_ok "bash-detector $4"; else case_fail "bash-detector $4 — expected $3 got $got"; fi
}
bw_case w1 "printf x > src/new.test.ts" NOTICE "test file via Bash is noticed"
bw_case w2 "printf TAMPERED > e2e-evidence/run-1/step-01.txt" NOTICE "evidence capture tamper is noticed"
bw_case w3 "rm e2e-evidence/run-1/step-01.txt" NOTICE "evidence deletion is noticed"
bw_case w4 "cp -p src/a.ts src/b.ts" SILENT "cp -p stays silent (no false deny)"
bw_case w5 "sed -i -e 's/x/y/' src/a.ts" SILENT "sed -i -e stays silent"
bw_case w6 "touch -c src/a.ts" SILENT "touch -c stays silent"
bw_case w7 "true" SILENT "no-op command stays silent"
bw_case w8 "echo sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ012345 > e2e-evidence/run-1/leak.txt" NOTICE "secret into evidence is noticed"

# failure path: PostToolUseFailure must behave identically and echo its own event name
printf '{"hook_event_name":"PostToolUseFailure","tool_name":"Bash","cwd":"%s","session_id":"h","tool_use_id":"wf","tool_input":{"command":"c"}}' "$BW" > "$BW/f.json"
sh "$HOOKS/bash-write-snapshot.sh" < "$BW/f.json" >/dev/null 2>&1
( cd "$BW" && printf x > src/fail.test.ts ) >/dev/null 2>&1
fout=$(sh "$HOOKS/bash-write-notice.sh" < "$BW/f.json" 2>&1)
if printf '%s' "$fout" | grep -q '"hookEventName": "PostToolUseFailure"'; then
  case_ok "bash-detector failure event echoes PostToolUseFailure"
else
  case_fail "bash-detector failure event -- got: $fout"
fi

# parallel calls: distinct baselines coexist, each consumed by its own call
printf '{"hook_event_name":"PostToolUse","tool_name":"Bash","cwd":"%s","session_id":"h","tool_use_id":"q1","tool_input":{"command":"c"}}' "$BW" > "$BW/q1.json"
printf '{"hook_event_name":"PostToolUse","tool_name":"Bash","cwd":"%s","session_id":"h","tool_use_id":"q2","tool_input":{"command":"c"}}' "$BW" > "$BW/q2.json"
sh "$HOOKS/bash-write-snapshot.sh" < "$BW/q1.json" >/dev/null 2>&1
sh "$HOOKS/bash-write-snapshot.sh" < "$BW/q2.json" >/dev/null 2>&1
nbase=$(ls "$HOME/.proofpunk/bash-baselines" 2>/dev/null | wc -l | tr -d ' ')
( cd "$BW" && printf x > src/par.test.ts ) >/dev/null 2>&1
p1=$(sh "$HOOKS/bash-write-notice.sh" < "$BW/q1.json" 2>&1)
p2=$(sh "$HOOKS/bash-write-notice.sh" < "$BW/q2.json" 2>&1)
left=$(ls "$HOME/.proofpunk/bash-baselines" 2>/dev/null | wc -l | tr -d ' ')
if [ "$nbase" -ge 2 ] && [ -n "$p1" ] && [ -n "$p2" ] && [ "$left" = "0" ]; then
  case_ok "bash-detector parallel calls isolated, state consumed"
else
  case_fail "bash-detector parallel -- baselines=$nbase leftover=$left"
fi
rm -rf "$BW"

echo "HOOK TEST FAILS: $FAILS"
rm -rf "$TMP"
exit "$FAILS"
