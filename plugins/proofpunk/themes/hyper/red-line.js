// Proofpunk themes — red-line (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Akira tail-light streak — arterial red, ember orange
const COLORS = {
  "black": "#000000",
  "red": "#FF3B3B",
  "green": "#8AFF6A",
  "yellow": "#FFC400",
  "blue": "#FFB454",
  "magenta": "#FF2A2A",
  "cyan": "#FF7A18",
  "white": "#F5ECEC",
  "lightBlack": "#5C4040",
  "lightRed": "#FF7878",
  "lightGreen": "#BAFFA7",
  "lightYellow": "#FFD23D",
  "lightBlue": "#FFCF91",
  "lightMagenta": "#FF6767",
  "lightCyan": "#FF9D55",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F5ECEC',
    cursorColor: '#FF2A2A',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(255,42,42,0.35)',
    borderColor: '#120808',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #A38B8B; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #FF2A2A; }
      .tab_icon { color: #FF7A18; }
      .header_header { background: #000000 !important; }
    `
  });
};
