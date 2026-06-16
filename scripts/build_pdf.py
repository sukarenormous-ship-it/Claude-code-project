#!/usr/bin/env python3
"""
Build PDF for Python for Quant Traders book.
Pipeline: HTML → KaTeX pre-render (Node.js) → WeasyPrint → PDF → merge
"""
import subprocess, sys, os
from pathlib import Path

BASE  = Path('/home/user/Claude-code-project')
DOCS  = BASE / 'docs'
OUT   = BASE / 'pdf'
TMP   = BASE / 'pdf/tmp'
OUT.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

PARTS = [f'python-part{i}.html' for i in range(7)] + ['python-appendix.html']

# Font path — absolute so WeasyPrint finds it regardless of working dir
FONT_DIR = DOCS / 'vendor/fonts'

PRINT_CSS = f"""
<style>
/* ---- Embed Sarabun font with absolute path ---- */
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-Regular.ttf") format("truetype");
  font-weight: 400;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-SemiBold.ttf") format("truetype");
  font-weight: 600;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-Bold.ttf") format("truetype");
  font-weight: 700;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{FONT_DIR}/Sarabun-ExtraBold.ttf") format("truetype");
  font-weight: 800;
}}

/* ---- Page layout ---- */
@page {{ size: A4; margin: 2cm 2.5cm 2.2cm 2.5cm; }}
body {{
  font-family: "Sarabun", sans-serif !important;
  font-size: 11pt;
  line-height: 1.7;
  color: #1f2937;
  background: #fff;
  max-width: none !important;
  padding: 0 !important;
}}

/* ---- Cover page ---- */
.cover {{
  text-align: center;
  padding: 60px 30px 50px;
  border-bottom: 3px solid #0d9488;
  margin-bottom: 30px;
  page-break-after: always;
}}
.cover .ch-num {{ color: #0d9488; font-size: 1em; font-weight: 700; }}
.cover h1 {{ font-size: 2em; font-weight: 800; color: #111827; margin: 8px 0; }}
.cover .sub {{ color: #64748b; font-size: 1em; }}

/* ---- Headings ---- */
h1 {{ page-break-before: always; }}
.cover h1 {{ page-break-before: avoid; }}
/* h2 = chapter heading (บทที่ N) — each chapter starts a new page */
h2 {{ font-size: 1.4em; page-break-before: always; page-break-after: avoid; }}
h3 {{ font-size: 1.15em; page-break-after: avoid; }}

/* ---- Light code blocks for print ---- */
.fm {{
  background: #f8f9fa !important;
  color: #1a1a1a !important;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 12px 16px;
  /* Sarabun fallback ensures Thai comments use correct font (not FreeSerif) */
  font-family: 'Courier New', 'Sarabun', monospace !important;
  font-size: 8.5pt;
  line-height: 1.5;
  page-break-inside: avoid;
  white-space: pre-wrap;
  word-break: break-word;
}}
.fm .c  {{ color: #6c757d !important; }}
.fm .k  {{ color: #0055aa !important; font-weight: bold; }}
.fm .s  {{ color: #007700 !important; }}
.fm .n  {{ color: #aa0000 !important; }}

.output {{
  background: #f0f4f8 !important;
  color: #1a1a1a !important;
  border: 1px solid #c8d6e5;
  font-size: 8.5pt;
  page-break-inside: avoid;
}}
.output::before {{ color: #495057 !important; }}

/* ---- Boxes ---- */
.bx, .key-idea, .running-ex, .bx.bg, .bx.br, .bx.bb, .bx.ba, .bx.bi, .bx.bk, .bx.bd {{
  page-break-inside: avoid;
}}

/* ---- Tables ---- */
table {{ page-break-inside: avoid; font-size: 9pt; }}

/* ---- Exercises ---- */
details {{ page-break-inside: avoid; }}
details[open] {{ page-break-inside: auto; }}

/* ---- AI decode ---- */
.ai-decode {{ page-break-inside: avoid; font-size: 9.5pt; }}

/* ---- Hide nav ---- */
.nav, nav {{ display: none !important; }}

/* ---- No orphans/widows ---- */
p {{ orphans: 3; widows: 3; }}
</style>
"""

COVER_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<style>
@font-face {{
  font-family: "Sarabun";
  src: url("file://{font_dir}/Sarabun-Regular.ttf") format("truetype");
  font-weight: 400;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{font_dir}/Sarabun-Bold.ttf") format("truetype");
  font-weight: 700;
}}
@font-face {{
  font-family: "Sarabun";
  src: url("file://{font_dir}/Sarabun-ExtraBold.ttf") format("truetype");
  font-weight: 800;
}}
@page {{ size: A4; margin: 0; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: "Sarabun", sans-serif;
  background: #fff;
  width: 210mm;
  height: 297mm;
  overflow: hidden;
}}

/* Top teal band */
.top-band {{
  background: #0d9488;
  height: 14mm;
  width: 100%;
}}

/* Main content area */
.main {{
  padding: 18mm 22mm 10mm;
  text-align: center;
}}

.series-label {{
  font-size: 10pt;
  font-weight: 700;
  color: #0d9488;
  letter-spacing: .15em;
  text-transform: uppercase;
  margin-bottom: 10mm;
}}

.title {{
  font-size: 42pt;
  font-weight: 800;
  color: #111827;
  line-height: 1.15;
  margin-bottom: 6mm;
}}

.title-th {{
  font-size: 28pt;
  font-weight: 700;
  color: #0d9488;
  margin-bottom: 8mm;
}}

.subtitle {{
  font-size: 12pt;
  color: #64748b;
  line-height: 1.7;
  margin-bottom: 10mm;
}}

/* Horizontal rule */
.rule {{
  width: 60mm;
  height: 3px;
  background: #0d9488;
  margin: 0 auto 10mm;
  border-radius: 2px;
}}

/* Parts table — 2 columns, clean */
.parts-table {{
  width: 130mm;
  margin: 0 auto 10mm;
  border-collapse: collapse;
}}
.parts-table td {{
  padding: 4px 10px;
  font-size: 10.5pt;
  text-align: left;
  color: #1f2937;
  border: none;
  background: none;
  line-height: 1.6;
}}
.parts-table td .num {{
  display: inline-block;
  width: 18mm;
  font-weight: 700;
  color: #0d9488;
}}
.parts-table td .name {{
  color: #374151;
}}

/* Stats row */
.stats {{
  display: table;
  margin: 0 auto 10mm;
  border-top: 1px solid #e5e7eb;
  border-bottom: 1px solid #e5e7eb;
  padding: 6mm 0;
  width: 130mm;
  text-align: center;
}}
.stat-item {{
  display: table-cell;
  padding: 0 12mm;
  border-right: 1px solid #e5e7eb;
}}
.stat-item:last-child {{ border-right: none; }}
.stat-num {{
  font-size: 22pt;
  font-weight: 800;
  color: #0d9488;
  line-height: 1;
}}
.stat-label {{
  font-size: 8.5pt;
  color: #64748b;
  margin-top: 2px;
}}

.audience {{
  font-size: 10pt;
  color: #64748b;
  line-height: 1.7;
}}

/* Bottom teal band */
.bottom-band {{
  background: #0d9488;
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 10mm;
}}
</style>
</head>
<body>
<div class="top-band"></div>
<div class="main">
  <div class="series-label">Python for Quant Traders</div>

  <div class="title">Python</div>
  <div class="title-th">สำหรับ Quant Trader</div>

  <div class="subtitle">
    เรียน Python เพื่อวิเคราะห์ตลาดการเงิน<br>
    ตั้งแต่พื้นฐานจนถึงระบบเทรดสดจริง
  </div>

  <div class="rule"></div>

  <table class="parts-table">
    <tr>
      <td><span class="num">Part 0</span><span class="name">รากฐาน — คณิต · สถิติ · ตลาด</span></td>
      <td><span class="num">Part I</span><span class="name">Python Basics</span></td>
    </tr>
    <tr>
      <td><span class="num">Part II</span><span class="name">Math Tools — สถิติ · Optimization</span></td>
      <td><span class="num">Part III</span><span class="name">OOP &amp; Design Patterns</span></td>
    </tr>
    <tr>
      <td><span class="num">Part IV</span><span class="name">Backtesting</span></td>
      <td><span class="num">Part V</span><span class="name">AI-Assisted Coding</span></td>
    </tr>
    <tr>
      <td colspan="2" style="text-align:center">
        <span class="num">Part VI</span><span class="name">Async &amp; Live Trading</span>
      </td>
    </tr>
  </table>

  <div class="stats">
    <div class="stat-item">
      <div class="stat-num">35</div>
      <div class="stat-label">บท</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">7</div>
      <div class="stat-label">Parts</div>
    </div>
    <div class="stat-item">
      <div class="stat-num">0</div>
      <div class="stat-label">พื้นฐาน CS ที่ต้องการ</div>
    </div>
  </div>

  <div class="audience">
    ออกแบบสำหรับทุกคน — หมอ ทนาย สถาปนิก นักธุรกิจ<br>
    ไม่ต้องมีพื้นฐาน Computer Science
  </div>
</div>
<div class="bottom-band"></div>
</body>
</html>
""".format(font_dir=FONT_DIR)


HOWTO_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<style>
@font-face {{ font-family:"Sarabun"; src:url("file://{font_dir}/Sarabun-Regular.ttf"); font-weight:400; }}
@font-face {{ font-family:"Sarabun"; src:url("file://{font_dir}/Sarabun-Bold.ttf"); font-weight:700; }}
@font-face {{ font-family:"Sarabun"; src:url("file://{font_dir}/Sarabun-ExtraBold.ttf"); font-weight:800; }}
@page {{ size: A4; margin: 2cm 2.5cm 2.2cm; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family:"Sarabun",sans-serif; color:#1f2937; font-size:10.5pt; line-height:1.7; }}
h1 {{ font-size:19pt; font-weight:800; color:#111827; border-bottom:3px solid #0d9488;
      padding-bottom:3mm; margin-bottom:5mm; }}
h2 {{ font-size:12pt; font-weight:700; color:#0d9488; margin-top:5mm; margin-bottom:2mm; }}
p {{ margin-bottom:2mm; }}

/* Learning path */
.path {{ display:flex; align-items:center; flex-wrap:wrap; gap:2mm; margin:3mm 0 4mm; }}
.badge {{ background:#0d9488; color:#fff; font-weight:700; font-size:9pt;
          padding:1.5mm 3.5mm; border-radius:4px; white-space:nowrap; }}
.arrow {{ color:#0d9488; font-weight:700; font-size:13pt; line-height:1; }}
.skip {{ background:#f0fdf4; border-left:3px solid #0d9488; padding:2mm 4mm;
         border-radius:0 4px 4px 0; font-size:9.5pt; margin:2mm 0; }}
.skip strong {{ color:#0d9488; }}

/* Icon legend table */
.leg {{ width:100%; border-collapse:collapse; margin:2mm 0; }}
.leg td {{ padding:2mm 3mm; vertical-align:top; font-size:9.5pt; border:none; }}
.leg td:first-child {{ width:38mm; font-weight:700; white-space:nowrap; }}
.leg .ki {{ color:#0d9488; }}
.leg .re {{ color:#7c3aed; }}
.leg .wa {{ color:#b45309; }}
.leg .nb {{ color:#1d4ed8; }}
.leg .ex {{ color:#374151; }}

/* Running example box */
.ex-box {{ background:#fff8f0; border:2px dashed #f59e0b; border-radius:8px;
           padding:3mm 5mm; margin:3mm 0; font-size:9.5pt; }}
.ex-box strong {{ color:#b45309; }}
</style>
</head>
<body>

<h1>วิธีใช้หนังสือ</h1>

<h2>แผนผังการเรียน</h2>
<p>หนังสือออกแบบให้อ่านตามลำดับ แต่ถ้ามีพื้นฐานบางส่วนอยู่แล้ว สามารถข้ามได้ตามนี้</p>
<div class="path">
  <span class="badge">Part 0</span><span class="arrow">→</span>
  <span class="badge">Part I</span><span class="arrow">→</span>
  <span class="badge">Part II</span><span class="arrow">→</span>
  <span class="badge">Part III</span><span class="arrow">→</span>
  <span class="badge">Part IV</span><span class="arrow">→</span>
  <span class="badge">Part V</span><span class="arrow">→</span>
  <span class="badge">Part VI</span>
</div>
<div class="skip"><strong>มี Python พื้นฐานแล้ว?</strong> ข้ามไปเริ่มที่ Part II ได้เลย</div>
<div class="skip"><strong>รู้สถิติและ pandas แล้ว?</strong> ข้ามไปเริ่มที่ Part III</div>
<div class="skip"><strong>ต้องการ Backtesting โดยตรง?</strong> อ่าน Part 0 บท 1–3 ก่อน → แล้วข้ามไป Part IV</div>

<h2>สัญลักษณ์ที่ใช้ในหนังสือ</h2>
<table class="leg">
  <tr>
    <td class="ki">💡 แนวคิดหลัก</td>
    <td>กรอบสีเขียว — แนวคิดหรือสูตรสำคัญที่ต้องจำ ปรากฏในทุก Part</td>
  </tr>
  <tr>
    <td class="re">🔄 ตัวอย่างต่อเนื่อง</td>
    <td>กรอบเส้นประสีส้ม — ตัวอย่าง BTC Pair Trading ที่ดำเนินต่อเนื่องตลอดทั้งเล่ม</td>
  </tr>
  <tr>
    <td class="wa">⚠️ ข้อควรระวัง</td>
    <td>กรอบสีแดง — จุดที่ผู้เริ่มต้นมักเข้าใจผิด หรือข้อผิดพลาดที่ควรหลีกเลี่ยง</td>
  </tr>
  <tr>
    <td class="nb">📌 หมายเหตุ</td>
    <td>กรอบสีน้ำเงิน — ข้อมูลเพิ่มเติมที่น่าสนใจแต่ไม่จำเป็นต้องจำ</td>
  </tr>
  <tr>
    <td class="ex">▶ แบบฝึกหัด</td>
    <td>กล่องสีเขียว — คลิก "ดูเฉลย" (เวอร์ชัน HTML) หรืออ่านเฉลยด้านล่างโจทย์ (PDF)</td>
  </tr>
</table>

<h2>ตัวอย่างหลักตลอดเล่ม: BTC Pair Trading</h2>
<div class="ex-box">
  <strong>กลยุทธ์ตัวอย่าง:</strong> Pair Trading ระหว่าง BTC-USDT บน Bybit และ BTC-USDT บน Binance
  ทั้งสองตลาดเคลื่อนไหวพร้อมกันเกือบสมบูรณ์ แต่มีราคาต่างกันเล็กน้อยชั่วคราว
  ทำให้เห็นภาพได้ชัดว่าแต่ละเครื่องมือ Python — ตั้งแต่ NumPy, pandas, OOP จนถึง
  Async WebSocket — นำไปใช้งานจริงในระบบเทรดอย่างไร
</div>

<h2>วิธีทำแบบฝึกหัด</h2>
<p>แบบฝึกหัดท้ายบทแต่ละข้อมีโจทย์และ <strong>ดูเฉลย</strong> ที่ซ่อนอยู่
แนะนำให้ลองทำเองก่อนแล้วค่อยเปิดดูเฉลย
ในเวอร์ชัน PDF กดไม่ได้ — เฉลยจะอยู่ถัดจากโจทย์โดยตรง</p>

<h2>โค้ดในหนังสือ</h2>
<p>ทุกโค้ดมีคำอธิบายภาษาไทยในบรรทัดคอมเมนต์ และ output จริงแสดงด้วยกรอบสีเทา
แนะนำให้รันโค้ดตามไปด้วยใน Jupyter Notebook หรือ Google Colab</p>

</body>
</html>
""".format(font_dir=FONT_DIR)


BACKCOVER_HTML = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<style>
@font-face {{ font-family:"Sarabun"; src:url("file://{font_dir}/Sarabun-Regular.ttf"); font-weight:400; }}
@font-face {{ font-family:"Sarabun"; src:url("file://{font_dir}/Sarabun-Bold.ttf"); font-weight:700; }}
@font-face {{ font-family:"Sarabun"; src:url("file://{font_dir}/Sarabun-ExtraBold.ttf"); font-weight:800; }}
@page {{ size: A4; margin: 0; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: "Sarabun", sans-serif;
  background: #fff;
  width: 210mm;
  height: 297mm;
  overflow: hidden;
  position: relative;
}}
.top-band {{ background:#0d9488; height:14mm; width:100%; }}
.main {{ padding:14mm 22mm 10mm; }}

.tagline {{
  font-size:15pt; font-weight:700; color:#0d9488;
  margin-bottom:5mm; line-height:1.4;
}}

.summary {{
  font-size:11pt; color:#374151; line-height:1.75;
  margin-bottom:7mm;
  border-left:3px solid #0d9488;
  padding-left:5mm;
}}

.section-label {{
  font-size:10pt; font-weight:800; color:#111827;
  text-transform:uppercase; letter-spacing:.08em;
  margin-bottom:3mm; margin-top:6mm;
}}

.learn-list {{
  list-style:none; padding:0; margin-bottom:6mm;
}}
.learn-list li {{
  font-size:10.5pt; color:#1f2937; padding:1.5mm 0;
  padding-left:6mm; position:relative; line-height:1.6;
}}
.learn-list li::before {{
  content:"✓"; position:absolute; left:0;
  color:#0d9488; font-weight:700;
}}

.for-who {{
  background:#f0fdfa; border:1px solid #99f6e4;
  border-radius:8px; padding:4mm 6mm; margin-bottom:6mm;
  font-size:10pt; color:#374151; line-height:1.7;
}}
.for-who strong {{ color:#0d9488; }}

.rule {{ width:40mm; height:2px; background:#0d9488; margin:6mm 0; border-radius:2px; }}

.stats-row {{
  display:flex; gap:10mm; align-items:center;
  margin-bottom:5mm;
}}
.stat {{ text-align:center; }}
.stat .num {{ font-size:20pt; font-weight:800; color:#0d9488; line-height:1; }}
.stat .lbl {{ font-size:8pt; color:#64748b; }}
.stat-sep {{ width:1px; height:10mm; background:#e5e7eb; }}

.bottom-band {{
  background:#0d9488;
  position:absolute; bottom:0; left:0; right:0;
  height:10mm;
  display:flex; align-items:center;
  padding:0 22mm;
}}
.bottom-band .url {{
  color:#fff; font-size:9pt; font-weight:600; opacity:.85;
}}
</style>
</head>
<body>
<div class="top-band"></div>
<div class="main">

  <div class="tagline">
    จาก 0 ถึงระบบเทรดสดจริง<br>ด้วย Python ในภาษาไทย
  </div>

  <div class="summary">
    หนังสือภาษาไทยเล่มแรกที่พาคุณสร้างระบบ Quantitative Trading ตั้งแต่พื้นฐาน Python
    ไปจนถึงกลยุทธ์ Pair Trading แบบ Real-time บน Bybit และ Binance
    โดยไม่ต้องมีพื้นฐาน Computer Science แม้แต่บรรทัดเดียว
  </div>

  <div class="stats-row">
    <div class="stat"><div class="num">35</div><div class="lbl">บท</div></div>
    <div class="stat-sep"></div>
    <div class="stat"><div class="num">7</div><div class="lbl">Parts</div></div>
    <div class="stat-sep"></div>
    <div class="stat"><div class="num">0</div><div class="lbl">พื้นฐาน CS</div></div>
    <div class="stat-sep"></div>
    <div class="stat"><div class="num">1</div><div class="lbl">ตัวอย่างต่อเนื่อง</div></div>
  </div>

  <div class="rule"></div>

  <div class="section-label">สิ่งที่คุณจะได้เรียนรู้</div>
  <ul class="learn-list">
    <li>เขียน Python ตั้งแต่ตัวแปรจนถึง Async WebSocket ในภาษาไทย</li>
    <li>วิเคราะห์ข้อมูลราคาด้วย NumPy, pandas, และ Matplotlib</li>
    <li>สร้าง Pair Trading Strategy พร้อม z-score signal และ Kalman Filter</li>
    <li>ออกแบบ OOP Architecture ที่ขยายง่ายด้วย Design Patterns</li>
    <li>Backtest กลยุทธ์อย่างถูกต้อง — ไม่มี Look-ahead Bias</li>
    <li>ใช้ AI (Claude/ChatGPT) ช่วยเขียนและ Debug โค้ดอย่างมีประสิทธิภาพ</li>
    <li>เชื่อมต่อ Bybit/Binance WebSocket และส่งคำสั่งเทรดสดจริง</li>
  </ul>

  <div class="for-who">
    <strong>เหมาะสำหรับ:</strong> หมอ ทนาย สถาปนิก นักธุรกิจ และทุกคนที่อยากเข้าใจตลาดการเงิน
    ผ่านโค้ด — ไม่ต้องมีพื้นฐาน CS ใช้แค่ความอยากรู้และความอดทนอ่านทีละบท
  </div>

</div>
<div class="bottom-band">
  <span class="url">Python for Quant Traders — ฉบับภาษาไทย</span>
</div>
</body>
</html>
""".format(font_dir=FONT_DIR)


def prerender(src: Path, dst: Path):
    """Pre-render KaTeX and inject print CSS."""
    result = subprocess.run(
        ['node', str(BASE / 'scripts/prerender_katex.js'), str(src), str(dst)],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f'  KaTeX error: {result.stderr}', file=sys.stderr)
        return False
    # Inject print CSS (font + print overrides)
    html = dst.read_text('utf8')
    # Remove original vendor font link (we embed fonts via @font-face in PRINT_CSS)
    html = html.replace('<link href="vendor/fonts/sarabun.css" rel="stylesheet">', '')
    html = html.replace('<link href="../vendor/fonts/sarabun.css" rel="stylesheet">', '')
    html = html.replace('</head>', PRINT_CSS + '\n</head>')
    dst.write_text(html, 'utf8')
    return True


def to_pdf(src: Path, dst: Path):
    """Convert HTML to PDF with WeasyPrint."""
    from weasyprint import HTML
    HTML(filename=str(src)).write_pdf(str(dst))


def merge_pdfs(parts: list, output: Path):
    """Merge all part PDFs into one."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    for p in parts:
        writer.append(str(p))
    with open(str(output), 'wb') as f:
        writer.write(f)
    size_mb = output.stat().st_size / 1024 / 1024
    print(f'Merged → {output.name} ({size_mb:.1f} MB)')


if __name__ == '__main__':
    pdf_parts = []

    # 1. Book cover page
    print('[Cover page]')
    cover_html = TMP / 'cover.html'
    cover_pdf  = OUT / 'cover.pdf'
    cover_html.write_text(COVER_HTML, 'utf8')
    try:
        to_pdf(cover_html, cover_pdf)
        pdf_parts.append(cover_pdf)
        print(f'  OK ({cover_pdf.stat().st_size // 1024} KB)')
    except Exception as e:
        print(f'  Cover error: {e}', file=sys.stderr)

    # 1b. How-to-read page
    print('[How-to-read page]')
    howto_html = TMP / 'howto.html'
    howto_pdf  = OUT / 'howto.pdf'
    howto_html.write_text(HOWTO_HTML, 'utf8')
    try:
        to_pdf(howto_html, howto_pdf)
        pdf_parts.append(howto_pdf)
        print(f'  OK ({howto_pdf.stat().st_size // 1024} KB)')
    except Exception as e:
        print(f'  How-to error: {e}', file=sys.stderr)

    # 2. Each part
    for part_html in PARTS:
        src  = DOCS / part_html
        stem = part_html.replace('.html', '')
        pre  = TMP / f'{stem}_prerendered.html'
        pdf  = OUT / f'{stem}.pdf'

        print(f'\n[{stem}]')
        print(f'  Pre-rendering KaTeX...')
        if not prerender(src, pre):
            print(f'  SKIP (KaTeX failed)')
            continue

        print(f'  Converting to PDF...')
        try:
            to_pdf(pre, pdf)
            pdf_parts.append(pdf)
            size = pdf.stat().st_size // 1024
            print(f'  OK ({size} KB)')
        except Exception as e:
            print(f'  PDF error: {e}', file=sys.stderr)

    # 3. Back cover page
    print('\n[Back cover page]')
    back_html = TMP / 'backcover.html'
    back_pdf  = OUT / 'backcover.pdf'
    back_html.write_text(BACKCOVER_HTML, 'utf8')
    try:
        to_pdf(back_html, back_pdf)
        print(f'  OK ({back_pdf.stat().st_size // 1024} KB)')
    except Exception as e:
        print(f'  Back cover error: {e}', file=sys.stderr)

    # 4. Merge
    if len(pdf_parts) > 1:
        print('\nMerging all parts...')
        merge_pdfs(pdf_parts, OUT / 'python-for-quant-traders-complete.pdf')

    print('\nDone!')
