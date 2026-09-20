#!/usr/bin/env python3
"""ตรวจความอ่านง่ายของร้อยแก้วไทยทั้งคลัง — style guide หมวด C

กฎที่ตรวจ (ทั้งหมดมาจาก references/style-guide.md):
  1. ประโยค ≤ ~2 บรรทัดจอ
     "ประโยค" = ส่วนที่คั่นด้วย " · " ตามที่ style guide กำหนดไว้เอง
     เกณฑ์อักษรมาจากการวัดจริง: เรนเดอร์ด้วย Chromium ที่ความกว้าง body ของคลัง
     แล้วหารความสูงด้วย line-height ได้มัธยฐาน 81 อักษร/บรรทัด → 2 บรรทัด ≈ 162
  2. em-dash "—" ≤ 1 ตัวต่อประโยค (นับหลังตัดด้วย " · ")
  3. มี (1)(2)(3) ในประโยคเดียว = สัญญาณให้เปลี่ยนเป็น <ul>

ไม่ตรวจ: .fm (สูตร) · pre/code (โค้ด) · table · บล็อกที่มีบล็อกซ้อนข้างใน

ใช้:  python3 tools/prose_qa.py                  → รายงานทั้งคลัง
      python3 tools/prose_qa.py math-part9       → เจาะจงไฟล์
      python3 tools/prose_qa.py --list <ไฟล์>    → พิมพ์ประโยคที่ยาวเกินออกมาด้วย
      python3 tools/prose_qa.py --max N          → exit 1 ถ้ารวมเกิน N (ใช้กันถอยหลัง)
"""
import glob
import html.parser
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

CHARS_PER_LINE = 81      # วัดจริงจาก Chromium — ดู docstring
MAX_LINES = 2            # style guide หมวด C
LIMIT = CHARS_PER_LINE * MAX_LINES
SKIP_ANCESTORS = {"pre", "code", "table", "script", "style"}
SKIP_CLASSES = {"fm", "cap"}
NESTED = {"p", "li", "ul", "ol", "div", "table", "svg", "pre"}
# ฉบับเล่าเรื่องมีเป้าหมายต่างจากบทสอน — ประโยคยาวที่นั่นอาจเป็นความตั้งใจ
# ยังตรวจและรายงาน แต่แยกยอดออกมา ไม่นับรวมในเพดาน --max
NARRATIVE = re.compile(r"-narrative|^case-")


class Prose(html.parser.HTMLParser):
    """เก็บข้อความของ <p>/<li> ที่ไม่มีบล็อกซ้อนข้างใน และไม่ได้อยู่ในสูตร/โค้ด/ตาราง"""

    def __init__(self):
        super().__init__()
        self.stack = []          # (tag, classes)
        self.cur = None          # (tag, line, ชิ้นส่วนข้อความ)
        self.blocks = []

    def _skipping(self):
        return any(t in SKIP_ANCESTORS or (SKIP_CLASSES & c) for t, c in self.stack)

    def handle_starttag(self, tag, attrs):
        cls = set(dict(attrs).get("class", "").split())
        if self.cur and tag in NESTED:
            self.cur = None                      # มีบล็อกซ้อน — ทิ้ง ไปวัดตัวในแทน
        if tag in ("p", "li") and not self.cur and not self._skipping():
            self.cur = (tag, self.getpos()[0], [])
        self.stack.append((tag, cls))

    def handle_endtag(self, tag):
        if self.cur and tag == self.cur[0]:
            t = re.sub(r"\s+", " ", "".join(self.cur[2])).strip()
            if len(t) >= 20:
                self.blocks.append((self.cur[0], self.cur[1], t))
            self.cur = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.cur and not self._skipping():
            self.cur[2].append(data)


def sentences(text):
    """style guide: แต่ละส่วนที่คั่นด้วย ' · ' คือหนึ่งประโยค"""
    return [s.strip() for s in text.split(" · ") if s.strip()]


def check(path):
    src = open(path, encoding="utf-8").read()
    p = Prose()
    p.feed(src)
    long_, dash, enum = [], [], []
    for tag, line, text in p.blocks:
        for s in sentences(text):
            if len(s) > LIMIT:
                long_.append((line, len(s), s))
            if s.count("—") > 1:
                dash.append((line, s.count("—"), s))
            if re.search(r"\(1\).{0,200}\(2\).{0,200}\(3\)", s):
                enum.append((line, 0, s))
    return long_, dash, enum


def main(argv):
    show = "--list" in argv
    argv = [a for a in argv if a != "--list"]
    cap = None
    if "--max" in argv:
        i = argv.index("--max")
        cap = int(argv[i + 1])
        del argv[i:i + 2]

    files = [os.path.join(DOCS, a if a.endswith(".html") else a + ".html") for a in argv] \
        or sorted(glob.glob(os.path.join(DOCS, "*.html")))
    rows, tot = [], [0, 0, 0]
    for f in files:
        long_, dash, enum = check(f)
        if not (long_ or dash or enum):
            continue
        rows.append((len(long_) + len(dash) + len(enum), os.path.basename(f), long_, dash, enum))
        tot[0] += len(long_); tot[1] += len(dash); tot[2] += len(enum)

    rows.sort(reverse=True)
    teach = [r for r in rows if not NARRATIVE.search(r[1])]
    narr = [r for r in rows if NARRATIVE.search(r[1])]
    rows = teach + narr
    for n, name, long_, dash, enum in rows:
        bits = []
        if long_: bits.append(f"ยาวเกิน {len(long_)}")
        if dash: bits.append(f"em-dash ซ้อน {len(dash)}")
        if enum: bits.append(f"(1)(2)(3) {len(enum)}")
        print(f"{n:4d}  {name:<34} {' · '.join(bits)}")
        if show:
            for line, v, s in sorted(long_, key=lambda r: -r[1])[:8]:
                print(f"        บรรทัด {line:>5} · {v:>4} อักษร  {s[:96]}…")
            for line, v, s in dash[:4]:
                print(f"        บรรทัด {line:>5} · — {v} ตัว    {s[:96]}…")
            for line, _, s in enum[:4]:
                print(f"        บรรทัด {line:>5} · (1)(2)(3)  {s[:96]}…")

    total = sum(tot)
    n_teach = sum(r[0] for r in teach)
    n_narr = sum(r[0] for r in narr)
    print(f"\nตรวจ {len(files)} ไฟล์ · ประโยคยาวเกิน {LIMIT} อักษร (~{MAX_LINES} บรรทัด) {tot[0]} "
          f"· em-dash ซ้อน {tot[1]} · (1)(2)(3) ในประโยคเดียว {tot[2]} · รวม {total}")
    print(f"แยกตามชนิด: บทสอน {n_teach} · ฉบับเล่าเรื่อง {n_narr} (ไม่นับในเพดาน)")
    total = n_teach
    if cap is not None and total > cap:
        print(f"❌ เกินเพดานที่ตั้งไว้ {cap}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:      # ต่อท้ายด้วย head/less ได้โดยไม่ traceback
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
