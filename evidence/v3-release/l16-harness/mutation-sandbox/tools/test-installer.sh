#!/usr/bin/env bash
# test-installer.sh — execute the REAL tools/proofpunk-install.sh against
# scratch source/target directories and assert observable outcomes (exit
# code + on-disk state). dry-run-install.sh tests the /proofpunk:install
# slash-command template merge instead — it never invokes this installer.
# Run this before any change to proofpunk-install.sh.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT
FAILS=0

ok()  { echo "  PASS: $1"; }
bad() { echo "  FAIL: $1"; FAILS=$((FAILS+1)); }

[ -f "$(dirname "$0")/proofpunk-install.sh" ] || { echo "FATAL: installer not found next to $0"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "FATAL: python3 unavailable — group 7's frontmatter/reference check depends on it to distinguish a real catch from a shell-only fallback"; exit 1; }

# Scratch HOME: isolate every installer invocation from the real user's
# home directory (same pattern as test-hooks.sh), even though --dir is
# always passed explicitly below so no code path should need it.
export HOME="$TMP/home"
mkdir -p "$HOME"

# Hardcoded, not parsed from the installer: sourcing this list FROM
# proofpunk-install.sh would make the harness track the installer's own
# (possibly buggy) declaration and silently absorb exactly the ghost- or
# missing-skill-entry bug class tools/AGENTS.md warns about. This is the
# independently known-correct 18-skill set.
EXPECTED_SKILLS="brainstorm codebase-truth-audit end-user-testing full-functional-audit implement mobile-validation-runner plan-hardening production-readiness prompt-forge proofpunk red-team-eval root-cause-debugging session-intent stack-testing tui-testing ui-experience-audit validation-plan visual-inspection"
SKILL_COUNT="$(printf '%s' "$EXPECTED_SKILLS" | wc -w | tr -d ' ')"
FIRST_SKILL="$(printf '%s' "$EXPECTED_SKILLS" | awk '{print $1}')"

echo "== group 1: happy path (clean install of all $SKILL_COUNT skills)"
T1="$TMP/happy"
OUT=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$REPO_ROOT" --dir "$T1" --no-doctrine 2>&1)
RC=$?
if [ "$RC" -eq 0 ] && printf '%s' "$OUT" | grep -q "${SKILL_COUNT} installed"; then
  ok "clean install exits 0 and reports $SKILL_COUNT installed"
else
  bad "clean install — rc=$RC out=$OUT"
fi
missing=0
for s in $EXPECTED_SKILLS; do
  [ -f "$T1/$s/SKILL.md" ] || missing=$((missing+1))
done
if [ "$missing" -eq 0 ]; then
  ok "all $SKILL_COUNT skill dirs installed with SKILL.md"
else
  bad "$missing skill dir(s) missing SKILL.md after install"
fi

echo
echo "== group 2: collision default (second run over same dir does not clobber)"
CANARY="$T1/$FIRST_SKILL/CANARY-marker"
echo "untouched" > "$CANARY"
OUT2=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$REPO_ROOT" --dir "$T1" --no-doctrine 2>&1)
RC2=$?
if [ "$RC2" -eq 0 ] && printf '%s' "$OUT2" | grep -q "${SKILL_COUNT} skipped (collision)"; then
  ok "second run over same dir exits 0 and reports all $SKILL_COUNT skipped"
else
  bad "collision default — rc=$RC2 out=$OUT2"
fi
if [ -f "$CANARY" ]; then
  ok "existing skill dir untouched (canary file survived the second run)"
else
  bad "canary file gone — collision default clobbered an existing skill dir"
fi

echo
echo "== group 3: --override replaces and reports replaced"
OUT3=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$REPO_ROOT" --dir "$T1" --no-doctrine --override 2>&1)
RC3=$?
if [ "$RC3" -eq 0 ] && printf '%s' "$OUT3" | grep -q "${SKILL_COUNT} replaced"; then
  ok "--override exits 0 and reports $SKILL_COUNT replaced"
else
  bad "--override — rc=$RC3 out=$OUT3"
fi
if [ -f "$CANARY" ]; then
  bad "--override did not actually replace $FIRST_SKILL (canary file still present in live dir)"
else
  ok "--override actually replaced $FIRST_SKILL (canary file gone from live dir)"
fi
bak_dir=""
for f in "$T1"/.${FIRST_SKILL}.bak-*; do
  [ -d "$f" ] && bak_dir="$f"
done
if [ -n "$bak_dir" ] && [ -f "$bak_dir/CANARY-marker" ]; then
  ok "--override kept a .bak-* backup containing the pre-override skill content"
else
  bad "--override with default backup left no usable .bak-* copy of $FIRST_SKILL (bak_dir='$bak_dir')"
fi

echo
echo "== group 4: --only <name> installs exactly one skill"
T4="$TMP/only-one"
OUT4=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$REPO_ROOT" --dir "$T4" --no-doctrine --only "$FIRST_SKILL" 2>&1)
RC4=$?
count4=$(find "$T4" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
if [ "$RC4" -eq 0 ] && [ -f "$T4/$FIRST_SKILL/SKILL.md" ] && [ "${count4:-0}" -eq 1 ]; then
  ok "--only $FIRST_SKILL installs exactly that one skill dir"
else
  bad "--only single skill — rc=$RC4 dircount=${count4:-0} out=$OUT4"
fi

echo
echo "== group 5: --only <nonexistent> exits non-zero and reports missing"
T5="$TMP/only-bogus"
OUT5=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$REPO_ROOT" --dir "$T5" --no-doctrine --only "definitely-not-a-real-skill-xyz" 2>&1)
RC5=$?
if [ "$RC5" -eq 3 ] && printf '%s' "$OUT5" | grep -qi "no skill named"; then
  ok "--only bogus-name exits 3 and warns the skill was not found"
else
  bad "--only bogus-name — expected rc=3 with 'no skill named' warning, got rc=$RC5 out=$OUT5"
fi
count5=$(find "$T5" -mindepth 1 2>/dev/null | wc -l | tr -d ' ')
if [ "${count5:-0}" -eq 0 ]; then
  ok "--only bogus-name installed nothing (target dir empty or absent)"
else
  bad "--only bogus-name left ${count5:-0} unexpected file(s)/dir(s) in $T5"
fi

echo
echo "== group 6: --dry-run creates no files"
T6="$TMP/dryrun-target"
OUT6=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$REPO_ROOT" --dir "$T6" --no-doctrine --dry-run 2>&1)
RC6=$?
if [ "$RC6" -eq 0 ] && [ ! -e "$T6" ]; then
  ok "--dry-run exits 0 and creates no target directory"
else
  exists="no"; [ -e "$T6" ] && exists="yes"
  bad "--dry-run — expected rc=0 and no $T6, got rc=$RC6 exists=$exists out=$OUT6"
fi

echo
echo "== group 7: malformed skill (missing frontmatter) fails verify — the D3 regression"
SCRATCH_SRC="$TMP/scratch-src"
mkdir -p "$SCRATCH_SRC/plugins/proofpunk/skills/bad-skill"
cat > "$SCRATCH_SRC/plugins/proofpunk/skills/bad-skill/SKILL.md" <<'EOF'
# Bad Skill

This file deliberately has no YAML frontmatter block, matching the class
of malformed skill that must fail verification instead of a green tick.
EOF
T7="$TMP/malformed-target"
OUT7=$(bash "$(dirname "$0")/proofpunk-install.sh" --source-dir "$SCRATCH_SRC" --dir "$T7" --no-doctrine --only bad-skill 2>&1)
RC7=$?
if [ "$RC7" -ne 0 ] && printf '%s' "$OUT7" | grep -qi "no frontmatter"; then
  ok "malformed SKILL.md (no frontmatter) is caught: run fails (rc=$RC7), not a green tick"
else
  bad "malformed SKILL.md was NOT caught — expected non-zero rc + 'no frontmatter', got rc=$RC7 out=$OUT7"
fi
if [ -f "$T7/bad-skill/SKILL.md" ]; then
  ok "install step still copied the malformed SKILL.md before verify caught it (proves the check ran post-copy, not pre-empted)"
else
  bad "malformed SKILL.md was never copied to $T7/bad-skill/SKILL.md — cannot tell install-skip from verify-catch"
fi
if printf '%s' "$OUT7" | grep -qi '✓ bad-skill'; then
  bad "malformed skill got a false green tick '✓ bad-skill' in verify output"
else
  ok "no false '✓ bad-skill' green tick in verify output"
fi
if printf '%s' "$OUT7" | grep -qi 'all skills pass'; then
  bad "verify step claimed 'all skills pass' despite the malformed skill"
else
  ok "verify step did not claim 'all skills pass'"
fi

echo
echo "== group 8: --hooks registers EVERY proofpunk hook in settings.json"
H8="$TMP/hooks-home"
mkdir -p "$H8"
OUT8=$(HOME="$H8" bash "$(dirname "$0")/proofpunk-install.sh" --target claude-code \
  --source-dir "$REPO_ROOT" --only proofpunk --hooks 2>&1)
RC8=$?
S8="$H8/.claude/settings.json"
if [ "$RC8" -eq 0 ] && [ -f "$S8" ]; then
  ok "--hooks install succeeded (rc=0) and wrote $S8"
else
  bad "--hooks install failed: rc=$RC8, settings exists=$([ -f "$S8" ] && echo yes || echo no)"
fi
for HOOK in no-test-files evidence-guard capture-guard; do
  if [ -f "$H8/.proofpunk/hooks/$HOOK.sh" ]; then
    ok "$HOOK.sh copied to the hook home"
  else
    bad "$HOOK.sh was NOT copied to $H8/.proofpunk/hooks/"
  fi
  # Registration is the part plugin-side tests cannot see: a script on disk
  # that settings.json never invokes is a guard that silently never fires.
  if [ -f "$S8" ] && grep -q "$HOOK.sh" "$S8"; then
    ok "$HOOK.sh is REGISTERED in settings.json (not just copied)"
  else
    bad "$HOOK.sh is on disk but absent from settings.json — dead guard"
  fi
done
OUT8B=$(HOME="$H8" bash "$(dirname "$0")/proofpunk-install.sh" --target claude-code \
  --source-dir "$REPO_ROOT" --only proofpunk --hooks 2>&1)
RC8B=$?
N8=$(grep -c 'capture-guard.sh' "$S8" 2>/dev/null || echo 0)
if [ "$RC8B" -eq 0 ] && [ "$N8" -eq 1 ]; then
  ok "second --hooks run is idempotent: capture-guard.sh appears exactly once"
else
  bad "re-running --hooks was not idempotent: rc=$RC8B, capture-guard.sh occurrences=$N8"
fi

echo

echo "== group 9: fresh_evidence.py strict seal/validate contract"
# Guards the vacuous-pass defect: validate() returned OK on runs with zero
# artifacts, on unsealed runs, and on same-size content substitution.
FE="$(cd "$(dirname "$0")/.." && pwd)/plugins/proofpunk/skills/end-user-testing/scripts/fresh_evidence.py"
EV=$(mktemp -d); ( cd "$EV"
  python3 "$FE" init-run harness >/dev/null 2>&1
  python3 "$FE" seal >/dev/null 2>&1; echo "empty_seal_rc=$?"
  python3 "$FE" validate >/dev/null 2>&1; echo "empty_validate_rc=$?"
  echo PASSED > "$(python3 "$FE" next-step verdict).txt"
  python3 "$FE" validate >/dev/null 2>&1; echo "unsealed_rc=$?"
  python3 "$FE" seal >/dev/null 2>&1
  python3 "$FE" validate >/dev/null 2>&1; echo "sealed_clean_rc=$?"
  d=$(ls -d e2e-evidence/run-*); echo FAILED > "$d/step-01-verdict.txt"
  python3 "$FE" validate >/dev/null 2>&1; echo "samesize_tamper_rc=$?"
) > "$EV/out.txt" 2>&1
exp="empty_seal_rc=2 empty_validate_rc=2 unsealed_rc=2 sealed_clean_rc=0 samesize_tamper_rc=2"
got=$(tr '\n' ' ' < "$EV/out.txt" | sed 's/  */ /g;s/ $//')
if [ "$got" = "$exp" ]; then ok "fresh_evidence strict contract: empty/unsealed/tamper refused, clean sealed passes"
else bad "fresh_evidence contract drift — expected [$exp] got [$got]"; fi
rm -rf "$EV"


echo "== group 10: installed tree matches canonical hooks.json"
# Derive-don't-restate: the installer must install exactly what hooks.json
# declares. This is the check that would have caught session-start.sh shipping
# uncopied and SessionStart/InstructionsLoaded shipping unregistered.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
PH=$(mktemp -d)
HOME="$PH" bash "$REPO/tools/proofpunk-install.sh" --source-dir "$REPO" --target claude-code --hooks >/dev/null 2>&1
irc=$?
python3 - "$REPO" "$PH" > "$PH/parity.txt" 2>&1 <<'PYP'
import json, os, re, sys
repo, home = sys.argv[1], sys.argv[2]
spec = json.load(open(os.path.join(repo, "plugins/proofpunk/hooks/hooks.json")))
spec = spec.get("hooks", spec)
want = {m for a in spec.values() for e in a for h in e.get("hooks", [])
        for m in re.findall(r"([a-z-]+\.sh)", h["command"])}
got = set(os.listdir(os.path.join(home, ".proofpunk/hooks")))
inst = json.load(open(os.path.join(home, ".claude/settings.json")))["hooks"]
want_regs = sum(len(e.get("hooks", [])) for a in spec.values() for e in a)
got_regs = sum(len(e.get("hooks", [])) for a in inst.values() for e in a)
print("scripts", want == got, sorted(want ^ got))
print("events", set(spec) == set(inst), sorted(set(spec) ^ set(inst)))
print("regs", want_regs == got_regs, want_regs, got_regs)
PYP
if [ "$irc" = "0" ] && ! grep -q "False" "$PH/parity.txt"; then
  ok "installed tree matches canonical hooks.json (scripts, events, registrations)"
else
  bad "canonical hooks.json parity: $(cat "$PH/parity.txt" | tr '\n' ' ')"
fi
rm -rf "$PH"

echo "INSTALLER TEST FAILS: $FAILS"
exit "$FAILS"
