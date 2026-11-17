#!/usr/bin/env node
// Topic icons for the Topics grid on /articles/.
//
//   node topics.mjs           write content/topic-glyphs.json
//   node topics.mjs --check   fail if that file is stale
//
// Each hub in config.toml names one icon (`glyph = "doc"`) from lib/topic-icons.mjs, the
// small line set drawn for the site's chrome. This writes one inline <svg> per hub.
// build.py puts that SVG inside the hub's box, and the .topic-glyph rule in
// static/css/main.css strokes it in the text colour, so it follows the light and dark
// themes with no image request.
//
// The article figures draw from lib/glyphs.js and never from this set, so nothing here
// feeds the figure pipeline's hash. No browser is involved and the output is the same on
// every machine.
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { assertFits, icons, iconSvg } from './lib/topic-icons.mjs';

const TOOL_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(TOOL_DIR, '../..');
const OUT = path.join(ROOT, 'content/topic-glyphs.json');

function hubs() {
  const blocks = readFileSync(path.join(ROOT, 'config.toml'), 'utf8').split('[[content.categories]]').slice(1);
  return blocks.map((block) => {
    const body = block.split(/^\[/m)[0];
    const field = (key) => body.match(new RegExp(`^${key} = "([^"]*)"`, 'm'))?.[1];
    return { slug: field('slug'), glyph: field('glyph') };
  });
}

const list = hubs();
for (const { slug, glyph } of list) {
  if (!glyph) throw new Error(`config.toml: hub ${slug} has no glyph`);
  if (!icons[glyph]) throw new Error(`config.toml: hub ${slug} names glyph "${glyph}", which lib/topic-icons.mjs does not define (it has: ${Object.keys(icons).join(', ')})`);
}
const used = list.map((hub) => hub.glyph);
const repeated = used.find((name, i) => used.indexOf(name) !== i);
if (repeated) throw new Error(`config.toml: glyph "${repeated}" is used by two hubs; each topic gets its own`);
// Runs for --check too, so CI stops on an icon that is clipped or out of line.
Object.keys(icons).forEach(assertFits);
const fresh = JSON.stringify(Object.fromEntries(list.map((hub) => [hub.slug, iconSvg(hub.glyph)])), null, 2) + '\n';

if (process.argv.includes('--check')) {
  let committed = '';
  try { committed = readFileSync(OUT, 'utf8'); } catch { /* reported below */ }
  if (committed !== fresh) {
    console.error('content/topic-glyphs.json is stale: run `node tools/image-brand/topics.mjs` and commit the result');
    process.exit(1);
  }
  console.log(`topic glyphs: ${list.length} current`);
} else {
  writeFileSync(OUT, fresh);
  console.log(`topic glyphs: wrote ${list.length} to ${path.relative(ROOT, OUT)} (${Buffer.byteLength(fresh)} bytes)`);
}
