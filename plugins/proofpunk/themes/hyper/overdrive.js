// Proofpunk themes — overdrive (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Redline RPM — turbo cyan, tachometer green
const COLORS = {
  "black": "#000000",
  "red": "#FF4757",
  "green": "#64FF47",
  "yellow": "#E8FF47",
  "blue": "#47E8FF",
  "magenta": "#00FFCC",
  "cyan": "#A0FF00",
  "white": "#E8FCF5",
  "lightBlack": "#2E574C",
  "lightRed": "#FF848F",
  "lightGreen": "#98FF84",
  "lightYellow": "#F0FF84",
  "lightBlue": "#84F0FF",
  "lightMagenta": "#3DFFD8",
  "lightCyan": "#B7FF3D",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#E8FCF5',
    cursorColor: '#00FFCC',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(0,255,204,0.35)',
    borderColor: '#061210',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #6B9E8F; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #00FFCC; }
      .tab_icon { color: #A0FF00; }
      .header_header { background: #000000 !important; }
    `
  });
};
