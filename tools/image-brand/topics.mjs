#!/usr/bin/env node
// Topic glyphs for the Topics grid on /articles/.
//
//   node topics.mjs           write content/topic-glyphs.json
//   node topics.mjs --check   fail if that file is stale
//
// Each hub in config.toml names one tile glyph (`glyph = "doc"`, options as in @glyph).
// This draws it with lib/glyphs.js, the library every article figure uses, and writes one
// inline <svg> per hub. build.py puts that SVG inside the hub's box, and the `.gl-*` rules
// in static/css/main.css colour it from the site tokens, so it follows the light and dark
// themes with no image request.
//
// glyphs.js only creates elements and sets attributes, so a small stand-in for the DOM
// runs it here. No browser is involved and the output is the same on every machine.
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const TOOL_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(TOOL_DIR, '../..');
const OUT = path.join(ROOT, 'content/topic-glyphs.json');
const W = 56, H = 48; // the tile glyph box, GUIDELINE.md §7

const node = (name) => ({
  name, attrs: {}, children: [], text: '',
  setAttribute(k, v) { this.attrs[k] = String(v); },
  getAttribute(k) { return this.attrs[k]; },
  appendChild(child) { this.children.push(child); return child; },
  set textContent(value) { this.text = String(value); },
});
const sandbox = { document: { createElementNS: (_ns, name) => node(name) } };
sandbox.window = sandbox;
vm.runInNewContext(readFileSync(path.join(TOOL_DIR, 'lib/glyphs.js'), 'utf8'), sandbox);
const glyphs = sandbox.npGlyphs.tile;

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
const serialize = (n) => {
  const attrs = Object.entries(n.attrs).map(([k, v]) => ` ${k}="${esc(v)}"`).join('');
  const inner = n.children.map(serialize).join('') + esc(n.text);
  return inner ? `<${n.name}${attrs}>${inner}</${n.name}>` : `<${n.name}${attrs}/>`;
};

// `doc badge=check` -> ['doc', { badge: 'check' }]; a bare word is a flag.
function parseSpec(spec) {
  const [name, ...rest] = spec.trim().split(/\s+/);
  const opts = {};
  for (const token of rest) {
    const [key, value] = token.split('=');
    opts[key] = value === undefined ? true : /^-?\d+(\.\d+)?$/.test(value) ? Number(value) : value;
  }
  return [name, opts];
}

function hubs() {
  const blocks = readFileSync(path.join(ROOT, 'config.toml'), 'utf8').split('[[content.categories]]').slice(1);
  return blocks.map((block) => {
    const body = block.split(/^\[/m)[0];
    const field = (key) => body.match(new RegExp(`^${key} = "([^"]*)"`, 'm'))?.[1];
    return { slug: field('slug'), glyph: field('glyph') };
  });
}

function draw({ slug, glyph }) {
  if (!glyph) throw new Error(`config.toml: hub ${slug} has no glyph`);
  const [name, opts] = parseSpec(glyph);
  if (!glyphs[name]) throw new Error(`config.toml: hub ${slug} names glyph "${name}", which lib/glyphs.js does not define as a tile glyph`);
  const hatch = `topic-${slug}-hatch`;
  const svg = node('svg');
  for (const [k, v] of Object.entries({ class: 'topic-glyph', viewBox: `${-W / 2} ${-H / 2} ${W} ${H}`, width: W, height: H, 'aria-hidden': 'true', focusable: 'false' })) svg.setAttribute(k, v);
  const body = node('g');
  glyphs[name](body, W, H, { ...opts, accent: true, hatch });
  const markup = body.children.map(serialize).join('');
  // The 45° hatch of GUIDELINE.md §6, defined only for a glyph that uses it.
  const defs = markup.includes(`url(#${hatch})`)
    ? `<defs><pattern id="${hatch}" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><path class="np-hatch" d="M0,0V5"/></pattern></defs>`
    : '';
  return serialize(svg).replace('/>', `>${defs}${markup}</svg>`);
}

const list = hubs();
const used = list.map((hub) => parseSpec(hub.glyph || '')[0]);
const repeated = used.find((name, i) => used.indexOf(name) !== i);
if (repeated) throw new Error(`config.toml: glyph "${repeated}" is used by two hubs; each topic gets its own`);
const fresh = JSON.stringify(Object.fromEntries(list.map((hub) => [hub.slug, draw(hub)])), null, 2) + '\n';

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
