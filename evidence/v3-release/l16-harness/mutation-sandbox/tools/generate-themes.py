#!/usr/bin/env python3
"""Render the Proofpunk theme pack from the canonical palette source.

Reads  plugins/proofpunk/themes/palettes.json
Writes plugins/proofpunk/themes/omp/*.json        (oh-my-pi custom themes)
       plugins/proofpunk/themes/opencode/*.json   (OpenCode custom themes)
       plugins/proofpunk/themes/hyper/*.js        (Hyper terminal modules)

Deterministic: same palettes.json -> byte-identical output. Hand-edits to
rendered files are overwritten. Stdlib only.
"""
import colorsys
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
THEMES = os.path.join(ROOT, "plugins", "proofpunk", "themes")


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def to_hex(rgb):
    return "#%02X%02X%02X" % tuple(round(c * 255) for c in rgb)


def shift(hexcolor, dl=0.0, ds=0.0, dh=0.0):
    r, g, b = hx(hexcolor)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + dh) % 1.0
    l = min(1, max(0, l + dl))
    s = min(1, max(0, s + ds))
    return to_hex(colorsys.hls_to_rgb(h, l, s))


def mix(a, b, t):
    ra, ga, ba = hx(a)
    rb, gb, bb = hx(b)
    return to_hex((ra + (rb - ra) * t, ga + (gb - ga) * t, ba + (bb - ba) * t))


def ramp(c1, c2, c3):
    """6-step thinking ramp: dim -> accent -> accent2."""
    return [c1, mix(c1, c2, 0.45), mix(c1, c2, 0.8), c2, mix(c2, c3, 0.55), c3]


def omp_theme(name, p):
    d, a, a2 = p["dim"], p["accent"], p["accent2"]
    r = ramp(d, a, a2)
    return {
        "$schema": "https://raw.githubusercontent.com/can1357/oh-my-pi/main/packages/coding-agent/theme-schema.json",
        "name": name,
        "vars": {
            "accent": a, "accent2": a2, "info": p["info"], "success": p["success"],
            "error": p["error"], "warning": p["warning"], "text": p["text"],
            "muted": p["muted"], "dim": d, "panel": p["panel"], "panel2": p["panel2"],
            "dimAccent": mix(a, "#000000", 0.55), "dimAccent2": mix(a2, "#000000", 0.5),
            "toolPendingBg": mix(p["panel"], "#000000", 0.4),
            "toolSuccessBg": mix(p["success"], "#000000", 0.9),
            "toolErrorBg": mix(p["error"], "#000000", 0.88),
            "statusBg": mix(p["panel"], "#000000", 0.3),
        },
        "colors": {
            "accent": "accent", "border": "info", "borderAccent": "accent2", "borderMuted": "dim",
            "success": "success", "error": "error", "warning": "warning",
            "muted": "muted", "dim": "dim", "text": "text", "thinkingText": "dimAccent",
            "selectedBg": "panel2", "userMessageBg": "panel", "userMessageText": "text",
            "customMessageBg": "panel2", "customMessageText": "text", "customMessageLabel": "accent2",
            "toolPendingBg": "toolPendingBg", "toolSuccessBg": "toolSuccessBg", "toolErrorBg": "toolErrorBg",
            "toolTitle": "info", "toolOutput": "muted",
            "mdHeading": "accent", "mdLink": "info", "mdLinkUrl": "dim",
            "mdCode": "accent2", "mdCodeBlock": "text", "mdCodeBlockBorder": "dim",
            "mdQuote": "muted", "mdQuoteBorder": "dimAccent", "mdHr": "dim", "mdListBullet": "accent",
            "toolDiffAdded": "success", "toolDiffRemoved": "error", "toolDiffContext": "muted",
            "link": "info",
            "syntaxComment": "dim", "syntaxKeyword": "accent", "syntaxFunction": "info",
            "syntaxVariable": "text", "syntaxString": "success", "syntaxNumber": "warning",
            "syntaxType": "accent2", "syntaxOperator": "accent", "syntaxPunctuation": "muted",
            "thinkingOff": r[0], "thinkingMinimal": r[1], "thinkingLow": r[2],
            "thinkingMedium": r[3], "thinkingHigh": r[4], "thinkingXhigh": r[5],
            "bashMode": "warning", "pythonMode": "accent2",
            "statusLineBg": "statusBg", "statusLineSep": 236, "statusLineModel": "accent",
            "statusLinePath": "info", "statusLineGitClean": "success", "statusLineGitDirty": "warning",
            "statusLineContext": "accent2", "statusLineSpend": "info", "statusLineStaged": "success",
            "statusLineDirty": "warning", "statusLineUntracked": "error", "statusLineOutput": "accent",
            "statusLineCost": "muted", "statusLineSubagents": "accent2",
        },
        "export": {"pageBg": "#000000", "cardBg": p["panel"], "infoBg": p["panel2"]},
        "symbols": {"preset": "unicode"},
    }


def opencode_theme(name, p):
    a, a2 = p["accent"], p["accent2"]
    return {
        "$schema": "https://opencode.ai/theme.json",
        "defs": {
            "accent": a, "accent2": a2, "info": p["info"], "ok": p["success"],
            "err": p["error"], "warn": p["warning"], "fg": p["text"], "mut": p["muted"],
            "dimc": p["dim"], "void": "#000000", "panel": p["panel"], "panel2": p["panel2"],
            "addBg": mix(p["success"], "#000000", 0.88), "delBg": mix(p["error"], "#000000", 0.86),
        },
        "theme": {
            "primary": "accent", "secondary": "accent2", "accent": "info",
            "error": "err", "warning": "warn", "success": "ok", "info": "info",
            "text": "fg", "textMuted": "mut",
            "background": "void", "backgroundPanel": "panel", "backgroundElement": "panel2",
            "border": "dimc", "borderActive": "accent", "borderSubtle": "dimc",
            "diffAdded": "ok", "diffRemoved": "err", "diffContext": "mut", "diffHunkHeader": "mut",
            "diffHighlightAdded": "ok", "diffHighlightRemoved": "err",
            "diffAddedBg": "addBg", "diffRemovedBg": "delBg", "diffContextBg": "panel",
            "diffLineNumber": "dimc", "diffAddedLineNumberBg": "addBg", "diffRemovedLineNumberBg": "delBg",
            "markdownText": "fg", "markdownHeading": "accent", "markdownLink": "info",
            "markdownLinkText": "accent2", "markdownCode": "ok", "markdownBlockQuote": "mut",
            "markdownEmph": "warn", "markdownStrong": "accent", "markdownHorizontalRule": "dimc",
            "markdownListItem": "accent", "markdownListEnumeration": "accent2",
            "markdownImage": "info", "markdownImageText": "accent2", "markdownCodeBlock": "fg",
            "syntaxComment": "dimc", "syntaxKeyword": "accent", "syntaxFunction": "info",
            "syntaxVariable": "fg", "syntaxString": "ok", "syntaxNumber": "warn",
            "syntaxType": "accent2", "syntaxOperator": "accent", "syntaxPunctuation": "mut",
        },
    }


def hyper_module(name, p, desc):
    a, a2 = p["accent"], p["accent2"]

    def ansi(c, l=0.0, s=0.0):
        return shift(c, dl=l, ds=s)

    colors = {
        "black": "#000000", "red": p["error"], "green": p["success"], "yellow": p["warning"],
        "blue": p["info"], "magenta": a, "cyan": a2, "white": p["text"],
        "lightBlack": p["dim"], "lightRed": ansi(p["error"], 0.12), "lightGreen": ansi(p["success"], 0.12),
        "lightYellow": ansi(p["warning"], 0.12), "lightBlue": ansi(p["info"], 0.12),
        "lightMagenta": ansi(a, 0.12), "lightCyan": ansi(a2, 0.12), "lightWhite": "#FFFFFF",
    }
    cr, cg, cb = hx(a)
    sel = "rgba(%d,%d,%d,0.35)" % (round(cr * 255), round(cg * 255), round(cb * 255))
    return f"""// Proofpunk themes — {name} (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// {desc}
const COLORS = {json.dumps(colors, indent=2)};
exports.decorateConfig = (config) => {{
  return Object.assign({{}}, config, {{
    backgroundColor: '#000000',
    foregroundColor: '{p["text"]}',
    cursorColor: '{a}',
    cursorAccentColor: '#000000',
    selectionColor: '{sel}',
    borderColor: '{p["panel"]}',
    colors: {{ ...(config.colors || {{}}), ...COLORS }},
    css: `
      ${{config.css || ''}}
      .tabs_nav .tabs_list .tab_text {{ color: {p["muted"]}; }}
      .tabs_nav .tabs_list .tab_active .tab_text {{ color: {a}; }}
      .tab_icon {{ color: {a2}; }}
      .header_header {{ background: #000000 !important; }}
    `
  }});
}};
"""


def main():
    with open(os.path.join(THEMES, "palettes.json")) as f:
        doc = json.load(f)
    themes = doc["themes"]
    for sub in ("omp", "opencode", "hyper"):
        os.makedirs(os.path.join(THEMES, sub), exist_ok=True)
    count = 0
    for name, entry in themes.items():
        p = entry["colors"]
        desc = entry.get("description", "")
        with open(os.path.join(THEMES, "omp", name + ".json"), "w") as f:
            json.dump(omp_theme(name, p), f, indent=2)
            f.write("\n")
        with open(os.path.join(THEMES, "opencode", name + ".json"), "w") as f:
            json.dump(opencode_theme(name, p), f, indent=2)
            f.write("\n")
        with open(os.path.join(THEMES, "hyper", name + ".js"), "w") as f:
            f.write(hyper_module(name, p, desc))
        count += 3
    print("rendered %d files for %d themes" % (count, len(themes)))


if __name__ == "__main__":
    sys.exit(main())
