#!/usr/bin/env python3
"""intent_verdict.py — record and query the intent-verification verdict.

The stop guards ask "was a completion claimed without evidence?". That misses
the more expensive failure: a session that produced real evidence for work
nobody asked for, or for a fraction of what was asked. Every existing gate goes
green on that session.

This helper is the mechanical half of the fix (contract:
`references/intent-verification.md`). The MODEL reads the session and judges
whether the original intent was met; this script records that judgment and
answers the one question a stop guard can check without pretending to
comprehend anything:

    may this session stop?

Commands:
  recover <transcript>        print the session's verbatim first user request
  record --verdict MET|UNMET|PARTIAL [--unmet TEXT]...   write the verdict
  status                      print the verdict as JSON (exit 0 even if absent)
  may-stop                    exit 0 if the session may end, 2 if it may not

Identity comes from --session-id and --cwd, or $PROOFPUNK_SESSION_ID / $PWD.

Exit codes: 0 success / allowed, 2 refusal or stop-not-allowed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# Same namespace convention as bash-write-snapshot.sh:147. A home-relative
# path is reachable identically from a shell hook, an OMP extension and an
# OpenCode plugin -- none of them needs a platform API to find it.
ROOT = Path(os.path.expanduser("~/.proofpunk/intent"))

# Operator-approved 2026-09-12. Attempts 1 and 2 restart; the 3rd escalates.
# An unbounded retry on an unachievable goal burns the budget and surfaces as
# exhaustion rather than as a diagnosis.
MAX_ATTEMPTS = 3

# .planning/plugin-improvement-criteria.md:41 permits exactly four verdicts:
# PASS / FAIL / BLOCKED / UNVERIFIED. An earlier draft of this file invented
# "PARTIAL", which is the half-credit this project's own criteria forbid --
# and the exact error corrected in the v4 status report hours earlier.
#
# The mapping onto intent:
#   MET         the original request was accomplished          (PASS)
#   UNMET       it was not                                     (FAIL)
#   UNVERIFIABLE the session cannot be judged -- transcript     (UNVERIFIED)
#               unreadable, intent unrecoverable
# There is deliberately no partial grade. "Three of four clauses" is UNMET
# with the fourth named in `unmet`; a request is not partially satisfied any
# more than a criterion is partially passed.
VERDICTS = ("MET", "UNMET", "UNVERIFIABLE")


def key_for(session_id: str, cwd: str) -> str:
    return hashlib.sha256(f"{session_id}:{cwd}".encode()).hexdigest()[:32]


def path_for(session_id: str, cwd: str) -> Path:
    return ROOT / (key_for(session_id, cwd) + ".json")


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def recover_intent(transcript: str) -> str:
    """Return the verbatim first user request from a session transcript.

    Verbatim matters: grading against a summary grades the summary. The first
    `user` record carrying real text is the original ask -- measured against
    real transcripts under ~/.claude/projects/, every one of which carries
    typed `user` records with the opening request intact.
    """
    p = Path(transcript)
    if not p.is_file():
        return ""
    try:
        with p.open(errors="ignore") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if rec.get("type") != "user":
                    continue
                content = (rec.get("message") or {}).get("content")
                if isinstance(content, str):
                    text = content
                elif isinstance(content, list):
                    text = " ".join(
                        b.get("text", "") for b in content if isinstance(b, dict)
                    )
                else:
                    continue
                if text.strip():
                    return text.strip()
    except OSError:
        return ""
    return ""


def load(session_id: str, cwd: str) -> dict:
    f = path_for(session_id, cwd)
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text())
    except (OSError, json.JSONDecodeError, ValueError):
        # A corrupt verdict is not a passing verdict. Returning {} routes
        # may-stop to "no verdict recorded", which blocks.
        return {}


def save(session_id: str, cwd: str, data: dict) -> Path:
    ROOT.mkdir(parents=True, exist_ok=True)
    f = path_for(session_id, cwd)
    fd, tmp = tempfile.mkstemp(dir=str(ROOT))
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, f)  # atomic: a half-written verdict never appears
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return f


def cmd_record(args) -> int:
    if args.verdict not in VERDICTS:
        print(f"verdict must be one of {', '.join(VERDICTS)}", file=sys.stderr)
        return 2
    prior = load(args.session_id, args.cwd)

    # The attempt counter lives in the verdict file so it survives a restart --
    # the one thing a loop bound must survive to mean anything.
    attempt = int(prior.get("attempt", 0))
    if args.verdict != "MET":
        attempt += 1

    intent = args.intent or prior.get("original_intent", "")
    if args.transcript and not intent:
        intent = recover_intent(args.transcript)

    data = {
        "session_id": args.session_id,
        "cwd": args.cwd,
        "original_intent": intent,
        "verdict": args.verdict,
        "unmet": list(args.unmet or []),
        "attempt": attempt,
        "next_prompt": args.next_prompt or "",
        "recorded": iso_now(),
    }
    # Once the cap is spent it stays spent. Dropping this on a later record
    # would let a fresh UNMET re-enter the restart branch, so the cap would
    # bound one streak instead of the run.
    if prior.get("escalated"):
        data["escalated"] = prior["escalated"]
    f = save(args.session_id, args.cwd, data)
    print(str(f))
    return 0


def cmd_status(args) -> int:
    print(json.dumps(load(args.session_id, args.cwd), indent=2))
    return 0


def cmd_may_stop(args) -> int:
    """Exit 0 if this session may end, 2 if it may not.

    This is the entire question a stop guard needs answered, and it is
    answerable without reading one word of the session.
    """
    data = load(args.session_id, args.cwd)

    if not data:
        print(
            "Proofpunk: no intent verdict recorded for this session. Before "
            "stopping, read the session's ORIGINAL request (first user message, "
            "verbatim), judge whether it was actually accomplished, and record "
            "the verdict with intent_verdict.py record. Evidence that a task ran "
            "is not evidence the asked-for thing happened.",
            file=sys.stderr,
        )
        return 2

    verdict = data.get("verdict", "")
    attempt = int(data.get("attempt", 0))

    if verdict == "MET":
        return 0

    if attempt >= MAX_ATTEMPTS:
        # Refusing to stop here would BE the unbounded loop the cap exists to
        # prevent. Allow the stop; the escalation report is the deliverable.
        #
        # `escalated` latches so the message fires exactly once and, more
        # importantly, so the post-cap state is distinguishable from the
        # pre-cap one. Without it a later `record` could push the counter
        # around and re-enter the restart branch -- the cap would bound a
        # single streak rather than the run.
        if not data.get("escalated"):
            data["escalated"] = iso_now()
            try:
                save(args.session_id, args.cwd, data)
            except OSError:
                pass  # never let a bookkeeping write failure change the verdict
            print(
                f"Proofpunk: intent still {verdict} after {attempt} attempts "
                f"(cap {MAX_ATTEMPTS}). Stopping is allowed, but this run owes "
                "an escalation report naming the unmet intent and what was "
                "tried. Do not silently drop it, and do not restart implement "
                "again -- the cap is spent.",
                file=sys.stderr,
            )
        return 0

    unmet = data.get("unmet") or []
    detail = ("; ".join(unmet))[:400] if unmet else "see the recorded verdict"
    print(
        f"Proofpunk: the original intent was not met (verdict={verdict}, "
        f"attempt {attempt} of {MAX_ATTEMPTS}). Unmet: {detail}. "
        "Write the next-session fix prompt naming exactly what is missing, then "
        "restart implement against the ORIGINAL request -- never against a "
        "restatement of it, which lets the goal drift toward whatever the last "
        "attempt found convenient.",
        file=sys.stderr,
    )
    return 2


def cmd_recover(args) -> int:
    text = recover_intent(args.transcript)
    if not text:
        print(f"no user request found in {args.transcript}", file=sys.stderr)
        return 2
    print(text)
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--session-id", default=os.environ.get("PROOFPUNK_SESSION_ID", ""))
    ap.add_argument("--cwd", default=os.getcwd())
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("recover")
    p.add_argument("transcript")
    p.set_defaults(fn=cmd_recover)

    p = sub.add_parser("record")
    p.add_argument("--verdict", required=True)
    p.add_argument("--unmet", action="append")
    p.add_argument("--intent")
    p.add_argument("--transcript")
    p.add_argument("--next-prompt")
    p.set_defaults(fn=cmd_record)

    p = sub.add_parser("status")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("may-stop")
    p.set_defaults(fn=cmd_may_stop)

    args = ap.parse_args(argv[1:])
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
