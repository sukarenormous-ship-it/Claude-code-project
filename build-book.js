/**
 * build-book.js — ประกอบ docs/arb-part*.html เป็นหนังสือเล่มเดียว
 *   ผลลัพธ์: docs/arb-book.html และ docs/arb-book.pdf (หน้าปก + สารบัญ + เลขหน้าต่อเนื่อง)
 *
 * รัน:  node build-book.js
 */
const fs = require('fs');
const path = require('path');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const DOCS = path.join(__dirname, 'docs');
const PARTS = [
  ['arb-part1.html',  'Part I',    'รากฐาน',                  'บท 1–3'],
  ['arb-part2a.html', 'Part II-A', 'วิธีคิดแบบ Arbitrageur',   'บท 4–6'],
  ['arb-part2b.html', 'Part II-B', 'Taxonomy & Discovery',    'บท 7–10'],
  ['arb-part3.html',  'Part III',  'Options Arbitrage',       'บท 11–14'],
  ['arb-part4.html',  'Part IV',   'Cross-Market Arbitrage',  'บท 15–17'],
  ['arb-part5.html',  'Part V',    'Statistical Arbitrage',   'บท 18–21'],
  ['arb-part6.html',  'Part VI',   'Merger & Event Arbitrage','บท 22–24'],
  ['arb-part7.html',  'Part VII',  'Execution & Risk',        'บท 25–27'],
  ['arb-part8.html',  'Part VIII', 'ฝึกตา · PM · Alt Data',   'บท 28–31'],
  ['arb-part9.html',  'Part IX',   'กรณีศึกษา & Cheat Sheet', 'บท 32–33'],
];

const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// ---------- ดึงเฉพาะเนื้อใน <body>, ตัดหน้าปกของแต่ละ Part และท้ายบท ----------
function extractBody(html) {
  let b = html.slice(html.indexOf('<body>') + 6, html.lastIndexOf('</body>'));
  b = b.replace(/<div class="cover">[\s\S]*?<\/div>\s*<\/div>/, '');       // cover (nested)
  b = b.replace(/<div class="cover">[\s\S]*?<div class="desc">[\s\S]*?<\/div>\s*<\/div>/, '');
  b = b.replace(/<hr style="margin:40px 0[^>]*>\s*<div style="text-align:center[\s\S]*$/, ''); // footer
  b = b.replace(/<script[\s\S]*?<\/script>/g, '');
  return b.trim();
}

// ---------- รวม CSS ของทุก Part (ใช้ชุดที่สมบูรณ์ที่สุด = ของ part5) ----------
function extractStyle(html) {
  const m = html.match(/<style>([\s\S]*?)<\/style>/);
  return m ? m[1] : '';
}

function build() {
  const files = PARTS.map(([f]) => fs.readFileSync(path.join(DOCS, f), 'utf8'));

  // เลือก style ที่ยาวที่สุด (ครอบคลุมคลาสครบสุด) เป็นฐาน
  const baseStyle = files.map(extractStyle).sort((a, b) => b.length - a.length)[0];

  const toc = PARTS.map(([f, part, title, ch], i) =>
    `<tr><td><strong>${esc(part)}</strong></td><td>${esc(title)}</td>` +
    `<td style="color:#64748b">${esc(ch)}</td>` +
    `<td><a href="#p${i + 1}">ไปที่บท</a></td></tr>`).join('\n');

  const sections = PARTS.map(([f, part, title, ch], i) => `
<div class="partsep" id="p${i + 1}">
  <div class="pnum">${esc(part)}</div>
  <div class="ptitle">${esc(title)}</div>
  <div class="pch">${esc(ch)}</div>
</div>
${extractBody(files[i])}`).join('\n');

  const html = `<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Arbitrage: จากแนวคิดสู่การปฏิบัติ — ฉบับรวมเล่ม</title>
<link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
${baseStyle}
/* ---------- ส่วนเพิ่มสำหรับฉบับรวมเล่ม ---------- */
.bookcover{text-align:center;padding:120px 20px 80px;border-bottom:none}
.bookcover h1{font-size:2.6em;line-height:1.25;color:var(--g9)}
.bookcover .sub{font-size:1.25em;color:var(--blue);font-weight:600;margin:18px 0 6px}
.bookcover .meta{color:#64748b;margin-top:28px;line-height:2}
.bookcover .rule{width:80px;height:4px;background:var(--blue);margin:28px auto;border-radius:2px}
.partsep{page-break-before:always;text-align:center;padding:90px 20px 40px;border-bottom:3px solid var(--blue);margin-bottom:24px}
.partsep .pnum{font-size:1.05em;font-weight:800;color:var(--blue);letter-spacing:.08em}
.partsep .ptitle{font-size:2em;font-weight:800;color:var(--g9);margin:10px 0 6px;line-height:1.3}
.partsep .pch{color:#64748b}
.toc{page-break-before:always}
.toc h2{border-bottom:3px solid var(--blue)}
.toc a{color:var(--blue);text-decoration:none}
.disc{background:var(--amber-bg);border-left:4px solid var(--amber);padding:16px 20px;border-radius:0 8px 8px 0;margin:24px 0}
@media print{
  .bookcover{page-break-after:always;padding-top:150px}
  .partsep{page-break-before:always}
  h2{page-break-before:auto}          /* ให้ Part separator คุมการขึ้นหน้าแทน */
  .partsep+h2{page-break-before:avoid}
}
</style>
</head>
<body>

<div class="bookcover">
  <h1>Arbitrage<br>จากแนวคิดสู่การปฏิบัติ</h1>
  <div class="rule"></div>
  <div class="sub">ฉบับรวมเล่ม — อิงหลักฐานวิจัย พร้อมเลนส์สำหรับรายย่อย</div>
  <div class="meta">
    33 บท · 9 Parts · 24+5 Drills · 6 Cases<br>
    งานวิจัยอ้างอิง 44 รายการ · โค้ด Python รันได้จริง
  </div>
</div>

<div class="toc">
<h2>สารบัญ</h2>
<table>
<tr><th>Part</th><th>หัวข้อ</th><th>บท</th><th></th></tr>
${toc}
</table>

<div class="disc">
<strong>⚖️ อ่านก่อนเริ่ม</strong><br>
หนังสือเล่มนี้เขียนเพื่อ<strong>การศึกษา ไม่ใช่คำแนะนำการลงทุน</strong> — ตัวเลขผลตอบแทนที่อ้างจากงานวิจัย
เกือบทั้งหมดเป็นค่า<em>ก่อนหักต้นทุน (gross)</em> ให้ใช้เป็น "เพดานบน" ไม่ใช่ค่าที่คาดหวังได้จริง
การเทรดมีความเสี่ยงขาดทุน และการ short หรือใช้ leverage อาจขาดทุน<em>เกินเงินลงทุน</em>
<br><br>
สิ่งที่ทำให้เล่มนี้ต่างจากตำรา arbitrage ทั่วไปคือ <strong>คอลัมน์ "สถานะของ edge"</strong> —
กลยุทธ์จำนวนมากในตำราคลาสสิก<em>ตายไปแล้ว</em> และเราบอกตรงๆ ว่าอันไหนตาย พร้อมหลักฐาน
</div>
</div>

${sections}

<div class="partsep">
  <div class="pnum">จบเล่ม</div>
  <div class="ptitle">Arbitrage: จากแนวคิดสู่การปฏิบัติ</div>
  <div class="pch">รอดก่อน แล้วค่อยกำไร · gross ≠ net · edge เสื่อมได้จริง</div>
</div>

</body>
</html>`;

  const outHtml = path.join(DOCS, 'arb-book.html');
  fs.writeFileSync(outHtml, html, 'utf8');
  console.log(`${outHtml} — ${(html.length / 1024).toFixed(0)} KB`);
  return outHtml;
}

(async () => {
  const outHtml = build();
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + outHtml, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(4000);
  const pdfPath = path.join(DOCS, 'arb-book.pdf');
  await page.pdf({
    path: pdfPath,
    format: 'A4',
    margin: { top: '18mm', bottom: '18mm', left: '16mm', right: '16mm' },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: `<div style="font-size:8px;font-family:Sarabun,sans-serif;width:100%;text-align:center;color:#94a3b8;">Arbitrage: จากแนวคิดสู่การปฏิบัติ</div>`,
    footerTemplate: `<div style="font-size:8px;font-family:Sarabun,sans-serif;width:100%;text-align:center;color:#94a3b8;">หน้า <span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
  });
  await browser.close();
  const kb = (fs.statSync(pdfPath).size / 1024).toFixed(0);
  console.log(`${pdfPath} — ${kb} KB`);
})();
