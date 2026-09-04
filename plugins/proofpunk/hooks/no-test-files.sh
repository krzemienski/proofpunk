#!/bin/sh
# Proofpunk PreToolUse guard — the write path never creates test files.
#
# Matcher: Write|Edit. Denies (exit 2, stderr fed back to Claude) when the
# target path is a test artifact:
#   *test*, *.spec.*, *.test.*, __tests__/ directories, fixtures-as-tests
# The pipeline's validation is end-user driving, never a test file.
# Warns on stderr (still exit 0) when a non-test file's content carries
# mock/stub markers (class Fake*/Mock*/Stub*, jest.mock, unittest.mock,
# sinon.stub, @patch, MagicMock, NotImplementedError placeholder body,
# TODO: implement) — a soft nudge, not a deny, so legitimate domain names
# and edits to existing test infrastructure are not blocked.
# Silent (exit 0) for everything else.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

python3 - <<'PYEOF'
import json, os, re, sys

try:
    data = json.loads(os.environ["PROOFPUNK_HOOK_INPUT"])
except Exception:
    sys.exit(0)

ti = data.get("tool_input") or {}
path = str(ti.get("file_path") or "")
if not path:
    sys.exit(0)

TEST_PATH = re.compile(
    r"(_?tests?_|__tests__|\.spec\.|\.test\.|/tests?/|/test_|_test\.|/fixtures?/.*test|/testing/)",
    re.I,
)
if TEST_PATH.search(path):
    sys.stderr.write(
        f"Proofpunk: refusing to create a test artifact ({path}). The write path validates by "
        "driving the real system as the end user — never by writing test files. If this project "
        "has a pre-existing suite and the user explicitly asked to extend it, surface that to the "
        "user and let them decide — the default is no new test files.\n"
    )
    sys.exit(2)

content = str(ti.get("content") or ti.get("new_string") or "")
MOCK_MARKERS = [
    ("a Fake/Mock/Stub class", r"\bclass\s+(?:Fake|Mock|Stub)[A-Za-z0-9_]*\b"),
    ("jest.mock", r"jest\.mock\("),
    ("unittest.mock", r"unittest\.mock"),
    ("sinon.stub", r"sinon\.stub\("),
    ("@patch", r"@patch\("),
    ("MagicMock", r"\bMagicMock\("),
    ("NotImplementedError placeholder body", r"raise\s+NotImplementedError"),
    ("TODO: implement", r"TODO:\s*implement"),
]
if content:
    for label, pat in MOCK_MARKERS:
        if re.search(pat, content):
            sys.stderr.write(
                f"Proofpunk (warn): {path} contains {label} — possible mock/stub. "
                "The pipeline validates by driving the real system, not by mocking it. "
                "Proceeding, but if this is meant as production code, replace the "
                "mock with the real implementation.\n"
            )
            break
sys.exit(0)
PYEOF
