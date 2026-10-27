#!/usr/bin/env node
// Horizontal-overflow sweep over every URL in a sitemap.
//
//   node tools/overflow_sweep.mjs <site-base-url> <out.json> [widths=320,375]
//
// Reads <site-base-url>/sitemap.xml, rewrites each URL onto <site-base-url>, and opens it
// at each width. It records two failures:
// - the page itself scrolling sideways;
// - any visible element in <main> that runs past the right gutter. The allowed right edge
//   mirrors the left edge of the page's text column. Content inside a scroll container
//   (code that scrolls, wide tables) is exempt, because its overflow is deliberate.
// Exits 1 if any page fails either check.
import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = await import(path.join(here, 'image-brand/node_modules/playwright-core/index.mjs'));
const [base, out, widthArg = '320,375'] = process.argv.slice(2);
if (!base || !out) { console.error('usage: overflow_sweep.mjs <site-base-url> <out.json> [widths]'); process.exit(2); }
const widths = widthArg.split(',').map(Number);
const origin = new URL(base).origin;

const sitemap = await (await fetch(new URL('/sitemap.xml', base))).text();
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => origin + new URL(m[1]).pathname);
const browser = await chromium.launch();
const results = [];

const measure = () => {
  const vw = window.innerWidth;
  const main = document.querySelector('main') || document.body;
  const lefts = [...main.querySelectorAll('h1, h2, p, li')].map((e) => e.getBoundingClientRect()).filter((r) => r.width > 0 && r.left >= 0).map((r) => r.left);
  const gutter = lefts.length ? Math.min(...lefts) : 0;
  const limit = vw - gutter + 0.5;
  const scrolls = (node) => {
    for (let n = node.parentElement; n && n !== main.parentElement; n = n.parentElement) {
      const ox = getComputedStyle(n).overflowX;
      if (ox === 'auto' || ox === 'scroll' || ox === 'hidden' || ox === 'clip') return true;
    }
    return false;
  };
  // What actually draws: each text run (measured with a Range, since a paragraph's box is
  // the column's full width) and replaced or code elements. Containers are skipped; their
  // boxes include their own padding and reach the gutter by design.
  const visible = (el) => !el.closest('[inert], [aria-hidden="true"], script, style, noscript, template') && getComputedStyle(el).visibility !== 'hidden' && getComputedStyle(el).position !== 'fixed';
  const offenders = [];
  const report = (el, right, text) => offenders.push({ tag: el.tagName.toLowerCase(), cls: String(el.getAttribute('class') || '').slice(0, 40), text: text.trim().slice(0, 50), over: Math.round((right - limit) * 10) / 10 });
  const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
  const range = document.createRange();
  for (let t = walker.nextNode(); t; t = walker.nextNode()) {
    if (!t.data.trim()) continue;
    const el = t.parentElement;
    if (!el || !visible(el) || scrolls(t)) continue;
    range.selectNodeContents(t);
    const r = range.getBoundingClientRect();
    if (r.width && r.right > limit) report(el, r.right, t.data);
  }
  for (const el of main.querySelectorAll('img, svg, video, iframe, canvas, pre, table, input, textarea, select, button, code')) {
    if (!visible(el) || scrolls(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width && r.right > limit) report(el, r.right, el.textContent || el.getAttribute('alt') || '');
  }
  return { pageOverflow: document.documentElement.scrollWidth - vw, gutter: Math.round(gutter * 10) / 10, offenders: offenders.slice(-5), offenderCount: offenders.length };
};

for (const width of widths) {
  const ctx = await browser.newContext({ viewport: { width, height: 800 } });
  await ctx.route((u) => u.origin !== origin && !/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname), (r) => r.abort());
  const page = await ctx.newPage();
  for (const url of urls) {
    try {
      await page.goto(url, { waitUntil: 'load', timeout: 30000 });
      await page.evaluate(() => document.fonts.ready.then(() => true));
      const m = await page.evaluate(measure);
      results.push({ url: new URL(url).pathname, width, ok: m.pageOverflow <= 0 && !m.offenderCount, ...m });
    } catch (e) {
      results.push({ url: new URL(url).pathname, width, ok: false, error: String(e).slice(0, 200) });
    }
  }
  await ctx.close();
}
await browser.close();
writeFileSync(out, JSON.stringify(results, null, 2) + '\n');
for (const width of widths) {
  const w = results.filter((r) => r.width === width);
  console.log(`${width}px: ${w.filter((r) => r.ok).length}/${w.length} pages clean`);
}
const bad = results.filter((r) => !r.ok);
for (const r of bad) console.error(`FAIL ${r.width} ${r.url}: overflow ${r.pageOverflow}, ${r.offenderCount} offender(s) ${JSON.stringify(r.offenders || r.error)}`);
process.exit(bad.length ? 1 : 0);
