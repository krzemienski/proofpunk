# step-32 — the branch I hardened, and the one I forgot

## 1. Write/Edit were credited unconditionally

    def _is_first_party_write(call):
        if call["name"] in ("Write", "Edit"):
            return True          # <- no target check

I hardened the Bash branch against five wrong-path forms and left the other
branch returning True for ANY Write/Edit. An SDK write to /etc/passwd would
have counted as installing the memory file.

Why no test caught it: searched the recorded evidence for Write/Edit calls
and found ZERO. Every install arm used Bash. A branch that real data never
exercises can only be held honest synthetically — which is exactly what the
test now does (wrong-path Write/Edit, all three path keys, empty target,
truncated record).

Both branches now resolve their target against the arm's cwd and require
realpath equality. The test mirrors production line-for-line, so its
"kept in sync" comment is finally true. 47 -> 67 assertions.

## 2. The fourth acceptance criterion had no check at all

commands/install.md lists four acceptance criteria. Three were measured
(exists, <=200 lines, marker-delimited, substituted). The fourth — "the
verification block at the end was actually run, output in the report" — had
nothing measuring it. I had audited this command twice without noticing.

Added `verification_block_run`. First attempt used `basename in cmd` while
claiming the write check's discipline; tested it and found the leak:

    cd /tmp/other && wc -l CLAUDE.md; grep -c "proofpunk:begin" CLAUDE.md
    -> qualified, while verifying a DIFFERENT file

Now resolves every CLAUDE.md reference against the effective cwd, and
requires BOTH distinguishing probes plus a completed non-error result.
Proven able to fail: 6 negative forms rejected, in-flight calls rejected.

## 3. Why it is NOT in the promotion gate

INSTALL_EFFECT_CHECKS is the gate. Adding a check changes the verdict, so
the check must first be observed passing live. Replaying the recorded run:

    matched verification-block calls: 0 / 6

Not because the command skipped verification — call 6 IS the block — but
because persisted input is truncated at 200 chars and the `grep` falls past
the cut. The artifact literally cannot confirm it. At runtime the predicate
reads the live dict and would match; "would" is not evidence.

So: RECORDED, not gating. The criterion stays UNVERIFIED as a named gap.
Promote only after a live arm reports it True.

## 4. Truncation was destroying evidence silently

tool_calls now carry input_len, input_truncated and input_sha256. A clipped
record is now visibly clipped instead of indistinguishable from absence —
the same confusion that produced the 0/6 reading twice this session.

`hashlib` was not imported. Caught by checking before running, unlike the
missing `re` two commits ago which I only caught on replay.

## Suite
verify-counts, verify-orchestration, test-hooks, test-integrations 36/36,
test-write-assertion 67, dry-run-install, test-installer — all PASS.
INSTALL_EFFECT_CHECKS still 6.

VERDICT: two real holes closed, one new check added but deliberately not
gating, and the capture format no longer hides its own truncation. P6
remains UNVERIFIED at 4/6.
