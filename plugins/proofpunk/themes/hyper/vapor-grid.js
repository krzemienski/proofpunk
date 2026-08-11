// Proofpunk themes — vapor-grid (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Synthwave sunset grid — violet horizon, teal scanlines
const COLORS = {
  "black": "#000000",
  "red": "#FF71CE",
  "green": "#01CD8E",
  "yellow": "#FFFB96",
  "blue": "#05FFA1",
  "magenta": "#B967FF",
  "cyan": "#01CDFE",
  "white": "#EFEAF7",
  "lightBlack": "#4E4468",
  "lightRed": "#FFAEE3",
  "lightGreen": "#0DFEB4",
  "lightYellow": "#FFFDD3",
  "lightBlue": "#42FFB8",
  "lightMagenta": "#D5A4FF",
  "lightCyan": "#3ED9FE",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#EFEAF7',
    cursorColor: '#B967FF',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(185,103,255,0.35)',
    borderColor: '#0D0A14',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #8E86A3; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #B967FF; }
      .tab_icon { color: #01CDFE; }
      .header_header { background: #000000 !important; }
    `
  });
};
