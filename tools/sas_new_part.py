#!/usr/bin/env python3
"""พิมพ์เปลือก HTML ของหน้าใหม่ในชุด "แกะสไลด์ Stat Arb"

    python3 tools/sas_new_part.py <slug> "<ชื่อตอน>" "<คำสัญญาหนึ่งบรรทัด>" > docs/statarb-slides-<slug>.html
    slug = index | part1 … part8

เปลือกคัดมาจาก docs/statarb-data-quality.html ตรงตัว: <head> + บล็อก <style> แรก (CSS · palette ของทั้งคลัง)
และ Thai line-break <script> ท้ายไฟล์ (ห้ามแก้ — tools/sas_build.py check เทียบกับต้นฉบับทุกตัวอักษร)
แล้วเพิ่ม <style> อีกหนึ่งบล็อกสำหรับคลาสที่ใช้เฉพาะชุดนี้

    pre.code      โค้ดให้ผู้อ่านรันตาม                  <pre class="code">import numpy as np …</pre>
    pre.out       ผลลัพธ์โปรแกรม (build tool เติมให้)   <!--OUT:p8.demo.good--><!--/OUT:p8.demo.good-->
    .slide        กรอบ "ถอดความจากสไลด์"               <div class="slide" data-label="สไลด์แผ่นที่ 4">…</div>
    details.ans   เฉลยที่ซ่อนไว้                        <details class="ans"><summary>ดูเฉลย</summary>…</details>
    .station      ขั้นตอนมีเลขกำกับ                     <div class="station" data-n="1"><div class="bt">…</div>…</div>
                  (หรือใส่ <span class="n">1</span> เป็นลูกตัวแรกแทน data-n)
    .nav          บรรทัดนำทางท้ายหน้า                   <p class="nav"><a …>← ก่อนหน้า</a> · <a …>สารบัญ</a> · …</p>
    .tag-sim      ป้ายเล็ก "ข้อมูลจำลอง"                <span class="tag-sim">ข้อมูลจำลอง</span>
    .figw         กรอบของกราฟกว้าง (tools/sas_svg.py ใส่ให้เอง) — บนจอแคบ ≤ 640px กราฟคงความกว้าง 600px
                  แล้วเลื่อนดูด้านข้างได้ (เหมือนตารางใน .tw) แทนที่จะถูกบีบจนอ่านตัวเลขไม่ออก

เขียนเนื้อหาแทนที่บรรทัด <!--BODY--> แล้วรัน (ระบุไฟล์ของตัวเองเสมอ)
    python3 tools/sas_build.py charts,fill,out,snippets,check docs/statarb-slides-<slug>.html

ผลลัพธ์เขียนออก stdout เป็น UTF-8 เสมอ (ไม่ขึ้นกับ locale ของเครื่อง) · ไฟล์ต้นแบบหาย/เปลี่ยนโครง = exit 1 พร้อมเหตุผล
"""

import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "docs", "statarb-data-quality.html")
SERIES = "แกะสไลด์ Stat Arb"
BODY_MARK = "<!--BODY-->"
SLUGS = ["index"] + [f"part{i}" for i in range(1, 9)]

# คลาสเฉพาะชุดนี้ — หน้าตาเข้าชุดกับกล่องเดิม (.bx · .scene · .dft) · พิมพ์ได้ · อ่านบนมือถือได้
SERIES_CSS = """<style>
pre.code,pre.out{font-family:'Courier New',monospace;font-size:.86em;line-height:1.55;border-radius:6px;margin:12px 0;padding:12px 16px;overflow-x:auto;white-space:pre;tab-size:4}
pre.code{background:var(--g1);color:var(--g8);border:1px solid var(--g2)}
pre.out{background:var(--g0);color:var(--g9);border:1px solid var(--g2);border-left:4px solid var(--g7)}
.slide{position:relative;border:1px solid #c7d2fe;background:#f8faff;border-radius:10px;padding:16px 20px 10px;margin:20px 0}
.slide[data-label]{padding-top:26px}
.slide[data-label]::before{content:attr(data-label)}
.slide[data-label]::before,.slide>.lbl{position:absolute;top:-11px;left:16px;background:var(--blue);color:#fff;font-size:.72em;font-weight:700;line-height:1.5;padding:1px 10px;border-radius:20px;white-space:nowrap}
.slide .fm{background:#fff;border:1px solid var(--g2)}
details.ans{border:1px dashed #a5b4fc;border-radius:8px;padding:8px 16px;margin:10px 0;background:#fff}
details.ans>summary{cursor:pointer;font-weight:700;color:var(--blue)}
details.ans[open]{background:var(--blue-bg);padding-bottom:12px}
details.ans[open]>summary{margin-bottom:8px}
.station{position:relative;border:1px solid var(--g2);border-left:4px solid var(--blue);border-radius:0 10px 10px 0;background:#fff;padding:12px 18px 6px 62px;margin:16px 0;min-height:58px}
.station[data-n]::before{content:attr(data-n)}
.station[data-n]::before,.station>.n{position:absolute;left:14px;top:12px;width:34px;height:34px;border-radius:50%;background:var(--blue);color:#fff;font-weight:800;font-size:1.05em;line-height:34px;text-align:center}
.station>.bt{color:var(--g9)}
.nav{text-align:center;margin-top:30px;padding-top:14px;border-top:1px solid var(--g2);font-size:.95em}
.tag-sim{display:inline-block;font-size:.72em;font-weight:700;line-height:1.5;color:#0e7490;background:#ecfeff;border:1px solid #a5f3fc;border-radius:20px;padding:0 9px;margin-left:4px;vertical-align:middle;white-space:nowrap}
@media(max-width:640px){pre.code,pre.out{font-size:.78em;padding:10px 12px}.slide{padding-left:14px;padding-right:14px}.station{padding-left:52px;padding-right:12px}.station[data-n]::before,.station>.n{left:10px;width:30px;height:30px;line-height:30px}.figw{overflow-x:auto;-webkit-overflow-scrolling:touch}.figw>svg.fig{width:600px;max-width:none;margin:14px 0 6px}.figw+.cap{margin-top:4px}.figw+.cap::before{content:"↔ เลื่อนกราฟไปด้านข้างได้ · ";white-space:nowrap}}
@media print{pre.code,pre.out{white-space:pre-wrap;overflow-wrap:anywhere;overflow:visible}pre.code,pre.out,.slide,.station,details.ans{page-break-inside:avoid}details.ans::details-content{content-visibility:visible;display:block}details.ans>summary{list-style:none}.nav{display:none}}
</style>"""


SCRIPT_MARK = "<!-- ═══════════════ Thai line-break script"


def skeleton(slug, title, promise):
    """HTML ทั้งหน้าของเปลือก (str) · ValueError ถ้าไฟล์ต้นแบบไม่มีโครงที่คาดไว้"""
    with open(SOURCE, encoding="utf-8") as fh:
        src = fh.read()
    esc = lambda s: html.escape(s, quote=False)

    if "<body>" not in src or SCRIPT_MARK not in src:
        raise ValueError(f"ไฟล์ต้นแบบ {SOURCE} ไม่มี <body> หรือบล็อก Thai line-break script")
    head = src[:src.index("<body>")]
    if head.count("<style>") != 1 or "</head>" not in head or not re.search(r"<title>.*?</title>", head, re.S):
        raise ValueError(f"คาดว่า <head> ของ {SOURCE} มี <title> และ <style> บล็อกเดียว")
    head = re.sub(r"<title>.*?</title>", lambda m: f"<title>{SERIES} — {esc(title)}</title>", head, count=1, flags=re.S)
    head = head.replace("</head>", "\n" + SERIES_CSS + "\n</head>", 1)

    script = src[src.rindex(SCRIPT_MARK):]

    cover = f'''<body>

<!-- ═══════════════ COVER · {slug} ═══════════════ -->
<div class="cover">
<h1>{SERIES}</h1>
<div class="sub">{esc(title)}</div>
<div class="desc">{esc(promise)}</div>
</div>

{BODY_MARK}

'''
    return head + cover + script


def main(argv):
    if hasattr(sys.stderr, "reconfigure"):       # ข้อความช่วยเหลือเป็นภาษาไทย — อย่าให้ขึ้นกับ locale ของเครื่อง
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    # ชื่อตอนภาษาไทยที่ส่งมาใน locale ที่ไม่ใช่ UTF-8 (LC_ALL=C) จะถูกถอดเป็น surrogate — แปลงกลับเป็น UTF-8 จริง
    argv = [os.fsencode(a).decode("utf-8", "replace") for a in argv]
    if len(argv) != 4 or argv[1] not in SLUGS:
        sys.stderr.write(__doc__)
        if len(argv) > 1 and argv[1] not in SLUGS:
            sys.stderr.write(f"\n✗ slug ต้องเป็นหนึ่งใน: {', '.join(SLUGS)} (ได้ {argv[1]!r})\n")
        elif len(argv) != 4:
            sys.stderr.write(f"\n✗ ต้องมี 3 อาร์กิวเมนต์: slug \"ชื่อตอน\" \"คำสัญญา\" (ได้ {len(argv) - 1})\n")
        return 1
    try:
        page = skeleton(argv[1], argv[2], argv[3])
    except (OSError, ValueError) as e:
        sys.stderr.write(f"✗ สร้างเปลือกไม่ได้: {e}\n")
        return 1
    # เขียนเป็นไบต์ UTF-8 ตรง ๆ: ผลลัพธ์ถูก redirect ลงไฟล์ จึงต้องไม่ขึ้นกับ locale (Windows cp874) และไม่แปลง \n
    out = getattr(sys.stdout, "buffer", None)
    if out is not None:
        out.write(page.encode("utf-8"))
        out.flush()
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
