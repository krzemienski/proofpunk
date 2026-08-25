#!/usr/bin/env python3
"""Generate the proofpunk GitHub Pages site into proofpunk-main/docs/."""
import os, re, glob, json, html, subprocess, datetime

ROOT = os.environ.get("PROOFPUNK_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs")
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT + "/assets", exist_ok=True)

TODAY = datetime.date.today().isoformat()

def esc(s):
    return html.escape(str(s), quote=True)

def fm_parse(path):
    import yaml
    t = open(path).read()
    m = re.match(r'^---\n(.*?)\n---\n', t, re.S)
    if not m:
        return {}, t
    return (yaml.safe_load(m.group(1)) or {}), t[m.end():]

MMDC = os.environ.get("MMDC", "/tmp/mmdc/node_modules/.bin/mmdc")
_mmd_i = [0]

def fix_mermaid_block(block):
    """Rewrite node ids that collide with mermaid reserved words (end…) into
    aliased ids with display labels. Idempotent."""
    RESERVED = re.compile(r"\bend\b", re.I)
    tokens = set()
    for m in re.finditer(r"([A-Za-z0-9_-]+)\s*-->", block):
        tokens.add(m.group(1))
    for m in re.finditer(r"-->\s*([A-Za-z0-9_-]+)", block):
        tokens.add(m.group(1))
    bad = {t for t in tokens if RESERVED.search(t)}
    if not bad:
        return block
    aliases = {t: f"n{i}" for i, t in enumerate(sorted(bad))}
    def rw(tok):
        return aliases.get(tok, tok)
    lines = []
    for line in block.splitlines():
        m = re.match(r"^(\s*)([A-Za-z0-9_-]+)(\s*-->\s*)([A-Za-z0-9_-]+)(.*)$", line)
        if m:
            indent, a, arrow, b, rest = m.groups()
            lines.append(f"{indent}{rw(a)}{arrow}{rw(b)}{rest}")
        else:
            lines.append(line)
    decl = next((i for i, l in enumerate(lines)
                 if re.match(r"\s*(graph|flowchart|sequenceDiagram|stateDiagram|classDiagram|erDiagram|gantt|pie|gitGraph)", l)), 0)
    defs = [f'  {a}["{t}"]' for t, a in aliases.items()]
    return "\n".join(lines[:decl+1] + defs + lines[decl+1:]) + "\n"

def render_mermaid_html(html_text):
    """Post-pandoc: replace <pre class="mermaid"> blocks with inline SVG."""
    def repl(m):
        code = html.unescape(m.group(1))
        fixed = fix_mermaid_block(code)
        _mmd_i[0] += 1
        idx = _mmd_i[0]
        if os.path.exists(MMDC):
            src = f"/tmp/mmd-{idx}.mmd"; svg = f"/tmp/mmd-{idx}.svg"
            open(src, "w").write(fixed)
            r = subprocess.run([MMDC, "-i", src, "-o", svg, "-b", "transparent", "-t", "dark"],
                               capture_output=True, text=True,
                               env={**os.environ})
            if r.returncode == 0 and os.path.exists(svg):
                body = open(svg).read()
                body = body.replace('id="my-svg"', f'id="mmd-{idx}"', 1).replace("#my-svg", f"#mmd-{idx}")
                return f'<div class="mermaid-diagram">{body}</div>'
        # honest fallback: corrected source + explicit note
        return f'<pre class="mermaid"><code>{html.escape(fixed)}</code></pre><p class="mmd-note">(diagram source — pre-renderer unavailable)</p>'
    return re.sub(r'<pre class="mermaid"><code>(.*?)</code></pre>', repl, html_text, flags=re.S)

def pandoc(md_text):
    r = subprocess.run(["pandoc", "-f", "gfm-raw_html", "-t", "html", "--wrap=none"],
                       input=md_text, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    out = r.stdout
    # escape any literal tags pandoc passed through that are not real HTML
    KNOWN = set("html head body title meta link div span nav main section footer h1 h2 h3 h4 h5 h6 p a ul ol li "
                "table thead tbody tr th td pre code blockquote em strong b i u s dl dt dd hr br img input del sup sub".split())
    def _esc_unknown(m):
        tag = m.group(2).lower()
        if tag in KNOWN:
            return m.group(0)
        return html.escape(m.group(0))
    out = re.sub(r"<(/?)([A-Za-z][A-Za-z0-9-]*)([^<>]*)>", _esc_unknown, out)
    return out

_pandoc_plain = pandoc
def pandoc(md_text):  # noqa: F811 — wrap with mermaid pre-rendering
    return render_mermaid_html(_pandoc_plain(md_text))

# ---------------- data ----------------
skills = []
for d in sorted(glob.glob(ROOT + "/plugins/proofpunk/skills/*/")):
    name = os.path.basename(d.rstrip('/'))
    fm, body = fm_parse(d + "SKILL.md")
    extras = sorted(os.path.relpath(p, d) for p in glob.glob(d + "**/*.*", recursive=True)
                    if not p.endswith("SKILL.md") and "__pycache__" not in p)
    refs = [e for e in extras if e.startswith("references/")]
    scripts = [e for e in extras if e.startswith("scripts/")]
    assets = [e for e in extras if e.startswith("assets/")]
    skills.append({
        "dir": name, "name": fm.get("name", name),
        "description": re.sub(r"\s+", " ", str(fm.get("description", ""))).strip(),
        "extras": extras, "refs": refs, "scripts": scripts, "assets": assets,
    })

commands = []
for p in sorted(glob.glob(ROOT + "/plugins/proofpunk/commands/*.md")):
    fm, body = fm_parse(p)
    commands.append({"slug": os.path.basename(p)[:-3], "description": str(fm.get("description", "")),
                     "hint": str(fm.get("argument-hint", "")).strip('"'), "body": body})

op_commands = []
for p in sorted(glob.glob(ROOT + "/plugins/proofpunk/opencode/commands/*.md")):
    fm, body = fm_parse(p)
    op_commands.append({"slug": os.path.basename(p)[:-3], "description": str(fm.get("description", "")),
                        "hint": str(fm.get("argument-hint", "")).strip('"'), "body": body})

doc_files = sorted(glob.glob(ROOT + "/plugins/proofpunk/docs/*.md"))
ref_files = sorted(glob.glob(ROOT + "/plugins/proofpunk/references/*.md"))

marketplace = json.load(open(ROOT + "/.claude-plugin/marketplace.json"))
VERSION = marketplace["metadata"]["version"]
palettes = json.load(open(ROOT + "/plugins/proofpunk/themes/palettes.json"))["themes"]
THEME_NAMES = [t["name"] if isinstance(t, dict) else t for t in palettes]

# one-line "what it enforces" per skill, from the root README skill table
readme = open(ROOT + "/README.md").read()
enforces = {}
skills_section = re.search(r"## The skills\n(.*?)\n## ", readme, re.S).group(1)
for m in re.finditer(r"\| `([a-z-]+)` \| ([^|]+) \|", skills_section):
    enforces[m.group(1)] = m.group(2).strip()
SKILL_DIRS = len([d for d in glob.glob(os.path.join(ROOT, "plugins/proofpunk/skills/*")) if os.path.isdir(d)])
assert len(enforces) == SKILL_DIRS, f"README skill table has {len(enforces)} rows but {SKILL_DIRS} skill dirs exist"

# skill layers, from README "skill stack" mermaid (codebase-truth-audit added to Deep analysis,
# per README: "the code-truth lane to session-intent's intent lane")
LAYERS = [
    ("ORCHESTRATION", ["implement"]),
    ("PROMPT & PLAN", ["prompt-forge", "brainstorm", "validation-plan", "plan-hardening"]),
    ("EXECUTION", ["cook", "stack-testing", "mobile-validation-runner"]),
    ("PROOF", ["functional-validation", "end-user-testing", "visual-inspection",
               "ui-experience-audit", "full-functional-audit", "tui-testing"]),
    ("DEEP ANALYSIS", ["root-cause-debugging", "red-team-eval", "production-readiness",
                       "session-intent", "codebase-truth-audit"]),
]
layer_of = {}
for lname, members in LAYERS:
    for mname in members:
        layer_of[mname] = lname

N_SKILLS = len(skills)
N_CMDS = len(commands)          # claude commands
N_OPCMDS = len(op_commands)     # opencode variants
N_REFS = len(ref_files)
N_THEMES = len(THEME_NAMES)
N_DOCS = len(doc_files)

print(f"skills={N_SKILLS} cmds={N_CMDS}+{N_OPCMDS} refs={N_REFS} themes={N_THEMES} docs={N_DOCS} v{VERSION}")

# ---------------- chrome ----------------
TABS = [("index.html", "overview"), ("skills.html", "skills"), ("commands.html", "commands"),
        ("docs.html", "docs"), ("install.html", "install")]

def chrome(title, desc, active, main_html, status_left):
    tabs = "".join(
        f'<a href="{href}" class="{"on" if label == active else ""}"><span class="n">{i+1}</span>{label}</a>'
        for i, (href, label) in enumerate(TABS))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">
<div class="chrome">
  <div class="chrome-bar">
    <span class="brand">PROOFPUNK</span><span class="sep">│</span>
    <span class="meta">krzemienski/proofpunk</span><span class="sep">│</span>
    <span class="branch">⑂ main</span><span class="sep">│</span>
    <span class="meta"><span class="led ok"></span>{N_SKILLS} skills</span>
    <span class="meta"><span class="led ok"></span>{N_CMDS}+{N_OPCMDS} commands</span>
    <span class="meta"><span class="led warn"></span>{N_REFS} doctrine refs</span>
    <span class="meta"><span class="led idle"></span>{N_THEMES} themes</span>
  </div>
  <nav class="tabs">{tabs}</nav>
<main>
{main_html}
</main>
  <div class="statusline"><span><b>{esc(status_left)}</b></span><span>v{VERSION} · ⑂ main · {N_SKILLS} skills · {N_CMDS}+{N_OPCMDS} commands · {N_REFS} refs · generated {TODAY}</span></div>
</div>
<footer>
  <div class="wrap" style="padding:0">
    <span>PROOFPUNK — done means proven by end-user testing. No mocks, no stubs, UNVERIFIED never PASS.</span>
    &nbsp;<a href="https://github.com/krzemienski/proofpunk">github.com/krzemienski/proofpunk</a>
    &nbsp;· plugin v{VERSION} · MIT license
  </div>
</footer>
</div>
</body>
</html>
"""

def write(name, content):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)
    print("wrote", name, len(content))

# ---------------- index.html ----------------
theme_preview = ", ".join(THEME_NAMES[:5]) + ", …"
layer_rows = ""
for i, (lname, members) in enumerate(LAYERS, 1):
    names = " · ".join(f'<a href="skills.html#{m}">{m}</a>' for m in members)
    layer_rows += f'''    <div class="brow"><span class="idx">L{i}</span><span><span class="name">{lname}</span>
      <span class="gate">{names}</span></span>
      <span class="badge pass">{len(members)} SKILL{"S" if len(members) > 1 else ""}</span></div>\n'''

_mmd_blocks = re.findall(r"```mermaid\n(.*?)```", readme, re.S)
readme_diagrams = ""
for _b in _mmd_blocks:
    readme_diagrams += render_mermaid_html(f'<pre class="mermaid"><code>{html.escape(_b)}</code></pre>')

index_main = f"""
<section>
  <div class="marker">01 / WHAT IT IS</div>
  <h1>“Done” means proven<br>by end-user testing<span class="cursor"></span></h1>
  <p><strong>Proofpunk</strong> is an execution-first delivery <strong>plugin for Claude Code,
  oh-my-pi (OMP), and OpenCode</strong>: {N_SKILLS} skills where the AI drives the real system as an
  end user — clicking, typing, submitting via MCP/automation tools — and any claim it did not
  actually execute is reported <strong>UNVERIFIED</strong>, never PASS. No mocks, no stubs, no
  test-mode bypasses.</p>
  <div class="cmdline">
    <div><span class="p">~$</span> <span class="c">/plugin marketplace add krzemienski/proofpunk</span></div>
    <div><span class="p">~$</span> <span class="c">/plugin install proofpunk@proofpunk-marketplace</span></div>
    <div class="out">proofpunk v{VERSION} │ {N_SKILLS} skills · {N_CMDS} commands · doctrine hook · <span class="hl">{N_THEMES} flat-black themes</span></div>
  </div>
  <div class="chips">
    <span class="chip"><b>{N_SKILLS}</b> skills</span>
    <span class="chip"><b>{N_CMDS}</b> slash commands <i>+{N_OPCMDS} opencode</i></span>
    <span class="chip"><b>{N_REFS}</b> doctrine references</span>
    <span class="chip"><b>{N_DOCS}</b> architecture docs</span>
    <span class="chip"><b>{N_THEMES}</b> cyberpunk themes</span>
    <span class="chip"><b>3</b> platforms</span>
  </div>
  <div class="grid3">
    <div class="panel"><div class="ptitle">THE IRON RULE</div>
      <p>If the real system doesn't work, <strong>fix the real system</strong>. Never mocks, stubs,
      test doubles, fake endpoints, or test-mode bypasses.</p></div>
    <div class="panel"><div class="ptitle">END-USER ACTOR MANDATE</div>
      <p>Validation is never faked, skipped, or assumed. The AI personally executes the actions a
      real end user would — clicking, tapping, typing, submitting. Unexecuted validation is
      <strong>UNVERIFIED</strong>, never done.</p></div>
    <div class="panel"><div class="ptitle">FRESH EVIDENCE</div>
      <p>Run-scoped, sequential, non-empty, never reused across runs — cited by full path with a
      description of what is SEEN. PASS criteria are defined <strong>before</strong> evidence.</p></div>
  </div>
</section>
<section>
  <div class="marker">02 / THE SKILL STACK</div>
  <h2>{N_SKILLS} skills, five layers, one closed graph</h2>
  <p>Every referenced skill ships — the Related Skills graph is closed. Layers from the repository
  architecture: orchestration composes prompt &amp; plan, execution, proof, and deep analysis;
  every verdict cites the shared doctrine in <code>references/</code>.</p>
  <div class="board">
{layer_rows}  </div>
  <p><a href="skills.html">All {N_SKILLS} skills, in detail →</a></p>
</section>
<section>
  <div class="marker">03 / COMMAND SURFACE</div>
  <h2>Six verbs for the whole pipeline</h2>
  <div class="board">
    <div class="brow"><span class="idx">01</span><span><span class="name">/proofpunk:implement</span>
      <span class="gate">orchestrated front door — mine, forge, plan, execute, prove, report</span></span>
      <span class="badge pass">ORCHESTRATE</span></div>
    <div class="brow"><span class="idx">02</span><span><span class="name">/proofpunk:cook</span>
      <span class="gate">the execution engine — task-by-task, each task proven as the end user</span></span>
      <span class="badge pass">EXECUTE</span></div>
    <div class="brow"><span class="idx">03</span><span><span class="name">/proofpunk:verify</span>
      <span class="gate">end-user test the current work, producing executed proof</span></span>
      <span class="badge pass">PROVE</span></div>
    <div class="brow"><span class="idx">04</span><span><span class="name">/proofpunk:forge-prompt</span>
      <span class="gate">author high-quality prompts on the canonical XML skeleton</span></span>
      <span class="badge pass">AUTHOR</span></div>
    <div class="brow"><span class="idx">05</span><span><span class="name">/proofpunk:rate-prompt</span>
      <span class="gate">score any prompt against the 7-dimension /100 rubric, remediate to file</span></span>
      <span class="badge pass">SCORE</span></div>
    <div class="brow"><span class="idx">06</span><span><span class="name">/proofpunk:truth-audit</span>
      <span class="gate">repo-wide intent-vs-code truth audit with evidence-backed findings</span></span>
      <span class="badge pass">AUDIT</span></div>
  </div>
  <p><a href="commands.html">Full command reference →</a></p>
</section>
<section>
  <div class="marker">04 / THE PROOF</div>
  <h2>Shipped against itself: the mood-ring walkthrough</h2>
  <p><code>examples/mood-ring/</code> is a complete live walkthrough on the Flaskr tutorial app:
  the Mood Ring feature (per-post mood emoji + filter bar), built and audited end-to-end by the
  skills in series. The sealed evidence run holds <strong>19 artifacts, <code>validate OK</code></strong>,
  including 5 browser screenshots committed as PNGs — and <strong>32/32 tests green</strong>
  (24 baseline + 8 new).</p>
  <ul>
    <li>A forged <code>&lt;script&gt;alert(1)&lt;/script&gt;</code> mood POST safely defaults to 😐 with a flash notice.</li>
    <li>An invalid <code>?mood=🦄</code> filter returns 200 unfiltered — no 500, no leak.</li>
    <li>Visual inspection caught (and the loop fixed) a blue-on-blue invisible “All” filter label — a real HIGH defect.</li>
  </ul>
  <div class="grid2">
    <div class="panel"><div class="ptitle">THEMES — {N_THEMES} FLAT-BLACK VARIATIONS</div>
      <p>One canonical palette source renders to OMP, OpenCode, and Hyper formats: {esc(theme_preview)}
      pure <code>#000000</code> canvas, two-neon accent systems, tuned status colors.</p></div>
    <div class="panel"><div class="ptitle">THREE PLATFORMS, ONE PLUGIN</div>
      <p>Claude Code plugin with SessionStart doctrine hook; OMP plugin with doctrine-guard
      extension; OpenCode plugin + agent + commands; plain skills for any agent via the installer.</p></div>
  </div>
</section>
<section>
  <div class="marker">05 / ARCHITECTURE</div>
  <h2>The system, rendered</h2>
  {readme_diagrams}
  <p style="font-size:12.5px"><a href="doc-architecture.html">the full call graph + method ownership →</a></p>
</section>
"""
write("index.html", chrome(
    "proofpunk — done means proven by end-user testing",
    "Proofpunk — execution-first delivery plugin for Claude Code, OMP, and OpenCode. 18 skills where end-user testing is the only PASS.",
    "overview", index_main, "OVERVIEW"))

# ---------------- skills.html ----------------
rows = ""
for i, s in enumerate(skills, 1):
    enf = enforces.get(s["dir"], "")
    rows += (f'    <div class="brow"><span class="idx">{i:02d}</span>'
             f'<span><span class="name"><a href="#{s["dir"]}" style="color:inherit">{s["name"]}</a></span>'
             f'<span class="gate">{esc(enf)}</span></span>'
             f'<span class="badge part">{esc(layer_of.get(s["dir"], ""))}</span></div>\n')

details = ""
for i, s in enumerate(skills, 1):
    extras_html = ""
    groups = [("references", s["refs"]), ("scripts", s["scripts"]), ("assets", s["assets"])]
    bits = []
    for label, items in groups:
        if items:
            bits.append(f"<strong>{len(items)} {label}</strong>: " +
                        ", ".join(f"<code>{esc(os.path.basename(x))}</code>" for x in items[:8]) +
                        (f" +{len(items)-8} more" if len(items) > 8 else ""))
    if bits:
        extras_html = '<p style="font-size:13px">Bundled — ' + " &nbsp;·&nbsp; ".join(bits) + "</p>"
    else:
        extras_html = '<p style="font-size:13px">Single-file skill — doctrine loaded on demand from shared references.</p>'
    details += f"""
  <div class="panel" id="{s["dir"]}">
    <div class="ptitle">{i:02d} / {esc(s["name"].upper())} &nbsp;·&nbsp; {esc(layer_of.get(s["dir"], ""))}</div>
    <p>{esc(s["description"])}</p>
    {extras_html}
    <p style="font-size:12.5px"><a href="https://github.com/krzemienski/proofpunk/tree/main/plugins/proofpunk/skills/{s["dir"]}">source → plugins/proofpunk/skills/{s["dir"]}/</a></p>
  </div>
"""

skills_main = f"""
<section>
  <div class="marker">01 / THE ARSENAL</div>
  <h1>{N_SKILLS} skills<span class="cursor"></span></h1>
  <p>Every skill ships in the plugin — the Related Skills graph is closed, nothing dangles.
  One-line enforcement contracts below; full frontmatter descriptions and bundled materials in
  the detail cards further down. Hands-on invocation examples for every skill live in the
  <a href="doc-usage-guide.html">usage guide</a>.</p>
  <div class="board">
{rows}  </div>
</section>
<section>
  <div class="marker">02 / DETAIL CARDS</div>
  <h2>What each skill actually does</h2>
{details}
</section>
"""
write("skills.html", chrome(
    f"skills — {N_SKILLS} skills — proofpunk",
    f"All {N_SKILLS} proofpunk skills with real frontmatter descriptions, layers, and bundled references/scripts.",
    "skills", skills_main, "SKILLS"))

# ---------------- commands.html ----------------
cmd_blocks = ""
for i, c in enumerate(commands, 1):
    body_html = pandoc(c["body"])
    cmd_blocks += f"""
  <div class="panel" id="{c["slug"]}">
    <div class="ptitle">{i:02d} / /proofpunk:{esc(c["slug"])}</div>
    <p><strong>{esc(c["description"])}</strong></p>
    <div class="cmdline" style="margin:12px 0">
      <div><span class="p">~$</span> <span class="c">/proofpunk:{esc(c["slug"])} {esc(c["hint"])}</span></div>
    </div>
    <div class="doc">{body_html}</div>
  </div>
"""

op_rows = ""
for i, c in enumerate(op_commands, 1):
    op_rows += (f'    <div class="brow"><span class="idx">OC{i}</span>'
                f'<span><span class="name">/{esc(c["slug"])}</span>'
                f'<span class="gate">{esc(c["description"])} — <code>{esc(c["hint"])}</code></span></span>'
                f'<span class="badge pass">SHIPS</span></div>\n')

commands_main = f"""
<section>
  <div class="marker">01 / CLAUDE CODE COMMANDS</div>
  <h1>{N_CMDS} slash commands<span class="cursor"></span></h1>
  <p>Each command activates its skill with a strict contract. These are the real command files
  from <code>plugins/proofpunk/commands/</code>, rendered verbatim. Conventions:
  <code>&lt;angle&gt;</code> required, <code>[bracket]</code> optional, <code>A | B</code> alternatives.</p>
{cmd_blocks}
</section>
<section>
  <div class="marker">02 / OPENCODE VARIANTS</div>
  <h2>The same six, prefixed for OpenCode</h2>
  <p>OpenCode commands live in <code>plugins/proofpunk/opencode/commands/</code> and invoke the
  same skills under the <code>proofpunk-</code> prefix.</p>
  <div class="board">
{op_rows}  </div>
</section>
"""
write("commands.html", chrome(
    f"commands — {N_CMDS}+{N_OPCMDS} commands — proofpunk",
    "Proofpunk slash command reference: implement, cook, verify, forge-prompt, rate-prompt, truth-audit — plus OpenCode variants.",
    "commands", commands_main, "COMMANDS"))

# ---------------- docs.html + doc/ref subpages ----------------
def doc_desc(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = lines[0].lstrip('# ').strip() if lines else ""
    para = ""
    for l in lines[1:]:
        if not l.startswith('#') and not l.startswith('```'):
            para = l
            break
    return title, para

DOC_TITLES = {}
for p in doc_files:
    base = os.path.basename(p)[:-3]
    text = open(p).read()
    title, para = doc_desc(text)
    DOC_TITLES[base] = (title, para)
    page = f"""
<section>
  <div class="marker">DOC / {esc(base.upper())}</div>
  <div class="doc">
{pandoc(text)}
  </div>
  <p style="font-size:12.5px"><a href="https://github.com/krzemienski/proofpunk/blob/main/plugins/proofpunk/docs/{base}.md">source → plugins/proofpunk/docs/{base}.md</a> · <a href="docs.html">← all docs</a></p>
</section>
"""
    write(f"doc-{base}.html", chrome(f"{title} — proofpunk docs", para[:160] or title,
                                     "docs", page, f"DOC:{base.upper()}"))

REF_TITLES = {}
for p in ref_files:
    base = os.path.basename(p)[:-3]
    text = open(p).read()
    title, para = doc_desc(text)
    REF_TITLES[base] = (title, para)
    page = f"""
<section>
  <div class="marker">DOCTRINE / {esc(base.upper())}</div>
  <div class="doc">
{pandoc(text)}
  </div>
  <p style="font-size:12.5px"><a href="https://github.com/krzemienski/proofpunk/blob/main/plugins/proofpunk/references/{base}.md">source → plugins/proofpunk/references/{base}.md</a> · <a href="docs.html">← all docs</a></p>
</section>
"""
    write(f"ref-{base}.html", chrome(f"{title} — proofpunk doctrine", para[:160] or title,
                                     "docs", page, f"REF:{base.upper()}"))

doc_rows = ""
for i, (base, (title, para)) in enumerate(DOC_TITLES.items(), 1):
    doc_rows += (f'    <div class="brow"><span class="idx">D{i}</span>'
                 f'<span><span class="name"><a href="doc-{base}.html" style="color:inherit">{esc(title)}</a></span>'
                 f'<span class="gate">{esc(para[:180])}</span></span>'
                 f'<span class="badge pass">RENDERED</span></div>\n')

ref_rows = ""
for i, (base, (title, para)) in enumerate(REF_TITLES.items(), 1):
    ref_rows += (f'    <div class="brow"><span class="idx">R{i}</span>'
                 f'<span><span class="name"><a href="ref-{base}.html" style="color:inherit">{esc(title)}</a></span>'
                 f'<span class="gate">{esc(para[:180])}</span></span>'
                 f'<span class="badge part">DOCTRINE</span></div>\n')

docs_main = f"""
<section>
  <div class="marker">01 / PROJECT DOCS</div>
  <h1>Architecture &amp; decisions<span class="cursor"></span></h1>
  <p>The four documents from <code>plugins/proofpunk/docs/</code>, rendered in full as subpages —
  how the {N_SKILLS} skills execute as one system, how they were consolidated from a 664-skill
  universe scan, hands-on invocation examples, and the v1.0.0 validation record.</p>
  <div class="board">
{doc_rows}  </div>
</section>
<section>
  <div class="marker">02 / SHARED DOCTRINE</div>
  <h2>{N_REFS} ruling references</h2>
  <p>The doctrine every skill loads on demand — the Iron Rule, the End-User Actor Mandate, the
  evidence contract, severity model, platform routing, preflight checks, and CI gate
  classification. Rendered from <code>plugins/proofpunk/references/</code>.</p>
  <div class="board">
{ref_rows}  </div>
</section>
"""
write("docs.html", chrome("docs — architecture & doctrine — proofpunk",
                          "Proofpunk architecture, usage guide, consolidation decisions, validation results, and the 13 ruling doctrine references.",
                          "docs", docs_main, "DOCS"))

# ---------------- install.html ----------------
install_main = f"""
<section>
  <div class="marker">01 / CLAUDE CODE</div>
  <h1>Install proofpunk<span class="cursor"></span></h1>
  <p>One plugin: {N_SKILLS} skills, {N_CMDS} slash commands, and the SessionStart doctrine hook —
  from the marketplace in two commands.</p>
  <div class="cmdline">
    <div><span class="p">~$</span> <span class="c">/plugin marketplace add krzemienski/proofpunk</span></div>
    <div><span class="p">~$</span> <span class="c">/plugin install proofpunk@proofpunk-marketplace</span></div>
    <div class="out">proofpunk v{VERSION} · category: quality · license: MIT</div>
  </div>
</section>
<section>
  <div class="marker">02 / OH-MY-PI (OMP)</div>
  <h2>OMP plugin — skills, commands, doctrine-guard extension</h2>
  <p>Catalog at <code>.omp-plugin/marketplace.json</code>, with a Claude-compatible
  <code>.claude-plugin/</code> fallback.</p>
  <div class="cmdline">
    <div><span class="p">~$</span> <span class="c">omp plugin marketplace add krzemienski/proofpunk</span></div>
    <div><span class="p">~$</span> <span class="c">omp plugin install proofpunk@proofpunk</span></div>
  </div>
</section>
<section>
  <div class="marker">03 / OPENCODE &amp; ANY AGENT</div>
  <h2>OpenCode — or plain skills anywhere</h2>
  <p>The installer drops the plugin, commands, agent, and skills into
  <code>~/.config/opencode/</code> — or use the full plugin via the same catalog above. For any
  other agent, install plain skills into any directory with
  <code>tools/proofpunk-install.sh</code>:</p>
  <div class="cmdline">
    <div><span class="p">~$</span> <span class="c">bash tools/proofpunk-install.sh --target claude-code</span><span class="out">            # ~/.claude/skills (also read by OpenCode + OMP)</span></div>
    <div><span class="p">~$</span> <span class="c">bash tools/proofpunk-install.sh --target omp --themes --plugins</span><span class="out"> # oh-my-pi skills + themes + extension</span></div>
    <div><span class="p">~$</span> <span class="c">bash tools/proofpunk-install.sh --target opencode --themes --plugins</span></div>
    <div><span class="p">~$</span> <span class="c">bash tools/proofpunk-install.sh --target agents</span><span class="out">                 # ~/.agents/skills (shared)</span></div>
  </div>
  <p>Or download <code>proofpunk-marketplace.tar.gz</code> from the repo's release artifacts and
  extract it into your marketplaces directory.</p>
  <div class="grid2">
    <div class="panel"><div class="ptitle">SELF-CONTAINED SKILLS</div>
      <p>The installer rewrites <code>../../references/X</code> citations to bundled copies inside
      each skill, injects the <code>proofpunk-doctrine/</code> bundle, and verifies the result —
      every installed skill stands alone.</p></div>
    <div class="panel"><div class="ptitle">SURGICAL CONTROL</div>
      <p><code>--only a,b,c</code> subsets, <code>--override</code> with timestamped
      <code>.bak</code> backups, <code>--dry-run</code> plans, <code>--verify</code> self-check,
      <code>--inject-claude-md</code> idempotent rules block.</p></div>
  </div>
</section>
<section>
  <div class="marker">04 / THEMES</div>
  <h2>{N_THEMES} flat-black cyberpunk themes</h2>
  <p><code>--themes</code> copies the pack into every detected platform. One canonical palette
  source (<code>themes/palettes.json</code>) renders to three formats: OMP theme JSON
  (<code>~/.omp/agent/themes/</code>), OpenCode theme JSON
  (<code>~/.config/opencode/themes/</code>), and Hyper modules (merge into
  <code>~/.hyper.js</code>). Claude Code has no custom-palette API, so the Claude plugin ships the
  themes for the other surfaces you run beside it.</p>
  <p style="font-size:13px">{esc(", ".join(THEME_NAMES))}</p>
</section>
"""
write("install.html", chrome("install — proofpunk",
                             "Install proofpunk for Claude Code, oh-my-pi (OMP), OpenCode, or any agent — plugin, marketplace, installer, and themes.",
                             "install", install_main, "INSTALL"))
print("DONE")
