#!/usr/bin/env python3
"""
session_intent.py — reconstruct per-session intent from Claude Code transcripts.

Reads ~/.claude/projects/<project-slug>/*.jsonl (each line one event) and emits
a per-session intent record: first user prompt (the session's stated intent),
all subsequent user prompts (steering), tool usage, files touched, git commits
observed in bash commands, branches, models, and time bounds.

Sessions are EVIDENCE. Session summaries, commit messages, and docs are CLAIMS.
This tool only reports what is literally in the transcript; unrecoverable
intent is reported as null, never invented.

Stdlib only. Usage:
  python3 session_intent.py [--projects-dir ~/.claude/projects]
                            [--project SUBSTR] [--since YYYY-MM-DD] [--until YYYY-MM-DD]
                            [--json out.json] [--md out.md]
"""
import argparse, json, os, re, sys, glob
from datetime import datetime, timezone

COMMIT_RE = re.compile(r'\bgit\s+commit\b')
REV_PARSE_RE = re.compile(r'\bgit\s+rev-parse\b')
FILE_KEYS = ("file_path", "notebook_path", "path")

def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None

def text_blocks(content):
    """Yield text from a message content that is str or list-of-blocks."""
    if isinstance(content, str):
        yield content
    elif isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str):
                yield b["text"]

def is_tool_result(content):
    return isinstance(content, list) and any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content)

def scan_file(path):
    sessions = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            sid = ev.get("sessionId") or os.path.basename(path)
            s = sessions.setdefault(sid, {
                "session_id": sid, "transcript": path,
                "project_dir": ev.get("cwd"), "git_branch": ev.get("gitBranch"),
                "start": None, "end": None,
                "first_prompt": None, "user_prompts": [],
                "tool_counts": {}, "models": set(),
                "files_touched": set(), "bash_commits": 0, "bash_commands": 0,
            })
            ts = parse_ts(ev.get("timestamp"))
            if ts:
                s["start"] = ts if s["start"] is None else min(s["start"], ts)
                s["end"] = ts if s["end"] is None else max(s["end"], ts)
            if ev.get("cwd") and not s["project_dir"]:
                s["project_dir"] = ev["cwd"]
            if ev.get("gitBranch") and not s["git_branch"]:
                s["git_branch"] = ev["gitBranch"]
            msg = ev.get("message") or {}
            model = msg.get("model")
            if model:
                s["models"].add(model)
            etype = ev.get("type")
            content = msg.get("content")
            if etype == "user" and not is_tool_result(content):
                for t in text_blocks(content):
                    t = t.strip()
                    if not t or t.startswith("<local-command") or t.startswith("<command-"):
                        continue
                    s["user_prompts"].append(t)
                    if s["first_prompt"] is None:
                        s["first_prompt"] = t
            elif etype == "assistant" and isinstance(content, list):
                for b in content:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"):
                        continue
                    name = b.get("name", "?")
                    s["tool_counts"][name] = s["tool_counts"].get(name, 0) + 1
                    inp = b.get("input") or {}
                    for k in FILE_KEYS:
                        v = inp.get(k)
                        if isinstance(v, str) and v:
                            s["files_touched"].add(v)
                    if name == "Bash":
                        cmd = inp.get("command") or ""
                        if cmd:
                            s["bash_commands"] += 1
                            if COMMIT_RE.search(cmd):
                                s["bash_commits"] += 1
    return sessions

def to_public(s):
    return {
        "session_id": s["session_id"],
        "transcript": s["transcript"],
        "project_dir": s["project_dir"],
        "git_branch": s["git_branch"],
        "start": s["start"].isoformat() if s["start"] else None,
        "end": s["end"].isoformat() if s["end"] else None,
        "intent": s["first_prompt"],          # None == intent unrecoverable
        "steering_prompts": len(s["user_prompts"]) - (1 if s["first_prompt"] else 0),
        "user_prompts": s["user_prompts"],
        "tool_counts": dict(sorted(s["tool_counts"].items(), key=lambda kv: -kv[1])),
        "models": sorted(s["models"]),
        "files_touched": sorted(s["files_touched"]),
        "bash_commands": s["bash_commands"],
        "git_commits_in_session": s["bash_commits"],
    }

def render_md(rows):
    out = ["# Session Intent Matrix", "",
           "| session | project | branch | window | intent (first user prompt) | steering | commits | top tools |",
           "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        intent = (r["intent"] or "*intent unrecoverable*").replace("|", "\\|")
        intent = intent[:120] + ("…" if len(intent) > 120 else "")
        window = "{} → {}".format((r["start"] or "?")[:16], (r["end"] or "?")[11:16])
        tools = ", ".join(f"{k}×{v}" for k, v in list(r["tool_counts"].items())[:4])
        out.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            r["session_id"][:8], os.path.basename(r["project_dir"] or "?"),
            r["git_branch"] or "?", window, intent, r["steering_prompts"],
            r["git_commits_in_session"], tools))
    return "\n".join(out) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--project", default=None, help="substring filter on project dir slug or cwd")
    ap.add_argument("--since", default=None)
    ap.add_argument("--until", default=None)
    ap.add_argument("--json", dest="json_out", default=None)
    ap.add_argument("--md", dest="md_out", default=None)
    a = ap.parse_args()

    since = parse_ts(a.since + "T00:00:00+00:00") if a.since else None
    until = parse_ts(a.until + "T23:59:59+00:00") if a.until else None

    files = sorted(glob.glob(os.path.join(a.projects_dir, "**", "*.jsonl"), recursive=True))
    if not files:
        print(f"NO TRANSCRIPTS: no *.jsonl under {a.projects_dir}", file=sys.stderr)
        sys.exit(2)

    rows = []
    for f in files:
        for s in scan_file(f).values():
            if a.project:
                hay = " ".join([f, s["project_dir"] or ""])
                if a.project not in hay:
                    continue
            if since and s["end"] and s["end"] < since:
                continue
            if until and s["start"] and s["start"] > until:
                continue
            rows.append(to_public(s))
    rows.sort(key=lambda r: r["start"] or "")

    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
    if a.md_out:
        with open(a.md_out, "w", encoding="utf-8") as fh:
            fh.write(render_md(rows))
    print(f"{len(rows)} sessions from {len(files)} transcript files")
    if not (a.json_out or a.md_out):
        print(render_md(rows))

if __name__ == "__main__":
    main()
