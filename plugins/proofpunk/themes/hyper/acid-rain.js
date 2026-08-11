// Proofpunk themes — acid-rain (flat-black cyberpunk, Hyper terminal)
// Install: copy into your Hyper plugins, or merge the colors below into ~/.hyper.js config.
// Toxic drizzle on chrome — acid lime with bioluminescent mint
const COLORS = {
  "black": "#000000",
  "red": "#FF4D6D",
  "green": "#7CFF00",
  "yellow": "#EEFF00",
  "blue": "#00E5A0",
  "magenta": "#B6FF00",
  "cyan": "#00FFB3",
  "white": "#F0F5E8",
  "lightBlack": "#46503F",
  "lightRed": "#FF8A9F",
  "lightGreen": "#9BFF3D",
  "lightYellow": "#F2FF3D",
  "lightBlue": "#23FFBD",
  "lightMagenta": "#C8FF3D",
  "lightCyan": "#3DFFC5",
  "lightWhite": "#FFFFFF"
};
exports.decorateConfig = (config) => {
  return Object.assign({}, config, {
    backgroundColor: '#000000',
    foregroundColor: '#F0F5E8',
    cursorColor: '#B6FF00',
    cursorAccentColor: '#000000',
    selectionColor: 'rgba(182,255,0,0.35)',
    borderColor: '#0A0F08',
    colors: { ...(config.colors || {}), ...COLORS },
    css: `
      ${config.css || ''}
      .tabs_nav .tabs_list .tab_text { color: #87917F; }
      .tabs_nav .tabs_list .tab_active .tab_text { color: #B6FF00; }
      .tab_icon { color: #00FFB3; }
      .header_header { background: #000000 !important; }
    `
  });
};
