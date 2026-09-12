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

import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("./e2e-evidence")
SLUG_RE = re.compile(r"^[A-Za-z0-9_-]+$")
HEX64_RE = re.compile(r"[0-9a-f]{64}")

# references/evidence-contract.md rule 3: "every artifact > min_size_bytes
# (default 1024). Zero-byte or tiny files are INVALID; discard and re-capture."
# validate only ever rejected zero bytes, so a 40-byte artifact proving
# nothing sailed through as `validate OK` -- the enforcement tool
# under-enforcing the doctrine it exists to enforce.
#
# This is a REFUSAL, not a warning. The contract says INVALID; downgrading
# that to a passing notice would be weakening doctrine from inside the tool
# that enforces it, which is the same class of defect as a silent fail-open.
# A capture too small to carry its claim is re-captured with its context
# (the command, the rc, the surrounding state), not blessed.
MIN_SIZE_BYTES = 1024


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

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


def active_run(explicit: str | None = None) -> Path:
    """Resolve the run to operate on.

    `explicit` wins when given. Otherwise the active run is the most recently
    modified run-* directory -- which is ambiguous the moment two runs share
    an mtime. That is not hypothetical: validating three runs in a loop by
    touching each one in turn put all three on the same second, so every
    iteration validated whichever directory won the tie, and a run that
    genuinely fails reported rc=0. Pass --run to remove the guess.
    """
    if explicit:
        p = Path(explicit)
        if not p.is_dir():
            p = ROOT / explicit
        if not p.is_dir():
            raise refuse(f"no such run directory: {explicit}")
        if not p.name.startswith("run-"):
            raise refuse(f"not a run directory (must be named run-*): {explicit}")
        return p
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


def cmd_next_step(slug: str, run: str | None = None) -> str:
    slug = check_slug(slug)
    run_dir = active_run(run)
    n = len(list(run_dir.glob("step-*")))
    return str(run_dir / f"step-{n + 1:02d}-{slug}")


def cmd_seal(run: str | None = None) -> str:
    run_dir = active_run(run)
    steps = sorted(p for p in run_dir.glob("step-*") if p.is_file())
    if not steps:
        raise refuse(f"refusing to seal {run_dir}: it contains zero step-* artifacts")
    count = 0
    total_bytes = 0
    lines = ["# fresh-evidence-inventory v2 (name size sha256)"]
    for f in steps:
        size = f.stat().st_size
        # Size alone cannot detect an equal-length substitution -- a verdict
        # artifact flipped from PASSED to FAILED keeps its byte count. The
        # digest is what makes a sealed inventory a tamper-evident record.
        lines.append(f"{f.name} {size} {sha256_of(f)}")
        count += 1
        total_bytes += size
    lines.append(f"sealed={iso_now()} count={count} total_bytes={total_bytes}")
    inv = run_dir / "evidence-inventory.txt"
    inv.write_text("\n".join(lines) + "\n")
    return str(inv)


def cmd_validate(run: str | None = None) -> str:
    run_dir = active_run(run)
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
    steps = [f for f in sorted(run_dir.glob("step-*")) if f.is_file()]

    # A run with no captured artifacts proves nothing. Without this check the
    # loop below never executes, `bad` stays 0, and validate greens an empty
    # run -- the vacuous pass that makes every downstream seal claim suspect.
    if not steps:
        print(f"NO ARTIFACTS: {run_dir} contains zero step-* files", file=sys.stderr)
        bad += 1

    for f in steps:
        mtime = f.stat().st_mtime
        if mtime < started_epoch:
            print(f"STALE: {f} (mtime {int(mtime)} < run-start {int(started_epoch)})", file=sys.stderr)
            bad += 1
        size = f.stat().st_size
        if size == 0:
            print(f"EMPTY: {f} (zero bytes)", file=sys.stderr)
            bad += 1
        # The contract says "> min_size_bytes", so exactly MIN_SIZE_BYTES is
        # NOT sufficient -- `< MIN_SIZE_BYTES` would pass a 1024-byte file the
        # rule excludes. Measured at the boundary: 1023 refused, 1024 refused,
        # 1025 accepted.
        elif size <= MIN_SIZE_BYTES:
            print(
                f"THIN: {f} ({size} bytes, needs > {MIN_SIZE_BYTES}) — too small to "
                "carry a claim; re-capture with its command, rc, and "
                "surrounding state (evidence-contract.md rule 3)",
                file=sys.stderr,
            )
            bad += 1

    # seal must have run, and the sealed inventory must still describe what is
    # on disk. An unsealed run, or one whose files changed after sealing, is
    # not citable evidence.
    inv = run_dir / "evidence-inventory.txt"
    if not inv.is_file():
        print(f"UNSEALED: {run_dir} has no evidence-inventory.txt (run seal)", file=sys.stderr)
        bad += 1
    else:
        inv_lines = [l for l in inv.read_text().splitlines() if l.strip()]
        sealed_line = next((l for l in inv_lines if l.startswith("sealed=")), None)
        if sealed_line is None:
            print(f"UNSEALED: {inv} has no sealed= line (run seal)", file=sys.stderr)
            bad += 1
        else:
            recorded: dict[str, tuple[int, str]] = {}
            versioned = any(l.startswith("# fresh-evidence-inventory v2") for l in inv_lines)
            if not versioned:
                print(
                    f"LEGACY INVENTORY: {inv} predates digest sealing and cannot prove "
                    "content integrity. Re-seal the run to make it citable.",
                    file=sys.stderr,
                )
                bad += 1
            for l in inv_lines:
                if l.startswith("sealed=") or l.startswith("#"):
                    continue
                parts = l.rsplit(" ", 2)
                if len(parts) != 3 or not parts[1].isdigit() or not HEX64_RE.fullmatch(parts[2]):
                    print(f"CORRUPT INVENTORY: cannot parse {l!r} in {inv}", file=sys.stderr)
                    bad += 1
                    continue
                name, size_s, digest = parts
                if name != Path(name).name or not name.startswith("step-"):
                    print(f"UNSAFE INVENTORY NAME: {name!r} in {inv}", file=sys.stderr)
                    bad += 1
                    continue
                if name in recorded:
                    print(f"DUPLICATE INVENTORY ROW: {name} appears more than once in {inv}", file=sys.stderr)
                    bad += 1
                    continue
                recorded[name] = (int(size_s), digest)

            on_disk = {f.name: f for f in steps}
            for name, (size, digest) in sorted(recorded.items()):
                f = on_disk.get(name)
                if f is None:
                    print(f"MISSING: {name} is in the sealed inventory but absent from {run_dir}", file=sys.stderr)
                    bad += 1
                    continue
                actual = f.stat().st_size
                if actual != size:
                    print(f"TAMPERED: {name} is {actual} bytes, sealed as {size}", file=sys.stderr)
                    bad += 1
                elif sha256_of(f) != digest:
                    print(f"TAMPERED: {name} matches its sealed size but not its sealed sha256", file=sys.stderr)
                    bad += 1
            for name in sorted(set(on_disk) - set(recorded)):
                print(f"UNSEALED ARTIFACT: {name} was written after seal (re-seal the run)", file=sys.stderr)
                bad += 1

            # The summary line is part of the seal; if it disagrees with the
            # rows it summarises, the inventory has been edited by hand.
            fields = dict(
                p.split("=", 1) for p in sealed_line.split() if "=" in p
            )
            try:
                if int(fields.get("count", -1)) != len(recorded):
                    print(f"INVENTORY MISMATCH: sealed count={fields.get('count')} but {len(recorded)} rows", file=sys.stderr)
                    bad += 1
                if int(fields.get("total_bytes", -1)) != sum(s for s, _ in recorded.values()):
                    print(f"INVENTORY MISMATCH: sealed total_bytes={fields.get('total_bytes')} disagrees with rows", file=sys.stderr)
                    bad += 1
            except ValueError:
                print(f"CORRUPT INVENTORY: unparseable sealed= line in {inv}", file=sys.stderr)
                bad += 1

    if bad == 0:
        return f"validate OK: {run_dir}"
    print(f"validate FAIL: {bad} issues", file=sys.stderr)
    raise SystemExit(2)


USAGE = """Usage:
  fresh_evidence.py init-run <slug>
  fresh_evidence.py next-step <slug> [--run <run-dir>]
  fresh_evidence.py seal            [--run <run-dir>]
  fresh_evidence.py validate        [--run <run-dir>]

All operations work against ./e2e-evidence/ in the current working directory.
Without --run, the target is the most recently modified run-* subdirectory.
That is AMBIGUOUS when two runs share an mtime -- validating several runs in
a loop by touching each in turn puts them all on the same second, and every
iteration then targets whichever directory wins the tie. Pass --run whenever
more than one run exists and you mean a specific one.
"""


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        sys.stdout.write(USAGE)
        return 0 if len(argv) >= 2 else 0
    command = argv[1]
    # --run <dir> may appear anywhere after the command. Pulled out before
    # positional handling so `next-step <slug> --run <dir>` and
    # `next-step --run <dir> <slug>` behave identically.
    rest = list(argv[2:])
    run: str | None = None
    positionals: list[str] = []
    i = 0
    while i < len(rest):
        tok = rest[i]
        if tok == "--run":
            if i + 1 >= len(rest):
                print("--run requires a run directory", file=sys.stderr)
                return 2
            if run is not None:
                # Silently honouring the first and dropping the second is how
                # a caller ends up operating on a run they did not name.
                print("--run given more than once", file=sys.stderr)
                return 2
            run = rest[i + 1]
            i += 2
            continue
        if tok.startswith("-"):
            print(f"unknown option: {tok}", file=sys.stderr)
            return 2
        positionals.append(tok)
        i += 1

    # Arity is checked per command. Tolerating a stray positional means
    # `validate junk` runs as though it were `validate`, which hides a typo
    # in exactly the tool whose job is to refuse things.
    expected = {"init-run": 1, "next-step": 1, "seal": 0, "validate": 0}
    if command in expected and len(positionals) != expected[command]:
        print(
            f"{command} takes {expected[command]} positional argument(s), "
            f"got {len(positionals)}: {positionals}",
            file=sys.stderr,
        )
        return 2
    argv = [argv[0], command, *positionals]
    try:
        if command == "init-run":
            if len(argv) < 3:
                raise refuse("init-run requires a slug")
            if run is not None:
                raise refuse("init-run creates a run; --run does not apply")
            print(cmd_init_run(argv[2]))
        elif command == "next-step":
            if len(argv) < 3:
                raise refuse("next-step requires a slug describing this step")
            print(cmd_next_step(argv[2], run))
        elif command == "seal":
            print(cmd_seal(run))
        elif command == "validate":
            print(cmd_validate(run))
        else:
            sys.stderr.write(USAGE)
            return 2
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
