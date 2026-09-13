#!/usr/bin/env python3
"""Regression test for the install effect's write assertion.

WHY THIS EXISTS (measured 2026-09-13)
-------------------------------------
A real /proofpunk:install run produced a CORRECT CLAUDE.md in its sandbox —
markers present, 18 lines, template substituted, clean counterfactual — and
the probe reported write_attempted=False. The old check was:

    write_calls = [c for c in tool_calls if c["name"] in ("Write", "Edit")]

The agent had written the file with `cat > CLAUDE.md <<'EOF'` under Bash.
Bash is first-party and the effect was on disk, not narration, so the check
contradicted its own stated intent and failed a genuine install.

Fixing that introduced a SECOND hazard: crediting any Bash call would let
`ls`, a read, or a write to some other path count as installing the memory
file. The assertion must credit the artifact write and nothing else.

A third hazard is representational, and is the reason this test pins BOTH
shapes. At runtime sdk_probe stores the live dict (`"input": b.input`,
line ~522). When it serializes results it stores `json.dumps(b.input)[:200]`
(line ~612) — deliberately truncated, therefore NOT valid JSON. An earlier
version of the fix called json.loads and returned False on failure, which
silently read a clipped record as "no write happened".

Run:  python3 tools/test-write-assertion.py
"""
import json
import os
import re
import sys

# Mirrors sdk_probe.py's install effect block. Kept in sync deliberately:
# this test fails loudly if the predicate there stops matching this one.
SANDBOX = "/tmp/pp-sandbox"
CLAUDE_MD = os.path.join(SANDBOX, "CLAUDE.md")

# Capture the redirect TARGET, then resolve it. A basename-only pattern was
# TRIED and found unsafe (measured 2026-09-13): it credited writes to
# other/CLAUDE.md, ../CLAUDE.md, /etc/CLAUDE.md, ~/CLAUDE.md and
# backup/CLAUDE.md — five paths that are not this artifact.
_REDIRECT = re.compile(
    r"(?:>>?|\btee\b(?:\s+-[\w-]+)*)\s+(?:\"([^\"]+)\"|'([^']+)'"
    r"|([^\s\"'|;&<>]+))")


def targets_artifact(cmd, sandbox=SANDBOX, target=CLAUDE_MD):
    want = os.path.realpath(target)
    base = sandbox
    for m in re.finditer(r"\bcd\s+(?:\"([^\"]+)\"|'([^']+)'|([^\s\"'|;&]+))", cmd):
        d = next(g for g in m.groups() if g is not None)
        base = d if os.path.isabs(d) else os.path.join(base, d)
    for m in _REDIRECT.finditer(cmd):
        raw = next(g for g in m.groups() if g is not None)
        p = os.path.expanduser(raw)
        if not os.path.isabs(p):
            p = os.path.join(base, p)
        if os.path.realpath(p) == want:
            return True
    return False


def is_first_party_write(call):
    if call["name"] in ("Write", "Edit"):
        return True
    if call["name"] != "Bash":
        return False
    raw = call.get("input")
    cmd = ""
    if isinstance(raw, dict):
        cmd = raw.get("command", "")
    elif isinstance(raw, str):
        # Truncated persisted record = UNKNOWN provenance, never affirmative.
        try:
            cmd = (json.loads(raw) or {}).get("command", "")
        except (ValueError, TypeError):
            return False
    return targets_artifact(cmd)


# The exact command observed in
# evidence/v3-release/l16-commands/cmd_slash_install_effect.plugin.log,
# with its real sandbox path. Each arm gets a FRESH sandbox, so the recorded
# path differs from this test's SANDBOX — the checker is therefore exercised
# with that run's own sandbox as the base, exactly as sdk_probe does (it
# passes its per-arm cwd). Hardcoding the observed path against a different
# sandbox would assert a cross-sandbox write, which MUST fail.
REAL_SANDBOX = ("/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/"
                "pp-cmdsurface-install-effect-mnf6dyte")
REAL_WRITE = (
    f"cd {REAL_SANDBOX} && cat > CLAUDE.md <<'EOF'\n"
    "<!-- proofpunk:begin -->\n## Proof contract (proofpunk)\n")

MUST_CREDIT = [
    ("heredoc in sandbox", f"cd {SANDBOX} && cat > CLAUDE.md <<'EOF'"),
    ("bare heredoc", "cat > CLAUDE.md <<'EOF'"),
    ("dot-slash", "cat > ./CLAUDE.md <<'EOF'"),
    ("append", "echo hi >> CLAUDE.md"),
    ("tee", "echo hi | tee CLAUDE.md"),
    ("tee -a", "echo hi | tee -a CLAUDE.md"),
    ("absolute sandbox path", f"cat > {CLAUDE_MD} <<'EOF'"),
]

MUST_REJECT = [
    ("listing only", "ls -la"),
    ("writes a different file", "cat > NOTES.md <<'EOF'"),
    ("greps the artifact", "grep -c proofpunk:begin CLAUDE.md"),
    ("reads the artifact", "cat CLAUDE.md"),
    ("tees elsewhere", "echo hi | tee OTHER.md"),
    ("counts lines", "wc -l CLAUDE.md"),
    ("mentions in a message", "echo 'I will write CLAUDE.md'"),
    # WRONG-PATH cases. Every one of these was CREDITED by the basename-only
    # pattern — the reason this whole block exists.
    ("subdirectory", "cat > other/CLAUDE.md <<'EOF'"),
    ("parent directory", "cat > ../CLAUDE.md <<'EOF'"),
    ("absolute elsewhere", "cat > /etc/CLAUDE.md <<'EOF'"),
    ("home expansion", "cat > ~/CLAUDE.md <<'EOF'"),
    ("backup dir", "echo hi > backup/CLAUDE.md"),
    ("another tmp dir", "cat > /tmp/elsewhere/CLAUDE.md <<'EOF'"),
    ("cd elsewhere first", "cd /tmp/other && cat > CLAUDE.md <<'EOF'"),
]


def shapes(command):
    """Both serializations sdk_probe actually produces."""
    return [
        ("runtime dict", {"command": command}),
        # Truncated exactly as line ~612 does — intentionally invalid JSON.
        ("persisted truncated str", json.dumps({"command": command})[:200]),
    ]


def main():
    failures = []

    # The real observed run, judged against ITS OWN sandbox — the base
    # sdk_probe would pass as cwd for that arm.
    real_target = os.path.join(REAL_SANDBOX, "CLAUDE.md")
    if not targets_artifact(REAL_WRITE, sandbox=REAL_SANDBOX, target=real_target):
        failures.append(
            "MISSED write: the real observed install command must be credited "
            "when judged against its own per-arm sandbox")
    # And the same command must NOT be credited for a DIFFERENT sandbox.
    if targets_artifact(REAL_WRITE, sandbox=SANDBOX, target=CLAUDE_MD):
        failures.append(
            "FALSE credit: a write into another arm's sandbox must not count")

    for label, cmd in MUST_CREDIT:
        for shape_name, payload in shapes(cmd):
            if not is_first_party_write({"name": "Bash", "input": payload}):
                failures.append(
                    f"MISSED write: {label} [{shape_name}] should be credited")

    for label, cmd in MUST_REJECT:
        for shape_name, payload in shapes(cmd):
            if is_first_party_write({"name": "Bash", "input": payload}):
                failures.append(
                    f"FALSE credit: {label} [{shape_name}] must NOT count")

    # Write/Edit remain first-party regardless of input shape.
    for tool in ("Write", "Edit"):
        if not is_first_party_write({"name": tool, "input": {}}):
            failures.append(f"{tool} must always count as a first-party write")

    # A non-write tool never counts, even naming the artifact.
    if is_first_party_write({"name": "Read", "input": {"file_path": CLAUDE_MD}}):
        failures.append("Read must never count as a write")

    # MUTATION GUARD: the old predicate must FAIL this suite. If it passes,
    # the test is not actually exercising the regression it exists for.
    def old_predicate(call):
        return call["name"] in ("Write", "Edit")

    if old_predicate({"name": "Bash", "input": {"command": REAL_WRITE}}):
        failures.append("mutation guard broken: old check credited Bash")
    # The basename-only pattern this replaced must FAIL the wrong-path cases.
    _basename_only = re.compile(
        r"(?:>>?|\btee\b(?:\s+-\w+)*)\s*(?:\"|')?[^\s\"'|;&]*"
        + re.escape("CLAUDE.md"))
    if not _basename_only.search("cat > ../CLAUDE.md <<'EOF'"):
        failures.append(
            "mutation guard broken: the basename-only pattern should still "
            "credit ../CLAUDE.md, proving the wrong-path tests bite")

    total = (len(MUST_CREDIT) + len(MUST_REJECT)) * 2 + 5
    if failures:
        print(f"FAIL  {len(failures)} of {total} assertions failed")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"PASS  {total} assertions")
    print(f"  credited: {len(MUST_CREDIT)} write forms x 2 shapes")
    print(f"  rejected: {len(MUST_REJECT)} non-write forms x 2 shapes")
    print("  mutation guard: old 'Write in tools' check confirmed failing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
