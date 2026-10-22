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
import { parseSource } from './lib/source.mjs';

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
const peleJs = readFileSync(path.join(TOOL_DIR, 'node_modules/pele/dist/pele.global.js'), 'utf8');
const peleVersion = JSON.parse(readFileSync(path.join(TOOL_DIR, 'node_modules/pele/package.json'), 'utf8')).version;
const css = themeCss(tokens) + brandCss;
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

function embedSnippet(src, rel, dims) {
  const caption = src.meta.caption ? `\n  <figcaption>${src.meta.caption}</figcaption>` : '';
  return `<figure class="np-figure">
  <img src="${rel}.svg" width="${dims.width}" height="${dims.height}" alt="${src.meta.alt.replace(/"/g, '&quot;')}" loading="lazy" decoding="async">${caption}
</figure>`;
}

async function main() {
  const failures = [];
  const contrast = contrastReport(tokens).filter((r) => !r.ok);
  for (const r of contrast) failures.push(`contrast: ${r.scheme} ${r.fg} on ${r.bg} is ${r.ratio}, needs ${r.min} (${r.use})`);
  for (const d of siteDrift(tokens)) console.warn(`drift: ${d.scheme} ${d.token} is ${d.image}; site ${d.site} is ${d.live}`);

  const files = findSources();
  if (!files.length) { console.log('no sources'); return failures; }
  const sources = files.map(parseSource);

  const browser = await chromium.launch();
  const page = await (await browser.newContext({ deviceScaleFactor: 1 })).newPage();
  await page.setContent(`<!doctype html><html><head><style>${fontFaceCss(FACES)}${css}body{margin:0}</style></head><body></body></html>`);
  await page.addScriptTag({ content: peleJs });
  await page.addScriptTag({ content: plateJs });
  await page.evaluate(async (faces) => {
    await Promise.all(faces.map(([fam, w]) => document.fonts.load(`${w} 14px '${fam}'`)));
  }, FACES.map((f) => [f.family, f.weight]));

  const shot = await (await browser.newContext({ deviceScaleFactor: 2 })).newPage();

  for (const src of sources) {
    const label = path.relative(REPO_DIR, src.file);
    try {
      const hash = createHash('sha256')
        .update([readFileSync(src.file, 'utf8'), JSON.stringify(tokens), brandCss, plateJs, peleVersion].join('\0'))
        .digest('hex').slice(0, 16);
      const result = await page.evaluate(({ src, tokens, hash }) => {
        document.body.innerHTML = '';
        const dims = src.meta.kind === 'og' ? window.npComposeOg(src, tokens, { hash }) : window.npComposeArticle(src, tokens, { hash });
        const plate = document.body.querySelector('svg.np-plate');
        const text = [...plate.querySelectorAll('text, tspan')].map((t) => t.textContent).join('');
        return { dims, text, svg: new XMLSerializer().serializeToString(plate) };
      }, { src, tokens, hash });

      const fonts = await embedFonts(result.text + ' ');
      const svg = `<!-- ninadpathak.com image brand · source content/diagrams/${src.slug}/${src.id}.mmd · pele ${peleVersion} · ${hash} -->\n`
        + result.svg.replace('/*NP-STYLE*/', minify(fonts + css)) + '\n';

      const outDir = path.join(OUT_ROOT, src.slug);
      const svgPath = path.join(outDir, `${src.id}.svg`);
      if (CHECK) {
        const committed = existsSync(svgPath) ? readFileSync(svgPath, 'utf8') : '';
        if (!committed.includes(hash)) failures.push(`${label}: output is stale; run node tools/image-brand/render.mjs`);
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
        const rel = `/static/images/diagrams/${src.slug}/${src.id}`;
        writeFileSync(path.join(outDir, `${src.id}.json`), JSON.stringify({
          source: `content/diagrams/${src.slug}/${src.id}.mmd`, hash, pele: peleVersion,
          width: result.dims.width, height: result.dims.height, scale: result.dims.scale,
          alt: src.meta.alt, caption: src.meta.caption ?? null, embed: embedSnippet(src, rel, result.dims),
        }, null, 2) + '\n');
      }
      console.log(`${label} -> ${path.relative(REPO_DIR, svgPath)} ${result.dims.width}x${result.dims.height} scale ${result.dims.scale}`);
    } catch (error) {
      failures.push(`${label}: ${error.message}`);
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
