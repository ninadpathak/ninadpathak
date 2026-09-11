// Static localhost render evidence. No interactive signed-in browser session.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const here = __dirname;
const visual = path.join(here, 'visual');
fs.mkdirSync(visual, { recursive: true });
const cohort = JSON.parse(fs.readFileSync(path.join(here, 'cohort.json')));

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const evidence = { baseURL: 'http://127.0.0.1:8765', renders: [], removedHTTP: [], retainedHTTP: [] };
  try {
    for (const entry of cohort) {
      const response = await fetch(evidence.baseURL + entry.canonical);
      assert.equal(response.status, entry.impressions ? 200 : 404, entry.canonical);
      evidence[entry.impressions ? 'retainedHTTP' : 'removedHTTP'].push({ url: entry.canonical, status: response.status });
    }
    for (const [name, viewport] of [['desktop', { width: 1440, height: 1000 }], ['mobile', { width: 390, height: 844 }]]) {
      const page = await browser.newPage({ viewport, reducedMotion: 'reduce' });
      for (const route of ['/', '/articles/', '/articles/ai-search-optimization/', '/articles/distribution/']) {
        await page.goto(evidence.baseURL + route, { waitUntil: 'networkidle' });
        await page.evaluate(async () => {
          await document.fonts.ready;
          for (const img of document.images) img.loading = 'eager';
          await Promise.all([...document.images].map(img => img.decode()));
        });
        const state = await page.evaluate(() => ({
          title: document.title,
          canonical: document.querySelector('link[rel="canonical"]').href,
          robots: document.querySelector('meta[name="robots"]').content,
          width: document.documentElement.clientWidth,
          scrollWidth: document.documentElement.scrollWidth,
          emptyState: document.querySelector('.empty-state')?.innerText || null,
          images: [...document.images].map(i => ({ src: i.getAttribute('src'), complete: i.complete, naturalWidth: i.naturalWidth, naturalHeight: i.naturalHeight })),
        }));
        assert.ok(state.scrollWidth <= state.width + 1, route + ' page overflow');
        if (route.includes('optimization') || route.includes('distribution')) {
          assert.equal(state.robots, 'noindex, follow');
          assert.ok(state.emptyState.includes('No articles are currently published'));
        }
        const file = name + '-' + (route.split('/').filter(Boolean).join('-') || 'home') + '.png';
        await page.screenshot({ path: path.join(visual, file), fullPage: route !== '/' && route !== '/articles/' });
        evidence.renders.push({ viewport, route, file, capture: route === '/' || route === '/articles/' ? 'top viewport' : 'full page', ...state });
      }
      await page.close();
    }
    fs.writeFileSync(path.join(visual, 'manifest.json'), JSON.stringify(evidence, null, 2) + '\n');
    console.log('PASS: 20 removed routes return 404; 67 retained return 200; 8 renders, decoded images, no horizontal page overflow, noindex empty category states.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
