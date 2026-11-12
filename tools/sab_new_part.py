#!/usr/bin/env python3
"""สร้างไฟล์บทใหม่ของ "Stat Arb for Non Quant · เล่ม 1" จากเปลือกกลาง tools/sab_shell/

เปลือก (CSS · palette · Thai line-break script) เก็บที่เดียวใน tools/sab_shell/head.html + tail.html
เพื่อไม่ให้ความต่างเล็ก ๆ สะสมข้ามบท — ห้ามแก้ Thai line-break script ด้วยมือ (กฎ style guide)

    python3 tools/sab_new_part.py part4 "หัวข้อรอง" "คำโปรย"     # เขียน docs/sab-part4.html (ปฏิเสธถ้ามีไฟล์แล้ว)
    python3 tools/sab_new_part.py index "หน้ารวมเล่ม" "คำโปรย"     # slug ใดก็ได้ → docs/sab-<slug>.html
    python3 tools/sab_new_part.py --sync                          # เขียนหัว/ท้ายใหม่ให้ docs/sab-*.html ทุกไฟล์เมื่อเปลือกเปลี่ยน

ต่างจาก nq_new_part.py: เขียนไฟล์เอง (ไม่พิมพ์ออก stdout จึงไม่เสี่ยง `>` ทับเนื้อบท) · ใช้ slug ที่รับมา ·
เปลือกเก็บที่เดียวและ --sync ได้
"""

import glob
import html as htmllib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL = os.path.join(ROOT, "tools", "sab_shell")
DOCS = os.path.join(ROOT, "docs")
BOOK = "Stat Arb for Non Quant"
BOOK_TH = "เชือกที่ผูกสองราคา"
BODY_MARK = "<!--BODY-->"
TAIL_MARK = "<!-- ═══════════════ Thai line-break script"


def shell():
    with open(os.path.join(SHELL, "head.html"), encoding="utf-8") as fh:
        head = fh.read()
    with open(os.path.join(SHELL, "tail.html"), encoding="utf-8") as fh:
        tail = fh.read()
    return head, tail


def skeleton(slug, sub, desc):
    head, tail = shell()
    esc = htmllib.escape
    head = head.replace("{{TITLE}}", esc(f"{BOOK} — {sub}"), 1)
    cover = f'''

<!-- ═══════════════ COVER ═══════════════ -->
<div class="cover">
<h1>{BOOK} · เล่ม 1 — {BOOK_TH}</h1>
<div class="sub">{esc(sub)}</div>
<div class="desc">{esc(desc)}</div>
</div>

{BODY_MARK}

'''
    return head + cover + tail


def target(slug):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        sys.exit(f"slug ต้องเป็น a-z 0-9 - เท่านั้น: {slug!r}")
    return os.path.join(DOCS, f"sab-{slug}.html")


def create(slug, sub, desc):
    path = target(slug)
    if os.path.exists(path):
        sys.exit(f"ปฏิเสธ: {os.path.relpath(path, ROOT)} มีอยู่แล้ว (ใช้ --sync ถ้าต้องการอัปเดตเปลือก)")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(skeleton(slug, sub, desc))
    print(f"สร้าง {os.path.relpath(path, ROOT)}")


def sync():
    """แทนหัว (ถึง <body>) และท้าย (ตั้งแต่ Thai script) ด้วยเปลือกปัจจุบัน · เก็บ <title> เดิมของแต่ละไฟล์"""
    head, tail = shell()
    changed = 0
    for path in sorted(glob.glob(os.path.join(DOCS, "sab-*.html"))):
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        if "<body>" not in src or TAIL_MARK not in src:
            print(f"ข้าม (ไม่ใช่เปลือก sab): {os.path.basename(path)}")
            continue
        m = re.search(r"<title>(.*?)</title>", src, re.S)
        title = m.group(1) if m else BOOK
        body = src[src.index("<body>") + len("<body>"):src.rindex(TAIL_MARK)]
        new = head.replace("{{TITLE}}", title, 1) + body + tail
        if new != src:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            changed += 1
            print(f"อัปเดตเปลือก {os.path.basename(path)}")
    print(f"--sync: เปลี่ยน {changed} ไฟล์")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--sync"]:
        sync()
    elif len(args) == 3 and not args[0].startswith("-"):
        create(*args)
    else:
        print(__doc__)
        sys.exit(1)
