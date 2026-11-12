"""ค่าคงที่และตัวช่วยกลางของเล่ม "Stat Arb for Non Quant · เล่ม 1" — ใช้ร่วมโดย sab_*.py

prefix · ชื่อบท · การเรียงบทเป็นตัวเลข · ประกอบหน้าด้วยเปลือก tools/sab_shell/
(nq_*.py ฝังค่าเหล่านี้ซ้ำในทุกไฟล์และเรียงบทแบบสตริง ทำให้ part10 มาก่อน part2)
"""

import glob
import html as htmllib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SHELL = os.path.join(ROOT, "tools", "sab_shell")
PREFIX = "sab"
BOOK = "Stat Arb for Non Quant"
BOOK_TH = "เชือกที่ผูกสองราคา"

# ชื่อบทตามสารบัญในแผน (docs/sab-book-plan.md หัวข้อ 4)
TITLES = {
    0: "ส่วนต่าง 3,000 บนหน้าจอ",
    1: "ค่าผ่านทางสองขา และนิ้วที่จับเชือก",
    2: "เงินบนโต๊ะมาจากไหน",
    3: "สมุดบัญชีสองขา",
    4: "คืนที่ราคาขึ้น 10%",
    5: "12.17% บนจอ เหลือ 5.23% ในมือ",
    6: "วันที่ 30: ปิดหรือถือ",
    7: "Perp: เชือกที่ไม่มีวันล็อก",
    8: "hedge แล้ว…จากอะไร",
    9: "สองเหรียญที่เดินด้วยกัน",
    10: "คู่ที่สวยที่สุดจาก 200 คู่",
    11: "สมุดบัญชีของคู่",
    12: "กฎก่อนกด: สามตอนจบที่ซ้อมไว้",
    13: "กลับจริง แต่ทันไหม",
    14: "−21 แล้วสัญญาณกลับมาที่ 3.8",
    15: "อ่านผลที่ขาดทุนให้เป็น",
    16: "จากกราฟสู่คำสั่งจริง",
    17: "ธรรมชาติของ stat arb: ใครจ่ายเงินให้เรา",
    18: "เอาไปต่อยอด: คู่ใหม่ ตลาดใหม่ ไอเดียใหม่",
}


def part_no(path):
    m = re.search(rf"{PREFIX}-part(\d+)\.html$", os.path.basename(path))
    return int(m.group(1)) if m else None


def chapter_files(docs=DOCS):
    """docs/sab-partN.html เรียงตามเลขบท (ไม่ใช่ตามสตริง)"""
    files = [p for p in glob.glob(os.path.join(docs, f"{PREFIX}-part*.html")) if part_no(p) is not None]
    return sorted(files, key=part_no)


def shell():
    with open(os.path.join(SHELL, "head.html"), encoding="utf-8") as fh:
        head = fh.read()
    with open(os.path.join(SHELL, "tail.html"), encoding="utf-8") as fh:
        tail = fh.read()
    return head, tail


def page(title, sub, desc, body):
    head, tail = shell()
    esc = htmllib.escape
    head = head.replace("{{TITLE}}", esc(f"{BOOK} — {title}"), 1)
    cover = (f'\n<div class="cover">\n<h1>{BOOK} · เล่ม 1 — {BOOK_TH}</h1>\n'
             f'<div class="sub">{sub}</div>\n<div class="desc">{desc}</div>\n</div>\n')
    return head + cover + body + "\n" + tail


def fmt(v):
    """ตัวเลขจาก JSON → ข้อความที่พิมพ์ในบท: comma หลักพัน · ลบใช้ U+2212 · ทศนิยมตามที่ JSON เก็บ"""
    if isinstance(v, bool) or v is None:
        return "" if v is None else str(v)
    if isinstance(v, int):
        s = f"{abs(v):,}"
    elif isinstance(v, float):
        txt = repr(abs(v))
        dec = len(txt.split(".")[1]) if "." in txt and "e" not in txt else 2
        s = f"{abs(v):,.{dec}f}"
    else:
        return str(v)
    return ("−" if v < 0 else "") + s


def get_path(fig, path):
    cur = fig
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            raise KeyError(path)
    return cur
