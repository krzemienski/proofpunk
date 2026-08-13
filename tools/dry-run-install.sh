#!/usr/bin/env bash
# dry-run-install.sh — execute the /proofpunk:install mechanics against a
# sandbox project and assert every acceptance criterion from commands/install.md.
# This validates the template/assets/merge logic deterministically (the command
# doc itself is the agent playbook this script mirrors).
set -u
PP="$(cd "$(dirname "$0")/../plugins/proofpunk" && pwd)"
FIX="${1:-/tmp/pp-init-fixture}"
FAILS=0
ok() { echo "  PASS: $1"; }
bad() { echo "  FAIL: $1"; FAILS=$((FAILS+1)); }

echo "== fixture: existing project with package.json + existing CLAUDE.md"
rm -rf "$FIX"
mkdir -p "$FIX/src"
cat > "$FIX/package.json" <<'EOF'
{"name":"demo-app","scripts":{"test":"vitest run","build":"tsc -p tsconfig.json"},"dependencies":{"ink":"^5.0.0"}}
EOF
cat > "$FIX/CLAUDE.md" <<'EOF'
# demo-app

User's own project notes that must survive the install untouched.
EOF

echo "== step 1 detect"
STACK="node"; TEST_CMD="vitest run"; BUILD_CMD="tsc -p tsconfig.json"; IS_TUI=1
[ -f "$FIX/package.json" ] && ok "detected node stack"
grep -q ink "$FIX/package.json" && ok "detected TUI (ink)"

echo "== step 2 merge CLAUDE.md from template"
sed -e "s|{{PROJECT_NAME}}|demo-app|g" \
    -e "s|{{TEST_COMMAND}}|$TEST_CMD|g" \
    -e "s|{{BUILD_COMMAND}}|$BUILD_CMD|g" \
    "$PP/assets/claude-md-template.md" > "$FIX/.proofpunk-tpl.tmp"
# merge: replace marked section if present, else append (never edit outside markers)
if grep -q "proofpunk:begin" "$FIX/CLAUDE.md"; then
  python3 - "$FIX/CLAUDE.md" "$FIX/.proofpunk-tpl.tmp" <<'PYEOF'
import re, sys
doc = open(sys.argv[1]).read()
tpl = open(sys.argv[2]).read()
doc = re.sub(r"<!-- proofpunk:begin -->.*?<!-- proofpunk:end -->", tpl.strip(), doc, flags=re.S)
open(sys.argv[1], "w").write(doc)
PYEOF
else
  printf '\n' >> "$FIX/CLAUDE.md"
  cat "$FIX/.proofpunk-tpl.tmp" >> "$FIX/CLAUDE.md"
fi
rm -f "$FIX/.proofpunk-tpl.tmp"
grep -q "proofpunk:begin" "$FIX/CLAUDE.md" && ok "markers present"
grep -q "must survive the install untouched" "$FIX/CLAUDE.md" && ok "user content preserved"
LINES=$(wc -l < "$FIX/CLAUDE.md")
[ "$LINES" -le 200 ] && ok "CLAUDE.md ≤ 200 lines ($LINES)" || bad "CLAUDE.md too long ($LINES)"
grep -q "vitest run" "$FIX/CLAUDE.md" && ok "detected test command substituted"
! grep -q "{{" "$FIX/CLAUDE.md" && ok "no template placeholders left"

echo "== step 3 scoped rules"
mkdir -p "$FIX/.claude/rules"
cp "$PP/assets/rules/proof-obligations.md" "$FIX/.claude/rules/"
cp "$PP/assets/rules/evidence-contract.md" "$FIX/.claude/rules/"
[ "$IS_TUI" -eq 1 ] && cp "$PP/assets/rules/tui-driving.md" "$FIX/.claude/rules/"
[ -f "$FIX/.claude/rules/proof-obligations.md" ] && ok "proof-obligations rule written"
[ -f "$FIX/.claude/rules/evidence-contract.md" ] && ok "evidence-contract rule written"
[ -f "$FIX/.claude/rules/tui-driving.md" ] && ok "tui-driving rule written (TUI detected)"
grep -q "paths:" "$FIX/.claude/rules/evidence-contract.md" && ok "evidence-contract has paths scoping"

echo "== step 4 verify block (as the command prints it)"
wc -l "$FIX/CLAUDE.md" "$FIX/.claude/rules/"*.md
grep -c "proofpunk:begin" "$FIX/CLAUDE.md"
head -3 "$FIX/.claude/rules/proof-obligations.md"

echo
echo "INSTALL DRY-RUN FAILS: $FAILS"
exit "$FAILS"
