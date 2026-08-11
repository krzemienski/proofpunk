// truth-forge themes — neon-tokyo (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Shibuya crossing at midnight — hot pink signage over cyan rain
const COLORS = {
  "black": "#000000",
  "red": "#FF3B5C",
  "green": "#39FF88",
  "yellow": "#FFD600",
  "blue": "#00BFFF",
  "magenta": "#FF2D95",
  "cyan": "#00E5FF",
  "white": "#EDEDF2",
  "lightBlack": "#4A4660",
  "lightRed": "#FF788F",
  "lightGreen": "#76FFAD",
  "lightYellow": "#FFE03D",
  "lightBlue": "#3DCEFF",
  "lightMagenta": "#FF6AB4",
  "lightCyan": "#3DEBFF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#EDEDF2',
    cursorColor: '#FF2D95',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(255,45,149,0.35)',
    borderColor: '#0B0B14',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #8A8FA3; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #FF2D95; }
      .tab_icon { color: #00E5FF; }
      .header_header { background: #000000 !important; }
    `
  });
};
