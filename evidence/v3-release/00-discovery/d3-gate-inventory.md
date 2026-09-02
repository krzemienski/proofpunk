# D3 — Gate inventory: what exists, what each can and cannot see

Measured 2026-09-02 against `/Users/nick/proofpunk` @ `a41591a`.

## The six gates

| Gate | Lines | Invokes its subject? | Subject |
|---|---|---|---|
| `tools/test-hooks.sh` | 268 | **YES** — 9/9 scripts | every hook script, via `sh "$HOOKS/<name>.sh"` |
| `tools/test-installer.sh` | 264 | **YES** — 14 references | `tools/proofpunk-install.sh` |
| `tools/dry-run-install.sh` | 88 | **MODEL ONLY** — reimplements the steps; invokes no subject | models the `/proofpunk:install` agent playbook (`commands/install.md`); cannot prove real slash-surface behavior, and does NOT invoke `proofpunk-install.sh` — see F-D3-1 |
| `tools/verify-orchestration.py` | 145 | n/a (static graph) | skill/reference graph |
| `tools/sdk_probe.py` | 388 | n/a (live sessions) | installed plugin via agent SDK |
| `tools/build-site.py` | 611 | n/a (generator) | docs tree |

`tools/generate-themes.py` (192 lines) is a generator, not a gate.

### Method note — a near-miss worth recording

A first pass counted literal `hooks/` occurrences and reported **0** for
`test-hooks.sh`, which would have branded a working harness as vacuous. The
harness resolves scripts through a `$HOOKS` variable, so the literal string
never appears. Re-measured by listing every `.sh`-bearing line: **35
invocation sites covering all 9 scripts**. Recorded because "grep found no
matches" is not proof of absence — the same reasoning error the repo's own
mutation-testing history warns about.

## F-D3-1 — `dry-run-install.sh` is a MODEL of the install playbook, not a driver of it

**This finding was initially overstated and is corrected here.** The first
draft called it "the headline finding" and claimed the `5e5150b` defect was
never actually fixed. That was wrong on the evidence below.

### What the script does (read end to end, 88 lines)

- L7: resolves `$PP` to `plugins/proofpunk` — the plugin payload, never
  `tools/proofpunk-install.sh`.
- L31-34 / L37-43 / L45-46: reimplements the CLAUDE.md template
  substitution, marker-replacement merge, and append path inline.
- L58-60, L79: reimplements the scoped-rules copy with `cp`.
- L76-77: reimplements the AGENTS.md substitution for the OpenCode target.

### Why that is correct, not a defect

Its declared subject is not the shell installer. Header L2-5 states it
"execute[s] the `/proofpunk:install` mechanics … the command doc itself is
the agent playbook this script mirrors."
`plugins/proofpunk/commands/install.md` confirms `/proofpunk:install` is an
**agent playbook**, not a shell entry point: frontmatter declares
`--platform/--clobber/--no-rules`, and Steps 1-4 instruct the *agent* to
detect the platform, read `assets/claude-md-template.md` or
`agents-md-template.md`, substitute placeholders, merge inside
`proofpunk:begin/end` markers, and copy `assets/rules/`. There is no shell
program implementing that flow, so a harness for it must execute the steps
itself. `tools/proofpunk-install.sh` is a *different* subject — the plugin
installer — with its own harness.

### The `5e5150b` remedy, verified

`git show -s --format=%B 5e5150b` states the root cause verbatim:
"tools/dry-run-install.sh was documented in tools/AGENTS.md as the installer
dry-run harness but never invoked tools/proofpunk-install.sh (grep -c = 0)."

The remedy was **not** to make it invoke the installer. Per the same body:
"Add tools/test-installer.sh (7 assertion groups) driving the real
installer" and "Correct the mislabelled tools/AGENTS.md row."
`git show --stat 5e5150b -- tools/` confirms it: seven files touched
(`AGENTS.md`, `INSTALL.md`, `proofpunk-install.sh`, `sdk_probe.py`,
`test-hooks.sh`, `test-installer.sh` +174, `verify-orchestration.py`) —
**`dry-run-install.sh` was deliberately not modified.**

The label correction landed. Measured today:

| | `tools/AGENTS.md:16` |
|---|---|
| At `5e5150b^` | "Installer dry-run harness (0 fails expected) — run before any installer change" |
| Today | "Exercises the `/proofpunk:install` slash-command's template/rules merge logic … **does NOT invoke `proofpunk-install.sh`**" |

A new row 17 documents `test-installer.sh` as the "Real harness for
`proofpunk-install.sh`", and line 33 adds it to the required gate list.

### Verdict

The two harnesses have two different declared subjects, both are now
honestly labelled, and the `5e5150b` remedy landed as described. **The
harness-integrity violation as originally alleged does not exist.**

But the coverage claim must not be overstated either. `dry-run-install.sh`
is **MODEL ONLY**: it reimplements the playbook's steps in shell and asserts
on its own output. It invokes no subject at all — not the shell installer,
and not `/proofpunk:install` at the real slash surface. It therefore
**cannot** prove:

- that `/proofpunk:install` behaves this way when an agent actually runs it
  on Claude Code, OpenCode, or OMP;
- that the command doc and the agent's execution of it stay in parity —
  if `commands/install.md` changed tomorrow, the harness's hardcoded `sed`
  and `cp` steps would keep passing against the old flow;
- anything about the `--platform`, `--clobber`, or `--no-rules` flags the
  frontmatter declares, none of which the harness models.

So the honest reading is: the playbook's *merge mechanics* are covered
deterministically; the playbook *as a slash command* has **no gate at all**.
That is a real gap, listed below, and it is the same class as the OpenCode
UNPROVEN lane — proof at script level standing in for the user-facing
surface, which `6c560ea` already established is not equivalent.

Residual naming risk: a file called `dry-run-install.sh` beside
`proofpunk-install.sh` invited exactly the misreading this session made
twice. L16's meta-gate must assert *declared subject → invocation*, not
*filename → invocation*, or it will regenerate this false positive.

## F-D3-2 — installer coverage rests on one harness

`test-installer.sh` is the **only** gate that drives
`tools/proofpunk-install.sh` (14 references). It also carries the canonical-
parity assertion at L257:

```
ok "installed tree matches canonical hooks.json (scripts, events, registrations)"
```

Consequence: installer correctness has a single point of observation. If that
one group is skipped, mis-scoped, or vacuous, the installer has *zero*
coverage again — exactly the pre-`5e5150b` state. L1 and L16 must both treat
this file as load-bearing.

## Structural blind spots (what each gate cannot see)

| Gate | Structurally cannot see |
|---|---|
| `test-hooks.sh` | whether a hook is **registered**; it invokes scripts directly, bypassing `hooks.json` and `settings.json` entirely. A script that ships but is never wired passes here — the `99c72fb` defect class. |
| `test-installer.sh` | live host behavior; it proves the produced tree, not that Claude/OpenCode/OMP load it. |
| `dry-run-install.sh` | any real execution — it invokes no subject. It cannot see the shell installer, cannot see `/proofpunk:install` at the slash surface, and cannot detect drift between `commands/install.md` and its own copied steps. |
| `verify-orchestration.py` | runtime; it proves the *declared* graph, never the graph that ran. This is the gap L6 (`verify-runtime.py`) is scoped to close. |
| `sdk_probe.py` | anything outside a live Claude session — no OpenCode, no OMP. Platform parity is unobservable here (L14's gap). |
| `build-site.py` | correctness of the values it renders; it faithfully reproduces whatever the LAYERS map says, which is how `/proofpunk:cook` survived removal. |

## Surfaces with NO gate at all

- **Bash-authored writes** — the documented-open bypass; `PreToolUse` matches
  `Write|Edit` only.
- **OpenCode and OMP hook behavior** — no harness drives either host.
- **Per-skill behavior** — no eval exists for any individual skill's workflow.
- **Skill-canon conformance** — no gate checks frontmatter against any host's
  documented contract.
- **Count/version drift across docs** — no gate; the repo's most recurring
  defect class is unguarded.
- **`__pycache__` shipping into install targets** — no gate (F-D5-1).
- **`/proofpunk:install` at the real slash surface** — no gate. Its only
  harness (`dry-run-install.sh`) models the steps rather than driving the
  command, so slash-surface behavior and command-doc↔harness parity are both
  unobserved. Same class as the OpenCode UNPROVEN lane.
- **Harness integrity itself** — no gate. F-D3-1 shows why one is needed and
  why it must key on declared subject, not filename.

## Evidence

Produced by `wc -l`, stdlib substring counts over each harness, a full read of
`tools/dry-run-install.sh` and `plugins/proofpunk/commands/install.md`, a
line-level scan of `tools/test-hooks.sh`, `git show -s --format=%B 5e5150b`,
`git show --stat 5e5150b -- tools/`, and a before/after read of
`tools/AGENTS.md:16` via `git show 5e5150b^:tools/AGENTS.md`. Raw command
transcripts are the session record.
