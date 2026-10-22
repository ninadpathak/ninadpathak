#!/usr/bin/env node
// Contact sheet of every share card: node contact.mjs <out.png> [columns]
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright-core';
import { REPO_DIR } from './lib/tokens.mjs';

const [out = path.join(REPO_DIR, 'review/image-brand/og-contact-sheet.png'), cols = '4'] = process.argv.slice(2);
const root = path.join(REPO_DIR, 'static/images/diagrams');
const cards = readdirSync(root).filter((d) => existsSync(path.join(root, d, 'og.png'))).sort();
const cell = (slug) => `<figure style="margin:0"><img src="data:image/png;base64,${readFileSync(path.join(root, slug, 'og.png')).toString('base64')}" style="display:block;width:360px;border:1px solid #e0e0dc"><figcaption style="font:500 10px ui-monospace,Menlo,monospace;letter-spacing:.06em;color:#6b6b6b;margin-top:6px">${slug}</figcaption></figure>`;
const html = `<!doctype html><body style="margin:0;background:#f8f8f6"><div id="s" style="display:inline-block;padding:32px">
<div style="font:500 12px ui-monospace,Menlo,monospace;letter-spacing:.12em;color:#c23b00;text-transform:uppercase;margin-bottom:20px">// share cards · ${cards.length} posts</div>
<div style="display:grid;grid-template-columns:repeat(${Number(cols)},360px);gap:24px 20px">${cards.map(cell).join('')}</div></div></body>`;
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1 })).newPage();
await page.setContent(html);
await page.locator('#s').screenshot({ path: out });
await browser.close();
console.log(`${cards.length} cards -> ${path.relative(REPO_DIR, out)}`);
