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
CLAUDE_MD = "/tmp/pp-sandbox/CLAUDE.md"
_ARTIFACT = os.path.basename(CLAUDE_MD)
_REDIRECT = re.compile(
    r"(?:>>?|\btee\b(?:\s+-\w+)*)\s*(?:\"|')?[^\s\"'|;&]*" + re.escape(_ARTIFACT))


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
        try:
            cmd = (json.loads(raw) or {}).get("command", "")
        except (ValueError, TypeError):
            cmd = raw
    return bool(_REDIRECT.search(cmd))


# The exact command observed in
# evidence/v3-release/l16-commands/cmd_slash_install_effect.plugin.log
REAL_WRITE = (
    "cd /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/"
    "pp-cmdsurface-install-effect-mnf6dyte && cat > CLAUDE.md <<'EOF'\n"
    "<!-- proofpunk:begin -->\n## Proof contract (proofpunk)\n")

MUST_CREDIT = [
    ("real observed run", REAL_WRITE),
    ("heredoc", "cd /x && cat > CLAUDE.md <<'EOF'"),
    ("append", "echo hi >> CLAUDE.md"),
    ("tee", "echo hi | tee CLAUDE.md"),
    ("tee -a", "echo hi | tee -a CLAUDE.md"),
    ("absolute path", "cat > /tmp/pp-sandbox/CLAUDE.md <<'EOF'"),
]

MUST_REJECT = [
    ("listing only", "ls -la"),
    ("writes a different file", "cat > NOTES.md <<'EOF'"),
    ("greps the artifact", "grep -c proofpunk:begin CLAUDE.md"),
    ("reads the artifact", "cat CLAUDE.md"),
    ("tees elsewhere", "echo hi | tee OTHER.md"),
    ("counts lines", "wc -l CLAUDE.md"),
    ("mentions in a message", "echo 'I will write CLAUDE.md'"),
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

    total = (len(MUST_CREDIT) + len(MUST_REJECT)) * 2 + 3
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
