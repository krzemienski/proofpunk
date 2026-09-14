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
# Detection is by EFFECT - bash-write-snapshot.sh records a stat signature
# (size+mtime_ns+ctime_ns+inode) for protected paths at PreToolUse, this
# re-reads it after. A command that changes nothing emits nothing, whatever it
# looked like, so no false positive can interfere with a working command.
#
# The load-bearing field is st_ctime_ns, NOT a content hash. This comment used
# to claim "Content hashing (not mtime+size)"; the implementation has never
# hashed capture bytes -- sha256 appears in bash-write-snapshot.sh only to hash
# the baseline LOOKUP KEY (session:tool_use_id:cwd). Corrected 2026-09-14 after
# an audit read the comment and the code side by side. ctime_ns is set by the
# kernel on any inode or content change and cannot be forged from userspace, so
# `cp -p` and equal-size substitution -- the exact cases content hashing existed
# for -- are still caught, at ~400x lower cost. See bash-write-snapshot.sh:103.
set -eu

input=$(cat)

# Fail open when python3 is unavailable. Without this guard `set -eu` plus
# the python heredoc below exits 127, which the harness surfaces as a hook
# error on every matched tool call. This hook never denies, so it emits an
# observable enforcement-OFF notice and exits 0 -- silence would be
# indistinguishable from a clean run.
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "{\"hookSpecificOutput\":{\"hookEventName\":\"PostToolUse\",\"additionalContext\":\"Proofpunk: bash-write-notice enforcement OFF (python3-not-found).\"}}"
  exit 0
fi

export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import fnmatch, hashlib, json, os, re, sys

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

now = {}
try:
    for dirpath, dirnames, filenames in os.walk(cwd):
        dirnames[:] = [d for d in dirnames
                   if d not in SKIP and not SKIP_RX.match(d)
                   and d not in PRUNE_LIT
                   and not any(fnmatch.fnmatch(d, q) for q in PRUNE_GLOB)]
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
    "guards, which are registered on Write, Edit and MCP mutation tools - not on Bash. "
    "Detected by comparing a size+mtime_ns+ctime_ns+inode signature before and after "
    "the call - not by parsing the command, and not by hashing contents. "
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
