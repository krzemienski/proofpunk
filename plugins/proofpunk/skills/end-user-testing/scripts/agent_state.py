#!/usr/bin/env python3
"""Subagent liveness for stop guards — the four-state model.

Answers one question for a stop hook: may this session stop, or are its
children still working?

Contract (see references/subagent-aware-stop.md):

  live child  ==  status == "running"  AND  age(started_at) <= STALE_CUTOFF

The age clause is load-bearing, not defensive. Measured in this repo: three
"running" entries aged 257-266 hours. Blocking on status alone wedges every
session forever. Bounding staleness is what makes the guard correct.

Counters are never trusted: one real session carries total_completed=19
against total_spawned=4. The decision is computed from the agents list.

Fail-open by construction. A missing, unreadable, or malformed tracker yields
zero live children and an explicit reason. A stop guard that cannot read state
must never trap the session — an unrecoverable hang is worse than the bug this
fixes.

Commands
  live     --session ID [--cwd DIR]   exit 0 if children are live, 2 if not
  state    --session ID [--cwd DIR]   print the state name
  summary  --session ID [--cwd DIR]   per-agent terminal report (for the skill)

Exit codes are the interface; stdout is for humans and for hook `reason` text.
"""

import argparse
import datetime as dt
import json
import os
import pathlib
import sys

# Operator-approved. The runtime's own tracker uses 5 minutes
# (subagent-tracker/index.js:28), so 10 releases later, never earlier.
STALE_CUTOFF_SECONDS = 10 * 60

# Terminal states. Failure is not liveness: a failed child must not block.
TERMINAL = {"completed", "failed", "cancelled", "stale"}

STATE_NO_CHILDREN = "MAIN_IDLE_NO_CHILDREN"
STATE_CHILDREN_LIVE = "MAIN_IDLE_CHILDREN_LIVE"
STATE_ALL_COMPLETE = "ALL_COMPLETE"
# Fifth state. Nothing is live, so the stop is allowed, but at least one entry
# is not *proven* terminal (missing/unparsable age, or an unreadable record).
# Reporting these as ALL_COMPLETE would assert something unmeasured.
STATE_DEGRADED = "ALL_COMPLETE_DEGRADED"


def tracker_path(session_id: str, cwd: str) -> pathlib.Path:
    """The runtime's registry. Session-scoped, project-local."""
    return (
        pathlib.Path(cwd)
        / ".omc"
        / "state"
        / "sessions"
        / session_id
        / "subagent-tracking-state.json"
    )


def _age_seconds(stamp: object, now: dt.datetime) -> "float | None":
    """Seconds since an ISO-8601 stamp, or None when unusable.

    Unparsable is not zero: returning 0 would mark a leaked entry fresh and
    re-introduce the wedge. Callers treat None as "age unknown".
    """
    if not isinstance(stamp, str) or not stamp.strip():
        return None
    try:
        parsed = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return (now - parsed).total_seconds()


def classify(agents: list, now: dt.datetime, cutoff: int) -> dict:
    """Split a tracker's agent list into live and not-live.

    Four outcomes, not three. A running entry whose age cannot be determined is
    **unknown**, never silently folded into `stale`: a missing or unparsable
    `started_at` is not evidence of completion, and reporting it as "treated
    finished" would state something untrue.

    Unknown does not block (the measured hazard is leaked `running` entries, and
    an entry with no timestamp can never age out, so blocking on it would wedge
    the session with no recovery path). It is surfaced explicitly instead, so a
    broken record appears in the reason string and in the completion summary
    rather than disappearing.
    """
    live, stale, unknown, terminal, malformed = [], [], [], [], []
    for entry in agents:
        if not isinstance(entry, dict):
            malformed.append(entry)
            continue
        status = entry.get("status")
        if status in TERMINAL:
            terminal.append(entry)
            continue
        if status != "running":
            # Unknown status is not evidence of work in progress.
            malformed.append(entry)
            continue
        age = _age_seconds(entry.get("started_at"), now)
        if age is None:
            unknown.append(entry)
        elif age > cutoff:
            stale.append(entry)
        else:
            live.append(entry)
    return {
        "live": live,
        "stale": stale,
        "unknown": unknown,
        "terminal": terminal,
        "malformed": malformed,
    }


def read_state(session_id: str, cwd: str, cutoff: int = STALE_CUTOFF_SECONDS) -> dict:
    """Resolve the session's child state. Never raises; always fails open."""
    now = dt.datetime.now(dt.timezone.utc)
    path = tracker_path(session_id, cwd)

    if not session_id:
        return {
            "state": STATE_NO_CHILDREN,
            "live": [],
            "reason": "no session id supplied; cannot resolve a tracker (fail open)",
            "tracker": str(path),
            "readable": False,
        }
    if not path.is_file():
        return {
            "state": STATE_NO_CHILDREN,
            "live": [],
            "reason": "no tracker file; this session has no recorded children",
            "tracker": str(path),
            "readable": False,
        }
    try:
        raw = json.loads(path.read_text())
    except (OSError, ValueError) as err:
        return {
            # Not NO_CHILDREN: that would claim "no children recorded" when the
            # truth is "we cannot tell". Allowed (never wedge), but degraded.
            "state": STATE_DEGRADED,
            "live": [],
            "reason": f"tracker unreadable ({type(err).__name__}); failing open",
            "tracker": str(path),
            "readable": False,
        }

    agents = raw.get("agents")
    if not isinstance(agents, list):
        return {
            "state": STATE_DEGRADED,
            "live": [],
            "reason": "tracker has no agents list; failing open",
            "tracker": str(path),
            "readable": False,
        }

    buckets = classify(agents, now, cutoff)
    live = buckets["live"]
    if live:
        state = STATE_CHILDREN_LIVE
    elif buckets["unknown"] or buckets["malformed"]:
        # Allowed, but not proven finished — say so in the state name itself.
        state = STATE_DEGRADED
    elif buckets["terminal"] or buckets["stale"]:
        state = STATE_ALL_COMPLETE
    else:
        state = STATE_NO_CHILDREN

    bits = [f"{len(live)} live"]
    if buckets["stale"]:
        bits.append(f"{len(buckets['stale'])} stale(>{cutoff // 60}m, treated finished)")
    if buckets["unknown"]:
        bits.append(f"{len(buckets['unknown'])} UNKNOWN-age(allowed, NOT proven finished)")
    if buckets["terminal"]:
        bits.append(f"{len(buckets['terminal'])} terminal")
    if buckets["malformed"]:
        bits.append(f"{len(buckets['malformed'])} unparsable")

    return {
        "state": state,
        "live": live,
        "buckets": buckets,
        "reason": ", ".join(bits),
        "tracker": str(path),
        "readable": True,
        "unknown_age": buckets["unknown"],
    }


def _describe(entry: dict) -> str:
    kind = entry.get("agent_type") or entry.get("agentType") or "agent"
    ident = entry.get("agent_id") or entry.get("agentId") or "?"
    return f"{kind} ({str(ident)[:12]})"


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(prog="agent_state")
    ap.add_argument("command", choices=["live", "state", "summary"])
    ap.add_argument("--session", default="")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--cutoff", type=int, default=STALE_CUTOFF_SECONDS)
    args = ap.parse_args(argv)

    info = read_state(args.session, args.cwd, args.cutoff)

    if args.command == "state":
        print(info["state"])
        return 0

    if args.command == "live":
        live = info["live"]
        if live:
            names = ", ".join(_describe(e) for e in live[:4])
            print(f"LIVE {len(live)}: {names} [{info['reason']}]")
            return 0
        print(f"NONE: {info['reason']}")
        return 2

    # summary — the completion skill's artifact source
    print(f"state:   {info['state']}")
    print(f"tracker: {info['tracker']}")
    print(f"reason:  {info['reason']}")
    buckets = info.get("buckets") or {}
    if not buckets:
        print("agents:  none recorded")
        return 0
    for label in ("live", "terminal", "stale", "unknown", "malformed"):
        group = buckets.get(label) or []
        for entry in group:
            if isinstance(entry, dict):
                status = entry.get("status", "?")
                done = entry.get("completed_at") or "-"
                print(f"  [{label:9}] {_describe(entry):38} status={status:10} completed_at={done}")
            else:
                print(f"  [{label:9}] <non-object entry>")
    if buckets.get("unknown"):
        print()
        print("WARNING: entries above marked [unknown] have a missing or unparsable")
        print("started_at. They did NOT block the stop, and they are NOT proven")
        print("finished. Treat each as a broken tracker record to investigate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
