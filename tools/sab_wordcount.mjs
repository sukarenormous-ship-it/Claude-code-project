// นับคำบท docs/sab-partN.html ด้วย Intl.Segmenter('th') ในเบราว์เซอร์ (DOM จริง) → W17a / W17b / สัดส่วนเรื่องเล่า / เวลาอ่าน
//
//   node tools/sab_wordcount.mjs                # ทุกบท + รวมทั้งเล่ม (เกณฑ์เฟส 6)
//   node tools/sab_wordcount.mjs part4 part10   # เฉพาะบท
//   node tools/sab_wordcount.mjs --selftest
//
// เส้นทางหลัก = ทั้งหน้า ลบ: 🔎 details (deep/ans) · .sheet (ใบงานรวม 🔩 🔁 📱) · table.ledger · table.ncard ·
//               กล่อง 🔗 · กล่อง 📖 · ปก · script/style   (แผน 5.1 "งบคำ")
// เรื่องเล่า   = .scene-open + .scene ในเส้นทางหลัก (เพดาน 25%)
// เวลาอ่าน     = คำเส้นทางหลัก ÷ 80 คำ/นาที (วัดจากเล่ม nq)
// Playwright + Chromium ที่ติดตั้งในเครื่อง (ห้าม playwright install) · ตัดคำขอเครือข่ายทั้งหมด (ฟอนต์ไม่เกี่ยวกับการนับ)

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
export const WPM = 80;
export const MAIN_MIN = 1750, MAIN_MAX = 2200, PAGE_MAX = 3400, STORY_MAX = 0.25;

function countInPage() {
  const seg = new Intl.Segmenter('th', { granularity: 'word' });
  const words = (t) => { let n = 0; for (const s of seg.segment(t || '')) if (s.isWordLike) n++; return n; };
  const all = document.body.cloneNode(true);
  all.querySelectorAll('script,style,.cover').forEach((e) => e.remove());
  const page = words(all.textContent);
  const main = all.cloneNode(true);
  main.querySelectorAll('details,.sheet,table.ledger,table.ncard').forEach((e) => e.remove());
  main.querySelectorAll('.bx').forEach((e) => {
    const bt = e.querySelector('.bt');
    if (bt && /^\s*(🔗|📖)/.test(bt.textContent)) e.remove();
  });
  const mainWords = words(main.textContent);
  let story = 0;
  main.querySelectorAll('.scene-open,.scene').forEach((e) => { story += words(e.textContent); });
  return { page, main: mainWords, story };
}

export async function count(files) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.route('**/*', (r) => (r.request().url().startsWith('file:') ? r.continue() : r.abort()));
  const page = await ctx.newPage();
  const out = [];
  for (const f of files) {
    await page.goto('file://' + f, { waitUntil: 'load', timeout: 30000 });
    out.push({ file: path.basename(f), ...(await page.evaluate(countInPage)) });
  }
  await browser.close();
  return out;
}

export function judge(r) {
  const p = [];
  if (r.main < MAIN_MIN || r.main > MAIN_MAX) p.push(`W17a เส้นทางหลัก ${r.main} คำ (ต้อง ${MAIN_MIN}–${MAIN_MAX})`);
  if (r.page > PAGE_MAX) p.push(`W17b ทั้งหน้า ${r.page} คำ (เพดาน ${PAGE_MAX})`);
  if (r.main && r.story / r.main > STORY_MAX) p.push(`เรื่องเล่า ${(100 * r.story / r.main).toFixed(0)}% (เพดาน 25%)`);
  return p;
}

async function selftest() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'sabwc-'));
  const f = path.join(d, 'sab-part1.html');
  const w = (n) => Array.from({ length: n }, () => 'เงิน').join(' ');
  fs.writeFileSync(f, `<!DOCTYPE html><html><body><div class="cover">${w(50)}</div>
<div class="scene-open">${w(10)}</div><p>${w(30)}</p>
<details class="deep"><summary>x</summary>${w(100)}</details>
<div class="bx sheet">${w(40)}</div><div class="bx ba"><div class="bt">🔗 อยากลึก</div>${w(7)}</div>
<script>var x="${w(5)}"</script></body></html>`);
  const [r] = await count([f]);
  fs.rmSync(d, { recursive: true });
  // main = scene 10 + p 30 = 40 ; page = 40 + deep(100 + summary 'x' 1) + sheet 40 + 🔗 (7 + 'อยากลึก') ; story 10/40 = 25%
  const ok = r.main === 40 && r.story === 10 && r.page > 180 && judge(r).some((s) => s.startsWith('W17a'));
  console.log(ok ? 'selftest ผ่าน ✓ (ตัด 🔎/ใบงาน/🔗/ปก/script ออกจากเส้นทางหลัก · นับเรื่องเล่า)' : `selftest ไม่ผ่าน ✗ ${JSON.stringify(r)}`);
  return ok ? 0 : 1;
}

async function main() {
  const args = process.argv.slice(2);
  if (args[0] === '--selftest') process.exit(await selftest());
  let files = args.length
    ? args.map((a) => path.join(DOCS, `sab-${a}.html`))
    : fs.readdirSync(DOCS).filter((n) => /^sab-part\d+\.html$/.test(n))
        .sort((a, b) => parseInt(a.match(/\d+/)) - parseInt(b.match(/\d+/))).map((n) => path.join(DOCS, n));
  files = files.filter((f) => fs.existsSync(f));
  if (!files.length) { console.log('ยังไม่มีบท docs/sab-partN.html ให้นับ'); return; }
  const rows = await count(files);
  let bad = 0, totalMain = 0;
  for (const r of rows) {
    totalMain += r.main;
    const p = judge(r);
    bad += p.length;
    console.log(`${r.file}: เส้นทางหลัก ${r.main} คำ (~${Math.round(r.main / WPM)} นาที) · ทั้งหน้า ${r.page} · เรื่องเล่า ${r.main ? Math.round(100 * r.story / r.main) : 0}%`
      + (p.length ? '\n  - ' + p.join('\n  - ') : ' ✓'));
  }
  if (rows.length > 1) console.log(`รวม ${rows.length} บท: เส้นทางหลัก ${totalMain} คำ ≈ ${(totalMain / WPM / 60).toFixed(1)} ชม. (เกณฑ์เฟส 6 ≤ 8 ชม.)`);
  process.exit(bad ? 1 : 0);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await main();
