# Lane contracts — emitted, and the checker proven able to fail

## Why this was missing
implement's --parallel flag has specified lane contracts since v4:
```
### `--parallel` lane contracts

Lanes run concurrently, each its own todo chain. Before lanes start, the
orchestrator writes a **lane contract** per boundary — an executable file
stating the exact public interface each lane may expose and consume, plus
two more binding fields: which ACQUIRE digest file that lane consumes
(conforming to `../../../references/docs-acquisition.md`), and which
`references/*-validation.md` runbook that lane's proof obligation must use.

Both new fields are resolvable paths, never placeholders. Every lane's
end-user validation includes conformance against all three fields, so a
merge conflict on the interface — or a cross-lane assumption mismatch, two
lanes silently building against different hosts, or one validating with the
wrong runbook — surfaces as a failed validation with evidence, not a review
debate.
```
Three binding fields, 'resolvable paths, never placeholders'. No run had
ever emitted one. A contract nobody checks is a comment, so the contracts
ship with a checker that resolves every path they name.

## The contracts
  .planning/lane-contracts/lane-01-hooks.contract.yml (3722 bytes)
  .planning/lane-contracts/lane-02-evidence.contract.yml (2468 bytes)

## Checker, clean tree
```
$ python3 tools/verify-lane-contracts.py
  PASS  lane-01-hooks.contract.yml
  PASS  lane-02-evidence.contract.yml

LANE CONTRACTS: 2 checked, 0 error(s)
  files under lane ownership: 12
unpiped rc=
0
```

## Non-vacuity — each check is driven to FAILURE on a mutated copy

A checker that cannot fail proves nothing. Each of the five checks is
broken deliberately in a scratch copy and the failure observed.

### M1 — acquire_digest points at a file that does not exist
  unpiped rc=1  (correctly FAILS)
      ERROR: lane-01-hooks.contract.yml: acquire_digest does not resolve: .planning/v4-architecture/does-not-exist.md

### M2 — validation_runbook names an invented runbook
  unpiped rc=1  (correctly FAILS)
      ERROR: lane-01-hooks.contract.yml: validation_runbook does not resolve: plugins/proofpunk/references/made-up-validation.md

### M3 — owns claims a path matching nothing
  unpiped rc=1  (correctly FAILS)
      ERROR: lane-01-hooks.contract.yml: owns `plugins/proofpunk/nonexistent/*.sh` matches no file in the tree

### M4 — a binding field is deleted outright
  unpiped rc=1  (correctly FAILS)
      ERROR: lane-02-evidence.contract.yml: missing binding field `acquire_digest`

### M5 — two lanes claim the same file (overlapping ownership)
  unpiped rc=1  (correctly FAILS)
      ERROR: lane-02-evidence.contract.yml: lane `evidence` and lane `hooks` both claim plugins/proofpunk/hooks/stop-guard.sh — overlapping ownership

### M6 — the checker must refuse an EMPTY contract directory
  unpiped rc=1  
    no *.contract.yml files in /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.JnjBbj6tvy/empty
