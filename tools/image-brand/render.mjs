#!/usr/bin/env node
// Render article figures from Mermaid source into the ninadpathak.com image brand.
//
//   node render.mjs                      render every content/diagrams/<slug>/<id>.mmd
//   node render.mjs path/to/one.mmd      render selected sources
//   node render.mjs --check              fail if any committed output is stale, a contrast
//                                        pair breaks AA, or a source is invalid
//   node render.mjs --out DIR            write somewhere other than static/images/diagrams
//
// Output per figure: <id>.svg (light/dark via prefers-color-scheme, fonts embedded),
// <id>.light.png and <id>.dark.png at 2x, and <id>.json with alt text and embed markup.
// Share cards (`@kind og`) write <id>.svg and a 1200x630 <id>.png from their own small diagram.
import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import path from 'node:path';
import { chromium } from 'playwright-core';
import subsetFont from 'subset-font';
import { loadTokens, contrastReport, siteDrift, themeCss, TOOL_DIR, REPO_DIR } from './lib/tokens.mjs';
import { parseSource, countWords } from './lib/source.mjs';
import { publishedPosts, KICKERS } from './lib/posts.mjs';

const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
const CHECK = args.includes('--check');
const outIdx = args.indexOf('--out');
const OUT_ROOT = outIdx >= 0 ? path.resolve(args[outIdx + 1]) : path.join(REPO_DIR, 'static/images/diagrams');
const SRC_ROOT = path.join(REPO_DIR, 'content/diagrams');
const explicit = args.filter((a, i) => a.endsWith('.mmd') && args[i - 1] !== '--out').map((a) => path.resolve(a));

const FACES = [
  ['Inter', 400, '@fontsource/inter/files/inter-latin-400-normal.woff2'],
  ['Inter', 500, '@fontsource/inter/files/inter-latin-500-normal.woff2'],
  ['Inter', 600, '@fontsource/inter/files/inter-latin-600-normal.woff2'],
  ['Inter', 700, '@fontsource/inter/files/inter-latin-700-normal.woff2'],
  ['JetBrains Mono', 400, '@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2'],
  ['JetBrains Mono', 500, '@fontsource/jetbrains-mono/files/jetbrains-mono-latin-500-normal.woff2'],
  ['JetBrains Mono', 600, '@fontsource/jetbrains-mono/files/jetbrains-mono-latin-600-normal.woff2'],
].map(([family, weight, mod]) => ({ family, weight, buffer: readFileSync(require.resolve(mod)) }));

const tokens = loadTokens();
const brandCss = readFileSync(path.join(TOOL_DIR, 'theme/brand.css'), 'utf8');
const plateJs = readFileSync(path.join(TOOL_DIR, 'lib/plate.js'), 'utf8');
const glyphsJs = readFileSync(path.join(TOOL_DIR, 'lib/glyphs.js'), 'utf8');
const peleJs = readFileSync(path.join(TOOL_DIR, 'node_modules/pele/dist/pele.global.js'), 'utf8');
const peleVersion = JSON.parse(readFileSync(path.join(TOOL_DIR, 'node_modules/pele/package.json'), 'utf8')).version;
const css = themeCss(tokens) + brandCss;
// Everything that shapes the output goes into each figure's hash: the pipeline code, the
// tokens and theme, and the locked dependency versions (Pele, fonts, subset-font, and
// playwright-core, which pins the Chromium build).
const PIPELINE = ['render.mjs', 'lib/plate.js', 'lib/glyphs.js', 'lib/source.mjs', 'lib/tokens.mjs', 'lib/posts.mjs', 'theme/brand.css', 'brand.tokens.json', 'package-lock.json']
  .map((f) => readFileSync(path.join(TOOL_DIR, f), 'utf8')).join('\0');
const posts = new Map(publishedPosts().map((p) => [p.slug, p]));

// A share card's title, kicker, and URL come from the post itself at render time, so a
// retitle never edits the hashed source. A pending post (not on this branch yet) carries
// them in its og.mmd.
const pendingCards = JSON.parse(readFileSync(path.join(TOOL_DIR, 'og-cards.json'), 'utf8')).$pending || {};
function resolveCard(src) {
  const post = posts.get(src.slug) || (pendingCards[src.slug] && { slug: src.slug, ...pendingCards[src.slug] });
  if (post) {
    src.meta['og-title'] = post.title;
    src.meta['og-kicker'] = KICKERS[post.category] || src.meta['og-kicker'] || 'Article';
    src.meta['og-url'] = `ninadpathak.com/articles/${post.slug}/`;
  }
  if (!src.meta['og-title']) throw new Error('share card has no published post and no @og-title');
  return src;
}

// Committed and fresh SVGs must match token for token; numbers may differ by half a pixel
// so a different Chromium build's text metrics do not fail CI.
function svgDiff(a, b, tol = 0.5) {
  const A = a.split(/(-?\d+(?:\.\d+)?)/), B = b.split(/(-?\d+(?:\.\d+)?)/);
  let maxDelta = 0, first = null, count = 0;
  const n = Math.min(A.length, B.length);
  for (let i = 0; i < n; i++) {
    const bad = i % 2 ? Math.abs(Number(A[i]) - Number(B[i])) > tol : A[i] !== B[i];
    if (i % 2) maxDelta = Math.max(maxDelta, Math.abs(Number(A[i]) - Number(B[i])) || 0);
    if (bad) { count += 1; if (!first) first = `committed "${A.slice(Math.max(0, i - 3), i + 2).join('').slice(-90)}" vs fresh "${B.slice(Math.max(0, i - 3), i + 2).join('').slice(-90)}"`; }
  }
  if (A.length !== B.length) { count += 1; first = first || `token count ${A.length} vs ${B.length}`; }
  return { same: count === 0, count, first, maxDelta: Math.round(maxDelta * 100) / 100 };
}
const sameSvg = (a, b) => svgDiff(a, b).same;
const minify = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\s*\n\s*/g, '').replace(/\s*([{};:,])\s*/g, '$1').trim();

function findSources() {
  if (explicit.length) return explicit;
  if (!existsSync(SRC_ROOT)) return [];
  return readdirSync(SRC_ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .flatMap((d) => readdirSync(path.join(SRC_ROOT, d.name)).filter((f) => f.endsWith('.mmd')).map((f) => path.join(SRC_ROOT, d.name, f)))
    .sort();
}

const fontFaceCss = (faces) => faces.map((f) => `@font-face{font-family:'${f.family}';font-weight:${f.weight};font-style:normal;src:url(data:font/woff2;base64,${f.buffer.toString('base64')}) format('woff2')}`).join('');

async function embedFonts(text) {
  const chars = [...new Set(text)].sort().join('');
  const faces = [];
  for (const f of FACES) {
    faces.push({ ...f, buffer: await subsetFont(f.buffer, chars, { targetFormat: 'woff2' }) });
  }
  return fontFaceCss(faces);
}

// Breakpoint below which a figure with a narrow variant swaps to it (GUIDELINE.md §14a).
// The wide plate keeps 13 px labels at >=12 px down to a ~665 px column, which the site
// reaches at a 712 px viewport; below that the phone variant takes over.
const NARROW_MEDIA = '(max-width: 712px)';

function embedSnippet(src, rel, dims, narrowVariant) {
  const caption = src.meta.caption ? `\n  <figcaption>${src.meta.caption}</figcaption>` : '';
  const img = `<img${narrowVariant ? ' class="np-has-narrow"' : ''} src="${rel}.svg" width="${dims.width}" height="${dims.height}" alt="${src.meta.alt.replace(/"/g, '&quot;')}" loading="lazy" decoding="async">`;
  const picture = narrowVariant ? `<picture><source media="${NARROW_MEDIA}" srcset="${narrowVariant.rel}.svg" width="${narrowVariant.width}" height="${narrowVariant.height}">${img}</picture>` : img;
  return `<figure class="np-figure">
  <a class="np-figure-zoom" href="${rel}.svg">${picture}</a>${caption}
</figure>`;
}

async function main() {
  const failures = [];
  const contrast = contrastReport(tokens).filter((r) => !r.ok);
  for (const r of contrast) failures.push(`contrast: ${r.scheme} ${r.fg} on ${r.bg} is ${r.ratio}, needs ${r.min} (${r.use})`);
  for (const d of siteDrift(tokens)) console.warn(`drift: ${d.scheme} ${d.token} is ${d.image}; site ${d.site} is ${d.live}`);

  const files = findSources();
  if (!files.length) { console.log('no sources'); return failures; }
  // Narrow variants render first so the wide figure's embed can include them.
  const parsed = files.map(parseSource);
  // Every article figure gets a phone variant. A hand-written <id>.narrow.mmd wins; otherwise
  // one is derived from the source: 288 px wide, left-to-right flows turned top-to-bottom,
  // rings tightened. A derived variant that doesn't fit at 1:1 is skipped with a warning.
  const handNarrow = new Set(parsed.filter((p) => p.id.endsWith('.narrow')).map((p) => `${p.slug}/${p.id.replace(/\.narrow$/, '')}`));
  const derived = parsed.filter((p) => p.meta.kind === 'diagram' && !p.id.endsWith('.narrow') && !handNarrow.has(`${p.slug}/${p.id}`)).map((p) => {
    const d = JSON.parse(JSON.stringify(p));
    d.id = `${p.id}.narrow`;
    d.derived = true;
    d.meta.width = '288';
    d.mermaid = p.mermaid.replace(/^(flowchart|graph)\s+(LR|RL)/m, '$1 TB').replace(/direction (LR|RL)/g, 'direction TB');
    // Block diagrams collapse to one column; spans no longer apply.
    if (/^block(-beta)?/m.test(d.mermaid)) d.mermaid = d.mermaid.replace(/^(\s*)columns \d+/m, '$1columns 1').replace(/(\])\s*:\d+/g, '$1');
    // A ring is too wide for a phone: lay the loop out as a column; the router draws the return.
    if (d.meta.ringSpec) { d.meta.ringSpec = null; d.meta.centerGlyph = null; }
    // Strip glyphs in a narrow slab sit under their label instead of beside it.
    for (const g of Object.values(d.meta.glyphs)) {
      if (g.mode !== 'strip') continue;
      d.mermaid = d.mermaid.split(`⟦g:${g.w + 150}⟧`).join('⟦g:220⟧');
      g.opts.stacked = true;
      g.w = 220;
    }
    return d;
  });
  const sources = [...parsed, ...derived].sort((a, b) => (b.id.endsWith('.narrow') - a.id.endsWith('.narrow')) || a.file.localeCompare(b.file) || a.id.localeCompare(b.id));
  const narrow = new Map();

  // Unhinted font metrics on every platform: Linux Chromium otherwise rounds glyph
  // advances, which moves text-measured geometry by 1-16 px against a macOS render.
  const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
  const page = await (await browser.newContext({ deviceScaleFactor: 1 })).newPage();
  await page.setContent(`<!doctype html><html><head><style>${fontFaceCss(FACES)}${css}body{margin:0}</style></head><body></body></html>`);
  await page.addScriptTag({ content: peleJs });
  await page.addScriptTag({ content: glyphsJs });
  await page.addScriptTag({ content: plateJs });
  await page.evaluate(async (faces) => {
    await Promise.all(faces.map(([fam, w]) => document.fonts.load(`${w} 14px '${fam}'`)));
  }, FACES.map((f) => [f.family, f.weight]));

  const shot = await (await browser.newContext({ deviceScaleFactor: 2 })).newPage();

  for (const src of sources) {
    const label = path.relative(REPO_DIR, src.file) + (src.derived ? ' (derived narrow)' : '');
    try {
      if (src.meta.kind === 'og') resolveCard(src);
      const hash = createHash('sha256').update([readFileSync(src.file, 'utf8'), src.derived ? 'derived-narrow' : '', PIPELINE].join('\0')).digest('hex').slice(0, 16);
      const result = await page.evaluate(({ src, tokens, hash }) => {
        document.body.innerHTML = '';
        const dims = src.meta.kind === 'og' ? window.npComposeOg(src, tokens, { hash }) : window.npComposeArticle(src, tokens, { hash });
        const plate = document.body.querySelector('svg.np-plate');
        window.npPinText(plate);
        const audit = window.npAudit(plate, tokens);
        const text = [...plate.querySelectorAll('text, tspan')].map((t) => t.textContent).join('');
        // Words in the image, excluding the figure title band and decorative digits.
        // Wrapped labels are separate tspans; join them with spaces so wrapping never merges words.
        const lines = (t) => (t.querySelector('tspan') ? [...t.querySelectorAll('tspan')].map((s) => s.textContent).join(' ') : t.textContent);
        const visible = [...plate.querySelectorAll('text')].filter((t) => !t.closest('[data-exempt]'));
        const counted = visible.filter((t) => !t.classList.contains('gl-digit')).map(lines);
        // Smallest text in the plate, for the sweep's displayed-size check.
        const minText = { sans: 99, mono: 99 };
        for (const t of [...plate.querySelectorAll('text, tspan')].filter((t) => !t.closest('.np-og-title') && t.textContent.trim())) {
          const cs = getComputedStyle(t);
          const k = /Mono/.test(cs.fontFamily) ? 'mono' : 'sans';
          minText[k] = Math.min(minText[k], Math.round(parseFloat(cs.fontSize) * 100) / 100);
        }
        return { dims, text, counted, audit, minText, svg: new XMLSerializer().serializeToString(plate) };
      }, { src, tokens, hash });

      if (result.audit.length) throw new Error(`off-token marks: ${result.audit.slice(0, 8).join('; ')}${result.audit.length > 8 ? ` (+${result.audit.length - 8} more)` : ''}`);
      const words = countWords(result.counted.join(' '));
      const budget = tokens.wordBudget[src.meta.kind] ?? tokens.wordBudget.diagram;
      if (words.length > budget) throw new Error(`${words.length} words in the image; the budget is ${budget} (${words.join(' ')})`);
      const fonts = await embedFonts(result.text + ' ');
      const svg = `<!-- ninadpathak.com image brand · source content/diagrams/${src.slug}/${src.id}.mmd · pele ${peleVersion} · ${hash} -->\n`
        + result.svg.replace('/*NP-STYLE*/', minify(fonts + css)) + '\n';

      const outDir = path.join(OUT_ROOT, src.slug);
      const svgPath = path.join(outDir, `${src.id}.svg`);
      const isNarrow = src.id.endsWith('.narrow');
      const rel = `/static/images/diagrams/${src.slug}/${src.id}`;
      if (isNarrow) narrow.set(`${src.slug}/${src.id.replace(/\.narrow$/, '')}`, { rel, width: result.dims.width, height: result.dims.height, minText: result.minText });
      const meta = !isNarrow && src.meta.kind !== 'og' ? JSON.stringify({
        source: `content/diagrams/${src.slug}/${src.id}.mmd`, hash, pele: peleVersion,
        width: result.dims.width, height: result.dims.height, scale: result.dims.scale, minText: result.minText,
        narrow: narrow.get(`${src.slug}/${src.id}`) || null,
        alt: src.meta.alt, caption: src.meta.caption ?? null, embed: embedSnippet(src, rel, result.dims, narrow.get(`${src.slug}/${src.id}`)),
      }, null, 2) + '\n' : null;
      if (CHECK) {
        const committed = existsSync(svgPath) ? readFileSync(svgPath, 'utf8') : '';
        if (!committed.includes(hash)) { failures.push(`${label}: output is stale; run node tools/image-brand/render.mjs`); continue; }
        const siblings = isNarrow ? [] : src.meta.kind === 'og' ? [`${src.id}.png`] : [`${src.id}.light.png`, `${src.id}.dark.png`, `${src.id}.json`];
        for (const f of siblings) if (!existsSync(path.join(outDir, f))) failures.push(`${label}: missing ${src.slug}/${f}`);
        const titleOf = (x) => (x.match(/<title[^>]*>([^<]*)<\/title>/) || [])[1];
        const kickerOf = (x) => (x.match(/class="np-og-kicker"[^>]*>(?:<tspan[^>]*>[^<]*<\/tspan>)?([^<]*)</) || [])[1];
        if (src.meta.kind === 'og' && (titleOf(committed) !== titleOf(svg) || kickerOf(committed) !== kickerOf(svg))) {
          // A retitled or recategorized post keeps its old card until someone re-renders; that is not a CI failure.
          console.warn(`warn ${label}: card still shows "${titleOf(committed)}" / ${kickerOf(committed)}; run node tools/image-brand/render.mjs to refresh it`);
        } else {
          const d = svgDiff(committed, svg);
          if (!d.same) failures.push(`${label}: committed SVG differs from a fresh render (${d.count} tokens, max numeric delta ${d.maxDelta}; first: ${d.first}); run node tools/image-brand/render.mjs`);
        }
        if (meta && existsSync(path.join(outDir, `${src.id}.json`)) && !sameSvg(readFileSync(path.join(outDir, `${src.id}.json`), 'utf8'), meta)) failures.push(`${label}: committed ${src.id}.json differs from a fresh render`);
        continue;
      }
      mkdirSync(outDir, { recursive: true });
      writeFileSync(svgPath, svg);

      const png = async (scheme, file) => {
        await shot.emulateMedia({ colorScheme: scheme });
        await shot.setViewportSize({ width: result.dims.width, height: result.dims.height });
        await shot.setContent(`<!doctype html><html><body style="margin:0">${svg.replace(/^<!--.*-->\n/, '')}</body></html>`);
        await shot.evaluate(() => document.fonts.ready);
        await shot.locator('svg.np-plate').screenshot({ path: file, omitBackground: false });
      };
      if (isNarrow) { console.log(`${label} -> ${path.relative(REPO_DIR, svgPath)} ${result.dims.width}x${result.dims.height} (narrow)`); continue; }
      if (src.meta.kind === 'og') {
        const ogPage = await (await browser.newContext({ deviceScaleFactor: 1 })).newPage();
        await ogPage.setViewportSize({ width: result.dims.width, height: result.dims.height });
        await ogPage.setContent(`<!doctype html><html><body style="margin:0">${svg.replace(/^<!--.*-->\n/, '')}</body></html>`);
        await ogPage.evaluate(() => document.fonts.ready);
        await ogPage.locator('svg.np-plate').screenshot({ path: path.join(outDir, `${src.id}.png`) });
        await ogPage.context().close();
      } else {
        await png('light', path.join(outDir, `${src.id}.light.png`));
        await png('dark', path.join(outDir, `${src.id}.dark.png`));
        if (meta) writeFileSync(path.join(outDir, `${src.id}.json`), meta);
      }
      console.log(`${label} -> ${path.relative(REPO_DIR, svgPath)} ${result.dims.width}x${result.dims.height} scale ${result.dims.scale} words ${words.length}/${budget}`);
    } catch (error) {
      if (src.derived) console.warn(`warn ${label}: no derived phone variant (${error.message.split('\n')[0].slice(0, 120)}); write ${src.id}.mmd by hand`);
      else failures.push(`${label}: ${error.message}`);
    }
  }
  await browser.close();
  return failures;
}

const failures = await main();
if (failures.length) {
  for (const f of failures) console.error(`FAIL ${f}`);
  process.exit(1);
}
