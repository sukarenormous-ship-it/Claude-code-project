#!/usr/bin/env python3
"""ตรวจคุณภาพหนังสือ "Stat Arb for Non Quant · เล่ม 1" (docs/sab-*.html) ในคำสั่งเดียว

ต่อยอดจาก nq_qa.py (โครงสร้าง HTML · W11 <br> ปลอม · กล่องบังคับ · W8 ลิงก์ · W9 เพดานศัพท์)
แล้วเพิ่มกฎของเล่มนี้ตามแผน docs/sab-book-plan.md หัวข้อ 10.4
  W12 สัญลักษณ์/สูตรต้องห้ามนอก 🔎     W13 ทศนิยม > 2 ตำแหน่งนอก 🔎      W14 ลิงก์ #anchor ต้องมีจริง
  W15 ฉากเปิดต่อบทก่อน + .pq สะพาน      W16 ป้ายที่มาตาราง/กราฟ · table.fees  W18 คำต้องห้าม
  W19 ใบงาน                             W20 บัตรธรรมชาติ                  W21 หมายเหตุ h/β เมื่อชี้ math-part9
  W22 ห้ามใช้ก่อนสอน (tools/sab_terms.json)                                W23 .dist · W24 .whyline · W25 data-claim
  D1  (--final) ไม่มี data-pending เหลือ

    python3 tools/sab_qa.py                    # ทุกไฟล์ docs/sab-*.html
    python3 tools/sab_qa.py --scope part4      # เฉพาะบท (W15 ข้ามเมื่อบทข้างเคียงยังไม่มีไฟล์)
    python3 tools/sab_qa.py --pending          # ลิงก์ไปไฟล์ที่ยังไม่มีในกล่อง data-pending = เตือน ไม่ fatal
    python3 tools/sab_qa.py --final            # เฟส 5: data-pending ห้ามเหลือ
    python3 tools/sab_qa.py --selftest         # ใส่ข้อผิดจงใจในบทหุ่น ต้องจับได้ครบ และกรณียกเว้นต้องไม่ถูกฟ้อง
"""

import glob
import json
import os
import re
import sys
import tempfile
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FIG = os.path.join(DOCS, "sab-figures.json")
TERMS = os.path.join(ROOT, "tools", "sab_terms.json")
TERM_CAP = 12
LAST_PART = 18
DIST_REQUIRED = {2, 4, 6, 7, 10, 12, 13, 14, 15, 16, 17}
OTHER_REQUIRED = {1, 2, 5, 7, 9, 12, 17}

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


def main_path(html):
    """ข้อความเส้นทางหลัก: ตัด 🔎 details.deep · details.ans · script/style/code · comment"""
    spans = blocks(html, lambda t, a: t == "details")
    return text_of(cut(html, spans))


def part_no(name):
    m = re.fullmatch(r"sab-part(\d+)\.html", name)
    return int(m.group(1)) if m else None


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return None


def get_path(fig, path):
    cur = fig
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def check_file(name, html, ctx):
    P = []
    n = part_no(name)
    pages, fig, terms, opts = ctx["pages"], ctx["fig"], ctx["terms"], ctx["opts"]

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
    for m in re.finditer(r"ไม่มีความเสี่ยง", vis):
        before = vis[max(0, m.start() - 2):m.start()]
        if not re.search(r"[\"“'‘]", before):
            P.append(f"{name}: W18 'ไม่มีความเสี่ยง' นอกเครื่องหมายคำพูด")

    # W12/W13 เส้นทางหลัก
    mp = main_path(html)
    mp_clean = re.sub(r"ภาคผนวก\s+[A-I]\b", " ", mp)
    mp_clean = re.sub(r"[\w.-]+\.(?:csv|xlsx|html|py)", " ", mp_clean)
    for sym in FORBIDDEN_SYMBOLS:
        if sym in mp_clean:
            P.append(f"{name}: W12 สัญลักษณ์ {sym!r} นอก 🔎")
    for sym in FORBIDDEN_LATIN:
        if re.search(r"(?<![A-Za-z0-9_\-])" + re.escape(sym) + r"(?![A-Za-z0-9_\-])", mp_clean):
            P.append(f"{name}: W12 สัญลักษณ์ {sym!r} นอก 🔎")
    for m in re.finditer(r"(?<![\d.])\d+\.\d{3,}(?![\d])", mp):
        P.append(f"{name}: W13 ทศนิยมเกิน 2 ตำแหน่ง {m.group(0)} นอก 🔎")

    # W16 ป้ายที่มา + table.fees
    for s, e, a in blocks(html, lambda t, a: t in ("table", "svg")):
        if has_class(a, "ledger") or has_class(a, "ncard") or "data-nosrc" in a:
            continue
        window = html[max(0, s - 300):min(len(html), e + 400)]
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
    if opts["final"] and re.search(r"\bdata-pending(?!-part)\b", html):
        P.append(f"{name}: D1 ยังมี data-pending เหลือ")

    if n is None:
        return P

    # ===== กฎเฉพาะบท =====
    for label, needle in REQUIRED_BOXES:
        if needle not in html and not (label.startswith("ประโยคทอง") and n == LAST_PART and 'class="pq' in html):
            P.append(f"{name}: ขาด {label}")
    for label, needle in CHAPTER_BOXES:
        if needle not in html:
            P.append(f"{name}: ขาดกล่อง {label}")
    for label, needles in ONE_OF:
        if not any(x in html for x in needles):
            P.append(f"{name}: ต้องมี {label}")
    if n in DIST_REQUIRED and 'class="dist"' not in html:
        P.append(f"{name}: W23 บท {n} ต้องมี .dist")
    if n in OTHER_REQUIRED and not blocks(html, lambda t, a: has_class(a, "other")):
        P.append(f"{name}: บท {n} ต้องมี 👥 .other")
    if (sheets or re.search(r'href="sab-tool-', html)) and 'class="whyline"' not in html:
        P.append(f"{name}: W24 มีใบงาน/เครื่องมือแต่ไม่มี .whyline")

    # W9 เพดานศัพท์ (นับจากกล่อง 📖 แบบเดียวกับ glossary)
    box = re.search(r"📖 ศัพท์ใหม่ในตอนนี้</div>(.*?)</div>\s*(?:<!--|$)", html, re.S)
    if box:
        got = re.findall(r"<li><strong>(.*?)</strong>\s*=", box.group(1))
        if len(got) > TERM_CAP:
            P.append(f"{name}: W9 ศัพท์ใหม่ {len(got)} คำ เกินเพดาน {TERM_CAP}")
        for li in re.findall(r"<li\b[^>]*>.*?</li>", box.group(1), re.S):
            if re.search(r"<(li|strong)\b[^>]*data-tier", li):
                P.append(f"{name}: W9 data-tier ต้องอยู่ที่ <span class=\"tier\"> ไม่ใช่ <li>/<strong>")

    # W15 ความต่อเนื่อง
    so = blocks(html, lambda t, a: has_class(a, "scene-open"))
    if so:
        a = so[0][2]
        cont = re.search(r'data-continues="([^"]+)"', a)
        if n == 0 and cont:
            P.append(f"{name}: W15 บท 0 ต้องไม่มี data-continues")
        if n > 0 and (not cont or cont.group(1) != f"part{n - 1}"):
            P.append(f"{name}: W15 ฉากเปิดต้องมี data-continues=\"part{n - 1}\"")
    if n < LAST_PART:
        hooks = re.findall(r'class="pq"[^>]*data-hook="([^"]+)"|data-hook="([^"]+)"[^>]*class="pq"', html)
        hooks = [x or y for x, y in hooks]
        if not hooks:
            P.append(f"{name}: W15 ไม่มี .pq สะพานที่มี data-hook")
        nxt = pages.get(f"sab-part{n + 1}.html")
        if nxt is not None and hooks:
            ns = blocks(nxt, lambda t, a: has_class(a, "scene-open"))
            scene = text_of(nxt[ns[0][0]:ns[0][1]]) if ns else ""
            for h in hooks:
                if h not in scene:
                    P.append(f"{name}: W15 data-hook {h!r} ไม่ปรากฏในฉากเปิดของบท {n + 1}")

    # W22 ห้ามใช้ก่อนสอน
    if terms:
        exempt = blocks(html, lambda t, a: t == "details" or (has_class(a, "pq") and "data-hook" in a)
                        or (t == "table" and has_class(a, "ncard")))      # หัวช่องบัตร 8 ช่องเป็นแม่แบบคงที่
        exempt += box_spans(html, "🧭 เส้นทางอ่าน") + box_spans(html, "🔗") + box_spans(html, "📖")
        txt = text_of(cut(html, exempt))
        for term, info in terms.items():
            if term.startswith("_"):
                continue
            taught = info.get("สอน")
            if taught is None or n >= taught:
                continue
            for form in [term] + info.get("รูปแบบ", []):
                pat = (r"(?<![A-Za-z])" + re.escape(form) + r"(?![A-Za-z])") if form.isascii() else re.escape(form)
                if re.search(pat, txt):
                    P.append(f"{name}: W22 ใช้ {form!r} ก่อนสอน (สอนในบท {taught})")
                    break
    return P


def run(docs_dir, fig_path, terms_path, scope=None, pending=False, final=False, quiet=False):
    files = sorted(glob.glob(os.path.join(docs_dir, "sab-*.html")),
                   key=lambda p: (part_no(os.path.basename(p)) is None, part_no(os.path.basename(p)) or 0, p))
    pages = {}
    for p in files:
        with open(p, encoding="utf-8") as fh:
            pages[os.path.basename(p)] = fh.read()
    for p in glob.glob(os.path.join(docs_dir, "*")):
        pages.setdefault(os.path.basename(p), None)
    ctx = {"pages": {k: v for k, v in pages.items() if v is not None}, "fig": load_json(fig_path),
           "terms": load_json(terms_path), "opts": {"pending": pending, "final": final}, "warnings": []}
    ctx["pages"].update({k: "" for k, v in pages.items() if v is None})
    targets = [f for f in files if not scope or os.path.basename(f) == f"sab-{scope}.html"]
    problems = []
    for p in targets:
        problems += check_file(os.path.basename(p), pages[os.path.basename(p)], ctx)
    if not quiet:
        print(f"ตรวจ {len(targets)} ไฟล์" + (" (ยังไม่มี tools/sab_terms.json — ข้าม W22)" if not ctx["terms"] else ""))
        for w in ctx["warnings"]:
            print("  ·", w)
        if problems:
            print(f"พบปัญหา {len(problems)} ข้อ")
            for p in problems:
                print("  -", p)
        else:
            print("ผ่านทุกข้อ ✓")
    if not targets and not quiet:
        print("ยังไม่มีไฟล์ docs/sab-*.html ให้ตรวจ")
    return (1 if problems else 0), problems


# ───────────────────────── selftest ─────────────────────────

def _chapter(n, extra="", hook="เงินสดอิสระ", cont=True, shell=True):
    cont_attr = f' data-continues="part{n - 1}"' if cont and n > 0 else ""
    sheet = ('<div class="bx sheet" data-sheet="04" data-from="00" data-to="05">'
             '<div class="bt">🛠 ใบ 04 · ใบกันชนเงินสด</div><p class="whyline">🔩 ทำไมต้องมีเครื่องมือนี้: ทุนหมดก่อน</p>'
             '<p>🔢 สมมติเพื่อสอน</p><table class="sheet-tbl"><tr><td data-key="ch04.ต้องโอน">11,220</td>'
             '<td class="blank"></td><td data-field="ใครจ่าย"></td></tr><tr><td>ถ้าเปลี่ยนตลาด</td></tr></table>'
             '<ol class="pass"><li>หนึ่ง</li><li>สอง</li><li>สาม</li></ol>'
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
    print("selftest", f"ผ่าน ✓ (จับข้อผิดจงใจครบ {len(expect)} ชนิด · กรณียกเว้น 'ภาคผนวก C' / '02b' / "
          "'funding-log.csv' / .pq ที่เอ่ยแนวคิดบทถัดไป ไม่ถูกฟ้อง)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest())
    scope = a[a.index("--scope") + 1] if "--scope" in a else None
    sys.exit(run(DOCS, FIG, TERMS, scope, "--pending" in a, "--final" in a)[0])
