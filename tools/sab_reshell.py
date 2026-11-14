#!/usr/bin/env python3
"""แทนบล็อก <style>…</style> ใน <head> ของทุกหน้า docs/sab-*.html ด้วยของเปลือก tools/sab_shell/head.html

ใช้เมื่อ CSS ของเปลือกเปลี่ยน (แผน 14.6) · แตะเฉพาะบล็อก <style> แรกที่อยู่ก่อน <body> — ไม่แตะ <title> · แท็ก <body …>
(หน้า v2 มี data-tpl="2") · เนื้อบท · <style> เฉพาะหน้าที่อยู่ใน body · Thai line-break script

    python3 tools/sab_reshell.py            # เขียนทับหน้าที่ CSS ไม่ตรงเปลือก
    python3 tools/sab_reshell.py --check    # ไม่เขียน: รายงานหน้าที่ไม่ตรง (exit 1 ถ้ามี)

ต่างจาก `sab_new_part.py --sync` (แทนทั้งหัวถึง <body> และท้ายไฟล์) — ตัวนี้เปลี่ยนเฉพาะ CSS
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
HEAD = os.path.join(ROOT, "tools", "sab_shell", "head.html")
STYLE_RE = re.compile(r"<style>.*?</style>", re.S)


def shell_style():
    with open(HEAD, encoding="utf-8") as fh:
        m = STYLE_RE.search(fh.read())
    if not m:
        sys.exit("ไม่พบ <style>…</style> ใน tools/sab_shell/head.html")
    return m.group(0)


def reshell(html, style):
    """คืน html ใหม่ หรือ None ถ้าหน้านี้ไม่มีบล็อก <style> ใน <head>"""
    body = re.search(r"<body\b", html)
    m = STYLE_RE.search(html, 0, body.start() if body else len(html))
    if not m:
        return None
    return html[:m.start()] + style + html[m.end():]


def run(docs=DOCS, write=True):
    style = shell_style()
    differ, skipped, n = [], [], 0
    for path in sorted(glob.glob(os.path.join(docs, "sab-*.html"))):
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        new = reshell(src, style)
        n += 1
        if new is None:
            skipped.append(name)
        elif new != src:
            differ.append(name)
            if write:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
    return n, differ, skipped


if __name__ == "__main__":
    a = sys.argv[1:]
    if a not in ([], ["--check"]):
        print(__doc__)
        sys.exit(2)
    n, differ, skipped = run(write=not a)
    for name in skipped:
        print(f"  - ข้าม (ไม่มี <style> ใน <head>): {name}")
    if a:
        for name in differ:
            print(f"  - CSS ไม่ตรงเปลือก: {name}")
        print(f"ตรวจ {n} หน้า · " + (f"ไม่ตรงเปลือก {len(differ)} หน้า — รัน python3 tools/sab_reshell.py"
                                    if differ else "CSS ตรงกับเปลือกทุกหน้า ✓"))
        sys.exit(1 if differ or skipped else 0)
    print(f"ตรวจ {n} หน้า · เขียน CSS ใหม่ {len(differ)} หน้า" + (": " + ", ".join(differ) if differ else ""))
    sys.exit(1 if skipped else 0)
