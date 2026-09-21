// Render book HTML pages to PDF using Playwright + Chromium.
//
// Usage:  node .claude/skills/knowledge-book/scripts/render-pdf.mjs [dir] [file1 file2 ...]
//   dir    — folder containing the .html pages (default: docs)
//   fileN  — base names without extension (default: every *.html in dir)
// Output:  <dir>/pdf/<name>.pdf  (one per chapter)
//
// Requires Playwright (in this environment Chromium is pre-installed and
// found via PLAYWRIGHT_BROWSERS_PATH — do NOT run `playwright install`).
// printBackground keeps the coloured boxes; the wait lets the
// Intl.Segmenter <wbr> injection settle so Thai line-breaks render the
// same as in the browser.
//
// ⚠️ KaTeX crash workaround (เจอจริงกับ python-part0 / python-part5)
// Chromium ในสภาพแวดล้อมนี้ crash ("Target crashed") ตอน layout ของ
// KaTeX HTML output บางหน้า · พิสูจน์แล้วว่าเกิดจาก KaTeX CSS + DOM
// ร่วมกัน: บล็อก CSS อย่างเดียวก็หาย · บล็อก JS อย่างเดียวก็หาย ·
// ทุกสูตรในหน้านั้นพังหมดแม้สูตรง่ายที่สุด (จึงไม่ใช่สูตรใดผิด) ·
// ลองทุก launch flag และทั้ง chromium กับ headless-shell ได้ผลเหมือนกัน
//
// ทางแก้: ถ้าหน้าไหน crash ให้ลองใหม่โดยบล็อก KaTeX CSS + auto-render
// แล้วเรียก katex.renderToString(..., {output:'mathml'}) เอง —
// Chromium เรนเดอร์ MathML ได้เองโดยไม่ต้องใช้ CSS ของ KaTeX จึงไม่ crash

import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';

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

const PDF_OPTS = {
  format: 'A4', printBackground: true,
  margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' },
};

// แปลงสูตรเป็น MathML ด้วยตัวเอง (ใช้เมื่อ auto-render ทำให้ crash)
// ⚠️ ต้องรองรับทั้ง $$...$$ (display) และ \(...\) (inline) — หนังสือใช้ทั้งคู่
// ถ้าทำแค่ $$ อย่างเดียว inline จะโผล่เป็น LaTeX ดิบใน PDF
const renderMathML = () => {
  if (typeof katex === 'undefined') return 0;

  // สคริปต์ตัดคำไทยแทรก <wbr> เข้าไปกลางข้อความ ทำให้ text node ถูกผ่า
  // สูตรที่มีภาษาไทยข้างใน (เช่น \text{น้ำหนัก}) จึงจับไม่ติด
  // ⚠️ ลบ <wbr> เฉพาะ element ที่มีสูตรเท่านั้น — ถ้าลบทั้งหน้า การตัดคำไทย
  //    จะหายไปทั้งเล่ม ซึ่งคือปัญหาที่สคริปต์นั้นมีไว้แก้พอดี
  document.querySelectorAll('wbr').forEach(w => {
    const host = w.parentElement;
    if (host && /\$\$|\\\(/.test(host.textContent)) w.remove();
  });
  document.body.normalize();

  const SKIP = { SCRIPT: 1, STYLE: 1, TEXTAREA: 1, CODE: 1, PRE: 1 };
  // display $$...$$  |  inline \(...\)
  const RX = /\$\$([\s\S]+?)\$\$|\\\(([\s\S]+?)\\\)/g;
  let count = 0;

  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      for (let el = n.parentNode; el && el.nodeType === 1; el = el.parentNode) {
        if (SKIP[el.tagName]) return NodeFilter.FILTER_REJECT;
        if (el.classList && el.classList.contains('fm')) return NodeFilter.FILTER_REJECT;
      }
      return /\$\$|\\\(/.test(n.nodeValue)
        ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    },
  });
  const targets = [];
  let node;
  while ((node = walk.nextNode())) targets.push(node);

  for (const t of targets) {
    const src = t.nodeValue;
    RX.lastIndex = 0;
    let m, last = 0;
    const frag = document.createDocumentFragment();
    while ((m = RX.exec(src))) {
      const isDisplay = m[1] !== undefined;
      const tex = (isDisplay ? m[1] : m[2]).trim();
      if (!tex) continue;
      if (m.index > last) {
        frag.appendChild(document.createTextNode(src.slice(last, m.index)));
      }
      const span = document.createElement('span');
      try {
        span.innerHTML = katex.renderToString(tex, {
          output: 'mathml', throwOnError: false, displayMode: isDisplay,
        });
        count++;
      } catch { span.textContent = m[0]; }
      frag.appendChild(span);
      last = m.index + m[0].length;
    }
    if (!last) continue;                      // ไม่เจอสูตรจริง — อย่าแตะ node
    if (last < src.length) {
      frag.appendChild(document.createTextNode(src.slice(last)));
    }
    t.parentNode.replaceChild(frag, t);
  }
  return count;
};

const browser = await chromium.launch({
  args: ['--no-sandbox', '--disable-dev-shm-usage'],
});

let ok = 0, viaMathml = 0;
const failed = [];

for (const f of files) {
  const url = 'file://' + path.join(dir, f + '.html');
  const out = path.join(dir, 'pdf', f + '.pdf');

  // ── รอบที่ 1: ปกติ (KaTeX HTML output) ──
  let done = false;
  let page = await browser.newPage();
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await document.fonts.ready;
    });
    await page.waitForTimeout(400);
    await page.pdf({ path: out, ...PDF_OPTS });
    console.log('ok        ' + f);
    ok++; done = true;
  } catch (e) {
    console.log('retry     ' + f + '  (' + String(e).split('\n')[0].slice(0, 45) + ')');
  }
  await page.close().catch(() => {});

  if (done) continue;

  // ── รอบที่ 2: เลี่ยง KaTeX CSS/auto-render แล้วเรนเดอร์เป็น MathML ──
  page = await browser.newPage();
  await page.route('**/katex.min.css', r => r.abort());
  await page.route('**/auto-render*', r => r.abort());
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(300);
    const n = await page.evaluate(renderMathML);
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await document.fonts.ready;
    });
    await page.waitForTimeout(600);
    await page.pdf({ path: out, ...PDF_OPTS });
    console.log('ok/mathml ' + f + '  (' + n + ' สูตร)');
    ok++; viaMathml++;
  } catch (e) {
    console.log('FAIL      ' + f + '  ' + String(e).split('\n')[0].slice(0, 60));
    failed.push(f);
  }
  await page.close().catch(() => {});
}

await browser.close();
console.log(`\nDONE  สำเร็จ ${ok}/${files.length}` +
            (viaMathml ? `  (ใช้ทาง MathML ${viaMathml})` : '') +
            (failed.length ? `  ล้มเหลว: ${failed.join(', ')}` : ''));
if (failed.length) process.exitCode = 1;
