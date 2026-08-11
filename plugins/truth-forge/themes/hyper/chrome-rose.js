// truth-forge themes — chrome-rose (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Rose-gold chrome — brushed metal, neon blush
const COLORS = {
  "black": "#000000",
  "red": "#FF6B81",
  "green": "#7FD9A8",
  "yellow": "#E8C87F",
  "blue": "#9FB8E8",
  "magenta": "#F27D9D",
  "cyan": "#C0C6D6",
  "white": "#F2EEF0",
  "lightBlack": "#544A51",
  "lightRed": "#FFA8B5",
  "lightGreen": "#AEE7C8",
  "lightYellow": "#F1DEB3",
  "lightBlue": "#D0DDF4",
  "lightMagenta": "#F8B5C7",
  "lightCyan": "#E5E8EE",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F2EEF0',
    cursorColor: '#F27D9D',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(242,125,157,0.35)',
    borderColor: '#110C0E',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #968B93; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #F27D9D; }
      .tab_icon { color: #C0C6D6; }
      .header_header { background: #000000 !important; }
    `
  });
};
