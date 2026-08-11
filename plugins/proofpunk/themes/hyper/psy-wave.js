// Proofpunk themes — psy-wave (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Psychedelic static — psychic magenta, deep-space purple
const COLORS = {
  "black": "#000000",
  "red": "#FF5252",
  "green": "#64FFDA",
  "yellow": "#FFD740",
  "blue": "#40C4FF",
  "magenta": "#E040FB",
  "cyan": "#7C4DFF",
  "white": "#F3EAFB",
  "lightBlack": "#51436B",
  "lightRed": "#FF8F8F",
  "lightGreen": "#A1FFE9",
  "lightYellow": "#FFE47D",
  "lightBlue": "#7DD7FF",
  "lightMagenta": "#EA7CFC",
  "lightCyan": "#A98AFF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F3EAFB',
    cursorColor: '#E040FB',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(224,64,251,0.35)',
    borderColor: '#0E0816',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #9786AB; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #E040FB; }
      .tab_icon { color: #7C4DFF; }
      .header_header { background: #000000 !important; }
    `
  });
};
