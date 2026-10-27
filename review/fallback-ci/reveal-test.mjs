import { readFileSync, mkdirSync } from 'node:fs';
const { chromium } = await import(new URL('../../tools/image-brand/node_modules/playwright-core/index.mjs', import.meta.url).pathname);
const BASE = 'http://127.0.0.1:8801/articles/vector-embeddings/';
const OUT = process.env.SHOTS || 'shots'; mkdirSync(OUT, { recursive: true });
const oldMain = readFileSync(process.env.OLD_MAIN_JS, 'utf8');
const b = await chromium.launch();
const results = [];
// Rocket-Loader-like: the page's inline script runs 1.5 s after the frame's load event.
const deferPage = (html) => html.replace('<script>', '<script type="text/deferred">').replace('</body>', `<script>addEventListener('load',function(){setTimeout(function(){var s=document.querySelector('script[type="text/deferred"]');var n=document.createElement('script');n.textContent=s.textContent;document.body.appendChild(n);},1500)})</script></body>`);
async function run(name, { width = 1366, scheme = 'light', block = false, defer = false, old = false, slowMain = false, shot = false }) {
  const ctx = await b.newContext({ viewport: { width, height: 900 }, colorScheme: scheme });
  const page = await ctx.newPage();
  await page.addInitScript((s) => { try { localStorage.setItem('np-theme', s); } catch (e) {} }, scheme);
  await page.route(/\/static\/visuals\/(cosine-similarity|matryoshka-truncation)$/, async (route) => {
    if (block) return route.abort();
    const r = await route.fetch(); let body = await r.text();
    if (defer) body = deferPage(body);
    route.fulfill({ response: r, body });
  });
  await page.route(/\/static\/js\/main\.js/, async (route) => {
    if (slowMain) await new Promise((res) => setTimeout(res, 3000));
    if (old) return route.fulfill({ status: 200, contentType: 'application/javascript', body: oldMain });
    route.continue();
  });
  await page.goto(BASE, { waitUntil: 'domcontentloaded' });
  const frames = page.locator('.visual-container--fallback');
  for (let i = 0; i < 2; i++) await frames.nth(i).scrollIntoViewIfNeeded();
  await page.waitForTimeout(5000);
  const state = await page.evaluate(() => [...document.querySelectorAll('.visual-container--fallback')].map((c) => {
    const f = c.querySelector('iframe');
    const img = [...c.querySelectorAll('.visual-fallback img')].find((i) => getComputedStyle(i).display !== 'none');
    return { src: f.getAttribute('src').split('/').pop(), ready: f.classList.contains('is-ready'), frameOpacity: getComputedStyle(f).opacity, fallbackShown: !!img && img.complete && img.naturalWidth > 0, fallbackTheme: img ? img.className : null };
  }));
  if (shot) for (let i = 0; i < 2; i++) await frames.nth(i).screenshot({ path: `${OUT}/${name}-${i}.png` });
  results.push({ name, width, scheme, block, defer, old, slowMain, state });
  await ctx.close();
}
for (const scheme of ['light', 'dark']) for (const width of [375, 1366]) await run(`normal-${scheme}-${width}`, { width, scheme, shot: true });
for (const scheme of ['light', 'dark']) await run(`blocked-${scheme}-375`, { width: 375, scheme, block: true, shot: true });
await run('deferred-page-new', { defer: true, shot: true });
await run('deferred-page-OLD-main', { defer: true, old: true });
await run('slow-main-new', { slowMain: true });
await run('slow-main-and-deferred-page-new', { slowMain: true, defer: true });
await b.close();
for (const r of results) console.log(r.name.padEnd(34), r.state.map((s) => `${s.src}: ready=${s.ready} opacity=${s.frameOpacity} fallback=${s.fallbackShown}/${s.fallbackTheme}`).join(' | '));
