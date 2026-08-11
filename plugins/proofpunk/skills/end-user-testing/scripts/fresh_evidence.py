#!/usr/bin/env python3
"""fresh_evidence.py — run-scoped evidence directory helper.

Enforces the eight fresh-evidence rules from the Proofpunk evidence
contract: every validation run owns a run-scoped directory, artifacts are
sequentially named, non-empty, fresh (mtime >= run start), cited by full
path, and sealed with an inventory. Ported from the fresh-evidence.sh
helper for cross-platform use (no BSD/GNU stat or date forks).

Commands:
  init-run <slug>   -> create e2e-evidence/run-<ISO-compact>-<slug>/, print run_id
  next-step <slug>  -> print the next sequential step-NN filename prefix
  seal              -> write evidence-inventory.txt for the active run
  validate          -> assert every artifact is fresh and non-empty

All operations work against ./e2e-evidence/ in the current working directory.
The "active run" is the most recently modified run-* subdirectory.

Exit codes: 0 success, 2 refusal (bad input, no active run, stale/empty
artifacts, unparseable run metadata).
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("./e2e-evidence")
SLUG_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class Refusal(Exception):
    """A rule violation that must stop the operation."""


def refuse(message: str) -> "Refusal":
    return Refusal(message)


def iso_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_slug(slug: str) -> str:
    if not slug or not SLUG_RE.match(slug):
        raise refuse("slug must be kebab-case alnum/dash/underscore")
    return slug


def active_run() -> Path:
    if not ROOT.is_dir():
        raise refuse("no active run")
    runs = [p for p in ROOT.glob("run-*") if p.is_dir()]
    if not runs:
        raise refuse("no active run")
    return max(runs, key=lambda p: p.stat().st_mtime)


def cmd_init_run(slug: str) -> str:
    slug = check_slug(slug)
    ROOT.mkdir(parents=True, exist_ok=True)
    run_id = f"run-{iso_compact()}-{slug}"
    run_dir = ROOT / run_id
    run_dir.mkdir()
    (run_dir / "evidence-inventory.txt").write_text("")
    (run_dir / ".run-meta").write_text(f"run_id={run_id}\nstarted={iso_now()}\n")
    return run_id


def cmd_next_step(slug: str) -> str:
    slug = check_slug(slug)
    run_dir = active_run()
    n = len(list(run_dir.glob("step-*")))
    return str(run_dir / f"step-{n + 1:02d}-{slug}")


def cmd_seal() -> str:
    run_dir = active_run()
    steps = sorted(p for p in run_dir.glob("step-*") if p.is_file())
    count = 0
    total_bytes = 0
    lines = []
    for f in steps:
        size = f.stat().st_size
        lines.append(f"{f.name} {size}")
        count += 1
        total_bytes += size
    lines.append(f"sealed={iso_now()} count={count} total_bytes={total_bytes}")
    inv = run_dir / "evidence-inventory.txt"
    inv.write_text("\n".join(lines) + "\n")
    return str(inv)


def cmd_validate() -> str:
    run_dir = active_run()
    meta = run_dir / ".run-meta"
    if not meta.is_file():
        raise refuse(f"no .run-meta in {run_dir}")
    started_line = next(
        (l for l in meta.read_text().splitlines() if l.startswith("started=")), None
    )
    if started_line is None:
        raise refuse(f"could not parse run-start timestamp in {meta}")
    started_raw = started_line.split("=", 1)[1].strip()
    try:
        started_epoch = datetime.strptime(
            started_raw, "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        raise refuse(f"could not parse run-start timestamp: {started_raw}")
    bad = 0
    for f in sorted(run_dir.glob("step-*")):
        if not f.is_file():
            continue
        mtime = f.stat().st_mtime
        if mtime < started_epoch:
            print(f"STALE: {f} (mtime {int(mtime)} < run-start {int(started_epoch)})", file=sys.stderr)
            bad += 1
        if f.stat().st_size == 0:
            print(f"EMPTY: {f} (zero bytes)", file=sys.stderr)
            bad += 1
    if bad == 0:
        return f"validate OK: {run_dir}"
    print(f"validate FAIL: {bad} issues", file=sys.stderr)
    raise SystemExit(2)


USAGE = """Usage:
  fresh_evidence.py init-run <slug>
  fresh_evidence.py next-step <slug>
  fresh_evidence.py seal
  fresh_evidence.py validate

All operations work against ./e2e-evidence/ in the current working directory.
The "active run" is the most recently modified run-* subdirectory.
"""


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.stdout.write(USAGE)
        return 0 if len(argv) >= 2 else 0
    command = argv[1]
    try:
        if command == "init-run":
            if len(argv) < 3:
                raise refuse("init-run requires a slug")
            print(cmd_init_run(argv[2]))
        elif command == "next-step":
            if len(argv) < 3:
                raise refuse("next-step requires a slug describing this step")
            print(cmd_next_step(argv[2]))
        elif command == "seal":
            print(cmd_seal())
        elif command == "validate":
            print(cmd_validate())
        else:
            sys.stderr.write(USAGE)
            return 2
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
