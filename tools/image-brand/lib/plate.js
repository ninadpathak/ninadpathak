/* Runs inside headless Chromium after pele.global.js and the brand fonts have loaded.
 * Pele lays the diagram out; this file restyles its SVG into the ninadpathak.com image
 * brand and composes the plate around it. Every coordinate here is a display pixel at
 * the 720 px article width; PNGs are exported at 2x.
 */
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const LEGEND_DEFAULTS = { accent: 'Primary step', focal: 'Focus', outcome: 'Outcome', muted: 'Optional', fail: 'Failure', pass: 'Pass', hot: 'Primary path' };
  const NODE_CLASSES = ['accent', 'focal', 'outcome', 'muted', 'fail', 'pass'];

  const el = (name, attrs = {}, parent) => {
    const node = document.createElementNS(NS, name);
    for (const [k, v] of Object.entries(attrs)) if (v !== undefined && v !== null) node.setAttribute(k, String(v));
    if (parent) parent.appendChild(node);
    return node;
  };
  const r2 = (n) => Math.round(n * 100) / 100;

  function makeMeasurer(T) {
    const ctx = document.createElement('canvas').getContext('2d');
    const role = T.type.roles;
    const font = (r, size) => `${r.weight} ${size ?? r.size}px '${r.family === 'mono' ? T.type.mono : T.type.sans}'`;
    return {
      width(text, size, style) {
        let t = text;
        let r = { ...role['node-label'], size };
        if (style & 1) r = { ...role['node-strong'], size };
        if (style & 4) r = { family: 'mono', weight: 400, size, tracking: '0' };
        if (t.startsWith('§')) { r = role['node-kicker']; t = t.slice(1).toUpperCase(); }
        else if (t.startsWith('~')) { r = role['node-detail']; t = t.slice(1); }
        ctx.font = font(r, r.size);
        ctx.letterSpacing = r.tracking && r.tracking !== '0' ? `${parseFloat(r.tracking) * r.size}px` : '0px';
        return ctx.measureText(t).width;
      },
    };
  }

  function parsePoints(d) {
    return [...d.matchAll(/(-?\d*\.?\d+),(-?\d*\.?\d+)/g)].map((m) => [Number(m[1]), Number(m[2])]);
  }

  // Restyle Pele's SVG in place. Returns facts the plate needs (classes in use, node boxes).
  function brandDiagram(svg, meta, T) {
    const used = new Set();
    svg.classList.add('np-diagram');
    svg.removeAttribute('width');
    svg.removeAttribute('height');

    const hotPrefixes = meta.hotEdges.map(([a, b]) => `L_${a}_${b}_`);
    if (hotPrefixes.length) used.add('hot');
    const ports = el('g', { class: 'np-ports' });

    // Edges: open chevrons that close on the node, a port ring where the edge leaves.
    for (const edge of svg.querySelectorAll('.pele-edge')) {
      const id = edge.getAttribute('data-id') || '';
      const hot = hotPrefixes.some((p) => id.startsWith(p));
      if (hot) edge.classList.add('np-hot');
      const [line, ...markers] = edge.querySelectorAll('path');
      for (const marker of markers) {
        if (!marker.classList.contains('pele-marker')) continue;
        const pts = parsePoints(marker.getAttribute('d'));
        if (pts.length !== 3) continue; // circle and cross markers keep Pele's shape
        const [tip, b1, b2] = pts;
        marker.setAttribute('d', `M${b1.join(',')}L${tip.join(',')}L${b2.join(',')}`);
        marker.setAttribute('fill', 'none');
        marker.removeAttribute('stroke');
        marker.classList.add('np-arrow');
        const lp = parsePoints(line.getAttribute('d'));
        const end = lp[lp.length - 1];
        const start = lp[0];
        const near = (p) => Math.hypot(p[0] - (b1[0] + b2[0]) / 2, p[1] - (b1[1] + b2[1]) / 2) < 2;
        if (near(end)) line.setAttribute('d', `${line.getAttribute('d')}L${tip.join(',')}`);
        else if (near(start)) line.setAttribute('d', line.getAttribute('d').replace(/^M[^LC]+/, `M${tip.join(',')}L${start.join(',')}`));
      }
      const lp = parsePoints(line.getAttribute('d'));
      const startsAtArrow = markers.some((m) => {
        const p = parsePoints(m.getAttribute('d'))[1];
        return p && Math.hypot(p[0] - lp[0][0], p[1] - lp[0][1]) < 6;
      });
      if (!startsAtArrow && lp.length) el('circle', { class: `np-port${hot ? ' np-port-hot' : ''}`, cx: lp[0][0], cy: lp[0][1], r: 2.25 }, ports);
    }
    svg.appendChild(ports);

    // Edge labels: mono caps on a canvas-colored mask, re-measured after restyling.
    for (const label of svg.querySelectorAll('.pele-edge-label')) {
      const text = label.querySelector('text');
      const rect = label.querySelector('rect');
      const id = label.getAttribute('data-id') || '';
      if (hotPrefixes.some((p) => id.startsWith(p))) label.classList.add('np-hot');
      text.textContent = text.textContent.toUpperCase();
      text.removeAttribute('font-size');
      label.parentNode.removeAttribute('font-size');
      text.setAttribute('dominant-baseline', 'central');
      const cy = Number(rect.getAttribute('y')) + Number(rect.getAttribute('height')) / 2;
      text.setAttribute('y', r2(cy));
      const box = text.getBBox();
      rect.setAttribute('x', r2(box.x - 6));
      rect.setAttribute('y', r2(cy - 8));
      rect.setAttribute('width', r2(box.width + 12));
      rect.setAttribute('height', 16);
      rect.setAttribute('rx', T.radius.label);
      rect.removeAttribute('fill');
    }

    // Clusters: dashed boundary, label lifted above the edges on a canvas mask with an
    // accent tick. `ghost` clusters exist only to steer layout and draw nothing.
    const clusterLabels = el('g', { class: 'np-cluster-labels' });
    for (const cluster of svg.querySelectorAll('.pele-cluster')) {
      const rect = cluster.querySelector('rect');
      const label = cluster.querySelector('.pele-cluster-label');
      rect.removeAttribute('fill');
      rect.removeAttribute('fill-opacity');
      rect.removeAttribute('stroke');
      if (cluster.classList.contains('ghost')) { label?.remove(); continue; }
      const blank = !label || !label.textContent.trim();
      if (blank) { label?.remove(); continue; }
      const x = Number(rect.getAttribute('x'));
      const y = Number(rect.getAttribute('y'));
      const g = el('g', { class: 'np-cluster-head' }, clusterLabels);
      const mask = el('rect', { class: 'np-cluster-mask', rx: T.radius.label }, g);
      const wash = el('rect', { class: 'np-cluster-mask-wash', rx: T.radius.label }, g);
      el('rect', { class: 'np-cluster-tick', x: x + 10, y: y + 10, width: 4, height: 4 }, g);
      label.textContent = label.textContent.toUpperCase();
      label.setAttribute('x', x + 20);
      label.setAttribute('y', y + 17);
      label.setAttribute('text-anchor', 'start');
      label.removeAttribute('fill');
      g.appendChild(label);
    }
    // Nodes: typographic roles per line, card alignment, class treatments.
    let index = 0;
    for (const node of svg.querySelectorAll('.pele-node')) {
      const shape = node.querySelector('rect, polygon, path, circle, ellipse');
      const label = node.querySelector('.pele-label');
      for (const c of NODE_CLASSES) if (node.classList.contains(c)) used.add(c);
      if (shape) {
        for (const s of node.querySelectorAll(':scope > rect, :scope > polygon, :scope > path, :scope > circle, :scope > ellipse')) {
          s.removeAttribute('fill');
          s.removeAttribute('stroke');
          s.classList.add('np-shape');
        }
      }
      let hasKicker = false;
      if (label) {
        const lines = label.querySelectorAll('tspan[x]').length ? [...label.querySelectorAll('tspan[x]')] : [label];
        let inDetail = false;
        for (const line of lines) {
          const t = line.textContent;
          if (inDetail) { line.classList.add('np-detail'); continue; }
          if (t.startsWith('§')) { line.textContent = t.slice(1).toUpperCase(); line.classList.add('np-kicker'); hasKicker = true; }
          else if (t.startsWith('~')) { line.textContent = t.slice(1); line.classList.add('np-detail'); inDetail = true; }
        }
        if (hasKicker && shape && shape.tagName === 'rect') {
          const x = Number(shape.getAttribute('x'));
          const w = Number(shape.getAttribute('width'));
          const textW = Math.max(...lines.map((l) => l.getComputedTextLength()));
          const pad = Math.min(16, (w - textW) / 2);
          label.setAttribute('text-anchor', 'start');
          for (const line of lines) line.setAttribute('x', r2(x + pad));
          node.classList.add('np-card');
        }
      }
      // A 3px rule across the top of the card, clipped to the card's rounded corners.
      const ruled = ['accent', 'fail', 'pass'].find((c) => node.classList.contains(c));
      if (ruled && shape && shape.tagName === 'rect') {
        const x = Number(shape.getAttribute('x')), y = Number(shape.getAttribute('y')), w = Number(shape.getAttribute('width'));
        const rr = T.radius.node, h = T.stroke['accent-rule'];
        el('path', { class: 'np-rule', d: `M${x},${y + h}V${y + rr}A${rr},${rr} 0 0 1 ${x + rr},${y}H${x + w - rr}A${rr},${rr} 0 0 1 ${x + w},${y + rr}V${y + h}Z` }, node);
      }
      index += 1;
      if (meta.index === 'on' && shape) {
        const b = shape.getBBox();
        const tag = el('text', { class: 'np-index', x: r2(b.x), y: r2(b.y - 5) }, node);
        tag.textContent = String(index).padStart(2, '0');
      }
    }
    svg.appendChild(clusterLabels);
    for (const head of clusterLabels.querySelectorAll('.np-cluster-head')) {
      const b = head.querySelector('text').getBBox();
      for (const m of head.querySelectorAll('.np-cluster-mask, .np-cluster-mask-wash')) {
        m.setAttribute('x', r2(b.x - 16)); m.setAttribute('y', r2(b.y - 3));
        m.setAttribute('width', r2(b.width + 22)); m.setAttribute('height', r2(b.height + 6));
      }
    }
    return { used };
  }

  function nodeBox(svg, id) {
    const node = svg.querySelector(`.pele-node[data-id="${CSS.escape(id)}"]`);
    if (!node) throw new Error(`@note target "${id}" is not a node id`);
    const shape = node.querySelector('.np-shape') || node;
    const b = shape.getBBox();
    const m = (node.getAttribute('transform') || '').match(/translate\(([-\d.]+),([-\d.]+)\)/);
    const [tx, ty] = m ? [Number(m[1]), Number(m[2])] : [0, 0];
    return { x: b.x + tx, y: b.y + ty, width: b.width, height: b.height };
  }

  function texture(parent, x, y, w, h, T, idPrefix) {
    const grid = T.canvas.article.grid;
    const defs = el('defs', {}, parent);
    const pat = el('pattern', { id: `${idPrefix}-grid`, width: grid, height: grid, patternUnits: 'userSpaceOnUse', x, y }, defs);
    el('circle', { class: 'np-grid-dot', cx: grid / 2, cy: grid / 2, r: 0.75 }, pat);
    el('rect', { class: 'np-field', x, y, width: w, height: h, fill: `url(#${idPrefix}-grid)` }, parent);
    // Drafting ruler along the field's top and left edges: 8 px minor, 40 px major.
    let d = '';
    for (let i = 0; x + i <= x + w; i += 8) d += `M${x + i},${y}v${i % 40 === 0 ? 6 : 3}`;
    for (let i = 0; y + i <= y + h; i += 8) d += `M${x},${y + i}h${i % 40 === 0 ? 6 : 3}`;
    el('path', { class: 'np-ruler', d }, parent);
    // Crop marks at the four inner corners of the field.
    const ci = 14, arm = 8;
    const corners = [[x + ci, y + ci, 1, 1], [x + w - ci, y + ci, -1, 1], [x + ci, y + h - ci, 1, -1], [x + w - ci, y + h - ci, -1, -1]];
    el('path', { class: 'np-crop', d: corners.map(([cx, cy, sx, sy]) => `M${cx},${cy + sy * arm}V${cy}H${cx + sx * arm}`).join('') }, parent);
  }

  function kickerText(parent, x, y, text, cls, anchor = 'start') {
    const t = el('text', { class: cls, x, y, 'text-anchor': anchor }, parent);
    const slash = el('tspan', { class: 'np-slash' }, t);
    slash.textContent = '// ';
    t.appendChild(document.createTextNode(text.toUpperCase()));
    return t;
  }

  function placeDiagram(plate, src, opts, T) {
    const host = el('g', {}, plate);
    const result = window.pele.render(src.mermaid, {
      measurer: makeMeasurer(T), fontFamily: T.type.sans, fontFamilyMono: T.type.mono, fontSize: 14,
      responsive: false, autoDirection: false, padding: 8, idPrefix: src.id, maxWidth: opts.maxWidth, links: false, images: false,
      config: { flowchart: { nodeSpacing: T.layout.nodeSpacing } },
    });
    host.innerHTML = result.svg;
    const svg = host.querySelector('svg');
    const facts = brandDiagram(svg, src.meta, T);
    return { host, svg, facts };
  }

  function legend(parent, used, meta, x, y) {
    const overrides = Object.fromEntries((meta.legend || '').split(';').filter(Boolean).map((p) => p.split('=').map((s) => s.trim())));
    if (meta.legend === 'off') return;
    const items = [...used].filter((c) => (overrides[c] ?? LEGEND_DEFAULTS[c]) && overrides[c] !== 'off');
    if (!items.length) return;
    let cx = x;
    for (const c of items) {
      const g = el('g', { class: `np-legend-item np-legend-${c}` }, parent);
      if (c === 'hot') {
        el('path', { class: 'np-legend-line', d: `M${cx},${y - 3.5}h14` }, g);
        el('circle', { class: 'np-port np-legend-port', cx, cy: y - 3.5, r: 2.25 }, g);
      } else {
        el('rect', { class: `np-swatch np-swatch-${c}`, x: cx, y: y - 8.5, width: 14, height: 10, rx: 2 }, g);
        if (['accent', 'fail', 'pass'].includes(c)) el('rect', { class: `np-swatch-rule np-swatch-rule-${c}`, x: cx, y: y - 8.5, width: 14, height: 2.5 }, g);
      }
      const t = el('text', { class: 'np-legend', x: cx + 20, y }, g);
      t.textContent = (overrides[c] ?? LEGEND_DEFAULTS[c]).toUpperCase();
      cx += 20 + t.getComputedTextLength() + 18;
    }
  }

  // Article figure: head band, textured field with the diagram, optional notes, foot band.
  window.npComposeArticle = (src, T) => {
    const C = T.canvas.article;
    const W = Number(src.meta.width || C.width);
    const plate = el('svg', { xmlns: NS, class: `np-plate np-kind-article`, viewBox: `0 0 ${W} 100`, width: W, height: 100, role: 'img' }, document.body);
    const style = el('style', {}, plate);
    style.textContent = '/*NP-STYLE*/';
    const title = el('title', { id: `${src.id}-title` }, plate);
    title.textContent = src.meta.kicker || src.id;
    const desc = el('desc', { id: `${src.id}-desc` }, plate);
    desc.textContent = src.meta.alt;
    plate.setAttribute('aria-labelledby', `${src.id}-title ${src.id}-desc`);

    const bg = el('rect', { class: 'np-canvas', x: 0, y: 0, width: W, height: 100 }, plate);
    const fieldLayer = el('g', { class: 'np-texture' }, plate);
    const { host, svg, facts } = placeDiagram(plate, src, { maxWidth: W - 2 * C.pad }, T);
    const vb = svg.viewBox.baseVal;
    const avail = W - 2 * C.pad;
    const s = Math.min(1, avail / vb.width);
    if (s < C.minScale) throw new Error(`${src.id}: diagram is ${Math.round(vb.width)} px wide and would shrink to ${Math.round(s * 100)}%. Split it or change direction.`);
    const dw = vb.width * s, dh = vb.height * s;
    const fieldTop = C.head;
    const dx = (W - dw) / 2, dy = fieldTop + C.pad;
    svg.setAttribute('x', r2(dx)); svg.setAttribute('y', r2(dy));
    svg.setAttribute('width', r2(dw)); svg.setAttribute('height', r2(dh));
    const fieldH = Math.ceil((C.pad * 2 + dh) / 8) * 8;

    // Callouts: a numbered badge pinned to the target's top-right corner.
    const notesLayer = el('g', { class: 'np-notes' }, plate);
    src.meta.notes.forEach((note, i) => {
      const b = nodeBox(svg, note.target);
      const cx = dx + (b.x + b.width) * s, cy = dy + b.y * s;
      el('circle', { class: 'np-badge', cx: r2(cx), cy: r2(cy), r: 8.5 }, notesLayer);
      const n = el('text', { class: 'np-badge-num', x: r2(cx), y: r2(cy), 'text-anchor': 'middle', 'dominant-baseline': 'central' }, notesLayer);
      n.textContent = String(i + 1);
    });

    let y = fieldTop + fieldH;
    texture(fieldLayer, 0.5, fieldTop, W - 1, fieldH, T, src.id);

    // Notes list under the field, one row per callout.
    if (src.meta.notes.length) {
      el('path', { class: 'np-sep', d: `M0,${y}H${W}` }, plate);
      y += 22;
      src.meta.notes.forEach((note, i) => {
        el('circle', { class: 'np-badge', cx: 28.5, cy: y - 4, r: 8.5 }, plate);
        const n = el('text', { class: 'np-badge-num', x: 28.5, y: y - 4, 'text-anchor': 'middle', 'dominant-baseline': 'central' }, plate);
        n.textContent = String(i + 1);
        const t = el('text', { class: 'np-note', x: 46, y }, plate);
        t.textContent = note.text;
        if (t.getComputedTextLength() > W - 66) throw new Error(`${src.id}: note ${i + 1} is too long for one line`);
        y += 24;
      });
      y += 2;
    }

    // Head band.
    kickerText(plate, 20, 27, src.meta.kicker || src.id, 'np-head-kicker');
    const meta = el('text', { class: 'np-head-meta', x: W - 20, y: 27, 'text-anchor': 'end' }, plate);
    meta.textContent = src.meta.fig ? `FIG. ${src.meta.fig}` : src.slug.toUpperCase();
    el('path', { class: 'np-sep', d: `M0,${C.head}H${W}` }, plate);

    // Foot band.
    el('path', { class: 'np-sep', d: `M0,${y}H${W}` }, plate);
    legend(plate, facts.used, src.meta, 20, y + 22);
    const site = el('text', { class: 'np-foot-meta', x: W - 20, y: y + 22, 'text-anchor': 'end' }, plate);
    site.textContent = 'NINADPATHAK.COM';
    const H = Math.ceil((y + C.foot) / 4) * 4;

    bg.setAttribute('height', H);
    el('rect', { class: 'np-frame', x: 0.5, y: 0.5, width: W - 1, height: H - 1, rx: T.radius.plate }, plate);
    plate.setAttribute('viewBox', `0 0 ${W} ${H}`);
    plate.setAttribute('height', H);
    return { width: W, height: H, scale: r2(s) };
  };

  // Share card: 1200x630, title left, the article's diagram on a drafting field right.
  window.npComposeOg = (card, src, T) => {
    const C = T.canvas.og;
    const W = C.width, H = C.height;
    const plate = el('svg', { xmlns: NS, class: 'np-plate np-kind-og np-light', viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img' }, document.body);
    const style = el('style', {}, plate);
    style.textContent = '/*NP-STYLE*/';
    const title = el('title', {}, plate);
    title.textContent = card.meta['og-title'];
    el('rect', { class: 'np-canvas', x: 0, y: 0, width: W, height: H }, plate);
    el('rect', { class: 'np-og-rule', x: 0, y: 0, width: W, height: 4 }, plate);

    const fx = 676, fy = 64, fw = W - fx - 48, fh = H - 128;
    el('rect', { class: 'np-og-panel', x: fx, y: fy, width: fw, height: fh, rx: 4 }, plate);
    texture(el('g', {}, plate), fx, fy, fw, fh, T, 'og');
    const { svg } = placeDiagram(plate, src, { maxWidth: fw - 64 }, T);
    const vb = svg.viewBox.baseVal;
    const s = Math.min(1.35, (fw - 64) / vb.width, (fh - 64) / vb.height);
    const dw = vb.width * s, dh = vb.height * s;
    svg.setAttribute('x', r2(fx + (fw - dw) / 2)); svg.setAttribute('y', r2(fy + (fh - dh) / 2));
    svg.setAttribute('width', r2(dw)); svg.setAttribute('height', r2(dh));

    kickerText(plate, C.pad, 112, card.meta['og-kicker'] || 'Article', 'np-og-kicker');
    // Title: greedy line breaks measured with the real font, at most four lines.
    const roleT = T.type.roles['og-title'];
    const maxW = fx - C.pad - 48;
    const words = card.meta['og-title'].split(/\s+/);
    const probe = el('text', { class: 'np-og-title' }, plate);
    const lines = [];
    let cur = '';
    for (const w of words) {
      const next = cur ? `${cur} ${w}` : w;
      probe.textContent = next;
      if (probe.getComputedTextLength() > maxW && cur) { lines.push(cur); cur = w; } else cur = next;
    }
    lines.push(cur);
    probe.remove();
    if (lines.length > 4) throw new Error(`og title wraps to ${lines.length} lines; the limit is 4`);
    const lh = roleT.size * roleT.leading;
    const t = el('text', { class: 'np-og-title', x: C.pad, y: 112 + 36 + roleT.size }, plate);
    lines.forEach((line, i) => {
      const span = el('tspan', { x: C.pad, dy: i === 0 ? 0 : r2(lh) }, t);
      span.textContent = line;
    });
    el('path', { class: 'np-sep', d: `M${C.pad},${H - 112}H${fx - 48}` }, plate);
    const by = el('text', { class: 'np-og-byline', x: C.pad, y: H - 76 }, plate);
    by.textContent = 'NINAD PATHAK';
    const url = el('text', { class: 'np-og-url', x: C.pad, y: H - 52 }, plate);
    url.textContent = card.meta['og-url'] || `ninadpathak.com/articles/${card.slug}/`;
    el('rect', { class: 'np-frame', x: 0.5, y: 0.5, width: W - 1, height: H - 1 }, plate);
    return { width: W, height: H, scale: r2(s) };
  };
})();
