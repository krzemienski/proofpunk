// Proofpunk themes — void-orchid (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Orchid blooming in the void — soft violet, moonlit blue
const COLORS = {
  "black": "#000000",
  "red": "#FF5370",
  "green": "#C3E88D",
  "yellow": "#FFCB6B",
  "blue": "#89DDFF",
  "magenta": "#C792EA",
  "cyan": "#82AAFF",
  "white": "#EAE4F2",
  "lightBlack": "#4A4258",
  "lightRed": "#FF90A3",
  "lightGreen": "#DEF2C0",
  "lightYellow": "#FFE1A8",
  "lightBlue": "#C6EFFF",
  "lightMagenta": "#E1C5F4",
  "lightCyan": "#BFD4FF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#EAE4F2',
    cursorColor: '#C792EA',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(199,146,234,0.35)',
    borderColor: '#0C0912',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #8A80A0; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #C792EA; }
      .tab_icon { color: #82AAFF; }
      .header_header { background: #000000 !important; }
    `
  });
};
