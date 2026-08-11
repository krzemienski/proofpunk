// truth-forge themes — night-drive (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Midnight expressway — dusk indigo, tail-light red
const COLORS = {
  "black": "#000000",
  "red": "#FF5252",
  "green": "#69F0AE",
  "yellow": "#FFC107",
  "blue": "#7986CB",
  "magenta": "#5C6BC0",
  "cyan": "#FF5252",
  "white": "#E8EAF6",
  "lightBlack": "#3E4468",
  "lightRed": "#FF8F8F",
  "lightGreen": "#A1F6CC",
  "lightYellow": "#FFD044",
  "lightBlue": "#A5AEDC",
  "lightMagenta": "#8893D1",
  "lightCyan": "#FF8F8F",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#E8EAF6',
    cursorColor: '#5C6BC0',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(92,107,192,0.35)',
    borderColor: '#0A0C14',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #7E84A3; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #5C6BC0; }
      .tab_icon { color: #FF5252; }
      .header_header { background: #000000 !important; }
    `
  });
};
