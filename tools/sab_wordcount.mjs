// นับคำบท docs/sab-partN.html และหน้าพื้นฐาน docs/sab-baseN.html ด้วย Intl.Segmenter('th') ในเบราว์เซอร์ (DOM จริง)
// → W17a / W17b / W17c / สัดส่วนเรื่องเล่า / เวลาอ่าน
//
//   node tools/sab_wordcount.mjs                # หน้าพื้นฐาน + ทุกบท + รวมทั้งเล่ม
//   node tools/sab_wordcount.mjs part4 base1    # เฉพาะหน้า
//   node tools/sab_wordcount.mjs --as-v2 part4  # ตัดสินด้วยเกณฑ์ v2 แม้หน้ายังเป็น v1 (ใช้โดย sab_migrate_v2.py)
//   node tools/sab_wordcount.mjs --selftest
//   node tools/sab_wordcount.mjs --book sab2     # เล่ม 2: docs/sab2-partN.html (หรือ SAB_BOOK=sab2)
//     เกณฑ์เล่ม 2: เส้นทางหลัก ≥ 5000 (ไม่มีเพดานแข็ง) · คำต่อตอนเกิน 3000 เตือนทุกบท (ไม่ล้ม) · สัดส่วน/เรื่องเล่าเหมือน v2 เล่ม 1
//
// หน้า v1 (ยังไม่ย้าย · แผน 5.1 "งบคำ")
//   เส้นทางหลัก = ทั้งหน้า ลบ: 🔎 details (deep/ans) · .sheet (ใบงานรวม 🔩 🔁 📱) · table.ledger · table.ncard ·
//                 กล่อง 🔗 · กล่อง 📖 · ปก · script/style
//   เกณฑ์: เส้นทางหลัก 1750–2300 · ทั้งหน้า ≤ 3500 · เรื่องเล่า ≤ 25%
// หน้า v2 (<body data-tpl="2"> และหน้า sab-baseN.html ทุกหน้า · แผน 14.4)
//   เส้นทางหลัก = ทั้งหน้า ลบ: details ทุกชนิด (hint/ans/deep/file) · .sheet · table.ledger · table.ncard · กล่อง 📖 · ปก · script/style
//   เกณฑ์: เส้นทางหลัก ≥ 2800 ไม่มีเพดานแข็ง (เกิน 6000 เตือน "⚠ ยาว แบ่งตอน" ไม่ล้ม) · หน้าพื้นฐาน 1200–2600 ·
//          เส้นทางหลัก ÷ ทั้งหน้า ≥ 65% · เรื่องเล่า ≤ 20%
// เรื่องเล่า   = .scene-open + .scene ในเส้นทางหลัก
// เวลาอ่าน     = คำเส้นทางหลัก ÷ 80 คำ/นาที (วัดจากเล่ม nq) — v2 รายงานไว้เฉย ๆ ไม่มีเป้า
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
// เลือกเล่ม: --book sab2 หรือ SAB_BOOK=sab2 (ค่าเริ่มต้น sab = เล่ม 1) — หน้า docs/<prefix>-partN.html
const bi = process.argv.indexOf('--book');
if (bi >= 0) { process.env.SAB_BOOK = process.argv[bi + 1]; process.argv.splice(bi, 2); }
export const PREFIX = process.env.SAB_BOOK || 'sab';
if (!/^sab2?$/.test(PREFIX)) { console.error(`SAB_BOOK / --book ต้องเป็น sab หรือ sab2 (พบ ${PREFIX})`); process.exit(2); }
export const WPM = 80;
export const MAIN_MIN = 1750, MAIN_MAX = 2300, PAGE_MAX = 3500, STORY_MAX = 0.25;                       // v1
export const V2_BOOK1 = { MAIN_MIN: 2800, BASE_MIN: 1200, BASE_MAX: 2600, SHARE_MIN: 0.65, STORY_MAX: 0.20, LONG: 6000, PART_MAX: 3500 };   // แผน 14.4
// เล่ม 2 (sab2): บทยาว 3–4 ตอน (แผน sab2 หัวข้อ 4: 6,000–9,000 คำต่อบท) → เส้นทางหลัก ≥ 5000 · ตรวจคำต่อตอนทุกบท (เกิน 3000 เตือน) · ไม่มีเพดานแข็ง
export const V2_BOOK2 = { ...V2_BOOK1, MAIN_MIN: 5000, PART_MAX: 3000, PARTS_ALWAYS: true };
export const V2 = PREFIX === 'sab2' ? V2_BOOK2 : V2_BOOK1;
const isBase = (name) => new RegExp(`^${PREFIX}-base\\d+\\.html$`).test(name);

function countInPage(forceV2) {
  const v2 = forceV2 || document.body.getAttribute('data-tpl') === '2';
  const seg = new Intl.Segmenter('th', { granularity: 'word' });
  const words = (t) => { let n = 0; for (const s of seg.segment(t || '')) if (s.isWordLike) n++; return n; };
  const all = document.body.cloneNode(true);
  all.querySelectorAll('script,style,.cover').forEach((e) => e.remove());
  if (v2) all.querySelectorAll('svg').forEach((e) => e.remove());   // v2: ข้อความในกราฟไม่ใช่คำที่อ่านเป็นร้อยแก้ว
  const page = words(all.textContent);
  const main = all.cloneNode(true);
  main.querySelectorAll('details,.sheet,table.ledger,table.ncard').forEach((e) => e.remove());
  main.querySelectorAll('.bx').forEach((e) => {
    const bt = e.querySelector('.bt');
    if (bt && (v2 ? /^\s*📖/ : /^\s*(🔗|📖)/).test(bt.textContent)) e.remove();   // v2: ลิงก์อ่านลึกอยู่ใน details.file แล้ว
  });
  const mainWords = words(main.textContent);
  let story = 0;
  main.querySelectorAll('.scene-open,.scene').forEach((e) => { story += words(e.textContent); });
  // คำต่อ "ตอน" (h2 ที่ขึ้นต้น "ตอน ก/ข/ค…") — บทยาวที่แบ่งตอนแล้วตัดสินทีละตอน
  const parts = {};
  let cur = null;
  const tw = document.createTreeWalker(main, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
  for (let nd = tw.nextNode(); nd; nd = tw.nextNode()) {
    if (nd.nodeType === 1) {
      if (nd.tagName === 'H2') { const m = nd.textContent.match(/^\s*ตอน\s*([ก-ฮ])/); if (m) cur = m[1]; }
      else if (nd.classList && (nd.classList.contains('sum3') || (nd.classList.contains('bg') && /✍️/.test(nd.textContent)))) cur = null;
      continue;
    }
    if (cur) parts[cur] = (parts[cur] || 0) + words(nd.textContent);
  }
  return { page, main: mainWords, story, v2, parts };
}

export async function count(files, asV2 = false) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  await ctx.route('**/*', (r) => (r.request().url().startsWith('file:') ? r.continue() : r.abort()));
  const page = await ctx.newPage();
  const out = [];
  for (const f of files) {
    await page.goto('file://' + f, { waitUntil: 'load', timeout: 30000 });
    const base = isBase(path.basename(f));
    out.push({ file: path.basename(f), base, ...(await page.evaluate(countInPage, asV2 || base)) });
  }
  await browser.close();
  return out;
}

const pct = (a, b) => (b ? Math.round(100 * a / b) : 0);

export function judge(r) {
  const p = [];
  if (r.v2) {
    if (r.base) {
      if (r.main < V2.BASE_MIN || r.main > V2.BASE_MAX) p.push(`W17a เส้นทางหลัก ${r.main} คำ (หน้าพื้นฐานต้อง ${V2.BASE_MIN}–${V2.BASE_MAX})`);
    } else if (r.main < V2.MAIN_MIN) p.push(`W17a เส้นทางหลัก ${r.main} คำ (v2 ต้อง ≥ ${V2.MAIN_MIN})`);
    if (!r.page || r.main / r.page < V2.SHARE_MIN) p.push(`W17c เส้นทางหลักเป็น ${pct(r.main, r.page)}% ของทั้งหน้า (v2 ต้อง ≥ ${100 * V2.SHARE_MIN}%)`);
    if (r.main && r.story / r.main > V2.STORY_MAX) p.push(`เรื่องเล่า ${pct(r.story, r.main)}% (เพดาน ${100 * V2.STORY_MAX}%)`);
    return p;
  }
  if (r.main < MAIN_MIN || r.main > MAIN_MAX) p.push(`W17a เส้นทางหลัก ${r.main} คำ (ต้อง ${MAIN_MIN}–${MAIN_MAX})`);
  if (r.page > PAGE_MAX) p.push(`W17b ทั้งหน้า ${r.page} คำ (เพดาน ${PAGE_MAX})`);
  if (r.main && r.story / r.main > STORY_MAX) p.push(`เรื่องเล่า ${(100 * r.story / r.main).toFixed(0)}% (เพดาน 25%)`);
  return p;
}

// ข้อสังเกตที่ไม่ทำให้ล้ม (แผน 14.4: ไม่มีเพดานแข็ง แต่บทยาวต้องแบ่งตอน)
export function notes(r) {
  if (!r.v2 || r.base) return [];
  const ps = Object.entries(r.parts || {});
  if (ps.length < 2) return r.main > V2.LONG ? [`⚠ ยาว แบ่งตอน (เส้นทางหลัก ${r.main} คำ เกิน ${V2.LONG} และยังไม่แบ่งตอน)`] : [];
  if (!V2.PARTS_ALWAYS && r.main <= V2.LONG) return [];                 // เล่ม 1: ดูคำต่อตอนเฉพาะบทที่ยาวเกิน LONG · เล่ม 2: ทุกบท
  const big = ps.filter(([, w]) => w > V2.PART_MAX);
  return big.length ? big.map(([k, w]) => `⚠ ตอน ${k} ยาว ${w} คำ (เกิน ${V2.PART_MAX}) แบ่งย่อยได้`) : [];
}

async function selftest() {
  const d = fs.mkdtempSync(path.join(os.tmpdir(), 'sabwc-'));
  const f = path.join(d, `${PREFIX}-part1.html`);
  const w = (n) => Array.from({ length: n }, () => 'เงิน').join(' ');
  fs.writeFileSync(f, `<!DOCTYPE html><html><body><div class="cover">${w(50)}</div>
<div class="scene-open">${w(10)}</div><p>${w(30)}</p>
<details class="deep"><summary>x</summary>${w(100)}</details>
<div class="bx sheet">${w(40)}</div><div class="bx ba"><div class="bt">🔗 อยากลึก</div>${w(7)}</div>
<script>var x="${w(5)}"</script></body></html>`);
  // v2: เส้นทางหลัก = pos 10 + ฉากเปิด 20 + p 70 + กล่อง 🔗 นอกแฟ้ม (หัว 1 + 7) = 108 · เรื่องเล่า 20
  //     ทั้งหน้า = 108 + 📖 (1 + 9) + hint (1 + 30) + ans (1 + 30) + แฟ้ม (1 + ใบงาน 40 + บัญชี 20 + p 15) + ใบงานนอกแฟ้ม 12 + บัตร 8 = 276
  const v2body = `<div class="cover">${w(50)}</div><p class="pos">${w(10)}</p>
<div class="scene-open">${w(20)}</div><p>${w(70)}</p>
<div class="bx ba"><div class="bt">🔗 เงิน</div>${w(7)}</div><div class="bx bb"><div class="bt">📖 เงิน</div>${w(9)}</div>
<ol><li><details class="hint"><summary>เงิน</summary>${w(20)}<details class="hint"><summary>เงิน</summary>${w(9)}</details></details>
<details class="ans"><summary>เงิน</summary>${w(30)}</details></li></ol>
<details class="file"><summary>เงิน</summary><div class="bx sheet">${w(40)}</div><table class="ledger"><tr><td>${w(20)}</td></tr></table><p>${w(15)}</p></details>
<div class="bx sheet">${w(12)}</div><table class="ncard"><tr><td>${w(8)}</td></tr></table>
<script>var x="${w(5)}"</script>`;
  const f2 = path.join(d, `${PREFIX}-part2.html`), fb = path.join(d, `${PREFIX}-base1.html`);
  fs.writeFileSync(f2, `<!DOCTYPE html><html><body data-tpl="2">${v2body}</body></html>`);
  fs.writeFileSync(fb, `<!DOCTYPE html><html><body>${v2body}</body></html>`);          // หน้า base = v2 เสมอ แม้ไม่มีป้าย
  const [r] = await count([f]);
  const [r2, rb] = await count([f2, fb]);
  const [rf] = await count([f], true);                                                  // --as-v2 กับหน้า v1: กล่อง 🔗 กลับมานับ
  fs.rmSync(d, { recursive: true });
  // main = scene 10 + p 30 = 40 ; page = 40 + deep(100 + summary 'x' 1) + sheet 40 + 🔗 (7 + 'อยากลึก') ; story 10/40 = 25%
  const v1ok = r.main === 40 && r.story === 10 && r.page > 180 && !r.v2 && judge(r).some((s) => s.startsWith('W17a'));
  const row = (o) => ({ v2: true, base: false, main: 3000, page: 4000, story: 100, ...o });
  const fails = (o, key) => judge(row(o)).some((s) => s.includes(key));
  const v2ok = r2.v2 && !r2.base && r2.main === 108 && r2.story === 20 && r2.page === 276
    && rb.v2 && rb.base && rb.main === 108 && rf.v2 && rf.main > 40
    && ['W17a', 'W17c'].every((k) => judge(r2).some((s) => s.startsWith(k))) && !judge(r2).some((s) => s.startsWith('เรื่องเล่า'))
    && judge(row({ main: V2.MAIN_MIN, page: V2.MAIN_MIN / 0.7, story: V2.MAIN_MIN * 0.2 })).length === 0   // พอดีเกณฑ์: MAIN_MIN คำ · 70% · เรื่องเล่า 20%
    && fails({ main: V2.MAIN_MIN - 1 }, 'W17a') && fails({ page: 5000 }, 'W17c') && fails({ story: 601 }, 'เรื่องเล่า')
    && judge(row({ main: 9500, page: 12000 })).length === 0 && notes(row({ main: 9500, page: 12000 })).length === 1   // ยาว = เตือน ไม่ล้ม
    && notes(row({ main: 9500, page: 12000, parts: { ก: 3000, ข: 3000, ค: 3600 } })).length === 1                       // ตอนที่เกิน PART_MAX เท่านั้น
    && (PREFIX !== 'sab2' || notes(row({ main: 5200, page: 7000, parts: { ก: 3100, ข: 2100 } })).length === 1)          // เล่ม 2: ตรวจตอนทุกบท
    && notes(row({ main: Math.max(3000, V2.MAIN_MIN) })).length === 0
    && fails({ base: true, main: 1199, page: 1500 }, 'W17a') && fails({ base: true, main: 2601, page: 3000 }, 'W17a')
    && judge(row({ base: true, main: 2000, page: 2500 })).length === 0
    && judge({ v2: false, main: 2000, page: 3000, story: 100 }).length === 0 && judge({ v2: false, main: 2800, page: 3000, story: 100 }).some((s) => s.startsWith('W17a'));
  const ok = v1ok && v2ok;
  console.log(ok ? 'selftest ผ่าน ✓ (ตัด 🔎/ใบงาน/🔗/ปก/script ออกจากเส้นทางหลัก · นับเรื่องเล่า · v2: ตัด details ทุกชนิด/ใบงาน/บัญชี/บัตร/📖 · '
    + `เกณฑ์ ≥ ${V2.MAIN_MIN} · ≥ 65% · เรื่องเล่า ≤ 20% · ตอนเกิน ${V2.PART_MAX} เตือนไม่ล้ม · หน้า base 1200–2600 · หน้า v1 ใช้เกณฑ์เดิม · เล่ม ${PREFIX})`
    : `selftest ไม่ผ่าน ✗ ${JSON.stringify({ r, r2, rb, rf })}`);
  return ok ? 0 : 1;
}

async function main() {
  const args = process.argv.slice(2);
  if (args[0] === '--selftest') process.exit(await selftest());
  const asV2 = args.includes('--as-v2');
  const names = args.filter((a) => !a.startsWith('--'));
  const num = (n) => parseInt(n.match(/\d+/));
  const byNum = (re) => fs.readdirSync(DOCS).filter((n) => re.test(n)).sort((a, b) => num(a) - num(b));
  let files = names.length
    ? names.map((a) => path.join(DOCS, `${PREFIX}-${a}.html`))
    : [...byNum(new RegExp(`^${PREFIX}-base\\d+\\.html$`)), ...byNum(new RegExp(`^${PREFIX}-part\\d+\\.html$`))].map((n) => path.join(DOCS, n));   // หน้าพื้นฐานมาก่อนบท 0
  files = files.filter((f) => fs.existsSync(f));
  if (!files.length) { console.log(`ยังไม่มีบท docs/${PREFIX}-partN.html ให้นับ`); return; }
  const rows = await count(files, asV2);
  let bad = 0, totalMain = 0;
  for (const r of rows) {
    totalMain += r.main;
    const p = judge(r);
    bad += p.length;
    const tail = [...p.map((x) => '\n  - ' + x), ...notes(r).map((x) => '\n  ' + x)].join('');
    console.log(`${r.file}: ${r.v2 ? '[v2] ' : ''}เส้นทางหลัก ${r.main} คำ (~${Math.round(r.main / WPM)} นาที) · ทั้งหน้า ${r.page}`
      + (r.v2 ? ` · เส้นทางหลัก ${pct(r.main, r.page)}% ของหน้า` : '') + ` · เรื่องเล่า ${pct(r.story, r.main)}%`
      + (p.length ? tail : ' ✓' + tail));
  }
  if (rows.length > 1) {
    const hours = (totalMain / WPM / 60).toFixed(1);
    console.log(rows.some((r) => r.v2)
      ? `รวม ${rows.length} หน้า: เส้นทางหลัก ${totalMain} คำ ≈ ${hours} ชม. (v2: รายงานเวลาไว้เฉย ๆ · แผน 14.4 ไม่มีเป้าเวลา)`
      : `รวม ${rows.length} บท: เส้นทางหลัก ${totalMain} คำ ≈ ${hours} ชม. (เกณฑ์เฟส 6 ≤ 8 ชม.)`);
  }
  process.exit(bad ? 1 : 0);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) await main();
