// Proofpunk themes — miami-vice (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Ocean Drive neon — flamingo pink, pool-water cyan
const COLORS = {
  "black": "#000000",
  "red": "#FF5C8A",
  "green": "#5CF2B8",
  "yellow": "#FFE28A",
  "blue": "#F9C6FF",
  "magenta": "#FF6EC7",
  "cyan": "#42E2E8",
  "white": "#FCEFF7",
  "lightBlack": "#5C4657",
  "lightRed": "#FF99B6",
  "lightGreen": "#95F7D1",
  "lightYellow": "#FFF1C7",
  "lightBlue": "#FFFFFF",
  "lightMagenta": "#FFABDF",
  "lightCyan": "#79EAEF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#FCEFF7',
    cursorColor: '#FF6EC7',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(255,110,199,0.35)',
    borderColor: '#120A10',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #A38FA0; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #FF6EC7; }
      .tab_icon { color: #42E2E8; }
      .header_header { background: #000000 !important; }
    `
  });
};
