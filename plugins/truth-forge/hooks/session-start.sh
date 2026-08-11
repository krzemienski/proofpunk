#!/bin/sh
# truth-forge SessionStart hook — injects the doctrine as session context.
cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "truth-forge is installed. Doctrine: execution logic over gate logic — decompose into tasks and execute each to completion; end-user testing is the only PASS (unexecuted checks are UNVERIFIED); no mocks or stubs; malformed input must fail clearly and safely. Commands: /truth-forge:implement, /truth-forge:cook, /truth-forge:verify, /truth-forge:truth-audit, /truth-forge:rate-prompt, /truth-forge:forge-prompt."
  }
}
JSON
