#!/usr/bin/env node
// Code-block sweep: before (main build) vs after (branch build), with layout checks.
//
//   node tools/codeblocks_sweep.mjs <before-url> <after-url> <out-dir> <slug> ...
//
// For each article at 320, 375, 768 and 1366 px in light and dark, it checks that:
// - the page doesn't scroll sideways;
// - every code block's left edge equals the text column's (the preceding paragraph,
//   within 0.5px) and stays inside the column;
// - a block whose code overflows scrolls, with the edge-fade background in place;
// - short inline code (24 characters or fewer) sits on one line, and long inline code
//   breaks only between its segments;
// - at 1366 light, the copy button copies the code text exactly, and adding it didn't
//   change the head strip's height;
// - with JavaScript off, the page ships no copy button.
// It writes before/after sheets, per-width strips and sweep.json, and exits 1 on any failure.
import { mkdirSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = await import(path.join(here, 'image-brand/node_modules/playwright-core/index.mjs'));

const [beforeUrl, afterUrl, outDir, ...slugs] = process.argv.slice(2);
if (!slugs.length) { console.error('usage: codeblocks_sweep.mjs <before-url> <after-url> <out-dir> <slug> ...'); process.exit(2); }
mkdirSync(outDir, { recursive: true });
const WIDTHS = [320, 375, 768, 1366];
const SCHEMES = ['light', 'dark'];
const browser = await chromium.launch();
const results = [];
const unstick = 'header, nav, .nav, .reading-progress { position: static !important; }';

async function open(url, width, scheme, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 2, colorScheme: scheme, ...opts });
  await ctx.addInitScript((s) => { try { localStorage.setItem('np-theme', s); } catch (e) {} }, scheme);
  // Only the local build and the site's web fonts (Inter and JetBrains Mono come from
  // Google). Analytics and the booking widget can hold the load event for minutes.
  await ctx.route((u) => !/^https?:\/\/(127\.0\.0\.1|localhost|fonts\.googleapis\.com|fonts\.gstatic\.com)[:/]/.test(u.href), (route) => route.abort());
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load', timeout: 30000 });
  if (opts.javaScriptEnabled === false) return { ctx, page };
  await page.addStyleTag({ content: unstick });
  await page.evaluate(() => document.fonts.ready.then(() => true));
  return { ctx, page };
}

const measure = () => {
  const blocks = [...document.querySelectorAll('.post-content .code-block')];
  const out = { pageOverflow: document.documentElement.scrollWidth - window.innerWidth, blocks: [], inline: [] };
  for (const block of blocks) {
    const r = block.getBoundingClientRect();
    let ref = block.previousElementSibling;
    while (ref && ref.tagName !== 'P') ref = ref.previousElementSibling;
    const parent = block.parentElement;
    const ps = getComputedStyle(parent);
    const pr = parent.getBoundingClientRect();
    const colLeft = ref ? ref.getBoundingClientRect().left : pr.left + parseFloat(ps.paddingLeft) + parseFloat(ps.borderLeftWidth);
    const colRight = pr.right - parseFloat(ps.paddingRight) - parseFloat(ps.borderRightWidth);
    const pre = block.querySelector('pre');
    const cs = getComputedStyle(pre);
    const overflows = pre.scrollWidth > pre.clientWidth + 1;
    out.blocks.push({
      lang: block.dataset.lang,
      mode: block.classList.contains('code-block--wrap') ? 'wrap' : 'scroll',
      leftDelta: Math.round((r.left - colLeft) * 100) / 100,
      insideColumn: r.right <= colRight + 0.5,
      overflows,
      scrollable: cs.overflowX === 'auto' || cs.overflowX === 'scroll',
      edgeFade: (cs.backgroundImage.match(/linear-gradient/g) || []).length === 4 && cs.backgroundAttachment.includes('local'),
      focusable: pre.tabIndex === 0 && pre.getAttribute('role') === 'region' && !!pre.getAttribute('aria-label'),
    });
  }
  for (const code of document.querySelectorAll('.post-content :not(pre) > code')) {
    const rects = code.getClientRects().length;
    const len = code.textContent.length;
    const segsSplit = [...code.querySelectorAll('.code-seg')].filter((s) => s.getClientRects().length > 1).length;
    if ((len <= 24 && rects > 1) || segsSplit) out.inline.push({ text: code.textContent.slice(0, 40), rects, segsSplit });
  }
  return out;
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

// The first block, with the paragraph above it, so alignment shows in the shot.
async function shot(page, selector) {
  const el = page.locator(selector).first();
  if (!(await el.count())) return null;
  await el.scrollIntoViewIfNeeded();
  const box = await el.boundingBox();
  const prev = await el.evaluate((n) => { let p = n.previousElementSibling; while (p && p.tagName !== 'P') p = p.previousElementSibling; return p ? p.getBoundingClientRect().top + window.scrollY : null; });
  const top = prev !== null ? prev : box.y + (await page.evaluate(() => window.scrollY));
  const y = top - 12;
  const pageBox = await page.evaluate(() => ({ x: document.querySelector('.post-content').getBoundingClientRect().left + window.scrollX }));
  const x = Math.max(0, pageBox.x - 16);
  const width = Math.min(page.viewportSize().width - x, box.width + 32);
  const height = box.y + (await page.evaluate(() => window.scrollY)) + box.height + 12 - y;
  return page.screenshot({ fullPage: true, clip: { x, y, width, height } });
}

for (const slug of slugs) {
  const url = `/articles/${slug}/`;
  for (const scheme of SCHEMES) {
    const b = await open(beforeUrl + url, 1366, scheme);
    const a = await open(afterUrl + url, 1366, scheme);
    const before = await shot(b.page, '.post-content .highlight');
    const after = await shot(a.page, '.post-content .code-block');
    if (before && after) await sheet(`${slug}.before-after.${scheme}.png`, `${slug} · before (main) / after (branch) · 1366 · ${scheme}`, [['before', before, 700], ['after', after, 700]]);
    await b.ctx.close(); await a.ctx.close();
  }
  const cols = [];
  for (const scheme of SCHEMES) for (const width of WIDTHS) {
    if (process.env.SWEEP_DEBUG) console.error(`  ${slug} ${width} ${scheme}`);
    const { ctx, page } = await open(afterUrl + url, width, scheme, width === 1366 && scheme === 'light' ? { permissions: ['clipboard-read', 'clipboard-write'] } : {});
    const m = await page.evaluate(measure);
    let copy = null;
    if (width === 1366 && scheme === 'light') {
      const block = page.locator('.post-content .code-block').first();
      const headBefore = await block.locator('.code-block-head').evaluate((h) => h.getBoundingClientRect().height);
      const button = block.locator('.code-copy');
      await button.click();
      const clip = await page.evaluate(() => Promise.race([navigator.clipboard.readText(), new Promise((r) => setTimeout(() => r('<clipboard timeout>'), 5000))]));
      const expected = await block.locator('pre code').evaluate((c) => c.textContent.replace(/\n$/, ''));
      const label = await button.textContent();
      copy = { ok: clip === expected, label: label.trim(), headStable: headBefore === (await block.locator('.code-block-head').evaluate((h) => h.getBoundingClientRect().height)), live: await block.locator('.code-copy-status').textContent() };
    }
    const bad = m.blocks.filter((x) => Math.abs(x.leftDelta) > 0.5 || !x.insideColumn || (x.mode === 'scroll' && x.overflows && !(x.scrollable && x.edgeFade && x.focusable)));
    const ok = m.pageOverflow <= 0 && !bad.length && !m.inline.length && (!copy || (copy.ok && copy.headStable && copy.label === 'Copied'));
    results.push({ slug, width, scheme, ok, pageOverflow: m.pageOverflow, blocks: m.blocks.length, overflowing: m.blocks.filter((x) => x.overflows).length, bad, inlineSplit: m.inline, copy });
    const s = await shot(page, '.post-content .code-block');
    if (s) cols.push([`${width} · ${scheme}`, s, width >= 768 ? 460 : width]);
    await ctx.close();
  }
  if (cols.length) await sheet(`${slug}.sweep.png`, `${slug} · sweep 320 / 375 / 768 / 1366 · light and dark`, cols);
  // No script, no button.
  const nojs = await open(afterUrl + url, 375, 'light', { javaScriptEnabled: false });
  const buttons = await nojs.page.locator('.code-copy').count();
  results.push({ slug, width: 375, scheme: 'light', noJs: true, ok: buttons === 0, buttons });
  await nojs.ctx.close();
  console.log(`${slug}: ${results.filter((r) => r.slug === slug && r.ok).length}/${results.filter((r) => r.slug === slug).length} ok`);
}
writeFileSync(path.join(outDir, 'sweep.json'), JSON.stringify(results, null, 2) + '\n');
await browser.close();
const failed = results.filter((r) => !r.ok);
for (const r of failed) console.error(`FAIL ${r.slug} ${r.width} ${r.scheme}${r.noJs ? ' no-js' : ''}: ${JSON.stringify({ overflow: r.pageOverflow, bad: r.bad, inline: r.inlineSplit, copy: r.copy, buttons: r.buttons })}`);
process.exit(failed.length ? 1 : 0);
