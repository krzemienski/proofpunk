# P1 — installer failure-mode hunt, driven

P1 requires every BLOCKER to carry a verbatim failing command, its
unpiped rc, and the causing file:line. Each hostile condition below is
actually executed against the real installer, not reasoned about.

## C1 — clean HOME, full install (control: must succeed)
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.nxPEs1G967 bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk' --hooks >/dev/null 2>&1; echo controlled
unpiped rc=0
  controlled
```

## C2 — HOME unwritable (mode 500)
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.ONbsSLq6vJ bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk' --hooks
unpiped rc=1
  == Proofpunk installer ==
  target dir : /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.ONbsSLq6vJ/.claude/skills  (claude-code)
  source     : local checkout /Users/nick/proofpunk
  version    : installed=none → source=4.0.0 (source is always the newest main)
  installing : 18 skill(s)
  mkdir: /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.ONbsSLq6vJ/.claude: Permission denied
```

## C3 — malformed settings.json (must back up, not corrupt)
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.5V88rxukj7 bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk' --hooks
unpiped rc=0
    ✓ tui-testing
    ✓ ui-experience-audit
    ✓ validation-plan
    ✓ visual-inspection
  verify     : all skills pass (see ✓ lines above)
  == summary: 18 installed, 0 replaced, 0 skipped (collision), 0 missing ==
```

   backup created: 1 corrupt-* file(s)
   settings.json now valid JSON: yes

## C4 — HOME/.claude exists as a FILE where a dir is expected
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.qRHjJ6QNlF bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk' --hooks
unpiped rc=1
  == Proofpunk installer ==
  target dir : /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.qRHjJ6QNlF/.claude/skills  (claude-code)
  source     : local checkout /Users/nick/proofpunk
  version    : installed=none → source=4.0.0 (source is always the newest main)
  installing : 18 skill(s)
  mkdir: /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.qRHjJ6QNlF/.claude: Not a directory
```

## C5 — source dir does not exist
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.c5wJt2OH4n bash tools/proofpunk-install.sh --target claude-code --source local --source-dir /nonexistent/path --hooks
unpiped rc=1
  == Proofpunk installer ==
  target dir : /var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.c5wJt2OH4n/.claude/skills  (claude-code)
  ERROR: --source-dir '/nonexistent/path' is not a directory
```

## C6 — python3 absent, --hooks requested (guard at proofpunk-install.sh:413)
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.GOTb60vnle PATH='/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.WLxuYi08Nm' bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk' --hooks
unpiped rc=1
    INSTALL tui-testing
    INSTALL ui-experience-audit
    INSTALL validation-plan
    INSTALL visual-inspection
  hooks      : enforcement hooks (Stop/SubagentStop + PreToolUse)
  ERROR: --hooks requires python3 to merge hook entries into settings.json
```

## C7 — python3 absent, NO --hooks (skills must still install)
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.Cly5T0P5qK PATH='/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.WLxuYi08Nm' bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk'
unpiped rc=0
    ✓ tui-testing (frontmatter only — python3 unavailable for ref checks)
    ✓ ui-experience-audit (frontmatter only — python3 unavailable for ref checks)
    ✓ validation-plan (frontmatter only — python3 unavailable for ref checks)
    ✓ visual-inspection (frontmatter only — python3 unavailable for ref checks)
  verify     : all skills pass (see ✓ lines above)
  == summary: 18 installed, 0 replaced, 0 skipped (collision), 0 missing ==
```

   skills installed without python3: 18/18

## C8 — unknown flag (must reject, never silently ignore)
```
$ HOME=/var/folders/x9/t9mpdpkn4wn6mj59k7b48l9w0000gn/T/tmp.YJZYRWgXD6 bash tools/proofpunk-install.sh --target claude-code --source local --source-dir '/Users/nick/proofpunk' --bogus-flag
unpiped rc=1
  ERROR: unknown option: --bogus-flag (try --help)
```

