// truth-forge themes — static-noir (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Film-noir CRT — monochrome static, one red wire
const COLORS = {
  "black": "#000000",
  "red": "#FF2D55",
  "green": "#C8C8C8",
  "yellow": "#B8B8B8",
  "blue": "#A0A0B0",
  "magenta": "#E8E8E8",
  "cyan": "#FF2D55",
  "white": "#F0F0F0",
  "lightBlack": "#4A4A4A",
  "lightRed": "#FF6A87",
  "lightGreen": "#E7E7E7",
  "lightYellow": "#D7D7D7",
  "lightBlue": "#C1C1CC",
  "lightMagenta": "#FFFFFF",
  "lightCyan": "#FF6A87",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F0F0F0',
    cursorColor: '#E8E8E8',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(232,232,232,0.35)',
    borderColor: '#0B0B0C',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #8A8A8A; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #E8E8E8; }
      .tab_icon { color: #FF2D55; }
      .header_header { background: #000000 !important; }
    `
  });
};
