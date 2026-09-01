#!/bin/sh
# Proofpunk PostToolUse detector — reports Bash writes the guards never saw.
#
# Matcher: Bash. NEVER denies. Always exit 0, speaking only through
# additionalContext.
#
# WHAT THIS IS NOT: it does not close the Bash write bypass. The three
# PreToolUse guards (no-test-files, evidence-guard, capture-guard) are
# registered on Write|Edit, so a Bash-authored write never reaches them, and
# by the time this runs the write already happened. This is detection-only
# mitigation. It is scoped that way on purpose: an earlier attempt at
# prevention parsed shell to decide a deny and falsely blocked `cp -p`,
# `mv -f`, `touch -c` and `sed -i -e`.
#
# Detection is by EFFECT — bash-write-snapshot.sh hashes protected paths at
# PreToolUse, this re-hashes them after. A command that changes nothing emits
# nothing, whatever it looked like, so no false positive can interfere with a
# working command. Content hashing (not mtime+size) means `cp -p` and
# equal-size substitution are still caught.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import hashlib, json, os, re, sys

try:
    data = json.loads(os.environ["PROOFPUNK_HOOK_INPUT"])
except Exception:
    sys.exit(0)

EVENT = data.get("hook_event_name") or "PostToolUse"

if (data.get("tool_name") or "") != "Bash":
    sys.exit(0)

cwd = data.get("cwd") or ""
if not cwd or not os.path.isdir(cwd):
    sys.exit(0)

key = hashlib.sha256(
    f"{data.get('session_id') or ''}:{data.get('tool_use_id') or ''}:{cwd}".encode()
).hexdigest()[:32]
state = os.path.join(os.path.expanduser("~/.proofpunk/bash-baselines"), key + ".json")

try:
    import time
    _d = os.path.dirname(state)
    for _fn in os.listdir(_d):
        _fp = os.path.join(_d, _fn)
        if time.time() - os.path.getmtime(_fp) > 3600:
            os.unlink(_fp)
except OSError:
    pass

try:
    with open(state) as fh:
        base = json.load(fh)
except Exception:
    sys.exit(0)
finally:
    try:
        os.unlink(state)   # one baseline per call; never reused
    except OSError:
        pass

if base.get("root") != cwd:
    sys.exit(0)
prior = base.get("files") or {}
if not base.get("complete", False):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": EVENT,
        "additionalContext": "proofpunk: the pre-command baseline for this Bash call was "
        "incomplete (protected-path scan hit its cap), so Bash-authored writes to evidence "
        "or test paths cannot be detected for this call. Treat guard coverage as OFF here."}}))
    sys.exit(0)

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".turbo"}
PROTECTED_DIR = re.compile(r"(^|/)(e2e-)?evidence(/|$)")
TEST_PATH = re.compile(
    r"(_?tests?_|__tests__|\.spec\.|\.test\.|/tests?/|/test_|_test\.|/testing/)", re.I
)

def sha(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None

now = {}
try:
    for dirpath, dirnames, filenames in os.walk(cwd):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        rel_dir = os.path.relpath(dirpath, cwd)
        in_protected = bool(PROTECTED_DIR.search("/" + rel_dir.replace(os.sep, "/")))
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            r = os.path.relpath(fp, cwd)
            if not (in_protected or TEST_PATH.search("/" + r)):
                continue
            try:
                # No size cap inside evidence: a large capture is exactly the
                # artifact whose tampering matters most.
                if not in_protected and os.path.getsize(fp) > 4_000_000:
                    continue
            except OSError:
                continue
            now[fp] = sha(fp)
except OSError:
    sys.exit(0)

created = [p for p in now if p not in prior]
modified = [p for p in now if p in prior and now[p] != prior[p]]
deleted = [p for p in prior if p not in now]
if not created and not modified and not deleted:
    sys.exit(0)

CAPTURE_EXT = (".txt", ".log", ".out", ".err", ".jsonl", ".png", ".webp", ".har", ".csv")
SECRET = re.compile(
    r"(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|AKIA[0-9A-Z]{12,}|BEGIN [A-Z ]*PRIVATE KEY"
    r"|(api_key|secret_key|access_token)\s*=\s*['\"][^'\"]{8,})",
    re.I,
)

findings = []
for p in created + modified:
    r = os.path.relpath(p, cwd)
    if TEST_PATH.search("/" + r):
        findings.append(
            f"TEST FILE written via Bash: {r} — the write path proves work by driving "
            "the real system as the end user, never by writing test files"
        )
    if PROTECTED_DIR.search("/" + r.replace(os.sep, "/")):
        if p in modified and p.endswith(CAPTURE_EXT):
            findings.append(
                f"EXISTING EVIDENCE CAPTURE MODIFIED via Bash: {r} — captures are "
                "immutable once written; a modified capture is a fabricated claim"
            )
        try:
            if os.path.getsize(p) < 1_000_000:
                with open(p, errors="ignore") as fh:
                    if SECRET.search(fh.read()):
                        findings.append(
                            f"SECRET-SHAPED CONTENT IN EVIDENCE: {r} — evidence is "
                            "committed and public; redact before this lands"
                        )
        except OSError:
            pass

for dp in deleted:
    r = os.path.relpath(dp, cwd)
    if PROTECTED_DIR.search("/" + r.replace(os.sep, "/")):
        findings.append(
            f"EVIDENCE DELETED via Bash: {r} — sealed evidence is immutable; "
            "deleting a capture destroys the proof it carried"
        )

if not findings:
    sys.exit(0)

msg = (
    "proofpunk: a Bash command changed protected files without passing the PreToolUse "
    "guards, which are registered on Write|Edit only. Detected by hashing before and "
    "after the call — not by parsing the command. "
    + " | ".join(findings[:5])
    + ". This is a NOTICE, not a block: the write already happened and nothing was "
    "undone. Remediate now if it broke a rule you meant to honor."
)
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": EVENT,
        "additionalContext": msg,
    }
}))
sys.exit(0)
PYEOF
