# Proofpunk themes — flat-black cyberpunk pack

20 theme variations on the classic [Hyper](https://hyper.is) theme contract:
pure flat-black canvas, neon accent pairs, high-contrast highlights. One
canonical palette per theme, rendered to three formats:

| Format | Directory | Install target |
|---|---|---|
| OMP (oh-my-pi) theme JSON | `themes/omp/*.json` | `~/.omp/agent/themes/` |
| OpenCode theme JSON | `themes/opencode/*.json` | `~/.config/opencode/themes/` |
| Hyper terminal module | `themes/hyper/*.js` | referenced from `~/.hyper.js` |

The installer (`tools/proofpunk-install.sh --themes`) copies these into the
right place for every platform it detects. OMP selects a theme via the
`theme.dark` / `theme.light` settings or `/theme`; OpenCode via
`~/.config/opencode/tui.json` (`"theme": "<name>"`) or `/themes`; Hyper by
adding the module to its plugins array.

## The 20 variations

| Theme | Mood | Accent | Accent 2 | Info |
|---|---|---|---|---|
| `neon-tokyo` | Shibuya crossing at midnight — hot pink signage over cyan rain | `#FF2D95` | `#00E5FF` | `#00BFFF` |
| `acid-rain` | Toxic drizzle on chrome — acid lime with bioluminescent mint | `#B6FF00` | `#00FFB3` | `#00E5A0` |
| `vapor-grid` | Synthwave sunset grid — violet horizon, teal scanlines | `#B967FF` | `#01CDFE` | `#05FFA1` |
| `ion-storm` | Lightning over the data district — electric blue, violet strikes | `#4D7CFE` | `#B24BF3` | `#38BDF8` |
| `red-line` | Akira tail-light streak — arterial red, ember orange | `#FF2A2A` | `#FF7A18` | `#FFB454` |
| `ghost-shell` | Ghost in the Shell — pale thermoptic cyan, gunmetal blue | `#9BE8E8` | `#5B7C99` | `#7FD4FF` |
| `amber-phosphor` | Retro phosphor terminal — warm amber glow, honey highlights | `#FFB000` | `#FF8A00` | `#FFCF5C` |
| `ultraviolet` | Blacklight district — deep violet, UV magenta flare | `#9D4EDD` | `#FF4DFF` | `#7B8CFF` |
| `laser-lime` | Laser tag arena — high-beam lemon, lime grid | `#E8FF47` | `#47FFA0` | `#9DFF57` |
| `miami-vice` | Ocean Drive neon — flamingo pink, pool-water cyan | `#FF6EC7` | `#42E2E8` | `#F9C6FF` |
| `code-fall` | The Matrix has you — phosphor green fall on void black | `#00FF41` | `#008F11` | `#4DFFA6` |
| `chrome-rose` | Rose-gold chrome — brushed metal, neon blush | `#F27D9D` | `#C0C6D6` | `#9FB8E8` |
| `bio-lumen` | Abyssal bioluminescence — anglerfish teal, deep-current cyan | `#00E5A0` | `#00B8D4` | `#57F2FF` |
| `solar-flare` | Coronal mass ejection — molten orange, flare red | `#FF9500` | `#FF3D00` | `#FFBF47` |
| `cold-fusion` | Reactor core ice — frost blue, reactor white | `#7FDBFF` | `#E8F4FF` | `#A8E6FF` |
| `psy-wave` | Psychedelic static — psychic magenta, deep-space purple | `#E040FB` | `#7C4DFF` | `#40C4FF` |
| `night-drive` | Midnight expressway — dusk indigo, tail-light red | `#5C6BC0` | `#FF5252` | `#7986CB` |
| `overdrive` | Redline RPM — turbo cyan, tachometer green | `#00FFCC` | `#A0FF00` | `#47E8FF` |
| `void-orchid` | Orchid blooming in the void — soft violet, moonlit blue | `#C792EA` | `#82AAFF` | `#89DDFF` |
| `static-noir` | Film-noir CRT — monochrome static, one red wire | `#E8E8E8` | `#FF2D55` | `#A0A0B0` |

## Design contract

- **Flat black, always.** Every background is `#000000`; panels lift to the
  theme's near-black tint (`panel` / `panel2`). No gradients, no images.
- **Two-neon accent system.** `accent` drives primary chrome (headings,
  active borders, keywords); `accent2` is the counter-neon (types, labels,
  secondary highlights). `info` carries links and tool titles.
- **Semantic status colors** stay readable on black: success/error/warning
  are tuned per family so every variation keeps diff and status legibility.
- **Thinking ramp.** OMP `thinkingOff → thinkingXhigh` is a six-step ramp
  from the theme's dim tone through accent to accent2 — depth of thought
  reads as rising neon intensity.
- **Hyper fidelity.** The `.js` modules implement Hyper's `decorateConfig`
  contract: the 16 ANSI colors, cursor/selection/border, and composed CSS
  (they extend `config.css` instead of replacing it, so they play nice with
  other Hyper plugins).

## Regenerating

Palettes are the single source of truth in `themes/palettes.json`. Render all
three formats with:

```
python3 tools/generate-themes.py
```

This rewrites `themes/omp/`, `themes/opencode/`, and `themes/hyper/`
deterministically — hand-edits to rendered files will be overwritten.
