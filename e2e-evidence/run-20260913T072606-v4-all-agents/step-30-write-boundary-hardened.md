# step-30 — the safety boundary I claimed did not exist

## What I got wrong in step-29

I wrote "SAFETY BOUNDARY: a Bash call counts ONLY if its command text
actually redirects into the artifact this check verifies" and shipped a
basename regex. Adversarially tested afterwards:

    cat > other/CLAUDE.md <<'EOF'      CREDITED
    cat > ../CLAUDE.md <<'EOF'         CREDITED
    cat > /etc/CLAUDE.md <<'EOF'       CREDITED
    cat > ~/CLAUDE.md <<'EOF'          CREDITED
    echo x > backup/CLAUDE.md          CREDITED

Five wrong paths, all credited as installing THIS artifact. I asserted a
property without testing it — the same failure mode as the check I was
repairing, one commit later.

## Fix

Capture the redirect target, then RESOLVE it: honour the last `cd` so a
heredoc after cd-ing into the sandbox is judged from the right base, expand
~, join relatives against that base, require realpath equality with the
exact per-arm artifact. Verified 0 leaks / 0 misses across 21 forms, and a
write into another arm's sandbox is rejected.

## Truncated records: unknown, not affirmative

Step-29 fell back to scanning raw text when json.loads failed. That let a
CLIPPED record assert a write happened — inventing provenance from an
incomplete artifact, the same error class as the original bug. Now returns
False. This is safe because at runtime tool_calls hold the LIVE DICT
(sdk_probe ~522 `"input": b.input`); only the serialized copy is truncated
(~612, `json.dumps(...)[:200]`). Real verdicts always take the dict path.

## The fixture was wrong, not the checker

After hardening, the test failed 2 of 47 — both on REAL_WRITE. Correct
behaviour: that command cd's into its own per-arm sandbox, which is not the
test's SANDBOX, so crediting it would be a cross-sandbox write. Fixed by
judging it against its own sandbox and ADDING the paired assertion that the
same command must not count for a different one.

Worth naming: my first instinct was that the hardening had broken something.
It had not. Seventh instrument error.

## Naming

The advisory asked whether `write_attempted` should be renamed now that it
credits Bash. Checked commands/install.md: its acceptance criteria specify
WHAT must hold — file exists, <=200 lines, correct platform name,
marker-delimited, nothing outside markers edited, verification block run.
It never mandates a tool. So Bash is a permitted mechanism and the contract
name is right; what was wrong was the implementation. `write_tool_used` and
`write_mechanism` record the mechanism separately, so a reader can still see
HOW without the verdict depending on it.

## Suite at this HEAD
    verify-counts PASS · verify-orchestration PASS · test-hooks PASS
    test-integrations 36/36 (bun) · test-write-assertion 47 · dry-run PASS

## Status
P6 still UNVERIFIED. Two apparatus defects fixed; the unpinned, unrecorded
model remains untouched and remains the gating experiment.

VERDICT: a claimed safety property was false and is now tested. The lesson
repeats — assert nothing that has not been executed against adversarial
input.
