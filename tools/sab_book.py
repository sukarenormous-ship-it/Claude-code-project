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

# ภาคพื้นฐาน "คืนก่อนวันที่ 1" (แผน 14.5) — หน้า docs/sab-baseN.html อ่านก่อนบท 0 · เป็นแม่แบบ v2 เสมอ
BASE_TITLES = {
    1: "ซื้อไว้ก่อน แล้วขายทีหลัง",
    2: "ขายก่อน แล้วซื้อคืนทีหลัง",
    3: "สองขาในชุดเดียว",
    4: "สัญญาที่มีวันหมดอายุ และเงินสามกอง",
}
LAST_BASE = max(BASE_TITLES)


def part_no(path):
    m = re.search(rf"{PREFIX}-part(\d+)\.html$", os.path.basename(path))
    return int(m.group(1)) if m else None


def base_no(path):
    m = re.search(rf"{PREFIX}-base(\d+)\.html$", os.path.basename(path))
    return int(m.group(1)) if m else None


def chapter_files(docs=DOCS):
    """docs/sab-partN.html เรียงตามเลขบท (ไม่ใช่ตามสตริง)"""
    files = [p for p in glob.glob(os.path.join(docs, f"{PREFIX}-part*.html")) if part_no(p) is not None]
    return sorted(files, key=part_no)


def base_files(docs=DOCS):
    """docs/sab-baseN.html เรียงตามเลขหน้า"""
    files = [p for p in glob.glob(os.path.join(docs, f"{PREFIX}-base*.html")) if base_no(p) is not None]
    return sorted(files, key=base_no)


def teaching_files(docs=DOCS):
    """ลำดับอ่านของหน้าสอน: หน้าพื้นฐาน 1..4 แล้วบท 0..18"""
    return base_files(docs) + chapter_files(docs)


def page_label(path):
    """"พื้นฐาน N" หรือ "บท N" (None ถ้าไม่ใช่หน้าสอน)"""
    b, n = base_no(path), part_no(path)
    return f"พื้นฐาน {b}" if b is not None else (f"บท {n}" if n is not None else None)


def page_title(path):
    b, n = base_no(path), part_no(path)
    return BASE_TITLES.get(b, "") if b is not None else TITLES.get(n, "")


def is_v2(html, path=None):
    """หน้าแม่แบบ v2 = <body data-tpl="2"> (แผน 14.3) · หน้าพื้นฐานนับเป็น v2 เสมอ"""
    if path is not None and base_no(path) is not None:
        return True
    m = re.search(r"<body\b([^>]*)>", html)
    return bool(m and re.search(r'\bdata-tpl="2"', m.group(1)))


def term_box(html, v2=None):
    """เนื้อในกล่อง 📖 ศัพท์ใหม่ในตอนนี้ (ส่วนหลังหัวกล่อง) หรือ None
    v1: กล่อง 📖 เป็นกล่องสุดท้ายของหน้า (regex เดิมของ sab_glossary / sab_qa W9)
    v2: มี details.file ตามหลัง จึงนับ <div> เปิด/ปิดจนกล่องปิดจริง"""
    if not (is_v2(html) if v2 is None else v2):
        box = re.search(r"📖 ศัพท์ใหม่ในตอนนี้</div>(.*?)</div>\s*(?:<!--|$)", html, re.S)
        return box.group(1) if box else None
    m = re.search(r"📖 ศัพท์ใหม่ในตอนนี้\s*</div>", html)
    if not m:
        return None
    depth = 1
    for t in re.finditer(r"<(/?)div\b[^>]*>", html[m.end():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return html[m.end():m.end() + t.start()]
    return None


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
    """อ่านค่าตาม path ที่คั่นด้วย "." — คีย์ที่มีจุดในตัว (เช่น "บันไดที่0.1", "0.80") หาได้ด้วยการลองคีย์ยาวสุดก่อน"""
    parts = path.split(".")

    def walk(cur, i):
        if i == len(parts):
            return True, cur
        for j in range(len(parts), i, -1):
            key = ".".join(parts[i:j])
            if isinstance(cur, dict) and key in cur:
                ok, v = walk(cur[key], j)
                if ok:
                    return True, v
            elif isinstance(cur, list) and key.isdigit() and int(key) < len(cur):
                ok, v = walk(cur[int(key)], j)
                if ok:
                    return True, v
        return False, None
    ok, v = walk(fig, 0)
    if not ok:
        raise KeyError(path)
    return v
