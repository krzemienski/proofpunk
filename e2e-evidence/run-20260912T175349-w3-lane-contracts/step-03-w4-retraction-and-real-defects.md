# W4 — a retraction, and the defects that survived it

## RETRACTED: the 'echo -e' finding

step-02 drove every skill script with 'sh $script --help' and recorded
literal '-e' in the output of four scripts, which looks exactly like the
classic POSIX portability defect.

It is not. Every one of those scripts declares bash:
```
analyze-claude-md.sh                                       #!/bin/bash
analyze.sh                                                 #!/usr/bin/env bash
fetch-features.sh                                          #!/usr/bin/env bash
github-discovery.sh                                        #!/usr/bin/env bash
find-polluter.sh                                           #!/usr/bin/env bash
hitl-loop.template.sh                                      #!/usr/bin/env bash
```
Under bash, 'echo -e' is correct:
```
  bash: interpreted	escape
  sh:   -e interpreted	escape
```
The '-e' came from MY harness invoking a bash script with sh, not from
the product. A finding produced by the instrument, not the subject —
retracted rather than filed.

## SURVIVING DEFECT 1 — hitl-loop.template.sh has no argument handling

Driven under its own interpreter, not sh:
```
$ bash plugins/proofpunk/skills/root-cause-debugging/scripts/hitl-loop.template.sh --help </dev/null

>>> Open the app at http://localhost:3000 and sign in.
unpiped rc: 
  1
```
Its own header (line 6-7) documents 'Usage: bash hitl-loop.template.sh',
and it is a TEMPLATE meant to be copied and edited. So --help is not a
contract it ever claimed. Severity: cosmetic. Recorded, not fixed —
adding flag parsing to a copy-me template adds noise to the thing the
user is supposed to edit.

## SURVIVING DEFECT 2 — the disclosure-debt table in the task is wrong

The task names 6 skills >6KB with zero own references, totalling
47,149 B. Measured:
```
skill                         bytes  ownrefs
brainstorm                     7222        0
codebase-truth-audit          15330        1
end-user-testing              10894        0
full-functional-audit          7346        0
implement                     10649        1
plan-hardening                 6815        0
prompt-forge                  17307        7
session-intent                 6316        2
tui-testing                    7685        0
ui-experience-audit           10011        4
validation-plan                6765        1
visual-inspection              7187        0
```
prompt-forge (17,307 B) and codebase-truth-audit (15,330 B) are the two
largest skills in the plugin and appear in neither the task's table nor
its 47,149 B total. The real figure for skills >6KB is larger.
Acting on the stated list alone would have left the two biggest
contributors untouched.

## Script citations: 22 resolvable, 0 dangling
Every scripts/ path cited anywhere under plugins/proofpunk/skills
resolves to a real file, and every skill-local python script answers
--help with rc=0. No skill instructs the agent to run something that
does not exist.
