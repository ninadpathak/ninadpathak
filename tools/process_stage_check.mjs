#!/usr/bin/env node
// Browser check for the pinned stage on /technical-writing-process/.
//
//   node tools/process_stage_check.mjs <site-base-url> <out.json> [browser=chromium]
//
// Source review cannot see either of the two defects this guards against: a figure taller
// than the stage (it loses its centring and leaves a piece behind during the next scene),
// and a browser without scroll timelines drawing all eight figures at once before
// process.js runs. So this opens the page and measures.
//
// At each viewport, with each scene scrolled to its end, it checks that
// - the current figure's drawn parts sit inside the field with equal space above and below;
// - every animated part of that figure has finished;
// - no part of any other figure is visible inside the field.
// Then, with process.js blocked, it checks that no engine shows more than one figure on the
// stage at load, and that the page falls back to its finished state once the script is
// known to be missing.
// Exits 1 if any check fails.
import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const pw = await import(path.join(here, 'image-brand/node_modules/playwright-core/index.mjs'));
const [base, out, kind = 'chromium'] = process.argv.slice(2);
if (!base || !out) { console.error('usage: process_stage_check.mjs <site-base-url> <out.json> [chromium|firefox|webkit]'); process.exit(2); }
const url = base.replace(/\/$/, '') + '/technical-writing-process/';
const VIEWPORTS = [[1920, 1080], [1440, 900], [1440, 700], [1366, 768], [1280, 720], [1024, 768], [768, 1024],
  [430, 932], [412, 915], [390, 844], [390, 664], [375, 667], [2560, 1300], [1440, 2000], [844, 390]];
const TOLERANCE = 1.5;

const measure = () => {
  const visible = (el) => {
    for (let node = el; node && node.nodeType === 1; node = node.parentElement) {
      const cs = getComputedStyle(node);
      if (cs.visibility === 'hidden' || cs.display === 'none' || parseFloat(cs.opacity) < 0.02) return false;
    }
    return true;
  };
  const figures = [...document.querySelectorAll('[data-figure]')];
  const frame = document.querySelector('.pp-frame .pf-field').getBoundingClientRect();
  return figures.map((figure) => {
    const stage = figure.querySelector('.pf-stage');
    const parts = [...stage.children].filter((el) => !el.classList.contains('pf-lead'));
    const boxes = parts.map((el) => el.getBoundingClientRect());
    const top = Math.min(...boxes.map((b) => b.top)), bottom = Math.max(...boxes.map((b) => b.bottom));
    const inField = [...stage.querySelectorAll('*')].filter((el) => {
      const b = el.getBoundingClientRect();
      return b.width > 0 && b.height > 0 && b.bottom > frame.top + 0.5 && b.top < frame.bottom - 0.5 && visible(el);
    }).length;
    const unfinished = [...stage.querySelectorAll('.pa')].filter((el) => {
      const cs = getComputedStyle(el);
      return parseFloat(cs.opacity) < 0.99 || (cs.transform !== 'none' && cs.transform !== 'matrix(1, 0, 0, 1, 0, 0)');
    }).length;
    return { id: figure.dataset.figure, above: +(top - frame.top).toFixed(1), below: +(frame.bottom - bottom).toFixed(1), inField, unfinished };
  });
};

const browser = await pw[kind].launch();
const report = { url, browser: kind, viewports: [], scriptBlocked: null, failures: [] };

for (const [width, height] of VIEWPORTS) {
  const context = await browser.newContext({ viewport: { width, height } });
  const page = await context.newPage();
  await page.goto(url, { waitUntil: 'load' });
  await page.waitForTimeout(400);
  const live = await page.evaluate(() => document.documentElement.classList.contains('pp-live'));
  const row = { width, height, live, scenes: [] };
  if (live) {
    const ids = await page.$$eval('.pp-scene', (els) => els.map((el) => el.id));
    for (const id of ids) {
      await page.evaluate((id) => {
        const box = document.getElementById(id).getBoundingClientRect();
        window.scrollTo({ top: box.bottom + window.scrollY - window.innerHeight - 2, behavior: 'instant' });
      }, id);
      await page.waitForTimeout(kind === 'chromium' ? 250 : 1500);
      const all = await page.evaluate(measure);
      const current = all.find((f) => f.id === id);
      const others = all.filter((f) => f.id !== id && f.inField > 0).map((f) => `${f.id}:${f.inField}`);
      row.scenes.push({ id, above: current.above, below: current.below, unfinished: current.unfinished, others });
      const where = `${kind} ${width}x${height} ${id}`;
      if (current.above < 0 || current.below < 0) report.failures.push(`${where}: figure is cut (above ${current.above}, below ${current.below})`);
      if (Math.abs(current.above - current.below) > TOLERANCE) report.failures.push(`${where}: off centre (above ${current.above}, below ${current.below})`);
      if (current.unfinished) report.failures.push(`${where}: ${current.unfinished} part(s) unfinished at the end of the scene`);
      if (others.length) report.failures.push(`${where}: other figures on stage: ${others.join(', ')}`);
    }
  }
  report.viewports.push(row);
  await context.close();
}

// process.js blocked: one figure at most on the stage at load, then the finished page.
{
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.route('**/static/js/process.js*', (route) => route.abort());
  await page.goto(url + '#review', { waitUntil: 'load' });
  await page.waitForTimeout(600);
  const early = await page.evaluate(() => ({
    classes: document.documentElement.className.trim(),
    shown: [...document.querySelectorAll('[data-figure]')].filter((f) => getComputedStyle(f).visibility !== 'hidden' && getComputedStyle(f).position === 'sticky').map((f) => f.dataset.figure),
    scrubbed: CSS.supports('animation-timeline: view()') && CSS.supports('timeline-scope: --a'),
  }));
  await page.waitForTimeout(4600);
  const late = await page.evaluate(() => ({
    classes: document.documentElement.className.trim(),
    pinned: [...document.querySelectorAll('[data-figure]')].filter((f) => getComputedStyle(f).position === 'sticky').length,
    hidden: [...document.querySelectorAll('[data-figure] .pa')].filter((el) => parseFloat(getComputedStyle(el).opacity) < 0.99).length,
  }));
  report.scriptBlocked = { early, late };
  // With scroll timelines the scrubbed path needs no script, so several figures are
  // pinned but only the current one is on stage; the stepped path may show one.
  if (!early.scrubbed && early.shown.length > 1) report.failures.push(`${kind} script blocked: ${early.shown.length} figures piled on the stage before the fallback (${early.shown.join(', ')})`);
  if (late.pinned || late.hidden || /pp-live|pp-io/.test(late.classes)) report.failures.push(`${kind} script blocked: page did not return to its finished state (${JSON.stringify(late)})`);
  await context.close();
}

await browser.close();
writeFileSync(out, JSON.stringify(report, null, 1));
console.log(`${kind}: ${report.viewports.filter((v) => v.live).length} live viewport(s) of ${VIEWPORTS.length}, ${report.failures.length} failure(s)`);
for (const failure of report.failures) console.log('  ' + failure);
process.exit(report.failures.length ? 1 : 0);
