# VERDICT — LaneHeadSkill (router head + verify-router-links)

Date: 2026-09-04 | Evidence root:
`/Users/nick/proofpunk/e2e-evidence/run-20260904T142528-v3-orchestrated/lane-head/`

D8 confirmed at source: the head is a router that links 17 independently
invocable skills. No merge. `plugins/proofpunk/skills/proofpunk/SKILL.md`
was mutation-restored to its original bytes; no other SKILL.md was edited.

## What changed

| File | What |
|---|---|
| `tools/verify-router-links.py:1-176` (sha256 `6f81a8ec9ff790218a012516c77b54137d7caa0753298e5ea31bd1e06b114f7d`) | **NEW.** Stdlib gate. Globs `plugins/proofpunk/skills/*/SKILL.md`, parses the head's Skill-calls table, asserts every non-head name is routed (`expected = glob_N - 1`, never a literal 17), zero orphans, every Shared-doctrine path resolves relative to the citing file. Names offenders on FAIL. |
| `plugins/proofpunk/skills/proofpunk/SKILL.md` | **Unchanged** vs pre-lane bytes. sha256 `b1e50906fc10b89471a837eaaef1d78c2ded0c10edd538782bc667adb5d2a3c9` matches `head-original.SKILL.md`. Temporary mutations in step-03 / step-05 were restored byte-identically (step-04 / step-06 logs share sha256 `473896209348ae0432a5f716e22bfbc37f81b4a57ee899bf1eae719353b2b385` with the clean baseline). |

Not edited: the other 17 SKILL.md files, `tools/gauge-report.py`, `tools/sdk_probe.py`.

## What was driven

1. `python3 tools/verify-router-links.py` — clean + two named mutations + two restores. Exit codes in sibling `.rc` files, never piped.
2. Six live routing goals via `claude_agent_sdk` (same SDK as `sdk_probe.py`; that file was being edited by LaneCommandSurface so it was not invoked). Plugin loaded as `SdkPluginConfig(type="local")`. `Skill` tool observed.
3. One listing-content session with CLI debug; host WARN captured.

`tools/sdk_probe.py router` was **not** re-driven this lane (file not stable). The orchestrator's earlier `pass:true` on that probe is inherited, not re-measured here.

## Per-claim

### Router is a router, not a merge — PASS

- 18 SKILL.md files still exist under `plugins/proofpunk/skills/*/SKILL.md` (gate: `skills_globbed=18`).
- Head Skill-calls table lists 17 unique names, one per non-head directory (`non_head_expected=17`, derived).
- D8 in `docs/discovery-register.md`: "Strengthen and prove the existing router head — not a single-file merge."

Citation: `lane-head/step-02-clean-baseline.log` sha256 `473896209348ae0432a5f716e22bfbc37f81b4a57ee899bf1eae719353b2b385`
(`rc=0` in `step-02-clean-baseline.rc`).

### Gate green on clean tree — PASS (script-level)

`python3 tools/verify-router-links.py` → rc 0, `doctrine_refs=13 all_resolved=true`.

Citation: `step-02-clean-baseline.log` / `.rc`; reconfirmed after all mutations in `step-06-restored-final.log` / `.rc` (same log sha256).

### Mutation 1 (orphan route) red-by-name — PASS (script-level)

Broke `| \`brainstorm\` |` → `| \`does-not-exist-skill\` |`. Gate rc=1, named both the unrouted skill and the orphan:

```
OFFENDER: unrouted skill(s) (expected 17 non-head from glob of 18; table has 17 unique): ['brainstorm']
OFFENDER: orphan route(s) (name does not exist as a skill dir): ['does-not-exist-skill']
```

Citation: `step-03-mutated-orphan-route.log` sha256 `7b3db4afb35a7de6f532924aca34cd212ca85f8fb64bea19e1aa1403dedd57c2`
`step-03-mutated-orphan-route.rc` = `1`.

### Mutation 2 (broken doctrine ref) red-by-name — PASS (script-level)

Broke `` `../../references/end-user-actor.md` `` → `` `../../references/does-not-exist.md` ``. Gate rc=1, named the path:

```
OFFENDER: doctrine reference(s) do not resolve relative to .../proofpunk/SKILL.md: ['../../references/does-not-exist.md -> .../plugins/proofpunk/references/does-not-exist.md']
```

Citation: `step-05-mutated-doctrine-ref.log` sha256 `e5980e2cc9d32e5c576e0c15b6674948bcc46096ea96a803273f524251abc499`
`step-05-mutated-doctrine-ref.rc` = `1`.

### Restores byte-identical — PASS (script-level)

- Head file sha256 after both restores = original `b1e50906fc10b89471a837eaaef1d78c2ded0c10edd538782bc667adb5d2a3c9`.
- Clean / restore-1 / restore-2 gate logs share sha256 `473896209348ae0432a5f716e22bfbc37f81b4a57ee899bf1eae719353b2b385`.

Citations: `head-original.SKILL.md`, `step-04-restored.log`, `step-06-restored-final.log`.

Note: `step-01-baseline.log` (sha256 `eb4fe0818ab8669d010f69957f2809e1cba384459cbe9c9a3f8d5fb87574a42b`, rc=1) is the **parser-prefix miss** from the first gate revision (heading `## Shared doctrine` vs `## Shared doctrine — …`). Left immutable. The clean arm is step-02, not step-01.

### Live routing, 6 shapes — PASS (live-session)

| id | expected (router table / Routes-to-nothing) | actual Skill reached | match | citation |
|---|---|---|---|---|
| build | `implement` | `proofpunk:implement` (after `proofpunk:proofpunk`) | yes | `step-08-live-build.json` sha256 `e04ae152ec2d93e95ab40bb5a12e3e02f182f4417a1b9dcee37956bbe31513f2` |
| audit | `full-functional-audit` | `full-functional-audit` | yes | `step-09-live-audit.json` sha256 `55316ddce996ac4e6a2d29a484cec7a62e5c5f6f60a0bce58186f4aebb2dd8b1` |
| bug | `root-cause-debugging` | `root-cause-debugging` | yes | `step-10-live-bug.json` sha256 `745a3de0f0f8e782c01fab6bf5c73b57cbfe0766cdac2ea090c7aecb8b5842ea` |
| proof | `end-user-testing` | `end-user-testing` | yes | `step-11-live-proof.json` sha256 `88fc7bd9baaad0405b867406623f45511d9dadbb0aa3c2b8b167e4da52693f21` |
| planning | `validation-plan` | `validation-plan` | yes | `step-12-live-planning.json` sha256 `44787ba1a9aab5d5fe10b43981bcabac31c1da8137193f12d7bc979673c8747b` |
| nothing | ROUTES_TO_NOTHING (`Explain what this function does`) | no Skill call; reply `ROUTES_TO_NOTHING` | yes | `step-13-live-nothing.json` sha256 `b5a3b171a27a0e9242bf868603f49e8adcee3c5b6095085f699adff6fff63e23` |

Summary: `step-14-live-routing-summary.json` sha256 `b952553219d5b243e91d50629115cb3ea8218c7ff23e71b422157e6a6f191054`
(`n=6`, `matches=6`).

Proof level: live session with plugin loaded, observed `Skill` tool (or its absence on the negative case). Prompts were not retuned after the fact. The driver explicitly asked the model to follow the router; this is **router-followed-when-instructed**, not **cold auto-route from a bare user ask**.

### Gauge #7 host behavior — PASS as a measurement; UNMET target is a category error

Live host WARN (not the model's self-report):

```
Skill listing over budget: 1574 skills, 553023 chars > 150000 budget — descriptions will be truncated.
```

Citation: `step-16-host-warn.log` sha256 `a90eff733771a2d46c9150e561de03589c5efcc3e208b700cef0ffc7aa610b31`

The host's real aggregate ceiling on this session is **150000 chars**, and the named action is **truncate descriptions**. 1,536 is the per-skill `skillListingMaxDescChars` cap (no proofpunk skill is near it). Full write-up: `gauge7-host-behavior.md`. Catalog numbers: `step-17-catalog-facts.json` sha256 `3eb89d41802b43605baeed86be5f33e26b2581005c7adb37fd76c331fbcb362f`.

Recommended restatement (Lane E owns `gauge-report.py`; this lane does not edit it): keep 1,536 as a **per-skill** cap (already 18/18); replace the aggregate `<=1536` target with a live capture of the host WARN / its absence. Do not invent a new char threshold. Do not mass-rewrite descriptions.

## Open / UNRESOLVED

- **`tools/sdk_probe.py router` this lane:** UNVERIFIED. LaneCommandSurface was still mutating that file; corroboration used `claude_agent_sdk` directly. Orchestrator's earlier `pass:true` is not re-measured here.
- **Cold auto-route:** UNVERIFIED. Live probes instructed the model to follow the router. A bare user ask with no "follow the router" cue was not driven.
- **Why `proofpunk:implement` is missing from `init.skills` (17/18 namespaced skills):** UNVERIFIED. Could be listing-budget rank/drop, or command/skill name collision (`proofpunk:implement` is also a slash command). Needs an isolated-plugin control (`setting_sources=[]`). Exact-name `Skill` load still succeeded on the build ask.
- **Isolated proofpunk-only listing budget:** UNVERIFIED. The 1574 / 553023 / 150000 WARN is host-wide, dominated by the operator's installed corpus, not by proofpunk's ~13,955 description chars.
- **Model listing JSON** (`step-15-listing-content.json`, `listing_truncated: false`): contradicted by the host WARN on the same session. Not used as evidence.
- **Gauge #7 in `gauge-report.py`:** still the old aggregate-vs-1536 row until Lane E restates it. This lane's artifact for that decision is `gauge7-host-behavior.md`.
