// truth-forge themes — ultraviolet (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Blacklight district — deep violet, UV magenta flare
const COLORS = {
  "black": "#000000",
  "red": "#FF4D6D",
  "green": "#4DFFB8",
  "yellow": "#FFD24D",
  "blue": "#7B8CFF",
  "magenta": "#9D4EDD",
  "cyan": "#FF4DFF",
  "white": "#F0EAF7",
  "lightBlack": "#4E4260",
  "lightRed": "#FF8A9F",
  "lightGreen": "#8AFFD0",
  "lightYellow": "#FFE18A",
  "lightBlue": "#B8C1FF",
  "lightMagenta": "#B981E7",
  "lightCyan": "#FF8AFF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F0EAF7',
    cursorColor: '#9D4EDD',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(157,78,221,0.35)',
    borderColor: '#0D0814',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #9186A3; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #9D4EDD; }
      .tab_icon { color: #FF4DFF; }
      .header_header { background: #000000 !important; }
    `
  });
};
