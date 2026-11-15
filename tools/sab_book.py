"""ค่าคงที่และตัวช่วยกลางของหนังสือ "Stat Arb for Non Quant" (เล่ม 1 = sab · เล่ม 2 = sab2) — ใช้ร่วมโดย sab_*.py

prefix · ชื่อบท · การเรียงบทเป็นตัวเลข · ประกอบหน้าด้วยเปลือก tools/sab_shell/
(nq_*.py ฝังค่าเหล่านี้ซ้ำในทุกไฟล์และเรียงบทแบบสตริง ทำให้ part10 มาก่อน part2)

เลือกเล่ม (Book selection): ตัวแปรแวดล้อม SAB_BOOK=sab2 หรืออาร์กิวเมนต์ --book sab2 ของเครื่องมือใดก็ได้
(ค่าเริ่มต้น sab = เล่ม 1 · ไม่ระบุ = พฤติกรรมเดิมทุกอย่าง) — import โมดูลนี้จะดึง --book ออกจาก sys.argv
แล้วตั้ง SAB_BOOK ให้กระบวนการลูกด้วย จึงใส่ --book ตรงไหนของบรรทัดคำสั่งก็ได้
    python3 tools/sab_qa.py --book sab2 --selftest      ≡   SAB_BOOK=sab2 python3 tools/sab_qa.py --selftest
"""

import glob
import html as htmllib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
TOOLS = os.path.join(ROOT, "tools")
SHELL = os.path.join(ROOT, "tools", "sab_shell")


def _book_from_argv():
    """--book X / --book=X ใน sys.argv → ตัดออก (ให้ตัวแยกอาร์กิวเมนต์เดิมของแต่ละเครื่องมือไม่เห็น) แล้วตั้ง SAB_BOOK"""
    a = sys.argv
    for i, x in enumerate(list(a)):
        if x == "--book" and i + 1 < len(a):
            os.environ["SAB_BOOK"] = a[i + 1]
            del a[i:i + 2]
            return
        if x.startswith("--book="):
            os.environ["SAB_BOOK"] = x.split("=", 1)[1]
            del a[i]
            return


_book_from_argv()
BOOK_ID = os.environ.get("SAB_BOOK", "sab") or "sab"
if BOOK_ID not in ("sab", "sab2"):
    sys.exit(f"SAB_BOOK / --book ต้องเป็น sab หรือ sab2 (พบ {BOOK_ID!r})")
PREFIX = BOOK_ID
BOOK = "Stat Arb for Non Quant"
# ชื่อบทตามสารบัญในแผน (docs/sab-book-plan.md หัวข้อ 4)
TITLES_1 = {
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
    14: "−22 แล้วสัญญาณกลับมาที่ 3.8",
    15: "อ่านผลที่ขาดทุนให้เป็น",
    16: "จากกราฟสู่คำสั่งจริง",
    17: "ธรรมชาติของ stat arb: ใครจ่ายเงินให้เรา",
    18: "เอาไปต่อยอด: คู่ใหม่ ตลาดใหม่ ไอเดียใหม่",
}

# ภาคพื้นฐาน "คืนก่อนวันที่ 1" (แผน 14.5) — หน้า docs/sab-baseN.html อ่านก่อนบท 0 · เป็นแม่แบบ v2 เสมอ
BASE_TITLES_1 = {
    1: "ซื้อไว้ก่อน แล้วขายทีหลัง",
    2: "ขายก่อน แล้วซื้อคืนทีหลัง",
    3: "สองขาในชุดเดียว",
    4: "สัญญาที่มีวันหมดอายุ และเงินสามกอง",
}

# เล่ม 2 (docs/sab2-book-plan.md หัวข้อ 4 · ชื่อร่าง) — บท sab2-part1..17 · ไม่มีหน้าพื้นฐาน
TITLES_2 = {
    1: "เส้นที่ลากผ่านจุด: h มาจากข้อมูลอย่างไร",
    2: "ราคาหรือ log ราคา",
    3: "มีเชือกจริงไหม: ทดสอบแทนการมอง",
    4: "กลับเร็วแค่ไหน และมั่นใจได้แค่ไหน",
    5: "ไม้บรรทัดที่เลื่อนได้",
    6: "เชื่อข้อมูลใหม่แค่ไหน: Kalman แบบคิดด้วยมือ",
    7: "เข้าเมื่อไร ออกเมื่อไร: จากเส้น 2 ไปถึง \"optimal\"",
    8: "หักแรงร่วมออก เหลืออะไร",
    9: "PCA: ให้ข้อมูลบอกแรงร่วมเอง",
    10: "ตะกร้าหลายขา",
    11: "จัดเงินหลายกลยุทธ์",
    12: "เครื่อง backtest ของตัวเอง",
    13: "ลองได้กี่ครั้งก่อนผลจะไม่มีความหมาย",
    14: "ต้นทุน ขนาด และการเสื่อมของกลยุทธ์",
    15: "รวมหลายสัญญาณ และโมเดลที่เรียนรู้เอง",
    16: "สิ่งที่อยู่ถัดไป: ความสัมพันธ์ไม่เป็นเส้นตรง และ options",
    17: "โครงงานของคุณเอง",
}

# ทะเบียนเล่ม: ทุกอย่างที่ต่างกันระหว่างเล่มอยู่ที่นี่ที่เดียว (เครื่องมืออ่านผ่านชื่อระดับโมดูลด้านล่าง)
BOOKS = {
    "sab": {"vol": 1, "th": "เชือกที่ผูกสองราคา", "titles": TITLES_1, "base_titles": BASE_TITLES_1,
            "plan": "docs/sab-book-plan.md", "shell_extra": None, "prev": None},
    "sab2": {"vol": 2, "th": "วัดเชือก สร้างพอร์ต ทดสอบให้ซื่อ", "titles": TITLES_2, "base_titles": {},
             "plan": "docs/sab2-book-plan.md", "shell_extra": os.path.join(TOOLS, "sab2_shell", "extra.css"),
             "prev": "sab"},
}
CFG = BOOKS[BOOK_ID]
VOL = CFG["vol"]
BOOK_TH = CFG["th"]
TITLES = CFG["titles"]
BASE_TITLES = CFG["base_titles"]
FIRST_PART, LAST_PART = min(TITLES), max(TITLES)
LAST_BASE = max(BASE_TITLES, default=0)
FIG = os.path.join(DOCS, f"{PREFIX}-figures.json")
TERMS = os.path.join(TOOLS, f"{PREFIX}_terms.json")
BIBLE = os.path.join(TOOLS, f"{PREFIX}_bible.json")
FIG_PLUGINS = os.path.join(TOOLS, f"{PREFIX}_figures_ch")
CHART_PLUGINS = os.path.join(TOOLS, f"{PREFIX}_charts_ch")


def load_terms(book=None):
    """ทะเบียนศัพท์ของเล่ม (tools/<prefix>_terms.json) · เล่มที่มีเล่มก่อนหน้า: คำของเล่มก่อนถือว่าสอนแล้ว
    (ใส่ "สอน": "เล่ม1" → teach_order = None → W22 ไม่ฟ้อง) · คำที่ลงทะเบียนซ้ำในเล่มนี้ใช้ของเล่มก่อน และติด "_ซ้ำ"
    คืน None ถ้าเล่มนี้ยังไม่มีทะเบียน"""
    book = book or BOOK_ID
    path = os.path.join(TOOLS, f"{book}_terms.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        terms = json.load(fh)
    prev = BOOKS[book]["prev"]
    if prev:
        old = load_terms(prev) or {}
        for k, v in old.items():
            if k.startswith("_"):
                continue
            taught = {**v, "สอน": f"เล่ม{BOOKS[prev]['vol']}"}
            if k in terms:
                taught["_ซ้ำ"] = terms[k].get("สอน")
            terms[k] = taught
    return terms


def part_no(path):
    m = re.search(rf"{PREFIX}-part(\d+)\.html$", os.path.basename(path))
    return int(m.group(1)) if m else None


def base_no(path):
    m = re.search(rf"{PREFIX}-base(\d+)\.html$", os.path.basename(path))
    return int(m.group(1)) if m else None


def chapter_files(docs=DOCS):
    """docs/<prefix>-partN.html เรียงตามเลขบท (ไม่ใช่ตามสตริง)"""
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
    """(head, tail) ของเปลือก · เล่มที่มี shell_extra (เล่ม 2: tools/sab2_shell/extra.css) = เปลือกกลาง + CSS เพิ่ม
    ต่อท้ายบล็อก <style> (เปลือกกลางไม่เปลี่ยน → หน้าเล่ม 1 ไม่ต้อง reshell)"""
    with open(os.path.join(SHELL, "head.html"), encoding="utf-8") as fh:
        head = fh.read()
    with open(os.path.join(SHELL, "tail.html"), encoding="utf-8") as fh:
        tail = fh.read()
    extra = CFG["shell_extra"]
    if extra:
        with open(extra, encoding="utf-8") as fh:
            css = fh.read().strip()
        i = head.index("</style>")
        head = head[:i] + "\n" + css + "\n" + head[i:]
    return head, tail


def page(title, sub, desc, body):
    head, tail = shell()
    esc = htmllib.escape
    head = head.replace("{{TITLE}}", esc(f"{BOOK} — {title}"), 1)
    cover = (f'\n<div class="cover">\n<h1>{BOOK} · เล่ม {VOL} — {BOOK_TH}</h1>\n'
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
