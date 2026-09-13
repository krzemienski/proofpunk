#!/bin/sh
# Proofpunk Stop/SubagentStop guard — the unproven-completion detector.
#
# Reads the session transcript (JSONL) from the hook input and applies the
# deterministic heuristic documented in docs/hooks-and-init-design.md §2:
#   claim without cited proof artifact  → decision:block (reason feeds back)
#   claim + proof but no scout record   → decision:block (scout is mandatory)
#   anything else                       → SILENT (exit 0, no output)
#
# Fail-open is observable. Missing python3, missing/unreadable transcript,
# or a heuristic crash used to exit 0 with no output — identical to "ran
# clean". Those paths now emit hookSpecificOutput.additionalContext containing
# the marker "enforcement OFF" and still exit 0 (Stop cannot be blocked on
# an unread transcript). A silent stop means the heuristic actually ran.
#
# Proof is artifact-gated: bare prose ("screenshot", "verdict",
# "evidence-inventory", "step-NN") no longer counts. Proof is either
# (a) an e2e-evidence/ or evidence/-rooted path that actually resolves to a
# real file relative to the hook's cwd, or (b) an inline non-path assertion
# (curl ... 200 / validate OK) that names no file and needs none. Scout
# likewise requires a path-shaped token on the same line as the scout
# keyword — prose alone ("scouted the touchpoints") does not satisfy it.
# See backlog #4/#5.
#
# Contract (per Claude Code hooks reference):
#   - top-level {"decision":"block","reason":"..."} — the turn continues with
#     reason as Claude's next instruction
#   - hookSpecificOutput.additionalContext — soft, non-blocking context
# Always <50ms, never reads more than the last 40 transcript lines.
set -eu

input=$(cat)

# Soft, non-blocking notice. Never decision:block — we did not inspect a
# transcript, so we cannot claim a completion. Reason tokens are [A-Za-z0-9_-]
# only so this printf stays valid JSON without an encoder.
emit_off() {
  _reason=$1
  _event=${2:-Stop}
  printf '%s\n' "{\"hookSpecificOutput\":{\"hookEventName\":\"${_event}\",\"additionalContext\":\"Proofpunk: stop-guard enforcement OFF (${_reason}). A ran-clean stop is only this notice's absence.\"}}"
  exit 0
}

if ! command -v python3 >/dev/null 2>&1; then
  emit_off "python3-not-found" "Stop"
fi

transcript=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('transcript_path', ''))
except Exception:
    raise SystemExit(2)
" ) || emit_off "stdin-json-unreadable" "Stop"

[ -n "$transcript" ] && [ -f "$transcript" ] && [ -r "$transcript" ] || {
  emit_off "transcript-missing-or-unreadable" "Stop"
}

cwd=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('cwd', ''))
except Exception:
    print('')
" ) || true

event=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('hook_event_name') or 'Stop')
except Exception:
    print('Stop')
" ) || true
[ -n "$event" ] || event=Stop

# session_id identifies WHICH session's intent verdict applies. It is present
# in every Stop payload and was previously unread. Reading it matters: an
# earlier attempt at the intent check derived the verdict key from an empty
# id, so the key collapsed to sha256(":" + cwd) -- identical for every session
# in a directory, letting one session's MET verdict authorize any other's
# stop. Extract it the same way as cwd and event, and fail to empty so a
# missing id can never silently match a real one.
session_id=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('session_id', ''))
except Exception:
    print('')
" ) || true

set +e
# The helper path is resolved HERE, where $0 is the real script path, and
# passed in. Inside a heredoc-piped script __file__ does not exist, so the
# block cannot locate its own directory.
_hookdir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
helper="$_hookdir/../skills/end-user-testing/scripts/intent_verdict.py"
python3 - "$transcript" "$cwd" "$event" "$session_id" "$helper" <<'PYEOF' 2>/dev/null
import json, os, re, sys

path = sys.argv[1]
cwd = sys.argv[2] if len(sys.argv) > 2 else ""
event = sys.argv[3] if len(sys.argv) > 3 else "Stop"
session_id = sys.argv[4] if len(sys.argv) > 4 else ""
helper = os.path.normpath(sys.argv[5]) if len(sys.argv) > 5 else ""

CLAIM = re.compile(r"\b(done|complete|completed|finished|shipped|works now|fixed it)\b", re.I)
# Non-path proof: an inline assertion that names no file and needs none.
# Both forms must carry a command shape, not a bare phrase: `curl <url> ... 200`
# names the endpoint it hit, and `fresh_evidence.py validate` names the tool
# that emitted the OK. A bare "validate OK" was two typed words wide and let a
# completion claim citing ZERO artifacts pass silently (backlog #4).
PROOF_NONPATH = re.compile(
    r"(curl\s+\S*https?://\S+.*?\b200\b|fresh_evidence(?:\.py)?\s+validate\b[^\n]*\bOK\b)",
    re.I,
)
# File-citation proof: only a path rooted at e2e-evidence/ or evidence/
# counts, and only once resolved (see path_proof). Bare keywords like
# "screenshot"/"verdict"/"evidence-inventory"/"step-NN" are no longer
# proof on their own (backlog #4).
PROOF_PATH = re.compile(r"(?<![\w-])(?:e2e-evidence|evidence)/[\w./-]+")
SCOUT_KEYWORD = re.compile(r"(scout|context summary|files touched|touchpoints|entry points)", re.I)
# A concrete FILE reference: two or more /-separated segments whose final
# segment carries an extension (src/app.py, plugins/proofpunk/hooks/x.sh).
# Requiring the extension is what keeps prose pairs ("and/or",
# "input/output") and bare URLs ("https://x.com/y") from counting as a
# scout record. Matched against extracted assistant text, never the raw
# JSON record — the envelope's own "cwd" would otherwise satisfy this on
# every line and make the conjunction inert (backlog #5).
PATH_SHAPED = re.compile(r"[\w.\-]+/[\w.\-/]*[\w\-]+\.[A-Za-z0-9]{1,8}\b")

try:
    with open(path, errors="ignore") as f:
        lines = f.readlines()[-40:]
except OSError:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": (
                "Proofpunk: stop-guard enforcement OFF (transcript-unreadable). "
                "A ran-clean stop is only this notice's absence."
            ),
        }
    }))
    raise SystemExit(0)

def is_assistant_line(record):
    # Role gate: CLAIM/PROOF/SCOUT may only ever fire from assistant-authored
    # lines. A user line can contain any of these words verbatim (asking
    # "is this done?", or pasting proof/scout-shaped text) and must never be
    # mistaken for the assistant's own claim or the assistant's own evidence.
    if not isinstance(record, dict):
        return False
    role = record.get("role")
    if role is None:
        message = record.get("message")
        if isinstance(message, dict):
            role = message.get("role")
    return isinstance(role, str) and role.strip().lower() == "assistant"

def assistant_text(record):
    # Signals must match the assistant's OWN WORDS, never the raw JSON record.
    # Real transcript envelopes carry "cwd":"/Users/<you>/<project>", which
    # satisfies PATH_SHAPED on every line — that made the SCOUT conjunction
    # inert: prose with no path at all scored as a scout. Extract the text
    # blocks and match those. Falls back to "" so a shape we do not recognize
    # grants no credit rather than silently reverting to raw-line matching.
    if not isinstance(record, dict):
        return ""
    message = record.get("message")
    content = (message or {}).get("content") if isinstance(message, dict) else None
    if content is None:
        content = record.get("content")
    if content is None and isinstance(record.get("text"), str):
        # Flat {"role": ..., "text": ...} records.
        return record["text"]
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
    return "\n".join(parts)

def path_proof(line):
    # A cited e2e-evidence/ or evidence/ path counts as proof only if it
    # resolves to a real FILE (not merely an existing path) that stays
    # rooted under <cwd>/e2e-evidence or <cwd>/evidence once normalized —
    # a "../" escape out of the evidence tree grants no credit. Fail safe:
    # an unresolvable cwd, a directory instead of a file, or any resolution
    # error grants no proof credit — never a crash (caller also wraps the
    # whole script in 2>/dev/null || true as a last-resort backstop).
    if not cwd:
        return False
    roots = []
    for name in ("e2e-evidence", "evidence"):
        try:
            roots.append(os.path.realpath(os.path.join(cwd, name)))
        except (OSError, ValueError):
            continue
    if not roots:
        return False
    for token in PROOF_PATH.findall(line):
        candidate = token.rstrip(").,;:!?\"'`")
        if not candidate:
            continue
        try:
            resolved = os.path.realpath(os.path.join(cwd, candidate))
            if not os.path.isfile(resolved):
                continue
            if any(resolved == root or resolved.startswith(root + os.sep) for root in roots):
                return True
        except (OSError, ValueError):
            continue
    return False

claim = False
proof = False
scout = False
for line in lines:
    try:
        record = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        # Unparseable line: role cannot be determined, so it is skipped for
        # every signal — never scanned as raw text.
        continue
    if not is_assistant_line(record):
        continue
    text = assistant_text(record)
    if not text:
        continue
    if CLAIM.search(text):
        claim = True
    if PROOF_NONPATH.search(text) or path_proof(text):
        proof = True
    # A scout record must be the assistant's OWN PROSE naming real files.
    # Cited evidence paths are masked out first: a run directory named
    # e2e-evidence/run-2026-scout/step-05.png otherwise supplies BOTH
    # conjuncts by itself (the word "scout" from the dirname, the path
    # shape from the path), letting any citation self-certify as its own
    # scout record. Only the dirname differed between the two arms that
    # exposed this, so mask the citations, then test the remaining prose.
    scout_text = PROOF_PATH.sub(" ", text)
    if SCOUT_KEYWORD.search(scout_text) and PATH_SHAPED.search(scout_text):
        scout = True

# Liveness comes FIRST, before any claim/proof/scout reasoning.
#
# Those gates ask "was this work proven?". This asks a different question that
# does not depend on the answer: are this session's background children still
# working? A subagent is not required to report back to the main thread, so the
# main transcript can look finished while children run.
#
# Ordering is load-bearing. Placed after the claim gates, an unproven claim
# blocks on its own reason and the liveness check is never reached -- measured:
# a live child with a completion claim reported "claimed without evidence" and
# said nothing about the running child.
#
# It does NOT run for SubagentStop. That event fires when a CHILD stops; holding
# a child open because its siblings are busy would deadlock the very work the
# session is waiting for. Contract: references/subagent-aware-stop.md
if event != "SubagentStop" and session_id:
    state_helper = os.path.join(os.path.dirname(helper), "agent_state.py") if helper else ""
    if state_helper and os.path.isfile(state_helper):
        import subprocess
        try:
            r = subprocess.run(
                [sys.executable, state_helper, "live",
                 "--session", session_id, "--cwd", cwd],
                capture_output=True, text=True, timeout=5)
            # rc 0 == at least one live child. Anything else (including a crash)
            # must not hold the session: the helper already fails open by
            # construction, and a stop guard that traps a session on its own
            # failure is worse than the bug it prevents.
            if r.returncode == 0:
                detail = (r.stdout or "").strip()
                print(json.dumps({"decision": "block", "reason": (
                    "Proofpunk: background subagents are still running, so this "
                    "session is not finished. " + detail + ". Wait for them to "
                    "complete and collect their results, or state explicitly why "
                    "their output is not needed.")}))
                sys.exit(0)
        except (OSError, subprocess.SubprocessError):
            pass  # fail open, exactly as the helper would

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
    # claim-with-proof, or no claim at all. The evidence question is settled.
    #
    # But evidence proves a task RAN, not that the asked-for thing HAPPENED.
    # A session can cite real artifacts for work nobody requested, or for one
    # clause of a four-clause request, and every gate goes green. So when a
    # completion is claimed, ask the second question: was the ORIGINAL intent
    # met? Contract: references/intent-verification.md
    #
    # This hook does not judge that — judging it is a natural-language
    # comparison, and a regex attempting it would be a guard faking
    # comprehension. It asks the helper that owns the rule. Delegation is
    # deliberate: an earlier draft reimplemented the key derivation and the
    # attempt cap here, which is two implementations of one rule and a
    # guarantee they drift.
    if claim:
        # Fail CLOSED. Every branch below that cannot establish "intent was
        # met" blocks, because this guard's failure mode is authorizing a stop
        # it should have refused. That is the opposite of the python3-absent
        # policy elsewhere in this hook set: there, a missing interpreter must
        # not break a user's tool call, so those guards allow and announce.
        # Here the guard IS the check, and an unverifiable check is a failed
        # check.
        block = None
        if not session_id:
            block = ("Proofpunk: a completion was claimed but this session has no "
                     "session_id, so its intent verdict cannot be identified. Without "
                     "it, one session's verdict could authorize another's stop. "
                     "Record the verdict explicitly with intent_verdict.py.")
        elif not (helper and os.path.isfile(helper)):
            block = ("Proofpunk: a completion was claimed but the intent-verification "
                     "helper is missing (skills/end-user-testing/scripts/"
                     "intent_verdict.py). Intent cannot be checked, so the claim "
                     "cannot be accepted. Reinstall the skills or downgrade to "
                     "UNVERIFIED.")
        else:
            import subprocess
            try:
                r = subprocess.run(
                    [sys.executable, helper, "--session-id", session_id,
                     "--cwd", cwd, "may-stop"],
                    capture_output=True, text=True, timeout=5)
                if r.returncode != 0:
                    block = (r.stderr or "").strip() or (
                        "Proofpunk: the original intent was not met.")
            except (OSError, subprocess.SubprocessError) as exc:
                block = (f"Proofpunk: the intent-verification helper could not run "
                         f"({type(exc).__name__}), so the completion claim cannot be "
                         "checked against the original request. Fix the helper or "
                         "downgrade the claim to UNVERIFIED.")
        if block:
            print(json.dumps({"decision": "block", "reason": block}))
PYEOF
py_rc=$?
set -e
[ "$py_rc" -eq 0 ] || emit_off "heuristic-python-failed" "$event"
