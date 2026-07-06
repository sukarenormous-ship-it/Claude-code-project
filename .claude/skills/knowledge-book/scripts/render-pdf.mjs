// Render book HTML pages to PDF using Playwright + Chromium.
//
// Usage:  node .claude/skills/knowledge-book/scripts/render-pdf.mjs [dir] [file1 file2 ...]
//   dir    — folder containing the .html pages (default: docs)
//   fileN  — base names without extension (default: every *.html in dir)
// Output:  <dir>/pdf/<name>.pdf  (one per chapter)
//
// Requires Playwright (in this environment Chromium is pre-installed and
// found via PLAYWRIGHT_BROWSERS_PATH — do NOT run `playwright install`).
// printBackground keeps the coloured boxes; the 400ms wait lets the
// Intl.Segmenter <wbr> injection settle so Thai line-breaks render the
// same as in the browser.

import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright/index.js')); }

const args = process.argv.slice(2);
const dir = path.resolve(args[0] || 'docs');
const named = args.slice(1);
const files = named.length
  ? named
  : fs.readdirSync(dir).filter(f => f.endsWith('.html')).map(f => f.replace(/\.html$/, '')).sort();

fs.mkdirSync(path.join(dir, 'pdf'), { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage();
for (const f of files) {
  await page.goto('file://' + path.join(dir, f + '.html'), { waitUntil: 'networkidle', timeout: 60000 });
  await page.evaluate(async () => { if (document.fonts && document.fonts.ready) await document.fonts.ready; });
  await page.waitForTimeout(400);
  await page.pdf({
    path: path.join(dir, 'pdf', f + '.pdf'),
    format: 'A4', printBackground: true,
    margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' },
  });
  console.log('ok ' + f);
}
await browser.close();
console.log('DONE ' + files.length + ' files');
