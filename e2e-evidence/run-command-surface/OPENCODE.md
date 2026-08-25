# OpenCode surface — installer propagation proof

The OpenCode half of the flag-drift fix, proven through the real installer
rather than by reading the repo file.

## Live machine still carries the defect

`~/.config/opencode/commands/proofpunk-truth-audit.md:3` on this host:

```
argument-hint: "<repo-path> [--since DATE] [--until DATE] [--label NAME]"
```

That is an older install. The repo fix does not reach a user until they
reinstall — worth stating plainly rather than implying the fix is live.

## Installer propagates the fix

Fresh install into a throwaway HOME (never touching the user's config):

```
HOME=$SB bash tools/proofpunk-install.sh --target opencode --plugins \
     --source-dir "$PWD" --quiet     # rc=0
```

Result in `$SB/.config/opencode/commands/`:

```
installed commands: forge-prompt, implement, install, rate-prompt,
                    truth-audit, verify
  has --start/--end : True
  has stale --since : False
stale cook installed: NONE
```

## Second finding: stale command on the live machine

`~/.config/opencode/commands/proofpunk-cook.md` exists on this host — the
command removed at v2.0.0. The fresh install produces **no** cook command, so
this is an orphan left by an earlier install that the installer does not clean
up.

Not fixed here: removing files from the user's live config is a destructive
change outside this repo, and needs operator consent. Recorded as a real
finding with its evidence.

## Scope

This proves the **installer output** is correct. It does **not** drive the
OpenCode binary executing the command — `opencode run` was available but
exercising it would install into or read from the user's live config.
