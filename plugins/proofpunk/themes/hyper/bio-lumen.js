// Proofpunk themes — bio-lumen (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Abyssal bioluminescence — anglerfish teal, deep-current cyan
const COLORS = {
  "black": "#000000",
  "red": "#FF5C7A",
  "green": "#3DFF9E",
  "yellow": "#C4FF57",
  "blue": "#57F2FF",
  "magenta": "#00E5A0",
  "cyan": "#00B8D4",
  "white": "#E6F7F2",
  "lightBlack": "#39524C",
  "lightRed": "#FF99AC",
  "lightGreen": "#7AFFBD",
  "lightYellow": "#D9FF94",
  "lightBlue": "#94F7FF",
  "lightMagenta": "#23FFBD",
  "lightCyan": "#12E0FF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#E6F7F2',
    cursorColor: '#00E5A0',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(0,229,160,0.35)',
    borderColor: '#060F0D',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #73918A; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #00E5A0; }
      .tab_icon { color: #00B8D4; }
      .header_header { background: #000000 !important; }
    `
  });
};
