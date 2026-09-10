#!/bin/sh
# Proofpunk PreToolUse steering guard — platform-mismatch redirect.
#
# Matcher: Bash. NEVER denies, NEVER blocks — always exit 0. This is a
# steering hook, not a stronger blocking one (v4-architecture/v4-spec.md
# §5, W5): when a Bash call looks like it is driving a validation attempt
# for the WRONG platform, it injects hookSpecificOutput.additionalContext
# naming the correct runbook and asks the agent to re-route. It never
# denies the call — a mismatch is a nudge, not a gate.
#
# Four conservative, mutually-exclusive command-shape signals (checked in
# this priority order, first match wins):
#   1. `xcrun simctl ...`                          -> implies iOS
#   2. a browser-automation tool name in the text
#      (playwright/puppeteer/selenium/webdriver/
#      chromedriver)                                -> implies Web
#   3. a repo-local built-binary invocation
#      (./bin/..., ./target/release|debug/...,
#      ./dist/...)                                  -> implies CLI
#   4. `curl` + an http(s) URL                       -> implies API or Web
#      (web validation explicitly includes API checks per
#      references/platform-routing.md, so curl in a web project is not
#      a mismatch — only curl against an iOS or CLI project is)
# Anything else in the command text is not a recognized validation shape
# and the hook stays silent — a guard that speaks on every Bash call is
# noise nobody will read.
#
# The project's actual platform is then looked up by walking UP from
# `cwd` (bounded to 6 levels, stopping at the first directory holding a
# `.git`, matching references/platform-routing.md's own Detection table:
#   .xcodeproj / Package.swift                -> ios
#   package.json w/ next|react|vite dep       -> web
#   package.json w/ a `bin` field, no web dep -> cli
#   Dockerfile / docker-compose.y*ml          -> api
#   pyproject.toml w/ [project.scripts]       -> cli
# A directory that shows more than one of these tags at once (a
# plausibly full-stack repo) is treated as ambiguous and the walk stops
# there rather than climbing past it looking for a tie-breaker higher up.
#
# MISMATCH fires only when BOTH sides are unambiguous: exactly one
# command-shape signal fired, AND exactly one project platform was
# detected, AND that platform is not among the signal's compatible set.
# Any uncertainty on either side (no signal, no detection, or a
# multi-tag directory) is silence, not a guess.
#
# Deliberately does NOT parse shell grammar or tokenize compound
# commands — that path was tried and retired in this repo for falsely
# blocking `cp -p`, `mv -f`, `touch -c`, `sed -i -e`
# (bash-write-snapshot.sh's own history). Matching is plain regex search
# over the raw command text; nothing here can misfire the way a real
# parser could, and even a misfire here only adds context, it never
# denies.
#
# Fail-open, twice over: the sh wrapper forces exit 0 unconditionally
# (python3 missing, a heredoc bug, anything) via `set +e` around the
# python3 call, and the python body itself wraps its entire logic in a
# single try/except so a malformed stdin payload, an unreadable
# package.json, or any other surprise degrades to silence rather than a
# crash. <50ms: no full-tree walk, just a handful of os.scandir /
# os.path.exists / small-file-read calls per directory level, capped at
# 6 levels.
set -eu

input=$(cat)
export PROOFPUNK_HOOK_INPUT="$input"

if ! command -v python3 >/dev/null 2>&1; then
  exit 0
fi

set +e
python3 - <<'PYEOF' 2>/dev/null
import json, os, re, sys

XCRUN_SIMCTL = re.compile(r"\bxcrun\s+simctl\b", re.I)
BROWSER_TOOL = re.compile(r"\b(?:playwright|puppeteer|selenium|webdriver|chromedriver)\b", re.I)
CLI_BINARY = re.compile(r"(?:^|&&|\|\||;)\s*\./(?:bin|target/(?:release|debug)|dist)/\S+")
HAS_CURL = re.compile(r"\bcurl\b", re.I)
HAS_URL = re.compile(r"https?://")


def classify_command(command):
    """Return (label, frozenset(compatible platforms)) for the first
    recognized validation-shaped signal in `command`, or None."""
    if XCRUN_SIMCTL.search(command):
        return ("an iOS simulator command (xcrun simctl)", frozenset({"ios"}))
    if BROWSER_TOOL.search(command):
        return ("a browser-automation invocation", frozenset({"web"}))
    if CLI_BINARY.search(command):
        return ("a locally built CLI binary", frozenset({"cli"}))
    if HAS_CURL.search(command) and HAS_URL.search(command):
        return ("a curl-based API/web check", frozenset({"api", "web"}))
    return None


def scan_dir_tags(dirpath):
    """Platform tags this single directory shows, per
    references/platform-routing.md's Detection table. Non-recursive."""
    tags = set()
    try:
        names = {e.name for e in os.scandir(dirpath)}
    except OSError:
        return tags

    if "Package.swift" in names or any(n.endswith(".xcodeproj") for n in names):
        tags.add("ios")

    if "package.json" in names:
        try:
            with open(os.path.join(dirpath, "package.json"), encoding="utf-8") as fh:
                pkg = json.load(fh)
            deps = {}
            if isinstance(pkg.get("dependencies"), dict):
                deps.update(pkg["dependencies"])
            if isinstance(pkg.get("devDependencies"), dict):
                deps.update(pkg["devDependencies"])
            if any(k in deps for k in ("next", "react", "vite")):
                tags.add("web")
            elif isinstance(pkg.get("bin"), (str, dict)):
                tags.add("cli")
        except Exception:
            pass

    if names & {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
        tags.add("api")

    if "pyproject.toml" in names:
        try:
            with open(os.path.join(dirpath, "pyproject.toml"), encoding="utf-8") as fh:
                if "[project.scripts]" in fh.read():
                    tags.add("cli")
        except Exception:
            pass

    return tags


def find_project_platform(cwd):
    """Walk up from cwd (bounded, stopping at .git) for the first
    directory with exactly one platform tag. None on no signal,
    ambiguous (multi-tag) signal, or bound/filesystem-root exhaustion."""
    d = os.path.normpath(cwd)
    for _ in range(6):
        tags = scan_dir_tags(d)
        if tags:
            return next(iter(tags)) if len(tags) == 1 else None
        if os.path.exists(os.path.join(d, ".git")):
            return None
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent
    return None


def emit(cwd, label, detected):
    runbook = f"references/{detected}-validation.md"
    msg = (
        f"proofpunk: this Bash command looks like {label}, but the project at "
        f"{cwd} matches the {detected} indicators in "
        f"references/platform-routing.md. Before proceeding, re-route to {runbook}."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": msg,
        }
    }))


def run():
    try:
        data = json.loads(os.environ.get("PROOFPUNK_HOOK_INPUT", ""))
    except Exception:
        return

    try:
        if (data.get("tool_name") or "") != "Bash":
            return

        ti = data.get("tool_input") or {}
        if not isinstance(ti, dict):
            return
        command = str(ti.get("command") or "")
        if not command:
            return

        cwd = data.get("cwd") or ""
        if not isinstance(cwd, str) or not cwd or not os.path.isdir(cwd):
            return

        signal = classify_command(command)
        if signal is None:
            return
        label, compatible = signal

        detected = find_project_platform(cwd)
        if detected is None or detected in compatible:
            return

        emit(cwd, label, detected)
    except Exception:
        return


run()
sys.exit(0)
PYEOF
set -e

exit 0
