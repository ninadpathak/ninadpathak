#!/usr/bin/env node
// Before/after review sheets. Needs a built site served locally (python3 build.py, then
// serve output/ with the rendered diagrams copied into output/static/images/diagrams).
//
//   node review.mjs http://localhost:8791 ../../review/image-brand
//
// For each sample, screenshots the current figure in its live article, swaps in the new
// figure on the same page, screenshots it again, and lays both side by side, light and dark.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';
import { REPO_DIR } from './lib/tokens.mjs';

const [base = 'http://localhost:8791', outArg = path.join(REPO_DIR, 'review/image-brand')] = process.argv.slice(2);
const OUT = path.resolve(outArg);
mkdirSync(OUT, { recursive: true });

const SAMPLES = [
  { name: '1-flowchart', type: 'Static SVG flowchart (decision tree)', url: '/articles/internal-vs-external-docs/', selector: 'figure.flowchart-image', diagram: 'internal-vs-external-docs/documentation-placement' },
  { name: '2-anatomy', type: 'Static SVG annotated example', url: '/articles/documentation-headings/', selector: '.visual-wrapper', diagram: 'documentation-headings/task-heading-anatomy', removeNext: 'p.visual-caption' },
  { name: '3-iframe-loop', type: 'Interactive iframe visual (HTML/SVG animation)', url: '/articles/agent-loop-anatomy/', selector: '.visual-wrapper', diagram: 'agent-loop-anatomy/agent-loop' },
  { name: '4-og-card', type: 'Share card (og:image)', og: 'agent-harnesses/og' },
];

const browser = await chromium.launch();

async function capture(sample, scheme) {
  const ctx = await browser.newContext({ viewport: { width: 1180, height: 900 }, deviceScaleFactor: 2, colorScheme: scheme });
  const page = await ctx.newPage();
  const setTheme = () => page.evaluate((s) => document.documentElement.setAttribute('data-theme', s), scheme);
  const shots = {};
  await page.goto(base + sample.url, { waitUntil: 'networkidle' });
  await setTheme();
  let target = page.locator(sample.selector).first();
  await target.scrollIntoViewIfNeeded();
  await page.waitForTimeout(2500);
  shots.before = await target.screenshot();
  const meta = JSON.parse(readFileSync(path.join(REPO_DIR, 'static/images/diagrams', `${sample.diagram}.json`), 'utf8'));
  await page.evaluate(({ selector, embed, removeNext }) => {
    const old = document.querySelector(selector);
    if (removeNext && old.nextElementSibling?.matches(removeNext)) old.nextElementSibling.remove();
    const holder = document.createElement('div');
    holder.innerHTML = embed;
    const fig = holder.firstElementChild;
    fig.style.cssText = 'margin:3rem 0';
    fig.querySelector('img').style.cssText = 'display:block;width:100%;height:auto';
    const cap = fig.querySelector('figcaption');
    if (cap) cap.style.cssText = 'margin-top:.75rem;font-family:var(--mono);font-size:var(--font-size-sm);line-height:var(--leading-relaxed);color:var(--text-3)';
    old.replaceWith(fig);
  }, { selector: sample.selector, embed: meta.embed, removeNext: sample.removeNext });
  target = page.locator('figure.np-figure').first();
  await target.scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);
  shots.after = await target.screenshot();
  await ctx.close();
  return shots;
}

async function sheet(sample, scheme, before, after, beforeNote, afterNote) {
  const dark = scheme === 'dark';
  const bg = dark ? '#090909' : '#f8f8f6', ink = dark ? '#f0f0f0' : '#0e0e0e', muted = dark ? '#8a8a8a' : '#6b6b6b', rule = dark ? '#1e1e1e' : '#e0e0dc', accent = dark ? '#ff5f1f' : '#c23b00';
  const img = (buf) => `data:image/png;base64,${buf.toString('base64')}`;
  const html = `<!doctype html><html><body style="margin:0;background:${bg};font-family:ui-monospace,Menlo,monospace;color:${ink}">
  <div id="s" style="display:inline-block;padding:40px">
    <div style="font-size:13px;letter-spacing:.12em;color:${accent};text-transform:uppercase">// ${sample.name} · ${sample.type} · ${scheme}</div>
    <div style="display:flex;gap:40px;margin-top:24px;align-items:flex-start">
      ${[['Before', before, beforeNote], ['After', after, afterNote]].map(([label, buf, note]) => `
      <div style="width:720px">
        <div style="font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:${muted};border-bottom:1px solid ${rule};padding-bottom:8px;margin-bottom:16px">${label}${note ? ` · ${note}` : ''}</div>
        <img src="${img(buf)}" style="display:block;max-width:720px;width:${label === 'Before' && sample.og ? '256px' : '720px'}">
      </div>`).join('')}
    </div>
  </div></body></html>`;
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.setContent(html);
  await page.locator('#s').screenshot({ path: path.join(OUT, `${sample.name}.${scheme}.png`) });
  await ctx.close();
}

for (const sample of SAMPLES) {
  if (sample.og) {
    const before = readFileSync(path.join(REPO_DIR, 'static/favicon.png'));
    const after = readFileSync(path.join(REPO_DIR, 'static/images/diagrams', `${sample.og}.png`));
    await sheet(sample, 'light', before, after, 'og:image today is /static/favicon.png, 512x512, on every page', '1200x630, per article');
    console.log(`${sample.name}.light.png`);
    continue;
  }
  for (const scheme of ['light', 'dark']) {
    const { before, after } = await capture(sample, scheme);
    await sheet(sample, scheme, before, after, 'live article, current asset', 'same page, new figure');
    console.log(`${sample.name}.${scheme}.png`);
  }
}
await browser.close();
// review/image-brand/README.md is maintained by hand.
