// Proofpunk themes — amber-phosphor (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Retro phosphor terminal — warm amber glow, honey highlights
const COLORS = {
  "black": "#000000",
  "red": "#FF5252",
  "green": "#CFFF5C",
  "yellow": "#FFD73D",
  "blue": "#FFCF5C",
  "magenta": "#FFB000",
  "cyan": "#FF8A00",
  "white": "#FFF3D6",
  "lightBlack": "#5C4F33",
  "lightRed": "#FF8F8F",
  "lightGreen": "#E1FF99",
  "lightYellow": "#FFE47A",
  "lightBlue": "#FFE199",
  "lightMagenta": "#FFC33D",
  "lightCyan": "#FFA63D",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#FFF3D6',
    cursorColor: '#FFB000',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(255,176,0,0.35)',
    borderColor: '#100C06',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #A3906A; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #FFB000; }
      .tab_icon { color: #FF8A00; }
      .header_header { background: #000000 !important; }
    `
  });
};
