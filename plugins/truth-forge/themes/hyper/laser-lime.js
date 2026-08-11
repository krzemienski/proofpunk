// truth-forge themes — laser-lime (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Laser tag arena — high-beam lemon, lime grid
const COLORS = {
  "black": "#000000",
  "red": "#FF5C7A",
  "green": "#6AFF5C",
  "yellow": "#FFF047",
  "blue": "#9DFF57",
  "magenta": "#E8FF47",
  "cyan": "#47FFA0",
  "white": "#F7FCE8",
  "lightBlack": "#525C3E",
  "lightRed": "#FF99AC",
  "lightGreen": "#A2FF99",
  "lightYellow": "#FFF584",
  "lightBlue": "#C1FF94",
  "lightMagenta": "#F0FF84",
  "lightCyan": "#84FFC0",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F7FCE8',
    cursorColor: '#E8FF47',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(232,255,71,0.35)',
    borderColor: '#0C0F06',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #97A07F; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #E8FF47; }
      .tab_icon { color: #47FFA0; }
      .header_header { background: #000000 !important; }
    `
  });
};
