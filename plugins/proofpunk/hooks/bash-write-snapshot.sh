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
#   2. Signature on size+mtime+ctime+inode, not content. ctime is set by the
#      kernel and cannot be forged from userspace, so `cp -p` and equal-size
#      substitution with a restored mtime are still caught -- verified by test.
#      Content hashing was removed: 10k protected files cost 15.5s per Bash
#      call and always blew the cap, silently disabling the guard.
#   3. Scope to protected paths only — evidence dirs and test-shaped paths —
#      so the cost is bounded. A full-tree walk on every Bash call is not
#      worth paying for.
# State is keyed per session+tool_use_id and written atomically, so parallel
# Bash calls cannot clobber each other's baselines.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import fnmatch, hashlib, json, os, re, sys, tempfile

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
# Vendored / generated trees are never user-authored, but their bundled test
# files flooded the scan (10,782 -> 595 false matches on a real repo).
SKIP_RX = re.compile(
    r"^(\.?venv[-_.].*|\.?virtualenv.*|site-packages|\.mypy_cache|\.pytest_cache"
    r"|\.tox|\.eggs|.*\.egg-info|\.ruff_cache|\.ipynb_checkpoints)$"
)
PROTECTED_DIR = re.compile(r"(^|/)(e2e-)?evidence(/|$)")
TEST_PATH = re.compile(
    r"(_?tests?_|__tests__|\.spec\.|\.test\.|/tests?/|/test_|_test\.|/testing/)", re.I
)
LIMIT = 100000  # stat signatures are ~400x cheaper than sha256; cap no longer binds

def _extra_prunes(root):
    """Optional per-repo prune list: .proofpunk-ignore at the repo root, one
    directory-name glob per line, '#' comments allowed. Bulk artifact trees
    (frame dumps, render caches) can hold tens of thousands of files that never
    match a protected pattern -- 81,397 walked / 0 matched in one real repo.
    Pruning them is a pure latency win. Absent file = unchanged behavior."""
    literals, globs = set(), []
    try:
        with open(os.path.join(root, ".proofpunk-ignore")) as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if not line:
                    continue
                # Split literals from globs. fnmatch is ~100x slower than a set
                # probe and the walk evaluates this for EVERY directory, so a
                # few hundred literal names must not become a few hundred
                # fnmatch calls per dir (measured: 2.17s -> 4.99s per Bash call
                # when 451 literals all went through fnmatch).
                if any(c in line for c in "*?["):
                    globs.append(line)
                else:
                    literals.add(line)
    except OSError:
        pass
    return literals, globs


PRUNE_LIT, PRUNE_GLOB = _extra_prunes(cwd)


def sha(p):
    # Stat signature, not content hash. Content hashing 10k protected files cost
    # 7.8s per pass (15.5s per Bash call) on a real repo and always blew the cap,
    # which silently disabled the guard entirely.
    #
    # st_ctime_ns is the load-bearing field: it is set by the kernel on any inode
    # or content change and CANNOT be forged from userspace. Verified empirically:
    # overwriting content and calling os.utime() to restore mtime leaves
    # size+mtime+inode byte-identical (attack succeeds) while ctime still moves
    # (attack detected). So this catches `cp -p` and equal-size substitution --
    # the exact cases content hashing existed for -- at ~0.02s per pass.
    try:
        s = os.stat(p)
        return f"{s.st_size}:{s.st_mtime_ns}:{s.st_ctime_ns}:{s.st_ino}"
    except OSError:
        return None

files = {}
complete = False
try:
    for dirpath, dirnames, filenames in os.walk(cwd):
        dirnames[:] = [d for d in dirnames
                   if d not in SKIP and not SKIP_RX.match(d)
                   and d not in PRUNE_LIT
                   and not any(fnmatch.fnmatch(d, q) for q in PRUNE_GLOB)]
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
