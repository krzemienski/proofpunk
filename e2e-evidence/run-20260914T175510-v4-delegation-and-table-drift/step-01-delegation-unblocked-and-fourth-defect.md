# step-07 — Delegation unblocked, then three parallel audits found a fourth gate gap

## Delegation: fixed, and proven by aftermath

The operator repaired the gpt-6 upstream on the route. I additionally repointed
two dead roles in `~/.omp/agent/config.yml` (operator file, outside this repo,
backed up first to `config.yml.bak-20260914T173955`):

```
  plan:    omniroute/cx/gpt-5.6-terra  ->  omniroute/cc/claude-sonnet-5
  advisor: omniroute/cx/gpt-6-astra    ->  omniroute/cc/claude-opus-5
```

### The probe sequence, and what each one proved

| Probe | Duration | Outcome |
|---|---|---|
| LivenessProbe (before any fix) | **197 ms** | `[omniroute/cx/gpt-6-astra] 401 codex expired` |
| LiveProbe2 (after my config edit) | **543 ms** | still `cx/gpt-6-astra` 401 — the running process had cached config, and `modelRoleStorage: project` meant `.omp/config.yml` in-repo still pinned `task`/`plan` to `cx/gpt-6-astra:auto` |
| LiveProbe3 (after operator's upstream fix) | **18.5 s** | **no 401.** Reached `yield`. Transcript shows `read(...) ⇒ ok · 60 lines` then `yield(result) ⇒ ok` |
| LiveProbe4 (file-based proof) | 25.0 s | wrote `/tmp/pp_probe4.txt` containing **`PROBE_ALIVE 19`** |

LiveProbe3 and LiveProbe4 both reported `SYSTEM WARNING: Subagent called yield
with null data` — a harness serialization quirk in the yield payload, **not** a
routing failure. The aftermath settles it: the file exists on disk with the
correct count (19 skills), and the transcript shows `read → write → read →
yield`, every call `ok`. Judging by the yield payload alone would have produced a
false "still broken" verdict.

**Delegation is working.** Three real audits ran in parallel immediately after.

## Fourth defect: verify-counts.py cannot see markdown table cells

`DocDriftAudit` reported stale counts in `README.md` and
`plugins/proofpunk/docs/architecture.md`. I verified each against source before
editing — all were real:

| File:line | Wrong | Live |
|---|---|---|
| `README.md:9` | router "hands off to **17**"; `references/` holds **17** | router=**18**, refs=**18** |
| `architecture.md:27` | "The other **17** are the actual methods" | **18** |
| `architecture.md:28` | Commands \| **6 (+6 OpenCode)** | **7 (+7)** |
| `architecture.md:31` | Shared references \| **15** | **18** |

Router edge count verified directly from the head skill's own routing table:

```
router edges: 18
['brainstorm', 'codebase-truth-audit', 'completion-summary', 'end-user-testing',
 'full-functional-audit', 'implement', 'mobile-validation-runner',
 'plan-hardening', 'production-readiness', 'prompt-forge', 'red-team-eval',
 'root-cause-debugging', 'session-intent', 'stack-testing', 'tui-testing',
 'ui-experience-audit', 'validation-plan', 'visual-inspection']
```

### The gate was blind to all five

```
$ python3 tools/verify-counts.py        # on the STALE docs
rc=0
```

The drift detector — the gate whose entire job is this defect class — passed.

### Root cause, measured

`CLAIM_RE` requires `<number> <noun>` adjacency. Executed against each stale line:

| Shape | CLAIM_RE | PLUS_RE |
|---|---|---|
| `hands off to 17 of them` (noun elsewhere) | `[]` | `[]` |
| `holds 17 shared` / `doctrine files` (noun on next line) | `[]` | `[]` |
| `\| Commands \| commands/*.md \| 6 (+6 OpenCode) \|` | `[]` | `[]` |
| `\| Shared references \| references/*.md \| 15 \|` | `[]` | `[]` |
| **control** `18 delivery skills` | `[('18','skills')]` | `[]` |
| **control** `7+7 commands` | `[('7','commands')]` | `[('7','7')]` |

**Markdown table rows are the structural blind spot**: the count sits in one
column and its noun in another, so no adjacency rule can ever see them. The two
prose misses are a narrower variant of the same thing (noun separated by
intervening words or a line break).

### The fix

A table-aware check, deliberately narrow: a row is examined only when its **first
cell is exactly a known count noun**, so a row about something else cannot be
dragged in by a stray number. The `N (+M)` commands pair is handled explicitly.

### Mutation proof

Scoped the stash to the two doc files so the tool fix stayed in place — otherwise
Arm 2 would have run the *old* gate and proved nothing:

```
$ git stash push -q -- README.md plugins/proofpunk/docs/architecture.md
```

| Arm | Condition | rc | Decisive output |
|---|---|---|---|
| 1 | docs fixed | **0** | `VERDICT: PASS — live .md counts match the tree` |
| 2 | docs stale, **tool fix retained** | **1** | `architecture.md:28: table row 'commands' says 6 (+6) (live 7 (+7))` / `architecture.md:31: table row 'shared references' says 15 (live accepts [18])` |
| 3 | restored | **0** | `VERDICT: PASS` |

Arm 2's messages (`table row '...'`) are emitted only by the new code, which is
what makes the arm non-vacuous: the old gate returned rc=0 on these same files.

## Two stale claims inside the hook scripts themselves

`BashBypassAudit` drove all five PreToolUse-registered scripts under a disposable
`mktemp -d` HOME (I authorized that boundary explicitly — its proposed
`HOME=/dev/null` would have tested an error path and risked a false "it denied"
reading). It confirmed the bypass is **open**, and corrected two claims:

1. **`bash-write-notice.sh:18` claimed "Content hashing (not mtime+size)".**
   Verified false against source: `bash-write-snapshot.sh:111` returns
   `f"{s.st_size}:{s.st_mtime_ns}:{s.st_ctime_ns}:{s.st_ino}"`. `sha256` appears
   only at line 144, hashing the baseline **lookup key**
   (`session:tool_use_id:cwd`), never capture bytes.

   The mechanism is sound — line 103 documents `st_ctime_ns` as load-bearing and
   unforgeable from userspace, catching `cp -p` and equal-size substitution at
   ~400x lower cost. Only the comment was wrong. Corrected, with the reason.

2. **The runtime notice told users the guards are "registered on Write|Edit
   only".** `hooks.json:40` shows the matcher is
   `^(Write|Edit|mcp__[A-Za-z0-9_]+__(write|edit|move|create|rename|delete|remove)[A-Za-z0-9_]*)$`
   — MCP mutation tools are covered too. Corrected.

**The bypass itself remains open and is not claimed closed.**
`verify-evidence-immutability.py` is *detection*, not prevention.

## V6 retry: predicate proven, transition still unprovable

`V6RetryProof` executed `is_transient_harness_error()` directly against a
10-shape matrix (no live sessions, no spend), including the real captured failure
log. It confirmed the parsed branch never searches `raw_body`, and correctly
returns False on reply-only/probe-text shapes — the scoping guard works.

Verdict: the **predicate** is proven; the **same-run attempt1 FAIL → attempt2
PASS transition** is not provable without a live provider fault or a
test-only fault-injection seam. No such seam exists today
(`PROOFPUNK_SURFACE_MODEL` selects a model, `PROOFPUNK_PLUGIN_DIR` a path;
neither injects failure). **Still UNPROVEN**, unchanged.

## Gates

16/16 rc=0 after these edits, including `shellcheck` over the 10 hook scripts and
`bash -n` over all 14 shell files — both load-bearing here, since two hook scripts
were modified. Logs: `gates-round2/`.
