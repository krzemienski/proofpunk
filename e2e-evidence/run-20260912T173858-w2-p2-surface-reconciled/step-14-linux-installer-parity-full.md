# Linux parity gap closed — test-installer.sh, root and non-root, full output

Supersedes step-13 (956 bytes, below the >1024 threshold this session
introduced — invalid evidence by its own rule, regardless of rc).

step-11 ran only five gates under Linux; test-installer.sh was omitted.
It is the gate that exercises the installer end to end AND contains the
fresh_evidence strict-contract group whose fixture this session changed
in e180035, so its Linux behaviour is precisely what must not be assumed.

Image: python:3.12-slim. Repo bind-mounted at /w. HOME is a fresh temp
dir inside the container so the --hooks group has somewhere writable.

## arm=root — root (uid 0)
```
$ docker run --rm  -v $(pwd):/w -w /w python:3.12-slim sh -c '... sh tools/test-installer.sh ...'
uid=0  python3=/usr/local/bin/python3  sh=/usr/bin/sh
HOME=/tmp/tmp.GIE2d9fRok (writable: yes)
unpiped rc=0
--- group headers and their results ---
== group 1: happy path (clean install of all 18 skills)
== group 2: collision default (second run over same dir does not clobber)
== group 3: --override replaces and reports replaced
== group 4: --only <name> installs exactly one skill
== group 5: --only <nonexistent> exits non-zero and reports missing
== group 6: --dry-run creates no files
== group 7: malformed skill (missing frontmatter) fails verify — the D3 regression
== group 8: --hooks registers EVERY proofpunk hook in settings.json
== group 9: fresh_evidence.py strict seal/validate contract
== group 10: installed tree matches canonical hooks.json
== group 11: F-D5-1 installed tree never contains __pycache__ or *.pyc
== group 12: F-D5-2 installed fresh_evidence.py is runnable
INSTALLER TEST FAILS: 0
--- the fresh_evidence strict contract group (changed this session) ---
== group 9: fresh_evidence.py strict seal/validate contract
  PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
  PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
--- totals ---
PASS lines: 28
FAIL lines: 0
(no FAIL lines present)
```

## arm=nonroot — non-root (uid 1000)
```
$ docker run --rm --user 1000:1000 -v $(pwd):/w -w /w python:3.12-slim sh -c '... sh tools/test-installer.sh ...'
uid=1000  python3=/usr/local/bin/python3  sh=/usr/bin/sh
HOME=/tmp/tmp.oRS9IjInQU (writable: yes)
unpiped rc=0
--- group headers and their results ---
== group 1: happy path (clean install of all 18 skills)
== group 2: collision default (second run over same dir does not clobber)
== group 3: --override replaces and reports replaced
== group 4: --only <name> installs exactly one skill
== group 5: --only <nonexistent> exits non-zero and reports missing
== group 6: --dry-run creates no files
== group 7: malformed skill (missing frontmatter) fails verify — the D3 regression
== group 8: --hooks registers EVERY proofpunk hook in settings.json
== group 9: fresh_evidence.py strict seal/validate contract
== group 10: installed tree matches canonical hooks.json
== group 11: F-D5-1 installed tree never contains __pycache__ or *.pyc
== group 12: F-D5-2 installed fresh_evidence.py is runnable
INSTALLER TEST FAILS: 0
--- the fresh_evidence strict contract group (changed this session) ---
== group 9: fresh_evidence.py strict seal/validate contract
  PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
  PASS: fresh_evidence strict contract: empty/thin/unsealed/tamper refused, clean sealed passes
--- totals ---
PASS lines: 28
FAIL lines: 0
(no FAIL lines present)
```

## Hook harness, same two arms
  arm=root: unpiped rc=0  HOOK TEST FAILS: 0  PASS=83
  arm=nonroot: unpiped rc=0  HOOK TEST FAILS: 0  PASS=83

Both gates pass identically as root and as uid 1000. The prior release's
defects were visible in exactly one of those arms, which is why both are
run rather than one.
