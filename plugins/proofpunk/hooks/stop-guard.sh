#!/bin/sh
# Proofpunk Stop/SubagentStop guard — the unproven-completion detector.
#
# Reads the session transcript (JSONL) from the hook input and applies the
# deterministic heuristic documented in docs/hooks-and-init-design.md §2:
#   claim without cited proof artifact  → decision:block (reason feeds back)
#   claim + proof but no scout record   → decision:block (scout is mandatory)
#   anything else                       → SILENT (exit 0, no output)
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

cwd=$(printf '%s' "$input" | python3 -c "
import json, sys
try:
    print(json.load(sys.stdin).get('cwd', ''))
except Exception:
    print('')
" 2>/dev/null || true)

python3 - "$transcript" "$cwd" <<'PYEOF' 2>/dev/null || true
import json, os, re, sys

path = sys.argv[1]
cwd = sys.argv[2] if len(sys.argv) > 2 else ""

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
    lines = []

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
