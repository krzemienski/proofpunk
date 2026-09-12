# The OMP session_stop guard has never blocked anything

## The code
```
    pi.on("session_stop", async (_event, _ctx) => {
      const text = JSON.stringify(
        (_ctx as { session?: unknown }).session ?? {},
      ).slice(-6000);
      const CLAIM =
        /\b(done|complete|completed|finished|shipped|works now|fixed it)\b/i;
      const PROOF =
        /(e2e-evidence\/|evidence-inventory|step-\d+[-.]|screenshot|verdict|curl\s+\S+\s+200|validate\s+OK)/i;
      if (CLAIM.test(text) && !PROOF.test(text)) {
```
Note the cast: `(_ctx as { session?: unknown }).session`. TypeScript
casts do not create properties — they silence the compiler about one
that may not exist.

## ScoutRuntimes, with SDK-level citations
  - `_ctx.session` is NOT part of the installed ExtensionContext type.
    Real ctx is cwd / sessionManager / exec / ... (pi v17.3.4
    runner.ts:956-978).
  - The real session_stop event carries messages[], turn_id,
    last_assistant_message, session_id, session_file, stop_hook_active,
    signal (shared-events.ts:96-107) — on the EVENT, which this handler
    ignores, not on the context, which it reads.

## Executed, not argued
The handler's extraction reproduced verbatim and run against both
context shapes:
```
  ctx WITHOUT .session  (what the scout says actually ships):
      {"text":"{}","claim":false,"proof":false,"wouldContinue":false}
  ctx WITH .session     (what the code assumes):
      claim=true proof=false wouldContinue=true
```

With the context that actually ships, the guard stringifies {} and
sees the literal two-character string "{}". No claim regex can match
it. wouldContinue is false for every session that has ever run.

## What was actually verified in the process
The cap-8 comment at line 75-76 IS real: SESSION_STOP_CONTINUATION_CAP
= 8 at agent-session.ts:347, enforced at :3418-3444, which queues a
hidden continuation message. I recorded that comment as unverified in
step-04 and it is now confirmed — the runtime bound exists. It simply
has never been reached, because nothing ever returns continue:true.

## Class of defect
Identical to the python3 fail-open that opened this session: a guard
that reports healthy while enforcing nothing. It is worse here, because
there is no failure to observe at all — no error, no exit code, no
notice. It silently evaluates an empty object and allows.

No gate catches it. There is no test for the OMP extension in this
repo at all — tools/test-hooks.sh covers only the shell hooks:
  occurrences of extensions/proofpunk.ts in the harness: 0
  occurrences of session_stop: 0

## Consequence for this task
The OMP adapter cannot be 'added to the existing guard', because the
existing guard is inert. It has to read the EVENT (which carries
messages and session_id) rather than the context, and that is a
behaviour change to shipped code — not the additive edit I assumed
when I scoped this work.
