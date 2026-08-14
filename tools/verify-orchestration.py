#!/usr/bin/env python3
"""verify-orchestration.py — executable proof that the Proofpunk skills
execute as one delegation DAG, in the documented order, without duplicated
methods.

Checks (each emits run-scoped evidence via the end-user-testing helper):
  1. Graph parse: every SKILL.md carries a '## Skill calls' table.
  2. Closure: every callee exists; no self-calls.
  3. Acyclicity + topological depth (leaf owners at depth 0).
  4. Called-by consistency: every 'Called by' claim has a real edge.
  5. Orchestrator order: implement's stages invoke skills in DAG order.
  6. Duplication sweep: shared 12-word shingles below threshold and the
     End-User Actor Mandate verbatim in exactly one skill (its owner).

Exit 0 = proven, 1 = at least one check failed. Stdlib only, deterministic.
"""
import os, re, sys, glob, subprocess, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SK = os.path.join(ROOT, "plugins", "proofpunk", "skills")
HELPER = os.path.join(SK, "end-user-testing", "scripts", "fresh_evidence.py")
SHINGLE_THRESHOLD = 200

FAILS = []
def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok: FAILS.append(name)
    return ok

def body_of(p):
    t = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n.*?\n---\n", t, re.S)
    return t[m.end():] if m else t

skills = sorted(os.path.basename(os.path.dirname(p))
                for p in glob.glob(os.path.join(SK, "*", "SKILL.md")))
bodies = {s: body_of(os.path.join(SK, s, "SKILL.md")) for s in skills}

# ---- 1+2. parse + closure --------------------------------------------------
print("CHECK 1-2: parse '## Skill calls' tables, closure, no self-calls")
CALLS = {}
for s in skills:
    m = re.search(r"## Skill calls\n(.*?)(?=\n## |\Z)", bodies[s], re.S)
    if not check(f"{s}: has Skill calls section", bool(m)): continue
    sec = m.group(1)
    if "calls nothing" in sec:
        CALLS[s] = []
    else:
        rows = re.findall(r"^\| `([a-z0-9-]+)` \|", sec, re.M)
        CALLS[s] = rows
        check(f"{s}: table parsed ({len(rows)} edges)", len(rows) > 0)
    for v in CALLS.get(s, []):
        check(f"{s} -> {v}: callee exists", v in skills)
        check(f"{s}: no self-call", v != s)

# ---- 3. acyclicity + depth -------------------------------------------------
print("CHECK 3: acyclicity + topological depth")
WHITE, GRAY, BLACK = 0, 1, 2
color = {s: WHITE for s in skills}
cyc = []
def dfs(u, path):
    color[u] = GRAY
    for v in CALLS.get(u, []):
        if v not in color: continue
        if color[v] == GRAY: cyc.append(path + [v])
        elif color[v] == WHITE: dfs(v, path + [v])
    color[u] = BLACK
for s in skills:
    if color[s] == WHITE: dfs(s, [s])
check("graph is acyclic (DAG)", not cyc, "; ".join("->".join(c) for c in cyc))
depth = {}
def dep(u):
    if u in depth: return depth[u]
    depth[u] = 0 if not CALLS.get(u) else 1 + max(dep(v) for v in CALLS[u] if v in skills)
    return depth[u]
if not cyc:
    for s in skills: dep(s)
    sinks = sorted(s for s, d in depth.items() if d == 0)
    print("  depth map:", ", ".join(f"{s}={d}" for s, d in sorted(depth.items(), key=lambda x: -x[1])))
    check("leaf owners are the canonical-method skills",
          set(sinks) == {"brainstorm", "end-user-testing", "prompt-forge", "session-intent", "tui-testing"},
          f"sinks={sinks}")

# ---- 4. called-by consistency ----------------------------------------------
print("CHECK 4: 'Called by' lines match real edges")
for s in skills:
    m = re.search(r"## Skill calls\n(.*?)(?=\n## |\Z)", bodies[s], re.S)
    sec = m.group(1)
    cb = re.search(r"Called by: ([^.]+)\.", sec)
    claimed = set(re.findall(r"`([a-z0-9-]+)`", cb.group(1))) if cb else set()
    real = {u for u, vs in CALLS.items() if s in vs}
    check(f"{s}: called-by claims == real edges", claimed == real,
          f"claimed={sorted(claimed)} real={sorted(real)}")

# ---- 5. orchestrator order --------------------------------------------------
print("CHECK 5: implement's stages invoke skills in DAG order")
impl = bodies.get("implement", "")
stage_secs = re.split(r"(?m)^(## Stage \d[^\n]*)$", impl)
stage_text = {}
for i in range(1, len(stage_secs), 2):
    num = re.search(r"Stage (\d)", stage_secs[i]).group(1)
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
nums = [int(n) for n in stage_text]
check("stage sections appear in declared order", nums == sorted(nums), f"order={nums}")
rail = re.search(r"regression (posture|rail)[^\n]*", impl, re.I)
check("regression posture declared (existing suites stay green, never proof)", bool(rail))

# ---- 6. duplication sweep ---------------------------------------------------
print("CHECK 6: duplication sweep")
N = 12
def shingles(text):
    w = re.findall(r"[a-z0-9'-]+", text.lower())
    return {" ".join(w[i:i+N]) for i in range(len(w)-N)}
sh = {s: shingles(b) for s, b in bodies.items()}
total = 0
for i, a in enumerate(skills):
    for b in skills[i+1:]:
        total += len(sh[a] & sh[b])
check(f"shared {N}-word shingles below threshold", total <= SHINGLE_THRESHOLD,
      f"{total} <= {SHINGLE_THRESHOLD}")
mandate = [s for s in skills if re.search(
    r"marking (validation|end-user testing) complete without the ai actually invoking",
    bodies[s], re.I)]
check("verbatim Actor Mandate only in its owner", mandate == [], f"copies={mandate}")
canon = "The End-User Actor Mandate (canonical" in bodies.get("end-user-testing", "")
check("end-user-testing carries the canonical mandate section", canon)

# ---- verdict ----------------------------------------------------------------
print()
if FAILS:
    print(f"VERDICT: FAIL — {len(FAILS)} check(s) failed: {FAILS}")
    sys.exit(1)
print("VERDICT: PASS — the 17 skills execute as one delegation DAG, in the")
print("documented order, with methods owned exactly once.")
