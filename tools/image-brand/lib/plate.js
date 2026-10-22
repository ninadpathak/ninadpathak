/* Runs inside headless Chromium after pele.global.js, glyphs.js and the brand fonts load.
 * Pele lays the diagram out; this file turns its nodes into drawn glyphs, re-routes edges
 * orthogonally (or onto a ring), adds the visual motifs, and composes the plate.
 * Coordinates are display pixels at the 720 px article width.
 *
 * Motif numbers (M1 … M14) match GUIDELINE.md §7.
 */
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const NODE_CLASSES = ['accent', 'focal', 'outcome', 'muted', 'fail', 'pass', 'external', 'stack'];
  const COL = 80;

  // ---------------------------------------------------------------- helpers
  const el = (name, attrs = {}, parent) => {
    const node = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) node.setAttribute(k, String(v));
    if (parent) parent.appendChild(node);
    return node;
  };
  const r2 = (n) => Math.round(n * 100) / 100;
  const text = (parent, cls, x, y, content, anchor) => {
    const t = el('text', { class: cls, x: r2(x), y: r2(y), 'text-anchor': anchor }, parent);
    t.textContent = content;
    return t;
  };
  const central = (t) => { t.setAttribute('dominant-baseline', 'central'); return t; };
  // Text width comes from canvas metrics and is pinned on the element with textLength, so
  // every box measured around text is the same on macOS and Linux (SVG text layout is not).
  const mctx = document.createElement('canvas').getContext('2d');
  const canvasWidth = (node) => {
    let w = 0;
    for (const c of node.childNodes) {
      if (c.nodeType === 1) { w += canvasWidth(c); continue; }
      if (c.nodeType !== 3 || !c.data) continue;
      const cs = getComputedStyle(node);
      mctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      mctx.letterSpacing = cs.letterSpacing === 'normal' ? '0px' : cs.letterSpacing;
      w += mctx.measureText(c.data.replace(/\s+/g, ' ')).width;
    }
    return w;
  };
  const pin = (t) => {
    const w = r2(canvasWidth(t));
    if (w > 0) { t.setAttribute('textLength', w); t.setAttribute('lengthAdjust', 'spacing'); }
    return w;
  };
  const pinAll = (root) => {
    for (const t of root.querySelectorAll('text')) {
      const lines = t.querySelectorAll(':scope > tspan[x]');
      if (lines.length) lines.forEach(pin); else pin(t);
    }
  };
  window.npPinText = pinAll;
  // A text line's box with its horizontal extent taken from the pinned width: getBBox reports
  // glyph ink on Linux and advances on macOS.
  // Vertical extent comes from the font's ascent and descent for the same reason.
  const lineBox = (t) => {
    const w = Number(t.getAttribute('textLength')) || canvasWidth(t);
    const attr = (k) => Number(t.getAttribute(k) ?? t.closest('text').getAttribute(k)) || 0;
    const cs = getComputedStyle(t);
    mctx.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const m = mctx.measureText('H');
    const asc = m.fontBoundingBoxAscent, desc = m.fontBoundingBoxDescent;
    const base = attr('y') + (cs.dominantBaseline === 'central' ? (asc - desc) / 2 : 0);
    const x = attr('x');
    return { x: cs.textAnchor === 'middle' ? x - w / 2 : cs.textAnchor === 'end' ? x - w : x, y: base - asc, width: w, height: asc + desc };
  };
  // getBBox of a subtree with every text line counted by lineBox.
  const stableBBox = (root) => {
    const temps = [], hidden = [];
    for (const t of root.querySelectorAll('text')) {
      const lines = t.querySelectorAll(':scope > tspan[x]');
      for (const line of lines.length ? lines : [t]) {
        const b = lineBox(line);
        if (!b.width) continue;
        const r = el('rect', { x: b.x, y: b.y, width: b.width, height: b.height, fill: 'none' }, t.parentNode);
        if (t.getAttribute('transform')) r.setAttribute('transform', t.getAttribute('transform'));
        temps.push(r);
      }
      hidden.push([t, t.getAttribute('display')]);
      t.setAttribute('display', 'none');
    }
    const bb = root.getBBox();
    temps.forEach((r) => r.remove());
    for (const [t, d] of hidden) if (d === null) t.removeAttribute('display'); else t.setAttribute('display', d);
    return bb;
  };
  const width = pin;
  const parsePoints = (d) => [...d.matchAll(/(-?\d*\.?\d+),(-?\d*\.?\d+)/g)].map((m) => [Number(m[1]), Number(m[2])]);
  const fail = (src, msg) => { throw new Error(`${src.id}: ${msg}`); };
  const translateOf = (g) => {
    const m = (g.getAttribute('transform') || '').match(/translate\(([-\d.]+),([-\d.]+)\)/);
    return m ? [Number(m[1]), Number(m[2])] : [0, 0];
  };

  function makeMeasurer(T) {
    const ctx = document.createElement('canvas').getContext('2d');
    const role = T.type.roles;
    return {
      width(t, size, style) {
        const g = t.match(/^⟦g:([\d.]+)⟧/);
        if (g) return Number(g[1]);
        let r = { ...role['node-label'], size };
        if (style & 1) r = { ...role['node-strong'], size };
        if (style & 4) r = { family: 'mono', weight: 400, size, tracking: '0' };
        ctx.font = `${r.weight} ${r.size}px '${r.family === 'mono' ? T.type.mono : T.type.sans}'`;
        ctx.letterSpacing = '0px';
        return ctx.measureText(t).width;
      },
    };
  }

  // ---------------------------------------------------------------- geometry
  function boxes(svg) {
    const map = new Map();
    for (const g of svg.querySelectorAll('.pele-node, .pele-cluster')) {
      const id = g.getAttribute('data-id');
      if (!id) continue;
      const shape = g.querySelector(':scope > .np-hit') || g.querySelector(':scope > .np-shape') || g.querySelector('rect, polygon, path, circle, ellipse');
      if (!shape) continue;
      const b = shape.getBBox();
      const [tx, ty] = translateOf(g);
      const x = b.x + tx, y = b.y + ty;
      const ay = g.dataset.tilecy !== undefined ? ty + Number(g.dataset.tilecy) : y + b.height / 2;
      map.set(id, { id, g, x, y, w: b.width, h: b.height, l: x, r: x + b.width, t: y, b: y + b.height, cx: x + b.width / 2, cy: y + b.height / 2, ay, cluster: g.classList.contains('pele-cluster') });
    }
    return map;
  }

  function roundedPath(points, radius) {
    let pts = points.filter((p, i) => i === 0 || Math.hypot(p[0] - points[i - 1][0], p[1] - points[i - 1][1]) > 0.01);
    pts = pts.filter((p, i, a) => {
      if (i === 0 || i === a.length - 1) return true;
      const [x0, y0] = a[i - 1], [x2, y2] = a[i + 1];
      return Math.abs((p[0] - x0) * (y2 - y0) - (p[1] - y0) * (x2 - x0)) > 0.01;
    });
    let d = `M${r2(pts[0][0])},${r2(pts[0][1])}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [px, py] = pts[i - 1], [x, y] = pts[i], [nx, ny] = pts[i + 1];
      const l1 = Math.hypot(x - px, y - py), l2 = Math.hypot(nx - x, ny - y);
      const rr = Math.min(radius, l1 / 2, l2 / 2);
      d += `L${r2(x - ((x - px) / l1) * rr)},${r2(y - ((y - py) / l1) * rr)}Q${r2(x)},${r2(y)} ${r2(x + ((nx - x) / l2) * rr)},${r2(y + ((ny - y) / l2) * rr)}`;
    }
    const last = pts[pts.length - 1];
    return { d: `${d}L${r2(last[0])},${r2(last[1])}`, pts };
  }
  const segments = (pts) => pts.slice(1).map((p, i) => ({ a: pts[i], b: p, len: Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]) }));
  const at = (s, f) => [s.a[0] + (s.b[0] - s.a[0]) * f, s.a[1] + (s.b[1] - s.a[1]) * f];
  const chevron = (tip, from, L = 8, Wd = 3.4) => {
    const dx = tip[0] - from[0], dy = tip[1] - from[1], len = Math.hypot(dx, dy) || 1;
    const ux = dx / len, uy = dy / len;
    const bx = tip[0] - ux * L, by = tip[1] - uy * L;
    return `M${r2(bx - uy * Wd)},${r2(by + ux * Wd)}L${r2(tip[0])},${r2(tip[1])}L${r2(bx + uy * Wd)},${r2(by - ux * Wd)}`;
  };

  // M5 · Orthogonal router: side-centre ports, shared buses for siblings, 4 px corners.
  function routeEdges(svg, nodes) {
    const ids = [...nodes.keys()].filter((k) => !nodes.get(k).cluster).sort((a, b) => b.length - a.length);
    const edges = [];
    for (const g of svg.querySelectorAll('.pele-edge')) {
      const id = g.getAttribute('data-id') || '';
      let from = null, to = null;
      for (const a of ids) {
        if (!id.startsWith(`L_${a}_`)) continue;
        const rest = id.slice(a.length + 3);
        const b = ids.find((c) => rest.startsWith(`${c}_`) && /^\d+$/.test(rest.slice(c.length + 1)));
        if (b) { from = a; to = b; break; }
      }
      const paths = [...g.querySelectorAll('path')];
      const markers = paths.filter((m) => m.classList.contains('pele-marker'));
      edges.push({ g, id, from, to, line: paths.find((p) => !p.classList.contains('pele-marker')), markers });
    }
    // Diagonal neighbours follow the flowchart's main direction when both gaps are real,
    // so a top-to-bottom chart keeps its edges on the vertical buses.
    const vertical = !/^(LR|RL)$/.test(svg.dataset.direction || 'TB');
    const relation = (s, t) => {
      const gaps = { down: t.t - s.b, up: s.t - t.b, right: t.l - s.r, left: s.l - t.r };
      const open = Object.entries(gaps).filter(([, v]) => v >= 6);
      const v = open.filter(([k]) => k === 'down' || k === 'up'), h = open.filter(([k]) => k === 'right' || k === 'left');
      if (v.length && h.length && v[0][1] >= 20 && h[0][1] >= 20) return (vertical ? v : h)[0][0];
      const best = open.sort((a, b) => b[1] - a[1])[0];
      return best ? best[0] : null;
    };
    const all = [...nodes.values()];
    for (const e of edges) {
      e.nodes = all;
      e.s = nodes.get(e.from); e.t = nodes.get(e.to);
      e.rel = e.s && e.t ? relation(e.s, e.t) : null;
      const lp = parsePoints(e.line.getAttribute('d'));
      const near = (m, p) => { const tip = parsePoints(m.getAttribute('d'))[0]; return Math.hypot(tip[0] - p[0], tip[1] - p[1]); };
      e.both = e.markers.length >= 2;
      // Pele may draw a back edge from target to source; the head still belongs at the target.
      e.reverse = !e.rel && e.markers.length === 1 && near(e.markers[0], lp[0]) < near(e.markers[0], lp[lp.length - 1]);
      e.headless = e.markers.length === 0;
    }
    routeAll(edges);
    return edges;
  }

  function routeAll(edges) {
    const groups = new Map();
    for (const e of edges) if (e.rel) groups.set(`${e.from}:${e.rel}`, [...(groups.get(`${e.from}:${e.rel}`) || []), e]);
    for (const e of edges) {
      if (!e.rel) { e.pts = parsePoints(e.line.getAttribute('d')); e.routed = false; continue; }
      const { s, t } = e;
      const sign = e.rel === 'down' || e.rel === 'right' ? 1 : -1;
      const group = groups.get(`${e.from}:${e.rel}`);
      e.bus = group.length > 1 && e.startX === undefined;
      let pts;
      if (e.rel === 'down' || e.rel === 'up') {
        const sy = sign > 0 ? s.b : s.t, ey = sign > 0 ? t.t : t.b;
        const lo = Math.max(s.l, t.l) + 14, hi = Math.min(s.r, t.r) - 14;
        const sx = e.startX ?? s.cx;
        if (e.bus) {
          const gap = Math.min(...group.map((g) => (sign > 0 ? g.t.t - s.b : s.t - g.t.b)));
          const my = sy + (sign * gap) / 2;
          pts = [[sx, sy], [sx, my], [t.cx, my], [t.cx, ey]];
        } else if (Math.abs(sx - t.cx) < 1 || (e.startX === undefined && lo <= hi)) {
          const x = Math.abs(sx - t.cx) < 1 ? sx : sx >= lo && sx <= hi ? sx : t.cx >= lo && t.cx <= hi ? t.cx : (lo + hi) / 2;
          pts = [[x, sy], [x, ey]];
        } else {
          const my = (sy + ey) / 2;
          pts = [[sx, sy], [sx, my], [t.cx, my], [t.cx, ey]];
        }
      } else {
        const sx = sign > 0 ? s.r : s.l, ex = sign > 0 ? t.l : t.r;
        const lo = Math.max(s.t, t.t) + 10, hi = Math.min(s.b, t.b) - 10;
        if (e.bus) {
          const gap = Math.min(...group.map((g) => (sign > 0 ? g.t.l - s.r : s.l - g.t.r)));
          const mx = sx + sign * gap * 0.4;
          pts = [[sx, s.ay], [mx, s.ay], [mx, t.ay], [ex, t.ay]];
        } else if (Math.abs(s.ay - t.ay) < 1 || lo <= hi) {
          const y = Math.abs(s.ay - t.ay) < 1 ? s.ay : s.ay >= lo && s.ay <= hi ? s.ay : t.ay >= lo && t.ay <= hi ? t.ay : (lo + hi) / 2;
          pts = [[sx, y], [ex, y]];
        } else {
          const mx = (sx + ex) / 2;
          pts = [[sx, s.ay], [mx, s.ay], [mx, t.ay], [ex, t.ay]];
        }
      }
      // Detour: any vertical leg that would cross another node steps right of the obstacle.
      if ((e.rel === 'down' || e.rel === 'up') && e.nodes) {
        const hits = (x, y1, y2) => e.nodes.filter((n) => !n.cluster && n !== s && n !== t && x > n.l - 4 && x < n.r + 4 && Math.max(y1, y2) > n.t && Math.min(y1, y2) < n.b);
        for (let i = pts.length - 2; i >= 0; i--) {
          const [a0, a1] = [pts[i], pts[i + 1]];
          if (Math.abs(a0[0] - a1[0]) > 0.5) continue;
          const blockers = hits(a0[0], a0[1], a1[1]);
          if (!blockers.length) continue;
          const xr = Math.max(...blockers.map((n) => n.r)) + 14;
          const yTop = Math.min(...blockers.map((n) => n.t)) - 10, yBot = Math.max(...blockers.map((n) => n.b)) + 10;
          const [yIn, yOut] = sign > 0 ? [Math.max(a0[1], yTop), Math.min(a1[1], yBot)] : [Math.min(a0[1], yBot), Math.max(a1[1], yTop)];
          pts.splice(i + 1, 0, [a0[0], yIn], [xr, yIn], [xr, yOut], [a0[0], yOut]);
        }
      }
      e.pts = pts;
      e.routed = true;
    }
  }

  // M6 · Ports, handles, chevrons. M7 · flow particles on the hot path.
  function drawEdges(svg, edges, T) {
    const ports = el('g', { class: 'np-ports' }, svg);
    const seen = new Set();
    for (const e of edges) {
      for (const m of e.markers) m.remove();
      const pts = e.pts.map((p) => [...p]);
      const headAtEnd = !e.headless && (e.both || !e.reverse);
      const headAtStart = e.both || e.reverse;
      const pull = (i, j) => {
        const dx = pts[i][0] - pts[j][0], dy = pts[i][1] - pts[j][1], len = Math.hypot(dx, dy) || 1;
        pts[i] = [pts[i][0] - (dx / len) * 3, pts[i][1] - (dy / len) * 3];
      };
      if (e.routed && headAtEnd) pull(pts.length - 1, pts.length - 2);
      if (e.routed && headAtStart) pull(0, 1);
      const { d, pts: clean } = roundedPath(pts, T.radius.node);
      e.line.setAttribute('d', d);
      e.drawn = clean;
      const heads = [];
      if (headAtEnd) heads.push([clean[clean.length - 1], clean[clean.length - 2], e.routed ? e.pts[e.pts.length - 1] : null]);
      if (headAtStart) heads.push([clean[0], clean[1], e.routed ? e.pts[0] : null]);
      for (const [tip, from, border] of heads) {
        el('path', { class: 'pele-marker np-arrow', d: chevron(tip, from) }, e.g);
        if (border) {
          const key = `h${r2(border[0])},${r2(border[1])}`;
          if (!seen.has(key)) { seen.add(key); el('rect', { class: `np-handle${e.hot ? ' np-handle-hot' : ''}`, x: r2(border[0] - 2.5), y: r2(border[1] - 2.5), width: 5, height: 5 }, ports); }
        }
      }
      if (e.headless && e.routed) {
        const end = e.pts[e.pts.length - 1];
        const key = `h${r2(end[0])},${r2(end[1])}`;
        if (!seen.has(key)) { seen.add(key); el('rect', { class: 'np-handle', x: r2(end[0] - 2.5), y: r2(end[1] - 2.5), width: 5, height: 5 }, ports); }
      }
      if (!e.both) {
        const p = e.reverse ? clean[clean.length - 1] : clean[0];
        const key = `p${r2(p[0])},${r2(p[1])}`;
        if (!seen.has(key)) { seen.add(key); el('circle', { class: `np-port${e.hot ? ' np-port-hot' : ''}`, cx: r2(p[0]), cy: r2(p[1]), r: 2.5 }, ports); }
      }
      if (e.hot) particles(e.g, clean);
    }
  }

  // Three particles of shrinking size trailing toward the arrow on the longest segment.
  function particles(parent, pts) {
    const s = [...segments(pts)].sort((a, b) => b.len - a.len)[0];
    if (!s || s.len < 40) return;
    const ux = (s.b[0] - s.a[0]) / s.len, uy = (s.b[1] - s.a[1]) / s.len;
    const mid = at(s, 0.62);
    [[0, 2.4], [-7, 1.8], [-13, 1.2]].forEach(([off, r]) => el('circle', { class: 'np-particle', cx: r2(mid[0] + ux * off), cy: r2(mid[1] + uy * off), r }, parent));
  }

  // M8 · Edge marks: yes/no become a check or cross in a ring; anything else is 1–3 words.
  function edgeMarks(svg, edges) {
    const layer = el('g', { class: 'np-edge-labels' }, svg);
    for (const label of [...svg.querySelectorAll('.pele-edge-label')]) {
      const id = label.getAttribute('data-id') || '';
      const e = edges.find((x) => x.id === id);
      const old = label.querySelector('rect');
      const name = label.querySelector('text').textContent.trim();
      let p;
      if (e?.routed) {
        const segs = segments(e.drawn);
        const last = segs[segs.length - 1];
        p = at(last.len >= 30 ? last : [...segs].sort((a, b) => b.len - a.len)[0], 0.5);
      } else {
        p = [Number(old.getAttribute('x')) + Number(old.getAttribute('width')) / 2, Number(old.getAttribute('y')) + Number(old.getAttribute('height')) / 2];
      }
      label.remove();
      const g = el('g', { class: `np-edge-label${e?.hot ? ' np-hot' : ''}` }, layer);
      const mark = { yes: 'check', no: 'cross' }[name.toLowerCase()];
      if (mark) { window.npGlyphs.badge(g, p[0], p[1], mark, !!e?.hot, 7.5); continue; }
      const mask = el('rect', { class: 'np-label-mask', rx: 2 }, g);
      const t = central(text(g, 'np-edge-text', p[0], p[1], name.toUpperCase(), 'middle'));
      const w = width(t);
      for (const [k, v] of Object.entries({ x: p[0] - w / 2 - 6, y: p[1] - 8, width: w + 12, height: 16 })) mask.setAttribute(k, r2(v));
    }
  }

  // M9 · Step markers: numbered squares, in @path order or pinned with @step.
  function stepSquare(parent, x, y, n) {
    el('rect', { class: 'np-step', x: r2(x - 7), y: r2(y - 7), width: 14, height: 14, rx: 2 }, parent);
    central(text(parent, 'np-step-num', x, y + 0.5, String(n), 'middle'));
  }
  function stepMarkers(svg, edges, src) {
    const layer = el('g', { class: 'np-steps' }, svg);
    src.meta.hotEdges.map(([a, b]) => edges.find((x) => x.from === a && x.to === b)).filter((e) => e?.drawn).forEach((e, i) => {
      const segs = segments(e.drawn);
      if (Math.max(...segs.map((x) => x.len)) < 36) return;
      const first = segs[0];
      const p = first.len >= 30 ? at(first, Math.min(0.5, 16 / first.len)) : at([...segs].sort((a, b) => b.len - a.len)[0], 0.3);
      stepSquare(layer, p[0], p[1], i + 1);
    });
  }

  // ---------------------------------------------------------------- glyph nodes (M1–M3)
  function glyphNode(node, spec, T, defsId) {
    const shape = node.querySelector(':scope > .np-shape');
    const label = node.querySelector('.pele-label');
    const lines = label ? (label.querySelectorAll('tspan[x]').length ? [...label.querySelectorAll('tspan[x]')] : [label]) : [];
    for (const l of lines.filter((l) => l.textContent.startsWith('⟦'))) l.remove();
    const words = lines.filter((l) => l.isConnected && l.textContent.trim());
    const x = Number(shape.getAttribute('x')), y = Number(shape.getAttribute('y')), w = Number(shape.getAttribute('width')), h = Number(shape.getAttribute('height'));
    const opts = { ...spec.opts, hatch: `${defsId}-hatch`, accent: spec.opts.accent || node.classList.contains('focal') || node.classList.contains('accent') };
    if (spec.mode === 'strip' && spec.opts.stacked) {
      // M3 narrow: the label on top, the strip glyph under it across the slab.
      node.classList.add('np-slab');
      if (label) label.setAttribute('text-anchor', 'start');
      words.forEach((l, i) => { l.setAttribute('x', r2(x + 14)); l.setAttribute('y', r2(y + 22 + i * 17)); });
      const top = y + 22 + words.length * 17;
      const g = el('g', { class: 'np-glyph', transform: `translate(${r2(x + w / 2)},${r2(top + (y + h - top) / 2)})` }, node);
      window.npGlyphs.strip[spec.name](g, w - 28, Math.min(spec.h, y + h - top - 8), opts);
      return;
    }
    if (spec.mode === 'strip') {
      // M3 · Layer slab: label column on the left, the strip glyph across the rest.
      node.classList.add('np-slab');
      if (label) label.setAttribute('text-anchor', 'start');
      words.forEach((l, i) => { l.setAttribute('x', r2(x + 26)); l.setAttribute('y', r2(y + h / 2 + 5 + (i - (words.length - 1) / 2) * 17)); });
      const gx = x + 150 + (w - 150 - 18) / 2;
      const g = el('g', { class: 'np-glyph', transform: `translate(${r2(gx)},${r2(y + h / 2)})` }, node);
      window.npGlyphs.strip[spec.name](g, w - 150 - 18, Math.min(spec.h, h - 14), opts);
      return;
    }
    // M1 · Tile: the glyph on a surface tile. M2 · Bare: the glyph alone. Label underneath.
    shape.classList.add('np-hit');
    shape.classList.remove('np-shape');
    const labelH = words.length * 19;
    const tileH = h - labelH - (words.length ? 6 : 0);
    const tw = Math.min(w, spec.w + 18);
    if (spec.mode === 'tile') {
      const tile = el('rect', { class: 'np-tile', x: r2(-tw / 2), y: r2(y), width: r2(tw), height: r2(tileH), rx: T.radius.node });
      node.insertBefore(tile, node.firstChild);
      if (node.classList.contains('stack')) for (const off of [6, 3]) node.insertBefore(el('rect', { class: 'np-stack-ghost', x: r2(-tw / 2 + off), y: r2(y - off), width: r2(tw), height: r2(tileH), rx: T.radius.node }), tile);
      if (node.classList.contains('external')) tile.after(el('rect', { class: 'np-hatch-fill', x: r2(-tw / 2), y: r2(y), width: r2(tw), height: r2(tileH), rx: T.radius.node, fill: `url(#${defsId}-hatch)` }));
    }
    const gy = spec.mode === 'bare' ? y + 15 : y + tileH / 2;
    const g = el('g', { class: 'np-glyph', transform: `translate(0,${r2(gy)})` }, node);
    node.dataset.tilecy = r2(spec.mode === 'bare' ? gy : y + tileH / 2);
    if (spec.mode === 'bare') shape.setAttribute('height', r2(spec.h + 4));
    const draw = window.npGlyphs.tile[spec.name];
    if (!draw) throw new Error(`unknown glyph "${spec.name}"`);
    draw(g, spec.w, Math.min(spec.h, tileH - 8), opts);
    if (label) label.setAttribute('text-anchor', 'middle');
    words.forEach((l, i) => { l.setAttribute('x', 0); l.setAttribute('y', r2(y + tileH + 17 + i * 19)); l.classList.add('np-glyph-label'); });
    // Corner badge (any tile glyph): a status or owner mark pinned to the tile's top-right.
    if (spec.opts.corner && spec.mode === 'tile') window.npGlyphs.badge(node, tw / 2 - 3, y + 3, spec.opts.corner, node.classList.contains('fail') ? false : !!opts.accent, 8);
  }

  // ---------------------------------------------------------------- ring layout (M10)
  function ringLayout(svg, src, T, nodes) {
    const spec = src.meta.ringSpec;
    const ring = spec.ids.map((id) => nodes.get(id));
    if (ring.some((n) => !n)) fail(src, '@ring names a node that does not exist');
    const cx = ring.reduce((s, n) => s + n.cx, 0) / ring.length, cy = ring.reduce((s, n) => s + n.cy, 0) / ring.length;
    const R = spec.r || 140;
    const n = ring.length;
    const start = spec.start === undefined ? Math.PI : (spec.start * Math.PI) / 180;
    const angle = (i) => start + (2 * Math.PI * i) / n;
    const place = (box, x, y) => {
      const [tx, ty] = translateOf(box.g);
      box.g.setAttribute('transform', `translate(${r2(x + (tx - box.cx))},${r2(y + (ty - box.cy))})`);
    };
    ring.forEach((b, i) => place(b, cx + R * Math.cos(angle(i)), cy + R * Math.sin(angle(i))));
    // Neighbours of the ring sit radially outside the station they connect to.
    const ringSet = new Set(spec.ids);
    const edgeIds = [...svg.querySelectorAll('.pele-edge')].map((g) => g.getAttribute('data-id') || '');
    for (const [id, b] of nodes) {
      if (b.cluster || ringSet.has(id)) continue;
      const i = spec.ids.findIndex((r) => edgeIds.some((e) => e.startsWith(`L_${id}_${r}_`) || e.startsWith(`L_${r}_${id}_`)));
      if (i < 0) continue;
      const a = angle(i), out = R + (spec.gap ?? 96) + (Math.abs(Math.cos(a)) * b.w + Math.abs(Math.sin(a)) * b.h) / 2;
      if (spec.stack) {
        // Narrow plates: neighbours sit above or below the ring, never beside it.
        const up = Math.sin(a) < 0 || (Math.abs(Math.sin(a)) < 0.01 && Math.cos(a) < 0);
        const used = [...nodes.values()].filter((o) => o.stacked === (up ? 'up' : 'down')).length;
        b.stacked = up ? 'up' : 'down';
        place(b, cx + (used ? (used % 2 ? 1 : -1) * 70 : 0), cy + (up ? -1 : 1) * (R + (spec.gap ?? 30) + 40 + b.h / 2));
      } else place(b, cx + out * Math.cos(a), cy + out * Math.sin(a));
    }
    for (const g of [...svg.querySelectorAll('.pele-edge')]) {
      const id = g.getAttribute('data-id') || '';
      if (spec.ids.some((a) => spec.ids.some((b) => id.startsWith(`L_${a}_${b}_`)))) {
        svg.querySelector(`.pele-edge-label[data-id="${CSS.escape(id)}"]`)?.remove();
        g.remove();
      }
    }
    for (const c of [...svg.querySelectorAll('.pele-cluster')]) c.remove();

    // The track: double hairline rail with ticks, accent arcs between stations, chevrons,
    // particles, and a numbered square on each arc.
    const track = el('g', { class: 'np-ring' });
    svg.insertBefore(track, svg.querySelector('.pele-nodes'));
    el('circle', { class: 'np-ring-rail', cx: r2(cx), cy: r2(cy), r: r2(R + 9) }, track);
    el('circle', { class: 'np-ring-rail', cx: r2(cx), cy: r2(cy), r: r2(R - 9) }, track);
    let ticks = '';
    for (let k = 0; k < 120; k++) {
      const a = (2 * Math.PI * k) / 120, r1 = R + 9, rr = k % 10 === 0 ? R + 3 : R + 6;
      ticks += `M${r2(cx + r1 * Math.cos(a))},${r2(cy + r1 * Math.sin(a))}L${r2(cx + rr * Math.cos(a))},${r2(cy + rr * Math.sin(a))}`;
    }
    el('path', { class: 'np-ring-ticks', d: ticks }, track);
    const p = (a, r = R) => [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    const gap = 0.5;
    for (let i = 0; i < n; i++) {
      const a0 = angle(i) + gap, a1 = angle(i + 1) - gap;
      const [sx, sy] = p(a0), [ex, ey] = p(a1);
      el('path', { class: 'np-ring-arc', d: `M${r2(sx)},${r2(sy)}A${r2(R)},${r2(R)} 0 0 1 ${r2(ex)},${r2(ey)}` }, track);
      el('path', { class: 'np-arrow np-ring-head', d: chevron([ex, ey], p(a1 - 0.06)) }, track);
      const am = (a0 + a1) / 2;
      [[0.1, 2.4], [0.04, 1.8], [-0.01, 1.2]].forEach(([off, r]) => { const [x, y] = p(am + off); el('circle', { class: 'np-particle', cx: r2(x), cy: r2(y), r }, track); });
      const [mx, my] = p(am - 0.14);
      stepSquare(track, mx, my, i + 1);
    }
    if (src.meta.centerGlyph) {
      const cg = src.meta.centerGlyph;
      const g = el('g', { class: 'np-glyph np-ring-center', transform: `translate(${r2(cx)},${r2(cy)})` }, track);
      const hub = Math.min(R - 52, 66);
      el('circle', { class: 'np-ring-hub', cx: 0, cy: 0, r: r2(hub) }, g);
      window.npGlyphs.tile[cg.name](g, cg.w, cg.h, { ...cg.opts, hatch: `${src.id}-hatch` });
      if (cg.opts.label) text(g, 'np-glyph-label', 0, 40, String(cg.opts.label), 'middle');
    }
  }

  // ---------------------------------------------------------------- parts brackets (M11)
  // Bracket each phrase of a node's label; that part's edge starts from its bracket.
  function partsBrackets(svg, src, nodes, edges) {
    pinAll(svg);
    const spec = src.meta.partsSpec;
    const node = nodes.get(spec.target);
    if (!node) fail(src, '@parts target is not a node');
    const label = node.g.querySelector('.pele-label');
    const lines = label.querySelectorAll('tspan[x]').length ? [...label.querySelectorAll('tspan[x]')] : [label];
    const layer = el('g', { class: 'np-parts' }, node.g);
    const [tx] = translateOf(node.g);
    spec.parts.forEach((part, i) => {
      const line = lines.find((l) => l.textContent.replace(/ /g, ' ').includes(part.phrase));
      if (!line) fail(src, `@parts phrase "${part.phrase}" is not in the label`);
      const txt = line.textContent.replace(/ /g, ' ');
      const start = txt.indexOf(part.phrase);
      const x0 = line.getStartPositionOfChar(start).x, x1 = line.getEndPositionOfChar(start + part.phrase.length - 1).x;
      const by = Number(line.getAttribute('y')) + 7;
      el('path', { class: `np-part np-part-${i + 1}`, d: `M${r2(x0 + 1)},${r2(by - 2)}V${r2(by + 2)}H${r2(x1 - 1)}V${r2(by - 2)}` }, layer);
      const e = edges.find((x) => x.from === spec.target && x.to === part.node);
      if (e) e.startX = tx + (x0 + x1) / 2;
    });
  }

  // ---------------------------------------------------------------- restyle
  function brandDiagram(svg, src, T, defsId) {
    const used = new Set();
    const meta = src.meta;
    svg.classList.add('np-diagram');
    svg.dataset.direction = src.direction || 'TB';
    svg.removeAttribute('width');
    svg.removeAttribute('height');

    // M4 · Clusters: dashed boundary, wash, tick, one-word label on a mask above the edges.
    const clusterLabels = el('g', { class: 'np-cluster-labels' }, svg);
    for (const cluster of svg.querySelectorAll('.pele-cluster')) {
      const rect = cluster.querySelector('rect');
      // Pele sometimes draws a cluster's title in a separate group with a halo copy.
      const titleGroup = svg.querySelector(`.pele-cluster-title[data-id="${CSS.escape(cluster.getAttribute('data-id') || '')}"]`);
      const label = cluster.querySelector('.pele-cluster-label') || titleGroup?.querySelector('.pele-cluster-label');
      if (titleGroup) { if (label) cluster.appendChild(label); titleGroup.remove(); }
      for (const a of ['fill', 'fill-opacity', 'stroke']) rect.removeAttribute(a);
      rect.classList.add('np-shape');
      if (cluster.classList.contains('hatch')) rect.after(el('rect', { class: 'np-hatch-fill', x: rect.getAttribute('x'), y: rect.getAttribute('y'), width: rect.getAttribute('width'), height: rect.getAttribute('height'), rx: T.radius.node, fill: `url(#${defsId}-hatch)` }));
      if (cluster.classList.contains('ghost') || !label || !label.textContent.trim()) { label?.remove(); continue; }
      const x = Number(rect.getAttribute('x')), y = Number(rect.getAttribute('y'));
      const g = el('g', { class: 'np-cluster-head' }, clusterLabels);
      label.textContent = label.textContent.toUpperCase();
      label.removeAttribute('fill');
      for (const [k, v] of Object.entries({ x: x + 20, y: y + 17, 'text-anchor': 'start' })) label.setAttribute(k, v);
      el('rect', { class: 'np-cluster-mask' }, g);
      el('rect', { class: 'np-cluster-tick', x: x + 10, y: y + 10, width: 4, height: 4 }, g);
      g.appendChild(label);
    }

    for (const node of svg.querySelectorAll('.pele-node')) {
      const shapes = [...node.querySelectorAll(':scope > rect, :scope > polygon, :scope > path, :scope > circle, :scope > ellipse')];
      for (const c of NODE_CLASSES) if (node.classList.contains(c)) used.add(c);
      for (const s of shapes) { s.removeAttribute('fill'); s.removeAttribute('stroke'); s.classList.add('np-shape'); }
      const spec = meta.glyphs[node.getAttribute('data-id')];
      if (spec) { glyphNode(node, spec, T, defsId); continue; }
      const shape = shapes[0];
      if (shape && shape.tagName === 'rect' && ['accent', 'fail', 'pass'].some((c) => node.classList.contains(c))) {
        const x = Number(shape.getAttribute('x')), y = Number(shape.getAttribute('y')), w = Number(shape.getAttribute('width'));
        const rr = T.radius.node, h3 = T.stroke['accent-rule'];
        const rule = el('path', { class: 'np-rule', d: `M${x},${y + h3}V${y + rr}A${rr},${rr} 0 0 1 ${x + rr},${y}H${x + w - rr}A${rr},${rr} 0 0 1 ${x + w},${y + rr}V${y + h3}Z` });
        const lab = node.querySelector('.pele-label');
        lab ? lab.before(rule) : node.appendChild(rule);
      }
    }

    // Step squares pinned to slabs (block stacks have no edges to carry them).
    for (const [id, n] of Object.entries(meta.steps)) {
      const node = svg.querySelector(`.pele-node[data-id="${CSS.escape(id)}"]`);
      if (!node) fail(src, `@step target "${id}" is not a node`);
      const b = node.querySelector(':scope > .np-shape, :scope > .np-hit').getBBox();
      stepSquare(node, b.x, b.y + b.height / 2, n);
    }

    let nodes = boxes(svg);
    if (meta.ringSpec) { ringLayout(svg, src, T, nodes); nodes = boxes(svg); }
    let edges = [];
    if (svg.classList.contains('pele-flowchart')) {
      edges = routeEdges(svg, nodes);
      if (meta.partsSpec) { partsBrackets(svg, src, nodes, edges); routeAll(edges); }
      const hot = new Set(meta.hotEdges.map(([a, b]) => `${a}>${b}`));
      for (const e of edges) { e.hot = hot.has(`${e.from}>${e.to}`); if (e.hot) e.g.classList.add('np-hot'); }
      drawEdges(svg, edges, T);
      edgeMarks(svg, edges);
      if (meta.hotEdges.length && !meta.ringSpec) stepMarkers(svg, edges, src);
      svg.appendChild(svg.querySelector('.np-ports'));
    }
    svg.appendChild(clusterLabels);
    pinAll(clusterLabels);
    for (const head of clusterLabels.querySelectorAll('.np-cluster-head')) {
      const b = lineBox(head.querySelector('.pele-cluster-label'));
      const m = head.querySelector('.np-cluster-mask');
      for (const [k, v] of Object.entries({ x: b.x - 16, y: b.y - 3, width: b.width + 22, height: b.height + 6, rx: T.radius.label })) m.setAttribute(k, r2(v));
    }
    if (svg.classList.contains('pele-xychart')) brandChart(svg, src, T, defsId, used);
    return { used, nodes, edges };
  }

  // M12 · Tile bars: each bar is built from unit tiles; only callouts carry a value.
  function brandChart(svg, src, T, defsId, used) {
    svg.querySelector('.pele-title')?.remove();
    const labels = [...svg.querySelectorAll('.pele-axis-labels text')];
    const numeric = labels.filter((t) => /^-?\d+(\.\d+)?$/.test(t.textContent.trim()));
    const horizontal = numeric.length > 1 && numeric[0].getAttribute('y') === numeric[1].getAttribute('y');
    const pos = (t) => Number(t.getAttribute(horizontal ? 'x' : 'y'));
    const [a, b] = numeric;
    const ppu = Math.abs((pos(b) - pos(a)) / (Number(b.textContent) - Number(a.textContent)));
    for (const t of numeric) t.classList.add('np-tick');
    for (const t of labels.filter((x) => !numeric.includes(x))) t.classList.add('np-category');
    for (const g of svg.querySelectorAll('.pele-axis-labels, .pele-axis-titles')) { g.removeAttribute('fill'); g.removeAttribute('font-size'); }
    for (const t of svg.querySelectorAll('.pele-axis-titles text')) t.textContent = t.textContent.toUpperCase();
    const unit = src.meta.unit || '';
    // A percent sign follows the number; any other unit ($) leads it.
    const fmt = (v) => { const r = Math.round(v * 100) / 100; const n = Number.isInteger(r) ? r : r.toFixed(2); return unit === '%' ? `${n}%` : `${unit}${n}`; };
    // One tile per unit of the value axis, or per `@tile n` units when values run into the hundreds.
    const per = src.meta.tileUnits || 1;
    const tile = ppu * per;
    const values = el('g', { class: 'np-values' }, svg);
    const bars = [];
    // Callouts print the source's values; widths measured back from pixels carry float noise.
    const data = [...(src.mermaid || '').matchAll(/^\s*bar\s*\[([^\]]*)\]/gm)].map((m) => m[1].split(',').map(Number));
    [...svg.querySelectorAll('.pele-series')].forEach((series, si) => {
      series.removeAttribute('fill');
      series.classList.add(`np-series-${si + 1}`);
      used.add(`series-${si + 1}`);
      [...series.querySelectorAll('rect')].forEach((r, ci) => {
        const x = Number(r.getAttribute('x')), y = Number(r.getAttribute('y')), w = Number(r.getAttribute('width')), h = Number(r.getAttribute('height'));
        r.remove();
        const v = Number.isFinite(data[si]?.[ci]) ? data[si][ci] : (horizontal ? w / ppu : h / ppu);
        bars.push({ si, ci, x, y, w, h, v });
        const n = Math.ceil(v / per - 1e-6);
        for (let k = 0; k < n; k++) {
          const tw = Math.min(tile, w - k * tile) - 1.2;
          if (tw <= 0.4) continue;
          el('rect', { class: `np-bar-tile np-bar-tile-${si + 1}`, x: r2(x + k * tile), y: r2(y + 1), width: r2(tw), height: r2(h - 2), rx: 1 }, series);
          if (si === 1) el('rect', { class: 'np-hatch-fill', x: r2(x + k * tile), y: r2(y + 1), width: r2(tw), height: r2(h - 2), fill: `url(#${defsId}-hatch)` }, series);
        }
      });
    });
    for (const [si, ci] of src.meta.callouts) {
      const bar = bars.find((x) => x.si === si - 1 && x.ci === ci);
      if (!bar) fail(src, `@callout ${si}:${ci} names no bar`);
      central(text(values, 'np-value', bar.x + bar.w + 6, bar.y + bar.h / 2, fmt(bar.v)));
    }
    if (src.meta.ratioAt !== null) {
      const [s1, s2] = [0, 1].map((si) => bars.find((x) => x.si === si && x.ci === src.meta.ratioAt));
      const x1 = s1.x + s1.w, x2 = s2.x + s2.w, y = s2.y + s2.h + 8;
      el('path', { class: 'np-ratio', d: `M${r2(x1)},${r2(s1.y + s1.h / 2)}H${r2(x1 + 4)}M${r2(x1 + 2)},${r2(s1.y + s1.h / 2)}V${r2(y)}H${r2(x2)}V${r2(s2.y + s2.h + 2)}` }, values);
      const rt = central(text(values, 'np-ratio-text', (x1 + x2) / 2, y, `${Number((s2.v / s1.v).toFixed(2))}×`, 'middle'));
      values.insertBefore(el('rect', { class: 'np-label-mask', x: r2((x1 + x2) / 2 - width(rt) / 2 - 5), y: r2(y - 7), width: r2(width(rt) + 10), height: 14 }), rt);
    }
  }

  // M13 · Dimension brackets, labelled by a badge glyph (":lock") or at most three words.
  function drawDims(svg, src, nodes) {
    if (!src.meta.dims.length) return;
    const layer = el('g', { class: 'np-dims' }, svg);
    const all = [...nodes.values()];
    const right = Math.max(...all.map((n) => n.r)), bottom = Math.max(...all.map((n) => n.b));
    const slots = { v: [], h: [] };
    const slot = (kind, lo, hi) => {
      let i = 0;
      while ((slots[kind][i] || []).some(([a, b]) => lo < b + 24 && hi > a - 24)) i++;
      (slots[kind][i] = slots[kind][i] || []).push([lo, hi]);
      return i;
    };
    const tick = (x, y) => `M${r2(x - 4)},${r2(y + 4)}L${r2(x + 4)},${r2(y - 4)}`;
    const mark = (x, y, label, vertical) => {
      if (label.startsWith(':')) {
        layer.appendChild(el('rect', { class: 'np-label-mask', x: r2(x - 13), y: r2(y - 10), width: 26, height: 20 }));
        window.npGlyphs.badge(layer, x, y, label.slice(1), false, 9);
        return;
      }
      const t = central(text(layer, 'np-dim-text', x, y, label.toUpperCase(), 'middle'));
      const m = el('rect', { class: 'np-label-mask', x: r2(x - width(t) / 2 - 6), y: r2(y - 7), width: r2(width(t) + 12), height: 14 });
      layer.insertBefore(m, t);
      // A vertical span's words run along its line, reading upward, so they never cross a tile.
      if (vertical) for (const n of [t, m]) n.setAttribute('transform', `rotate(-90 ${r2(x)} ${r2(y)})`);
    };
    for (const d of src.meta.dims) {
      const a = nodes.get(d.from), b = nodes.get(d.to);
      if (!a || !b) fail(src, `@dim target "${!a ? d.from : d.to}" is not a node or cluster id`);
      const vertical = a === b || a.b <= b.t + 1 || b.b <= a.t + 1;
      if (vertical) {
        const top = a.t <= b.t ? a : b, bot = a.b >= b.b ? a : b;
        const x = right + 22 + slot('v', top.t, bot.b) * 30;
        el('path', { class: 'np-dim-ext', d: `M${r2(top.r + 4)},${r2(top.t)}H${r2(x + 6)}M${r2(bot.r + 4)},${r2(bot.b)}H${r2(x + 6)}` }, layer);
        el('path', { class: 'np-dim-line', d: `M${r2(x)},${r2(top.t)}V${r2(bot.b)}${tick(x, top.t)}${tick(x, bot.b)}` }, layer);
        mark(x, (top.t + bot.b) / 2, d.label, true);
      } else {
        const lft = a.l <= b.l ? a : b, rgt = a.r >= b.r ? a : b;
        const y = bottom + 22 + slot('h', lft.l, rgt.r) * 30;
        el('path', { class: 'np-dim-ext', d: `M${r2(lft.l)},${r2(lft.b + 4)}V${r2(y + 6)}M${r2(rgt.r)},${r2(rgt.b + 4)}V${r2(y + 6)}` }, layer);
        el('path', { class: 'np-dim-line', d: `M${r2(lft.l)},${r2(y)}H${r2(rgt.r)}${tick(lft.l, y)}${tick(rgt.r, y)}` }, layer);
        mark((lft.l + rgt.r) / 2, y, d.label);
      }
    }
  }

  // ---------------------------------------------------------------- plate parts
  function defs(plate, id, T) {
    const d = el('defs', {}, plate);
    const grid = T.canvas.article.grid;
    const dots = el('pattern', { id: `${id}-grid`, width: grid, height: grid, patternUnits: 'userSpaceOnUse' }, d);
    el('circle', { class: 'np-grid-dot', cx: grid / 2, cy: grid / 2, r: 0.75 }, dots);
    const hatch = el('pattern', { id: `${id}-hatch`, width: 5, height: 5, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, d);
    el('path', { class: 'np-hatch', d: 'M0,0V5' }, hatch);
  }

  // M14 · Drafting field: dot grid, ruled strips with 80 px cells, ruler, crop marks. No text.
  function field(parent, x, y, w, h, id, S = 12) {
    el('rect', { class: 'np-field', x, y, width: w, height: h, fill: `url(#${id}-grid)` }, parent);
    if (S) {
      el('rect', { class: 'np-strip', x, y, width: w, height: S }, parent);
      el('rect', { class: 'np-strip', x, y: y + S, width: S, height: h - S }, parent);
      let grid = `M${x},${y + S}H${x + w}M${x + S},${y}V${y + h}`;
      for (let cx = x + S + COL; cx < x + w - 1; cx += COL) grid += `M${cx},${y}v${S}`;
      for (let cy = y + S + COL; cy < y + h - 1; cy += COL) grid += `M${x},${cy}h${S}`;
      el('path', { class: 'np-sep', d: grid }, parent);
    }
    let d = '';
    const ox = x + S, oy = y + S;
    for (let i = 8; ox + i < x + w; i += 8) d += `M${ox + i},${oy}v${i % 40 === 0 ? 5 : 2.5}`;
    for (let i = 8; oy + i < y + h; i += 8) d += `M${ox},${oy + i}h${i % 40 === 0 ? 5 : 2.5}`;
    el('path', { class: 'np-ruler', d }, parent);
    const ci = 14, arm = 8;
    const corners = [[ox + ci, oy + ci, 1, 1], [x + w - ci, oy + ci, -1, 1], [ox + ci, y + h - ci, 1, -1], [x + w - ci, y + h - ci, -1, -1]];
    el('path', { class: 'np-crop', d: corners.map(([cx, cy, sx, sy]) => `M${cx},${cy + sy * arm}V${cy}H${cx + sx * arm}`).join('') }, parent);
    return { ox, oy };
  }

  // Foot band: a drafting scale bar and a registration target. No text.
  function foot(plate, y, W) {
    const g = el('g', { class: 'np-foot' }, plate);
    el('path', { class: 'np-sep', d: `M0,${y}H${W}` }, g);
    for (let i = 0; i < 8; i++) el('rect', { class: i % 2 ? 'np-scale-off' : 'np-scale-on', x: 20 + i * 14, y: y + 11, width: 14, height: 4 }, g);
    el('path', { class: 'np-scale-ticks', d: Array.from({ length: 9 }, (_, i) => `M${20 + i * 14},${y + 8}v10`).join('') }, g);
    const cx = W - 30, cy = y + 13;
    el('circle', { class: 'np-reg', cx, cy, r: 6 }, g);
    el('path', { class: 'np-reg', d: `M${cx - 10},${cy}H${cx + 10}M${cx},${cy - 10}V${cy + 10}` }, g);
    el('circle', { class: 'np-reg-dot', cx, cy, r: 1.6 }, g);
    return 26;
  }

  function kickerText(parent, x, y, content, cls) {
    const t = el('text', { class: cls, x, y, 'data-exempt': '1' }, parent);
    el('tspan', { class: 'np-slash' }, t).textContent = '// ';
    t.appendChild(document.createTextNode(content.toUpperCase()));
    return t;
  }

  // Key: chart series by default; @key names glyph encodings (solid, hatch, outline, accent).
  function seriesKey(svg, src, defsId, maxW = Infinity) {
    const g = el('g', { class: 'np-series-key' }, svg);
    const entries = src.meta.keySpec || src.meta.seriesNames.map((name, i) => [i === 0 ? 'series-1' : 'series-2', name]);
    const swatch = { 'series-1': ['np-bar-tile np-bar-tile-1', false], 'series-2': ['np-bar-tile np-bar-tile-2', true], solid: ['gl-solid', false], hatch: ['gl-fill', true], outline: ['gl-fill', false], accent: ['gl-accent', false] };
    let cx = 0, cy = 0, widest = 0;
    for (const [kind, name] of entries) {
      const item = el('g', {}, g);
      const [cls, hatchIt] = swatch[kind] || swatch.outline;
      el('rect', { class: cls, x: 0, y: -8, width: 12, height: 10, rx: 1 }, item);
      if (hatchIt) el('rect', { class: 'np-hatch-fill', x: 0, y: -8, width: 12, height: 10, fill: `url(#${defsId}-hatch)` }, item);
      const iw = 18 + width(text(item, 'np-key', 18, 0, name.toUpperCase()));
      if (cx && cx + iw > maxW) { cx = 0; cy += 18; } // wrap the key on narrow plates
      item.setAttribute('transform', `translate(${r2(cx)},${r2(cy)})`);
      cx += iw + 22;
      widest = Math.max(widest, cx - 22);
    }
    g.dataset.rows = String(cy / 18 + 1);
    return { g, w: widest };
  }

  function renderPele(host, src, T, maxWidth) {
    host.innerHTML = window.pele.render(src.mermaid, {
      measurer: makeMeasurer(T), fontFamily: T.type.sans, fontFamilyMono: T.type.mono, fontSize: 14,
      responsive: false, autoDirection: false, padding: 8, idPrefix: src.id, maxWidth, links: false, images: false,
      config: { flowchart: { nodeSpacing: src.meta.spacingSpec?.[0] ?? T.layout.nodeSpacing, rankSpacing: src.meta.spacingSpec?.[1] ?? T.layout.rankSpacing }, xyChart: { width: Math.min(maxWidth, T.layout.chartWidth), height: T.layout.chartHeight } },
    }).svg;
    return host.querySelector('svg');
  }

  function fit(svg, maxW, maxH, minScale, maxScale, src, margin = 6) {
    pinAll(svg);
    const bb = stableBBox(svg);
    const x0 = bb.x - margin, y0 = bb.y - margin, cw = bb.width + 2 * margin, ch = bb.height + 2 * margin;
    svg.setAttribute('viewBox', `${r2(x0)} ${r2(y0)} ${r2(cw)} ${r2(ch)}`);
    const s = Math.min(maxScale, maxW / cw, maxH ? maxH / ch : Infinity);
    if (s < minScale) fail(src, `diagram is ${Math.round(cw)}×${Math.round(ch)} px and would render at ${Math.round(s * 100)}%; the floor is ${Math.round(minScale * 1000) / 10}%. Split it or change direction.`);
    return { s, cw, ch };
  }

  // ---------------------------------------------------------------- article plate
  window.npComposeArticle = (src, T) => {
    const W = Number(src.meta.width || T.canvas.article.width);
    // Narrow plates (phone variants) keep a tighter field so more of the width carries the diagram.
    const narrow = W < 480;
    const C = { ...T.canvas.article, pad: narrow ? 8 : T.canvas.article.pad };
    const S = narrow ? 0 : 12; // narrow plates drop the ruled coordinate strips
    const plate = el('svg', { xmlns: NS, class: 'np-plate np-kind-article', viewBox: `0 0 ${W} 100`, width: W, height: 100, role: 'img' }, document.body);
    el('style', {}, plate).textContent = '/*NP-STYLE*/';
    el('title', { id: `${src.id}-title` }, plate).textContent = src.meta.kicker || src.id;
    el('desc', { id: `${src.id}-desc` }, plate).textContent = src.meta.alt;
    plate.setAttribute('aria-labelledby', `${src.id}-title ${src.id}-desc`);
    defs(plate, src.id, T);
    const bg = el('rect', { class: 'np-canvas', x: 0, y: 0, width: W, height: 100 }, plate);
    const fieldLayer = el('g', { class: 'np-texture' }, plate);
    const host = el('g', {}, plate);
    const inner = W - S - 2 * C.pad;
    const svg = renderPele(host, src, T, inner);
    const facts = brandDiagram(svg, src, T, src.id);
    drawDims(svg, src, facts.nodes);
    if (src.meta.seriesNames.length || src.meta.keySpec) {
      const bb = stableBBox(svg);
      const { g, w } = seriesKey(svg, src, src.id, Math.min(inner - 12, bb.width));
      const rows = Number(g.dataset.rows);
      g.setAttribute('transform', `translate(${r2(bb.x + Math.max(0, bb.width - w))},${r2(bb.y - 18 * rows)})`);
    }
    const { s, cw, ch } = fit(svg, inner, 0, C.minScale, 1, src, narrow ? 1 : 6);
    const dw = cw * s, dh = ch * s;
    // Head band: the title wraps onto a second line (and the band grows) when it doesn't fit.
    const title = (src.meta.kicker || src.id).toUpperCase();
    const kick = kickerText(plate, 20, 27, title, 'np-head-kicker');
    let headH = C.head;
    if (20 + width(kick) > W - 20) {
      const words = title.split(' ');
      let best = 1, bestDiff = Infinity;
      for (let i = 1; i < words.length; i++) { const d = Math.abs(words.slice(0, i).join(' ').length - words.slice(i).join(' ').length); if (d < bestDiff) { bestDiff = d; best = i; } }
      kick.textContent = '';
      el('tspan', { class: 'np-slash' }, kick).textContent = '// ';
      kick.appendChild(document.createTextNode(words.slice(0, best).join(' ')));
      el('tspan', { x: 20 + width(kick.querySelector('.np-slash')), dy: 16 }, kick).textContent = words.slice(best).join(' ');
      headH = C.head + 16;
    }
    const top = headH;
    const fieldH = Math.ceil((S + C.pad * 2 + dh) / 8) * 8;
    const dx = S + (W - S - dw) / 2, dy = top + S + (fieldH - S - dh) / 2;
    for (const [k, v] of Object.entries({ x: dx, y: dy, width: dw, height: dh })) svg.setAttribute(k, r2(v));
    field(fieldLayer, 0, top, W, fieldH, src.id, S);

    if (src.meta.fig) {
      const f = text(plate, 'np-head-meta', W - 20, 27, `FIG. ${src.meta.fig}`, 'end');
      f.setAttribute('data-exempt', '1');
      if (20 + width(kick) + 16 > W - 20 - width(f)) f.remove(); // no room: the title wins
    }
    el('path', { class: 'np-sep', d: `M0,${headH}H${W}` }, plate);

    let y = top + fieldH;
    y += foot(plate, y, W);
    const H = Math.ceil(y / 4) * 4;
    bg.setAttribute('height', H);
    el('rect', { class: 'np-frame', x: 0.5, y: 0.5, width: W - 1, height: H - 1, rx: T.radius.plate }, plate);
    plate.setAttribute('viewBox', `0 0 ${W} ${H}`);
    plate.setAttribute('height', H);
    return { width: W, height: H, scale: Math.round(s * 100) / 100 };
  };

  // ---------------------------------------------------------------- audit
  // Every drawn mark must land on a token: stroke widths, corner radii, and text floors,
  // measured after all transforms. render.mjs fails the figure on any violation.
  window.npAudit = (plate, T) => {
    const A = T.audit;
    const base = plate.getScreenCTM().a;
    const scaleOf = (n) => (n.getScreenCTM()?.a || base) / base;
    const near = (v, set) => set.some((x) => Math.abs(x - v) < 0.02);
    const out = [];
    const describe = (n) => `${n.tagName}.${(n.getAttribute('class') || '').split(' ')[0] || '-'}`;
    for (const n of plate.querySelectorAll('path, rect, circle, ellipse, polygon, line, polyline')) {
      if (n.closest('pattern, defs')) continue;
      const cs = getComputedStyle(n);
      if (cs.display === 'none') continue;
      const k = cs.vectorEffect === 'non-scaling-stroke' ? 1 : scaleOf(n);
      const sw = parseFloat(cs.strokeWidth) * k;
      if (cs.stroke !== 'none' && sw > 0 && !near(sw, A.strokes)) out.push(`stroke ${Math.round(sw * 100) / 100} on ${describe(n)}`);
      if (n.tagName === 'rect') {
        const rx = parseFloat(n.getAttribute('rx') || cs.rx || 0) || 0;
        if (!near(rx, A.radii)) out.push(`radius ${rx} on ${describe(n)}`);
      }
    }
    const W = plate.viewBox.baseVal.width;
    for (const t of plate.querySelectorAll('text')) {
      const b = t.getBBox();
      const m = t.closest('svg.np-diagram') ? null : b; // diagram text is measured in its own viewBox
      if (m && (m.x < 4 || m.x + m.width > W - 4)) out.push(`text runs past the plate edge: "${t.textContent.slice(0, 24)}"`);
    }
    for (const t of [...plate.querySelectorAll('text, tspan')].filter((t) => t.textContent.trim())) {
      const cs = getComputedStyle(t);
      const size = parseFloat(cs.fontSize) * scaleOf(t);
      const mono = /Mono/.test(cs.fontFamily);
      if (size + 0.01 < (mono ? A.minMono : A.minSans)) out.push(`text ${Math.round(size * 10) / 10}px "${t.textContent.slice(0, 20)}"`);
    }
    return [...new Set(out)];
  };

  // ---------------------------------------------------------------- share card
  window.npComposeOg = (card, T) => {
    const C = T.canvas.og;
    const W = C.width, H = C.height;
    const plate = el('svg', { xmlns: NS, class: 'np-plate np-kind-og np-light', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img' }, document.body);
    el('style', {}, plate).textContent = '/*NP-STYLE*/';
    el('title', {}, plate).textContent = card.meta['og-title'];
    defs(plate, card.id, T);
    el('rect', { class: 'np-canvas', x: 0, y: 0, width: W, height: H }, plate);
    el('rect', { class: 'np-og-rule', x: 0, y: 0, width: W, height: 4 }, plate);
    const fx = 624, fy = 40, fw = W - fx - 40, fh = H - 80;
    el('rect', { class: 'np-og-panel', x: fx, y: fy, width: fw, height: fh, rx: 4 }, plate);
    const F = field(el('g', {}, plate), fx, fy, fw, fh, card.id);
    let scale = 0;
    if (card.mermaid) {
      const host = el('g', {}, plate);
      const svg = renderPele(host, card, T, 300);
      svg.classList.add('np-scaled');
      brandDiagram(svg, card, T, card.id);
      const { s, cw, ch } = fit(svg, fx + fw - F.ox - 56, fy + fh - F.oy - 56, C.minDiagramScale, 2.6, card);
      scale = s;
      const dw = cw * s, dh = ch * s;
      for (const [k, v] of Object.entries({ x: F.ox + (fx + fw - F.ox - dw) / 2, y: F.oy + (fy + fh - F.oy - dh) / 2, width: dw, height: dh })) svg.setAttribute(k, r2(v));
    }
    kickerText(plate, C.pad, 100, card.meta['og-kicker'] || 'Article', 'np-og-kicker');
    const roleT = T.type.roles['og-title'];
    const maxW = fx - C.pad - 40;
    // Title steps down 54 → 48 → 42 px until it fits in four lines.
    const wrap = (size) => {
      const probe = el('text', { class: 'np-og-title', style: `font-size:${size}px` }, plate);
      const lines = [];
      let cur = '';
      for (const w of card.meta['og-title'].split(/\s+/)) {
        const next = cur ? `${cur} ${w}` : w;
        probe.textContent = next;
        if (canvasWidth(probe) > maxW && cur) { lines.push(cur); cur = w; } else cur = next;
      }
      lines.push(cur);
      probe.remove();
      return lines;
    };
    const size = C.titleSizes.find((sz) => wrap(sz).length <= 4);
    if (!size) throw new Error(`og title does not fit in four lines even at ${C.titleSizes[C.titleSizes.length - 1]} px`);
    const lines = wrap(size);
    const t = el('text', { class: 'np-og-title', x: C.pad, y: 100 + 30 + size, style: `font-size:${size}px`, 'data-exempt': '1' }, plate);
    lines.forEach((line, i) => { el('tspan', { x: C.pad, dy: i === 0 ? 0 : r2(size * roleT.leading) }, t).textContent = line; });
    const by = H - 40 - 48;
    el('path', { class: 'np-sep', d: `M${C.pad},${by}H${fx - 40}` }, plate);
    text(plate, 'np-og-byline', C.pad, by + 26, 'NINAD PATHAK').setAttribute('data-exempt', '1');
    text(plate, 'np-og-url', C.pad, by + 46, card.meta['og-url'] || `ninadpathak.com/articles/${card.slug}/`).setAttribute('data-exempt', '1');
    el('rect', { class: 'np-frame', x: 0.5, y: 0.5, width: W - 1, height: H - 1 }, plate);
    return { width: W, height: H, scale: Math.round(scale * 100) / 100 };
  };
})();
