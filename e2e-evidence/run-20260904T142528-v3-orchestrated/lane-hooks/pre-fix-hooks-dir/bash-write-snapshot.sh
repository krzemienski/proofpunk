#!/bin/sh
# Proofpunk PreToolUse baseline — records protected paths before a Bash call.
#
# Matcher: Bash. NEVER denies. Always exit 0 with no stdout, so per the hooks
# reference it registers "no decision" and the call proceeds untouched.
#
# Its only job is to leave a baseline that bash-write-notice.sh diffs
# afterward. Without a pre-command snapshot, a post-command scan cannot
# attribute a change to THIS call.
#
# Three deliberate design choices:
#   1. Never parse shell. A write is detected by its effect on disk, so
#      `cp -p`, `mv -f`, `touch -c`, `sed -i -e` behave exactly as before.
#      An earlier attempt parsed commands to deny and falsely blocked all four.
#   2. Hash content, not mtime+size. `cp -p` preserves mtime, and equal-size
#      substitution is exactly the tampering that matters most.
#   3. Scope to protected paths only — evidence dirs and test-shaped paths —
#      so the cost is bounded. A full-tree walk on every Bash call is not
#      worth paying for.
# State is keyed per session+tool_use_id and written atomically, so parallel
# Bash calls cannot clobber each other's baselines.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import hashlib, json, os, re, sys, tempfile

try:
    data = json.loads(os.environ["PROOFPUNK_HOOK_INPUT"])
except Exception:
    sys.exit(0)

if (data.get("tool_name") or "") != "Bash":
    sys.exit(0)

cwd = data.get("cwd") or ""
if not cwd or not os.path.isdir(cwd):
    sys.exit(0)

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next", ".turbo"}
PROTECTED_DIR = re.compile(r"(^|/)(e2e-)?evidence(/|$)")
TEST_PATH = re.compile(
    r"(_?tests?_|__tests__|\.spec\.|\.test\.|/tests?/|/test_|_test\.|/testing/)", re.I
)
LIMIT = 4000

def sha(p):
    try:
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None

files = {}
complete = False
try:
    for dirpath, dirnames, filenames in os.walk(cwd):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        rel_dir = os.path.relpath(dirpath, cwd)
        in_protected = bool(PROTECTED_DIR.search("/" + rel_dir.replace(os.sep, "/")))
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            r = os.path.relpath(p, cwd)
            if not (in_protected or TEST_PATH.search("/" + r)):
                continue
            try:
                if not in_protected and os.path.getsize(p) > 4_000_000:
                    continue
            except OSError:
                continue
            files[p] = sha(p)
            if len(files) > LIMIT:
                raise StopIteration
    complete = True
except StopIteration:
    complete = False          # truncated: Post must not classify created/deleted
except OSError:
    complete = False

key = hashlib.sha256(
    f"{data.get('session_id') or ''}:{data.get('tool_use_id') or ''}:{cwd}".encode()
).hexdigest()[:32]
d = os.path.expanduser("~/.proofpunk/bash-baselines")
try:
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, "w") as fh:
        json.dump({"root": cwd, "complete": complete, "files": files}, fh)
    os.replace(tmp, os.path.join(d, key + ".json"))
except OSError:
    pass

sys.exit(0)
PYEOF
