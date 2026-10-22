#!/usr/bin/env node
// Keeps article embeds in step with the rendered figures. Each `<figure class="np-figure">`
// block in a post is matched to its figure by the zoom link and replaced with the embed
// markup from that figure's .json, so width, height, alt, and caption never go stale.
//
//   node embed.mjs           rewrite stale embeds in content/posts
//   node embed.mjs --check   list stale embeds and exit 1 if any
import { readFileSync, readdirSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const POSTS = path.join(ROOT, 'content/posts');
const check = process.argv.includes('--check');
const BLOCK = /<figure class="np-figure">[\s\S]*?<\/figure>/g;

let stale = 0;
for (const name of readdirSync(POSTS).filter((f) => f.endsWith('.md')).sort()) {
  const file = path.join(POSTS, name);
  const before = readFileSync(file, 'utf8');
  const after = before.replace(BLOCK, (block) => {
    const href = block.match(/class="np-figure-zoom" href="([^"]+)\.svg"/)?.[1];
    const json = href && path.join(ROOT, `${href}.json`);
    if (!json || !existsSync(json)) return block;
    const embed = JSON.parse(readFileSync(json, 'utf8')).embed;
    if (embed === block) return block;
    stale++;
    console.log(`${check ? 'stale' : 'updated'} ${name}: ${href}`);
    return embed;
  });
  if (!check && after !== before) writeFileSync(file, after);
}
if (check && stale) { console.error(`${stale} embed(s) differ from their figure; run node tools/image-brand/embed.mjs`); process.exit(1); }
