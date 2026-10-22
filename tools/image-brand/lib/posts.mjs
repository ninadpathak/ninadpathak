// Read the few post frontmatter fields the image pipeline needs (title, slug, category, status).
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { REPO_DIR } from './tokens.mjs';

export const KICKERS = { 'ai-engineering': 'AI engineering', 'technical-documentation': 'Technical documentation', 'developer-experience': 'Developer experience' };

export function frontmatter(file) {
  const m = readFileSync(file, 'utf8').match(/^---\n([\s\S]*?)\n---/);
  if (!m) return {};
  const out = {};
  const lines = m[1].split('\n');
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([a-z_]+):\s*(.*)$/);
    if (!kv) continue;
    let v = kv[2];
    while (i + 1 < lines.length && /^\s+\S/.test(lines[i + 1]) && !/^\s*-/.test(lines[i + 1])) v += ` ${lines[++i].trim()}`;
    if (/^'.*'$/.test(v)) v = v.slice(1, -1).replace(/''/g, "'");
    else if (/^".*"$/.test(v)) v = JSON.parse(v);
    out[kv[1]] = v;
  }
  return out;
}

export function publishedPosts() {
  const dir = path.join(REPO_DIR, 'content/posts');
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter((f) => f.endsWith('.md')).map((f) => ({ file: f, ...frontmatter(path.join(dir, f)) }))
    .filter((p) => p.status === 'published').map((p) => ({ ...p, slug: p.slug || p.file.replace(/\.md$/, '') }));
}
