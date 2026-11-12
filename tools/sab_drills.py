#!/usr/bin/env python3
"""สร้าง docs/sab-appendix-drills.html (ภาคผนวก D · แบบฝึกทั้งเล่ม) และ docs/sab-appendix-answers.html (เฉลยแยก)

ต่อยอดจาก nq_drills.py
  - เรียงบทเป็นตัวเลข (ต้นแบบ sorted(glob) → part10 มาก่อน part2)
  - ใช้ html.parser แทน regex: ต้นแบบ `<li>(.*?)</li>` ทิ้ง/ตัดข้อเมื่อมีรายการซ้อน, `<li class>`, หรือ <p> นำหน้า <ol>
  - แยก <details class="ans"> ออกไปหน้าเฉลย (เล่มนี้ตัดสินว่า "มีเฉลย")
  - รวมข้อเก่าของ v0.9 ที่ยังใช้จาก docs/sab-figures.json คีย์ แบบฝึก_v09 (ถ้ามี: {"chNN": [{"ข้อ": html, "เฉลย": html}]})
  - ข้อความหน้าเป็น config ด้านล่าง · ใช้เปลือก tools/sab_shell/

    python3 tools/sab_drills.py
    python3 tools/sab_drills.py --check
    python3 tools/sab_drills.py --selftest
"""

import json
import os
import re
import sys
import tempfile
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

TARGET = "sab-appendix-drills.html"
ANSWERS = "sab-appendix-answers.html"
CONFIG = {
    "วิธีใช้": ("ทุกบทมีสามข้อ: (ก) คำนวณเลขใหม่ (ข) ตัดสินใจและอธิบาย (ค) ถ่ายโอนไปตลาดอื่น · "
               "ทำก่อนแล้วค่อยเปิดหน้าเฉลย · ข้อที่ขึ้นกับบัญชีของคุณเอง เฉลยจะบอกวิธีตรวจแทนตัวเลข"),
    "ไม่มีเฉลย": "ข้อนี้ขึ้นกับตลาดและบัญชีของคุณเอง — ตรวจด้วยเกณฑ์ผ่านในใบงานของบท",
}
VOID = {"br", "hr", "img", "meta", "link", "input", "wbr", "source"}


class DrillParser(HTMLParser):
    """หา <ol> แรกหลังกล่อง ✍️ ลองทำเอง แล้วเก็บ <li> ระดับบนสุดของ ol นั้นแบบนับชั้น"""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.armed = False        # เจอหัว ✍️ แล้ว รอ <ol>
        self.depth = 0            # ชั้นของ ol เป้าหมาย (0 = ยังไม่อยู่ใน)
        self.li_depth = 0
        self.items, self.cur, self.done = [], None, False
        self.in_ans = 0
        self.ans = None

    def _raw(self):
        return self.get_starttag_text() or ""

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        raw = self._raw()
        if self.depth:
            if self.in_ans:                      # ภายในเฉลย: เก็บดิบ ไม่แตะตัวนับชั้นของ ol/li
                if tag == "details":
                    self.in_ans += 1
                self.ans.append(raw)
                return
            if tag == "ol" or tag == "ul":
                self.depth += 1
            if tag == "li" and self.depth == 1 and self.li_depth == 0:
                self.cur, self.ans, self.li_depth = [], None, 1
                return
            if self.cur is not None:
                if tag == "li":
                    self.li_depth += 1
                if tag == "details" and ("ans" in (dict(attrs).get("class") or "").split()):
                    self.in_ans, self.ans = 1, []
                    return
                if self.in_ans:
                    if tag == "details":
                        self.in_ans += 1
                    self.ans.append(raw)
                else:
                    self.cur.append(raw)
            return
        if self.armed and tag == "ol":
            self.depth = 1

    def handle_startendtag(self, tag, attrs):
        if self.cur is not None and not self.done:
            (self.ans if self.in_ans else self.cur).append(self._raw())

    def handle_endtag(self, tag):
        if self.done or not self.depth:
            return
        if self.cur is not None:
            if self.in_ans:
                if tag == "details":
                    self.in_ans -= 1
                    if self.in_ans == 0:
                        return
                self.ans.append(f"</{tag}>")
                return
            if tag == "li":
                self.li_depth -= 1
                if self.li_depth == 0:
                    self.items.append(("".join(self.cur).strip(), "".join(self.ans).strip() if self.ans is not None else None))
                    self.cur = None
                    return
            self.cur.append(f"</{tag}>")
        if tag in ("ol", "ul"):
            self.depth -= 1
            if self.depth == 0:
                self.done = True

    def handle_data(self, data):
        if "✍️ ลองทำเอง" in data and not self.depth:
            self.armed = True
        if self.cur is not None and not self.done:
            (self.ans if self.in_ans else self.cur).append(data)

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")


def _clean_answer(a):
    if a is None:
        return None
    return re.sub(r"^\s*<summary\b.*?</summary>", "", a, flags=re.S).strip()


def collect(docs=B.DOCS, fig_path=None):
    chapters = []
    for path in B.chapter_files(docs):
        with open(path, encoding="utf-8") as fh:
            p = DrillParser()
            p.feed(fh.read())
        items = [(q, _clean_answer(a)) for q, a in p.items]
        chapters.append((B.part_no(path), items, []))
    fig_path = fig_path or os.path.join(docs, "sab-figures.json")
    if os.path.exists(fig_path):
        with open(fig_path, encoding="utf-8") as fh:
            old = json.load(fh).get("แบบฝึก_v09") or {}
        by = {c[0]: c for c in chapters}
        for k, lst in (old.items() if isinstance(old, dict) else []):
            m = re.fullmatch(r"ch(\d+)", k)
            if not m or not isinstance(lst, list):
                continue
            n = int(m.group(1))
            extra = [(it.get("ข้อ", ""), it.get("เฉลย")) for it in lst if isinstance(it, dict)]
            if n in by:
                by[n][2].extend(extra)
            else:
                chapters.append((n, [], extra))
        chapters.sort(key=lambda c: c[0])
    return chapters


def render(chapters):
    total = sum(len(i) + len(x) for _, i, x in chapters)
    q_parts, a_parts = [], []
    for n, items, extra in chapters:
        title = B.TITLES.get(n, "")
        allq = items + extra
        if not allq:
            continue
        lis = "\n".join(f'<li id="q{n}-{i}">{q} <a href="{ANSWERS}#a{n}-{i}">ดูเฉลย</a></li>'
                        for i, (q, _) in enumerate(allq, 1))
        note = (f'<p class="nw" style="font-size:.88em;color:#64748b">ข้อ {len(items) + 1}–{len(allq)} มาจากต้นฉบับ v0.9</p>'
                if extra else "")
        q_parts.append(f'<h2 id="ch{n}">บท {n} — {title}</h2>\n<p><a href="{B.PREFIX}-part{n}.html">กลับไปอ่านบทนี้</a></p>\n'
                       f'<ol>\n{lis}\n</ol>{note}')
        ans = "\n".join(f'<li id="a{n}-{i}">{a if a else CONFIG["ไม่มีเฉลย"]} '
                        f'<a href="{TARGET}#q{n}-{i}">กลับไปที่ข้อ</a></li>' for i, (_, a) in enumerate(allq, 1))
        a_parts.append(f'<h2 id="ch{n}">บท {n} — {title}</h2>\n<ol>\n{ans}\n</ol>')
    intro = f'<div class="bx bb" style="font-size:.92em"><div class="bt">🧭 วิธีใช้หน้านี้</div><p>{CONFIG["วิธีใช้"]}</p></div>'
    foot = ('<div class="bx ba"><div class="bt">📖 หมายเหตุ</div><p>หน้านี้สร้างด้วย <code>tools/sab_drills.py</code> '
            'ดึงจากกล่อง ✍️ ลองทำเอง ในบทโดยตรง ถ้าแก้บทให้รันสคริปต์ใหม่</p></div>')
    drills = B.page("ภาคผนวก D: แบบฝึกทั้งเล่ม", "ภาคผนวก D — แบบฝึกทั้งเล่ม",
                    f"{total} ข้อจาก {len(chapters)} บท · เฉลยแยกหน้า", intro + "\n" + "\n".join(q_parts) + "\n" + foot)
    answers = B.page("เฉลยแบบฝึก", "เฉลยแบบฝึก (คู่กับภาคผนวก D)",
                     "ทำข้อก่อน แล้วค่อยเปิดหน้านี้", intro + "\n" + "\n".join(a_parts) + "\n" + foot)
    return drills, answers


def selftest():
    head, tail = B.shell()

    def ch(ol):
        return head + '<div class="bx bg"><div class="bt">✍️ ลองทำเอง</div></div>\n' + ol + "\n<ol><li>ไม่ใช่แบบฝึก</li></ol>" + tail
    ok = True
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "sab-part10.html"), "w", encoding="utf-8").write(ch(
            '<ol><li>ข้อหนึ่ง <ul><li>ย่อย ก</li><li>ย่อย ข</li></ul> ต่อท้าย'
            '<details class="ans"><summary>แนวคำตอบ</summary><p>ตอบ <strong>11,220</strong></p></details></li>'
            '<li class="x">ข้อสอง</li><li>ข้อสาม</li></ol>'))
        open(os.path.join(d, "sab-part2.html"), "w", encoding="utf-8").write(ch(
            '<ol><li>A<details class="ans"><summary>s</summary><ol><li>ขั้น 1</li><li>ขั้น 2</li></ol></details></li></ol>'))
        chs = collect(d, os.path.join(d, "none.json"))
    if [c[0] for c in chs] != [2, 10]:
        ok = False
        print("selftest ล้ม: ลำดับบท", [c[0] for c in chs])
    ten = dict((c[0], c[1]) for c in chs)[10]
    if len(ten) != 3 or "ย่อย ข" not in ten[0][0] or "ต่อท้าย" not in ten[0][0] or "ข้อสอง" not in ten[1][0]:
        ok = False
        print("selftest ล้ม: ข้อที่มีรายการซ้อน/li class", ten)
    if not ten[0][1] or "11,220" not in ten[0][1] or "summary" in ten[0][1] or "แนวคำตอบ" in ten[0][0]:
        ok = False
        print("selftest ล้ม: แยกเฉลย", ten[0])
    two = dict((c[0], c[1]) for c in chs)[2]
    if len(two) != 1 or "ขั้น 2" not in (two[0][1] or ""):
        ok = False
        print("selftest ล้ม: เฉลยมีรายการซ้อน", two)
    print("selftest", "ผ่าน ✓ (เรียง part2 ก่อน part10 · details/รายการซ้อน · li class · แยกเฉลย)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    chapters = collect()
    total = sum(len(i) + len(x) for _, i, x in chapters)
    short = [n for n, i, _ in chapters if len(i) != 3]
    if short:
        print("  - บทที่ ✍️ ไม่ครบ 3 ข้อ:", short)
    if "--check" in sys.argv:
        print(f"แบบฝึก {total} ข้อ จาก {len(chapters)} บท")
        sys.exit(1 if short else 0)
    if not total:
        print("ยังไม่มีบทที่มีกล่อง ✍️ — ยังไม่เขียนภาคผนวก D")
        sys.exit(0)
    drills, answers = render(chapters)
    for name, html in ((TARGET, drills), (ANSWERS, answers)):
        with open(os.path.join(B.DOCS, name), "w", encoding="utf-8") as fh:
            fh.write(html)
    print(f"เขียน docs/{TARGET} + docs/{ANSWERS} · {total} ข้อ จาก {len(chapters)} บท")
