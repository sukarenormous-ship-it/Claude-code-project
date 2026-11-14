#!/usr/bin/env python3
"""สร้าง docs/sab-appendix-glossary.html (ภาคผนวก B · ศัพท์ 3 ชั้น) จากกล่อง 📖 ของทุกบท + JSON ศัพท์_v09

ต่อยอดจาก nq_glossary.py
  - เรียงบทเป็นตัวเลข (ต้นแบบใช้ sorted(glob) → part10 มาก่อน part2)
  - ชั้นคำอ่านจาก <span class="tier" data-tier="ก|ข|ค"> ในแต่ละ <li> (สัญญา markup แผน 5.1 #23)
    ก = แอป/บัญชี · ข = แกนกลยุทธ์ · ค = ลงลึก · ไม่มี span → ชั้นตามตำแหน่ง (3 คำแรก = ก · ที่เหลือ = ข)
  - data-tier ที่ <li>/<strong> = ผิด (regex จะทิ้งคำเงียบ ๆ) → ฟ้อง
  - คำเดียวกันห้ามอยู่คนละชั้น · คำซ้ำข้ามบทเก็บบทแรกที่พบ
  - รวมศัพท์ v0.9 ที่ยังใช้จาก docs/sab-figures.json คีย์ ศัพท์_v09 (ถ้ามี)
  - ใช้เปลือก tools/sab_shell/ (ต้นแบบดึงเปลือกจาก nq-part1.html ตายตัว)
  - รอบ v2 (แผน 14.5): อ่านกล่อง 📖 ของหน้าพื้นฐาน docs/sab-baseN.html ก่อนบท 0 (ป้าย "พื้นฐาน N" · ชั้นตั้งต้น ก)
    หน้า v2 เขียนกล่อง 📖 เป็นรายการเดียวได้ (ไม่ต้องแบ่ง "3 คำที่ต้องจำก่อน / ที่เหลือ") — ไม่มี span.tier = ชั้น ข (หน้าพื้นฐาน = ก)

    python3 tools/sab_glossary.py
    python3 tools/sab_glossary.py --check      # ตรวจอย่างเดียว ไม่เขียน
    python3 tools/sab_glossary.py --selftest
"""

import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

TIER_NAMES = {"ก": "ชั้น ก — คำบนแอปและบัญชี", "ข": "ชั้น ข — แกนของกลยุทธ์", "ค": "ชั้น ค — ลงลึก (อ่านเมื่อพร้อม)"}
TARGET = "sab-appendix-glossary.html"


def _strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def _items(seg):
    """<li>…</li> ใน segment → [(คำ, นิยาม, tier|None, ปัญหา|None)]"""
    out = []
    for li_attrs, li in re.findall(r"<li\b([^>]*)>(.*?)</li>", seg, re.S):
        m = re.match(r"\s*<strong\b([^>]*)>(.*?)</strong>\s*=\s*(.*)", li, re.S)
        if "data-tier" in li_attrs or (m and "data-tier" in m.group(1)):
            out.append((_strip(m.group(2)) if m else _strip(li)[:30], "", None, "data-tier ต้องอยู่ที่ <span class=\"tier\">"))
            continue
        if not m:
            continue
        tm = re.search(r'<span class="tier" data-tier="([^"]*)"', m.group(3))
        tier = tm.group(1) if tm else None
        prob = None if tier in (None, "ก", "ข", "ค") else f"data-tier={tier!r} ต้องเป็น ก/ข/ค"
        desc = _strip(re.sub(r'<span class="tier"[^>]*>.*?</span>', "", m.group(3)))
        out.append((_strip(m.group(2)), desc, tier, prob))
    return out


def collect(docs=B.DOCS, fig_path=None):
    rows, problems, seen = [], [], {}
    for path in B.teaching_files(docs):                 # หน้าพื้นฐาน 1..4 ก่อน แล้วบท 0..18
        part, base = B.part_no(path), B.base_no(path)
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        v2 = B.is_v2(html, path)
        blk = B.term_box(html, v2)
        if blk is None:
            continue
        must = re.search(r"<strong>3 คำที่ต้องจำก่อน</strong></p>\s*<ul>(.*?)</ul>", blk, re.S)
        rest = re.search(r"<strong>ที่เหลือ</strong>(.*)", blk, re.S)
        if v2 and not must and not rest:                # v2: รายการเดียวทั้งกล่อง
            groups = [(blk, "ก" if base is not None else "ข")]
        else:
            groups = [(must.group(1) if must else "", "ก"), (rest.group(1) if rest else "", "ข")]
        for seg, default in groups:
            for term, desc, tier, prob in _items(seg):
                if prob:
                    problems.append(f"{name}: {term!r} {prob}")
                    continue
                tier = tier or default
                key = term.casefold()
                if key in seen:
                    if seen[key][1] != tier:
                        problems.append(f"{name}: {term!r} ชั้น {tier} แต่{seen[key][0]} ให้ชั้น {seen[key][1]}")
                    continue
                seen[key] = (B.page_label(path), tier)
                rows.append({"บท": part, "ชั้น": tier, "คำ": term, "นิยาม": desc,
                             **({"พื้นฐาน": base} if base is not None else {})})
    fig_path = fig_path or os.path.join(docs, "sab-figures.json")
    if os.path.exists(fig_path):
        with open(fig_path, encoding="utf-8") as fh:
            v09 = json.load(fh).get("ศัพท์_v09") or []
        for it in v09 if isinstance(v09, list) else []:
            term = it.get("คำ")
            if not term or term.casefold() in seen:
                continue
            seen[term.casefold()] = ("ต้นฉบับ v0.9", it.get("ชั้น", "ค"))
            rows.append({"บท": None, "ชั้น": it.get("ชั้น", "ค"), "คำ": term, "นิยาม": it.get("นิยาม", "")})
    return rows, problems


def render(rows):
    def table(items):
        trs = []
        for r in items:
            where = (f'<a href="{B.PREFIX}-base{r["พื้นฐาน"]}.html">พื้นฐาน {r["พื้นฐาน"]}</a>' if r.get("พื้นฐาน")
                     else f'<a href="{B.PREFIX}-part{r["บท"]}.html">บท {r["บท"]}</a>' if r["บท"] is not None
                     else "ต้นฉบับ v0.9")
            trs.append(f'<tr><td class="nw"><strong>{r["คำ"]}</strong></td><td>{r["นิยาม"]}</td>'
                       f'<td class="nw">{where}</td></tr>')
        return ('<div class="tw"><table data-nosrc>\n<tr><th class="nw">คำ</th><th>ความหมาย</th>'
                '<th class="nw">พบครั้งแรก</th></tr>\n' + "\n".join(trs) + "\n</table></div>")

    parts = []
    for t in ("ก", "ข", "ค"):
        items = [r for r in rows if r["ชั้น"] == t]
        if items:
            parts.append(f"<h2>{TIER_NAMES[t]}</h2>\n{table(items)}")
    body = f'''
<div class="bx bb" style="font-size:.92em"><div class="bt">🧭 วิธีใช้หน้านี้</div>
<p>ศัพท์ทั้งเล่มแบ่งสามชั้น — ชั้น ก คือคำที่เจอบนแอปและในบัญชี ชั้น ข คือแกนของกลยุทธ์
ชั้น ค เปิดดูเมื่ออ่านกล่องลงลึก · หน้านี้สร้างจากกล่องศัพท์ในบทโดยตรง จึงตรงกับเนื้อหาเสมอ</p></div>

{chr(10).join(parts)}

<div class="bx ba"><div class="bt">📖 หมายเหตุ</div>
<p>หน้านี้สร้างด้วย <code>tools/sab_glossary.py</code> · ถ้าแก้กล่องศัพท์ในบทใด ให้รันสคริปต์ใหม่</p></div>
'''
    return B.page("ภาคผนวก B: ศัพท์ 3 ชั้น", "ภาคผนวก B — ศัพท์ 3 ชั้น",
                  "คำบนแอป · แกนกลยุทธ์ · ลงลึก — แต่ละคำลิงก์กลับไปบทที่พบครั้งแรก", body)


def selftest():
    head, tail = B.shell()

    def ch(items_must, items_rest=""):
        return (head + '<div class="bx bb"><div class="bt">📖 ศัพท์ใหม่ในตอนนี้</div>'
                f'<p><strong>3 คำที่ต้องจำก่อน</strong></p><ul>{items_must}</ul>'
                f'<p><strong>ที่เหลือ</strong></p><ul>{items_rest}</ul></div>\n' + tail)
    ok = True
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "sab-part2.html"), "w", encoding="utf-8").write(ch(
            '<li><strong>basis</strong> = ส่วนต่าง <span class="tier" data-tier="ข"></span></li>',
            '<li><strong>funding</strong> = ค่าถือ</li>'))
        open(os.path.join(d, "sab-part10.html"), "w", encoding="utf-8").write(ch(
            '<li data-tier="ก"><strong>ผิดที่</strong> = x</li>'
            '<li><strong>basis</strong> = ซ้ำ <span class="tier" data-tier="ก"></span></li>'
            '<li><strong>คู่ปลอม</strong> = y <span class="tier" data-tier="ค"></span></li>'))
        rows, probs = collect(d, os.path.join(d, "none.json"))
        # v2: หน้าพื้นฐานมาก่อนบท · รายการเดียว · <li> ใน details.file ที่ตามหลังกล่อง 📖 ไม่ถูกเก็บเป็นศัพท์
        v2box = ('<div class="bx bb"><div class="bt">📖 ศัพท์ใหม่ในตอนนี้</div><ul>{}</ul></div>\n'
                 '<details class="file"><summary>📁 แฟ้มของบทนี้</summary><div class="bx sheet"><ul>'
                 '<li><strong>ไม่ใช่ศัพท์</strong> = อยู่ในแฟ้ม</li></ul></div></details>\n')
        v2head = head.replace("<body>", '<body data-tpl="2">')
        open(os.path.join(d, "sab-base2.html"), "w", encoding="utf-8").write(v2head + v2box.format(
            '<li><strong>Short (สถานะขาย/ขายชอร์ต)</strong> = ขายก่อน</li>') + tail)
        open(os.path.join(d, "sab-part3.html"), "w", encoding="utf-8").write(v2head + v2box.format(
            '<li><strong>Carry (ผลตอบแทนจากการถือ)</strong> = ได้จากการถือ</li>'
            '<li><strong>Margin (หลักประกัน)</strong> = เงินค้ำ <span class="tier" data-tier="ก"></span></li>') + tail)
        rows2, probs2 = collect(d, os.path.join(d, "none.json"))
    got2 = [(r.get("พื้นฐาน"), r["บท"], r["คำ"], r["ชั้น"]) for r in rows2]
    want2 = [(2, None, "Short (สถานะขาย/ขายชอร์ต)", "ก"), (None, 2, "basis", "ข"), (None, 2, "funding", "ข"),
             (None, 3, "Carry (ผลตอบแทนจากการถือ)", "ข"), (None, 3, "Margin (หลักประกัน)", "ก"), (None, 10, "คู่ปลอม", "ค")]
    if got2 != want2 or len(probs2) != len(probs) or 'sab-base2.html">พื้นฐาน 2</a>' not in render(rows2):
        ok = False
        print("selftest ล้ม: หน้า base / บท v2", got2, probs2)
    order = [r["บท"] for r in rows]
    if order != sorted(order):
        ok = False
        print("selftest ล้ม: ลำดับบทไม่เป็นตัวเลข", order)
    if [r["คำ"] for r in rows] != ["basis", "funding", "คู่ปลอม"]:
        ok = False
        print("selftest ล้ม: คำที่เก็บได้", [r["คำ"] for r in rows])
    if {r["คำ"]: r["ชั้น"] for r in rows} != {"basis": "ข", "funding": "ข", "คู่ปลอม": "ค"}:
        ok = False
        print("selftest ล้ม: ชั้นคำ", rows)
    for e in ("data-tier ต้องอยู่", "'basis' ชั้น ก"):
        if not any(e in p for p in probs):
            ok = False
            print("selftest ล้ม: ไม่จับ", e, probs)
    print("selftest", "ผ่าน ✓ (เรียง part2 ก่อน part10 · data-tier ผิดที่ถูกจับ · คำซ้ำข้ามชั้นถูกจับ · "
          "หน้า base มาก่อนบทและติดป้าย \"พื้นฐาน N\" · กล่อง 📖 แบบ v2 ไม่เก็บ <li> ของ details.file)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if any(x not in ['--check', '--selftest'] for x in sys.argv[1:]):
        print(__doc__)
        sys.exit(2)
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    rows, problems = collect()
    for p in problems:
        print("  -", p)
    if "--check" in sys.argv:
        print(f"ศัพท์ {len(rows)} คำ · ปัญหา {len(problems)} ข้อ")
        sys.exit(1 if problems else 0)
    if not rows:
        print("ยังไม่มีบทที่มีกล่อง 📖 — ยังไม่เขียนภาคผนวก B")
        sys.exit(1 if problems else 0)
    with open(os.path.join(B.DOCS, TARGET), "w", encoding="utf-8") as fh:
        fh.write(render(rows))
    print(f"เขียน docs/{TARGET} · {len(rows)} คำ · " +
          " · ".join(f"ชั้น {t}: {sum(1 for r in rows if r['ชั้น'] == t)}" for t in "กขค"))
    sys.exit(1 if problems else 0)
