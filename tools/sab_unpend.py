#!/usr/bin/env python3
"""ปลดป้าย data-pending เมื่อไฟล์ที่ลิงก์ถึงมีอยู่แล้ว (เฟส 4–5 · ก่อน sab_qa.py --final)

กล่อง/ลิงก์ที่ชี้ไฟล์ซึ่งยังไม่มีถูกห่อด้วย data-pending ระหว่างเขียน · สคริปต์นี้ตรวจทุกหน้า docs/sab-*.html
ถ้าทุก href / <code>ไฟล์</code> ในองค์ประกอบนั้นมีไฟล์จริงแล้ว ลบ attribute data-pending และข้อความรอ เช่น "(มาในเฟสเครื่องมือ)"
data-pending-part (ช่องเทาในบัตรธรรมชาติ) ไม่แตะ

    python3 tools/sab_unpend.py            # ปลดและรายงานที่ยังรอ
    python3 tools/sab_unpend.py --check    # รายงานอย่างเดียว
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
OPEN_RE = re.compile(r'<(\w+)\b([^>]*\sdata-pending(?:="[^"]*")?)(?=[\s>/])([^>]*)>')
NOTES = [r"\s*\((?:มา|รอ)[^()]{0,40}\)", r"\s*\(ยังไม่มีไฟล์\)"]


def element_end(html, start, tag):
    depth, i = 0, start
    for m in re.finditer(rf"<(/?){tag}\b[^>]*>", html[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.end()
    return len(html)


def refs(seg):
    out = set(re.findall(r'href="([^"#:?]+\.(?:html|csv|xlsx|pdf))', seg))
    out |= set(re.findall(r"<code>([\w./-]+\.(?:html|csv|xlsx))</code>", seg))
    if not out:
        m = re.match(r"<code[^>]*>([\w./-]+\.(?:html|csv|xlsx))</code>", seg)
        if m:
            out.add(m.group(1))
    return out


def process(html):
    pending, i = [], 0
    while True:
        m = OPEN_RE.search(html, i)
        if not m:
            break
        if "data-pending-part" in m.group(0):
            i = m.end()
            continue
        end = element_end(html, m.start(), m.group(1))
        seg = html[m.start():end]
        missing = [r for r in refs(seg) if not os.path.exists(os.path.join(DOCS, r))]
        if missing:
            pending.append(", ".join(missing))
            i = end
            continue
        new_open = re.sub(r'\sdata-pending(?:="[^"]*")?', "", m.group(0), count=1)
        body = seg[len(m.group(0)):]
        for n in NOTES:
            body = re.sub(n, "", body)
        html = html[:m.start()] + new_open + body + html[end:]
        i = m.start() + len(new_open)
    return html, pending


if __name__ == "__main__":
    check = "--check" in sys.argv
    left = 0
    for path in sorted(glob.glob(os.path.join(DOCS, "sab-*.html"))):
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        new, pending = process(html)
        for p in pending:
            print(f"  รอ: {os.path.basename(path)} → {p}")
        left += len(pending)
        if new != html and not check:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
            print(f"ปลด data-pending ใน {os.path.basename(path)}")
    print(f"ยังรอ {left} จุด")
    sys.exit(1 if left else 0)
