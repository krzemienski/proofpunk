// Proofpunk themes — cold-fusion (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Reactor core ice — frost blue, reactor white
const COLORS = {
  "black": "#000000",
  "red": "#FF7A9E",
  "green": "#7FFFD4",
  "yellow": "#FFE8A8",
  "blue": "#A8E6FF",
  "magenta": "#7FDBFF",
  "cyan": "#E8F4FF",
  "white": "#F0F7FF",
  "lightBlack": "#47586B",
  "lightRed": "#FFB7CB",
  "lightGreen": "#BCFFE9",
  "lightYellow": "#FFF8E5",
  "lightBlue": "#E5F8FF",
  "lightMagenta": "#BCECFF",
  "lightCyan": "#FFFFFF",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F0F7FF',
    cursorColor: '#7FDBFF',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(127,219,255,0.35)',
    borderColor: '#090D12',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #8AA3B8; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #7FDBFF; }
      .tab_icon { color: #E8F4FF; }
      .header_header { background: #000000 !important; }
    `
  });
};
