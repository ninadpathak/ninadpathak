#!/usr/bin/env node
// Visual sweep for a batch: before (main build) vs after (branch build), then every
// changed figure at 320, 375 and 1366 px in light and dark, with layout checks.
//
//   node sweep.mjs <before-url> <after-url> <out-dir> <slug>[#selector] ...
//
// The selector defaults to the first .np-figure on the after page and the element it
// replaced on the before page (same position in the article). Writes PNG sheets and
// sweep.json; exits 1 if any page scrolls sideways or any figure image fails to load.
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';

const [beforeUrl, afterUrl, outDir, ...targets] = process.argv.slice(2);
if (!targets.length) { console.error('usage: sweep.mjs <before-url> <after-url> <out-dir> <slug>[|before-selector] ...'); process.exit(2); }
mkdirSync(outDir, { recursive: true });
const WIDTHS = [320, 375, 768, 1024, 1366];
const SCHEMES = ['light', 'dark'];
const browser = await chromium.launch();
const results = [];
const unstick = 'header, nav, .site-header, .reading-progress, [class*="progress"] { position: static !important; } .skip-link, [href="#main"], [href="#content"] { display: none !important; }';

async function open(url, width, scheme) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 2, colorScheme: scheme });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.evaluate(([s, css]) => {
    document.documentElement.setAttribute('data-theme', s);
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
  }, [scheme, unstick]);
  return { ctx, page };
}

const shot = async (page, selector) => {
  const el = page.locator(selector).first();
  await el.scrollIntoViewIfNeeded();
  await page.waitForTimeout(400);
  return el.screenshot();
};

async function sheet(file, title, columns) {
  const img = (b) => `data:image/png;base64,${b.toString('base64')}`;
  const html = `<!doctype html><body style="margin:0;background:#f8f8f6;font-family:ui-monospace,Menlo,monospace">
  <div id="s" style="display:inline-block;padding:32px"><div style="font-size:12px;letter-spacing:.12em;color:#c23b00;text-transform:uppercase">// ${title}</div>
  <div style="display:flex;gap:28px;margin-top:18px;align-items:flex-start">${columns.map(([label, buf, w]) => `<div style="width:${w}px"><div style="font-size:11px;letter-spacing:.1em;color:#6b6b6b;text-transform:uppercase;border-bottom:1px solid #e0e0dc;padding-bottom:6px;margin-bottom:12px">${label}</div><img src="${img(buf)}" style="display:block;width:${w}px"></div>`).join('')}</div></div></body>`;
  const ctx = await browser.newContext({ viewport: { width: 1800, height: 1000 } });
  const page = await ctx.newPage();
  await page.setContent(html);
  await page.locator('#s').screenshot({ path: path.join(outDir, file) });
  await ctx.close();
}

for (const target of targets) {
  const [slug, beforeSel = '.visual-wrapper, figure'] = target.split('|');
  const url = `/articles/${slug}/`;
  // Before / after at desktop, both schemes.
  for (const scheme of SCHEMES) {
    const b = await open(beforeUrl + url, 1366, scheme);
    const a = await open(afterUrl + url, 1366, scheme);
    const before = await shot(b.page, beforeSel);
    const after = await shot(a.page, 'figure.np-figure');
    await sheet(`${slug}.before-after.${scheme}.png`, `${slug} · before (main) / after (branch) · 1366 · ${scheme}`, [['before', before, 640], ['after', after, 640]]);
    await b.ctx.close(); await a.ctx.close();
  }
  // Sweep: three widths × two schemes, with layout checks.
  const cols = [];
  for (const scheme of SCHEMES) for (const width of WIDTHS) {
    const { ctx, page } = await open(afterUrl + url, width, scheme);
    // Lazy images load only near the viewport: bring the figure in and wait for its image.
    await page.locator('figure.np-figure').first().scrollIntoViewIfNeeded();
    await page.waitForFunction(() => { const i = document.querySelector('figure.np-figure img'); return i && i.complete && i.naturalWidth > 0; }, null, { timeout: 15000 }).catch(() => {});
    const metrics = await page.evaluate(async () => {
      const fig = document.querySelector('figure.np-figure');
      const img = fig?.querySelector('img');
      // Displayed text size = the plate's smallest text × its on-screen scale (GUIDELINE.md §4).
      const meta = img ? await (await fetch(img.getAttribute('src').replace(/\.svg$/, '.json'))).json() : null;
      const variant = img && meta?.narrow && img.currentSrc.includes('.narrow.svg') ? meta.narrow : meta;
      const k = img && variant ? img.getBoundingClientRect().width / variant.width : 0;
      const shown = variant ? { sans: Math.round(variant.minText.sans * k * 10) / 10, mono: Math.round(variant.minText.mono * k * 10) / 10 } : null;
      const scroller = fig?.querySelector('.np-figure-zoom');
      return {
        pageOverflow: document.documentElement.scrollWidth - window.innerWidth,
        figureLoaded: !!img && img.complete && img.naturalWidth > 0,
        figureWidth: img ? Math.round(img.getBoundingClientRect().width) : 0,
        figureFits: scroller ? scroller.scrollWidth <= scroller.clientWidth + 1 : false,
        variant: img ? (img.currentSrc.includes('.narrow.svg') ? 'narrow' : 'wide') : null,
        shownText: shown,
        textOk: !!shown && shown.sans >= 12 && shown.mono >= 8.5,
        // A variant may not be stretched past 1.25x its drawn width.
        notBlownUp: !!variant && k <= 1.25 + 0.01,
        scale: Math.round(k * 100) / 100,
      };
    });
    results.push({ slug, width, scheme, ...metrics, ok: metrics.pageOverflow <= 0 && metrics.figureLoaded && metrics.figureFits && metrics.textOk && metrics.notBlownUp });
    cols.push([`${width} · ${scheme} · ${metrics.variant} · ${metrics.shownText?.sans}px`, await shot(page, 'figure.np-figure'), width >= 768 ? 420 : width * 0.9]);
    await ctx.close();
  }
  await sheet(`${slug}.sweep.png`, `${slug} · sweep 320 / 375 / 768 / 1024 / 1366 · light and dark`, cols);
  console.log(`${slug}: ${results.filter((r) => r.slug === slug && r.ok).length}/${WIDTHS.length * SCHEMES.length} ok`);
}
writeFileSync(path.join(outDir, 'sweep.json'), JSON.stringify(results, null, 2) + '\n');
await browser.close();
const bad = results.filter((r) => !r.ok);
for (const r of bad) console.error(`FAIL ${r.slug} ${r.width} ${r.scheme}: overflow ${r.pageOverflow}px, loaded ${r.figureLoaded}, fits ${r.figureFits}, ${r.variant} ×${r.scale} text ${JSON.stringify(r.shownText)}`);
process.exit(bad.length ? 1 : 0);
