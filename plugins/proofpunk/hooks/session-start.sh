#!/bin/sh
# Proofpunk SessionStart hook — injects the doctrine as session context.
cat <<'JSON'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Proofpunk is installed. Doctrine: execution logic over gate logic — decompose into tasks and execute each to completion; end-user testing is the only PASS (unexecuted checks are UNVERIFIED); no mocks or stubs; malformed input must fail clearly and safely. Commands: /proofpunk:implement, /proofpunk:cook, /proofpunk:verify, /proofpunk:truth-audit, /proofpunk:rate-prompt, /proofpunk:forge-prompt."
  }
}
JSON
