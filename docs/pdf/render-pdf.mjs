// Render every book page to PDF using Playwright + Chromium.
//
// Usage:  node docs/pdf/render-pdf.mjs
// Output: docs/pdf/<name>.pdf  (one per chapter)
//
// Requires Playwright (globally installed in this environment at
// /opt/node22/lib/node_modules). Chromium is found automatically via
// PLAYWRIGHT_BROWSERS_PATH. printBackground keeps the coloured boxes;
// the 400ms wait lets the Intl.Segmenter <wbr> injection settle so Thai
// line-breaks render the same as in the browser.

import { createRequire } from 'module';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
// Prefer a locally-resolvable Playwright; fall back to the global install.
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright/index.js')); }

const docs = path.dirname(fileURLToPath(import.meta.url)) + '/..';
const files = [
  'index', 'notation',
  'theory-part1', 'theory-part2', 'theory-part3', 'theory-part4', 'theory-part5', 'theory-part6', 'theory-extra',
  'pillars-part1', 'pillars-part2', 'pillars-part3', 'pillars-part4', 'pillars-part5',
];

const browser = await chromium.launch();
const page = await browser.newPage();
for (const f of files) {
  await page.goto('file://' + path.join(docs, f + '.html'), { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(async () => { if (document.fonts && document.fonts.ready) await document.fonts.ready; });
  await page.waitForTimeout(400);
  await page.pdf({
    path: path.join(docs, 'pdf', f + '.pdf'),
    format: 'A4', printBackground: true,
    margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' },
  });
  console.log('ok ' + f);
}
await browser.close();
console.log('DONE ' + files.length + ' files');
