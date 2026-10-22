// A figure source is plain Mermaid. Brand metadata rides in `%% @key value` comments,
// which Mermaid and Pele both ignore, so the file stays valid in any Mermaid tool.
import { readFileSync } from 'node:fs';
import path from 'node:path';

const LIST_KEYS = new Set(['path', 'glyph', 'dim', 'step', 'callout']);
const KNOWN = new Set([
  'kind', 'fig', 'kicker', 'alt', 'caption', 'path', 'glyph', 'ring', 'center', 'dim', 'step', 'parts',
  'callout', 'ratio', 'series', 'unit', 'legend', 'width', 'spacing', 'og-title', 'og-kicker', 'og-url',
]);
// v2 text components, removed in v3 (GUIDELINE.md §6). Their content belongs in the article.
const REMOVED = new Set(['note', 'detail', 'table', 'row', 'bar', 'timeline', 'index']);

// Glyphs drawn as a wide strip inside a layer slab (block diagrams); everything else is a tile.
export const STRIP_GLYPHS = new Set(['queue', 'sram', 'paged', 'quant', 'gpu']);
const TILE = { w: 56, h: 48 };
// Glyphs whose drawing is wider than the default tile.
const TILE_SIZES = { context: { w: 92, h: 48 } };
const STRIP = { w: 360, h: 46, label: 150 };

const split = (s, sep = '|') => s.split(sep).map((p) => p.trim());

function parseGlyph(spec, file) {
  const [id, rest = ''] = split(spec);
  const [name, ...tokens] = rest.split(/\s+/).filter(Boolean);
  if (!id || !name) throw new Error(`${file}: @glyph needs "id | name [options]"`);
  const opts = {};
  for (const t of tokens) {
    const [k, v] = t.split('=');
    if (v === undefined) {
      if (['lock', 'globe', 'question', 'check', 'cross', 'flag'].includes(k)) opts.badge = k;
      else opts[k] = true;
    } else opts[k] = /^[-\d.]+$/.test(v) ? Number(v) : v.includes(',') ? v.split(',').map(Number) : v;
  }
  const strip = STRIP_GLYPHS.has(name);
  const base = strip ? STRIP : TILE_SIZES[name] || TILE;
  const w = opts.w ?? base.w, h = opts.h ?? base.h;
  return { id, name, opts, strip, w, h, mode: opts.bare ? 'bare' : strip ? 'strip' : 'tile' };
}

export function parseSource(file) {
  const text = readFileSync(file, 'utf8');
  const meta = { path: [], glyph: [], dim: [], step: [], callout: [] };
  const body = [];
  for (const line of text.split('\n')) {
    const m = line.match(/^\s*%%\s*@([a-z-]+)\s*(.*)$/);
    if (!m) { body.push(line); continue; }
    const [, key, value] = m;
    if (REMOVED.has(key)) throw new Error(`${file}: @${key} was a v2 text component and is gone in v3; draw it or move it to the article`);
    if (!KNOWN.has(key)) throw new Error(`${file}: unknown directive @${key}`);
    if (LIST_KEYS.has(key)) meta[key].push(value.trim());
    else meta[key] = value.trim();
  }
  const slug = path.basename(path.dirname(file));
  const id = path.basename(file, '.mmd');
  meta.kind ??= 'diagram';
  if (meta.kind === 'diagram' && !meta.alt) throw new Error(`${file}: @alt is required`);
  if (meta.kind === 'og' && !meta['og-title']) throw new Error(`${file}: @og-title is required`);

  meta.hotEdges = meta.path.flatMap((p) => {
    const ids = split(p, '>');
    return ids.slice(1).map((to, i) => [ids[i], to]);
  });
  meta.glyphs = Object.fromEntries(meta.glyph.map((g) => { const x = parseGlyph(g, file); return [x.id, x]; }));
  meta.dims = meta.dim.map((d) => { const [from, to, label = ''] = split(d); return { from, to, label }; });
  meta.steps = Object.fromEntries(meta.step.map((s) => split(s)));
  meta.ringSpec = meta.ring ? { ids: split(split(meta.ring)[0], '>'), r: Number(split(meta.ring)[1] || 0) || null } : null;
  meta.centerGlyph = meta.center ? parseGlyph(`center | ${meta.center}`, file) : null;
  meta.partsSpec = meta.parts ? (() => {
    const [target, list] = split(meta.parts);
    return { target, parts: list.split(';').map((p) => p.trim()).filter(Boolean).map((p) => { const [phrase, node] = p.split('>').map((x) => x.trim()); return { phrase, node }; }) };
  })() : null;
  meta.callouts = meta.callout.map((c) => c.split(':').map(Number));
  meta.ratioAt = meta.ratio === undefined ? null : Number(meta.ratio);
  meta.seriesNames = meta.series ? split(meta.series, ';') : [];
  meta.spacingSpec = meta.spacing ? meta.spacing.split(',').map(Number) : null;

  let mermaid = body.join('\n').trim();
  for (const g of Object.values(meta.glyphs)) mermaid = injectGlyph(mermaid, g, file);
  return { file, slug, id, meta, mermaid };
}

// Reserve room for a glyph inside the node: placeholder lines that the measurer sizes to the
// glyph and the brand layer deletes before drawing. Tiles stack the glyph above the label;
// strips sit beside a label column inside a full-width slab.
function injectGlyph(src, g, file) {
  const re = new RegExp(`(^|[\\s;&])(${g.id.replace(/[-]/g, '\\-')})(\\[\\[|\\(\\[|\\[\\(|\\(\\(|\\[|\\(|\\{)("\`?)`, 'm');
  const m = src.match(re);
  if (!m || !m[4]) throw new Error(`${file}: @glyph target "${g.id}" must be defined with a quoted label, e.g. ${g.id}["Label"]`);
  const lines = g.mode === 'strip' ? Math.max(1, Math.ceil((g.h - 14) / 21)) : Math.ceil((g.h + 12) / 21);
  const w = g.mode === 'strip' ? g.w + STRIP.label : g.w + 16;
  const placeholder = Array.from({ length: lines }, () => `⟦g:${w}⟧`).join('\n') + '\n';
  const at = m.index + m[0].length;
  return src.slice(0, at) + placeholder + src.slice(at);
}

// Words that count against the budget: tokens with two or more letters.
export function countWords(text) {
  return text.split(/\s+/).filter((t) => (t.match(/[A-Za-z]/g) || []).length >= 2);
}
