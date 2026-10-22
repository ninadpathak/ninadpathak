// A figure source is plain Mermaid. Brand metadata rides in `%% @key value` comments,
// which Mermaid and Pele both ignore, so the file stays valid in any Mermaid tool.
import { readFileSync } from 'node:fs';
import path from 'node:path';

const LIST_KEYS = new Set(['note', 'path', 'dim', 'detail', 'row']);
const KNOWN = new Set([
  'kind', 'fig', 'kicker', 'alt', 'caption', 'path', 'note', 'index', 'width', 'legend',
  'og-title', 'og-kicker', 'og-url', 'dim', 'detail', 'table', 'row', 'bar', 'timeline', 'series', 'unit',
]);

// Per-figure budget for annotation components (GUIDELINE.md §9). Exceeding it is an error,
// so density stays a decision rather than an accident.
export const BUDGET = { note: 2, dim: 2, detail: 2, table: 1, timeline: 1, rows: 8 };

const split = (s, sep = '|') => s.split(sep).map((p) => p.trim());

export function parseSource(file) {
  const text = readFileSync(file, 'utf8');
  const meta = { note: [], path: [], dim: [], detail: [], row: [] };
  const body = [];
  for (const line of text.split('\n')) {
    const m = line.match(/^\s*%%\s*@([a-z-]+)\s*(.*)$/);
    if (!m) { body.push(line); continue; }
    const [, key, value] = m;
    if (!KNOWN.has(key)) throw new Error(`${file}: unknown directive @${key}`);
    if (LIST_KEYS.has(key)) meta[key].push(value.trim());
    else meta[key] = value.trim();
  }
  const slug = path.basename(path.dirname(file));
  const id = path.basename(file, '.mmd');
  meta.kind ??= 'diagram';
  if (meta.kind === 'diagram' && !meta.alt) throw new Error(`${file}: @alt is required`);
  if (meta.kind === 'og' && !meta['og-title']) throw new Error(`${file}: @og-title is required`);

  meta.notes = meta.note.map((n) => {
    const [target, ...rest] = split(n);
    return { target, text: rest.join(' | ') };
  });
  // `@path a>b>c` marks the primary route; every consecutive pair becomes a hot edge.
  meta.hotEdges = meta.path.flatMap((p) => {
    const ids = split(p, '>');
    return ids.slice(1).map((to, i) => [ids[i], to]);
  });
  meta.dims = meta.dim.map((d) => {
    const [from, to, label] = split(d);
    return { from, to, label };
  });
  meta.details = meta.detail.map((d) => {
    const [target, title, rows = ''] = split(d);
    return { target, title, rows: rows.split(';').map((r) => r.trim()).filter(Boolean).map((r) => {
      const i = r.indexOf(':');
      return i < 0 ? [r, ''] : [r.slice(0, i).trim(), r.slice(i + 1).trim()];
    }) };
  });
  if (meta.table) {
    const [title, ...columns] = split(meta.table);
    meta.tableSpec = { title, columns, rows: meta.row.map((r) => split(r)), bar: meta.bar === undefined ? null : Number(meta.bar) };
    for (const r of meta.tableSpec.rows) if (r.length !== columns.length) throw new Error(`${file}: @row "${r.join(' | ')}" has ${r.length} cells, table has ${columns.length}`);
  }
  if (meta.timeline) {
    const [steps, mode = 'line', returnLabel = ''] = split(meta.timeline);
    meta.timelineSpec = { steps: split(steps, '>'), loop: mode === 'loop', returnLabel };
  }
  meta.seriesNames = meta.series ? split(meta.series, ';') : [];

  const over = [
    ['note', meta.notes.length], ['dim', meta.dims.length], ['detail', meta.details.length],
    ['table', meta.tableSpec ? 1 : 0], ['timeline', meta.timelineSpec ? 1 : 0], ['rows', meta.row.length],
  ].filter(([k, n]) => n > BUDGET[k]);
  if (over.length) throw new Error(`${file}: over the component budget: ${over.map(([k, n]) => `${n} ${k} (max ${BUDGET[k]})`).join(', ')}`);

  const mermaid = body.join('\n').trim();
  const direction = (mermaid.match(/^(?:flowchart|graph)\s+(TB|TD|BT|LR|RL)/m) || [])[1] || null;
  return { file, slug, id, meta, direction, mermaid: mermaid ? prepareMermaid(mermaid) : '' };
}

// Kicker lines (`§`) must not wrap: Pele measures a line whole before splitting it at
// spaces, so non-breaking spaces keep the kicker one run. Detail lines (`~`) may wrap;
// every line after the first `~` line is styled as detail.
function prepareMermaid(src) {
  return src.replace(/(^\s*|\["`?)([§~])([^\n"`]*)/gm, (_, lead, mark, rest) => {
    if (mark === '~' && rest.length > 64) throw new Error(`detail line over 64 characters: "${rest}"`);
    return lead + mark + (mark === '§' ? rest.replace(/ /g, ' ') : rest);
  });
}
