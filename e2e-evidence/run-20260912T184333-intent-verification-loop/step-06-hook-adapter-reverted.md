# A cross-session authorization bypass I wrote, and reverted

## What I was building
An intent check inside stop-guard.sh: when a completion is claimed with
evidence, also require a recorded intent verdict, and block if the
verdict says the original request was not met.

## The defect
The hook needs this session's identity to find its verdict file, whose
key is sha256(session_id + ':' + cwd). I wrote:
```
  sid = os.environ.get("PROOFPUNK_SESSION_ID") or (sys.argv[4] if len(sys.argv) > 4 else "")
```
and the hook's actual invocation is:
  python3 - "$transcript" "$cwd" "$event"

Three arguments. sys.argv[4] is ALWAYS absent, and the env var is not
set by any caller. So sid is always the empty string, and the key
collapses to sha256(':' + cwd) — identical for every session in the
same directory.

## Why that is a security defect, not a bug
One session records verdict=MET. Every other session in that directory
then reads that same file and is authorized to stop, whatever it did.
The guard would report clean while enforcing nothing — and worse than
nothing, because it LOOKS like enforcement. A cross-session
authorization bypass in the component whose entire job is refusing
unearned stops.

## How it surfaced
Not from a gate. tools/test-hooks.sh passes against the reverted tree
and would have passed against the broken one too — no case exercises
intent verdicts, because the feature is new. It surfaced from review
pressure asking whether the wrapper actually passes a session id. It
does not.

## Disposition: reverted, not patched
```
$ git checkout -- plugins/proofpunk/hooks/stop-guard.sh
$ bash tools/test-hooks.sh
unpiped rc=0
$ git status --short plugins/proofpunk/hooks/
  (clean)
```

Four successive patches to that one edit introduced: an undefined
INTENT_REASON, an undefined intent_ok(), a malformed conditional, a
reference to a non-existent SESSION_ID, duplicated cap logic that would
drift from intent_verdict.py, and finally this. Six defects in one
block is a signal about the approach, not about care.

## The correct design, for whoever continues
The hook must NOT reimplement key derivation or cap semantics. It
should shell out to the helper that owns them:
```
  intent_verdict.py may-stop --session-id "$session_id" --cwd "$cwd"
  rc=0 -> allow the stop    rc=2 -> block with the helper's stderr
```
One implementation of the rule, one place it can be wrong. And the
wrapper must first extract session_id from the Stop payload's stdin
JSON — it is present in the payload and currently unread.

## Status of the three surfaces
  hooks/stop-guard.sh            NOT WIRED — reverted to HEAD, clean
  extensions/proofpunk.ts        NOT WIRED
  opencode/plugin/proofpunk.ts   NOT WIRED
The contract and the helper are complete and driven; no adapter is.
