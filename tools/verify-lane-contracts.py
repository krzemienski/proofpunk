#!/usr/bin/env python3
"""verify-lane-contracts.py — make a lane contract executable.

`implement`'s --parallel flag has specified lane contracts since v4:

    plugins/proofpunk/skills/implement/references/execution-loop.md:49-63
    "the orchestrator writes a lane contract per boundary — an executable file
     stating the exact public interface each lane may expose and consume, plus
     two more binding fields: which ACQUIRE digest file that lane consumes ...
     and which references/*-validation.md runbook that lane's proof obligation
     must use. Both new fields are resolvable paths, never placeholders."

No run had ever emitted one. A contract nobody checks is a comment, so this
script is what makes the word "executable" true: it resolves every path the
contract names and asserts every ownership claim against the real tree.

Checks per contract:
  1. All three binding fields are present.
  2. acquire_digest resolves AND conforms to references/docs-acquisition.md
     (it must carry a `## Gaps` section — item 6 of that contract, the one
     section every conforming digest has).
  3. validation_runbook resolves AND is one of the real *-validation.md
     runbooks, not an invented path.
  4. Every `owns` glob matches at least one real file. An ownership claim over
     nothing is how a lane silently stops guarding its boundary.
  5. No two lanes claim the same file. Overlapping ownership is the merge
     conflict lane contracts exist to surface before it happens.
  6. The proof_obligation names an artifact glob, an assertion, and an
     end_user_validation step.

Exit 0 if every contract passes, 1 otherwise. No pipes: the caller reads the
exit code directly.

Usage: python3 tools/verify-lane-contracts.py [--dir .planning/lane-contracts]
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNBOOK_DIR = REPO / "plugins/proofpunk/references"
REQUIRED_FIELDS = ("interface", "acquire_digest", "validation_runbook", "proof_obligation")


def load_yaml(path: Path) -> dict:
    """Parse the contract subset we need without requiring PyYAML.

    Deliberately minimal: these files are written by this project, and a
    hand-rolled reader keeps the checker dependency-free so it can run in the
    same bare containers the gates run in (debian:stable-slim has no pip).
    """
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text()) or {}
    except ImportError:
        pass

    # Fallback: extract just the scalar fields and the list blocks we check.
    text = path.read_text()
    out: dict = {}
    current_list = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if line.startswith("- ") and current_list is not None:
            item = line[2:].strip()
            if not item.startswith("name:"):
                out.setdefault(current_list, []).append(item)
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if indent == 0:
                current_list = None
            if key in ("owns", "may_not_touch") and not val:
                current_list = key
                out.setdefault(key, [])
                continue
            if key in REQUIRED_FIELDS or key in ("lane", "boundary"):
                if val and val not in (">", "|"):
                    out[key] = val
                else:
                    out.setdefault(key, "<block>")
            elif key in ("assertion", "artifact", "end_user_validation"):
                out.setdefault("proof_obligation_keys", []).append(key)
    return out


def check(path: Path, claimed: dict[str, str]) -> list[str]:
    errs: list[str] = []
    c = load_yaml(path)
    name = c.get("lane", path.stem)

    for field in REQUIRED_FIELDS:
        if field not in c:
            errs.append(f"{path.name}: missing binding field `{field}`")

    digest = c.get("acquire_digest")
    if digest and digest != "<block>":
        d = REPO / digest
        if not d.is_file():
            errs.append(f"{path.name}: acquire_digest does not resolve: {digest}")
        elif "## Gaps" not in d.read_text():
            errs.append(
                f"{path.name}: acquire_digest {digest} has no `## Gaps` section — "
                "item 6 of references/docs-acquisition.md; an omitted heading "
                "reads as 'not written', not 'nothing to report'"
            )

    runbook = c.get("validation_runbook")
    if runbook and runbook != "<block>":
        r = REPO / runbook
        if not r.is_file():
            errs.append(f"{path.name}: validation_runbook does not resolve: {runbook}")
        else:
            real = {p.name for p in RUNBOOK_DIR.glob("*-validation.md")}
            if r.name not in real:
                errs.append(
                    f"{path.name}: validation_runbook {r.name} is not one of the "
                    f"real runbooks ({', '.join(sorted(real))})"
                )

    # `owns` lives under `interface` in the YAML shape; the flat fallback
    # hoists it to the top level. Accept both.
    iface = c.get("interface")
    owns = c.get("owns") or (iface.get("owns", []) if isinstance(iface, dict) else [])
    for pattern in owns:
        hits = glob.glob(str(REPO / pattern), recursive=True)
        if not hits:
            errs.append(f"{path.name}: owns `{pattern}` matches no file in the tree")
            continue
        for h in hits:
            rel = str(Path(h).relative_to(REPO))
            if rel in claimed and claimed[rel] != name:
                errs.append(
                    f"{path.name}: lane `{name}` and lane `{claimed[rel]}` both "
                    f"claim {rel} — overlapping ownership"
                )
            claimed[rel] = name

    # Two parse paths reach this point: PyYAML (nested dict) and the
    # dependency-free fallback (flat key list). Read both, or the checker
    # reports a missing field on a contract that has it -- which is exactly
    # what it did on first run.
    po = c.get("proof_obligation")
    if isinstance(po, dict):
        keys = set(po)
    else:
        keys = set(c.get("proof_obligation_keys", []))
    for need in ("assertion", "artifact", "end_user_validation"):
        if need not in keys:
            errs.append(f"{path.name}: proof_obligation is missing `{need}`")

    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    # NOT .planning/ — that path is gitignored, so contracts written there
    # never reach a user or CI. A lane contract is part of the shipped
    # plugin surface, next to the references it cites.
    ap.add_argument("--dir", default="plugins/proofpunk/lane-contracts")
    args = ap.parse_args()

    d = REPO / args.dir
    if not d.is_dir():
        print(f"no lane-contract directory at {args.dir}", file=sys.stderr)
        return 1

    files = sorted(d.glob("*.contract.yml"))
    if not files:
        # A checker that greens an empty set is the vacuous pass this project
        # exists to prevent.
        print(f"no *.contract.yml files in {args.dir}", file=sys.stderr)
        return 1

    claimed: dict[str, str] = {}
    all_errs: list[str] = []
    for f in files:
        errs = check(f, claimed)
        status = "PASS" if not errs else "FAIL"
        print(f"  {status}  {f.name}")
        all_errs.extend(errs)

    print()
    for e in all_errs:
        print(f"  ERROR: {e}", file=sys.stderr)

    print(f"LANE CONTRACTS: {len(files)} checked, {len(all_errs)} error(s)")
    print(f"  files under lane ownership: {len(claimed)}")
    return 1 if all_errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
