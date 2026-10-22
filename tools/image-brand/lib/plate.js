/* Runs inside headless Chromium after pele.global.js and the brand fonts have loaded.
 * Pele lays the diagram out; this file restyles its SVG into the ninadpathak.com image
 * brand, re-routes flowchart edges orthogonally, draws the annotation components, and
 * composes the plate. Coordinates are display pixels at the 720 px article width.
 *
 * Component numbers (C1 … C16) match GUIDELINE.md §8.
 */
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const NODE_CLASSES = ['accent', 'focal', 'outcome', 'muted', 'fail', 'pass', 'external', 'stack'];
  const LEGEND_DEFAULTS = {
    accent: 'Primary step', focal: 'Focus', outcome: 'Outcome', muted: 'Optional', fail: 'Failure', pass: 'Pass',
    external: 'External', stack: 'Many instances', hot: 'Primary path', flow: 'Flow', async: 'Async', both: 'Two-way',
  };
  const COL = 80; // grid coordinate pitch (C3)

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
  const width = (t) => t.getComputedTextLength();
  const parsePoints = (d) => [...d.matchAll(/(-?\d*\.?\d+),(-?\d*\.?\d+)/g)].map((m) => [Number(m[1]), Number(m[2])]);
  const fail = (src, msg) => { throw new Error(`${src.id}: ${msg}`); };

  function makeMeasurer(T) {
    const ctx = document.createElement('canvas').getContext('2d');
    const role = T.type.roles;
    return {
      width(t, size, style) {
        let r = { ...role['node-label'], size };
        if (style & 1) r = { ...role['node-strong'], size };
        if (style & 4) r = { family: 'mono', weight: 400, size, tracking: '0' };
        if (t.startsWith('§')) { r = role['node-kicker']; t = t.slice(1).toUpperCase(); }
        else if (t.startsWith('~')) { r = role['node-detail']; t = t.slice(1); }
        ctx.font = `${r.weight} ${r.size}px '${r.family === 'mono' ? T.type.mono : T.type.sans}'`;
        ctx.letterSpacing = r.tracking && r.tracking !== '0' ? `${parseFloat(r.tracking) * r.size}px` : '0px';
        // A kicker may carry a right-aligned meta (`§Layer 1 | sync`); reserve a gap for it.
        return ctx.measureText(t.replace(/\s*\|\s*/, ' '.repeat(6))).width;
      },
    };
  }

  // ---------------------------------------------------------------- geometry
  function boxes(svg) {
    const map = new Map();
    for (const g of svg.querySelectorAll('.pele-node, .pele-cluster')) {
      const id = g.getAttribute('data-id');
      if (!id) continue;
      const shape = g.querySelector(':scope > .np-shape') || g.querySelector('rect, polygon, path, circle, ellipse');
      if (!shape) continue;
      const b = shape.getBBox();
      const m = (g.getAttribute('transform') || '').match(/translate\(([-\d.]+),([-\d.]+)\)/);
      const [tx, ty] = m ? [Number(m[1]), Number(m[2])] : [0, 0];
      const x = b.x + tx, y = b.y + ty;
      map.set(id, { id, g, x, y, w: b.width, h: b.height, l: x, r: x + b.width, t: y, b: y + b.height, cx: x + b.width / 2, cy: y + b.height / 2, cluster: g.classList.contains('pele-cluster') });
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
  const chevron = (tip, from) => {
    const dx = tip[0] - from[0], dy = tip[1] - from[1], len = Math.hypot(dx, dy) || 1;
    const ux = dx / len, uy = dy / len, L = 8, Wd = 3.4;
    const bx = tip[0] - ux * L, by = tip[1] - uy * L;
    return `M${r2(bx - uy * Wd)},${r2(by + ux * Wd)}L${r2(tip[0])},${r2(tip[1])}L${r2(bx + uy * Wd)},${r2(by - ux * Wd)}`;
  };

  // C6 · Orthogonal router. Edges leave and enter at side centres; siblings that leave the
  // same side share one port and one bus line, so trees come out symmetric.
  function routeEdges(svg, nodes, src, T) {
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
    const relation = (s, t) => {
      const gaps = { down: t.t - s.b, up: s.t - t.b, right: t.l - s.r, left: s.l - t.r };
      const best = Object.entries(gaps).filter(([, v]) => v >= 6).sort((a, b) => b[1] - a[1])[0];
      return best ? best[0] : null;
    };
    for (const e of edges) {
      e.s = nodes.get(e.from); e.t = nodes.get(e.to);
      e.rel = e.s && e.t ? relation(e.s, e.t) : null;
      const lp = parsePoints(e.line.getAttribute('d'));
      const near = (m, p) => { const tip = parsePoints(m.getAttribute('d'))[0]; return Math.hypot(tip[0] - p[0], tip[1] - p[1]); };
      e.both = e.markers.length >= 2;
      e.reverse = e.markers.length === 1 && near(e.markers[0], lp[0]) < near(e.markers[0], lp[lp.length - 1]);
      e.headless = e.markers.length === 0;
      e.dashed = /dash/.test(e.line.getAttribute('style') || '') || e.line.hasAttribute('stroke-dasharray');
    }
    const groups = new Map();
    for (const e of edges) if (e.rel) groups.set(`${e.from}:${e.rel}`, [...(groups.get(`${e.from}:${e.rel}`) || []), e]);

    for (const e of edges) {
      if (!e.rel) { e.pts = parsePoints(e.line.getAttribute('d')); e.routed = false; continue; }
      const { s, t } = e;
      const sign = e.rel === 'down' || e.rel === 'right' ? 1 : -1;
      const group = groups.get(`${e.from}:${e.rel}`);
      let pts;
      if (e.rel === 'down' || e.rel === 'up') {
        const sy = sign > 0 ? s.b : s.t, ey = sign > 0 ? t.t : t.b;
        const lo = Math.max(s.l, t.l) + 14, hi = Math.min(s.r, t.r) - 14;
        if (group.length > 1) {
          const gap = Math.min(...group.map((g) => (sign > 0 ? g.t.t - s.b : s.t - g.t.b)));
          const my = sy + (sign * gap) / 2;
          pts = [[s.cx, sy], [s.cx, my], [t.cx, my], [t.cx, ey]];
        } else if (lo <= hi) {
          const x = s.cx >= lo && s.cx <= hi ? s.cx : t.cx >= lo && t.cx <= hi ? t.cx : (lo + hi) / 2;
          pts = [[x, sy], [x, ey]];
        } else {
          const my = (sy + ey) / 2;
          pts = [[s.cx, sy], [s.cx, my], [t.cx, my], [t.cx, ey]];
        }
      } else {
        const sx = sign > 0 ? s.r : s.l, ex = sign > 0 ? t.l : t.r;
        const lo = Math.max(s.t, t.t) + 10, hi = Math.min(s.b, t.b) - 10;
        if (group.length > 1) {
          const gap = Math.min(...group.map((g) => (sign > 0 ? g.t.l - s.r : s.l - g.t.r)));
          const mx = sx + sign * gap * 0.4;
          pts = [[sx, s.cy], [mx, s.cy], [mx, t.cy], [ex, t.cy]];
        } else if (lo <= hi) {
          const y = s.cy >= lo && s.cy <= hi ? s.cy : t.cy >= lo && t.cy <= hi ? t.cy : (lo + hi) / 2;
          pts = [[sx, y], [ex, y]];
        } else {
          const mx = (sx + ex) / 2;
          pts = [[sx, s.cy], [mx, s.cy], [mx, t.cy], [ex, t.cy]];
        }
      }
      e.bus = group.length > 1;
      e.pts = pts;
      e.routed = true;
    }
    return edges;
  }

  // Draw shafts, chevrons, ports (C7, output ring) and handles (C7, input square).
  function drawEdges(svg, edges, T) {
    const ports = el('g', { class: 'np-ports' }, svg);
    const seen = new Set();
    for (const e of edges) {
      for (const m of e.markers) m.remove();
      const pts = e.pts.map((p) => [...p]);
      // Arrow direction follows the source: for a reversed edge the head sits at pts[0].
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
      if (!e.both) {
        const p = e.reverse ? clean[clean.length - 1] : clean[0];
        const key = `p${r2(p[0])},${r2(p[1])}`;
        if (!seen.has(key)) { seen.add(key); el('circle', { class: `np-port${e.hot ? ' np-port-hot' : ''}`, cx: r2(p[0]), cy: r2(p[1]), r: 2.5 }, ports); }
      }
    }
    svg.appendChild(ports);
  }

  // C8 · Edge labels: mono caps on a canvas mask; `label :: payload` adds a payload chip.
  function brandEdgeLabels(svg, edges) {
    const layer = el('g', { class: 'np-edge-labels' }, svg);
    for (const label of [...svg.querySelectorAll('.pele-edge-label')]) {
      const id = label.getAttribute('data-id') || '';
      const e = edges.find((x) => x.id === id);
      const old = label.querySelector('rect');
      const [name, payload] = label.querySelector('text').textContent.split(' :: ');
      let p;
      if (e?.routed) {
        const segs = segments(e.drawn);
        const last = segs[segs.length - 1];
        // On a bus, the label belongs on the branch's own drop, not the shared trunk.
        p = at(last.len >= (payload ? 44 : 24) ? last : [...segs].sort((a, b) => b.len - a.len)[0], 0.5);
      } else {
        p = [Number(old.getAttribute('x')) + Number(old.getAttribute('width')) / 2, Number(old.getAttribute('y')) + Number(old.getAttribute('height')) / 2];
      }
      label.remove();
      const g = el('g', { class: `np-edge-label${e?.hot ? ' np-hot' : ''}` }, layer);
      // A branch whose own horizontal run is short carries its label above the line,
      // set flush to the arrow, so the trunk and the arrowhead stay visible.
      if (e?.routed && !payload) {
        const segs = segments(e.drawn);
        const last = segs[segs.length - 1];
        const horizontal = Math.abs(last.a[1] - last.b[1]) < 0.5;
        if ((segs.length > 1 || e.bus) && horizontal && last.len < 140) {
          const dir = Math.sign(last.b[0] - last.a[0]);
          const tx = last.b[0] - dir * 14;
          text(g, 'np-edge-text', tx, last.b[1] - 6, name.toUpperCase(), dir > 0 ? 'end' : 'start');
          continue;
        }
      }
      const mask = el('rect', { class: 'np-label-mask', rx: 2 }, g);
      const h = payload ? 38 : 16;
      const nt = central(text(g, 'np-edge-text', p[0], payload ? p[1] - 10 : p[1], name.toUpperCase(), 'middle'));
      let w = width(nt);
      if (payload) {
        const chip = el('rect', { class: 'np-payload-chip', rx: 2 }, g);
        const pt = central(text(g, 'np-payload', p[0], p[1] + 9, payload, 'middle'));
        const pw = width(pt);
        for (const [k, v] of Object.entries({ x: p[0] - pw / 2 - 6, y: p[1] + 1, width: pw + 12, height: 16 })) chip.setAttribute(k, r2(v));
        w = Math.max(w, pw + 12);
      }
      for (const [k, v] of Object.entries({ x: p[0] - w / 2 - 6, y: p[1] - h / 2, width: w + 12, height: h })) mask.setAttribute(k, r2(v));
    }
  }

  // C10 · Step markers: numbered squares along the hot path, in @path order.
  function stepMarkers(svg, edges, src) {
    const layer = el('g', { class: 'np-steps' }, svg);
    const order = src.meta.hotEdges.map(([a, b]) => edges.find((x) => x.from === a && x.to === b)).filter((e) => e?.drawn);
    order.forEach((e, i) => {
      const segs = segments(e.drawn);
      if (Math.max(...segs.map((x) => x.len)) < 36) return;
      const first = segs[0];
      const p = first.len >= 30 ? at(first, Math.min(0.5, 16 / first.len)) : at([...segs].sort((a, b) => b.len - a.len)[0], 0.3);
      el('rect', { class: 'np-step', x: r2(p[0] - 7), y: r2(p[1] - 7), width: 14, height: 14, rx: 2 }, layer);
      central(text(layer, 'np-step-num', p[0], p[1] + 0.5, String(i + 1), 'middle'));
    });
  }

  // ---------------------------------------------------------------- Pele restyle
  function brandDiagram(svg, src, T, defsId) {
    const used = new Set();
    const meta = src.meta;
    svg.classList.add('np-diagram');
    svg.removeAttribute('width');
    svg.removeAttribute('height');

    // C5 · Clusters: dashed boundary; label strip lifted above the edges on a mask.
    const clusterLabels = el('g', { class: 'np-cluster-labels' }, svg);
    for (const cluster of svg.querySelectorAll('.pele-cluster')) {
      const rect = cluster.querySelector('rect');
      const label = cluster.querySelector('.pele-cluster-label');
      for (const a of ['fill', 'fill-opacity', 'stroke']) rect.removeAttribute(a);
      rect.classList.add('np-shape');
      if (cluster.classList.contains('hatch')) {
        rect.after(el('rect', { class: 'np-hatch-fill', x: rect.getAttribute('x'), y: rect.getAttribute('y'), width: rect.getAttribute('width'), height: rect.getAttribute('height'), rx: T.radius.node, fill: `url(#${defsId}-hatch)` }));
      }
      if (cluster.classList.contains('ghost') || !label || !label.textContent.trim()) { label?.remove(); continue; }
      const x = Number(rect.getAttribute('x')), y = Number(rect.getAttribute('y')), w = Number(rect.getAttribute('width'));
      const g = el('g', { class: 'np-cluster-head' }, clusterLabels);
      const [name, metaText] = label.textContent.split(' | ');
      label.textContent = name.toUpperCase();
      label.removeAttribute('fill');
      for (const [k, v] of Object.entries({ x: x + 20, y: y + 17, 'text-anchor': 'start' })) label.setAttribute(k, v);
      el('rect', { class: 'np-cluster-mask' }, g);
      el('rect', { class: 'np-cluster-mask-wash' }, g);
      el('rect', { class: 'np-cluster-tick', x: x + 10, y: y + 10, width: 4, height: 4 }, g);
      g.appendChild(label);
      if (metaText) {
        const mt = text(g, 'np-cluster-meta', x + w - 10, y + 17, metaText.toUpperCase(), 'end');
        mt.dataset.mask = '1';
      }
    }

    // C4 · Nodes: line roles, card alignment, class treatments, stacked instances.
    let index = 0;
    for (const node of svg.querySelectorAll('.pele-node')) {
      const shapes = [...node.querySelectorAll(':scope > rect, :scope > polygon, :scope > path, :scope > circle, :scope > ellipse')];
      const shape = shapes[0];
      for (const c of NODE_CLASSES) if (node.classList.contains(c)) used.add(c);
      for (const s of shapes) { s.removeAttribute('fill'); s.removeAttribute('stroke'); s.classList.add('np-shape'); }
      if (node.classList.contains('stack')) {
        for (const off of [6, 3]) for (const sh of shapes) {
          const ghost = sh.cloneNode(true);
          ghost.setAttribute('class', 'np-stack-ghost');
          ghost.setAttribute('transform', `translate(${off},${-off})`);
          node.insertBefore(ghost, shapes[0]);
        }
      }
      const label = node.querySelector('.pele-label');
      let hasKicker = false;
      if (label) {
        const lines = label.querySelectorAll('tspan[x]').length ? [...label.querySelectorAll('tspan[x]')] : [label];
        let inDetail = false;
        for (const line of lines) {
          const t = line.textContent;
          if (inDetail) { line.classList.add('np-detail'); continue; }
          if (t.startsWith('§')) {
            const [k, m] = t.slice(1).split(/\s*\|\s*/);
            line.textContent = k.toUpperCase();
            line.classList.add('np-kicker');
            if (m) line.dataset.meta = m.toUpperCase();
            hasKicker = true;
          } else if (t.startsWith('~')) { line.textContent = t.slice(1); line.classList.add('np-detail'); inDetail = true; }
        }
        if (hasKicker && shape && shape.tagName === 'rect') {
          const x = Number(shape.getAttribute('x')), w = Number(shape.getAttribute('width'));
          const textW = Math.max(...lines.map((l) => l.getComputedTextLength()));
          const pad = Math.max(10, Math.min(16, (w - textW) / 2));
          label.setAttribute('text-anchor', 'start');
          for (const line of lines) line.setAttribute('x', r2(x + pad));
          for (const line of lines.filter((l) => l.dataset.meta)) {
            const mt = el('text', { class: 'np-kicker-meta', x: r2(x + w - pad), y: line.getAttribute('y'), 'text-anchor': 'end' }, node);
            mt.textContent = line.dataset.meta;
          }
          node.classList.add('np-card');
        }
      }
      if (shape && shape.tagName === 'rect') {
        const x = Number(shape.getAttribute('x')), y = Number(shape.getAttribute('y')), w = Number(shape.getAttribute('width')), h = Number(shape.getAttribute('height'));
        const rr = T.radius.node;
        if (node.classList.contains('external')) shape.after(el('rect', { class: 'np-hatch-fill', x, y, width: w, height: h, rx: rr, fill: `url(#${defsId}-hatch)` }));
        if (['accent', 'fail', 'pass'].some((c) => node.classList.contains(c))) {
          const h3 = T.stroke['accent-rule'];
          const rule = el('path', { class: 'np-rule', d: `M${x},${y + h3}V${y + rr}A${rr},${rr} 0 0 1 ${x + rr},${y}H${x + w - rr}A${rr},${rr} 0 0 1 ${x + w},${y + rr}V${y + h3}Z` });
          label ? label.before(rule) : node.appendChild(rule);
        }
      }
      index += 1;
      if (meta.index === 'on' && shape) {
        const b = shape.getBBox();
        text(node, 'np-index', b.x, b.y - 5, String(index).padStart(2, '0'));
      }
    }

    const nodes = boxes(svg);
    let edges = [];
    if (svg.classList.contains('pele-flowchart')) {
      edges = routeEdges(svg, nodes, src, T);
      const hot = new Set(meta.hotEdges.map(([a, b]) => `${a}>${b}`));
      for (const e of edges) {
        e.hot = hot.has(`${e.from}>${e.to}`);
        if (e.hot) { e.g.classList.add('np-hot'); used.add('hot'); }
        used.add(e.dashed ? 'async' : e.both ? 'both' : 'flow');
      }
      drawEdges(svg, edges, T);
      brandEdgeLabels(svg, edges);
      if (meta.hotEdges.length) stepMarkers(svg, edges, src);
    }
    svg.appendChild(clusterLabels);
    for (const head of clusterLabels.querySelectorAll('.np-cluster-head')) {
      const b = head.querySelector('.pele-cluster-label').getBBox();
      for (const m of head.querySelectorAll('.np-cluster-mask, .np-cluster-mask-wash')) {
        for (const [k, v] of Object.entries({ x: b.x - 16, y: b.y - 3, width: b.width + 22, height: b.height + 6, rx: T.radius.label })) m.setAttribute(k, r2(v));
      }
      const mt = head.querySelector('.np-cluster-meta');
      if (mt) {
        const mb = mt.getBBox();
        const mm = el('rect', { class: 'np-cluster-mask', x: r2(mb.x - 6), y: r2(mb.y - 3), width: r2(mb.width + 12), height: r2(mb.height + 6), rx: T.radius.label });
        head.insertBefore(mm, mt);
        head.insertBefore(el('rect', { class: 'np-cluster-mask-wash', x: r2(mb.x - 6), y: r2(mb.y - 3), width: r2(mb.width + 12), height: r2(mb.height + 6), rx: T.radius.label }), mt);
      }
    }
    if (svg.classList.contains('pele-xychart')) brandChart(svg, src, T, defsId, used);
    return { used, nodes, edges };
  }

  // C14 · Bar charts: series fills, value labels at bar ends, quiet grid.
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
    const fmt = (v) => { const r = Math.round(v * 100) / 100; return `${unit}${Number.isInteger(r) ? r : r.toFixed(2)}`; };
    const values = el('g', { class: 'np-values' }, svg);
    [...svg.querySelectorAll('.pele-series')].forEach((series, si) => {
      series.removeAttribute('fill');
      series.classList.add(`np-series-${si + 1}`);
      used.add(`series-${si + 1}`);
      for (const r of [...series.querySelectorAll('rect')]) {
        const x = Number(r.getAttribute('x')), y = Number(r.getAttribute('y')), w = Number(r.getAttribute('width')), h = Number(r.getAttribute('height'));
        if (si === 1) series.appendChild(el('rect', { class: 'np-hatch-fill', x, y, width: w, height: h, fill: `url(#${defsId}-hatch)` }));
        const v = horizontal ? w / ppu : h / ppu;
        if (horizontal) central(text(values, 'np-value', x + w + 5, y + h / 2, fmt(v)));
        else text(values, 'np-value', x + w / 2, y - 5, fmt(v), 'middle');
      }
    });
  }

  // C11 · Dimension lines between two nodes or clusters, in a gutter right of or below the diagram.
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
    for (const d of src.meta.dims) {
      const a = nodes.get(d.from), b = nodes.get(d.to);
      if (!a || !b) fail(src, `@dim target "${!a ? d.from : d.to}" is not a node or cluster id`);
      const vertical = a === b || a.b <= b.t + 1 || b.b <= a.t + 1 || (Math.max(a.b, b.b) - Math.min(a.t, b.t)) > (Math.max(a.r, b.r) - Math.min(a.l, b.l));
      if (vertical) {
        const top = a.t <= b.t ? a : b, bot = a.b >= b.b ? a : b;
        const x = right + 20 + slot('v', top.t, bot.b) * 30;
        el('path', { class: 'np-dim-ext', d: `M${r2(top.r + 4)},${r2(top.t)}H${r2(x + 6)}M${r2(bot.r + 4)},${r2(bot.b)}H${r2(x + 6)}` }, layer);
        el('path', { class: 'np-dim-line', d: `M${r2(x)},${r2(top.t)}V${r2(bot.b)}${tick(x, top.t)}${tick(x, bot.b)}` }, layer);
        const t = text(layer, 'np-dim-text', 0, 0, d.label.toUpperCase(), 'middle');
        t.setAttribute('transform', `translate(${r2(x + 12)},${r2((top.t + bot.b) / 2)}) rotate(90)`);
      } else {
        const lft = a.l <= b.l ? a : b, rgt = a.r >= b.r ? a : b;
        const y = bottom + 20 + slot('h', lft.l, rgt.r) * 30;
        el('path', { class: 'np-dim-ext', d: `M${r2(lft.l)},${r2(lft.b + 4)}V${r2(y + 6)}M${r2(rgt.r)},${r2(rgt.b + 4)}V${r2(y + 6)}` }, layer);
        el('path', { class: 'np-dim-line', d: `M${r2(lft.l)},${r2(y)}H${r2(rgt.r)}${tick(lft.l, y)}${tick(rgt.r, y)}` }, layer);
        const t = central(text(layer, 'np-dim-text', (lft.l + rgt.r) / 2, y, d.label.toUpperCase(), 'middle'));
        const w = width(t);
        layer.insertBefore(el('rect', { class: 'np-label-mask', x: r2((lft.l + rgt.r) / 2 - w / 2 - 6), y: r2(y - 7), width: r2(w + 12), height: 14 }), t);
      }
    }
  }

  // C12 · Detail marks: a dashed boundary and lettered tag on the node a detail panel expands.
  function drawDetailMarks(svg, src, nodes) {
    if (!src.meta.details.length) return;
    const layer = el('g', { class: 'np-detail-marks' }, svg);
    src.meta.details.forEach((d, i) => {
      const n = nodes.get(d.target);
      if (!n) fail(src, `@detail target "${d.target}" is not a node id`);
      el('rect', { class: 'np-detail-ring', x: r2(n.x - 5), y: r2(n.y - 5), width: r2(n.w + 10), height: r2(n.h + 10), rx: 6 }, layer);
      tag(layer, n.x - 5, n.b + 5, String.fromCharCode(65 + i));
    });
  }

  function tag(parent, cx, cy, letter) {
    el('rect', { class: 'np-detail-tag', x: r2(cx - 7), y: r2(cy - 7), width: 14, height: 14, rx: 2 }, parent);
    central(text(parent, 'np-detail-letter', cx, cy + 0.5, letter, 'middle'));
  }

  // ---------------------------------------------------------------- plate parts
  function defs(plate, id, T) {
    const d = el('defs', {}, plate);
    const grid = T.canvas.article.grid;
    const dots = el('pattern', { id: `${id}-grid`, width: grid, height: grid, patternUnits: 'userSpaceOnUse' }, d);
    el('circle', { class: 'np-grid-dot', cx: grid / 2, cy: grid / 2, r: 0.75 }, dots);
    const hatch = el('pattern', { id: `${id}-hatch`, width: 6, height: 6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, d);
    el('path', { class: 'np-hatch', d: 'M0,0V6' }, hatch);
  }

  // C1 · Drafting field, C2 · ruler, C3 · grid coordinates, crop marks.
  function field(parent, x, y, w, h, id) {
    const S = 16;
    el('rect', { class: 'np-field', x, y, width: w, height: h, fill: `url(#${id}-grid)` }, parent);
    el('rect', { class: 'np-strip', x, y, width: w, height: S }, parent);
    el('rect', { class: 'np-strip', x, y: y + S, width: S, height: h - S }, parent);
    el('path', { class: 'np-sep', d: `M${x},${y + S}H${x + w}M${x + S},${y}V${y + h}` }, parent);
    const ox = x + S, oy = y + S;
    let grid = '';
    for (let i = 0, cx = ox; cx < x + w - 1; i++, cx += COL) {
      if (x + w - cx >= 24) text(parent, 'np-coord', cx + Math.min(COL, x + w - cx) / 2, y + 11.5, String.fromCharCode(65 + i), 'middle');
      if (i) grid += `M${cx},${y}v${S}`;
    }
    for (let i = 0, cy = oy; cy < y + h - 1; i++, cy += COL) {
      if (y + h - cy >= 24) text(parent, 'np-coord', x + S / 2, cy + Math.min(COL, y + h - cy) / 2 + 3, String(i + 1), 'middle');
      if (i) grid += `M${x},${cy}h${S}`;
    }
    el('path', { class: 'np-sep', d: grid }, parent);
    let d = '';
    for (let i = 8; ox + i < x + w; i += 8) d += `M${ox + i},${oy}v${i % 40 === 0 ? 6 : 3}`;
    for (let i = 8; oy + i < y + h; i += 8) d += `M${ox},${oy + i}h${i % 40 === 0 ? 6 : 3}`;
    el('path', { class: 'np-ruler', d }, parent);
    const ci = 14, arm = 8;
    const corners = [[ox + ci, oy + ci, 1, 1], [x + w - ci, oy + ci, -1, 1], [ox + ci, y + h - ci, 1, -1], [x + w - ci, y + h - ci, -1, -1]];
    el('path', { class: 'np-crop', d: corners.map(([cx, cy, sx, sy]) => `M${cx},${cy + sy * arm}V${cy}H${cx + sx * arm}`).join('') }, parent);
    return { ox, oy, coord: (px, py) => `${String.fromCharCode(65 + Math.max(0, Math.floor((px - ox) / COL)))}${Math.max(0, Math.floor((py - oy) / COL)) + 1}` };
  }

  function kickerText(parent, x, y, content, cls, anchor = 'start') {
    const t = el('text', { class: cls, x, y, 'text-anchor': anchor }, parent);
    el('tspan', { class: 'np-slash' }, t).textContent = '// ';
    t.appendChild(document.createTextNode(content.toUpperCase()));
    return t;
  }

  function badge(parent, cx, cy, n) {
    el('circle', { class: 'np-badge', cx: r2(cx), cy: r2(cy), r: 8.5 }, parent);
    central(text(parent, 'np-badge-num', cx, cy + 0.5, String(n), 'middle'));
  }

  function panelFrame(parent, x, y, w, h, title, letter, meta) {
    const g = el('g', { class: 'np-panel' }, parent);
    el('rect', { class: 'np-panel-box', x, y, width: w, height: h, rx: 4 }, g);
    el('rect', { class: 'np-panel-head', x: x + 0.5, y: y + 0.5, width: w - 1, height: 23.5, rx: 3.5 }, g);
    el('path', { class: 'np-sep', d: `M${x},${y + 24}H${x + w}` }, g);
    let tx = x + 12;
    if (letter) { tag(g, x + 17, y + 12, letter); tx = x + 31; }
    text(g, 'np-panel-title', tx, y + 16, title.toUpperCase());
    if (meta) text(g, 'np-panel-meta', x + w - 12, y + 16, meta, 'end');
    return g;
  }

  // C12 · Detail panel: key/value rows for the node a detail tag marks.
  function detailPanel(parent, x, y, w, d, letter, ref) {
    const h = 24 + 8 + d.rows.length * 24;
    const g = panelFrame(parent, x, y, w, h, d.title, letter, `DETAIL ${letter} · ${ref}`);
    const keys = d.rows.map(([k]) => text(g, 'np-kv-key', x + 12, 0, k.toUpperCase()));
    const kw = Math.max(...keys.map(width)) + 14;
    d.rows.forEach(([, v], i) => {
      const yy = y + 24 + 20 + i * 24;
      keys[i].setAttribute('y', yy);
      const t = text(g, 'np-kv-value', x + 12 + kw, yy, v);
      if (x + 12 + kw + width(t) > x + w - 10) throw new Error(`detail ${letter} value "${v}" is too long for its panel`);
      if (i < d.rows.length - 1) el('path', { class: 'np-row-sep', d: `M${x + 12},${yy + 8}H${x + w - 12}` }, g);
    });
    return h;
  }

  // C13 · Data table with an optional inline bar column (C14 mini-chart).
  function tablePanel(parent, x, y, w, spec) {
    const rowH = 24, head = 24 + 24;
    const h = head + spec.rows.length * rowH + 4;
    const g = panelFrame(parent, x, y, w, h, spec.title, null, `${spec.rows.length} ROWS`);
    const isNum = (s) => /^[~≈<>]?\s?[$€£]?[-\d.,]+\s*(%|×|x|ms|s|GB|MB|K|M|B)?(\s?[-–]\s?[$€£]?[-\d.,]+\s*(%|×|x|ms|s|GB)?)?$/i.test(s.trim());
    const numCols = spec.columns.map((_, c) => spec.rows.every((r) => isNum(r[c])));
    const probe = (s, cls) => { const t = text(g, cls, 0, -100, s); const v = width(t); t.remove(); return v; };
    const BAR = spec.bar !== null ? 92 : 0;
    const colW = spec.columns.map((col, c) => Math.max(probe(col.toUpperCase(), 'np-th'), ...spec.rows.map((r) => probe(r[c], numCols[c] ? 'np-td-num' : 'np-td'))) + 24);
    const total = colW.reduce((s, v) => s + v, 0) + BAR;
    if (total > w - 24) throw new Error(`table "${spec.title}" needs ${Math.round(total)} px; the panel has ${w - 24}`);
    const textCols = colW.map((v, i) => [v, i]).filter(([, i]) => !numCols[i]);
    const grow = textCols.length ? textCols.sort((p, q) => q[0] - p[0])[0][1] : 0;
    colW[grow] += w - 24 - total;
    const xs = colW.reduce((acc, cw, i) => [...acc, acc[i] + cw], [x + 12]);
    const cx = (c) => (numCols[c] ? xs[c + 1] - 12 : xs[c]);
    spec.columns.forEach((col, c) => text(g, 'np-th', cx(c), y + 24 + 16, col.toUpperCase(), numCols[c] ? 'end' : 'start'));
    if (BAR) text(g, 'np-th', xs[xs.length - 1] + 4, y + 24 + 16, 'SCALE');
    el('path', { class: 'np-row-sep np-th-sep', d: `M${x + 12},${y + head}H${x + w - 12}` }, g);
    const vals = BAR ? spec.rows.map((r) => parseFloat(r[spec.bar].replace(/[^\d.-]/g, ''))) : [];
    const max = Math.max(...vals, 0);
    spec.rows.forEach((r, i) => {
      const yy = y + head + i * rowH + 16;
      r.forEach((cell, c) => text(g, numCols[c] ? 'np-td-num' : 'np-td', cx(c), yy, cell, numCols[c] ? 'end' : 'start'));
      if (BAR) {
        const bx = xs[xs.length - 1] + 4, full = BAR - 12;
        el('rect', { class: 'np-bar-track', x: r2(bx), y: yy - 7, width: full, height: 6 }, g);
        el('rect', { class: 'np-bar', x: r2(bx), y: yy - 7, width: r2(Math.max(1.5, (full * vals[i]) / max)), height: 6 }, g);
      }
      if (i < spec.rows.length - 1) el('path', { class: 'np-row-sep', d: `M${x + 12},${yy + 8}H${x + w - 12}` }, g);
    });
    return h;
  }

  // C15 · Step timeline: the hot path laid flat, with a return hook for loops.
  function timelinePanel(parent, x, y, w, spec, labelOf, refOf) {
    const h = spec.loop ? 112 : 84;
    const g = panelFrame(parent, x, y, w, h, spec.loop ? 'One iteration' : 'Sequence', null, `${spec.steps.length} STEPS${spec.loop ? ' · REPEATS' : ''}`);
    const ty = y + 54, x0 = x + 84, x1 = x + w - 84, n = spec.steps.length;
    const step = (x1 - x0) / (n - 1 || 1);
    el('path', { class: 'np-track', d: `M${x0},${ty}H${x1}` }, g);
    for (let i = 0; i < n - 1; i++) el('path', { class: 'np-arrow-free np-arrow-hot', d: chevron([x0 + (i + 0.5) * step + 4, ty], [x0 + i * step, ty]) }, g);
    spec.steps.forEach((id, i) => {
      const cx = x0 + i * step;
      el('rect', { class: 'np-step', x: r2(cx - 7), y: ty - 7, width: 14, height: 14, rx: 2 }, g);
      central(text(g, 'np-step-num', cx, ty + 0.5, String(i + 1), 'middle'));
      text(g, 'np-tl-label', cx, ty + 26, labelOf(id), 'middle');
      text(g, 'np-tl-ref', cx, ty - 14, refOf(id), 'middle');
    });
    if (spec.loop) {
      const ry = ty + 42;
      el('path', { class: 'np-track np-return', d: roundedPath([[x1 + 7, ty], [x1 + 60, ty], [x1 + 60, ry], [x0 - 60, ry], [x0 - 60, ty], [x0 - 10, ty]], 4).d }, g);
      el('path', { class: 'np-arrow-free np-arrow-hot', d: chevron([x0 - 9, ty], [x0 - 60, ty]) }, g);
      if (spec.returnLabel) {
        const t = central(text(g, 'np-tl-return', (x0 + x1) / 2, ry, spec.returnLabel.toUpperCase(), 'middle'));
        g.insertBefore(el('rect', { class: 'np-panel-mask', x: r2((x0 + x1) / 2 - width(t) / 2 - 8), y: ry - 7, width: r2(width(t) + 16), height: 14 }), t);
      }
    }
    return h;
  }

  // C16 · Title block: key row, then source / fig / scale / rev / drawn cells.
  function titleBlock(plate, y, W, src, facts, info) {
    const g = el('g', { class: 'np-title-block' }, plate);
    el('rect', { class: 'np-tb-bg', x: 0, y, width: W, height: 66 }, g);
    el('path', { class: 'np-sep', d: `M0,${y}H${W}M0,${y + 30}H${W}M56,${y}V${y + 30}` }, g);
    text(g, 'np-tb-label', 20, y + 19, 'KEY');
    const overrides = Object.fromEntries((src.meta.legend || '').split(';').filter(Boolean).map((p) => p.split('=').map((s) => s.trim())));
    const order = ['hot', 'flow', 'async', 'both', 'series-1', 'series-2', 'accent', 'focal', 'outcome', 'external', 'stack', 'muted', 'fail', 'pass'];
    const items = src.meta.legend === 'off' ? [] : order.filter((c) => facts.used.has(c) && overrides[c] !== 'off');
    let cx = 70;
    const ky = y + 19;
    for (const c of items) {
      const lg = el('g', { class: `np-legend-item np-legend-${c}` }, g);
      if (['hot', 'flow', 'async', 'both'].includes(c)) {
        el('path', { class: `np-legend-line np-legend-line-${c}`, d: `M${cx},${ky - 3.5}h20` }, lg);
        el('path', { class: `np-arrow-free${c === 'hot' ? ' np-arrow-hot' : ''}`, d: chevron([cx + 20, ky - 3.5], [cx, ky - 3.5]) }, lg);
        if (c === 'both') el('path', { class: 'np-arrow-free', d: chevron([cx, ky - 3.5], [cx + 20, ky - 3.5]) }, lg);
        else el('circle', { class: `np-port${c === 'hot' ? ' np-port-hot' : ''}`, cx, cy: ky - 3.5, r: 2.25 }, lg);
        cx += 27;
      } else {
        el('rect', { class: `np-swatch np-swatch-${c}`, x: cx, y: ky - 8.5, width: 14, height: 10, rx: 2 }, lg);
        if (['accent', 'fail', 'pass'].includes(c)) el('rect', { class: `np-swatch-rule np-swatch-rule-${c}`, x: cx, y: ky - 8.5, width: 14, height: 2.5 }, lg);
        if (['external', 'series-2'].includes(c)) el('rect', { class: 'np-hatch-fill', x: cx, y: ky - 8.5, width: 14, height: 10, rx: 2, fill: `url(#${src.id}-hatch)` }, lg);
        cx += 20;
      }
      const label = overrides[c] ?? (c.startsWith('series-') ? src.meta.seriesNames[Number(c.slice(7)) - 1] : LEGEND_DEFAULTS[c]) ?? c;
      cx += width(text(lg, 'np-legend', cx, ky, label.toUpperCase())) + 18;
    }
    if (cx - 18 > W - 16) throw new Error(`${src.id}: the key is ${Math.round(cx)} px wide; shorten @legend labels or drop entries`);
    const cells = [
      ['SOURCE', `${src.slug}/${src.id}.mmd`],
      ['FIG', src.meta.fig || '—'],
      ['SCALE', info.scale === 1 ? '1:1' : `${info.scale}:1`],
      ['REV', info.hash.slice(0, 7)],
      ['DRAWN', 'NINADPATHAK.COM'],
    ];
    const vw = cells.map(([, v]) => { const t = text(g, 'np-tb-value', 0, -50, v); const w = width(t); t.remove(); return w + 28; });
    vw[0] = W - vw.slice(1).reduce((a, b) => a + b, 0);
    let x = 0;
    cells.forEach(([label, value], i) => {
      if (i) el('path', { class: 'np-sep', d: `M${r2(x)},${y + 30}V${y + 66}` }, g);
      const px = x + (i ? 14 : 20);
      text(g, 'np-tb-label', px, y + 44, label);
      text(g, 'np-tb-value', px, y + 58, value);
      x += vw[i];
    });
    return 66;
  }

  function renderPele(host, src, T, maxWidth) {
    host.innerHTML = window.pele.render(src.mermaid, {
      measurer: makeMeasurer(T), fontFamily: T.type.sans, fontFamilyMono: T.type.mono, fontSize: 14,
      responsive: false, autoDirection: false, padding: 8, idPrefix: src.id, maxWidth, links: false, images: false,
      config: { flowchart: { nodeSpacing: T.layout.nodeSpacing, rankSpacing: T.layout.rankSpacing }, xyChart: { width: Math.min(maxWidth, T.layout.chartWidth), height: T.layout.chartHeight } },
    }).svg;
    return host.querySelector('svg');
  }

  // Grow the viewBox to the drawn content (dims and tags reach outside Pele's box), then scale.
  function fit(svg, maxW, maxH, minScale, maxScale, src) {
    const vb = svg.viewBox.baseVal;
    const bb = svg.getBBox();
    const x0 = Math.min(vb.x, bb.x - 2), y0 = Math.min(vb.y, bb.y - 2);
    const cw = Math.max(vb.x + vb.width, bb.x + bb.width + 2) - x0, ch = Math.max(vb.y + vb.height, bb.y + bb.height + 2) - y0;
    svg.setAttribute('viewBox', `${r2(x0)} ${r2(y0)} ${r2(cw)} ${r2(ch)}`);
    const s = Math.min(maxScale, maxW / cw, maxH ? maxH / ch : Infinity);
    if (s < minScale) fail(src, `diagram is ${Math.round(cw)}×${Math.round(ch)} px and would render at ${Math.round(s * 100)}%; the floor is ${Math.round(minScale * 1000) / 10}%. Split it or change direction.`);
    return { s, x0, y0, cw, ch };
  }

  // ---------------------------------------------------------------- article plate
  window.npComposeArticle = (src, T, info) => {
    const C = T.canvas.article;
    const W = Number(src.meta.width || C.width);
    const plate = el('svg', { xmlns: NS, class: 'np-plate np-kind-article', viewBox: `0 0 ${W} 100`, width: W, height: 100, role: 'img' }, document.body);
    el('style', {}, plate).textContent = '/*NP-STYLE*/';
    el('title', { id: `${src.id}-title` }, plate).textContent = src.meta.kicker || src.id;
    el('desc', { id: `${src.id}-desc` }, plate).textContent = src.meta.alt;
    plate.setAttribute('aria-labelledby', `${src.id}-title ${src.id}-desc`);
    defs(plate, src.id, T);
    const bg = el('rect', { class: 'np-canvas', x: 0, y: 0, width: W, height: 100 }, plate);
    const fieldLayer = el('g', { class: 'np-texture' }, plate);
    const host = el('g', {}, plate);
    const inner = W - 16 - 2 * C.pad;
    const svg = renderPele(host, src, T, inner);
    const facts = brandDiagram(svg, src, T, src.id);
    drawDims(svg, src, facts.nodes);
    drawDetailMarks(svg, src, facts.nodes);
    const { s, x0, y0, cw, ch } = fit(svg, inner, 0, C.minScale, 1, src);
    const dw = cw * s, dh = ch * s;
    const top = C.head;
    const fieldH = Math.ceil((16 + C.pad * 2 + dh) / 8) * 8;
    const dx = 16 + (W - 16 - dw) / 2, dy = top + 16 + (fieldH - 16 - dh) / 2;
    for (const [k, v] of Object.entries({ x: dx, y: dy, width: dw, height: dh })) svg.setAttribute(k, r2(v));
    const F = field(fieldLayer, 0, top, W, fieldH, src.id);
    const toPlate = (px, py) => [dx + (px - x0) * s, dy + (py - y0) * s];
    const refOf = (id) => { const n = facts.nodes.get(id); return n ? F.coord(...toPlate(n.cx, n.cy)) : ''; };

    // C9 · Callouts pinned to node corners, listed with grid references.
    const notesLayer = el('g', { class: 'np-notes' }, plate);
    const noteRefs = src.meta.notes.map((note, i) => {
      const n = facts.nodes.get(note.target);
      if (!n) fail(src, `@note target "${note.target}" is not a node id`);
      badge(notesLayer, ...toPlate(n.r, n.t), i + 1);
      return refOf(note.target);
    });

    let y = top + fieldH;
    if (src.meta.notes.length) {
      el('path', { class: 'np-sep', d: `M0,${y}H${W}` }, plate);
      y += 22;
      src.meta.notes.forEach((note, i) => {
        badge(plate, 28.5, y - 4, i + 1);
        text(plate, 'np-note-ref', 46, y, noteRefs[i]);
        const t = text(plate, 'np-note', 74, y, note.text);
        if (74 + width(t) > W - 20) fail(src, `note ${i + 1} is too long for one line`);
        y += 24;
      });
      y += 2;
    }

    // Panels band: timeline, table, then up to two detail panels side by side.
    const meta = src.meta;
    if (meta.timelineSpec || meta.tableSpec || meta.details.length) {
      el('path', { class: 'np-sep', d: `M0,${y}H${W}` }, plate);
      const band = el('rect', { class: 'np-panels-bg', x: 0, y, width: W, height: 10 }, plate);
      let py = y + 16;
      const labelOf = (id) => {
        const n = facts.nodes.get(id);
        const k = n?.g.querySelector('.np-kicker');
        if (k) { const t = k.textContent.replace(/^\d+\s+/, '').toLowerCase(); return t.charAt(0).toUpperCase() + t.slice(1); }
        return n?.g.querySelector('.pele-label')?.textContent || id;
      };
      if (meta.timelineSpec) py += timelinePanel(plate, 20, py, W - 40, meta.timelineSpec, labelOf, refOf) + 12;
      if (meta.tableSpec) py += tablePanel(plate, 20, py, W - 40, meta.tableSpec) + 12;
      if (meta.details.length) {
        const pw = meta.details.length === 1 ? W - 40 : (W - 52) / 2;
        const hs = meta.details.map((d, i) => detailPanel(plate, 20 + i * (pw + 12), py, pw, d, String.fromCharCode(65 + i), refOf(d.target)));
        py += Math.max(...hs) + 12;
      }
      py += 4;
      band.setAttribute('height', py - y);
      y = py;
    }

    // Head band.
    kickerText(plate, 20, 27, meta.kicker || src.id, 'np-head-kicker');
    text(plate, 'np-head-meta', W - 20, 27, meta.fig ? `FIG. ${meta.fig}` : src.slug.toUpperCase(), 'end');
    el('path', { class: 'np-sep', d: `M0,${C.head}H${W}` }, plate);

    const scale = Math.round(s * 100) / 100;
    y += titleBlock(plate, y, W, src, facts, { ...info, scale });
    const H = Math.ceil(y / 4) * 4;
    bg.setAttribute('height', H);
    el('rect', { class: 'np-frame', x: 0.5, y: 0.5, width: W - 1, height: H - 1, rx: T.radius.plate }, plate);
    plate.setAttribute('viewBox', `0 0 ${W} ${H}`);
    plate.setAttribute('height', H);
    return { width: W, height: H, scale };
  };

  // ---------------------------------------------------------------- share card
  // The card draws its own small diagram (the og source's Mermaid body) at 1.75x or more,
  // so its labels stay readable when a feed shows the card about 500 px wide.
  window.npComposeOg = (card, T, info) => {
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
      brandDiagram(svg, card, T, card.id);
      const { s, cw, ch } = fit(svg, fx + fw - F.ox - 56, fy + fh - F.oy - 56, C.minDiagramScale, 2.4, card);
      scale = s;
      const dw = cw * s, dh = ch * s;
      for (const [k, v] of Object.entries({ x: F.ox + (fx + fw - F.ox - dw) / 2, y: F.oy + (fy + fh - F.oy - dh) / 2, width: dw, height: dh })) svg.setAttribute(k, r2(v));
    }

    kickerText(plate, C.pad, 100, card.meta['og-kicker'] || 'Article', 'np-og-kicker');
    const roleT = T.type.roles['og-title'];
    const maxW = fx - C.pad - 40;
    const probe = el('text', { class: 'np-og-title' }, plate);
    const lines = [];
    let cur = '';
    for (const w of card.meta['og-title'].split(/\s+/)) {
      const next = cur ? `${cur} ${w}` : w;
      probe.textContent = next;
      if (probe.getComputedTextLength() > maxW && cur) { lines.push(cur); cur = w; } else cur = next;
    }
    lines.push(cur);
    probe.remove();
    if (lines.length > 4) throw new Error(`og title wraps to ${lines.length} lines; the limit is 4`);
    const t = el('text', { class: 'np-og-title', x: C.pad, y: 100 + 30 + roleT.size }, plate);
    lines.forEach((line, i) => { el('tspan', { x: C.pad, dy: i === 0 ? 0 : r2(roleT.size * roleT.leading) }, t).textContent = line; });

    // Title block, card edition.
    const by = H - 40 - 96, bw = fx - C.pad - 40;
    const g = el('g', { class: 'np-title-block' }, plate);
    el('rect', { class: 'np-og-block', x: C.pad, y: by, width: bw, height: 96, rx: 4 }, g);
    el('path', { class: 'np-sep', d: `M${C.pad},${by + 48}H${C.pad + bw}M${C.pad + bw - 120},${by + 48}V${by + 96}` }, g);
    text(g, 'np-og-tb-label', C.pad + 16, by + 18, 'AUTHOR');
    text(g, 'np-og-byline', C.pad + 16, by + 38, 'NINAD PATHAK');
    text(g, 'np-og-tb-label', C.pad + 16, by + 66, 'READ');
    text(g, 'np-og-url', C.pad + 16, by + 85, card.meta['og-url'] || `ninadpathak.com/articles/${card.slug}/`);
    text(g, 'np-og-tb-label', C.pad + bw - 104, by + 66, 'REV');
    text(g, 'np-og-url', C.pad + bw - 104, by + 85, info.hash.slice(0, 7));
    el('rect', { class: 'np-frame', x: 0.5, y: 0.5, width: W - 1, height: H - 1 }, plate);
    return { width: W, height: H, scale: r2(scale) };
  };
})();
