#!/usr/bin/env python3
"""The end-of-process completion gate.

Confirms every background subagent reached a terminal status, WRITES the run
summary artifact, and returns the gate code. Contract
(references/subagent-aware-stop.md section 9):

    exit 0  all children terminal, summary written
    exit 2  a live child remains; the stop must not be signalled

Ordering is the point. This runs BEFORE the stop: a summary written once the
session has ended cannot influence whether it should have ended. While a child
is live it writes NOTHING and exits 2 -- a summary naming a still-running agent
as finished would be false.

Platform scope is measured, not assumed. Only the Claude/OMC runtime writes the
tracker this reads (OMP and OpenCode: 0 artifacts found). On those runtimes the
gate reports UNSUPPORTED in the artifact rather than implying a clean run --
absence of a tracker is absence of evidence, not proof of completion.

Usage
  completion_gate.py --session ID [--cwd DIR] [--out PATH]
"""

import argparse
import datetime as dt
import os
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from agent_state import (  # noqa: E402
    STATE_CHILDREN_LIVE,
    STATE_DEGRADED,
    STATE_NO_CHILDREN,
    _describe,
    read_state,
)


def _render(info: dict, session: str, cwd: str) -> str:
    """The summary artifact. Reports what was measured, nothing more."""
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    buckets = info.get("buckets") or {}
    lines = [
        "# Run completion summary",
        "",
        f"written:  {now}",
        f"session:  {session}",
        f"cwd:      {cwd}",
        f"state:    {info['state']}",
        f"tracker:  {info['tracker']}",
        f"reason:   {info['reason']}",
        "",
    ]

    if not info.get("readable"):
        if info["state"] == STATE_NO_CHILDREN:
            lines += [
                "## No tracker on this runtime",
                "",
                "No subagent tracker was found for this session. Only the",
                "Claude/OMC runtime writes one; on OMP and OpenCode it is absent.",
                "",
                "This gate therefore confirms NOTHING about child completion here.",
                "Absence of a tracker is absence of evidence, not proof that every",
                "agent finished.",
                "",
            ]
        else:
            lines += [
                "## Tracker could not be read",
                "",
                "The tracker exists but could not be parsed, so no per-agent record",
                "is available. The stop was allowed (a guard that cannot read state",
                "must not trap the session), but nothing here is proven finished.",
                "",
            ]
        return "\n".join(lines) + "\n"

    counted = sum(len(buckets.get(k) or []) for k in ("live", "terminal", "stale", "unknown", "malformed"))
    lines += [
        "## Agents",
        "",
        f"counted from the agents list: {counted}",
        "(never from total_* -- those counters are incoherent on real sessions:",
        " one reports total_completed=19 against total_spawned=4)",
        "",
    ]

    labels = {
        "terminal": "reached a terminal status",
        "stale": "aged out past the staleness cutoff (treated finished)",
        "unknown": "age unknown -- NOT proven finished",
        "malformed": "record unparsable -- NOT proven finished",
        "live": "STILL RUNNING",
    }
    for key in ("terminal", "stale", "unknown", "malformed", "live"):
        group = buckets.get(key) or []
        if not group:
            continue
        lines.append(f"### {labels[key]} ({len(group)})")
        lines.append("")
        for entry in group:
            if isinstance(entry, dict):
                lines.append(
                    f"- {_describe(entry)} status={entry.get('status', '?')} "
                    f"completed_at={entry.get('completed_at') or '-'}"
                )
            else:
                lines.append("- <non-object entry in the agents list>")
        lines.append("")

    if buckets.get("unknown") or buckets.get("malformed") or info["state"] == STATE_DEGRADED:
        lines += [
            "## Not proven finished",
            "",
            "Entries above marked 'NOT proven finished' have a missing or",
            "unparsable started_at, or could not be read. They did not hold the",
            "stop -- an entry with no timestamp can never age out, so blocking on",
            "it would wedge the session with no recovery -- but they are not",
            "evidence of completion. Investigate each as a broken tracker record.",
            "",
        ]

    lines += [
        "## What this summary does not claim",
        "",
        "It records RECORDED completion. The tracker carries status, agent_type,",
        "started_at and completed_at -- no liveness field -- so it cannot prove a",
        "process exited, and it says nothing about whether any agent's work was",
        "correct. Correctness is proven by driving the real system as the end",
        "user, not here.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(prog="completion_gate")
    ap.add_argument("--session", default="")
    ap.add_argument("--cwd", default=os.getcwd())
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)

    info = read_state(args.session, args.cwd)

    if info["state"] == STATE_CHILDREN_LIVE:
        # Write nothing. A summary naming a running agent as finished is false.
        names = ", ".join(_describe(e) for e in info["live"][:4])
        print(f"GATE: live children remain ({len(info['live'])}): {names}")
        print("No summary written. Wait for them, or state why their output is not needed.")
        return 2

    out = pathlib.Path(args.out) if args.out else pathlib.Path(args.cwd) / "run-completion-summary.md"
    body = _render(info, args.session or "(none)", args.cwd)
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(out.parent))
        with os.fdopen(fd, "w") as fh:
            fh.write(body)
        os.replace(tmp, out)  # atomic: a half-written summary never appears
    except OSError as err:
        print(f"GATE: children are terminal, but the summary could not be written ({err})")
        return 2

    print(f"GATE: {info['state']} — {info['reason']}")
    print(f"summary: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
