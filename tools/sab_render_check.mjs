// R1: เปิดทุกหน้า docs/sab-*.html ที่กว้าง 1000 px และ 420 px แล้วตรวจ
//   - page error (JS พัง) · console error
//   - ล้นแนวนอน "ระดับหน้า" (documentElement.scrollWidth > ความกว้างจอ) — ตารางใน .tw ล้นระดับ element โดยตั้งใจ จึงไม่นับ
//   - SVG ว่าง (ไม่มีลูก หรือกว้าง/สูง 0)
//
//   node tools/sab_render_check.mjs              # ทุกหน้า sab-*
//   node tools/sab_render_check.mjs part4 index  # เฉพาะหน้า
//   node tools/sab_render_check.mjs --selftest
//
// Playwright + Chromium ที่ติดตั้งในเครื่อง (ห้าม playwright install) · ตัดคำขอเครือข่ายภายนอก (ฟอนต์) เพื่อให้รันออฟไลน์ได้

import { createRequire } from 'module';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright/index.js')); }

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const DOCS = path.join(ROOT, 'docs');
const WIDTHS = [1000, 420];

async function check(files) {
  const browser = await chromium.launch();
  const problems = [];
  for (const width of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 } });
    await ctx.route('**/*', (r) => (r.request().url().startsWith('file:') ? r.continue() : r.abort()));
    const page = await ctx.newPage();
    for (const f of files) {
      const name = path.basename(f);
      const errs = [];
      const onErr = (e) => errs.push(`page error: ${e.message}`);
      const onCon = (m) => { if (m.type() === 'error' && !/ERR_FAILED|net::/.test(m.text())) errs.push(`console: ${m.text()}`); };
      page.on('pageerror', onErr);
      page.on('console', onCon);
      await page.goto('file://' + f, { waitUntil: 'load', timeout: 30000 });
      await page.waitForTimeout(300);
      const r = await page.evaluate(() => {
        const sw = document.documentElement.scrollWidth, cw = document.documentElement.clientWidth;
        const empty = [...document.querySelectorAll('svg')].filter((s) => {
          const b = s.getBoundingClientRect();
          return !s.children.length || b.width === 0 || b.height === 0;
        }).length;
        return { sw, cw, empty };
      });
      page.off('pageerror', onErr);
      page.off('console', onCon);
      for (const e of errs) problems.push(`${name} @${width}px: ${e}`);
      if (r.sw > r.cw + 1) problems.push(`${name} @${width}px: ล้นแนวนอนระดับหน้า (${r.sw} > ${r.cw})`);
      if (r.empty) problems.push(`${name} @${width}px: SVG ว่าง ${r.empty} รูป`);
    }
    await ctx.close();
  }
  await browser.close();
  return problems;
}

async function selftest() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'sabrc-'));
  const good = path.join(d, 'sab-good.html');
  const bad = path.join(d, 'sab-bad.html');
  fs.writeFileSync(good, '<!DOCTYPE html><html><body><div class="tw" style="overflow-x:auto"><table style="min-width:900px"><tr><td>x</td></tr></table></div>'
    + '<svg viewBox="0 0 10 10" width="100" height="50"><rect width="5" height="5"/></svg></body></html>');
  fs.writeFileSync(bad, '<!DOCTYPE html><html><body><div style="width:1400px">กว้างเกิน</div><svg width="100" height="50"></svg>'
    + '<script>undefinedFn()</script></body></html>');
  const p = await check([good, bad]);
  fs.rmSync(d, { recursive: true });
  const ok = !p.some((s) => s.startsWith('sab-good'))
    && ['ล้นแนวนอน', 'SVG ว่าง', 'page error'].every((k) => p.some((s) => s.startsWith('sab-bad') && s.includes(k)));
  console.log(ok ? 'selftest ผ่าน ✓ (จับล้นหน้า · SVG ว่าง · page error · ตารางใน .tw ไม่ถูกฟ้อง)' : 'selftest ไม่ผ่าน ✗\n' + p.join('\n'));
  return ok ? 0 : 1;
}

const args = process.argv.slice(2);
if (args[0] === '--selftest') process.exit(await selftest());
let files = args.length
  ? args.map((a) => path.join(DOCS, `sab-${a}.html`))
  : fs.readdirSync(DOCS).filter((n) => /^sab-.*\.html$/.test(n)).sort().map((n) => path.join(DOCS, n));
files = files.filter((f) => fs.existsSync(f));
if (!files.length) { console.log('ยังไม่มีหน้า docs/sab-*.html ให้ตรวจ'); process.exit(0); }
const problems = await check(files);
console.log(`ตรวจ ${files.length} หน้า × ${WIDTHS.join('/')} px`);
if (problems.length) { console.log(`พบปัญหา ${problems.length} ข้อ`); problems.forEach((p) => console.log('  -', p)); process.exit(1); }
console.log('ผ่าน ✓');
