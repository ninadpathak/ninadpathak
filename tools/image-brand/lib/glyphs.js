/* Glyph library for the ninadpathak.com image brand (GUIDELINE.md §7).
 * Each glyph draws a concept, centred on 0,0 inside a w×h box, from the same parts:
 * 1.25 px line strokes, surface fills, hatching, and at most one accent element.
 * Glyphs carry no words. Runs in the browser before plate.js.
 */
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const el = (name, attrs, parent) => {
    const n = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) n.setAttribute(k, typeof v === 'number' ? String(Math.round(v * 100) / 100) : v);
    if (parent) parent.appendChild(n);
    return n;
  };
  const P = (g, d, cls) => el('path', { d, class: cls }, g);
  // Glyph corners snap to the radius tokens: 1 for cells and tiles, 2 for bodies, 4 for frames.
  const snap = (rx) => (rx === 0 ? 0 : rx <= 1.5 ? 1 : rx <= 3 ? 2 : 4);
  const R = (g, x, y, w, h, cls, rx = 0) => el('rect', { x, y, width: w, height: h, rx: snap(rx), class: cls }, g);
  const C = (g, cx, cy, r, cls) => el('circle', { cx, cy, r, class: cls }, g);
  const r2 = (n) => Math.round(n * 100) / 100;
  const hatch = (o) => `url(#${o.hatch})`;

  // ---------------------------------------------------------------- badges (14–18 px)
  const BADGES = {
    lock(g, a) {
      R(g, -4, -1, 8, 6, a ? 'gl-accent' : 'gl-solid', 1);
      P(g, 'M-2.6,-1V-3.4A2.6,2.6 0 0 1 2.6,-3.4V-1', a ? 'gl-accent-line' : 'gl-ink');
    },
    globe(g, a) {
      const c = a ? 'gl-accent-line' : 'gl-ink';
      C(g, 0, 0, 5.2, c);
      el('ellipse', { cx: 0, cy: 0, rx: 2.2, ry: 5.2, class: c }, g);
      P(g, 'M-5.2,0H5.2', c);
    },
    question(g, a) {
      const c = a ? 'gl-accent-line' : 'gl-ink';
      P(g, 'M-2.4,-2.2A2.5,2.5 0 1 1 1,0.1C0,0.6 0,1.2 0,2', c);
      C(g, 0, 4, 0.9, a ? 'gl-accent' : 'gl-solid');
    },
    check(g, a) { P(g, 'M-3.4,0.2L-1,2.6L3.6,-2.6', a ? 'gl-accent-line gl-thick' : 'gl-ink gl-thick'); },
    cross(g, a) { P(g, 'M-2.8,-2.8L2.8,2.8M2.8,-2.8L-2.8,2.8', a ? 'gl-accent-line gl-thick' : 'gl-ink gl-thick'); },
    person(g, a) {
      C(g, 0, -2.2, 2.4, a ? 'gl-accent' : 'gl-solid');
      P(g, 'M-4.2,4.6C-4.2,0.8 4.2,0.8 4.2,4.6Z', a ? 'gl-accent' : 'gl-solid');
    },
    flag(g, a) {
      P(g, 'M-2.5,5V-5', 'gl-ink');
      P(g, 'M-2.5,-5L4.5,-2.5L-2.5,0Z', a ? 'gl-accent' : 'gl-solid');
    },
  };
  function badge(g, x, y, name, accent, r = 8.5) {
    const b = el('g', { transform: `translate(${r2(x)},${r2(y)})` }, g);
    C(b, 0, 0, r, accent ? 'gl-badge gl-badge-accent' : 'gl-badge');
    BADGES[name](b, accent);
    return b;
  }

  // ---------------------------------------------------------------- tile glyphs
  const G = {};

  // A page: folded corner, heading bar, text lines, optional badge.
  G.doc = (g, w, h, o, dx = 0, dy = 0) => {
    const pw = Math.min(w * 0.62, h * 0.72), ph = pw * 1.28, f = pw * 0.28;
    const x0 = dx - pw / 2, y0 = dy - ph / 2;
    P(g, `M${r2(x0)},${r2(y0)}H${r2(x0 + pw - f)}L${r2(x0 + pw)},${r2(y0 + f)}V${r2(y0 + ph)}H${r2(x0)}Z`, 'gl-fill');
    P(g, `M${r2(x0 + pw - f)},${r2(y0)}V${r2(y0 + f)}H${r2(x0 + pw)}`, 'gl-line');
    R(g, x0 + 5, y0 + 6, pw * 0.42, 2.6, o.accent ? 'gl-accent' : 'gl-solid');
    [0.72, 0.6, 0.72, 0.44].forEach((k, i) => R(g, x0 + 5, y0 + 14 + i * 5.5, (pw - 10) * k, 1.6, 'gl-bar'));
    if (o.badge) badge(g, x0 + pw - 1, y0 + ph - 2, o.badge, o.accent);
  };

  // Two pages, one public and one private, joined by a contract line.
  G.pair = (g, w, h, o) => {
    G.doc(g, w * 0.8, h * 0.82, { badge: 'lock' }, -9, -4);
    G.doc(g, w * 0.8, h * 0.82, { badge: 'globe', accent: o.accent }, 9, 5);
  };

  // A reader: head and shoulders, optional badge.
  G.reader = (g, w, h, o) => {
    const s = Math.min(w, h);
    C(g, 0, -s * 0.17, s * 0.15, 'gl-fill');
    P(g, `M${r2(-s * 0.28)},${r2(s * 0.3)}C${r2(-s * 0.28)},${r2(s * 0.02)} ${r2(s * 0.28)},${r2(s * 0.02)} ${r2(s * 0.28)},${r2(s * 0.3)}Z`, 'gl-fill');
    if (o.badge) badge(g, s * 0.27, s * 0.22, o.badge, o.accent);
  };

  // An application window: title rule, sidebar, content blocks.
  G.window = (g, w, h, o) => {
    const ww = w * 0.78, wh = h * 0.66, x0 = -ww / 2, y0 = -wh / 2;
    R(g, x0, y0, ww, wh, 'gl-fill', 3);
    P(g, `M${r2(x0)},${r2(y0 + 7)}H${r2(x0 + ww)}`, 'gl-hair');
    R(g, x0 + 3, y0 + 2.2, 2.6, 2.6, o.accent ? 'gl-accent' : 'gl-solid', 1.3);
    R(g, x0 + 4, y0 + 11, ww * 0.24, wh - 15, 'gl-fill2', 1);
    [0.6, 0.45, 0.55].forEach((k, i) => R(g, x0 + ww * 0.34, y0 + 12 + i * 6, (ww * 0.6) * k, 1.6, 'gl-bar'));
  };

  // A loop: a 300° track with a chevron, three particles, and a hub.
  G.loop = (g, w, h, o) => {
    const r = Math.min(w, h) * 0.34;
    const a0 = (-50 * Math.PI) / 180, a1 = (220 * Math.PI) / 180;
    const p = (a, rr = r) => [rr * Math.cos(a), rr * Math.sin(a)];
    C(g, 0, 0, r + 5, 'gl-hair');
    C(g, 0, 0, r - 5, 'gl-hair');
    const [sx, sy] = p(a0), [ex, ey] = p(a1);
    const cls = o.accent ? 'gl-accent-line gl-thick' : 'gl-ink gl-thick';
    P(g, `M${r2(sx)},${r2(sy)}A${r2(r)},${r2(r)} 0 1 1 ${r2(ex)},${r2(ey)}`, cls);
    const tip = p(a1 + 0.3), b1 = p(a1, r - 5), b2 = p(a1, r + 5);
    P(g, `M${r2(b1[0])},${r2(b1[1])}L${r2(tip[0])},${r2(tip[1])}L${r2(b2[0])},${r2(b2[1])}`, cls);
    [[a1 - 0.35, 2.2], [a1 - 0.6, 1.6], [a1 - 0.8, 1.1]].forEach(([a, rr]) => { const [x, y] = p(a); C(g, x, y, rr, o.accent ? 'gl-accent' : 'gl-solid'); });
    C(g, 0, 0, r * 0.32, 'gl-fill');
    C(g, 0, 0, 1.8, o.accent ? 'gl-accent' : 'gl-solid');
  };

  // Token tiles: rows of tiles; the last row grows (context accumulating).
  G.tokens = (g, w, h, o) => {
    const rows = Array.isArray(o.rows) ? o.rows : o.rows ? [o.rows] : [5, 4, 6];
    const tw = 7, th = 8, gap = 2.2;
    const maxCols = Math.max(...rows);
    const x0 = -(maxCols * (tw + gap) - gap) / 2, y0 = -(rows.length * (th + gap) - gap) / 2;
    rows.forEach((n, ri) => {
      for (let i = 0; i < n; i++) {
        const x = x0 + i * (tw + gap), y = y0 + ri * (th + gap);
        const last = ri === rows.length - 1 && i === n - 1;
        const cls = last && o.accent !== false ? 'gl-accent' : ri === 0 ? 'gl-solid' : ri === 1 ? 'gl-fill gl-hatch-host' : 'gl-fill';
        R(g, x, y, tw, th, cls, 1.5);
        if (ri === 1) R(g, x, y, tw, th, 'gl-hatch', 1.5).setAttribute('fill', hatch(o));
      }
    });
  };

  // A context window: bracketed rows of tokens; the newest row runs past the right bracket.
  G.context = (g, w, h, o) => {
    const rows = Array.isArray(o.rows) ? o.rows : [6, 7, 9], tw = 7, th = 8, gap = 2.2, inside = 7;
    const ww = inside * (tw + gap) - gap, x0 = -ww / 2 - 6, y0 = -(rows.length * (th + gap) - gap) / 2;
    const bx0 = x0 - 5, bx1 = x0 + ww + 5, by0 = y0 - 6, by1 = -y0 + 6;
    P(g, `M${r2(bx0 + 4)},${r2(by0)}H${r2(bx0)}V${r2(by1)}H${r2(bx0 + 4)}M${r2(bx1 - 4)},${r2(by0)}H${r2(bx1)}V${r2(by1)}H${r2(bx1 - 4)}`, 'gl-ink gl-thick');
    rows.forEach((n, ri) => {
      for (let i = 0; i < n; i++) {
        const x = x0 + i * (tw + gap), y = y0 + ri * (th + gap);
        const over = i >= inside;
        R(g, x, y, tw, th, over ? 'gl-accent' : ri === 0 ? 'gl-solid' : 'gl-fill', 1);
        if (ri === 1 && !over) R(g, x, y, tw, th, 'gl-hatch', 1).setAttribute('fill', hatch(o));
      }
    });
  };

  // Vectors: axes with three embeddings; the nearest pair shares an accent arc.
  G.vectors = (g, w, h, o) => {
    const s = Math.min(w, h) * 0.38;
    P(g, `M${r2(-s)},${r2(s)}H${r2(s + 4)}M${r2(-s)},${r2(s)}V${r2(-s - 4)}`, 'gl-line');
    P(g, `M${r2(s + 1)},${r2(s - 2.5)}L${r2(s + 4)},${r2(s)}L${r2(s + 1)},${r2(s + 2.5)}M${r2(-s - 2.5)},${r2(-s - 1)}L${r2(-s)},${r2(-s - 4)}L${r2(-s + 2.5)},${r2(-s - 1)}`, 'gl-line');
    const tips = [[s * 0.9, -s * 0.35], [s * 0.55, -s * 0.85], [-s * 0.3, -s * 0.95]];
    tips.forEach(([x, y], i) => {
      P(g, `M${r2(-s)},${r2(s)}L${r2(x)},${r2(y)}`, i < 2 ? (o.accent ? 'gl-accent-line' : 'gl-ink') : 'gl-ink');
      C(g, x, y, 2.2, i < 2 && o.accent ? 'gl-accent' : 'gl-solid');
    });
    P(g, `M${r2(-s + s * 0.9)},${r2(s - s * 0.55)}A${r2(s * 0.95)},${r2(s * 0.95)} 0 0 0 ${r2(-s + s * 0.62)},${r2(s - s * 0.88)}`, 'gl-hair');
  };

  // A waveform: voice in, with the newest syllable in accent.
  G.wave = (g, w, h, o) => {
    const bars = [0.25, 0.5, 0.85, 0.6, 1, 0.7, 0.4, 0.8, 0.5, 0.3, 0.55];
    const bw = 3, gap = 2.4, x0 = -(bars.length * (bw + gap) - gap) / 2, hh = h * 0.34;
    bars.forEach((k, i) => R(g, x0 + i * (bw + gap), -hh * k, bw, 2 * hh * k, i === 8 && o.accent ? 'gl-accent' : 'gl-solid', 1));
    P(g, `M${r2(x0 - 4)},0H${r2(-x0 + 4)}`, 'gl-hair');
  };

  // A plug meeting a socket: a connector, client, or integration point.
  G.plug = (g, w, h, o) => {
    R(g, -20, -8, 14, 16, 'gl-fill', 2);
    P(g, 'M-6,-4H0M-6,4H0', 'gl-ink gl-thick');
    R(g, 4, -10, 16, 20, 'gl-fill2', 2);
    P(g, 'M8,-4H12M8,4H12', 'gl-ink gl-thick');
    P(g, 'M-26,0H-20M20,0H26', o.accent ? 'gl-accent-line' : 'gl-line');
    C(g, 0, 0, 1.6, o.accent ? 'gl-accent' : 'gl-solid');
  };

  // A ranked list: rows that shorten with rank; `hi` marks one row in accent.
  G.ranked = (g, w, h, o) => {
    const n = o.rows || 6, rh = 3.2, gap = 3.4, x0 = -w * 0.32, ww = w * 0.64, y0 = -(n * (rh + gap) - gap) / 2;
    for (let i = 0; i < n; i++) {
      const y = y0 + i * (rh + gap);
      C(g, x0 - 4, y + rh / 2, 1, 'gl-solid');
      R(g, x0, y, ww * (1 - i * 0.09), rh, i === (o.hi ?? -1) ? 'gl-accent' : 'gl-bar', 1);
    }
  };

  // A globe: meridians and parallels; the network or the public web.
  G.globe = (g, w, h, o) => {
    const r = Math.min(w, h) * 0.34;
    C(g, 0, 0, r, 'gl-fill');
    el('ellipse', { cx: 0, cy: 0, rx: r * 0.45, ry: r, class: 'gl-line' }, g);
    P(g, `M${r2(-r)},0H${r2(r)}M${r2(-r * 0.87)},${r2(-r * 0.5)}H${r2(r * 0.87)}M${r2(-r * 0.87)},${r2(r * 0.5)}H${r2(r * 0.87)}`, 'gl-hair');
    C(g, r * 0.5, -r * 0.35, 2, o.accent ? 'gl-accent' : 'gl-solid');
  };

  // A store: three stacked cylinder discs; durable storage.
  G.store = (g, w, h, o) => {
    const rx = Math.min(w * 0.3, 16), ry = 4.5;
    for (const [i, y] of [[0, 8], [1, 0], [2, -8]]) {
      P(g, `M${-rx},${y}V${y + 6}A${rx},${ry} 0 0 0 ${rx},${y + 6}V${y}`, 'gl-fill');
      el('ellipse', { cx: 0, cy: y, rx, ry, class: i === 2 && o.accent ? 'gl-fill gl-accent-edge' : 'gl-fill' }, g);
    }
  };

  // Experts: a grid of experts with only a few lit (`on` of `n`).
  G.experts = (g, w, h, o) => {
    const n = o.n || 256, on = o.on || 8, cols = o.cols || 32, rows = Math.ceil(n / cols), s = o.s || 3.6, gap = Math.max(1.2, s / 3);
    const lit = new Set(Array.from({ length: on }, (_, k) => (k * 37 + 11) % n));
    const x0 = -(cols * (s + gap) - gap) / 2, y0 = -(rows * (s + gap) - gap) / 2;
    for (let i = 0; i < n; i++) R(g, x0 + (i % cols) * (s + gap), y0 + Math.floor(i / cols) * (s + gap), s, s, lit.has(i) ? 'gl-accent' : 'gl-cell', 1);
  };

  // A ledger: rows stacked newest on top; superseded rows hatched, never removed.
  G.ledger = (g, w, h, o) => {
    const n = o.rows || 3, rw = w * 0.62, rh = 8, gap = 3, y0 = -(n * (rh + gap) - gap) / 2;
    for (let i = 0; i < n; i++) {
      const y = y0 + i * (rh + gap), newest = i === 0;
      R(g, -rw / 2, y, rw, rh, newest ? 'gl-fill gl-accent-edge' : 'gl-fill', 1);
      if (!newest) R(g, -rw / 2, y, rw, rh, 'gl-hatch', 1).setAttribute('fill', hatch(o));
      C(g, -rw / 2 + 5, y + rh / 2, 1.4, newest ? 'gl-accent' : 'gl-solid');
    }
  };

  // Memory cells: a grid filled to a level; the newest cell is accent; optional checkpoint flag.
  G.cells = (g, w, h, o) => {
    const cols = o.cols || 6, rows = o.rows || 4, s = 6, gap = 2;
    const fill = o.fill ?? 0.6;
    const n = Math.round(cols * rows * fill);
    const x0 = -(cols * (s + gap) - gap) / 2, y0 = -(rows * (s + gap) - gap) / 2;
    for (let i = 0; i < cols * rows; i++) {
      const x = x0 + (i % cols) * (s + gap), y = y0 + Math.floor(i / cols) * (s + gap);
      R(g, x, y, s, s, i < n - 1 ? 'gl-solid' : i === n - 1 ? 'gl-accent' : 'gl-cell', 1);
    }
    if (o.flag) badge(g, -x0 + 4, y0 - 2, 'flag', false, 7.5);
  };

  // An eye with a log trace: observation.
  G.eye = (g, w, h, o) => {
    const r = Math.min(w, h) * 0.34;
    P(g, `M${r2(-r)},${r2(-3)}Q0,${r2(-r * 0.9)} ${r2(r)},${r2(-3)}Q0,${r2(r * 0.6)} ${r2(-r)},${r2(-3)}Z`, 'gl-fill');
    C(g, 0, -3.5, r * 0.32, 'gl-line');
    C(g, 0, -3.5, r * 0.12, o.accent ? 'gl-accent' : 'gl-solid');
    [0.9, 0.6, 0.75].forEach((k, i) => { C(g, -r, r * 0.55 + i * 4.5, 0.9, 'gl-solid'); R(g, -r + 3, r * 0.55 + i * 4.5 - 0.8, (2 * r - 3) * k, 1.6, 'gl-bar'); });
  };

  // A model: three isometric slabs; the top slab carries the accent edge.
  G.core = (g, w, h, o) => {
    const b = Math.min(w * 0.36, h * 0.5), a = b * 0.5, t = 5;
    for (const [i, dy] of [[0, 11], [1, 0], [2, -11]]) {
      const top = i === 2;
      P(g, `M${r2(-b)},${r2(dy)}L0,${r2(dy + a)}L0,${r2(dy + a + t)}L${r2(-b)},${r2(dy + t)}Z`, 'gl-fill2');
      const right = P(g, `M0,${r2(dy + a)}L${r2(b)},${r2(dy)}L${r2(b)},${r2(dy + t)}L0,${r2(dy + a + t)}Z`, 'gl-fill');
      const hr = P(g, right.getAttribute('d'), 'gl-hatch'); hr.setAttribute('fill', hatch(o));
      P(g, `M0,${r2(dy - a)}L${r2(b)},${r2(dy)}L0,${r2(dy + a)}L${r2(-b)},${r2(dy)}Z`, top && o.accent ? 'gl-fill gl-accent-edge' : 'gl-fill');
      // Weight lines across the top slab.
      if (top) for (const k of [-0.25, 0.25]) P(g, `M${r2(-b / 2 + k * b)},${r2(dy - a / 2 + k * a)}L${r2(b / 2 + k * b)},${r2(dy + a / 2 + k * a)}`, 'gl-hair');
    }
  };

  // A tool set: four small tiles, each with its own instrument.
  G.tools = (g, w, h, o) => {
    const s = 17, gap = 4, x0 = -(2 * s + gap) / 2, y0 = -(2 * s + gap) / 2;
    const at = (i) => [x0 + (i % 2) * (s + gap), y0 + Math.floor(i / 2) * (s + gap)];
    for (let i = 0; i < 4; i++) { const [x, y] = at(i); R(g, x, y, s, s, 'gl-fill', 2); }
    let [x, y] = at(0); C(g, x + 7.5, y + 7.5, 3.6, 'gl-ink'); P(g, `M${x + 10.2},${y + 10.2}L${x + 13.5},${y + 13.5}`, 'gl-ink gl-thick');
    [x, y] = at(1); P(g, `M${x + 4},${y + 5}L${x + 7.5},${y + 8.5}L${x + 4},${y + 12}M${x + 9},${y + 12.5}H${x + 13.5}`, o.accent ? 'gl-accent-line' : 'gl-ink');
    [x, y] = at(2);
    const brace = (bx, dir) => `M${bx + 2 * dir},${y + 4}Q${bx},${y + 4} ${bx},${y + 6.5}V${y + 7.5}Q${bx},${y + 8.5} ${bx - 1.2 * dir},${y + 8.5}Q${bx},${y + 8.5} ${bx},${y + 10.5}V${y + 11}Q${bx},${y + 13} ${bx + 2 * dir},${y + 13}`;
    P(g, brace(x + 5, 1) + brace(x + 12, -1), 'gl-ink');
    [x, y] = at(3); el('ellipse', { cx: x + 8.5, cy: y + 5, rx: 4.5, ry: 1.8, class: 'gl-ink' }, g); P(g, `M${x + 4},${y + 5}V${y + 12}A4.5,1.8 0 0 0 ${x + 13},${y + 12}V${y + 5}M${x + 4},${y + 8.5}A4.5,1.8 0 0 0 ${x + 13},${y + 8.5}`, 'gl-ink');
  };

  // A rack: three server units with vents and status lights.
  G.rack = (g, w, h, o) => {
    const rw = w * 0.62, uh = 8.5, gap = 3, y0 = -(3 * uh + 2 * gap) / 2, x0 = -rw / 2;
    for (let i = 0; i < 3; i++) {
      const y = y0 + i * (uh + gap);
      R(g, x0, y, rw, uh, 'gl-fill', 1.5);
      for (let v = 0; v < 4; v++) P(g, `M${r2(x0 + 4 + v * 3)},${r2(y + 2.2)}V${r2(y + uh - 2.2)}`, 'gl-hair');
      C(g, x0 + rw - 5, y + uh / 2, 1.3, i === 0 && o.accent ? 'gl-accent' : 'gl-solid');
      C(g, x0 + rw - 9.5, y + uh / 2, 1.3, 'gl-cell');
    }
  };

  // A chip: package, pins on four sides, hatched die.
  G.chip = (g, w, h, o) => {
    const s = Math.min(w, h) * 0.6, d = s * 0.52;
    for (let i = 0; i < 5; i++) {
      const k = -s / 2 + (s / 6) * (i + 1);
      P(g, `M${r2(k)},${r2(-s / 2 - 4)}V${r2(-s / 2)}M${r2(k)},${r2(s / 2)}V${r2(s / 2 + 4)}M${r2(-s / 2 - 4)},${r2(k)}H${r2(-s / 2)}M${r2(s / 2)},${r2(k)}H${r2(s / 2 + 4)}`, 'gl-line');
    }
    R(g, -s / 2, -s / 2, s, s, 'gl-fill', 2);
    R(g, -d / 2, -d / 2, d, d, 'gl-fill2', 1);
    R(g, -d / 2, -d / 2, d, d, 'gl-hatch', 1).setAttribute('fill', hatch(o));
    R(g, -d / 2, -d / 2, d, d, o.accent ? 'gl-accent-line' : 'gl-line', 1);
    C(g, -s / 2 + 3.5, -s / 2 + 3.5, 1, 'gl-solid');
  };

  // An inbox tray with work arriving.
  G.inbox = (g, w, h, o) => {
    const tw = w * 0.6, th = h * 0.26, y0 = 2;
    P(g, `M${r2(-tw / 2)},${r2(y0)}V${r2(y0 + th)}H${r2(tw / 2)}V${r2(y0)}`, 'gl-ink');
    P(g, `M${r2(-tw / 2)},${r2(y0)}H${r2(-tw / 6)}L${r2(-tw / 8)},${r2(y0 + 5)}H${r2(tw / 8)}L${r2(tw / 6)},${r2(y0)}H${r2(tw / 2)}`, 'gl-ink');
    R(g, -6, -15, 12, 9, o.accent ? 'gl-accent' : 'gl-fill', 1.5);
    P(g, 'M0,-4V1M-3,-1.5L0,1.5L3,-1.5', 'gl-ink');
  };

  // A stop gate: octagon with a bar.
  G.stop = (g, w, h, o) => {
    const r = Math.min(w, h) * 0.3;
    const pts = Array.from({ length: 8 }, (_, i) => { const a = (Math.PI / 8) * (2 * i + 1); return `${r2(r * Math.cos(a))},${r2(r * Math.sin(a))}`; });
    P(g, `M${pts.join('L')}Z`, 'gl-fill');
    R(g, -r * 0.55, -2, r * 1.1, 4, o.accent ? 'gl-accent' : 'gl-solid', 1);
  };

  // Action: a play head pushing a bar. Object: an isometric cube. Context: a key.
  G.action = (g, w, h, o) => {
    P(g, 'M-9,-11L9,0L-9,11Z', o.accent ? 'gl-accent' : 'gl-fill');
    P(g, 'M13,-11V11', 'gl-ink gl-thick');
  };
  G.object = (g, w, h, o) => {
    const s = 12;
    P(g, `M0,${-s}L${s},${-s / 2}L0,0L${-s},${-s / 2}Z`, o.accent ? 'gl-fill gl-accent-edge' : 'gl-fill');
    P(g, `M${-s},${-s / 2}L0,0V${s}L${-s},${s / 2}Z`, 'gl-fill2');
    const right = P(g, `M0,0L${s},${-s / 2}V${s / 2}L0,${s}Z`, 'gl-fill');
    P(g, right.getAttribute('d'), 'gl-hatch').setAttribute('fill', hatch(o));
  };
  G.key = (g, w, h, o) => {
    C(g, -8, 0, 6.5, 'gl-fill');
    C(g, -8, 0, 2.2, o.accent ? 'gl-accent' : 'gl-solid');
    P(g, 'M-1.5,0H13M8,0V5M12,0V4', 'gl-ink gl-thick');
  };

  // A heading slab: a single bar with a short ghost bar after it (a vague topic label).
  G.outline = (g, w, h, o) => {
    const pw = w * 0.7, x0 = -pw / 2;
    R(g, x0, -h * 0.42, pw, h * 0.84, 'gl-fill', 2);
    [[0.5, 3], [0.8, 1.6], [0.65, 1.6], [0.5, 3], [0.75, 1.6]].forEach(([k, t], i) => R(g, x0 + 5, -h * 0.42 + 6 + i * 6.5, (pw - 10) * k, t, i === 3 && o.accent ? 'gl-accent' : t > 2 ? 'gl-solid' : 'gl-bar'));
  };

  // ---------------------------------------------------------------- strip glyphs (wide)
  const S = {};

  // Continuous batching: lanes of requests; one finishes early and a new one joins.
  S.queue = (g, w, h, o) => {
    const lanes = [[0, 0.82], [0, 0.34, 0.4, 0.94], [0, 0.6, 0.66, 0.9], [0, 0.48, 0.54, 0.86]];
    const lh = 5.5, gap = 4, y0 = -(lanes.length * (lh + gap) - gap) / 2, x0 = -w / 2;
    lanes.forEach((cuts, li) => {
      const y = y0 + li * (lh + gap);
      for (let i = 0; i < cuts.length; i += 2) {
        const a = cuts[i], b = cuts[i + 1] ?? 1;
        const joined = i > 0;
        R(g, x0 + a * w, y, (b - a) * w - 2, lh, joined ? (li === 1 ? 'gl-accent' : 'gl-fill2') : 'gl-solid', 1.5);
      }
    });
    for (let i = 0; i <= 10; i++) P(g, `M${r2(x0 + (w * i) / 10)},${r2(-y0 + 4)}v${i % 5 === 0 ? 4 : 2}`, 'gl-hair');
    P(g, `M${r2(x0)},${r2(-y0 + 4)}H${r2(-x0)}`, 'gl-hair');
  };

  // Attention tiling: the full score matrix is too big for on-chip memory, so it streams
  // through tile by tile. Lower triangle = causal scores; one tile in flight, in accent.
  S.sram = (g, w, h, o) => {
    const rows = 8, cols = 16, c = Math.min((h - 4) / rows, (w * 0.55) / cols), my = -rows * c / 2;
    const total = cols * c + 36 + Math.min(h - 6, 40), mx = -total / 2;
    for (let r = 0; r < rows; r++) for (let k = 0; k < cols; k++) {
      const causal = k <= r * 2 + 1;
      R(g, mx + k * c, my + r * c, c - 0.8, c - 0.8, causal ? 'gl-fill2' : 'gl-cell-empty', 0.6);
    }
    const tx = mx + 6 * c, ty = my + 4 * c;
    R(g, tx, ty, 2 * c - 0.8, 2 * c - 0.8, 'gl-accent', 0.6);
    R(g, tx - 2, ty - 2, 2 * c + 3.2, 2 * c + 3.2, 'gl-accent-line', 1);
    const ax = mx + cols * c + 10;
    for (let i = 0; i < 3; i++) P(g, `M${r2(ax + i * 5)},-4l4,4l-4,4`, 'gl-accent-line');
    const s = Math.min(h - 6, 40), sx = ax + 26;
    for (let i = 1; i < 5; i++) {
      const k = -s / 2 + (s / 5) * i;
      P(g, `M${r2(sx + s / 2 + k)},${r2(-s / 2 - 4)}V${r2(-s / 2)}M${r2(sx + s / 2 + k)},${r2(s / 2)}V${r2(s / 2 + 4)}`, 'gl-line');
    }
    R(g, sx, -s / 2, s, s, 'gl-fill', 2);
    R(g, sx + s / 2 - c, -c, 2 * c - 0.8, 2 * c - 0.8, 'gl-accent', 0.6);
    R(g, sx + 4, -s / 2 + 4, s - 8, s - 8, 'gl-hatch', 1).setAttribute('fill', hatch(o));
  };

  // Paged KV cache: logical sequences mapped onto non-contiguous physical blocks.
  S.paged = (g, w, h, o) => {
    const n = 22, bw = (w - (n - 1) * 2) / n, bh = 10, by = h / 2 - bh - 1, x0 = -w / 2;
    const owner = [0, 1, 0, 2, -1, 1, 1, 0, 2, -1, 0, 2, 1, -1, 0, 2, 2, -1, 1, 0, -1, 2];
    const cls = ['gl-solid', 'gl-fill', 'gl-accent'];
    owner.forEach((s, i) => {
      const x = x0 + i * (bw + 2);
      R(g, x, by, bw, bh, s < 0 ? 'gl-cell-empty' : cls[s], 1);
      if (s === 1) R(g, x, by, bw, bh, 'gl-hatch', 1).setAttribute('fill', hatch(o));
    });
    const ly = -h / 2 + 2;
    [0, 1, 2].forEach((s) => {
      const lx = x0 + s * (w / 3) + 6, lw = w / 3 - 24;
      R(g, lx, ly, lw, 5, cls[s], 1.5);
      if (s === 1) R(g, lx, ly, lw, 5, 'gl-hatch', 1.5).setAttribute('fill', hatch(o));
      const mine = owner.map((v, i) => [v, i]).filter(([v]) => v === s).map(([, i]) => i).slice(0, 4);
      mine.forEach((i, k) => {
        const tx = x0 + i * (bw + 2) + bw / 2, sx = lx + (lw * (k + 0.5)) / mine.length;
        P(g, `M${r2(sx)},${r2(ly + 5)}C${r2(sx)},${r2(ly + 12)} ${r2(tx)},${r2(by - 7)} ${r2(tx)},${r2(by)}`, s === 2 ? 'gl-accent-hair' : 'gl-hair');
      });
    });
  };

  // Quantization: one weight drawn at 16, 8, and 4 bits.
  S.quant = (g, w, h, o) => {
    const bits = [16, 8, 4], cw = Math.min(8, (w * 0.42) / 16), ch = 7, gap = 1.4;
    w = 22 + 16 * (cw + gap) + 4; // centre the drawing in its strip
    const rowGap = (h - 3 * ch) / 2;
    bits.forEach((b, i) => {
      const y = -h / 2 + i * (ch + rowGap);
      const x0 = -w / 2 + 22;
      const t = el('text', { x: r2(-w / 2), y: r2(y + ch - 0.5), class: 'gl-digit' }, g);
      t.textContent = String(b);
      for (let k = 0; k < b; k++) R(g, x0 + k * (cw + gap), y, cw, ch, i === 0 ? 'gl-solid' : i === 1 ? (o.accent ? 'gl-accent' : 'gl-solid') : 'gl-fill', 1);
      if (i === 2) for (let k = 0; k < b; k++) R(g, x0 + k * (cw + gap), y, cw, ch, 'gl-hatch', 1).setAttribute('fill', hatch(o));
    });
    // Memory saved: a bracket of freed width beside the 4-bit row.
    const x16 = -w / 2 + 22 + 16 * (cw + gap), x4 = -w / 2 + 22 + 4 * (cw + gap), yb = h / 2 - ch / 2;
    P(g, `M${r2(x4 + 4)},${r2(yb)}H${r2(x16 - gap)}`, 'gl-dim');
    P(g, `M${r2(x4 + 4)},${r2(yb - 3)}v6M${r2(x16 - gap)},${r2(yb - 3)}v6`, 'gl-dim');
  };

  // GPU: package with pins, a hatched die, and four memory stacks.
  S.gpu = (g, w, h, o) => {
    const s = Math.min(h - 8, 40);
    const cx = -w / 2 + s / 2 + 8;
    const sub = el('g', { transform: `translate(${r2(cx)},0)` }, g);
    G.chip(sub, s / 0.6, s / 0.6, o);
    const x0 = cx + s / 2 + 16;
    for (let i = 0; i < 4; i++) {
      const x = x0 + i * 22;
      for (let k = 0; k < 4; k++) R(g, x, -12 + k * 6.5, 16, 5, k === 0 && i === 0 && o.accent ? 'gl-accent' : 'gl-fill', 1);
    }
    // Interconnect: a bus of hairlines to a second package.
    const bx = x0 + 4 * 22 + 10, ex = w / 2 - s / 2 - 8;
    if (ex - bx > 40) {
      for (let k = -2; k <= 2; k++) P(g, `M${r2(bx)},${r2(k * 3)}H${r2(ex - s / 2 - 4)}`, k === 0 ? 'gl-accent-hair' : 'gl-hair');
      const sub2 = el('g', { transform: `translate(${r2(ex)},0)` }, g);
      G.chip(sub2, s / 0.6, s / 0.6, {});
    }
  };

  // Sliding context window: turns in a row; the oldest fall away left, the newest joins right.
  S.sliding = (g, w, h, o) => {
    const n = 16, tw = (w - 60) / n - 3, th = 12, y = -th / 2, x0 = -w / 2 + 30;
    const win = [5, 14];
    for (let i = 0; i < n; i++) {
      const x = x0 + i * (tw + 3), out = i < win[0], fresh = i === n - 1;
      const dy = out ? (win[0] - i) * 2.2 : 0;
      R(g, x, y + dy, tw, th, fresh ? 'gl-accent' : out ? 'gl-cell-empty' : i % 3 === 0 ? 'gl-solid' : 'gl-fill', 1);
      if (out) R(g, x, y + dy, tw, th, 'gl-hatch', 1).setAttribute('fill', hatch(o));
    }
    const bx0 = x0 + win[0] * (tw + 3) - 4, bx1 = x0 + (n) * (tw + 3) + 1;
    P(g, `M${r2(bx0 + 5)},${r2(y - 7)}H${r2(bx0)}V${r2(y + th + 7)}H${r2(bx0 + 5)}M${r2(bx1 - 5)},${r2(y - 7)}H${r2(bx1)}V${r2(y + th + 7)}H${r2(bx1 - 5)}`, 'gl-ink gl-thick');
    for (const k of [0, 6, 12]) P(g, `M${r2(bx0 - 8 - k)},${r2(y + th / 2)}l-3,-2.5M${r2(bx0 - 8 - k)},${r2(y + th / 2)}l-3,2.5`, 'gl-line');
  };

  // Per-turn budget: each turn replays the system prompt and all history, then adds a message and an answer.
  S.budget = (g, w, h, o) => {
    const turns = 6, sys = 3, msg = 1, out = 2, unit = (w - 20) / (sys + turns * (msg + out)), bh = Math.min(9, (h - (turns - 1) * 3) / turns);
    const x0 = -w / 2 + 10, y0 = -(turns * (bh + 3) - 3) / 2;
    for (let t = 0; t < turns; t++) {
      const y = y0 + t * (bh + 3);
      let x = x0;
      const seg = (n, cls, hatchIt) => { const ww = n * unit - 0.8; R(g, x, y, ww, bh, cls, 1); if (hatchIt) R(g, x, y, ww, bh, 'gl-hatch', 1).setAttribute('fill', hatch(o)); x += n * unit; };
      seg(sys, 'gl-solid');
      if (t) seg(t * (msg + out), 'gl-fill', true);
      seg(msg, 'gl-fill');
      seg(out, 'gl-accent');
    }
  };

  window.npGlyphs = { tile: G, strip: S, badge, BADGES };
})();
