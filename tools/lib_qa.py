#!/usr/bin/env python3
"""QA ทั้งคลัง docs/*.html — รันก่อน commit ทุกครั้ง

ตรวจ (ล้มเหลว = exit 1):
  1. tag balance ของ div/p/ul/ol/li/details (ห้ามมีแท็กปิดเกินหรือแท็กเปิดค้าง)
  2. บล็อก "📖 อ่านสูตรว่า" (<p class="read">):
       - ต้องเปิดด้วย <strong>📖 อ่านสูตรว่า:</strong>
       - ต้องอยู่ถัดจาก </div> (กล่อง .fm) หรือ </p> ที่มีสูตร inline
       - ห้ามมี <br> / <ul> / <ol> ข้างใน
       - ไฟล์ที่มี .read ต้องมี CSS .read{…}
  3. ลิงก์ภายในทุกตัว (href ที่ไม่ใช่ http/mailto/#top) ต้องชี้ไฟล์ที่มีจริง
     และ anchor (#id) ต้องมีในไฟล์ปลายทาง
เตือน (ไม่ล้มเหลว):
  - ไฟล์เนื้อหาที่ไม่มี banner 🧭 เส้นทางอ่าน
  - ไฟล์ที่มี .fm แต่ไม่มี script ตัดคำไทย (Intl.Segmenter)
ใช้: python3 tools/lib_qa.py [ไฟล์...]   (ไม่ระบุ = ทุกไฟล์ใน docs/)
"""
import glob
import html.parser
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
BLOCK_TAGS = ("div", "p", "ul", "ol", "li", "details")
SKIP_BANNER = ("index.html", "nq-index.html", "notation.html", "nq-appendix-map.html",
               "nq-appendix-glossary.html", "quant-tool-critique-framework.html")


class TagParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.ids = [], [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag in BLOCK_TAGS:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            if self.stack and self.stack[-1][0] == tag:
                self.stack.pop()
            else:
                self.errors.append(f"</{tag}> เกินที่บรรทัด {self.getpos()[0]}")


def ids_of(path, cache={}):
    if path not in cache:
        p = TagParser()
        p.feed(open(path, encoding="utf-8").read())
        cache[path] = p.ids
    return cache[path]


def check(path):
    src = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    errs, warns = [], []

    p = TagParser()
    p.feed(src)
    errs += p.errors
    errs += [f"<{t}> เปิดค้างตั้งแต่บรรทัด {ln}" for t, ln in p.stack if t in ("div", "p", "details")]

    reads = list(re.finditer(r'<p class="read">.*?</p>', src, re.S))
    if reads and ".read{" not in src:
        errs.append("มี <p class=\"read\"> แต่ไม่มี CSS .read{}")
    for m in reads:
        ln = src[:m.start()].count("\n") + 1
        body = m.group(0)
        if not body.startswith('<p class="read"><strong>📖 อ่านสูตรว่า:</strong>'):
            errs.append(f"บรรทัด {ln}: บล็อก 📖 ไม่ได้เปิดด้วย <strong>📖 อ่านสูตรว่า:</strong>")
        if re.search(r"<br|<ul|<ol", body):
            errs.append(f"บรรทัด {ln}: บล็อก 📖 มี <br>/<ul>/<ol>")
        before = src[:m.start()].rstrip()
        if not (before.endswith("</div>") or before.endswith("</p>")):
            errs.append(f"บรรทัด {ln}: บล็อก 📖 ไม่ได้อยู่ถัดจากกล่องสูตร")

    for m in re.finditer(r'href="([^"]+)"', src):
        h = m.group(1)
        if h.startswith(("http", "mailto:", "#top")) or h == "#":
            continue
        fn, _, anc = h.partition("#")
        target = os.path.join(DOCS, fn) if fn else path
        ln = src[:m.start()].count("\n") + 1
        if not os.path.exists(target):
            errs.append(f"บรรทัด {ln}: ลิงก์ไปไฟล์ที่ไม่มี {h}")
            continue
        if anc and anc not in ids_of(target):
            errs.append(f"บรรทัด {ln}: anchor ไม่มีในปลายทาง {h}")

    if name not in SKIP_BANNER and "🧭" not in src and 'class="fm"' in src:
        warns.append("ไม่มี banner 🧭 เส้นทางอ่าน")
    if 'class="fm"' in src and "Intl.Segmenter" not in src:
        warns.append("ไม่มี script ตัดคำไทย")
    return errs, warns


def main(argv):
    files = [os.path.join(DOCS, a if a.endswith(".html") else a + ".html") for a in argv] \
        or sorted(glob.glob(os.path.join(DOCS, "*.html")))
    total_err = 0
    n_read = 0
    for f in files:
        errs, warns = check(f)
        n_read += open(f, encoding="utf-8").read().count('class="read"')
        total_err += len(errs)
        for e in errs:
            print(f"❌ {os.path.basename(f)}: {e}")
        for w in warns:
            print(f"⚠️  {os.path.basename(f)}: {w}")
    print(f"ตรวจ {len(files)} ไฟล์ · บล็อก 📖 {n_read} · ข้อผิดพลาด {total_err}")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
