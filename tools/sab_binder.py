#!/usr/bin/env python3
"""รวมใบงาน .sheet ทุกบท → docs/sab-appendix-worksheets.html (ภาคผนวก E · แฟ้มกลยุทธ์ของฉัน) + CSV

ใบงานเขียนครั้งเดียวในบทตามสัญญา markup (แผน 6.3) แล้วออกได้สองฉบับจาก markup เดียว
  ฉบับมิน  : ช่อง <td data-key="…"> เติมค่าจาก docs/sab-figures.json (ตัวเลขในใบของมินขัดกับ JSON ไม่ได้)
  ฉบับเปล่า: ช่อง data-key ว่าง ให้ผู้อ่านกรอกเอง
ใบที่มี data-csv="ชื่อ.csv" ได้ไฟล์ docs/sab-worksheets/ชื่อ.csv (utf-8-sig ให้ Excel อ่านไทยได้) จากหัวตารางใบนั้น

    python3 tools/sab_binder.py            # เขียนภาคผนวก E (ฉบับเปล่าก่อน ตามด้วยฉบับมิน) + CSV
    python3 tools/sab_binder.py --check    # ตรวจอย่างเดียว: เกณฑ์ผ่าน 3 ข้อ · data-from/to ชี้ใบที่มีจริง · data-key มีใน JSON
    python3 tools/sab_binder.py --selftest
"""

import csv
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sab_book as B  # noqa: E402

TARGET = "sab-appendix-worksheets.html"
CSV_DIR = "sab-worksheets"
OPEN_RE = re.compile(r'<div\b[^>]*class="[^"]*\bsheet\b[^"]*"[^>]*>')


def sheet_blocks(html):
    """คืน [(attrs_html, outer_html)] ของ div.sheet ทุกใบ (นับชั้น div)"""
    out, i = [], 0
    while True:
        m = OPEN_RE.search(html, i)
        if not m:
            return out
        depth = 1
        for t in re.finditer(r"<(/?)div\b[^>]*>", html[m.end():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = m.end() + t.end()
                break
        else:
            end = len(html)
        out.append((m.group(0), html[m.start():end]))
        i = end


def attr(a, name):
    m = re.search(name + r'="([^"]*)"', a)
    return m.group(1) if m else None


def collect(docs=B.DOCS):
    sheets = []
    for path in B.chapter_files(docs):
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        for a, outer in sheet_blocks(html):
            csvname = attr(a, "data-csv")
            if not csvname:                                   # ใบที่อ้างไฟล์ sab-worksheets/X.csv ในเนื้อ → ใช้ชื่อนั้น
                m = re.search(r"sab-worksheets/([\w-]+\.csv)", outer)
                csvname = m.group(1) if m else None
            sheets.append({"บท": B.part_no(path), "id": attr(a, "data-sheet") or "?", "from": attr(a, "data-from") or "",
                           "to": attr(a, "data-to") or "", "csv": csvname, "html": outer})
    return sheets


def fill(outer, fig, blank):
    def sub(m):
        open_tag, key = m.group(1), m.group(2)
        if blank:
            return f"{open_tag}</td>"
        try:
            return f"{open_tag}{B.fmt(B.get_path(fig, key))}</td>"
        except KeyError:
            return f"{open_tag}??</td>"
    return re.sub(r'(<td\b[^>]*\bdata-key="([^"]+)"[^>]*>).*?</td>', sub, outer, flags=re.S)


def check(sheets, fig):
    P = []
    ids = {s["id"] for s in sheets}
    for s in sheets:
        tag = f"บท {s['บท']} ใบ {s['id']}"
        pas = re.search(r'<ol class="pass">(.*?)</ol>', s["html"], re.S)
        if not pas or len(re.findall(r"<li\b", pas.group(1))) != 3:
            P.append(f"{tag}: ต้องมีเกณฑ์ผ่าน 3 ข้อ")
        for ref in filter(None, re.split(r"[,\s]+", s["from"] + "," + s["to"])):
            if ref not in ids and not ref.startswith("ภผ"):
                P.append(f"{tag}: data-from/to ชี้ใบ {ref} ที่ยังไม่มี")
        for k in re.findall(r'data-key="([^"]+)"', s["html"]):
            try:
                B.get_path(fig, k)
            except KeyError:
                P.append(f"{tag}: data-key {k!r} ไม่มีใน JSON")
    return P


def write_csv(sheets, docs):
    os.makedirs(os.path.join(docs, CSV_DIR), exist_ok=True)
    made = []
    for s in sheets:
        if not s["csv"]:
            continue
        heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th\b[^>]*>(.*?)</th>", s["html"], re.S)]
        path = os.path.join(docs, CSV_DIR, s["csv"])
        with open(path, "w", encoding="utf-8-sig", newline="") as fh:
            csv.writer(fh).writerow(heads or ["ช่อง", "ค่าของฉัน"])
        made.append(s["csv"])
    return made


def render(sheets, fig):
    def section(blank):
        out = []
        for s in sorted(sheets, key=lambda s: (s["บท"], s["id"])):
            body = fill(s["html"], fig, blank)
            out.append(f'<div class="sheet-page"><p class="nw" style="font-size:.85em;color:#64748b">'
                       f'จากบท {s["บท"]} — <a href="{B.PREFIX}-part{s["บท"]}.html">{B.TITLES.get(s["บท"], "")}</a></p>\n{body}</div>')
        return "\n".join(out)
    body = f'''
<div class="bx bb" style="font-size:.92em"><div class="bt">🧭 วิธีใช้หน้านี้</div>
<p>ใบงาน {len(sheets)} ใบจากทุกบท · ส่วนแรกเป็นฉบับเปล่าให้พิมพ์กรอก (หนึ่งใบหนึ่งหน้า) ส่วนที่สองเป็นฉบับที่มินกรอกไว้
ใช้เทียบหลังทำเสร็จ · ตัวเลขในใบของมินดึงจากชุดตัวเลขเดียวกับในบท จึงตรงกันเสมอ</p></div>
<style>@media print{{.sheet-page{{page-break-after:always}}}}</style>
<h2 id="blank">ฉบับเปล่า — กรอกเอง</h2>
{section(True)}
<h2 id="filled">ฉบับที่มินกรอก — ใช้เทียบ</h2>
{section(False)}
<div class="bx ba"><div class="bt">📖 หมายเหตุ</div><p>หน้านี้สร้างด้วย <code>tools/sab_binder.py</code> จากใบงานในบทโดยตรง</p></div>
'''
    return B.page("ภาคผนวก E: แฟ้มกลยุทธ์ของฉัน", "ภาคผนวก E — แฟ้มกลยุทธ์ของฉัน",
                  "ใบงานทุกใบ ฉบับเปล่าและฉบับที่มินกรอก จาก markup เดียว", body)


def load_fig(docs):
    p = os.path.join(docs, "sab-figures.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def selftest():
    head, tail = B.shell()
    sheet = ('<div class="bx sheet" data-sheet="04" data-from="00" data-to="05" data-csv="buffer.csv">'
             '<div class="bt">🛠 ใบ 04</div><table><tr><th>ช่อง</th><th>ค่า</th></tr>'
             '<tr><td>ต้องโอน</td><td data-key="ch04.ต้องโอน">11,220</td></tr>'
             '<tr><td>equity</td><td data-key="ch04.equity">x</td></tr></table>'
             '<ol class="pass"><li>1</li><li>2</li><li>3</li></ol><div><p>ซ้อน</p></div></div>')
    bad = '<div class="bx sheet" data-sheet="05" data-from="99"><ol class="pass"><li>1</li></ol><td data-key="ไม่มี"></td></div>'
    fig = {"ch04": {"ต้องโอน": 11220, "equity": -200}}
    ok = True
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "sab-part4.html"), "w", encoding="utf-8").write(head + sheet + tail)
        open(os.path.join(d, "sab-part10.html"), "w", encoding="utf-8").write(head + bad + tail)
        sheets = collect(d)
        probs = check(sheets, fig)
        made = write_csv(sheets, d)
        with open(os.path.join(d, CSV_DIR, "buffer.csv"), encoding="utf-8-sig") as fh:
            heads = fh.read().strip()
    if [s["id"] for s in sheets] != ["04", "05"] or "ซ้อน" not in sheets[0]["html"]:
        ok = False
        print("selftest ล้ม: แยกใบ", [s["id"] for s in sheets])
    filled, blank = fill(sheets[0]["html"], fig, False), fill(sheets[0]["html"], fig, True)
    if "11,220" not in filled or "−200" not in filled or "11,220" in blank:
        ok = False
        print("selftest ล้ม: เติมค่า", filled, blank)
    for e in ("ใบ 05: ต้องมีเกณฑ์ผ่าน", "ชี้ใบ 99", "'ไม่มี'"):
        if not any(e in p for p in probs):
            ok = False
            print("selftest ล้ม: ไม่จับ", e, probs)
    if made != ["buffer.csv"] or heads != "ช่อง,ค่า":
        ok = False
        print("selftest ล้ม: CSV", made, heads)
    print("selftest", "ผ่าน ✓ (แยกใบแบบนับชั้น · ฉบับมิน/เปล่าจาก markup เดียว · ตรวจเกณฑ์/ลิงก์ใบ/key · CSV BOM)" if ok else "ไม่ผ่าน ✗")
    return 0 if ok else 1


if __name__ == "__main__":
    if any(x not in ['--check', '--selftest'] for x in sys.argv[1:]):
        print(__doc__)
        sys.exit(2)
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(selftest())
    sheets, fig = collect(), load_fig(B.DOCS)
    probs = check(sheets, fig)
    for p in probs:
        print("  -", p)
    if "--check" in a or not sheets:
        print(f"ใบงาน {len(sheets)} ใบ · ปัญหา {len(probs)} ข้อ")
        sys.exit(1 if probs else 0)
    with open(os.path.join(B.DOCS, TARGET), "w", encoding="utf-8") as fh:
        fh.write(render(sheets, fig))
    made = write_csv(sheets, B.DOCS)
    print(f"เขียน docs/{TARGET} · {len(sheets)} ใบ · CSV {len(made)} ไฟล์")
    sys.exit(1 if probs else 0)
