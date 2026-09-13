# step-09 — mutation-test artifact: platform-steer.sh

Closes an INHERITED gate failure. `verify-mutation-artifact.py` reported
`platform-steer.sh` as the one harness with no linked mutation artifact.
Measured: my commit touched 0 files matching platform-steer, and HEAD~1
fails identically — pre-existing, not introduced. It still blocks the
release, so it is fixed here rather than excused.

## The subject
`plugins/proofpunk/hooks/platform-steer.sh` is a PreToolUse steering guard.
It NEVER denies — it emits `hookSpecificOutput.additionalContext` naming the
right runbook when a Bash command looks like it is validating the WRONG
platform. So the mutation test asks: if the detector is weakened, does the
steering disappear?

## Fixture
A real iOS project shape in a temp dir: `.git/` + `App.xcodeproj/`, which is
what `references/platform-routing.md`'s Detection table keys on. The command
driven is `npx playwright test` — a WEB tool inside an iOS project, i.e. a
genuine platform mismatch.

## BASELINE (green)
    rc=0   steers=True
    {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "proofpunk: this Bash command looks like a browser-autom

## MUTATION
The sole decision point is one regex (platform-steer.sh:76):

    BROWSER_TOOL = re.compile(r"\b(?:playwright|puppeteer|selenium|webdriver|chromedriver)\b", re.I)

replaced with a pattern that can never match:

    BROWSER_TOOL = re.compile(r"\b(?:__NEVER_MATCHES__)\b", re.I)

## MUTATED (red, naming the loss)
    rc=0   steers=False   -> SILENT, the steering is LOST
    (no output at all)

MUTATION CAUGHT: True

## A first attempt that did NOT catch it
I first replaced the literal string "playwright" once in the file. The mutant
still steered. Cause: that first occurrence is in the header COMMENT, not the
detector — and the regex still matched via the other tool names. A mutation
that edits documentation proves nothing. Recorded because the failed attempt
looked plausible and produced a green-looking mutant.

## Non-destructive
The mutant was written to a temp copy; `plugins/proofpunk/hooks/platform-steer.sh`
was never modified. Verified byte-identical after the run: True.

VERDICT: PASS — baseline steers, the named mutation silences it, and the
detector is proven load-bearing rather than decorative.
