// Line icons for the Topics grid on /articles/, one per hub.
//
// These are the site's own chrome, drawn like the theme toggle and the menu close mark:
// one stroke weight, no fills, no accent, on a 24-unit grid. They are separate from
// lib/glyphs.js on purpose. That library draws the article figures, and its fills,
// hatching and tones belong inside a figure; next to a title they read as decoration.
//
// Each icon is a list of path `d` strings. Every drawing's leftmost point sits at
// x = LEFT, so the icons line up with the text under them. The stroke's colour and
// weight come from the .topic-glyph rule in static/css/main.css, which must use STROKE.
export const GRID = 24;   // the drawing grid, in view-box units
export const SIZE = 28;   // the rendered width and height, in CSS px
export const LEFT = 3;
export const STROKE = 1.5;

export const icons = {
  // Technical documentation: a page with a folded corner and two lines of text.
  doc: ['M3 2.75h10l6 6v12.5H3z', 'M13 2.75v6h6', 'M7 13h8', 'M7 17h8'],
  // AI search: a lens over the passage an answer quotes.
  search: ['M18 10.5a7.5 7.5 0 1 1-15 0a7.5 7.5 0 0 1 15 0z', 'M16 16l5.25 5.25', 'M7.25 9h6.5', 'M7.25 12h4'],
  // Developer content: a speech bubble holding code.
  bubble: ['M3 3.75h18v12.5H10.5l-4.5 4v-4H3z', 'M9.5 7.5L7 10l2.5 2.5', 'M14.5 7.5L17 10l-2.5 2.5', 'M12.75 7l-1.5 6'],
  // AI agents: the loop, with the arrowhead that sends it round again.
  loop: ['M21 12a9 9 0 1 1-2.64-6.36', 'M19 1.5v4.75h-4.75'],
  // Agent memory: a store with a record written into it.
  store: [
    'M21 6c0 1.8-4 3.25-9 3.25S3 7.8 3 6s4-3.25 9-3.25S21 4.2 21 6z',
    'M3 6v12c0 1.8 4 3.25 9 3.25s9-1.45 9-3.25V6',
    'M3 12c0 1.8 4 3.25 9 3.25s9-1.45 9-3.25',
  ],
  // RAG: two vectors from one origin, compared by the angle between them.
  vectors: ['M3 2.75v18.5h18.25', 'M3 21.25L10 5.5', 'M3 21.25L20 10.5'],
  // Coding agents: a terminal with a prompt and a cursor.
  terminal: ['M3 3.75h18v16.5H3z', 'M7 8.5l3 3-3 3', 'M12.5 15.5h4.5'],
  // LLM inference: a chip, its pins and its core.
  chip: ['M7 7h10v10H7z', 'M10 3v4', 'M14 3v4', 'M10 17v4', 'M14 17v4', 'M3 10h4', 'M3 14h4', 'M17 10h4', 'M17 14h4', 'M10.5 10.5h3v3h-3z'],
};

// The inline <svg> for one icon. The view box starts at the painted left edge (the
// leftmost point less half the stroke), so the drawing is flush with the text column.
export function iconSvg(name) {
  const paths = icons[name].map((d) => `<path d="${d}"/>`).join('');
  return `<svg class="topic-glyph" viewBox="${LEFT - STROKE / 2} 0 ${GRID} ${GRID}" width="${SIZE}" height="${SIZE}" aria-hidden="true" focusable="false">${paths}</svg>`;
}
