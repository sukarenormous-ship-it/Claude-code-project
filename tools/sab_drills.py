#!/usr/bin/env python3
"""ภาคผนวก D (docs/sab-appendix-drills.html) — ตัวเติมตัวเลขและตัวตรวจของหน้าเขียนมือ

เดิมสคริปต์นี้คัดลอกกล่อง ✍️ ของทุกบทมาเป็นภาคผนวก D และแยกเฉลยไป docs/sab-appendix-answers.html
(ซ้ำกับในบท 57 จาก 57 ข้อ · รายงาน compare-v2/report-D §5) ตั้งแต่บทเป็นแม่แบบ v2 แบบฝึกห้าข้อพร้อมคำใบ้
และเฉลยอยู่ในบทแล้ว ภาคผนวก D จึงเป็นหน้าเขียนมือตามแผน 14.5/14.6: ชุดฝึกเปลี่ยนเงื่อนไข (v1…) ·
ทบทวนสะสมสามชุด (r1-… หลังบท 7 · r2-… หลังบท 14 · r3-… หลังบท 18) · บันไดประเมินตนเอง (#ladder)
ตัวเลขทุกตัวในหน้าอยู่ใน <span data-key="drills.…"> คำนวณใน tools/sab_figures_ch/drills.py
หน้าเฉลยเดิมเหลือเป็นหน้าชี้ทางสั้น ๆ (เฉลยอยู่ข้างข้อแล้ว) เพื่อให้ลิงก์เก่าไม่พัง

    python3 tools/sab_drills.py              # เติมตัวเลขใน data-key จาก sab-figures.json · เขียนหน้าชี้ทาง
    python3 tools/sab_drills.py --check      # ไม่เขียนอะไร: ตัวเลขตรง JSON · โครงหน้าครบ · ไม่ซ้ำแบบฝึกในบท · หน้าชี้ทางเป็นปัจจุบัน
    python3 tools/sab_drills.py --selftest   # ใส่ข้อผิดจงใจในหน้าหุ่น ต้องจับได้ครบ
"""

import difflib
import html as htmllib
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

TARGET = "sab-appendix-drills.html"
ANSWERS = "sab-appendix-answers.html"
FIG = os.path.join(B.DOCS, "sab-figures.json")
VARY = (18, 22)          # จำนวนข้อชุดเปลี่ยนเงื่อนไข (แผน: ราว 18–22)
REVIEW = (4, 6)          # ข้อต่อชุดทบทวนสะสม
COPY_RATIO = 0.6         # คล้ายแบบฝึกในบทเกินนี้ = ถือว่าคัดลอก


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



def collect(docs=B.DOCS):
    """[(บท, [(โจทย์ html, เฉลย html), …])] จากกล่อง ✍️ ของทุกบท (ใช้ตรวจว่าภาคผนวก D ไม่ซ้ำในบท)"""
    chapters = []
    for path in B.chapter_files(docs):
        with open(path, encoding="utf-8") as fh:
            p = DrillParser()
            p.feed(fh.read())
        chapters.append((B.part_no(path), p.items))
    return chapters


# ── หน้าชี้ทาง (แทนหน้าเฉลยเดิม) ─────────────────────────────────────────────
def render_stub():
    body = (f'<div class="bx bb"><div class="bt">เฉลยย้ายไปอยู่ข้างข้อแล้ว</div>'
            f'<p>หน้านี้เคยรวมเฉลยของแบบฝึกท้ายบท ตอนนี้แบบฝึกห้าข้อของแต่ละบทมีคำใบ้และเฉลยอยู่ในบทนั้นเลย '
            f'ส่วนภาคผนวก D มีโจทย์ชุดใหม่ที่ไม่ซ้ำกับในบท และเฉลยอยู่ใต้ข้อเช่นกัน</p>'
            f'<ul><li><a href="{TARGET}#vary1">ฝึกเมื่อเงื่อนไขเปลี่ยน</a> · '
            f'<a href="{TARGET}#review1">ทบทวนสะสมหลังบท 7</a> · <a href="{TARGET}#review2">หลังบท 14</a> · '
            f'<a href="{TARGET}#review3">หลังบท 18</a></li>'
            f'<li><a href="{TARGET}#ladder">บันไดประเมินตนเองสี่ขั้น</a></li>'
            f'<li><a href="{B.PREFIX}-index.html">สารบัญ</a> สำหรับแบบฝึกท้ายบท (เปิดบทแล้วเลื่อนไปที่กล่อง ✍️ ลองทำเอง)</li></ul></div>')
    return B.page("เฉลยแบบฝึก (ย้ายไปภาคผนวก D)", "เฉลยแบบฝึก — ย้ายไปอยู่ข้างข้อแล้ว",
                  "ภาคผนวก D และแบบฝึกท้ายบทมีเฉลยใต้ข้อทุกข้อ", body)


# ── เติม/ตรวจตัวเลข ──────────────────────────────────────────────────────────
KEY_RE = re.compile(r'(<(\w+)\b[^>]*\bdata-key="([^"]+)"[^>]*>)(.*?)(</\2>)', re.S)


def fill(page, fig):
    """คืน (หน้าที่เติมแล้ว, [ปัญหา]) · ปัญหา = คีย์ที่ไม่มีใน JSON"""
    problems = []

    def sub(m):
        try:
            v = B.get_path(fig, m.group(3))
        except KeyError:
            problems.append(f"data-key {m.group(3)!r} ไม่มีใน sab-figures.json")
            return m.group(0)
        return m.group(1) + B.fmt(v) + m.group(5)
    return KEY_RE.sub(sub, page), problems


# ── โครงหน้า ─────────────────────────────────────────────────────────────────
def items(page, pattern):
    """{id: html ของ <li id> นั้น} นับชั้น <li> เพื่อไม่ตัดกลางรายการซ้อน"""
    out = {}
    for m in re.finditer(rf'<li id="({pattern})">', page):
        depth, pos = 1, m.end()
        for t in re.finditer(r"<(/?)li\b[^>]*>", page[pos:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                out[m.group(1)] = page[pos:pos + t.start()]
                break
    return out



def question(h):
    """ข้อความโจทย์ (ตัด details ทั้งหมด รวมคำใบ้และเฉลย)"""
    while "<details" in h:
        h = re.sub(r"<details\b(?:(?!<details\b).)*?</details>", " ", h, flags=re.S)
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def check_item(iid, h, vary):
    P = []
    if vary:
        first = re.search(r"<p>(.*?)</p>", h, re.S)
        if not first or "เปลี่ยนจากตัวอย่างใน" not in first.group(1):
            P.append(f"{iid}: บรรทัดแรกต้องเป็น \"เปลี่ยนจากตัวอย่างในบท N: …\"")
        if len(re.findall("เปลี่ยนจากตัวอย่างใน", h)) != 1:
            P.append(f"{iid}: ต้องเปลี่ยนเงื่อนไขเพียงข้อเดียว (\"เปลี่ยนจากตัวอย่างใน\" หนึ่งครั้ง)")
    if not re.search(r'<details class="hint">.*?<details class="hint">', h, re.S):
        P.append(f"{iid}: ไม่มีคำใบ้สองระดับ (details.hint ซ้อน details.hint)")
    ans = re.search(r'<details class="ans">(.*?)</details>', h, re.S)
    if not ans:
        P.append(f"{iid}: ไม่มี details.ans")
        return P
    a = ans.group(1)
    p1 = re.search(r"</summary>\s*<p>(.*?)</p>", a, re.S)
    if not p1 or not p1.group(1).lstrip().startswith("<strong>"):
        P.append(f"{iid}: บรรทัดแรกของเฉลยต้องเป็นข้อสรุป (<p><strong>…)")
    if len(re.findall(r"<p>", a)) < 3:
        P.append(f"{iid}: เฉลยต้องมีข้อสรุป · ขั้นคิด · บรรทัดถ้าได้ (≥ 3 ย่อหน้า)")
    paras = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<p>(.*?)</p>", a, re.S)]
    if not any(re.search(r"ถ้า.{0,40}?(ได้|เลือก|เรียง|รายงาน).*?แปลว่า", x) for x in paras):
        P.append(f"{iid}: เฉลยไม่มีบรรทัด \"ถ้าได้ … แปลว่า …\"")
    return P


def check_structure(page):
    P = []
    vary = items(page, r"v\d+")
    if not VARY[0] <= len(vary) <= VARY[1]:
        P.append(f"ชุดเปลี่ยนเงื่อนไขมี {len(vary)} ข้อ (ต้อง {VARY[0]}–{VARY[1]})")
    nums = sorted(int(k[1:]) for k in vary)
    if nums != list(range(1, len(nums) + 1)):
        P.append(f"ลำดับข้อเปลี่ยนเงื่อนไขไม่ต่อกัน: {nums}")
    for k, h in vary.items():
        P += check_item(k, h, True)
    counts = {}
    for n in (1, 2, 3):
        if f'id="review{n}"' not in page:
            P.append(f"ไม่มีหัวข้อทบทวนสะสม id=review{n}")
        rv = items(page, rf"r{n}-\d+")
        counts[n] = len(rv)
        if not REVIEW[0] <= len(rv) <= REVIEW[1]:
            P.append(f"ทบทวนสะสมชุด {n} มี {len(rv)} ข้อ (ต้อง {REVIEW[0]}–{REVIEW[1]})")
        for k, h in rv.items():
            P += check_item(k, h, False)
    lad = re.search(r'id="ladder".*?<table\b[^>]*>(.*?)</table>', page, re.S)
    rows = len(re.findall(r"<tr><td>", lad.group(1))) if lad else 0
    if rows != 4:
        P.append(f"บันไดประเมินตนเองต้องมี 4 ขั้น (พบ {rows})")
    return P, len(vary), counts


def check_copies(page, chapters):
    """ข้อในภาคผนวก D ต้องไม่ใช่สำเนาแบบฝึกในบท · คืน (ปัญหา, ค่าคล้ายสูงสุด)"""
    P, worst = [], 0.0
    ours = {k: question(h) for k, h in items(page, r"v\d+|r\d-\d+").items()}
    theirs = [(n, i, question(q)) for n, lst in chapters for i, (q, _) in enumerate(lst, 1)]
    for k, q in ours.items():
        for n, i, t in theirs:
            sm = difflib.SequenceMatcher(None, q, t, autojunk=False)
            if sm.real_quick_ratio() < COPY_RATIO or sm.quick_ratio() < COPY_RATIO:
                continue
            r = sm.ratio()
            worst = max(worst, r)
            if r >= COPY_RATIO:
                P.append(f"{k}: คล้ายแบบฝึกข้อ {i} ของบท {n} ({r:.2f}) — ภาคผนวก D ห้ามคัดลอกแบบฝึกในบท")
    return P, worst


def run(check, docs=B.DOCS, fig_path=FIG, quiet=False):
    with open(fig_path, encoding="utf-8") as fh:
        fig = json.load(fh)
    path = os.path.join(docs, TARGET)
    with open(path, encoding="utf-8") as fh:
        page = fh.read()
    filled, P = fill(page, fig)
    if check and filled != page:
        stale = [m.group(3) for m, f in zip(KEY_RE.finditer(page), KEY_RE.finditer(filled)) if m.group(4) != f.group(4)]
        P.append(f"ตัวเลขใน data-key ไม่ตรง JSON {len(stale)} ช่อง (รัน python3 tools/sab_drills.py): {stale[:5]}")
    sP, nv, counts = check_structure(filled)
    cP, worst = check_copies(filled, collect(docs))
    P += sP + cP
    stub = render_stub()
    apath = os.path.join(docs, ANSWERS)
    if check:
        cur = open(apath, encoding="utf-8").read() if os.path.exists(apath) else ""
        if cur != stub:
            P.append(f"docs/{ANSWERS} ไม่ใช่หน้าชี้ทางปัจจุบัน (รัน python3 tools/sab_drills.py)")
    elif not P:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(filled)
        with open(apath, "w", encoding="utf-8") as fh:
            fh.write(stub)
    nkeys = len(KEY_RE.findall(filled))
    if not quiet:
        for p in P:
            print("  -", p)
        summary = (f"ภาคผนวก D: เปลี่ยนเงื่อนไข {nv} ข้อ · ทบทวนสะสม {counts[1]}/{counts[2]}/{counts[3]} ข้อ · "
                   f"data-key {nkeys} ช่อง · คล้ายแบบฝึกในบทสูงสุด {worst:.2f}")
        if P:
            print(summary, "· ไม่ผ่าน ✗")
        else:
            print(summary, "· ผ่าน ✓" if check else f"· เขียน docs/{TARGET} + docs/{ANSWERS} ✓")
    return P


def selftest():
    import tempfile
    head, tail = B.shell()

    def item(iid, vary=True, hint2=True, ans_first="<strong>สรุป</strong>", diag="ถ้าได้ 2 แปลว่าลืม", key="drills.x"):
        chg = '<p><strong>เปลี่ยนจากตัวอย่างในบท 1:</strong> หนึ่งข้อ</p>' if vary else '<p>ทบทวน</p>'
        h2 = '<details class="hint"><summary>ขั้น 2</summary><p>ก</p></details>' if hint2 else ""
        return (f'<li id="{iid}">{chg}<p>โจทย์ที่ไม่เหมือนใคร {iid} <span data-key="{key}"></span></p>'
                f'<details class="hint"><summary>คำใบ้</summary><p>ข</p>{h2}</details>'
                f'<details class="ans"><summary>เฉลย</summary><p>{ans_first}</p><p>ขั้น</p><p>{diag}</p></details></li>')
    good = [item(f"v{i}") for i in range(1, 19)]
    revs = "".join(f'<h3 id="review{n}">ท</h3><ol>' + "".join(item(f"r{n}-{j}", False) for j in range(1, 5)) + "</ol>"
                   for n in (1, 2, 3))
    lad = '<h2 id="ladder">บ</h2><table><tr><th>ข</th></tr>' + "<tr><td>1</td></tr>" * 4 + "</table>"
    chapter = (head + '<div class="bx bg"><div class="bt">✍️ ลองทำเอง</div><ol><li>คัดลอกข้อนี้มาทั้งข้อเลยนะ '
               'ซื้อ BTC หนึ่งเหรียญที่ 100,000 คู่กับขายสัญญา 1 BTC ที่ 103,000 ถือจนวันหมดอายุ ได้เท่าไร'
               '<details class="ans"><summary>เฉลย</summary><p>3,000</p></details></li></ol></div>' + tail)
    copied = ('<li id="v19"><p><strong>เปลี่ยนจากตัวอย่างในบท 0:</strong> ไม่มี</p><p>คัดลอกข้อนี้มาทั้งข้อเลยนะ '
              'ซื้อ BTC หนึ่งเหรียญที่ 100,000 คู่กับขายสัญญา 1 BTC ที่ 103,000 ถือจนวันหมดอายุ ได้เท่าไร</p>'
              '<details class="hint"><summary>ก</summary><p>ก</p><details class="hint"><summary>ข</summary><p>ข</p>'
              '</details></details><details class="ans"><summary>เฉลย</summary><p><strong>ส</strong></p><p>ข</p>'
              '<p>ถ้าได้ 1 แปลว่า</p></details></li>')
    bad = [item("v1", hint2=False), item("v2", ans_first="ไม่มีข้อสรุป"), item("v3", diag="ไม่มีบรรทัดวินิจฉัย"),
           item("v4", vary=False), item("v5", key="drills.ไม่มี")] + [item(f"v{i}") for i in range(6, 19)] + [copied]
    expect = ["v1: ไม่มีคำใบ้สองระดับ", "v2: บรรทัดแรกของเฉลย", "v3: เฉลยไม่มีบรรทัด", "v4: บรรทัดแรกต้องเป็น",
              "drills.ไม่มี", "v19: คล้ายแบบฝึกข้อ 1 ของบท 0", "ไม่ตรง JSON"]
    ok = True
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, "fig.json")
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump({"drills": {"x": -1234.5}}, fh)
        open(os.path.join(d, "sab-part0.html"), "w", encoding="utf-8").write(chapter)
        open(os.path.join(d, TARGET), "w", encoding="utf-8").write(head + "<ol>" + "".join(good) + "</ol>" + revs + lad + tail)
        if run(False, d, fp, quiet=True):
            ok = False
            print("selftest ล้ม: หน้าที่ถูกต้องถูกฟ้อง →", run(False, d, fp, quiet=True))
        page = open(os.path.join(d, TARGET), encoding="utf-8").read()
        if "−1,234.5</span>" not in page or run(True, d, fp, quiet=True):
            ok = False
            print("selftest ล้ม: เติมตัวเลข/หน้าชี้ทาง →", run(True, d, fp, quiet=True))
        open(os.path.join(d, TARGET), "w", encoding="utf-8").write(
            head + "<ol>" + "".join(bad).replace('data-key="drills.x"></span>', 'data-key="drills.x">9</span>', 1)
            + "</ol>" + revs + lad + tail)
        got = run(True, d, fp, quiet=True)
        for e in expect:
            if not any(e in p for p in got):
                ok = False
                print(f"selftest ล้ม: ไม่จับ {e!r} →", got)
    print("selftest", "ผ่าน ✓ (เติมตัวเลข · คำใบ้สองระดับ · ข้อสรุป · ถ้าได้ · เปลี่ยนจาก · คีย์หาย · คัดลอกจากบท)"
          if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    args = sys.argv[1:]
    if any(x not in ("--check", "--selftest") for x in args):
        print(__doc__)
        sys.exit(2)
    if args == ["--selftest"]:
        sys.exit(selftest())
    sys.exit(1 if run("--check" in args) else 0)
