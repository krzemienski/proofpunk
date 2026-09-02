# A8 — OpenCode skill contract (canon) + singular/plural verdict + local host

Agent: A8CanonOpenCode. All web sources retrieved **2026-09-02** (retrieval date
recorded per claim, as required). Product-tree reads are from repo @ a41591a.

---

## 1. First-party support and on-demand loading — CONFIRMED

- OpenCode has first-party skill support with a native `skill` tool, loaded on
  demand. V1 docs, verbatim: "Skills are loaded on-demand via the native
  `skill` tool—agents see available skills and can load the full content when
  needed."
  Source: https://opencode.ai/docs/skills/ (retrieved 2026-09-02), intro §.
- V2 docs: at each model step OpenCode advertises each skill's "ID, name, and
  description; it does not add every skill body to the prompt"; the body is
  added only when the model calls the `skill` tool with an exact ID.
  Source: https://opencode.ai/v2/docs/skills/ (retrieved 2026-09-02), §Runtime loading.
- Source code (installed version): `packages/opencode/src/skill/index.ts` at
  tag `v1.18.26` (commit 774cc7c1) — `fmt()` builds the advertisement from
  `name` + `description` only; full `content` is returned by `get/require`
  on tool call. Verified byte-identical to `dev` HEAD 69c172e8.
  Source: https://github.com/anomalyco/opencode/blob/v1.18.26/packages/opencode/src/skill/index.ts
  (retrieved 2026-09-02; identity checked via raw fetch + `cmp`).
- History: native skills landed at v1.0.190 via PRs sst/opencode#5930 (native
  `skill` tool + pattern permissions) and #6000 (per-agent filtering, v1.0.191).
  Source: https://raw.githubusercontent.com/malhashemi/opencode-skills/main/README.md
  (retrieved 2026-09-02), graduation banner.

## 2. Discovery path list — all six repo-assumed paths verified, with a caveat

V1 docs (https://opencode.ai/docs/skills/, retrieved 2026-09-02, §Place files)
list exactly six, matching the repo's assumption 1:1:

| Path | In official docs |
| --- | --- |
| `.opencode/skills/<name>/SKILL.md` | yes — "Project config" |
| `~/.config/opencode/skills/<name>/SKILL.md` | yes — "Global config" |
| `.claude/skills/<name>/SKILL.md` | yes — "Project Claude-compatible" |
| `~/.claude/skills/<name>/SKILL.md` | yes — "Global Claude-compatible" |
| `.agents/skills/<name>/SKILL.md` | yes — "Project agent-compatible" |
| `~/.agents/skills/<name>/SKILL.md` | yes — "Global agent-compatible" |

Project paths walk "up from your current working directory until it reaches
the git worktree" (same page, §Understand discovery). V2 docs give the same
six as a scope table (https://opencode.ai/v2/docs/skills/, §Discovery) and add
two forms the V1 page does not mention: root-level Markdown files
(`skills/git-release.md`) and `SKILL.md` at any depth within a source.

CAVEAT (compat dirs are plural-only in code): at v1.18.26 the `.claude` /
`.agents` trees are scanned with `EXTERNAL_SKILL_PATTERN = "skills/**/SKILL.md"`
(index.ts:23) — plural only — while opencode-owned config dirs use the brace
pattern (see §4). So `.claude/skill/` (singular) would NOT load, but that is
not a path the installer targets.

## 3. Frontmatter: recognized vs ignored

V1 docs (retrieved 2026-09-02, §Write frontmatter), verbatim: "Only these
fields are recognized: `name` (required), `description` (required),
`license` (optional), `compatibility` (optional), `metadata` (optional,
string-to-string map). **Unknown frontmatter fields are ignored.**" — the
silence is EXPLICITLY documented, confirming the repo's risk assessment.

| Field | V1 docs (/docs/skills/) | V2 docs (/v2/docs/skills/) | Source @ v1.18.26 |
| --- | --- | --- | --- |
| `name` | recognized, required | recognized; display label only, optional | read; non-string `name` ⇒ skill silently dropped (`isSkillFrontmatter` gate, no warning) |
| `description` | recognized, required | recognized, optional; absent ⇒ not advertised to model | read; optional; `fmt()` filters out description-less skills |
| `license` | recognized, optional | "may be included for portability, but V2 does not interpret them" | not read into `Info` — ignored |
| `compatibility` | recognized, optional | same quote — not interpreted | ignored |
| `metadata` | recognized, optional, string→string map | V2 interprets `metadata.opencode/slash` and `metadata.opencode/autoinvoke` only | not read — ignored |
| `slash` | not mentioned | recognized (`false` hides from interactive catalogs) | n/a |
| any unknown field | "Unknown frontmatter fields are ignored" (explicit) | "other metadata may be included … V2 does not interpret them" | only `name`/`description` ever read; rest silently dropped |

Extra silence found in source (worse than field-level): a SKILL.md whose
frontmatter fails the `isSkillFrontmatter` check (e.g. `name:` missing or
non-string) is dropped with **no log at all** (`if (!isSkillFrontmatter(md.data)) return`),
while YAML parse failures DO publish an error event. Frontmatter, `name`, and
`description` are all optional at V2 runtime (V2 docs, §Frontmatter).

## 4. THE DISCREPANCY — singular `skill/` vs plural `skills/`

### VERDICT: target PLURAL `skills/`. Both load on the installed binary; singular is legacy-compat. Install plural, tolerate singular. No dual install needed.

Evidence, per source:

1. **Official docs today say plural, in both doc lines.**
   - V1: `~/.config/opencode/skills/<name>/SKILL.md`, `.opencode/skills/<name>/SKILL.md`
     (https://opencode.ai/docs/skills/, retrieved 2026-09-02, §Place files).
   - V2: scope table Global `~/.config/opencode/skills`, Project `.opencode/skills`
     (https://opencode.ai/v2/docs/skills/, retrieved 2026-09-02, §Discovery).
   - V1→V2 migration doc: "Existing skill files and automatic
     `.opencode/skills/` discovery do not change."
     (https://opencode.ai/v2/docs/migrate-v1/, retrieved 2026-09-02, §Skills).
   Neither official page mentions a singular form anywhere (verified by
   reading both pages end-to-end).

2. **The singular source is third-party and historical.** The deprecated
   `opencode-skills` plugin README (proof-of-concept that graduated into
   native at v1.0.190) told users to migrate with `mv .opencode/skills skill`
   and `mv ~/.opencode/skills ~/.config/opencode/skill` — "Native uses skill/
   (singular) at project root".
   Source: https://raw.githubusercontent.com/malhashemi/opencode-skills/main/README.md
   (retrieved 2026-09-02), §Migration. This was true (or believed true) in the
   v1.0.190 era; it is not the current contract.

3. **User reports of a singular-only window.** Issue anomalyco/opencode#9819
   "Docs: Skill path mismatch — 'skills' (plural) vs 'skill' (singular)"
   (opened 2026-01-21, v1.1.28/1.1.29 era): multiple users reproduced
   "plural does not load, singular does"; a maintainer could not replicate.
   The issue was closed **2026-04-10 by the 90-day stale bot** ("issues are
   automatically closed after 90 days of no activity") — NOT by a documented
   fix. Related issues listed there: #8054 (opposite direction: "discovery
   only checks skills/, ignoring skill/"), #9044 ("Tweak .opencode/skill into
   .opencode/skills"), #6432 ("Backward compatibility broken — enforcement of
   the /skill directory naming") — i.e. the naming churned in both directions
   across releases.
   Source: https://github.com/anomalyco/opencode/issues/9819 (retrieved 2026-09-02).

4. **Source code settles it for the version on this host.**
   `packages/opencode/src/skill/index.ts` at tag `v1.18.26` (commit 774cc7c1,
   byte-identical to `dev` HEAD — verified by raw fetch + cmp):

   ```ts
   const EXTERNAL_SKILL_PATTERN  = "skills/**/SKILL.md"          // .claude / .agents
   const OPENCODE_SKILL_PATTERN  = "{skill,skills}/**/SKILL.md"  // opencode config dirs
   const SKILL_PATTERN           = "**/SKILL.md"                 // configured skills.paths / urls
   ```
   (index.ts:21–25). Every directory returned by `config.directories()`
   (config.ts:430, which includes the global `~/.config/opencode` and project
   `.opencode` trees) is scanned with the **brace pattern `{skill,skills}`** —
   BOTH the singular and the plural directory load, at the exact version
   installed on this host (1.18.26).

   Installer consequence: write to `skills/` (documented, canonical, matches
   both doc lines); if a legacy `skill/` tree exists, it will still load — no
   migration or dual install required, and no breakage from leaving it.

## 5. Names, lengths, casing, uniqueness, deny

- `name` (V1): 1–64 chars, lowercase alphanumeric + single hyphens, no
  leading/trailing `-`, no `--`, must match the containing directory name;
  regex `^[a-z0-9]+(-[a-z0-9]+)*$` (https://opencode.ai/docs/skills/,
  §Validate names). V2 does NOT enforce any of this — "IDs are exact and
  case-sensitive", path-derived, frontmatter `name` is display-only; the
  regex is only a portability recommendation (/v2/docs/skills/, §IDs and
  validation).
- `description` length: V1 must be 1–1024 characters (§Follow length rules);
  V2 enforces no maximum (§IDs and validation).
- `SKILL.md` casing: V1 troubleshooting step 1: "Verify `SKILL.md` is spelled
  in all caps"; V2: "a nested file named exactly `SKILL.md`"; source globs use
  the literal `SKILL.md`.
- Uniqueness across locations: V1 troubleshooting step 3: "Ensure skill names
  are unique across all locations". Source behavior: duplicates log a warning
  and the LAST-loaded copy silently overwrites (`state.skills[name] = …`);
  V2 formalizes it — keyed by ID, later source wins, with an explicit
  precedence order: built-ins < `.claude/skills` (global, then farthest
  ancestor→cwd) < `.agents/skills` (same) < `~/.config/opencode/skills` <
  project `.opencode/skills` (root→cwd) < explicit `skills` config entries.
- `deny` hides a skill from agents: V1 permission table — `deny` = "Skill
  hidden from agent, access rejected"; V2 — "`deny` removes matching skills
  from model-facing discovery and rejects skill tool loading". Source:
  `available(agent)` filters `Permission.evaluate("skill", name, …).action
  !== "deny"` (index.ts). Confirmed at doc AND code level.
- Built-in: opencode ships a built-in `customize-opencode` skill registered
  BEFORE disk discovery so a user copy of the same name overrides it
  (index.ts:27–34 comment).

## 6. opencode.json permission and source forms

- **V1 pattern-map form** (https://opencode.ai/docs/skills/, §Configure
  permissions): `"permission": { "skill": { "*": "allow", "pr-*": "allow",
  "internal-*": "deny", "experimental-*": "ask" } }` — wildcards supported;
  per-agent override via custom-agent frontmatter `permission.skill` or
  `agent.<id>.permission.skill` in opencode.json; tool disable via
  `tools: { "skill": false }` (omits `<available_skills>` entirely).
- **V2 config-array form** (https://opencode.ai/v2/docs/skills/, §Permissions;
  https://opencode.ai/v2/docs/migrate-v1/, §Permissions and tools): one
  ordered `permissions` array, `{ "action": "skill", "resource": "<pattern>",
  "effect": "allow"|"deny"|"ask" }`, **last matching rule wins**; same rules
  can live under `agents.<id>.permissions`.
- **V1 skill-source config**: `{"skills": {"paths": ["./team-skills"], "urls":
  ["https://example.com/skills/"]}}` → **V2 flat array**
  `{"skills": ["./team-skills", "https://example.com/skills/"]}`
  (migrate-v1 §Skills). Arrays from multiple config documents are additive.
  Relative paths resolve from the active working directory (not home, not the
  config file's dir); only `http://`/`https://` are URL sources. Source at
  1.18.26 still reads the normalized `cfg.skills?.paths` / `cfg.skills?.urls`
  shape; a missing dir logs "skill path not found" and is skipped.
- **HTTP catalog form** (V2 docs §HTTP catalogs): base URL serving
  `index.json` `{"skills":[{"name","version","files":[…]}]}`; files fetched
  from `<base>/<name>/<file>`; paths must be safe/relative/same-origin; each
  entry needs `SKILL.md` or a markdown named after the entry (use the named
  form — a root-level `SKILL.md` yields the literal ID `SKILL`); bump
  `version` to refresh the cache.

## 7. Local host (read-only inspection, 2026-09-02)

- `~/.config/opencode/skills/` **EXISTS** (233 entries; mix of proofpunk-era
  names and large third-party set — `ab-test-setup`, `ckm-*`-adjacent,
  `deepest-plan`, …). `~/.config/opencode/skill/` (singular) **DOES NOT
  EXIST**. The host already conforms to the plural-canonical verdict.
- `~/.config/opencode/commands/`: 56 `.md` files + `ck/` dir. Six live
  proofpunk commands, with the flags each declares (read from frontmatter):
  - `proofpunk-install.md` — `--platform claude-code|opencode|agents|omp`,
    `--clobber`, `--no-rules`; body claims platform conventions "verified
    against vendor docs, **2026-08-13**" — that date is now superseded by
    this capture (2026-09-02); the install-path row for opencode must match
    §4 (plural canonical, both load).
  - `proofpunk-implement.md` — `--parallel --auto --mine --fast`; activates
    `implement` skill.
  - `proofpunk-forge-prompt.md` — `--out`, `--depth core|advanced`;
    activates `prompt-forge`.
  - `proofpunk-rate-prompt.md` — `--in-place --report-only
    --ship-below-threshold --out`; activates `prompt-forge`.
  - `proofpunk-truth-audit.md` — `--start --end --label`; activates
    `codebase-truth-audit`.
  - `proofpunk-verify.md` — positional scope; references `implement` Stage 5
    and `end-user-testing` refs — those names exist both in the packaged
    plugin (repo skills list) and as live global copies, so the references
    resolve; no staleness proven.
  - `proofpunk-cook.md` is **no longer live** — see retirement below.
- `_retired-proofpunk-skills-20260902-030220/` (mtime 2026-09-02 03:02:20):
  17 skill trees — exactly the repo's 18 `plugins/proofpunk/skills/*` minus
  the `proofpunk` router skill (visual-inspection, validation-plan,
  ui-experience-audit, tui-testing, stack-testing, session-intent,
  root-cause-debugging, red-team-eval, prompt-forge, production-readiness,
  plan-hardening, mobile-validation-runner, implement, full-functional-audit,
  end-user-testing, codebase-truth-audit, brainstorm), each with full
  references/scripts/assets. Several of these names are ALSO still present
  under live `~/.config/opencode/skills/` (explicitly confirmed: `implement`,
  `brainstorm`, `codebase-truth-audit`; plus `proofpunk` and `cook`). So this
  directory is a **snapshot/archive of copies, not proof the names are absent
  from the live tree**. No README/manifest inside; repo-wide grep for
  `_retired-proofpunk` finds only one inventory line —
  `evidence/v3-release/00-baseline/tool-inventory.md:67-69`: "contains
  `_retired-proofpunk-skills-…` and `_retired-proofpunk-stale-…` — prior
  retirement of proofpunk surfaces". **The reason for the retirement is not
  recorded anywhere I searched** (repo grep, evidence tree, both dirs' contents).
- `_retired-proofpunk-stale-20260902-030412/` (mtime 2026-09-02 03:04:20):
  exactly one file, `proofpunk-cook.md` (activates the `cook` skill). Its
  staleness IS documented: `e2e-evidence/run-command-surface/OPENCODE.md:36-41`
  — the cook command "removed at v2.0.0 … an orphan left by an earlier
  install that the installer does not clean up". Baseline
  `tool-inventory.md:64-66` additionally records `cook` and
  `functional-validation` as **dead names** "alive in the installed tree".
- `~/.config/opencode/skills/cook/` exists as a directory. I did not read its
  SKILL.md, so whether THIS copy is the dead-name duplicate is unverified —
  the documented dead-name locations are `~/.omp/agent/skills/` (ground
  truth) and the retired command above; do not conflate them.

## Unresolved

1. Exact membership of `ConfigPaths.directories()` (what `config.ts:430`
   feeds to the brace pattern beyond global config + `.opencode` walk-up).
   Tried `packages/core/src/config/paths.ts` at v1.18.26 → HTTP 404; docs'
   scope table + `config.ts:438-439` (`.opencode` / `OPENCODE_CONFIG_DIR`
   special-casing) are the best available grounding.
2. Whether live `~/.config/opencode/skills/cook` is itself a dead-name
   leftover (SKILL.md unread — inspection halted to close this artifact).
3. Full 17/17 census of retired names still live under `skills/` — spot-checks
   confirmed 3 of the 17 (`implement`, `brainstorm`, `codebase-truth-audit`)
   plus `proofpunk`; a complete recount was not run.
4. Which exact release introduced the `{skill,skills}` brace glob (would pin
   the plural-canonical floor). Commit search via GitHub returned 0 matches;
   history bisect not attempted (archaeology halted). Installed 1.18.26 and
   dev HEAD both have it — that is the operative fact for the installer.
5. V2-beta docs describe behavior of a beta (`opencode2`); whether the host's
   `opencode` 1.18.26 binary exposes the V2 flat-array `skills` config verbatim
   or only via normalization is inferred from source (`cfg.skills?.paths/.urls`
   reads) — not exercised at runtime (running the CLI was out of scope).
