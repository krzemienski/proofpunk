# The orchestration invariant, stated correctly

Earlier in this session I described verify-orchestration.py as requiring
'literal ## Stage N headings AND in-section citations'. The second half
is wrong, and ScoutSkills caught it. Read directly:

```
tools/verify-orchestration.py:105-128 —
  # ---- 5. orchestrator order --------------------------------------------------
  print("CHECK 5: implement's stages invoke skills in DAG order")
  impl = bodies.get("implement", "")
  stage_secs = re.split(r"(?m)^(## Stage \d[^\n]*)$", impl)
  stage_text = {}
  for i in range(1, len(stage_secs), 2):
      # \d+(?:\.\d+)? so a fractional stage ("## Stage 1.5 — ACQUIRE...")
      # gets its own key instead of truncating to "1" and colliding with
      # (overwriting) Stage 1's own section in the dict below.
      num = re.search(r"Stage (\d+(?:\.\d+)?)", stage_secs[i]).group(1)
      stage_text[num] = stage_secs[i] + (stage_secs[i+1] if i+1 < len(stage_secs) else "")
  stage_expect = [
      ("1", "session-intent"), ("2", "brainstorm"), ("3", "prompt-forge"),
      ("4", "validation-plan"), ("5", "end-user-testing"),
      ("6", "root-cause-debugging"),
  ]
  for num, callee in stage_expect:
      check(f"implement Stage {num} invokes `{callee}`",
            num in stage_text and callee in stage_text[num],
            "" if num in stage_text else f"Stage {num} heading not found")
  nums = [float(n) for n in stage_text]  # float: keys may now be fractional ("1.5")
  check("stage sections appear in declared order", nums == sorted(nums), f"order={nums}")
  rail = re.search(r"regression (posture|rail)[^\n]*", impl, re.I)
  check("regression posture declared (existing suites stay green, never proof)", bool(rail))
```

## What CHECK 5 actually enforces
1. implement/SKILL.md is split on literal '^## Stage \d...' headings.
   A heading that is not literal — reworded, indented, or demoted — makes
   its stage invisible, and the check fails with 'Stage N heading not found'.
2. For six fixed pairs, the callee's BARE NAME must appear as a substring
   of that stage's section text: Stage 1 session-intent, 2 brainstorm,
   3 prompt-forge, 4 validation-plan, 5 end-user-testing,
   6 root-cause-debugging.
3. Stage numbers must appear in ascending order (floats, so 1.5 sorts
   between 1 and 2).
4. A regression posture/rail sentence must exist somewhere in the file.

There is NO citation-syntax check here. It does not care whether the
name is backticked, linked, or a path. Citation PATHS are a separate
tool's job — verify-citations.py, which sweeps globally.

## Why the distinction is load-bearing
Anyone refactoring implement/SKILL.md for disclosure debt (the W4
follow-on work) needs to know exactly what they must not break. Under
the wrong invariant you would preserve backticked citation syntax that
nothing checks, while a reworded stage heading — which nothing in the
prose warns you about — silently fails the gate.

Correct one-sentence form:
  verify-orchestration.py CHECK 5 requires implement/SKILL.md to keep
  literal '## Stage N' headings, in ascending order, each containing the
  bare name of its expected callee, plus one regression-posture line.

## Verified against the tool
  verify-orchestration.py unpiped rc=0
  literal '## Stage N' headings in implement: 9
    ## Stage 0 — Distill the TRUE success criteria (always first)
    ## Stage 1 — MINE (session-intent)
    ## Stage 1.5 — ACQUIRE (docs-first, before scouting)
    ## Stage 2 — SCOUT (mandatory, subagents)
    ## Stage 3 — FORGE (prompt-forge)
    ## Stage 4 — DECOMPOSE into the task graph
    ## Stage 5 — EXECUTE the loop
    ## Stage 6 — The stuck protocol
    ## Stage 7 — REPORT from the ledger
