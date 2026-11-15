#!/usr/bin/env python3
"""สร้างไฟล์บทใหม่ของ "Stat Arb for Non Quant" (เล่ม 1 ค่าเริ่มต้น · เล่ม 2 ด้วย --book sab2) จากเปลือกกลาง tools/sab_shell/

เปลือก (CSS · palette · Thai line-break script) เก็บที่เดียวใน tools/sab_shell/head.html + tail.html
เพื่อไม่ให้ความต่างเล็ก ๆ สะสมข้ามบท — ห้ามแก้ Thai line-break script ด้วยมือ (กฎ style guide)

    python3 tools/sab_new_part.py part4 "หัวข้อรอง" "คำโปรย"     # เขียน docs/sab-part4.html (ปฏิเสธถ้ามีไฟล์แล้ว)
    python3 tools/sab_new_part.py base1 ["หัวข้อรอง" "คำโปรย"]   # หน้าพื้นฐาน base1..base4 (แผน 14.5) → docs/sab-base1.html
    python3 tools/sab_new_part.py index "หน้ารวมเล่ม" "คำโปรย"     # slug ใดก็ได้ → docs/sab-<slug>.html
    python3 tools/sab_new_part.py --sync                          # เขียนหัว/ท้ายใหม่ให้ docs/sab-*.html ทุกไฟล์เมื่อเปลือกเปลี่ยน
    python3 tools/sab_new_part.py --book sab2 part3               # เล่ม 2 → docs/sab2-part3.html (ชื่อบทจากแผน sab2 ·
                                                                  #   โครง v2 + กล่อง .fails + บล็อก 💻 details.code)

บท (partN) และหน้าพื้นฐาน (baseN) ได้โครงแม่แบบ v2 (แผน 14.3): <body data-tpl="2"> · .pos · .scene-open · .pq ·
ตอนสอนที่จบด้วย .rest · .sum3 · ✍️ พร้อม details.hint สองระดับและ details.ans · .pq[data-hook] · 📖 · details.file
(หน้าพื้นฐานไม่มี details.file · แบบฝึก 3 ข้อ) — หัวข้อรอง/คำโปรยเว้นได้ จะใช้ชื่อจาก sab_book.py · slug อื่นได้เปลือกเปล่าเหมือนเดิม
ถ้าแก้เฉพาะ CSS ของเปลือก ใช้ tools/sab_reshell.py (แทนเฉพาะบล็อก <style>)

ต่างจาก nq_new_part.py: เขียนไฟล์เอง (ไม่พิมพ์ออก stdout จึงไม่เสี่ยง `>` ทับเนื้อบท) · ใช้ slug ที่รับมา ·
เปลือกเก็บที่เดียวและ --sync ได้
"""

import glob
import html as htmllib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BOOK = B.BOOK
BOOK_TH = B.BOOK_TH
BODY_MARK = "<!--BODY-->"
TAIL_MARK = "<!-- ═══════════════ Thai line-break script"
shell = B.shell        # เปลือกกลาง (+ tools/sab2_shell/extra.css เมื่อ --book sab2)

# เล่ม 2 (แผน sab2 หัวข้อ 5): กล่อง "พังเมื่อไร / บอกอะไรไม่ได้" และบล็อกพับ "💻 ทำด้วย Python" — ตรวจโดย sab_qa V9 · V10
V2_EXTRA = '''
<!-- กล่อง .fails หนึ่งกล่องต่อเครื่องมือ (กฎ V10: อย่างน้อยหนึ่งกล่องต่อบท) · เงื่อนไขที่ทำให้ผลใช้ไม่ได้ พร้อมตัวเลข ไม่ใช่ข้อเสียทั่วไป -->
<div class="fails"><div class="bt">⚠️ พังเมื่อไร / บอกอะไรไม่ได้</div>
<ul>
<li><strong>พังเมื่อ</strong> … (ตัวเลข: เช่น ข้อมูลสั้นกว่า … วัน ค่า … คลาดได้ถึง …)</li>
<li><strong>บอกไม่ได้ว่า</strong> …</li>
</ul></div>

<!-- บล็อก 💻 (กฎ V9): ≤ 25 บรรทัด · ทำซ้ำสิ่งที่เพิ่งทำด้วยมือ · รันด้วย PYTHONPATH=tools (import sab2_stats / sab2_sim / sab2_realdata ได้)
     ไม่มีเครือข่าย · บรรทัดสุดท้ายของ <pre> ต้องเป็น "# ผลที่ต้องได้: ค่า · ค่า" — ตัวเลขที่โค้ดพิมพ์ต้องตรงตามลำดับ
     (ปัดตามจำนวนทศนิยมที่เขียน) และทุกค่าต้องปรากฏในเนื้อหน้านอกบล็อกนี้ · เขียน < > & ในโค้ดเป็น &lt; &gt; &amp; -->
<details class="code"><summary>💻 ทำด้วย Python</summary>
<pre>xs = [1, 2, 3]
print(sum(xs) / len(xs))
# ผลที่ต้องได้: 2</pre>
<p>…อธิบายสั้น ๆ ว่าบรรทัดไหนตรงกับขั้นไหนที่ทำด้วยมือ · แบบ numpy/pandas ที่ผู้อ่านน่าจะใช้จริง…</p>
</details>
'''


EX_STEPS = ["ทำตาม", "เปลี่ยนเลขหนึ่งตัว", "เปลี่ยนเงื่อนไขหนึ่งข้อ", "ตัดสินใจ", "ถ่ายโอน"]      # บันไดห้าขั้น (แผน 14.3 ข้อ 6)


def v2_kind(slug):
    """('part', N) · ('base', N) สำหรับ slug ที่ได้โครง v2 · None = เปลือกเปล่า"""
    m = re.fullmatch(r"(part|base)(\d+)", slug)
    if not m:
        return None
    kind, n = m.group(1), int(m.group(2))
    if kind == "base" and n not in B.BASE_TITLES:
        sys.exit(f"หน้าพื้นฐานมีเฉพาะ base1..base{B.LAST_BASE}: {slug!r}")
    return kind, n


def v2_body(kind, n):
    """โครงบท v2 — ข้อความ "…" คือที่ให้เขียนแทน · คำแนะนำอยู่ใน comment (ไม่นับคำ ไม่ถูกตัวตรวจอ่าน)"""
    last_part = B.LAST_PART
    if kind == "base":
        where = f"ภาคพื้นฐาน · หน้า {n} จาก {B.LAST_BASE}"
        cont = f' data-continues="base{n - 1}"' if n > 1 else ""
        n_ex, n_hint, term_cap, tier = 3, 2, 4, "ก"
        nxt = f"หน้าพื้นฐาน {n + 1}" if n < B.LAST_BASE else "บท 0"
    else:
        where = f"ภาค … · บท {n} จาก {last_part}"
        cont = (f' data-continues="part{n - 1}"' if n > B.FIRST_PART
                else f' data-continues="base{B.LAST_BASE}"' if B.LAST_BASE else "")
        n_ex, n_hint, term_cap, tier = 5, 3, 7, "ข"
        nxt = f"บท {n + 1}"
    extra = kind == "part" and B.BOOK_ID != "sab"      # เล่ม 2: .fails + details.code
    hint = ('<details class="hint"><summary>คำใบ้</summary>\n'
            '<p>…ขั้นที่ 1: เริ่มจากตรงไหน…</p>\n'
            '<details class="hint"><summary>ยังไม่ออก? คำใบ้ขั้นที่ 2</summary><p>…ตัวเลขกลางทางหนึ่งตัว…</p></details>\n'
            '</details>\n')
    items = "".join(
        f'<li>({EX_STEPS[i] if n_ex == 5 else EX_STEPS[(0, 1, 3)[i]]}) …โจทย์…\n{hint if i < n_hint else ""}'
        '<details class="ans"><summary>เฉลย</summary><p>…เดินทีละขั้นเป็นประโยค… ถ้าได้ … แปลว่าพลาดตรง …</p></details>\n</li>\n'
        for i in range(n_ex))
    bridge = "" if kind == "part" and n == last_part else (
        f'<!-- คำถามสะพาน: data-hook = วลีที่ฉากเปิดของ{nxt} ต้องมีตรงตัว (W15) -->\n'
        '<div class="pq" data-hook="…">…คำถามสะพาน…</div>\n\n')
    file_block = "" if kind == "base" else '''<!-- แฟ้มท้ายบท (พับไว้): ใบงาน .sheet เต็มใบตามกติกา W19 เดิม (อย่างน้อยหนึ่งใบ) · บัญชีมิน table.ledger เมื่อบัญชีเปลี่ยน ·
     ช่องบัตร table.ncard ที่เติมในบทนี้ · ลิงก์อ่านลึก · 🔎 details.deep รอบสอง · หัวข้อย่อยในแฟ้มใช้ h3 (ไม่ใช้ h2) -->
<details class="file"><summary>📁 แฟ้มของบทนี้</summary>
…
</details>

'''
    return f'''<!-- ═══ แม่แบบ v2 (แผน 14.3 · คู่มือ tools/sab_research/writing-brief-v2.md) · ตรวจด้วย python3 tools/sab_qa.py ═══ -->
<p class="pos"><strong>{where}</strong> · ต้องรู้จากบทก่อน: (1) … (2) … (3) …</p>

<!-- ฉากเปิดของมิน: สั้น · ต้องมีวลี data-hook ของหน้าก่อนตรงตัว -->
<div class="scene-open" data-day="…"{cont}><div class="bt">📓 สมุดของมิน</div>
<p>…</p>
</div>

<div class="pq">…คำถามของบท…</div>

<!-- ═══ ตอนสอน (h2) 3 ถึง 6 ตอน · ทุกตอนจบด้วย .rest ═══
     ลำดับในตอน: สถานการณ์ → ตามเงินทีละประโยค → ตาราง (คอลัมน์ "คิดอย่างไร" = th/td class="calc") → ตั้งชื่อศัพท์ → 🛑 ทายก่อน
     → กราฟ + .readfig → 🚶 + .fm + .readeq → .rest · ย่อหน้า p หนึ่งย่อหน้ามีเครื่องหมายเท่ากับไม่เกินสองตัว
     ตารางสอนธรรมดาไม่ต้องติดป้ายที่มา · ตารางผลจำลอง/ข้อมูลจริง/ค่าจากแอป ใส่ data-src="sim|real|app" และป้าย 🎲/📡/📱 ใกล้ตาราง -->
<h2>…หัวข้อตอนที่ 1 (มีตัวเลขหลัก หรือเป็นคำถามที่ตอนนี้ตอบ)…</h2>
<p>…</p>
<div class="tw"><table>
<tr><th>เหตุการณ์</th><th class="calc">คิดอย่างไร</th><th class="nw">ผล</th></tr>
<tr><td>…</td><td class="calc">…</td><td class="nw">…</td></tr>
</table></div>

<div class="stop"><div class="bt">🛑 ทายก่อน</div>
<p>…</p></div>

<!-- กราฟ: วางตัวคั่น CHART ของ sab_charts.py ตรงนี้ แล้ววาง .readfig ไว้หลังตัวคั่นปิด (ข้างในตัวคั่นจะถูกเขียนทับ) -->
<p class="readfig"><strong>อ่านภาพ:</strong> …แกนและแท่งคืออะไร · ให้มองตรงไหน · สรุปได้ว่าอะไร…</p>

<p><strong>🚶 อ่านเป็นภาษาคนก่อน:</strong> …</p>
<div class="fm">… = …</div>
<p class="readeq"><strong>อ่านสมการ:</strong> …แทนเลขจริงของตัวอย่างลงในสูตร…</p>

{V2_EXTRA if extra else ""}
<div class="rest"><div class="bt">พักตรงนี้ได้</div>
<p>…สองสามประโยค พร้อมตัวเลขหลักของตอน · ไม่มีศัพท์ใหม่…</p></div>

<h2>…หัวข้อตอนที่ 2…</h2>
<p>…</p>

<div class="rest"><div class="bt">พักตรงนี้ได้</div>
<p>…</p></div>

<div class="sum3"><div class="bt">สรุป 3 ข้อ</div>
<ol>
<li>…</li>
<li>…</li>
<li>…</li>
</ol></div>

<!-- แบบฝึก {n_ex} ข้อ · ทุกข้อมี details.ans · ข้อคำนวณมี details.hint สองระดับ (อย่างน้อย {n_hint} ข้อ) -->
<div class="bx bg"><div class="bt">✍️ ลองทำเอง</div>
<ol>
{items}</ol></div>

{bridge}<!-- ศัพท์ที่สอนครั้งแรกในหน้านี้ ไม่เกิน {term_cap} คำ · ชั้นคำ ก = แอป/บัญชี · ข = แกนกลยุทธ์ · ค = ลงลึก -->
<div class="bx bb"><div class="bt">📖 ศัพท์ใหม่ในตอนนี้</div>
<ul>
<li><strong>English Term (คำแปลไทย)</strong> = … <span class="tier" data-tier="{tier}"></span></li>
</ul></div>

{file_block}'''


def skeleton(slug, sub, desc):
    head, tail = shell()
    esc = htmllib.escape
    head = head.replace("{{TITLE}}", esc(f"{BOOK} — {sub}"), 1)
    v2 = v2_kind(slug)
    if v2:                                              # ป้ายแม่แบบ v2 ที่ sab_qa / sab_wordcount ใช้เลือกกฎ
        head = head[:head.rindex("<body>")] + '<body data-tpl="2">'
    cover = f'''

<!-- ═══════════════ COVER ═══════════════ -->
<div class="cover">
<h1>{BOOK} · เล่ม {B.VOL} — {BOOK_TH}</h1>
<div class="sub">{esc(sub)}</div>
<div class="desc">{esc(desc)}</div>
</div>

{v2_body(*v2) if v2 else BODY_MARK}

'''
    return head + cover + tail


def target(slug):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit(f"slug ต้องเป็น a-z 0-9 - เท่านั้น: {slug!r}")
    return os.path.join(DOCS, f"{B.PREFIX}-{slug}.html")


def create(slug, sub=None, desc=None):
    path = target(slug)
    if os.path.exists(path):
        sys.exit(f"ปฏิเสธ: {os.path.relpath(path, ROOT)} มีอยู่แล้ว (ใช้ --sync ถ้าต้องการอัปเดตเปลือก)")
    v2 = v2_kind(slug)
    if sub is None:                                     # บท/หน้าพื้นฐาน: ชื่อจาก sab_book.py
        if not v2:
            sys.exit(__doc__)
        kind, n = v2
        sub = f"พื้นฐาน {n} — {B.BASE_TITLES[n]}" if kind == "base" else f"บท {n} — {B.TITLES.get(n, '…')}"
        desc = "…"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(skeleton(slug, sub, desc))
    print(f"สร้าง {os.path.relpath(path, ROOT)}")


def sync():
    """แทนหัว (ถึง <body>) และท้าย (ตั้งแต่ Thai script) ด้วยเปลือกปัจจุบัน · เก็บ <title> เดิมของแต่ละไฟล์"""
    head, tail = shell()
    changed = 0
    for path in sorted(glob.glob(os.path.join(DOCS, f"{B.PREFIX}-*.html"))):
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        body_tag = re.search(r"<body\b[^>]*>", src)           # หน้า v2 มี <body data-tpl="2"> — เก็บแท็กเดิมไว้
        if not body_tag or TAIL_MARK not in src:
            print(f"ข้าม (ไม่ใช่เปลือก {B.PREFIX}): {os.path.basename(path)}")
            continue
        m = re.search(r"<title>(.*?)</title>", src, re.S)
        title = m.group(1) if m else BOOK
        body = src[body_tag.end():src.rindex(TAIL_MARK)]
        new_head = head.replace("{{TITLE}}", title, 1)
        new = new_head[:new_head.rindex("<body>")] + body_tag.group(0) + body + tail
        if new != src:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            changed += 1
            print(f"อัปเดตเปลือก {os.path.basename(path)}")
    print(f"--sync: เปลี่ยน {changed} ไฟล์")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--sync"]:
        sync()
    elif len(args) in (1, 3) and not args[0].startswith("-"):
        create(*args)
    else:
        print(__doc__)
        sys.exit(1)
