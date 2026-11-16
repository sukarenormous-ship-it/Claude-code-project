#!/usr/bin/env python3
"""ตรวจคุณภาพหนังสือ "Stat Arb for Non Quant · เล่ม 1" (docs/sab-*.html) ในคำสั่งเดียว

ต่อยอดจาก nq_qa.py (โครงสร้าง HTML · W11 <br> ปลอม · กล่องบังคับ · W8 ลิงก์ · W9 เพดานศัพท์)
แล้วเพิ่มกฎของเล่มนี้ตามแผน docs/sab-book-plan.md หัวข้อ 10.4
  W12 สัญลักษณ์/สูตรต้องห้ามนอก 🔎     W13 ทศนิยม > 2 ตำแหน่งนอก 🔎      W14 ลิงก์ #anchor ต้องมีจริง
  W15 ฉากเปิดต่อบทก่อน + .pq สะพาน      W16 ป้ายที่มาตาราง/กราฟ · table.fees  W18 คำต้องห้าม
  W19 ใบงาน                             W20 บัตรธรรมชาติ                  W21 หมายเหตุ h/β เมื่อชี้ math-part9
  W22 ห้ามใช้ก่อนสอน (tools/sab_terms.json)                                W23 .dist · W24 .whyline · W25 data-claim
  D1  (--final) ไม่มี data-pending เหลือ

หน้า v2 (แผน 14 · <body data-tpl="2"> · บท sab-partN.html และหน้าพื้นฐาน sab-baseN.html) ใช้ V1–V8 แทนกล่องบังคับเดิม
  V1 โครงบังคับ (.pos · .scene-open · .pq คำถาม · 🛑 .stop · .sum3 · ✍️ · .pq[data-hook] · 📖 · details.file ที่มี .sheet)
  V2 ทุก <h2> ตอนสอนมี .rest     V3 ทุก .figw มี .readfig "อ่านภาพ:"     V4 ทุก .fm นอก details มี .readeq "อ่านสมการ:"
  V5 ✍️ ≥ 5 ข้อ มี details.ans ทุกข้อ · details.hint ≥ 3 ข้อ (base: 3 / 2)     V6 <p> บรรยายมี "=" ≤ 2
  V7 ศัพท์ใหม่ ≤ 7 (base ≤ 4)     V8 ป้าย/คำที่เลิกใช้ (🔁 · ⚠️ ค่าเริ่มต้น · 🧭 นิสัยคิด · 🧭 เส้นทางอ่าน · 🟠 · "nq")
  กฎเดิมที่ยังใช้กับ v2: W11–W15 · W16 (ตารางติดป้ายเฉพาะเมื่อประกาศ data-src="sim|real|app") · W18–W23 · W25 · D1
  กฎเดิมที่ข้ามใน v2: กล่องบังคับเดิม · W9 (แทนด้วย V7) · W22 ทางด่วน 🟠 · W24 (.whyline 🔩 เลิกใช้)
  หน้า v1 ใช้กฎเดิมทุกข้อ

    python3 tools/sab_qa.py                    # ทุกไฟล์ docs/sab-*.html
    python3 tools/sab_qa.py --scope part4      # เฉพาะบท (W15 ข้ามเมื่อบทข้างเคียงยังไม่มีไฟล์)
    python3 tools/sab_qa.py --pending          # ลิงก์ไปไฟล์ที่ยังไม่มีในกล่อง data-pending = เตือน ไม่ fatal
    python3 tools/sab_qa.py --final            # เฟส 5: data-pending ห้ามเหลือ
    python3 tools/sab_qa.py --selftest         # ใส่ข้อผิดจงใจในบทหุ่น ต้องจับได้ครบ และกรณียกเว้นต้องไม่ถูกฟ้อง

เล่ม 2 (--book sab2 หรือ SAB_BOOK=sab2 · หน้า docs/sab2-partN.html บท 1–17 · ค่าตั้งของเล่มอยู่ใน sab_book.BOOKS)
  ทุกบทต้องเป็น v2 · บทแรก (บท 1) ไม่มี data-continues · ไม่มีหน้าพื้นฐาน/ทางด่วน/.dist/.other บังคับ · details.file ไม่บังคับ .sheet
  W12 ห้ามเฉพาะ Π κ τ E[ C V K G ln (เล่ม 2 สอน log · σ · a, b) · W18 "ส่วนต่าง" → "spread ของคู่" ทุกบท
  W22 ใช้ tools/sab2_terms.json + คำของ tools/sab_terms.json ถือว่าสอนแล้ว (sab_book.load_terms)
  + V9 💻 details.code รันจริง · V10 กล่อง .fails · V11 ปลั๊กอินห้ามแตะช่วงทดสอบสุดท้าย — รายละเอียดใน tools/sab2_qa.py
    python3 tools/sab_qa.py --book sab2 --selftest
"""

import glob
import json
import os
import re
import sys
import tempfile
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402  (เลือกเล่มด้วย SAB_BOOK หรือ --book · ค่าเริ่มต้น sab)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
PREFIX = B.PREFIX
NEXT_VOL = B.BOOK_ID != "sab"                     # เล่ม 2: ทุกบทเป็น v2 · กฎ V9–V11 (tools/sab2_qa.py)
FIG = B.FIG
TERMS = B.TERMS
TERM_CAP = 12
LAST_PART = B.LAST_PART
FIRST_PART = B.FIRST_PART
DIST_REQUIRED = set() if NEXT_VOL else {2, 4, 6, 7, 10, 12, 13, 14, 15, 16, 17}
OTHER_REQUIRED = set() if NEXT_VOL else {1, 2, 5, 7, 9, 12, 17}
FAST = [] if NEXT_VOL else [0, 4, 5, 10, 12, 14, 17]     # ทางด่วน 🟠 (แผน 3.1) · เล่ม 2 ไม่มี
SPREAD_WORD_FROM = 1 if NEXT_VOL else 8           # W18 "ส่วนต่าง" → "spread ของคู่" ตั้งแต่บทนี้ (เล่ม 2: ทุกบท · ตารางศัพท์ Pair Spread)
SHEET_REQUIRED = not NEXT_VOL                     # V1 details.file ต้องมี .sheet (เล่ม 2: แฟ้มเป็นหน้าสมุดวิจัย ไม่บังคับใบงาน)

# ── v2 (แผน 14) ──
TERM_CAP_V2, TERM_CAP_BASE = 7, 4
LAST_BASE = B.LAST_BASE                           # หน้าพื้นฐาน sab-base1..4.html อยู่ก่อนบท 0 (เล่ม 2 ไม่มี → 0)
EX_MIN = {"part": (5, 3), "base": (3, 2)}         # ✍️ (จำนวนข้อขั้นต่ำ, ข้อที่มี details.hint ขั้นต่ำ)
EQ_MAX = 2                                        # V6: "=" ต่อ <p> บรรยาย
RETIRED = [("🔁", r"🔁"), ("⚠️ ค่าเริ่มต้น", r"⚠\s*ค่าเริ่มต้น"), ("🧭 นิสัยคิด", r"🧭\s*นิสัยคิด"),
           ("🧭 เส้นทางอ่าน", r"🧭\s*เส้นทางอ่าน"), ("🟠", r"🟠")]
NQ_RE = re.compile(r"(?<![A-Za-z0-9])nq(?![A-Za-z0-9])")
SRC_KIND = {"sim": "🎲", "real": "📡", "app": "📱"}   # W16 ในหน้า v2: <table data-src="sim|real|app">

VOID = {"br", "hr", "img", "meta", "link", "input", "wbr", "source", "path", "rect",
        "line", "circle", "text", "stop", "marker", "use", "polygon", "polyline",
        "ellipse", "tspan"}

REQUIRED_BOXES = [
    ("🧭 เส้นทางอ่าน", "🧭 เส้นทางอ่าน"),
    ("ประโยคทอง .pq", 'class="pq"'),
    ("📖 ศัพท์ใหม่", "📖 ศัพท์ใหม่ในตอนนี้"),
]
CHAPTER_BOXES = [
    ("📓 ฉากเปิด", 'class="scene-open"'),
    ("🛑 หยุดคิดก่อนพลิก", 'class="stop"'),
    ("⚠️ ค่าเริ่มต้น", "⚠️ ค่าเริ่มต้น"),
    ("🧭 นิสัยคิด", "🧭 นิสัยคิด"),
    ("🧮 📒 บัญชีมิน", "🧮"),
    ("📒 table.ledger", 'class="ledger"'),
    ("🧬 ธรรมชาติของกลยุทธ์", 'class="nature"'),
    ("🔁 ถ้าเปลี่ยนตลาด", "🔁"),
    ("🛠 ใบงาน", "sheet"),
    ("✍️ ลองทำเอง", "✍️ ลองทำเอง"),
    ("🎯 3 อย่างที่ต้องจำ", "🎯 3 อย่าง"),
    ("🔗 อยากลึกกว่านี้", "🔗"),
]
# หนึ่งใน 🧠/🎬 ต้องมี
ONE_OF = [("🧠 .qv หรือ 🎬 .scene", ['class="qv"', 'class="scene"'])]

FORBIDDEN_SYMBOLS = ["Π", "κ", "τ", "σ", "Σ", "E["]
FORBIDDEN_LATIN = ["b", "C", "V", "K", "d", "G", "ln", "log"]   # ตัวเดี่ยวตามขอบคำ ASCII
if NEXT_VOL:                                      # เล่ม 2 สอน log ราคา · การถดถอย (a, b) · σ ในบท 1–4 → ห้ามเฉพาะที่ยังไม่สอน
    FORBIDDEN_SYMBOLS = ["Π", "κ", "τ", "E["]
    FORBIDDEN_LATIN = ["C", "V", "G", "ln"]        # K สอนในบท 6 (Kalman Gain) จึงไม่ห้ามในเล่ม 2
SOURCE_TAGS = ("🔢", "🎲", "📡", "📱")


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"ปิด </{tag}> เกินมาที่บรรทัด {self.getpos()[0]}")
            return
        top = self.stack.pop()
        if top[0] != tag:
            self.errors.append(f"คาด </{top[0]}> (เปิดบรรทัด {top[1][0]}) แต่เจอ </{tag}> บรรทัด {self.getpos()[0]}")


TAG_RE = re.compile(r"<(/?)(div|details|section|table|ol|ul|p|span|aside|figure|svg)\b([^>]*)>", re.I)


def blocks(html, pred):
    """คืน [(start, end, attrs)] ของ element ที่ pred(tag, attrs) เป็นจริง (จับคู่แท็กชนิดเดียวกันแบบนับชั้น)"""
    out, opens = [], []
    for m in TAG_RE.finditer(html):
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if not closing:
            opens.append((tag, m.start(), attrs))
        else:
            for i in range(len(opens) - 1, -1, -1):
                if opens[i][0] == tag:
                    t, s, a = opens.pop(i)
                    del opens[i:]
                    if pred(t, a):
                        out.append((s, m.end(), a))
                    break
    return sorted(out)


def has_class(attrs, cls):
    m = re.search(r'class="([^"]*)"', attrs)
    return bool(m) and cls in m.group(1).split()


def cut(html, spans):
    keep, last = [], 0
    for s, e, _ in sorted(spans):
        if s >= last:
            keep.append(html[last:s])
            last = e
    keep.append(html[last:])
    return " ".join(keep)


def text_of(html):
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"<(script|style|code|pre)\b.*?</\1>", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    return html.replace("&nbsp;", " ")


def box_spans(html, emoji_title):
    """กล่อง .bx ที่หัว .bt ขึ้นต้นด้วยข้อความนี้"""
    return [b for b in blocks(html, lambda t, a: t == "div" and has_class(a, "bx"))
            if re.match(r'\s*<div class="bt">\s*' + re.escape(emoji_title), html[b[0]:b[1]][html[b[0]:b[1]].index(">") + 1:])]


def is_fold(t, a):
    """บล็อกพับที่พ้นกฎเส้นทางหลัก (🔎 details.deep · details.ans · details.hint) — ไม่รวม details.file ของหน้า v2
    ซึ่งเป็นเพียงที่เก็บใบงาน/บัญชี/บัตรท้ายบท เนื้อในยังต้องผ่าน W12 · W13 · W22 เหมือนตอนอยู่นอกบล็อก"""
    return t == "details" and not has_class(a, "file")


def main_path(html):
    """ข้อความเส้นทางหลัก: ตัด 🔎 details.deep · details.ans · details.hint · script/style/code · comment"""
    spans = blocks(html, is_fold)
    return text_of(cut(html, spans))


def part_no(name):
    m = re.fullmatch(rf"{PREFIX}-part(\d+)\.html", name)
    return int(m.group(1)) if m else None


def base_no(name):
    m = re.fullmatch(rf"{PREFIX}-base(\d+)\.html", name)
    return int(m.group(1)) if m else None


def is_v2(html):
    """หน้า v2 = แท็ก <body> มี data-tpl="2" (แผน 14.3)"""
    m = re.search(r"<body\b([^>]*)>", html or "")
    return bool(m and re.search(r'\bdata-tpl="2"', m.group(1)))


def teach_order(v):
    """ค่า "สอน" ใน sab_terms.json → ลำดับหน้า: บท N = N · "baseN" = N − 5 (หน้าพื้นฐานมาก่อนบท 0) · อื่น ๆ = None"""
    if isinstance(v, int) and not isinstance(v, bool):
        return v
    m = re.fullmatch(r"base(\d+)", v) if isinstance(v, str) else None
    return int(m.group(1)) - (LAST_BASE + 1) if m else None


def teach_label(v):
    return f"พื้นฐาน {v[4:]}" if isinstance(v, str) else f"บท {v}"


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return None


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


# ───────────────────────── v2: โครง DOM อย่างเบา + ตัวตรวจ V1–V8 ─────────────────────────

class Node:
    __slots__ = ("tag", "attrs", "start", "open_end", "close_start", "end", "parent", "children")

    def __init__(self, tag, attrs, start, open_end, parent):
        self.tag, self.attrs, self.start, self.open_end, self.parent = tag, attrs, start, open_end, parent
        self.close_start = self.end = open_end
        self.children = []

    def has(self, cls):
        return cls in (self.attrs.get("class") or "").split()

    def ancestors(self):
        a = self.parent
        while a is not None and a.tag != "#root":
            yield a
            a = a.parent


class Dom(HTMLParser):
    """element ทุกตัวพร้อมตำแหน่งในไฟล์ (start..end · เนื้อใน open_end..close_start) — ใช้กับกฎที่ต้องรู้ลำดับและการซ้อน"""

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.html = html
        self.line_at = [0] + [m.end() for m in re.finditer("\n", html)]
        self.root = Node("#root", {}, 0, 0, None)
        self.root.close_start = self.root.end = len(html)
        self.stack, self.nodes = [self.root], []
        self.feed(html)
        self.close()
        for n in self.stack[1:]:                       # แท็กที่ไม่ได้ปิด (Balance ฟ้องแยกแล้ว) → ถือว่ายาวถึงท้ายไฟล์
            n.close_start = n.end = len(html)

    def _off(self):
        line, col = self.getpos()
        return self.line_at[line - 1] + col

    def _add(self, tag, attrs):
        s = self._off()
        node = Node(tag, {k: (v or "") for k, v in attrs}, s, s + len(self.get_starttag_text() or ""), self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        return node

    def handle_starttag(self, tag, attrs):
        node = self._add(tag, attrs)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self._add(tag, attrs)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                s = self._off()
                e = self.html.find(">", s) + 1 or len(self.html)
                for n in self.stack[i + 1:]:
                    n.close_start = n.end = s
                self.stack[i].close_start, self.stack[i].end = s, e
                del self.stack[i:]
                return


def _norm(s):
    """ตัดช่องว่างและตัวเลือกรูปอีโมจิ U+FE0F — ใช้เทียบคำขึ้นต้น ("อ่านภาพ:" · "✍️ ลองทำเอง")"""
    return re.sub(r"\s+", "", s.replace("️", ""))


def _quote(s, k=60):
    t = re.sub(r"\s+", " ", s).strip()
    return t[:k] + ("…" if len(t) > k else "")


def audit_v2(html, kind, num):
    """ตรวจกฎ V1–V8 ของแม่แบบ v2 (แผน 14.3) กับ html หนึ่งหน้า — ไม่ดูป้าย data-tpl จึงใช้กับหน้า v1 แบบรายงานอย่างเดียวได้
    (tools/sab_migrate_v2.py) · kind = "part" | "base" · num = เลขบท/เลขหน้าพื้นฐาน
    คืน {"problems": [ข้อความขึ้นต้นด้วยรหัสกฎ], "stats": {…ตัวนับสำหรับรายงาน}}"""
    dom = Dom(html)
    N = dom.nodes
    P, S = [], {}

    def txt(n):
        return text_of(html[n.open_end:n.close_start])

    def line(pos):
        return html.count("\n", 0, pos) + 1

    def in_details(n):
        return any(a.tag == "details" for a in n.ancestors())

    def within(n, outer):
        return outer.start < n.start < outer.end

    top = [n for n in N if not in_details(n)]

    def first(pred, pool=top):
        return next((n for n in pool if pred(n)), None)

    pos = first(lambda n: n.has("pos"))
    scene = first(lambda n: n.has("scene-open"))
    cq = first(lambda n: n.has("pq") and "data-hook" not in n.attrs)
    stops = [n for n in N if n.has("stop")]
    sum3 = first(lambda n: n.has("sum3"))
    ex_bt = first(lambda n: n.has("bt") and _norm(txt(n)).startswith("✍ลองทำเอง"))
    hooks = [n for n in top if n.has("pq") and "data-hook" in n.attrs]
    tb_bt = first(lambda n: n.has("bt") and _norm(txt(n)).startswith("📖ศัพท์ใหม่ในตอนนี้"))
    files = [n for n in N if n.tag == "details" and n.has("file")]
    file_sheets = [n for n in N if n.has("sheet") and any(a.tag == "details" and a.has("file") for a in n.ancestors())]

    # V1 โครงบังคับ
    miss = [label for ok, label in (
        (pos, ".pos (แถบตำแหน่ง)"), (scene, ".scene-open (ฉากเปิด)"), (cq, ".pq คำถามของบท (ไม่มี data-hook)"),
        (stops, "🛑 .stop"), (sum3, ".sum3 (สรุป 3 ข้อ)"), (ex_bt, "✍️ ลองทำเอง"),
        (hooks or kind != "part" or num == LAST_PART, ".pq[data-hook] สะพานไปบทถัดไป"),
        (tb_bt, "📖 ศัพท์ใหม่ในตอนนี้")) if not ok]
    P += [f"V1 ขาด {m}" for m in miss]
    if kind == "part" and len(files) != 1:
        P.append(f"V1 ต้องมี details.file (📁 แฟ้มของบทนี้) หนึ่งบล็อกพอดี (พบ {len(files)})")
    elif kind == "part" and not file_sheets and SHEET_REQUIRED:
        P.append("V1 details.file ต้องมี .sheet อย่างน้อยหนึ่งใบ")
    elif len(files) > 1:
        P.append(f"V1 details.file มีได้ไม่เกินหนึ่งบล็อก (พบ {len(files)})")
    S["ขาด"], S["แฟ้ม"], S["ใบงานในแฟ้ม"] = miss, len(files), len(file_sheets)

    # V2 ทุก <h2> ตอนสอน (ระหว่างคำถามของบทกับ .sum3) มี .rest ก่อนหัวข้อถัดไป
    h2s = [n for n in top if n.tag == "h2"]
    if sum3:
        teach_end = sum3.start
    else:                                              # หน้าที่ยังไม่มี .sum3 (รายงานหน้า v1): หยุดที่อุปกรณ์ท้ายบทตัวแรก
        tail_marks = [n.start for n in top if n is ex_bt or n.has("nature") or n.has("sheet") or n.has("ledger")
                      or (n.tag == "h2" and _norm(txt(n)).startswith("🧮"))]
        teach_end = min(tail_marks, default=len(html))
    teach_start = cq.end if cq else (scene.end if scene else 0)
    teach = [h for h in h2s if teach_start <= h.start < teach_end]
    rests = [n for n in top if n.has("rest")]
    no_rest = []
    for i, h in enumerate(teach):
        nxt = teach[i + 1].start if i + 1 < len(teach) else teach_end
        if not any(h.end <= r.start < nxt for r in rests):
            no_rest.append(h)
    if not teach:
        P.append("V2 ไม่มี <h2> ตอนสอนระหว่างคำถามของบทกับ .sum3")
    P += [f'V2 ตอน «{_quote(txt(h), 40)}» (บรรทัด {line(h.start)}) ไม่มี .rest "พักตรงนี้ได้" ก่อนหัวข้อถัดไป' for h in no_rest]
    S["ตอน"], S["ตอนไม่มีrest"] = len(teach), [(line(h.start), _quote(txt(h), 50)) for h in no_rest]

    # V3 ทุก .figw มี .readfig "อ่านภาพ:" ตามหลัง (ก่อน .figw ถัดไป · <h2> ถัดไป · ท้ายบล็อกพับที่ครอบ · ท้ายหน้า)
    figs = [n for n in N if n.has("figw")]
    readfigs = [n for n in N if n.has("readfig")]
    all_h2 = [n for n in N if n.tag == "h2"]
    no_fig = []
    for f in figs:
        bounds = [g.start for g in figs if g.start > f.start] + [h.start for h in all_h2 if h.start > f.start]
        bounds += [a.close_start for a in f.ancestors() if a.tag == "details"]
        cand = [r for r in readfigs if f.end <= r.start < min(bounds, default=len(html))]
        key = re.search(r"<!--CHART:([^>]+?)-->\s*$", html[:f.start])
        label = f"กราฟ {key.group(1)}" if key else "กราฟ .figw"
        if not cand:
            no_fig.append((line(f.start), label))
            P.append(f'V3 {label} (บรรทัด {line(f.start)}) ไม่มี .readfig "อ่านภาพ:" ตามหลัง')
        elif not _norm(txt(cand[0])).startswith("อ่านภาพ:"):
            P.append(f'V3 .readfig ของ{label} (บรรทัด {line(cand[0].start)}) ต้องขึ้นต้นด้วย "อ่านภาพ:"')
    S["กราฟ"], S["กราฟไม่มีreadfig"] = len(figs), no_fig

    # V4 ทุก .fm นอก details มี .readeq "อ่านสมการ:" ตามหลังในตอนเดียวกัน (ก่อน <h2> ถัดไป/.sum3)
    fms = [n for n in top if n.has("fm")]
    readeqs = [n for n in top if n.has("readeq")]
    no_eq = []
    for f in fms:
        bounds = [h.start for h in h2s if h.start > f.start] + ([sum3.start] if sum3 and sum3.start > f.start else [])
        cand = [r for r in readeqs if f.end <= r.start < min(bounds, default=len(html))]
        if not cand:
            no_eq.append((line(f.start), _quote(txt(f), 50)))
            P.append(f'V4 สูตร «{_quote(txt(f), 40)}» (บรรทัด {line(f.start)}) ไม่มี .readeq "อ่านสมการ:" ตามหลังในตอนเดียวกัน')
        elif not _norm(txt(cand[0])).startswith("อ่านสมการ:"):
            P.append(f'V4 .readeq (บรรทัด {line(cand[0].start)}) ต้องขึ้นต้นด้วย "อ่านสมการ:"')
    S["สูตร"], S["สูตรไม่มีreadeq"] = len(fms), no_eq

    # V5 ✍️: <li> ระดับบนของ <ol> แรกหลังหัว ✍️ (ข้อตกลงเดียวกับ sab_drills.py) · ทุกข้อมี details.ans · มี details.hint ตามเกณฑ์
    need, need_hint = EX_MIN[kind]
    items, no_ans, hinted = [], [], 0
    if ex_bt:
        ol = next((n for n in N if n.tag == "ol" and n.start > ex_bt.start), None)
        items = [c for c in ol.children if c.tag == "li"] if ol else []

        def has_fold(li, cls):
            return any(d.tag == "details" and d.has(cls) and within(d, li) for d in N)
        no_ans = [i + 1 for i, li in enumerate(items) if not has_fold(li, "ans")]
        hinted = sum(1 for li in items if has_fold(li, "hint"))
        if len(items) < need:
            P.append(f"V5 ✍️ มี {len(items)} ข้อ (ต้อง ≥ {need})")
        P += [f"V5 ✍️ ข้อ {i} ไม่มี details.ans" for i in no_ans]
        if hinted < need_hint:
            P.append(f"V5 ✍️ มีคำใบ้ details.hint {hinted} ข้อ (ต้อง ≥ {need_hint})")
    S["แบบฝึก"] = {"ข้อ": len(items), "ต้อง": need, "ไม่มีเฉลย": no_ans, "มีคำใบ้": hinted, "ต้องมีคำใบ้": need_hint}

    # V6 เส้นทางหลัก (นอก details · ตาราง · .fm · .readeq · .sheet): <p> หนึ่งย่อหน้ามี "=" ไม่เกิน EQ_MAX
    def off_path(n):
        return n.tag in ("details", "table") or n.has("fm") or n.has("readeq") or n.has("sheet")
    many_eq = []
    for p in N:
        if p.tag != "p" or off_path(p) or any(off_path(a) for a in p.ancestors()):
            continue
        t = txt(p)
        if t.count("=") > EQ_MAX:
            many_eq.append((line(p.start), t.count("="), _quote(t)))
            P.append(f'V6 ย่อหน้าบรรทัด {line(p.start)} มี "=" {t.count("=")} ตัว (เกิน {EQ_MAX}): «{_quote(t)}»')
    S["ย่อหน้าเกิน="] = many_eq

    # V7 กล่อง 📖: นับ <li> ระดับบนของกล่อง · รูปแบบ <strong>English (ไทย)</strong> = …
    cap = TERM_CAP_V2 if kind == "part" else TERM_CAP_BASE
    n_terms = 0
    if tb_bt:
        box = tb_bt.parent
        if box.tag == "#root":
            P.append("V7 หัว 📖 ต้องเป็น .bt ที่อยู่ในกล่อง .bx")
        else:
            lis = [n for n in N if n.tag == "li" and within(n, box)
                   and not any(a.tag == "li" and within(a, box) for a in n.ancestors())]
            n_terms = len(lis)
            if n_terms > cap:
                P.append(f"V7 ศัพท์ใหม่ {n_terms} คำ เกินเพดาน {cap}")
            for li in lis:
                inner = html[li.open_end:li.close_start]
                if "data-tier" in li.attrs or re.match(r"\s*<strong\b[^>]*data-tier", inner):
                    P.append("W9 data-tier ต้องอยู่ที่ <span class=\"tier\"> ไม่ใช่ <li>/<strong>")
                elif not re.match(r"\s*<strong\b[^>]*>.*?</strong>\s*=", inner, re.S):
                    P.append(f"V7 รายการศัพท์ «{_quote(text_of(inner), 30)}» ต้องเป็นรูป <strong>English (ไทย)</strong> = ความหมาย")
    S["ศัพท์"], S["เพดานศัพท์"] = n_terms, cap

    # V8 ป้าย/คำที่เลิกใช้: ป้ายห้ามทั้งหน้า · "nq" ห้ามในเส้นทางหลัก (นอก details ทุกชนิด · นับ href และ <code> ด้วย)
    bare = re.sub(r"<(script|style)\b.*?</\1>", " ", re.sub(r"<!--.*?-->", " ", html, flags=re.S), flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", bare).replace("️", "")
    retired = [label for label, pat in RETIRED if re.search(pat, vis)]
    P += [f"V8 ป้ายที่เลิกใช้ในหน้า v2: {label}" for label in retired]
    nq = NQ_RE.search(cut(bare, blocks(bare, lambda t, a: t == "details")))
    if nq:
        retired.append('"nq" ในเส้นทางหลัก')
        P.append('V8 คำ "nq" (หรือลิงก์ nq-*.html) ในเส้นทางหลัก — การชี้ไปเล่ม nq อยู่ได้เฉพาะในบล็อกพับ/ภาคผนวก A')
    S["เลิกใช้"] = retired
    return {"problems": P, "stats": S}


def check_file(name, html, ctx):
    P = []
    n, b = part_no(name), base_no(name)
    kind = "part" if n is not None else ("base" if b is not None else None)
    v2 = kind is not None and (is_v2(html) or kind == "base" or NEXT_VOL)   # หน้า v1 (บทที่ยังไม่ย้าย) ใช้กฎเดิมทุกข้อ
    pages, fig, terms, opts = ctx["pages"], ctx["fig"], ctx["terms"], ctx["opts"]
    if kind == "base" and not is_v2(html):
        P.append(f"{name}: หน้าพื้นฐานต้องเป็นแม่แบบ v2 — ใส่ <body data-tpl=\"2\">")
    if kind == "part" and NEXT_VOL and not is_v2(html):
        P.append(f"{name}: บทเล่ม {B.VOL} ต้องเป็นแม่แบบ v2 — ใส่ <body data-tpl=\"2\">")

    # โครงสร้าง
    parser = Balance()
    parser.feed(html)
    P += [f"{name}: {e}" for e in parser.errors]
    P += [f"{name}: <{t}> เปิดบรรทัด {pos[0]} แล้วไม่ได้ปิด" for t, pos in parser.stack]
    body = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S)
    for m in re.finditer(r"<br\s*/?>\s*(?:•|·\s|\d+\.\s|-\s)", body):
        P.append(f"{name}: W11 <br> จำลองรายการ ควรใช้ <ul>/<ol> (ตำแหน่ง {m.start()})")
    if "data-thwbr" not in html:
        P.append(f"{name}: ไม่มี Thai line-break script")

    # W8 ลิงก์ภายใน (+ <code>ไฟล์</code> + .csv/.xlsx) · ไฟล์ในกล่อง data-pending ยอมได้เมื่อ --pending
    pend_spans = blocks(html, lambda t, a: "data-pending" in a and "data-pending-part" not in a)
    pend_text = "".join(html[s:e] for s, e, _ in pend_spans)
    refs = set(re.findall(r'href="([^"#:?]+\.(?:html|csv|xlsx|pdf))', html))
    refs |= set(re.findall(r"<code>([\w./-]+\.(?:html|csv|xlsx))</code>", html))
    for ref in sorted(refs):
        path = os.path.normpath(os.path.join(DOCS, ref))
        if not os.path.exists(path) and os.path.basename(ref) not in pages:
            if opts["pending"] and ref in pend_text:
                ctx["warnings"].append(f"{name}: (รอ) ลิงก์ {ref} ยังไม่มีไฟล์")
            else:
                P.append(f"{name}: W8 ลิงก์ไป {ref} ซึ่งไม่มีไฟล์อยู่จริง")

    # W14 anchor
    for ref, anc in set(re.findall(r'href="([^"#:]*)#([^"]+)"', html)):
        target = html if not ref else pages.get(ref)
        if ref and not target and os.path.exists(os.path.join(DOCS, ref)):   # หน้าคลังที่ไม่ใช่ sab-: อ่านจริง
            with open(os.path.join(DOCS, ref), encoding="utf-8") as fh:
                target = fh.read()
        if target is not None and not re.search(r'\bid="' + re.escape(anc) + '"', target):
            P.append(f"{name}: W14 ลิงก์ไป {ref or name}#{anc} แต่ไม่มี id นี้")

    # W18 คำต้องห้าม (ทั้งหน้า ยกเว้นโค้ด)
    vis = text_of(html)
    for w in ("เล่มเดิม", "Quant for Non-Quant"):
        if w in vis:
            P.append(f"{name}: W18 คำต้องห้าม {w!r}")
    for m in re.finditer(r"ทุก\s*8\s*ชั่วโมง", vis):
        if "ในตัวอย่าง" not in vis[max(0, m.start() - 80):m.end() + 80]:
            P.append(f"{name}: W18 'ทุก 8 ชั่วโมง' ต้องบอกว่าเป็นค่าในตัวอย่าง")
    allow = text_of(cut(html, [b for b in blocks(html, lambda t, a: True) if "data-allow" not in b[2]]))
    vis_no_allow = text_of(cut(html, blocks(html, lambda t, a: "data-allow" in a)))
    if "ถอยสู่ค่าเฉลี่ย" in vis_no_allow:
        P.append(f"{name}: W18 'ถอยสู่ค่าเฉลี่ย' นอกกล่อง data-allow (ใช้ 'กลับค่ากลาง')")
    del allow
    if n is not None and n >= SPREAD_WORD_FROM:                    # แผน 7.3: spread ของคู่ ห้ามเรียก "ส่วนต่าง"
        mp8 = main_path(html)
        for m in re.finditer(r"ส่วนต่าง(?!ราคาซื้อ-ขาย|ราคาซื้อขาย)", mp8):
            # ยกเว้นคำแปลในวงเล็บต่อท้ายศัพท์อังกฤษ (กฎ CLAUDE.md) เช่น Basis (ส่วนต่างราคา futures กับ spot)
            lp = mp8.rfind("(", 0, m.start())
            if lp >= 0 and ")" not in mp8[lp:m.start()] and re.search(r"[A-Za-z)]\s*$", mp8[max(0, lp - 40):lp]):
                continue
            P.append(f"{name}: W18 'ส่วนต่าง' ในภาค 2–3 — ใช้ 'spread ของคู่' (ยกเว้น ส่วนต่างราคาซื้อ-ขาย)")
            break
    for m in re.finditer(r"ไม่มีความเสี่ยง", vis):
        before = vis[max(0, m.start() - 2):m.start()]
        if not re.search(r"[\"“'‘]", before):
            P.append(f"{name}: W18 'ไม่มีความเสี่ยง' นอกเครื่องหมายคำพูด")

    # W12/W13 เส้นทางหลัก
    mp = main_path(html)
    mp_clean = re.sub(r"ภาคผนวก\s+[A-K]\b", " ", mp)          # J · K = ภาคผนวกของแผน 14.5
    mp_clean = re.sub(r"[\w.-]+\.(?:csv|xlsx|html|py)", " ", mp_clean)
    for sym in FORBIDDEN_SYMBOLS:
        if sym in mp_clean:
            P.append(f"{name}: W12 สัญลักษณ์ {sym!r} นอก 🔎")
    for sym in FORBIDDEN_LATIN:
        if re.search(r"(?<![A-Za-z0-9_\-])" + re.escape(sym) + r"(?![A-Za-z0-9_\-])", mp_clean):
            P.append(f"{name}: W12 สัญลักษณ์ {sym!r} นอก 🔎")
    for m in (re.finditer(r"(?<![\d.])\d+\.\d{3,}(?![\d])(?!\s*BTC)", mp) if kind is not None else []):   # W13 เฉพาะบท (หน้าเฉลยรวมคำตอบที่อยู่ใน details ของบท)     # ปริมาณเหรียญ เช่น 0.015 BTC ยกเว้น
        P.append(f"{name}: W13 ทศนิยมเกิน 2 ตำแหน่ง {m.group(0)} นอก 🔎")

    # W16 ป้ายที่มา + table.fees
    for s, e, a in blocks(html, lambda t, a: t in ("table", "svg")):
        if has_class(a, "ledger") or has_class(a, "ncard") or "data-nosrc" in a:
            continue
        window = html[max(0, s - 300):min(len(html), e + 400)]
        if v2 and html.startswith("<table", s):            # แผน 14.3: ตารางสอนธรรมดาไม่ต้องติดป้าย · ติดเมื่อเป็นผลจำลอง/ข้อมูลจริง/ค่าจากแอป
            src = re.search(r'data-src="([^"]*)"', a)
            if src and src.group(1) not in SRC_KIND:
                P.append(f"{name}: W16 ตารางที่ตำแหน่ง {s}: data-src ต้องเป็น sim | real | app (พบ {src.group(1)!r})")
            elif src and SRC_KIND[src.group(1)] not in window:
                P.append(f"{name}: W16 ตาราง data-src=\"{src.group(1)}\" ที่ตำแหน่ง {s} ไม่มีป้าย {SRC_KIND[src.group(1)]} ใกล้ตาราง")
            continue
        if not any(t in window for t in SOURCE_TAGS):
            P.append(f"{name}: W16 ตาราง/กราฟที่ตำแหน่ง {s} ไม่มีป้ายที่มา 🔢/🎲/📡/📱")
    for s, e, a in blocks(html, lambda t, a: t == "table" and has_class(a, "fees")):
        first = text_of(html[s:e]).strip()[:200]
        if not ("maker" in first and "taker" in first):
            P.append(f"{name}: W16 table.fees ต้องประกาศ maker/taker บรรทัดแรก")

    # W21
    if "math-part9.html" in html and not re.search(r"\bh\b.{0,80}β|β.{0,80}\bh\b", vis, re.S):
        P.append(f"{name}: W21 ชี้ math-part9.html ต้องมีหมายเหตุ h/β")

    # W25
    claims = {c.get("id") for c in (fig or {}).get("_claims", []) if isinstance(c, dict)}
    for s, e, a in blocks(html, lambda t, a: has_class(a, "other")):
        m = re.search(r'data-claim="([^"]+)"', a)
        if not m:
            P.append(f"{name}: W25 กล่อง .other ไม่มี data-claim")
        elif fig is not None and m.group(1) not in claims:
            P.append(f"{name}: W25 data-claim {m.group(1)!r} ไม่มีใน _claims")

    # W19 ใบงาน
    sheets = blocks(html, lambda t, a: t == "div" and has_class(a, "sheet"))
    for s, e, a in sheets:
        seg = html[s:e]
        sid = (re.search(r'data-sheet="([^"]+)"', a) or [None, "?"])[1]
        pas = re.search(r'<ol class="pass">(.*?)</ol>', seg, re.S)
        if not pas or len(re.findall(r"<li\b", pas.group(1))) != 3:
            P.append(f"{name}: W19 ใบ {sid} ต้องมี <ol class=\"pass\"> 3 ข้อ")
        elif '<p class="pass-h">' not in seg[max(0, pas.start() - 120):pas.start()]:
            P.append(f"{name}: W19 ใบ {sid} ต้องมีหัว <p class=\"pass-h\"><strong>✅ เกณฑ์ผ่าน 3 ข้อ</strong></p> ก่อน ol.pass")
        if 'data-field="ใครจ่าย"' not in seg:
            P.append(f"{name}: W19 ใบ {sid} ไม่มีช่อง ใครจ่าย")
        if "📱" not in seg or "ถ้าแอปไม่มีค่านี้" not in seg:
            P.append(f"{name}: W19 ใบ {sid} ต้องมี 📱 และทาง 'ถ้าแอปไม่มีค่านี้'")
        if "ถ้าเปลี่ยนตลาด" not in seg:
            P.append(f"{name}: W19 ใบ {sid} ไม่มีแถว 'ถ้าเปลี่ยนตลาด'")
        if "data-key=" not in seg:
            P.append(f"{name}: W19 ใบ {sid} ไม่มีค่าของมิน (data-key) — ใบมินต้องมาก่อนใบเปล่า")
        for k in re.findall(r'data-key="([^"]+)"', seg):
            if fig is not None:
                try:
                    get_path(fig, k)
                except KeyError:
                    P.append(f"{name}: W19 ใบ {sid} data-key {k!r} ไม่มีใน JSON")

    # W20 บัตรธรรมชาติ
    for s, e, a in blocks(html, lambda t, a: t == "table" and has_class(a, "ncard")):
        for td in re.finditer(r"<td\b([^>]*)>(.*?)</td>", html[s:e], re.S):
            attrs, inner = td.group(1), text_of(td.group(2)).strip()
            pm = re.search(r'data-pending-part="(\d+)"', attrs)
            if pm:
                if n is not None and int(pm.group(1)) <= n:
                    P.append(f"{name}: W20 ช่องเทา data-pending-part={pm.group(1)} ต้องมากกว่าบทนี้ ({n})")
            elif inner and "data-key" not in attrs and "data-label" not in attrs:
                P.append(f"{name}: W20 ช่องบัตรที่เติม {inner[:20]!r} ไม่มี data-key")

    # D1
    if opts["final"] and re.search(r"\sdata-pending(?!-part)(?=[\s=>])", re.sub(r"<style\b.*?</style>", "", html, flags=re.S)):
        P.append(f"{name}: D1 ยังมี data-pending เหลือ")

    if kind is None:
        return P
    here = n if kind == "part" else b - (LAST_BASE + 1)             # ลำดับหน้า: base1..4 = −4..−1 · บท N = N

    # ===== กฎเฉพาะบท / หน้าพื้นฐาน =====
    if v2:                                                          # แม่แบบ v2: V1–V8 แทนกล่องบังคับเดิม · W9 · W24
        P += [f"{name}: {m}" for m in audit_v2(html, kind, n if kind == "part" else b)["problems"]]
    else:
        for label, needle in REQUIRED_BOXES:
            if needle not in html and not (label.startswith("ประโยคทอง") and n == LAST_PART and 'class="pq' in html):
                P.append(f"{name}: ขาด {label}")
        for label, needle in CHAPTER_BOXES:
            if needle not in html:
                P.append(f"{name}: ขาดกล่อง {label}")
        for label, needles in ONE_OF:
            if not any(x in html for x in needles):
                P.append(f"{name}: ต้องมี {label}")
    if NEXT_VOL and kind == "part":                                 # เล่ม 2: V9 💻 รันจริง · V10 กล่อง .fails
        import sab2_qa
        P += sab2_qa.check_code(name, html, part=n)
        P += sab2_qa.check_fails(name, html, blocks, has_class, text_of)
    has_dist = bool(blocks(html, lambda t, a: has_class(a, "dist"))) if v2 else 'class="dist"' in html
    if kind == "part" and n in DIST_REQUIRED and not has_dist:
        P.append(f"{name}: W23 บท {n} ต้องมี .dist")
    if kind == "part" and n in OTHER_REQUIRED and not blocks(html, lambda t, a: has_class(a, "other")):
        P.append(f"{name}: บท {n} ต้องมี 👥 .other")
    if not v2 and (sheets or re.search(r'href="sab-tool-', html)) and 'class="whyline"' not in html:
        P.append(f"{name}: W24 มีใบงาน/เครื่องมือแต่ไม่มี .whyline")

    # W9 เพดานศัพท์ (นับจากกล่อง 📖 แบบเดียวกับ glossary) — หน้า v2 ใช้ V7
    box = None if v2 else re.search(r"📖 ศัพท์ใหม่ในตอนนี้</div>(.*?)</div>\s*(?:<!--|$)", html, re.S)
    if box:
        got = re.findall(r"<li><strong>(.*?)</strong>\s*=", box.group(1))
        if len(got) > TERM_CAP:
            P.append(f"{name}: W9 ศัพท์ใหม่ {len(got)} คำ เกินเพดาน {TERM_CAP}")
        for li in re.findall(r"<li\b[^>]*>.*?</li>", box.group(1), re.S):
            if re.search(r"<(li|strong)\b[^>]*data-tier", li):
                P.append(f"{name}: W9 data-tier ต้องอยู่ที่ <span class=\"tier\"> ไม่ใช่ <li>/<strong>")

    # W15 ความต่อเนื่อง — โซ่ base1 → … → base4 → บท 0 → … → บท 18 · บทข้างเคียงเป็น v1 หรือ v2 ก็ได้ (อ่าน .scene-open เหมือนกัน)
    so = blocks(html, lambda t, a: has_class(a, "scene-open"))
    if so and kind == "part":
        a = so[0][2]
        cont = re.search(r'data-continues="([^"]+)"', a)
        if n == FIRST_PART and cont and not (v2 and LAST_BASE and cont.group(1) == f"base{LAST_BASE}"):   # v2: ต่อจากหน้าพื้นฐานสุดท้ายได้
            P.append(f"{name}: W15 บท {FIRST_PART} ต้องไม่มี data-continues" + (f" (หรือ data-continues=\"base{LAST_BASE}\")" if v2 and LAST_BASE else ""))
        if n > FIRST_PART and (not cont or cont.group(1) != f"part{n - 1}"):
            P.append(f"{name}: W15 ฉากเปิดต้องมี data-continues=\"part{n - 1}\"")
    if kind == "base" or n < LAST_PART:
        if v2:                                                      # .pq[data-hook] ตามคลาส (ลำดับ attribute ใดก็ได้)
            hooks = [re.search(r'data-hook="([^"]+)"', a).group(1)
                     for _, _, a in blocks(html, lambda t, a: has_class(a, "pq") and re.search(r'data-hook="[^"]+"', a))]
        else:
            hooks = re.findall(r'class="pq"[^>]*data-hook="([^"]+)"|data-hook="([^"]+)"[^>]*class="pq"', html)
            hooks = [x or y for x, y in hooks]
        if not hooks and not v2:                                    # หน้า v2: V1 ฟ้องแล้ว (หน้าพื้นฐานไม่บังคับสะพาน)
            P.append(f"{name}: W15 ไม่มี .pq สะพานที่มี data-hook")
        if kind == "base":
            nxt_name, nxt_label = ((f"{PREFIX}-base{b + 1}.html", f"หน้าพื้นฐาน {b + 1}") if b < LAST_BASE
                                   else (f"{PREFIX}-part{FIRST_PART}.html", f"บท {FIRST_PART}"))
        else:
            nxt_name, nxt_label = f"{PREFIX}-part{n + 1}.html", f"บท {n + 1}"
        nxt = pages.get(nxt_name)
        if nxt is not None and hooks:
            ns = blocks(nxt, lambda t, a: has_class(a, "scene-open"))
            scene = text_of(nxt[ns[0][0]:ns[0][1]]) if ns else ""
            for h in hooks:
                if h not in scene:
                    P.append(f"{name}: W15 data-hook {h!r} ไม่ปรากฏในฉากเปิดของ{nxt_label}")

    # W22 ห้ามใช้ก่อนสอน
    if terms:
        exempt = blocks(html, lambda t, a: is_fold(t, a) or (has_class(a, "pq") and "data-hook" in a)
                        or (t == "table" and has_class(a, "ncard")))      # หัวช่องบัตร 8 ช่องเป็นแม่แบบคงที่
        exempt += box_spans(html, "🧭 เส้นทางอ่าน") + box_spans(html, "🔗") + box_spans(html, "📖")
        txt = text_of(cut(html, exempt))
        for term, info in terms.items():
            if term.startswith("_"):
                continue
            taught = teach_order(info.get("สอน"))                   # บท N หรือ "baseN" (หน้าพื้นฐาน มาก่อนบท 0)
            if taught is None or here >= taught:
                continue
            for form in [term] + info.get("รูปแบบ", []):
                pat = (r"(?<![A-Za-z])" + re.escape(form) + r"(?![A-Za-z])") if form.isascii() else re.escape(form)
                if re.search(pat, txt):
                    P.append(f"{name}: W22 ใช้ {form!r} ก่อนสอน (สอนใน{teach_label(info.get('สอน'))})")
                    break
        # W22 ทางด่วน: บทในทางด่วนใช้คำจากบทที่ทางด่วนข้าม → ต้องนิยามในกล่อง 🟠 ของบทนี้หรือบททางด่วนก่อนหน้า
        # เลิกตรวจในหน้า v2 (กล่อง 🟠 เลิกใช้ · แผน 14.6) และในบท v1 ที่บททางด่วนก่อนหน้าย้ายเป็น v2 แล้ว (โซ่กล่อง 🟠 ขาด)
        if kind == "part" and not v2 and n in FAST and not any(
                is_v2(pages.get(f"{PREFIX}-part{k}.html")) for k in FAST if k < n):
            fast_txt = ""
            for k in [k for k in FAST if k <= n]:
                pg = html if k == n else pages.get(f"{PREFIX}-part{k}.html")
                if pg:
                    fast_txt += " ".join(text_of(pg[s0:e0]) for s0, e0, _ in
                                         blocks(pg, lambda t, a: 'data-path="fast"' in a))
            body_txt = text_of(cut(html, exempt + blocks(html, lambda t, a: 'data-path="fast"' in a)))
            for term, info in terms.items():
                taught = teach_order(info.get("สอน")) if not term.startswith("_") else None
                if taught is None or taught < 0 or taught >= n or taught in FAST:      # < 0 = สอนในหน้าพื้นฐาน (ทางด่วนไม่ข้าม)
                    continue
                forms = [term] + info.get("รูปแบบ", [])
                used = next((f for f in forms if re.search(
                    (r"(?<![A-Za-z])" + re.escape(f) + r"(?![A-Za-z])") if f.isascii() else re.escape(f), body_txt)), None)
                if used and not any(f in fast_txt for f in forms):
                    P.append(f"{name}: W22 ทางด่วน ใช้ {used!r} (สอนบท {taught} ที่ทางด่วนข้าม) แต่ไม่มีในกล่อง 🟠")
    return P


def run(docs_dir, fig_path, terms_path, scope=None, pending=False, final=False, quiet=False):
    def order(p):                                                   # หน้าพื้นฐาน → บท (เรียงตามเลข) → หน้าอื่น
        name = os.path.basename(p)
        b, n = base_no(name), part_no(name)
        return (0, b, p) if b is not None else (1, n, p) if n is not None else (2, 0, p)
    files = sorted(glob.glob(os.path.join(docs_dir, f"{PREFIX}-*.html")), key=order)
    pages = {}
    for p in files:
        with open(p, encoding="utf-8") as fh:
            pages[os.path.basename(p)] = fh.read()
    for p in glob.glob(os.path.join(docs_dir, "*")):
        pages.setdefault(os.path.basename(p), None)
    terms = B.load_terms() if os.path.abspath(terms_path) == os.path.abspath(B.TERMS) else load_json(terms_path)
    ctx = {"pages": {k: v for k, v in pages.items() if v is not None}, "fig": load_json(fig_path),
           "terms": terms, "opts": {"pending": pending, "final": final}, "warnings": []}
    for k, v in (terms or {}).items():                              # เล่ม 2: คำที่ลงทะเบียนซ้ำกับเล่มก่อน (ใช้ของเล่มก่อน = สอนแล้ว)
        if not k.startswith("_") and isinstance(v, dict) and "_ซ้ำ" in v:
            ctx["warnings"].append(f"{os.path.basename(terms_path)}: {k!r} สอนแล้วใน{v['สอน']} — ลบออกจากทะเบียนเล่มนี้ได้")
    ctx["pages"].update({k: "" for k, v in pages.items() if v is None})
    targets = [f for f in files if not scope or os.path.basename(f) == f"{PREFIX}-{scope}.html"]
    problems = []
    for p in targets:
        problems += check_file(os.path.basename(p), pages[os.path.basename(p)], ctx)
    if NEXT_VOL and not scope and docs_dir == DOCS:                 # V11 ปลั๊กอินห้ามแตะช่วงทดสอบสุดท้าย (ยกเว้น ch17)
        import sab2_qa
        problems += sab2_qa.check_plugins()
    if not quiet:
        print(f"ตรวจ {len(targets)} ไฟล์" + (f" (ยังไม่มี tools/{PREFIX}_terms.json — ข้าม W22)" if not ctx["terms"] else ""))
        for w in ctx["warnings"]:
            print("  ·", w)
        if problems:
            print(f"พบปัญหา {len(problems)} ข้อ")
            for p in problems:
                print("  -", p)
        else:
            print("ผ่านทุกข้อ ✓")
    if not targets and not quiet:
        print(f"ยังไม่มีไฟล์ docs/{PREFIX}-*.html ให้ตรวจ")
    return (1 if problems else 0), problems


# ───────────────────────── selftest ─────────────────────────

def _chapter(n, extra="", hook="เงินสดอิสระ", cont=True, shell=True):
    cont_attr = f' data-continues="part{n - 1}"' if cont and n > 0 else ""
    sheet = ('<div class="bx sheet" data-sheet="04" data-from="00" data-to="05">'
             '<div class="bt">🛠 ใบ 04 · ใบกันชนเงินสด</div><p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ทุนหมดก่อน</p>'
             '<p>🔢 สมมติเพื่อสอน</p><table class="sheet-tbl"><tr><td data-key="ch04.ต้องโอน">11,220</td>'
             '<td class="blank"></td><td data-field="ใครจ่าย"></td></tr><tr><td>ถ้าเปลี่ยนตลาด</td></tr></table>'
             '<p class="pass-h"><strong>✅ เกณฑ์ผ่าน 3 ข้อ</strong></p><ol class="pass"><li>หนึ่ง</li><li>สอง</li><li>สาม</li></ol>'
             '<p class="app">📱 จดจากแอป · ถ้าแอปไม่มีค่านี้: ใช้ค่าในใบมิน</p></div>')
    body = f'''<div class="bx bb"><div class="bt">🧭 เส้นทางอ่าน</div><p>อ่านต่อจากบทก่อน แนวคิด z จะมาในบท 9</p></div>
<div class="scene-open" data-day="1"{cont_attr}><p>มินเปิดสมุด เงินสดอิสระของเขาเหลือ 14,700</p></div>
<div class="pq">คำถามของบท</div>
<p>ไฟล์ funding-log.csv ใช้ในภาคผนวก C และใบ 02b โดยไม่ใช่สัญลักษณ์</p>
<div class="stop"><div class="bt">🛑 หยุดคิด</div><p>ถ้าเป็นคุณ?</p></div>
<details class="deep" id="deep-1"><summary>🔎 ลงลึก</summary><p>σ และ ln และ 0.12345 อยู่ในนี้ได้</p></details>
<div class="other" data-claim="basis-long-leverage"><div class="bt">👥 คนอีกฝั่ง</div><p>ฝั่ง long</p></div>
<div class="qv"><div class="bt">🧠</div></div>
<div class="dft"><div class="bt">⚠️ ค่าเริ่มต้น</div></div>
<div class="bx bp"><div class="bt">🧭 นิสัยคิด</div></div>
<div class="dist"><p>n = 1</p></div>
<div class="nature"><div class="bt">🧬 ธรรมชาติของกลยุทธ์</div><table class="ncard"><tr><td data-label="1">ใครจ่าย</td>
<td data-key="ch04.ต้องโอน">11,220</td><td data-pending-part="{n + 3}"></td></tr></table></div>
<div class="transfer"><div class="bt">🔁 ถ้าเปลี่ยนตลาด</div></div>
<p>🧮</p><table class="ledger" data-part="{n}"><tr><td data-key="ch04.ต้องโอน">11,220</td></tr></table>
{sheet}
<div class="bx bg"><div class="bt">✍️ ลองทำเอง</div></div><ol><li>ข้อ<details class="ans"><summary>แนวคำตอบ</summary><p>ตอบ</p></details></li></ol>
<div class="bx bg"><div class="bt">🎯 3 อย่างที่ต้องจำ</div></div>
<div class="bx bb"><div class="bt">สรุป</div></div>
<div class="pq" data-hook="{hook}">ปมถัดไป แนวคิด z รออยู่</div>
<div class="bx ba"><div class="bt">🔗 อยากลึกกว่านี้</div><p>z ในบท 9</p></div>
{extra}
<div class="bx bb"><div class="bt">📖 ศัพท์ใหม่ในตอนนี้</div>
<p><strong>3 คำที่ต้องจำก่อน</strong></p><ul><li><strong>กันชน</strong> = เงินสำรอง <span class="tier" data-tier="ก"></span></li></ul></div>
'''
    return body


def selftest():
    with open(os.path.join(ROOT, "tools", "sab_shell", "tail.html"), encoding="utf-8") as fh:
        tail = fh.read()
    with open(os.path.join(ROOT, "tools", "sab_shell", "head.html"), encoding="utf-8") as fh:
        head = fh.read()
    fig = {"ch04": {"ต้องโอน": 11220}, "_claims": [{"id": "basis-long-leverage"}]}
    terms = {"z": {"สอน": 9, "รูปแบบ": ["ค่า z"]}, "กันชน": {"สอน": 4}}
    bad_extra = ('<p>กำไร σ และ log ของราคา 0.12345 และ ln</p><p>ไม่มีความเสี่ยง</p><p>อ่านเล่มเดิม</p>'
                 '<p>จ่ายทุก 8 ชั่วโมง</p><p>ถอยสู่ค่าเฉลี่ย</p><p>ใช้ z ตรงนี้</p>'
                 '<p>a<br>• b</p><a href="sab-tool-zz.html">x</a><a href="#nope">y</a>'
                 '<table><tr><td>ไม่มีป้าย</td></tr></table>'
                 '<table class="fees"><tr><td>ค่าธรรมเนียม</td></tr></table>'
                 '<div class="other"><p>ไม่มี claim</p></div>'
                 '<table class="ncard"><tr><td>ไม่มี key</td><td data-pending-part="1"></td></tr></table>'
                 '<div class="bx sheet" data-sheet="99"><ol class="pass"><li>1</li></ol></div>')
    expect = ["'σ'", "'log'", "0.12345", "'ln'", "ไม่มีความเสี่ยง", "เล่มเดิม", "ทุก 8 ชั่วโมง", "ถอยสู่ค่าเฉลี่ย",
              "W22 ใช้ 'z'", "W11", "sab-tool-zz.html", "#nope", "W16 ตาราง", "table.fees", "W25 กล่อง .other",
              "W20 ช่องบัตรที่เติม", "W20 ช่องเทา", "ใบ 99 ต้องมี", "data-tier ต้องอยู่", "W15 data-hook",
              "W15 ฉากเปิดต้องมี", "W23"]
    with tempfile.TemporaryDirectory() as d:
        fp, tp = os.path.join(d, "f.json"), os.path.join(d, "t.json")
        json.dump(fig, open(fp, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(terms, open(tp, "w", encoding="utf-8"), ensure_ascii=False)
        good4 = head + _chapter(4) + tail
        good5 = head + _chapter(5, hook="ไม่มีในบท6") .replace("มินเปิดสมุด", "มินเปิดสมุด เงินสดอิสระ") + tail
        open(os.path.join(d, "sab-part4.html"), "w", encoding="utf-8").write(good4)
        open(os.path.join(d, "sab-part5.html"), "w", encoding="utf-8").write(good5)
        _, p_good = run(d, fp, tp, scope="part4", quiet=True)
        bad6 = head + _chapter(6, extra=bad_extra, cont=False).replace('class="dist"', 'class="nodist"').replace(
            '<ul><li><strong>กันชน</strong>', '<ul><li data-tier="ข"><strong>คำผิดที่</strong> = x</li><li><strong>กันชน</strong>') + tail
        open(os.path.join(d, "sab-part6.html"), "w", encoding="utf-8").write(bad6)
        _, p_all = run(d, fp, tp, quiet=True)
    ok = True
    if p_good:
        ok = False
        print("selftest ล้ม: บทหุ่นที่ถูกต้องถูกฟ้อง →")
        for p in p_good:
            print("   ", p)
    for e in expect:
        if not any(e in p for p in p_all):
            ok = False
            print(f"selftest ล้ม: ไม่จับข้อผิดจงใจ {e!r}")
    ok2, n2 = _selftest_v2(head, tail, fig)
    ok = ok and ok2
    print("selftest", f"ผ่าน ✓ (จับข้อผิดจงใจครบ {len(expect)} ชนิด · กรณียกเว้น 'ภาคผนวก C' / '02b' / "
          "'funding-log.csv' / .pq ที่เอ่ยแนวคิดบทถัดไป ไม่ถูกฟ้อง · "
          f"v2: จับข้อผิดจงใจครบ {n2} กรณี (V1–V8 · กฎเดิมที่คงไว้ · หน้า base) · บท v2 / หน้า base ที่ถูกต้อง "
          "และบท v1 ที่อยู่ติดบท v2 ไม่ถูกฟ้อง)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


# ───────────────────────── selftest ของแม่แบบ v2 ─────────────────────────

def _v2_parts(kind, n, hook="เงินสดอิสระ", scene="", cont=None):
    """ชิ้นส่วนของหน้า v2 ที่ถูกต้อง (dict เรียงตามลำดับในหน้า) — กรณีผิดจงใจสร้างจากการลบ/แก้ทีละชิ้น"""
    if cont is None:
        cont = f"part{n - 1}" if kind == "part" and n > 0 else (f"base{LAST_BASE}" if kind == "part" else "")
    need, need_hint = EX_MIN[kind]
    hint = ('<details class="hint"><summary>คำใบ้</summary><p>เริ่มจากเงินที่จ่ายออกไปก่อน</p>'
            '<details class="hint"><summary>ยังไม่ออก? คำใบ้ขั้นที่ 2</summary><p>ตัวเลขกลางทางคือ 3</p></details></details>')
    items = "".join(f'<li>ข้อ {i + 1} {hint if i < need_hint else ""}<details class="ans"><summary>เฉลย</summary>'
                    '<p>ตอบ 3 ถ้าได้ 5 แปลว่าพลาดตรงเครื่องหมาย</p></details></li>' for i in range(need))
    sheet = ('<div class="bx sheet" data-sheet="04" data-from="00" data-to="05"><div class="bt">🛠 ใบ 04 · ใบกันชนเงินสด</div>'
             '<table class="sheet-tbl"><tr><td data-key="ch04.ต้องโอน">11,220</td><td class="blank"></td>'
             '<td data-field="ใครจ่าย"></td></tr><tr><td>ถ้าเปลี่ยนตลาด</td></tr></table>'
             '<p class="pass-h"><strong>✅ เกณฑ์ผ่าน 3 ข้อ</strong></p><ol class="pass"><li>หนึ่ง</li><li>สอง</li><li>สาม</li></ol>'
             '<p class="app">📱 จดจากแอป · ถ้าแอปไม่มีค่านี้: ใช้ค่าในใบมิน</p></div>')
    d = {
        "pos": '<p class="pos"><strong>ภาค 1 · บท 4 จาก 18</strong> · ต้องรู้จากบทก่อน: ระยะห่างของสองราคา</p>\n',
        "scene": f'<div class="scene-open" data-day="1"{f" data-continues={chr(34)}{cont}{chr(34)}" if cont else ""}>'
                 f'<p>มินเปิดสมุด {scene}</p></div>\n',
        "cq": '<div class="pq">คำถามของบท</div>\n',
        "h2a": '<h2>ตอนที่หนึ่ง: ได้ 3</h2>\n<p>ราคาขึ้น 2 + 1 = 3 แล้วลง 3 − 1 = 2</p>\n',
        "table": '<div class="tw"><table><tr><th>เหตุการณ์</th><th class="calc">คิดอย่างไร</th></tr>'
                 '<tr><td>ซื้อ</td><td class="calc">2 + 1 = 3 และ 3 = 3 และ 2 = 2</td></tr></table></div>\n',
        "stop": '<div class="stop"><div class="bt">🛑 ทายก่อน</div><p>ถ้าเป็นคุณ?</p></div>\n',
        "fig": '<!--CHART:sab-zz--><div class="figw"><svg class="fig" viewBox="0 0 10 10"><rect width="5" height="5"/></svg></div>'
               '<div class="cap">🔢 ภาพแนวคิด</div><!--/CHART:sab-zz-->\n',
        "readfig": '<p class="readfig"><strong>อ่านภาพ:</strong> แท่งซ้ายสูงกว่าแท่งขวา</p>\n',
        "fm": '<p><strong>🚶 อ่านเป็นภาษาคนก่อน:</strong> กำไรคือเงินที่รับลบเงินที่จ่าย</p>\n<div class="fm">กำไร = รับ − จ่าย</div>\n',
        "readeq": '<p class="readeq"><strong>อ่านสมการ:</strong> 3 − 2 = 1 และ 1 = 1 และ 2 = 2</p>\n',
        "rest_a": '<div class="rest"><div class="bt">พักตรงนี้ได้</div><p>ถึงตรงนี้ได้ 3</p></div>\n',
        "h2b": '<h2>ตอนที่สอง: เหลือ 2</h2>\n<p>เนื้อหาของตอนที่สอง</p>\n',
        "deep": '<details class="deep" id="deep-1"><summary>🔎 ลงลึก</summary><div class="fm">σ = 0.12345 = x</div>'
                '<p>a = b และ b = c และ c = a</p></details>\n',
        "dist": '<div class="dist"><div class="bt">ตัวอย่างเดียว (n = 1)</div><p>หนึ่งเส้นทาง</p></div>\n',
        "other": '<div class="other" data-claim="basis-long-leverage"><div class="bt">👥 คนอีกฝั่ง</div><p>ฝั่ง long</p></div>\n',
        "rest_b": '<div class="rest"><div class="bt">พักตรงนี้ได้</div><p>ถึงตรงนี้เหลือ 2</p></div>\n',
        "sum3": '<div class="sum3"><div class="bt">สรุป 3 ข้อ</div><ol><li>หนึ่ง</li><li>สอง</li><li>สาม</li></ol></div>\n',
        "ex": f'<div class="bx bg"><div class="bt">✍️ ลองทำเอง</div>\n<ol>{items}</ol></div>\n',
        "hook": f'<div class="pq" data-hook="{hook}">คำถามสะพาน แนวคิด z รออยู่</div>\n',
        "terms": '<div class="bx bb"><div class="bt">📖 ศัพท์ใหม่ในตอนนี้</div><ul>'
                 '<li><strong>Cash Buffer (กันชนเงินสด)</strong> = เงินสำรอง <span class="tier" data-tier="ก"></span></li>'
                 '<li><strong>Margin (หลักประกัน)</strong> = เงินค้ำสัญญา</li></ul></div>\n',
        "file": f'<details class="file"><summary>📁 แฟ้มของบทนี้</summary>\n{sheet}\n<table class="ledger" data-part="{n}">'
                '<tr><td data-key="ch04.ต้องโอน">11,220</td></tr></table>\n'
                '<details class="deep" id="deep-2"><summary>🔎 ลงลึกรอบสอง</summary><p>σ อยู่ในนี้ได้</p></details></details>\n',
    }
    if kind == "base":                                  # หน้าพื้นฐาน: แฟ้ม · ใบงาน · .dist · 👥 ไม่บังคับ
        for k in ("file", "dist", "other"):
            del d[k]
    return d


def _v2_page(head, tail, d):
    return head.replace("<body>", '<body data-tpl="2">') + "".join(d.values()) + tail


def _selftest_v2(head, tail, fig):
    """คืน (ผ่านไหม, จำนวนกรณีผิดจงใจ) — (1) ชุดหน้าที่ถูกต้องปนกันระหว่าง base · v2 · v1 ต้องไม่ถูกฟ้อง
    (2) กรณีผิดจงใจทีละข้อ ต้องถูกจับด้วยข้อความที่คาด"""
    terms = {"z": {"สอน": 9, "รูปแบบ": ["ค่า z"]}, "ค่าผ่านทาง": {"สอน": 1}, "ภาระค้าง": {"สอน": "base3"}}
    ok = True

    def write(d, name, text):
        with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def more(d, key, html):                             # ต่อท้ายชิ้นส่วน
        d[key] += html

    def swap(d, key, old, new):
        assert old in d[key], (key, old)
        d[key] = d[key].replace(old, new)

    term_li = "<li><strong>Term (คำ)</strong> = ความหมาย</li>"
    # (ชื่อไฟล์, ชนิด, เลข, ตัวแก้, ข้อความที่ต้องจับได้)
    cases = [
        ("part", 2, lambda d: d.pop("pos"), "V1 ขาด .pos"),
        ("part", 2, lambda d: d.pop("scene"), "V1 ขาด .scene-open"),
        ("part", 2, lambda d: d.pop("cq"), "V1 ขาด .pq คำถามของบท"),
        ("part", 2, lambda d: d.pop("stop"), "V1 ขาด 🛑 .stop"),
        ("part", 2, lambda d: d.pop("sum3"), "V1 ขาด .sum3"),
        ("part", 2, lambda d: d.pop("ex"), "V1 ขาด ✍️"),
        ("part", 2, lambda d: d.pop("hook"), "V1 ขาด .pq[data-hook]"),
        ("part", 2, lambda d: d.pop("terms"), "V1 ขาด 📖"),
        ("part", 2, lambda d: d.pop("file"), "V1 ต้องมี details.file"),
        ("part", 2, lambda d: more(d, "file", '<details class="file"><summary>📁 อีกแฟ้ม</summary><p>x</p></details>'),
         "หนึ่งบล็อกพอดี (พบ 2)"),
        ("part", 2, lambda d: swap(d, "file", 'class="bx sheet"', 'class="bx nosheet"'), "V1 details.file ต้องมี .sheet"),
        ("part", 2, lambda d: d.pop("rest_a"), "V2 ตอน «ตอนที่หนึ่ง"),
        ("part", 2, lambda d: d.pop("rest_b"), "V2 ตอน «ตอนที่สอง"),
        ("part", 2, lambda d: (d.pop("h2a"), d.pop("h2b")), "V2 ไม่มี <h2> ตอนสอน"),
        ("part", 2, lambda d: d.pop("readfig"), "V3 กราฟ sab-zz"),
        ("part", 2, lambda d: swap(d, "readfig", "อ่านภาพ:", "ดูภาพ:"), 'ต้องขึ้นต้นด้วย "อ่านภาพ:"'),
        ("part", 2, lambda d: d.pop("readeq"), "V4 สูตร «กำไร = รับ − จ่าย»"),
        ("part", 2, lambda d: swap(d, "readeq", "อ่านสมการ:", "สมการนี้:"), 'ต้องขึ้นต้นด้วย "อ่านสมการ:"'),
        ("part", 2, lambda d: d.update(ex=re.sub(r"<li>ข้อ 5 .*?</li>(?=</ol>)", "", d["ex"], flags=re.S)), "V5 ✍️ มี 4 ข้อ (ต้อง ≥ 5)"),
        ("part", 2, lambda d: swap(d, "ex", "</ol>", "<li>ข้อไม่มีเฉลย</li></ol>"), "V5 ✍️ ข้อ 6 ไม่มี details.ans"),
        ("part", 2, lambda d: d.update(ex=re.sub(r'(<li>ข้อ 1 )<details class="hint">.*?</details></details>', r"\1", d["ex"], flags=re.S)),
         "V5 ✍️ มีคำใบ้ details.hint 2 ข้อ (ต้อง ≥ 3)"),
        ("part", 2, lambda d: more(d, "h2b", "<p>ได้ 2 + 1 = 3 แล้ว 3 × 2 = 6 จึงเหลือ 6 − 1 = 5</p>"), 'มี "=" 3 ตัว'),
        ("part", 2, lambda d: d.update(terms=d["terms"].replace("</ul>", term_li * 6 + "</ul>")), "V7 ศัพท์ใหม่ 8 คำ เกินเพดาน 7"),
        ("part", 2, lambda d: d.update(terms=d["terms"].replace("</ul>", "<li>คำที่ไม่มีนิยาม</li></ul>")), "V7 รายการศัพท์"),
        ("part", 2, lambda d: d.update(terms=d["terms"].replace("<li><strong>Margin", '<li data-tier="ข"><strong>Margin')),
         "data-tier ต้องอยู่"),
        ("part", 2, lambda d: more(d, "file", '<div class="transfer"><div class="bt">🔁 ถ้าเปลี่ยนตลาด</div></div>'), "V8 ป้ายที่เลิกใช้ในหน้า v2: 🔁"),
        ("part", 2, lambda d: more(d, "h2b", '<div class="dft"><div class="bt">⚠️ ค่าเริ่มต้น</div></div>'), "V8 ป้ายที่เลิกใช้ในหน้า v2: ⚠️ ค่าเริ่มต้น"),
        ("part", 2, lambda d: more(d, "h2b", '<div class="bx bp"><div class="bt">🧭 นิสัยคิด</div></div>'), "V8 ป้ายที่เลิกใช้ในหน้า v2: 🧭 นิสัยคิด"),
        ("part", 2, lambda d: more(d, "pos", '<div class="bx bb"><div class="bt">🧭 เส้นทางอ่าน</div></div>'), "V8 ป้ายที่เลิกใช้ในหน้า v2: 🧭 เส้นทางอ่าน"),
        ("part", 2, lambda d: more(d, "pos", '<div class="bx bb" data-path="fast"><div class="bt">🟠 ย่อจากบทที่ข้าม</div></div>'), "V8 ป้ายที่เลิกใช้ในหน้า v2: 🟠"),
        ("part", 2, lambda d: more(d, "h2b", '<p>อ่านต่อใน <a href="https://example.invalid/nq-part7">เล่ม nq</a></p>'), 'V8 คำ "nq"'),
        # กฎเดิมที่คงไว้ในหน้า v2
        ("part", 2, lambda d: more(d, "h2b", "<p>ความผันผวน σ ของราคา</p>"), "W12 สัญลักษณ์ 'σ'"),
        ("part", 2, lambda d: more(d, "file", "<p>ในแฟ้มก็ห้าม 0.12345 และ ln</p>"), "W13 ทศนิยมเกิน 2 ตำแหน่ง 0.12345"),
        ("part", 2, lambda d: more(d, "h2b", "<p>ใช้ z ตรงนี้</p>"), "W22 ใช้ 'z'"),
        ("part", 2, lambda d: d.pop("dist"), "W23"),
        ("part", 2, lambda d: d.pop("other"), "ต้องมี 👥 .other"),
        ("part", 2, lambda d: swap(d, "scene", 'data-continues="part1"', 'data-continues="part0"'), "W15 ฉากเปิดต้องมี"),
        ("part", 2, lambda d: more(d, "h2b", '<div class="tw"><table data-src="sim"><tr><td>ผลจำลอง</td></tr></table></div>'),
         'W16 ตาราง data-src="sim"'),
        ("part", 2, lambda d: more(d, "h2b", '<svg viewBox="0 0 9 9"><rect width="5" height="5"/></svg>' + "<p>เว้นระยะ</p>" * 60), "W16 ตาราง/กราฟ"),
        # หน้าพื้นฐาน
        ("base", 2, lambda d: d.update(ex=re.sub(r"<li>ข้อ 3 .*?</li>(?=</ol>)", "", d["ex"], flags=re.S)), "V5 ✍️ มี 2 ข้อ (ต้อง ≥ 3)"),
        ("base", 2, lambda d: d.update(terms=d["terms"].replace("</ul>", term_li * 3 + "</ul>")), "V7 ศัพท์ใหม่ 5 คำ เกินเพดาน 4"),
        ("base", 2, lambda d: more(d, "h2b", "<p>เงินที่รับมายังมีภาระค้างอยู่</p>"), "W22 ใช้ 'ภาระค้าง' ก่อนสอน (สอนในพื้นฐาน 3)"),
        ("base", 2, lambda d: d.pop("rest_b"), "V2 ตอน «ตอนที่สอง"),
        ("base", 2, lambda d: d.update(_plain=True), "หน้าพื้นฐานต้องเป็นแม่แบบ v2"),
    ]
    with tempfile.TemporaryDirectory() as d0:
        fp, tp = os.path.join(d0, "f.json"), os.path.join(d0, "t.json")
        json.dump(fig, open(fp, "w", encoding="utf-8"), ensure_ascii=False)
        json.dump(terms, open(tp, "w", encoding="utf-8"), ensure_ascii=False)

        # (1) ชุดที่ถูกต้อง: base3 → base4 → บท 0 (v2) → บท 1 (v1) → บท 2 (v2) · บท 4 (v2 ทางด่วน) → บท 5 (v1 ทางด่วน)
        good = os.path.join(d0, "good")
        os.mkdir(good)
        b3 = _v2_parts("base", 3, hook="สองขาในชุดเดียว")
        more(b3, "h2b", "<p>เงินที่รับมายังมีภาระค้างอยู่</p>")                     # สอนใน base3 → ใช้ได้
        write(good, "sab-base3.html", _v2_page(head, tail, b3))
        write(good, "sab-base4.html", _v2_page(head, tail, _v2_parts("base", 4, hook="คืนก่อนวันที่ 1", scene="สองขาในชุดเดียว")))
        write(good, "sab-part0.html", _v2_page(head, tail, _v2_parts("part", 0, scene="คืนก่อนวันที่ 1")))
        write(good, "sab-part1.html", head + _chapter(1) + tail)                       # v1: ฉากเปิดมี "เงินสดอิสระ" ของบท 0
        write(good, "sab-part2.html", _v2_page(head, tail, _v2_parts("part", 2, scene="เงินสดอิสระ")))
        p4 = _v2_parts("part", 4)
        more(p4, "h2b", "<p>ค่าผ่านทางสองขา</p>")                                     # สอนบท 1 ที่ทางด่วนข้าม · v2 ไม่ตรวจทางด่วน
        write(good, "sab-part4.html", _v2_page(head, tail, p4))
        write(good, "sab-part5.html", head + _chapter(5, extra="<p>ค่าผ่านทางสองขา</p>") + tail)   # v1 หลังบททางด่วนที่เป็น v2
        _, p_good = run(good, fp, tp, quiet=True)
        if p_good:
            ok = False
            print("selftest ล้ม: หน้า v2/base ที่ถูกต้อง (หรือบท v1 ข้างเคียง) ถูกฟ้อง →")
            for p in p_good:
                print("   ", p)

        # (2) กรณีผิดจงใจ ทีละกรณี ในโฟลเดอร์ของตัวเอง (ไม่มีบทข้างเคียง)
        for i, (kind, n, mutate, want) in enumerate(cases):
            cd = os.path.join(d0, f"c{i}")
            os.mkdir(cd)
            d = _v2_parts(kind, n)
            mutate(d)
            plain = d.pop("_plain", False)
            name = f"sab-{kind}{n}.html"
            write(cd, name, (head + "".join(d.values()) + tail) if plain else _v2_page(head, tail, d))
            _, probs = run(cd, fp, tp, quiet=True)
            if not any(want in p for p in probs):
                ok = False
                print(f"selftest ล้ม: v2 ไม่จับข้อผิดจงใจ {want!r} → ได้ {probs}")

        # (3) โซ่ base4 → บท 0: hook ของหน้าพื้นฐานสุดท้ายต้องอยู่ในฉากเปิดของบท 0 · บท 0 แบบ v2 ต่อจากอย่างอื่นไม่ได้
        chain = os.path.join(d0, "chain")
        os.mkdir(chain)
        write(chain, "sab-base4.html", _v2_page(head, tail, _v2_parts("base", 4, hook="ไม่มีในบทศูนย์")))
        write(chain, "sab-part0.html", _v2_page(head, tail, _v2_parts("part", 0, cont="part9")))
        _, probs = run(chain, fp, tp, quiet=True)
        for want in ("W15 data-hook 'ไม่มีในบทศูนย์' ไม่ปรากฏในฉากเปิดของบท 0", "W15 บท 0 ต้องไม่มี data-continues"):
            if not any(want in p for p in probs):
                ok = False
                print(f"selftest ล้ม: v2 ไม่จับข้อผิดจงใจ {want!r} → ได้ {probs}")
    return ok, len(cases) + 2


def selftest_next():
    """--book sab2 --selftest: กฎ V9–V11 (tools/sab2_qa.py) + บทหุ่นเล่ม 2 ผ่าน run() จริง
    (ทุกบทเป็น v2 · บทแรก = บท 1 ไม่มี data-continues · คำเล่ม 1 ใช้ได้อิสระ · W22 ของคำเล่ม 2 · W18 ส่วนต่าง ทุกบท)"""
    import sab2_qa
    ok = sab2_qa.selftest() == 0
    head, tail = B.shell()
    fails = ('<div class="fails"><div class="bt">⚠️ พังเมื่อไร / บอกอะไรไม่ได้</div>'
             '<ul><li><strong>พังเมื่อ</strong> ข้อมูลสั้นกว่า 3 วัน</li></ul></div>\n')
    code = ('<details class="code"><summary>💻 ทำด้วย Python</summary>\n<pre>print(2 + 1)\n# ผลที่ต้องได้: 3</pre>\n'
            '<p>ทำซ้ำสิ่งที่คิดด้วยมือ</p></details>\n')

    def page(n, cont=None, scene="", drop=(), extra="", body_v2=True, **repl):
        d = _v2_parts("part", n, scene=scene, cont=cont)
        d["pos"] = d["pos"].replace("บท 4 จาก 18", f"บท {n} จาก {LAST_PART}")
        d["file"] = '<details class="file"><summary>📁 แฟ้มของบทนี้</summary><p>หน้าสมุดวิจัย</p></details>\n'
        for k in ("other", "dist"):
            del d[k]
        d["rest_a"] = fails + code + d["rest_a"]
        d["h2b"] = d["h2b"].replace("<p>เนื้อหาของตอนที่สอง</p>", f"<p>เนื้อหาของตอนที่สอง {extra}</p>")
        for k in drop:
            d["rest_a"] = d["rest_a"].replace({"fails": fails, "code": code}[k], "")
        for k, v in repl.items():
            d[k] = v
        h = head.replace("<body>", '<body data-tpl="2">') if body_v2 else head
        return h + "".join(d.values()) + tail

    with tempfile.TemporaryDirectory() as d0:
        fp = os.path.join(d0, f"{PREFIX}-figures.json")
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump({"_claims": []}, fh)
        tp = os.path.join(d0, "terms.json")
        with open(tp, "w", encoding="utf-8") as fh:
            json.dump({"Kalman Filter": {"สอน": 6}}, fh)

        def run_set(pages, terms=tp):
            d = tempfile.mkdtemp(dir=d0)
            for name, html in pages.items():
                with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
                    fh.write(html)
            return run(d, fp, terms, quiet=True)[1]
        good = {f"{PREFIX}-part1.html": page(1, cont="", extra="ใช้ Funding Rate จากเล่ม 1"),
                f"{PREFIX}-part2.html": page(2, scene="เงินสดอิสระ"),
                f"sab-part1.html": "<p>หน้าเล่ม 1 ต้องไม่ถูกตรวจ</p>"}
        probs = run_set(good, terms=B.TERMS) + run_set(good)
        if probs:
            ok = False
            print("selftest ล้ม: บทเล่ม 2 ที่ถูกต้องถูกฟ้อง →", probs)
        bad = {
            "V10 ไม่มีกล่อง .fails": page(1, cont="", drop=("fails",)),
            "V9 บล็อก 💻": page(1, cont="",
                               rest_a=fails + code.replace("print(2 + 1)", "print(2 + 2)") + '<div class="rest"><div class="bt">พักตรงนี้ได้</div><p>ถึงตรงนี้ได้ 3</p></div>\n'),
            "ต้องเป็นแม่แบบ v2": page(1, cont="", body_v2=False),
            "W15 บท 1 ต้องไม่มี data-continues": page(1, cont="part0"),
            "W22 ใช้ 'Kalman Filter' ก่อนสอน": page(1, cont="", extra="Kalman Filter"),
            "W18 'ส่วนต่าง'": page(1, cont="", extra="ส่วนต่างของคู่"),
        }
        for want, html in bad.items():
            got = run_set({f"{PREFIX}-part1.html": html})
            if not any(want in p for p in got):
                ok = False
                print(f"selftest ล้ม: ไม่จับ {want!r} → {got}")
    print("selftest", f"ผ่าน ✓ (เล่ม {B.VOL}: บทหุ่นที่ถูกต้องไม่ถูกฟ้อง · คำเล่ม 1 ใช้ได้ · จับ {len(bad)} กรณี "
          "V9 · V10 · v2 บังคับ · W15 บทแรก · W22 คำเล่มนี้ · W18 ส่วนต่าง)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest_next() if NEXT_VOL else selftest())
    scope = a[a.index("--scope") + 1] if "--scope" in a else None
    sys.exit(run(DOCS, FIG, TERMS, scope, "--pending" in a, "--final" in a)[0])
