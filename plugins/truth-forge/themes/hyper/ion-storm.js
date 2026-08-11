// truth-forge themes — ion-storm (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Lightning over the data district — electric blue, violet strikes
const COLORS = {
  "black": "#000000",
  "red": "#F87171",
  "green": "#34D399",
  "yellow": "#FBBF24",
  "blue": "#38BDF8",
  "magenta": "#4D7CFE",
  "cyan": "#B24BF3",
  "white": "#E8ECF5",
  "lightBlack": "#3E4A68",
  "lightRed": "#FBABAB",
  "lightGreen": "#66DEB2",
  "lightYellow": "#FCD160",
  "lightBlue": "#73D1FA",
  "lightMagenta": "#8AA9FE",
  "lightCyan": "#CB84F7",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#E8ECF5',
    cursorColor: '#4D7CFE',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(77,124,254,0.35)',
    borderColor: '#080A12',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #7E8AA3; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #4D7CFE; }
      .tab_icon { color: #B24BF3; }
      .header_header { background: #000000 !important; }
    `
  });
};
