// A figure source is plain Mermaid. Brand metadata rides in `%% @key value` comments,
// which Mermaid and Pele both ignore, so the file stays valid in any Mermaid tool.
import { readFileSync } from 'node:fs';
import path from 'node:path';

const LIST_KEYS = new Set(['note', 'path']);
const KNOWN = new Set(['kind', 'fig', 'kicker', 'alt', 'caption', 'path', 'note', 'index', 'width', 'diagram', 'og-title', 'og-kicker', 'og-url', 'legend']);

export function parseSource(file) {
  const text = readFileSync(file, 'utf8');
  const meta = { note: [], path: [] };
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
    const [target, ...rest] = n.split('|');
    return { target: target.trim(), text: rest.join('|').trim() };
  });
  // `@path a>b>c` marks the primary route; every consecutive pair becomes a hot edge.
  meta.hotEdges = meta.path.flatMap((p) => {
    const ids = p.split('>').map((s) => s.trim());
    return ids.slice(1).map((to, i) => [ids[i], to]);
  });
  return { file, slug, id, meta, mermaid: prepareMermaid(body.join('\n').trim()) };
}

// Kicker lines (`§`) must not wrap: Pele measures a line whole before splitting it at
// spaces, so non-breaking spaces keep the kicker one run. Detail lines (`~`) may wrap;
// every line after the first `~` line is styled as detail.
function prepareMermaid(src) {
  return src.replace(/(^\s*|\["`?)([§~])([^\n"`]*)/gm, (_, lead, mark, rest) => {
    if (mark === '~' && rest.length > 64) throw new Error(`detail line over 64 characters: "${rest}"`);
    return lead + mark + (mark === '§' ? rest.replace(/ /g, '\u00a0') : rest);
  });
}
