#!/usr/bin/env node
// Code-block script behaviour that a static sweep can't see.
//
//   node tools/codeblocks_behaviour.mjs <article-url>
//
// 1. A scroll block that fits at 1366 but overflows at 375 gains tabindex, role="region"
//    and an aria-label when the viewport narrows, and loses them when it widens again.
// 2. When the clipboard rejects a write, the live region says so and clears itself.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const { chromium } = await import(path.join(here, 'image-brand/node_modules/playwright-core/index.mjs'));
const url = process.argv[2];
const b = await chromium.launch();
const ctx = await b.newContext({ viewport: { width: 1366, height: 900 } });
await ctx.route((u) => !/^https?:\/\/(127\.0\.0\.1|localhost|fonts\.(googleapis|gstatic)\.com)[:/]/.test(u.href), (r) => r.abort());
const p = await ctx.newPage();
await p.goto(url, { waitUntil: 'load' });
await p.evaluate(() => document.fonts.ready.then(() => true));
const state = () => p.evaluate(() => [...document.querySelectorAll('.code-block--scroll pre')].map((pre) => ({ over: pre.scrollWidth > pre.clientWidth + 1, tab: pre.getAttribute('tabindex'), role: pre.getAttribute('role'), label: pre.getAttribute('aria-label') })));
const consistent = (s) => s.every((x) => (x.over ? x.tab === '0' && x.role === 'region' && !!x.label : x.tab === null && x.role === null && x.label === null));
const wide1 = await state();
await p.setViewportSize({ width: 375, height: 900 }); await p.waitForTimeout(400);
const narrow = await state();
await p.setViewportSize({ width: 1366, height: 900 }); await p.waitForTimeout(400);
const wide2 = await state();
const flipped = wide1.filter((x, i) => !x.over && narrow[i].over).length;
const resize = { blocks: wide1.length, overflowWide: wide1.filter((x) => x.over).length, overflowNarrow: narrow.filter((x) => x.over).length, flipped, consistent: consistent(wide1) && consistent(narrow) && consistent(wide2) };

// Make the clipboard reject.
await p.evaluate(() => { navigator.clipboard.writeText = () => Promise.reject(new Error('denied')); });
const block = p.locator('.code-block').first();
await block.locator('.code-copy').click();
await p.waitForTimeout(200);
const failMsg = await block.locator('.code-copy-status').textContent();
await p.waitForTimeout(4300);
const afterMsg = await block.locator('.code-copy-status').textContent();
const failure = { shown: failMsg, clearedAfter4s: afterMsg === '' };
console.log(JSON.stringify({ resize, failure }));
await b.close();
process.exit(resize.consistent && resize.flipped > 0 && failMsg.startsWith('Copy failed') && afterMsg === '' ? 0 : 1);
