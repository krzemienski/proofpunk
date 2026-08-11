// Proofpunk themes — solar-flare (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Coronal mass ejection — molten orange, flare red
const COLORS = {
  "black": "#000000",
  "red": "#FF4757",
  "green": "#A6FF4D",
  "yellow": "#FFD24D",
  "blue": "#FFBF47",
  "magenta": "#FF9500",
  "cyan": "#FF3D00",
  "white": "#FFF0E3",
  "lightBlack": "#5C4A3E",
  "lightRed": "#FF848F",
  "lightGreen": "#C5FF8A",
  "lightYellow": "#FFE18A",
  "lightBlue": "#FFD484",
  "lightMagenta": "#FFAE3D",
  "lightCyan": "#FF6C3D",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#FFF0E3',
    cursorColor: '#FF9500',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(255,149,0,0.35)',
    borderColor: '#120A06',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #A38D7A; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #FF9500; }
      .tab_icon { color: #FF3D00; }
      .header_header { background: #000000 !important; }
    `
  });
};
