---
name: tui-testing
description: >
  End-user proof for terminal UIs (Ink, blessed, textual, ratatui, curses):
  drive the real TUI in a real PTY as the end user with observe-then-act
  discipline, matched-assertion waits, three-facet evidence (screen + disk +
  logs), and pixel proof for visual claims. Codifies the measured lessons of
  driving agent-tty against a live Ink application: TTY guards, runtime
  floors, daemon PATH inheritance, cold-boot budgets, key-mount races
  transport-envelope traps, and per-run secret scans. Use when validating a
  TUI/CLI-interactive feature, when a gate drives a terminal app, or when
  'prove the TUI works' is the ask. Not for web UIs (use web-validation via
  the implement validation phase) or non-interactive CLIs (use `references/cli-validation.md`).
---

# TUI Testing — Terminal UI End-User Proof

## Run checklist

- [ ] Runtime floor probed (Node/python version the DRIVER needs, not the app)
- [ ] Session created in an isolated automation home, env passed at create only
- [ ] Console byte-stream captured via `script -qfc` (never a pipe)
- [ ] Every action preceded by an observed, matched wait (observe-then-act)
- [ ] Three-facet evidence: screens, disk reads, logs (console + app event log)
- [ ] Visual claims proven by screenshot, not by screen-text hash
- [ ] Secret scan of the run dir before sealing
- [ ] Sessions destroyed; verdict cites artifacts by full path

Terminal apps are the hardest target class to prove honestly: they render
into a character grid, guard on real TTYs, race on input timing, and their
automation envelopes lie politely. This skill is the measured discipline.

## The Iron Rules (each one cost a real defect)

1. **Never pipe a TTY-guarded app.** `cmd | tee log` makes stdout not-a-TTY;
   a well-built TUI exits instantly and every downstream wait matches
   nothing. Use `script -qfc 'cmd' logfile` — a real sub-PTY that logs every
   byte. (D7: two full gate runs produced no app at all.)
2. **Transport `ok` is not a match.** agent-tty-style envelopes return
   `ok: true` for "command executed" — with `result.matched: false
   timedOut: true` inside. Assert the condition-level field for EVERY wait;
   treat a missing/empty result as failure. (D8: a whole run reported
   green while the app never booted; a screenshot exposed it.)
3. **Observe-then-act, human-paced.** Never burst-type a chorded sequence in
   one write: overlay mounts lag keypresses and same-chunk characters are
   dropped (':' then the command must be separate writes with a wait or
   settle between). Wait for text that is actually VISIBLE — lines truncate
   at panel width, so a wait anchored on truncated text can never match.
   (D3, and the 'persiste…' truncation catch.)
4. **Probe the driver's runtime floor first.** `Promise.withResolvers`
   (Node ≥22) and friends fail with opaque RPC errors, not clear version
   messages. Run `doctor` or a trivial wait; fail fast with the version in
   the report. A long-lived automation DAEMON inherits the PATH of its
   first invocation — after switching runtimes, kill the daemon or every
   call silently uses the old one.
5. **Budget cold boots.** First-run compile of a large TUI can exceed
   120 s; use 300 s boot waits or the first run after any cache clear
   manufactures a fake failure.
6. **Screenshots for visual claims, text for content claims.** A screen
   hash is text-only: theme/color/state-glyph changes need a rendered
   screenshot with pixel inspection. Match the screenshot tool's browser
   dependency before the run (playwright headless shell version parity).
7. **Three facets or it didn't happen.** (a) screen waits + screenshots
   (b) direct disk reads of every file the app claims to have written
   (settings, plans, sentinels — never trust the UI's claim), (c) logs:
   console byte-stream + the app's own event/crash logs + exit codes.
   Name the missing facet in the verdict.
8. **Secrets never enter evidence.** Credentials pass via env at session
   create only; evidence carries redacted copies (first-7-chars previews);
   every run ends with a scripted grep scan of the whole run dir for the
   key material and its prefix. A scan hit = the run is unsealable.
9. **Never mutate a running driver; never double-drive a target.** Shells
   read scripts incrementally — editing mid-run corrupts the run. Two
   drivers on one fixture contaminate each other's disk assertions. Kill
   prior drivers; destroy sessions you created.
10. **The harness belongs in the repo.** Gate scripts, fixture builders
    and restore tools live in `tools/` with the code they test — volatile
    workbenches (tmpfs) wipe without warning, and the harness must never be
    the thing that gets lost.

## Gate anatomy (proven shape)

```
00 doctor/runtime probe                → fail fast on floor violations
01 negative leg (no creds)             → refusal rendered + nothing written (disk)
02 boot with creds via env             → 300 s boot wait on a VISIBLE anchor
03 provision/configure via the UI      → matched wait + disk read (redacted copy)
04 navigate to the feature             → selection confirmed via detail-pane text
05 invoke                              → matched wait on the real outcome
06 collect logs                        → app event log + console log + crash log
07 analyze logs (lifecycle assertions) → event counts, kinds, ordering, no garbage
08 graceful quit + recording export    → exit evidence + cast/video
09 artifact collection + secret scan   → run dir self-contained, zero key material
```

## Driving patterns that survive contact

- **Selection via detail panes.** Lists repeat titles; the detail pane's
  unique fields (spec id, path) are the only reliable selection anchors.
- **Wait on the anchor that exists.** Panel titles, statusline hints, and
  detail fields render deterministically; long stream lines truncate —
  never anchor on them.
- **Kill with signals, verify with snapshots.** Ctrl+C ×N, then a snapshot
  proving the shell prompt returned; destroy the session after.
- **Recordings for motion claims.** `record export` (cast/webm) when the
  claim involves animation, streaming, or frame rates; pin the artifact
  path from the envelope.

## Verdict additions for TUI runs

On top of the `end-user-testing` verdict template, a TUI verdict states:
driver + version, runtime floor probed, boot wait used, facet checklist
(screen/disk/logs) with any missing facet named, and the secret-scan line.

## Anti-Patterns

| Pattern | Do instead |
|---------|-----------|
| `app | tee log` then wait for UI text | `script -qfc` sub-PTY; the app must see a real TTY |
| `if envelope.ok` as the wait assertion | assert `result.matched` (or equivalent) for every wait |
| Burst-typing ':' + command in one write | separate writes; wait for the overlay to mount |
| Waiting on a long stream line's full text | anchor on short, deterministic, non-truncated text |
| "Screen didn't change" from a text hash | screenshot pixel-diff for color/glyph claims |
| Reusing a daemon across runtime changes | kill it; daemons keep their first PATH |
| Evidence that ends at the screenshot | add disk reads + logs — three facets |
| Secrets in settings.json copied raw into evidence | redacted copies + final grep scan |

## Skill calls

Leaf skill — owns canonical methods; calls nothing.
Called by: `implement`, `full-functional-audit`.
Pairs with `end-user-testing` (proof standard) and the shared runbooks (`references/*-validation.md`) (platform routing).
