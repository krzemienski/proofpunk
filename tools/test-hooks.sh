#!/usr/bin/env bash
# test-hooks.sh — execute every proofpunk hook with realistic JSON input and
# assert the decision behavior. Every case prints PASS/FAIL; exit 1 on any FAIL.
set -u
HOOKS="${1:-$(cd "$(dirname "$0")/../plugins/proofpunk/hooks" && pwd)}"
TMP=$(mktemp -d)
FAILS=0
export HOME="$TMP/home"
mkdir -p "$HOME/.claude" "$HOME/.proofpunk/bash-baselines"

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

# SessionStart never denies. Garbage stdin is ignored (script reads no
# stdin); still valid doctrine JSON, never a block decision. This is the
# allowing opposite of "could deny".
out=$(printf 'not-json' | sh "$HOOKS/session-start.sh" 2>/dev/null)
if printf '%s' "$out" | python3 -c '
import json, sys
d = json.load(sys.stdin)["hookSpecificOutput"]
assert d["hookEventName"] == "SessionStart"
assert "Proofpunk is installed" in d["additionalContext"]
' 2>/dev/null; then
  case_ok "session-start ignores stdin and never denies"
else
  case_fail "session-start stdin-ignored — got: $out"
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

# Case 4: missing transcript → non-blocking, but the fail-open must be
# OBSERVABLE. Silence is reserved for "the heuristic actually ran and found
# nothing to enforce"; a transcript it could never read must say so, or a
# guard that structurally cannot fail is indistinguishable from a clean run
# (this repo's defect Class 1). Still exit 0 — Stop cannot be blocked on an
# unread transcript — and must never emit a block decision.
out=$(printf '{"session_id":"s4","transcript_path":"/nonexistent/x.jsonl","cwd":"/tmp"}' | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard blocked on a missing transcript (must never block) — got: $out"; elif printf '%s' "$out" | grep -q 'enforcement OFF (transcript-missing-or-unreadable)'; then case_ok "stop-guard announces fail-open on missing transcript"; else case_fail "stop-guard fail-open was silent on missing transcript (must be observable) — got: $out"; fi

# Case 4b: python3 absent from PATH. Pre-fix: python3 missing made the
# `transcript=$(... python3 ... 2>/dev/null || true)` pipeline empty, then
# the `[ -n "$transcript" ] || exit 0` branch exited silently — same as a
# clean run. Isolated PATH=/bin (no python3 there) must emit python3-not-found.
out=$(PATH=/bin /bin/sh "$HOOKS/stop-guard.sh" <<'EOF'
{"session_id":"s4b","transcript_path":"/tmp/whatever.jsonl","cwd":"/tmp","hook_event_name":"Stop"}
EOF
)
rc=$?
if [ "$rc" -ne 0 ]; then case_fail "stop-guard python3-absent must exit 0 — rc=$rc out=$out"
elif printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard python3-absent must never block — got: $out"
elif printf '%s' "$out" | grep -q 'enforcement OFF (python3-not-found)'; then case_ok "stop-guard announces fail-open on missing python3"
else case_fail "stop-guard python3-absent was silent (must be observable) — got: $out"; fi

# Case 4c: unreadable existing transcript (chmod 000). Pre-fix: `[ -f ]`
# succeeded and python opened with errors=ignore / OSError → empty lines →
# silent exit 0. Now must emit transcript-missing-or-unreadable (or the
# python-side transcript-unreadable notice).
touch "$TMP/t4c.jsonl"
chmod 000 "$TMP/t4c.jsonl" 2>/dev/null || true
out=$(printf '{"session_id":"s4c","transcript_path":"%s","cwd":"/tmp","hook_event_name":"Stop"}' "$TMP/t4c.jsonl" | sh "$HOOKS/stop-guard.sh")
rc=$?
chmod 644 "$TMP/t4c.jsonl" 2>/dev/null || true
if [ "$rc" -ne 0 ]; then case_fail "stop-guard unreadable transcript must exit 0 — rc=$rc out=$out"
elif printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard unreadable transcript must never block — got: $out"
elif printf '%s' "$out" | grep -q 'enforcement OFF'; then case_ok "stop-guard announces fail-open on unreadable transcript"
else case_fail "stop-guard unreadable transcript was silent — got: $out"; fi

# Case 4d: malformed stdin JSON. Pre-fix: python3 -c except printed '' then
# `[ -n "$transcript" ] || exit 0` — silent. Now stdin-json-unreadable.
out=$(printf 'not-json' | sh "$HOOKS/stop-guard.sh")
rc=$?
if [ "$rc" -ne 0 ]; then case_fail "stop-guard malformed stdin must exit 0 — rc=$rc out=$out"
elif printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard malformed stdin must never block — got: $out"
elif printf '%s' "$out" | grep -q 'enforcement OFF (stdin-json-unreadable)'; then case_ok "stop-guard announces fail-open on malformed stdin"
else case_fail "stop-guard malformed stdin was silent — got: $out"; fi

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

# Case 11c: production path whose CONTENT carries a Fake* class. Path-only
# gating would stay silent (rc=0, empty stderr). The mock heuristic is a
# SOFT WARN — exit 0, never a deny — because a hard deny on `class Fake*`
# would block legitimate domain names. Pre-fix scripts without MOCK_MARKERS
# fail this case (empty stderr).
out=$(sh "$HOOKS/no-test-files.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/gateway.py","content":"class FakeGateway:\n    def send(self):\n        return 'ok'\n"}}
EOF
)
rc=$?
if [ "$rc" -ne 0 ]; then case_fail "no-test-files FakeGateway must stay exit 0 — rc=$rc out=$out"
elif printf '%s' "$out" | grep -q 'Fake/Mock/Stub class'; then case_ok "no-test-files warns on FakeGateway in production content"
else case_fail "no-test-files FakeGateway warn missing — out=$out"; fi

# Case 11d: production path with no mock markers → silent allow (exit 0, empty).
out=$(sh "$HOOKS/no-test-files.sh" 2>&1 <<'EOF'
{"tool_name":"Write","tool_input":{"file_path":"src/gateway.py","content":"class RealGateway:\n    def send(self):\n        return client.post('/v1')\n"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then case_ok "no-test-files silent on RealGateway production content"
else case_fail "no-test-files RealGateway — rc=$rc out=$out"; fi

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

echo "== stop-guard role gate + artifact-gated proof + path-shaped scout"
# Register item #10: discriminating regressions for the three defect classes
# the old raw-JSONL scanner let through (backlog #2/#4/#5). Every case here
# FAILS against the pre-fix stop-guard (which regex-matched raw transcript
# text with no role gate, no disk check, and no path-shaped-scout rule) and
# PASSES against the current implementation.

# Case 19: role-spoof, trigger direction (item #2) — a user line carrying
# claim-like words ('done', 'touchpoints') and no proof token must never
# TRIGGER the guard. The old scanner read the user's own "done" as a claim
# with no proof and blocked on the user's words alone.
cat > "$TMP/t7.jsonl" <<'EOF'
{"role":"user","text":"Is it done? Walk me through the touchpoints you changed."}
EOF
out=$(printf '{"session_id":"s7","transcript_path":"%s","cwd":"%s"}' "$TMP/t7.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"'; then case_fail "stop-guard triggered on a user line's claim words — got: $out"; elif [ -n "$out" ]; then case_fail "stop-guard spoke on user-only transcript (must be silent) — got: $out"; else case_ok "stop-guard ignores claim words on user lines"; fi

# Case 19b: role-spoof, satisfy direction (item #2) — a user "proving" the
# claim ('I verified it with a screenshot', 'touchpoints') must not satisfy
# proof/scout for an unproven assistant claim. The old scanner credited the
# user's 'screenshot' as proof and 'touchpoints' as scout → stayed silent.
cat > "$TMP/t8.jsonl" <<'EOF'
{"role":"assistant","text":"All done — complete."}
{"role":"user","text":"I verified it with a screenshot, and the touchpoints all look right to me."}
EOF
out=$(printf '{"session_id":"s8","transcript_path":"%s","cwd":"%s"}' "$TMP/t8.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"' && printf '%s' "$out" | grep -q 'without a cited'; then case_ok "stop-guard blocks claim 'proven' only by user words"; else case_fail "stop-guard accepted user-line proof/scout — got: $out"; fi

# Case 20: bare-keyword proof (item #4) — an assistant claim "proven" by
# prose ('verified with a screenshot') with no path-shaped artifact must
# block. The old PROOF regex counted the bare word 'screenshot' (and the
# bare 'touchpoints' as scout) → stayed silent on pure prose.
cat > "$TMP/t9.jsonl" <<'EOF'
{"role":"assistant","text":"Scout recap: I re-checked the touchpoints and entry points across the module."}
{"role":"assistant","text":"All done — complete and shipped. Verified with a screenshot as evidence."}
EOF
out=$(printf '{"session_id":"s9","transcript_path":"%s","cwd":"%s"}' "$TMP/t9.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"' && printf '%s' "$out" | grep -q 'without a cited'; then case_ok "stop-guard blocks prose-only proof"; else case_fail "stop-guard accepted bare-keyword proof — got: $out"; fi

# Case 21: fabricated path (item #4) — a cited e2e-evidence/ path that does
# NOT exist on disk earns no proof credit. The old PROOF matched the
# 'e2e-evidence/' substring with no disk check → stayed silent on an
# invented artifact.
cat > "$TMP/t10.jsonl" <<'EOF'
{"role":"assistant","text":"Scout context summary: touchpoints src/cart.ts, entry points src/main.ts"}
{"role":"assistant","text":"All done — complete. Evidence in e2e-evidence/run-2026-fake/step-99.png"}
EOF
out=$(printf '{"session_id":"s10","transcript_path":"%s","cwd":"%s"}' "$TMP/t10.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"' && printf '%s' "$out" | grep -q 'without a cited'; then case_ok "stop-guard blocks fabricated evidence path"; else case_fail "stop-guard credited nonexistent path as proof — got: $out"; fi

# Case 22: real-path proof, positive arm (items #4+#5) — a citation that
# resolves to a real file under <cwd>/evidence earns credit and the guard
# stays silent; the scout line carries a real path-shaped token. The old
# PROOF regex never recognized evidence/-rooted citations at all → it
# blocked this proven claim.
mkdir -p "$TMP/evidence/run-2026-real"
echo shot > "$TMP/evidence/run-2026-real/shot-final.png"
cat > "$TMP/t11.jsonl" <<'EOF'
{"role":"assistant","text":"Scout context summary: touchpoints src/checkout.ts, entry points src/main.ts"}
{"role":"assistant","text":"All done — complete. Evidence in evidence/run-2026-real/shot-final.png"}
EOF
out=$(printf '{"session_id":"s11","transcript_path":"%s","cwd":"%s"}' "$TMP/t11.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if [ -z "$out" ]; then case_ok "stop-guard silent on real on-disk evidence path"; else case_fail "stop-guard spoke on real evidence path — got: $out"; fi

# Case 23: bare-keyword scout (item #5) — 'touchpoints' with no path-shaped
# token on the same line is not a scout record, even alongside real on-disk
# proof. The old SCOUT matched the bare keyword → stayed silent. (The run dir
# is deliberately named 'run-2026-plain': SCOUT_KEYWORD is substring-based,
# so a dir name containing 'scout' would satisfy the keyword on the claim
# line itself.)
mkdir -p "$TMP/e2e-evidence/run-2026-plain"
echo shot > "$TMP/e2e-evidence/run-2026-plain/step-05.png"
cat > "$TMP/t12.jsonl" <<'EOF'
{"role":"assistant","text":"Scout context summary: I reviewed all the touchpoints in the checkout module."}
{"role":"assistant","text":"All done — complete. Evidence in e2e-evidence/run-2026-plain/step-05.png"}
EOF
out=$(printf '{"session_id":"s12","transcript_path":"%s","cwd":"%s"}' "$TMP/t12.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"' && printf '%s' "$out" | grep -q 'scout'; then case_ok "stop-guard blocks bare-keyword scout record"; else case_fail "stop-guard accepted bare-keyword scout — got: $out"; fi

# Case 24: scout-substring self-certification. Case 23 deliberately names its
# run dir 'run-2026-plain' to avoid the substring hazard — which means case 23
# passes with OR without the fix and cannot see this defect. This case IS the
# hazard: identical prose to case 23, but the cited evidence path contains the
# substring 'scout'. Unmasked, that single citation supplies BOTH conjuncts
# (keyword from the dirname, path shape from the path) and self-certifies as
# its own scout record — a false PASS in the proof-of-work guard. Only the
# dirname differs between case 23 and this case.
mkdir -p "$TMP/e2e-evidence/run-2026-scout"
echo shot > "$TMP/e2e-evidence/run-2026-scout/step-05.png"
cat > "$TMP/t13.jsonl" <<'EOF'
{"role":"assistant","text":"Scout context summary: I reviewed all the touchpoints in the checkout module."}
{"role":"assistant","text":"All done — complete. Evidence in e2e-evidence/run-2026-scout/step-05.png"}
EOF
out=$(printf '{"session_id":"s13","transcript_path":"%s","cwd":"%s"}' "$TMP/t13.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"' && printf '%s' "$out" | grep -q 'scout'; then case_ok "stop-guard blocks scout-substring self-certification"; else case_fail "stop-guard accepted scout-named evidence dir as its own scout record — got: $out"; fi

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

# Case 8b: malformed stdin → exit 0, no extra log line (fail-open, never a deny).
# This is the allowing opposite of "did write a line".
before=$(wc -l < "$HOME/.claude/proofpunk-loads.jsonl" | tr -d ' ')
out=$(printf 'not-json' | sh "$HOOKS/instructions-loaded.sh" 2>&1)
rc=$?
after=$(wc -l < "$HOME/.claude/proofpunk-loads.jsonl" | tr -d ' ')
if [ "$rc" -eq 0 ] && [ "$before" = "$after" ]; then case_ok "instructions-loaded fails open on malformed stdin"
else case_fail "instructions-loaded malformed stdin — rc=$rc before=$before after=$after out=$out"; fi

echo

# Case 25: bare-phrase non-path proof (item #4). PROOF_NONPATH exists so an
# inline assertion that needs no file can still count — but "validate OK" as a
# bare phrase was two typed words wide, and a claim citing ZERO artifacts
# passed silently. Both arms below are required: the bare phrase must block,
# and the real command shapes must still earn credit (otherwise the fix is a
# regression, not a tightening).
cat > "$TMP/t14.jsonl" <<'EOF'
{"role":"assistant","text":"Scouted src/app.py touchpoints. All done — complete. validate OK."}
EOF
out=$(printf '{"session_id":"s14","transcript_path":"%s","cwd":"%s"}' "$TMP/t14.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if printf '%s' "$out" | grep -q '"decision": "block"' && printf '%s' "$out" | grep -q 'without a cited'; then case_ok "stop-guard blocks bare-phrase 'validate OK' proof"; else case_fail "stop-guard credited a bare phrase as proof — got: $out"; fi

# Case 25b: positive arm — a real curl naming its endpoint and status still counts.
cat > "$TMP/t15.jsonl" <<'EOF'
{"role":"assistant","text":"Scouted src/app.py touchpoints. Done — curl https://api.example/health returned 200."}
EOF
out=$(printf '{"session_id":"s15","transcript_path":"%s","cwd":"%s"}' "$TMP/t15.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if [ -z "$out" ]; then case_ok "stop-guard silent on curl url+200 proof"; else case_fail "stop-guard rejected a real curl assertion — got: $out"; fi

# Case 25c: PROOF_NONPATH honesty. A typed curl+200 earns proof credit even
# when no HTTP request was ever made — the guard reads the transcript, not
# the network. Documented limitation (rule 10: never parse shell to close
# it). This case PASSES on both pre-fix and post-fix; it exists so a later
# "fix" that starts parsing shell cannot hide behind silence.
cat > "$TMP/t15c.jsonl" <<'EOF'
{"role":"assistant","text":"Scouted src/app.py touchpoints. Done — curl https://api.example/health returned 200."}
EOF
out=$(printf '{"session_id":"s15c","transcript_path":"%s","cwd":"%s"}' "$TMP/t15c.jsonl" "$TMP" | sh "$HOOKS/stop-guard.sh")
if [ -z "$out" ]; then case_ok "stop-guard curl+200 proof is transcript-only (request never confirmed)"
else case_fail "stop-guard curl+200 honesty case spoke — got: $out"; fi

echo "== bash-write-snapshot.sh (allow = silent exit 0; 'block' = non-Bash no-op)"
# Snapshot never denies. The allowing case is a real Bash snapshot that
# writes a baseline file. The "block-shaped" case is a non-Bash payload
# that the script ignores (exit 0, no state) — it cannot deny, so the
# closest observable opposite of "did work" is "did nothing".
SNAP=$(mktemp -d); mkdir -p "$SNAP/e2e-evidence/run-s" "$SNAP/src"
echo cap > "$SNAP/e2e-evidence/run-s/step-01.txt"
printf '{"hook_event_name":"PreToolUse","tool_name":"Bash","cwd":"%s","session_id":"snap","tool_use_id":"s1","tool_input":{"command":"true"}}' "$SNAP" > "$SNAP/in.json"
out=$(sh "$HOOKS/bash-write-snapshot.sh" < "$SNAP/in.json" 2>&1)
rc=$?
nbase=$(ls "$HOME/.proofpunk/bash-baselines" 2>/dev/null | wc -l | tr -d ' ')
if [ "$rc" -eq 0 ] && [ -z "$out" ] && [ "$nbase" -ge 1 ]; then case_ok "bash-write-snapshot records baseline on Bash"
else case_fail "bash-write-snapshot Bash arm — rc=$rc nbase=$nbase out=$out"; fi
# consume so leftover state cannot poison later cases
printf '{"hook_event_name":"PostToolUse","tool_name":"Bash","cwd":"%s","session_id":"snap","tool_use_id":"s1","tool_input":{"command":"true"}}' "$SNAP" > "$SNAP/in.json"
sh "$HOOKS/bash-write-notice.sh" < "$SNAP/in.json" >/dev/null 2>&1
out=$(sh "$HOOKS/bash-write-snapshot.sh" 2>&1 <<'EOF'
{"hook_event_name":"PreToolUse","tool_name":"Write","cwd":"/tmp","session_id":"snap","tool_use_id":"s2","tool_input":{"file_path":"src/a.ts"}}
EOF
)
rc=$?
if [ "$rc" -eq 0 ] && [ -z "$out" ]; then case_ok "bash-write-snapshot silent on non-Bash tool"
else case_fail "bash-write-snapshot non-Bash — rc=$rc out=$out"; fi
rm -rf "$SNAP"

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
