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
import shlex
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
    #
    # Only UNMET burns an attempt. UNVERIFIABLE must not: Stage 0 opens a run by
    # recording UNVERIFIABLE (nothing has been attempted yet, so intent is
    # genuinely unjudged), and counting that would spend one of the three
    # attempts before any work happened -- capping the run after two real
    # failures. Measured before this fix: a Stage 0 record left attempt=1, and
    # the third UNMET was already past the cap.
    #
    # UNVERIFIABLE still BLOCKS in may-stop below. It does not authorize a stop;
    # it just does not consume a retry, because there is nothing to retry yet.
    attempt = int(prior.get("attempt", 0))
    if args.verdict == "UNMET":
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
    # A restart re-runs Stage 0, which records UNVERIFIABLE again. Without this,
    # that wipes the unmet list and the fix-prompt pointer written by the
    # PREVIOUS attempt -- so the restarted run is told to fix something and no
    # longer knows what. Measured: after UNMET(unmet=['clause Y missing'],
    # next='.prompts/fix.md'), a Stage 0 re-record left unmet=[] next=''.
    #
    # Carry both forward unless this record supplies its own. Only a new UNMET
    # (or an explicit --unmet/--next-prompt) may change them; MET clears them,
    # because nothing is outstanding once intent is met.
    if args.verdict != "MET":
        if not args.unmet and prior.get("unmet"):
            data["unmet"] = list(prior["unmet"])
        if not args.next_prompt and prior.get("next_prompt"):
            data["next_prompt"] = prior["next_prompt"]
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


def cmd_capture(args) -> int:
    """Record the original request WITHOUT touching any review state.

    Stage 0 runs at the start of every attempt, including restarts. Using
    `record` there is unsafe no matter how careful the merge rules are: it
    takes a --verdict, so it can always overwrite the previous attempt's
    judgment. Measured before this existed -- an UNMET carrying
    unmet=['clause Y missing'] and next='.prompts/fix.md' was reduced to
    verdict=UNVERIFIABLE, unmet=[], next='' by the next Stage 0.

    capture is initialize-if-absent by construction. It cannot express a
    verdict, so it cannot destroy one:
      - no prior state -> create it, verdict UNVERIFIABLE, attempt 0
      - prior state    -> leave verdict/attempt/unmet/next_prompt/escalated
                          exactly as they are; only fill original_intent if
                          it is missing
    The original intent is written once and never rewritten, so the goal
    cannot drift toward a later paraphrase of itself.
    """
    prior = load(args.session_id, args.cwd)
    intent = args.intent or ""
    if args.transcript and not intent:
        intent = recover_intent(args.transcript)

    if not args.session_id:
        raise SystemExit(
            "capture needs --session-id (or $PROOFPUNK_SESSION_ID): without it "
            "every session in a directory shares one verdict key"
        )

    # load() flattens a corrupt file to {}, which would make capture treat it as
    # absent and overwrite it -- destroying an unreadable-but-real verdict,
    # possibly one carrying a spent cap. Distinguish "no file" from "file I
    # cannot parse" by looking at the path directly, and refuse the latter.
    f = path_for(args.session_id, args.cwd)
    if not prior and f.exists():
        raise SystemExit(
            f"refusing to capture over unreadable state at {f}. It may hold a "
            "verdict or a spent attempt cap. Inspect it, then move it aside "
            "deliberately -- capture will not overwrite what it cannot read."
        )

    if prior:
        if not prior.get("original_intent") and intent:
            prior["original_intent"] = intent
            save(args.session_id, args.cwd, prior)
            print(f"original_intent backfilled for {args.session_id}")
        else:
            print(f"intent already captured for {args.session_id}; unchanged")
        return 0

    if not intent:
        raise SystemExit(
            "capture needs the original request: pass --intent or --transcript"
        )
    save(args.session_id, args.cwd, {
        "session_id": args.session_id,
        "cwd": args.cwd,
        "original_intent": intent,
        "verdict": "UNVERIFIABLE",
        "unmet": [],
        "attempt": 0,
        "next_prompt": "",
        "recorded": iso_now(),
    })
    print(f"captured original intent for {args.session_id}")
    return 0


def cmd_may_stop(args) -> int:
    """Exit 0 if this session may end, 2 if it may not.

    This is the entire question a stop guard needs answered, and it is
    answerable without reading one word of the session.
    """
    data = load(args.session_id, args.cwd)

    if not data:
        # Name the helper by its ABSOLUTE resolved path and give the exact
        # runnable command. A blocked agent that cannot locate this file has
        # no path to resolve and will guess — or, as observed in the field,
        # conclude the tool is not installed and stay wedged. The recovery
        # instruction must be copy-pasteable, not a filename to go find.
        _self = os.path.abspath(__file__)
        # Quote the interpolated fields: a macOS cwd like
        # "~/Library/Mobile Documents" or "My Project" would otherwise emit a
        # command that silently parses as the wrong arguments. The env-var
        # fallback is left unquoted on purpose so the shell still expands it.
        _self = shlex.quote(_self)
        _sid = (shlex.quote(args.session_id) if args.session_id
                else "\"$PROOFPUNK_SESSION_ID\"")
        _cwd = shlex.quote(args.cwd or os.getcwd())
        print(
            "Proofpunk: no intent verdict recorded for this session. Before "
            "stopping, read the session's ORIGINAL request (first user message, "
            "verbatim), judge whether it was actually accomplished, and record "
            "the verdict. Evidence that a task ran is not evidence the "
            "asked-for thing happened.\n"
            "Run exactly:\n"
            f"  python3 {_self} --session-id {_sid} --cwd {_cwd} "
            "record --verdict MET|UNMET|UNVERIFIABLE",
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

    # A stop guard that re-asks on every settle pass needs the counter to move,
    # or it blocks forever: attempts advance on `record`, and a model that
    # never re-records would be held until the runtime's own continuation cap.
    # With --consume the block itself spends an attempt, so a re-gating guard
    # is bounded by MAX_ATTEMPTS whether or not the model records again.
    if args.consume:
        data["attempt"] = attempt + 1
        try:
            save(args.session_id, args.cwd, data)
        except OSError:
            pass  # a bookkeeping failure must not change the verdict
        attempt = data["attempt"]

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


def cmd_fix_prompt(args) -> int:
    """Write the next-session fix prompt from RECORDED state.

    Stage 8 told the model to "write the fix prompt", which made the one
    artifact that carries the goal across a restart a freehand paraphrase --
    the exact drift the original-intent rule exists to stop. The prompt is
    therefore composed from the verdict file: the intent is reproduced
    verbatim and the gaps are the recorded clauses, so a restart cannot
    inherit a softened goal.
    """
    state = load(args.session_id, args.cwd)
    if not state:
        print("no verdict recorded; nothing to carry forward", file=sys.stderr)
        return 2
    if state.get("verdict") == "MET":
        # Nothing is missing, so a fix prompt would invent work.
        print("verdict is MET; no fix prompt needed", file=sys.stderr)
        return 2
    intent = state.get("original_intent", "")
    if not intent:
        print("no original intent recorded; cannot carry the goal forward",
              file=sys.stderr)
        return 2

    unmet = [u for u in state.get("unmet", []) if str(u).strip()]
    attempt = state.get("attempt", 0)
    gaps = "\n".join(f"{i}. {u}" for i, u in enumerate(unmet, 1)) or \
        "(none recorded — re-derive the gap from the original request)"

    body = f"""# Fix prompt — attempt {attempt + 1}

A previous session set out to do the following and did not finish it. This
is the ORIGINAL request, reproduced verbatim. Do not work from a summary of
it, including this file's own wording below it.

## Original request

{intent}

## What was left unmet

{gaps}

## How to proceed

1. Re-read the original request above before planning anything.
2. Close the unmet clauses. They are obligations, not suggestions; a clause
   done well beside one untouched is still UNMET.
3. Do not re-do work that is already proven. Read the prior evidence run
   first and build on it.
4. Prove each clause by driving the real system as the end user. An
   unexecuted claim is UNVERIFIED, never PASS.
5. This is attempt {attempt + 1}. At attempt {MAX_ATTEMPTS} the run escalates to a
   human instead of restarting again, so treat this as a bounded retry.
"""

    out = Path(args.out).expanduser() if args.out else None
    if out is None:
        print(body, end="")
        return 0
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        # Atomic for the same reason save() is: a truncated fix prompt still
        # parses as a fix prompt, so the next session would silently inherit
        # a goal cut off mid-sentence.
        fd, tmp = tempfile.mkstemp(dir=str(out.parent))
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(body)
            os.replace(tmp, out)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except OSError as exc:
        print(f"could not write {out}: {exc}", file=sys.stderr)
        return 2
    # Point the verdict file at the prompt so the next session can find it
    # without being told where it is.
    state["next_prompt"] = str(out)
    save(args.session_id, args.cwd, state)
    print(f"wrote fix prompt for attempt {attempt + 1} to {out}")
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

    # Stage 0 uses capture, never record: it cannot express a verdict, so it
    # cannot overwrite a previous attempt's judgment on a restart.
    p = sub.add_parser("capture")
    p.add_argument("--intent")
    p.add_argument("--transcript")
    p.set_defaults(fn=cmd_capture)

    p = sub.add_parser("status")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("may-stop")
    # Opt-in: only a guard that re-fires on every settle pass needs this, and
    # it must be explicit so a plain status check never mutates the counter.
    p.add_argument("--consume", action="store_true")
    p.set_defaults(fn=cmd_may_stop)

    # Composed from recorded state, never freehand: the restart must inherit
    # the original goal, not a paraphrase of it.
    p = sub.add_parser("fix-prompt")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_fix_prompt)

    args = ap.parse_args(argv[1:])
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
