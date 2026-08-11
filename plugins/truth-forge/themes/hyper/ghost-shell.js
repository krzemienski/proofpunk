// truth-forge themes — ghost-shell (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Ghost in the Shell — pale thermoptic cyan, gunmetal blue
const COLORS = {
  "black": "#000000",
  "red": "#E86A92",
  "green": "#7FE8C0",
  "yellow": "#D9C77A",
  "blue": "#7FD4FF",
  "magenta": "#9BE8E8",
  "cyan": "#5B7C99",
  "white": "#EAF2F2",
  "lightBlack": "#3E4A52",
  "lightRed": "#F09FB9",
  "lightGreen": "#B3F1DA",
  "lightYellow": "#E7DBAA",
  "lightBlue": "#BCE9FF",
  "lightMagenta": "#CDF3F3",
  "lightCyan": "#7F9AB3",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#EAF2F2',
    cursorColor: '#9BE8E8',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(155,232,232,0.35)',
    borderColor: '#0A0E10',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #7A8B92; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #9BE8E8; }
      .tab_icon { color: #5B7C99; }
      .header_header { background: #000000 !important; }
    `
  });
};
