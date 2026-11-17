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
// assertFits (below) measures both promises, and topics.mjs runs it on every icon.
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

// ---------------------------------------------------------------------------------------
// Fit check. The inline <svg> clips at its view box, so an icon that leaves the grid ships
// cut off, and one that does not start at LEFT sits out of line with its title.
// ---------------------------------------------------------------------------------------

const STEPS = 256; // points sampled along each curve; the error is under 0.001 units here

// An elliptical arc from (x1, y1) to (x2, y2) as sampled points (SVG 1.1, appendix F.6.5).
function arcPoints(x1, y1, rx, ry, rotation, large, sweep, x2, y2) {
  if (rx === 0 || ry === 0 || (x1 === x2 && y1 === y2)) return [[x2, y2]];
  const phi = (rotation * Math.PI) / 180, cos = Math.cos(phi), sin = Math.sin(phi);
  const dx = (x1 - x2) / 2, dy = (y1 - y2) / 2;
  const px = cos * dx + sin * dy, py = -sin * dx + cos * dy;
  rx = Math.abs(rx); ry = Math.abs(ry);
  const scale = (px * px) / (rx * rx) + (py * py) / (ry * ry);
  if (scale > 1) { rx *= Math.sqrt(scale); ry *= Math.sqrt(scale); }
  const num = rx * rx * ry * ry - rx * rx * py * py - ry * ry * px * px;
  const k = (large === sweep ? -1 : 1) * Math.sqrt(Math.max(0, num) / (rx * rx * py * py + ry * ry * px * px));
  const cxp = (k * rx * py) / ry, cyp = (-k * ry * px) / rx;
  const cx = cos * cxp - sin * cyp + (x1 + x2) / 2, cy = sin * cxp + cos * cyp + (y1 + y2) / 2;
  const angle = (ux, uy) => Math.atan2(uy, ux);
  const start = angle((px - cxp) / rx, (py - cyp) / ry);
  let delta = angle((-px - cxp) / rx, (-py - cyp) / ry) - start;
  if (sweep && delta < 0) delta += 2 * Math.PI;
  if (!sweep && delta > 0) delta -= 2 * Math.PI;
  const points = [];
  for (let i = 1; i <= STEPS; i++) {
    const t = start + (delta * i) / STEPS;
    points.push([cx + rx * Math.cos(t) * cos - ry * Math.sin(t) * sin, cy + rx * Math.cos(t) * sin + ry * Math.sin(t) * cos]);
  }
  return points;
}

function cubicPoints(p0, p1, p2, p3) {
  const points = [];
  for (let i = 1; i <= STEPS; i++) {
    const t = i / STEPS, u = 1 - t;
    points.push([0, 1].map((k) => u * u * u * p0[k] + 3 * u * u * t * p1[k] + 3 * u * t * t * p2[k] + t * t * t * p3[k]));
  }
  return points;
}

const ARITY = { M: 2, L: 2, H: 1, V: 1, C: 6, S: 4, A: 7, Z: 0 };

// Every point a path's centre line passes through, as [x, y] pairs. It throws on a
// command it does not measure, so a new kind of path cannot pass unmeasured.
export function pathPoints(d) {
  const points = [];
  let x = 0, y = 0, startX = 0, startY = 0, lastControl = null;
  const tokens = [...d.matchAll(/([a-zA-Z])([^a-zA-Z]*)/g)];
  if (tokens.map((t) => t[0]).join('') !== d.trim()) throw new Error(`cannot read path "${d}"`);
  for (const [, cmd, args] of tokens) {
    const C = cmd.toUpperCase(), rel = cmd !== C, arity = ARITY[C];
    if (arity === undefined) throw new Error(`path command "${cmd}" in "${d}" is not measured; use M L H V C S A Z`);
    const v = (args.match(/-?(?:\d+\.?\d*|\.\d+)/g) || []).map(Number);
    if (arity === 0 ? v.length : v.length === 0 || v.length % arity) throw new Error(`"${cmd}" in "${d}" has ${v.length} numbers; it takes ${arity} at a time`);
    if (C === 'Z') { x = startX; y = startY; lastControl = null; continue; }
    for (let i = 0; i < v.length; i += arity) {
      const n = v.slice(i, i + arity), ox = rel ? x : 0, oy = rel ? y : 0;
      let control = null;
      if (C === 'M' || C === 'L') { x = ox + n[0]; y = oy + n[1]; points.push([x, y]); if (C === 'M' && i === 0) { startX = x; startY = y; } }
      else if (C === 'H') { x = ox + n[0]; points.push([x, y]); }
      else if (C === 'V') { y = oy + n[0]; points.push([x, y]); }
      else if (C === 'A') { const end = [ox + n[5], oy + n[6]]; points.push(...arcPoints(x, y, n[0], n[1], n[2], n[3], n[4], ...end)); [x, y] = end; }
      else {
        const first = C === 'C' ? [ox + n[0], oy + n[1]] : lastControl ? [2 * x - lastControl[0], 2 * y - lastControl[1]] : [x, y];
        const rest = C === 'C' ? n.slice(2) : n;
        control = [ox + rest[0], oy + rest[1]];
        const end = [ox + rest[2], oy + rest[3]];
        points.push(...cubicPoints([x, y], first, control, end));
        [x, y] = end;
      }
      lastControl = control;
    }
  }
  if (!points.length) throw new Error(`path "${d}" draws nothing`);
  return points;
}

// Throws unless the icon starts at LEFT and its painted area, the centre line widened by
// half the stroke, stays inside the view box.
export function assertFits(name) {
  const points = icons[name].flatMap(pathPoints);
  const xs = points.map((p) => p[0]), ys = points.map((p) => p[1]), half = STROKE / 2, slack = 0.005;
  const left = Math.min(...xs), right = Math.max(...xs), top = Math.min(...ys), bottom = Math.max(...ys);
  if (![left, right, top, bottom].every(Number.isFinite)) throw new Error(`lib/topic-icons.mjs: "${name}" could not be measured`);
  const at = (n) => Math.round(n * 100) / 100;
  if (Math.abs(left - LEFT) > slack) throw new Error(`lib/topic-icons.mjs: "${name}" starts at x = ${at(left)}; every icon starts at ${LEFT} so it lines up with its title`);
  if (right + half > LEFT - half + GRID + slack || top - half < -slack || bottom + half > GRID + slack) {
    throw new Error(`lib/topic-icons.mjs: "${name}" paints x ${at(left - half)} to ${at(right + half)}, y ${at(top - half)} to ${at(bottom + half)}, outside its view box (x ${LEFT - half} to ${LEFT - half + GRID}, y 0 to ${GRID})`);
  }
  return { left: at(left), right: at(right), top: at(top), bottom: at(bottom) };
}
