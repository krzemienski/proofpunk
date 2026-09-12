# Two corrections: the Docker image, and the commit window

## 1. debian:stable-slim vs python:3.12-slim

The prompt specifies re-running the matrix under debian:stable-slim.
step-14 used python:3.12-slim. That substitution was NOT arbitrary and
is not equivalent — measured:
```
$ docker run --rm debian:stable-slim sh -c 'command -v python3 || echo ABSENT'
python3 ABSENT

$ docker run --rm python:3.12-slim sh -c 'command -v python3'
/usr/local/bin/python3
```

debian:stable-slim ships no python3. Five of the six gates ARE python3
programs, so on that image they cannot run at all. The two images
therefore answer different questions:

  debian:stable-slim  -> how the product behaves with NO python3
  python:3.12-slim    -> whether the gates pass on Linux

Both are needed. step-14 answered the second. This step answers the
first, on the image the prompt actually named.

## 2. The product under debian:stable-slim, root and non-root
### arm=root — root (uid 0)
```
uid=0  python3=ABSENT

-- every hook, driven with a real payload, unpiped rc --
  bash-write-notice.sh  rc=0  bytes=142
  bash-write-snapshot.sh  rc=0  bytes=0
  capture-guard.sh  rc=0  bytes=144
  evidence-guard.sh  rc=0  bytes=138
  instructions-loaded.sh  rc=0  bytes=0
  no-test-files.sh  rc=0  bytes=120
  platform-steer.sh  rc=0  bytes=0
  post-write-walkthrough.sh  rc=0  bytes=147
  session-start.sh  rc=0  bytes=499
  stop-guard.sh  rc=0  bytes=176

-- the three fixed guards, driven with MUST-DENY payloads --
  no-test-files.sh  rc=0  -> Proofpunk: no-test-files enforcement OFF (python3-not-found) — test-file writes are NOT being
  evidence-guard.sh rc=0  -> Proofpunk: evidence-guard enforcement OFF (python3-not-found) — secret material in evidence w
  capture-guard.sh  rc=0  -> Proofpunk: capture-guard enforcement OFF (python3-not-found) — overwrites of existing evidenc

-- installer WITHOUT python3, no --hooks (skills must still install) --
  installer rc=0  skills placed: 18/18
-- installer WITHOUT python3, WITH --hooks (must fail closed) --
  installer rc=1  (expect 1)  message: ERROR: --hooks requires python3 to merge hook entries into settings.json
```

### arm=nonroot — non-root (uid 1000)
```
uid=1000  python3=ABSENT

-- every hook, driven with a real payload, unpiped rc --
  bash-write-notice.sh  rc=0  bytes=142
  bash-write-snapshot.sh  rc=0  bytes=0
  capture-guard.sh  rc=0  bytes=144
  evidence-guard.sh  rc=0  bytes=138
  instructions-loaded.sh  rc=0  bytes=0
  no-test-files.sh  rc=0  bytes=120
  platform-steer.sh  rc=0  bytes=0
  post-write-walkthrough.sh  rc=0  bytes=147
  session-start.sh  rc=0  bytes=499
  stop-guard.sh  rc=0  bytes=176

-- the three fixed guards, driven with MUST-DENY payloads --
  no-test-files.sh  rc=0  -> Proofpunk: no-test-files enforcement OFF (python3-not-found) — test-file writes are NOT being
  evidence-guard.sh rc=0  -> Proofpunk: evidence-guard enforcement OFF (python3-not-found) — secret material in evidence w
  capture-guard.sh  rc=0  -> Proofpunk: capture-guard enforcement OFF (python3-not-found) — overwrites of existing evidenc

-- installer WITHOUT python3, no --hooks (skills must still install) --
  installer rc=0  skills placed: 18/18
-- installer WITHOUT python3, WITH --hooks (must fail closed) --
  installer rc=1  (expect 1)  message: ERROR: --hooks requires python3 to merge hook entries into settings.json
```

## 3. Commit window — the prompt's count does not match the tree

The prompt states the v3->v4 window is 11 commits exclusive of d5a50b1.
Measured at the time this session started (HEAD was a2fdeb9):
```
$ git log -1 --format='%h %s' d5a50b1
d5a50b1 release(v3): bump 2.2.0 -> 3.0.0 across all version surfaces

$ git rev-list --count d5a50b1..a2fdeb9
17
$ git rev-list --count d5a50b1..HEAD   # includes this session's 3 commits
20
```

17 exclusive at session start, not 11. The prompt's own P7 ledger
(step-01-improvement-ledger.md of run-20260912T172206) also says 17,
so the 11 in the task text is the outlier. Recorded rather than
silently adopted: a P7 improvement count derived from '11 commits'
would be scoped to the wrong range.
