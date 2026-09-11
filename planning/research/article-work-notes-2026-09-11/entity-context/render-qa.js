// Static render QA, launched in a fresh headless Chromium session.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const directory = path.join(__dirname, 'visual');
const cases = [
  'agent-harnesses',
  'context-windows-vs-memory',
  'how-to-write-a-technical-tutorial-that-actually-teaches',
  'writing-release-notes-that-developers-trust',
  'how-memory-works-in-claude-code',
  'memory-serialization-between-sessions',
  'why-coding-agents-lose-their-memory',
  'how-memory-works-in-hyperagents',
];

(async () => {
  fs.mkdirSync(directory, { recursive: true });
  const browser = await chromium.launch({headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  const manifest = {baseURL: 'http://127.0.0.1:8765', browser: await browser.version(), capture: 'Normal viewport screenshots centered on work note and original opening; no full-page stitching', artifacts: []};
  try {
    for (const width of [1440, 390]) {
      for (const theme of ['dark', 'light']) {
        const context = await browser.newContext({viewport: {width, height: 950}, deviceScaleFactor: 1, reducedMotion: 'reduce'});
        await context.addInitScript(value => localStorage.setItem('np-theme', value), theme);
        const page = await context.newPage();
        for (const slug of (theme === 'dark' ? cases : cases.slice(0, 2))) {
          const url = `${manifest.baseURL}/articles/${slug}/`;
          const response = await page.goto(url, {waitUntil: 'networkidle'});
          assert.equal(response.status(), 200);
          await page.evaluate(() => document.fonts.ready);
          const note = page.locator('.article-work-note');
          assert.equal(await note.count(), 1);
          await note.evaluate(element => window.scrollTo(0, element.getBoundingClientRect().top + window.scrollY - 140));
          const images = await page.locator('img').evaluateAll(async imgs => Promise.all(imgs.map(async img => {
            const r = img.getBoundingClientRect();
            const visible = r.bottom > 0 && r.top < innerHeight;
            if (visible) {
              img.loading = 'eager';
              await img.decode();
            }
            return {src: img.getAttribute('src'), visible, complete: img.complete, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight};
          })));
          const data = await note.evaluate(element => {
            const rect = element.getBoundingClientRect();
            const content = document.querySelector('.post-content');
            const original = content.firstElementChild;
            const link = element.querySelector('a');
            const style = getComputedStyle(element);
            return {text: element.textContent.trim(), rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height}, clientWidth: element.clientWidth, scrollWidth: element.scrollWidth,
              immediatelyBeforeContent: element.nextElementSibling === content,
              originalFirstElement: original.tagName, originalFirstText: original.textContent.trim().slice(0, 250),
              originalFirstFontSize: getComputedStyle(original).fontSize,
              noteFontSize: getComputedStyle(element.querySelector('p')).fontSize, noteColor: style.color, bodyBackground: getComputedStyle(document.body).backgroundColor,
              link: link.getAttribute('href'), linkDecoration: getComputedStyle(link).textDecorationLine,
              pageWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth};
          });
          assert(data.immediatelyBeforeContent);
          assert.equal((data.text.match(/Ninad Pathak/g) || []).length, 1);
          assert(!/\b(?:I|me|my|mine|we|our|ours|us)\b|let['’]s/i.test(data.text));
          assert(data.rect.x >= 0 && data.rect.x + data.rect.width <= width + 1);
          assert(data.scrollWidth <= data.clientWidth + 1);
          assert(data.rect.y >= 0 && data.rect.y + data.rect.height <= 950);
          assert(data.linkDecoration.includes('underline'));
          assert(parseFloat(data.noteFontSize) >= 15 && parseFloat(data.noteFontSize) <= 16);
          await note.locator('a').focus();
          assert(await note.locator('a').evaluate(a => a === document.activeElement));
          await note.locator('a').evaluate(a => a.blur());
          const file = `${width}-${theme}-${slug}.png`;
          await page.screenshot({path: path.join(directory, file)});
          manifest.artifacts.push({file, url, viewport: {width, height: 950}, theme, ...data, images});
        }
        if (theme === 'dark') {
          await page.goto(manifest.baseURL + '/', {waitUntil: 'networkidle'});
          await page.evaluate(() => document.fonts.ready);
          assert.equal(await page.locator('.article-work-note').count(), 0);
          assert.equal(await page.locator('#hero-canvas').count(), 1);
          const file = `${width}-dark-home-unchanged.png`;
          await page.screenshot({path: path.join(directory, file)});
          manifest.artifacts.push({file, url: manifest.baseURL + '/', viewport: {width, height: 950}, theme, noteAbsent: true, matrixPresent: true});
        }
        await context.close();
      }
    }
    fs.writeFileSync(path.join(directory, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
    console.log(`PASS: ${manifest.artifacts.length} viewport artifacts; note placement/overflow/links/fonts asserted`);
  } finally {
    await Promise.race([browser.close(), new Promise(resolve => setTimeout(resolve, 5000))]);
    assert(!browser.isConnected(), 'Browser must disconnect before CLI exits');
    manifest.browserDisconnected = true;
    fs.writeFileSync(path.join(directory, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  }
// Browser and contexts are closed above; exit the CLI despite driver keepalives.
})().then(() => process.exit(0)).catch(error => { console.error(error); process.exit(1); });
