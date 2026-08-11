// Proofpunk themes — code-fall (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// The Matrix has you — phosphor green fall on void black
const COLORS = {
  "black": "#000000",
  "red": "#FF4060",
  "green": "#00FF41",
  "yellow": "#BFFF00",
  "blue": "#4DFFA6",
  "magenta": "#00FF41",
  "cyan": "#008F11",
  "white": "#D6FFDC",
  "lightBlack": "#2E4A36",
  "lightRed": "#FF7D93",
  "lightGreen": "#3DFF6F",
  "lightYellow": "#CEFF3D",
  "lightBlue": "#8AFFC5",
  "lightMagenta": "#3DFF6F",
  "lightCyan": "#00CC18",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#D6FFDC',
    cursorColor: '#00FF41',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(0,255,65,0.35)',
    borderColor: '#040D06',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #5C8A66; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #00FF41; }
      .tab_icon { color: #008F11; }
      .header_header { background: #000000 !important; }
    `
  });
};
