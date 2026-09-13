# step-05 — P10: doctrine enforcement + precedence map

## What P10 asked for
"Doctrine rules have hook enforcement or a stated gap." The prior verdict was
UNVERIFIED because no interaction/precedence map existed.

## Artifact produced
plugins/proofpunk/references/enforcement-map.md (5025 bytes)

## Measured, over the 17-file doctrine corpus (the map itself excluded)

    hook-enforced                        : 4
    hook-unenforced, covered elsewhere   : 13
    globally unenforced (no surface)     : 0

Enforcement edges:

    evidence-contract.md    <- evidence-guard.sh   BLOCK (exit 2)
    intent-verification.md  <- stop-guard.sh       BLOCK (decision:block)
    subagent-aware-stop.md  <- stop-guard.sh       BLOCK (decision:block)
    platform-routing.md     <- platform-steer.sh   advise

## Two corrections I had to make to my own measurement

1. FIRST DRAFT CLAIMED 13 FILES "UNENFORCED". False. It counted hook
   citations only. Measuring all four surfaces (hooks, skills, tools, CI)
   shows every one is carried: end-user-actor.md alone is applied by 12
   skills; run-trace-schema.md and severity-model.md by 2 tools each. A
   narrow edge definition produced a confident, wrong gap count.

2. SECOND MEASUREMENT COUNTED THE MAP ITSELF. Writing enforcement-map.md into
   references/ made the corpus 18 files, and the new file trivially had "no
   surface" — a self-referential artifact. Re-measured with it excluded: 17
   files, 0 globally unenforced.

Both are recorded rather than silently corrected, because each produced a
plausible-looking number that was wrong.

## Hook taxonomy fixed in the same document
10 scripts, 4 block-capable (capture-guard, evidence-guard, no-test-files via
exit 2; stop-guard via top-level decision:block), 6 non-blocking. This is the
taxonomy P9 needed: 4x2 + 6 = 14 honest cases, matching the criterion's number
by correct reasoning instead of its wrong "7 hooks all deny" premise.

## Precedence recorded
1. Any exit 2 denies; the three deniers are independent so order is irrelevant.
2. stop-guard runs on Stop/SubagentStop only — it cannot race a tool-call deny.
3. additionalContext never overrides a deny.
4. Fail-open is announced ("enforcement OFF"), so a silent stop means the
   heuristic actually ran.

## Cross-runtime section states the real limits
OMP blocks on tool_call and may request one continuation at session_stop.
OpenCode's only blocking seam is a throw from tool.execute.before; session.idle
returns void and cannot block. Neither can populate the subagent tracker.

VERDICT: PASS — the map exists, every rule has enforcement or a stated gap,
and precedence is documented.
