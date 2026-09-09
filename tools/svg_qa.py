#!/usr/bin/env python3
"""ตรวจภาพ inline SVG ทั้งคลังตามกฎใน references/visual-guide.md
  · มี role="img" และ aria-label (คำบรรยายภาพสำหรับ PDF/screen reader)
  · มี viewBox และไม่ hardcode width/height เป็น px
  · <text> ทุกตัวใช้ฟอนต์ Sarabun (มี font-family ที่มี Sarabun หรือสืบทอดจาก <g> ครอบ)
  · ภาพที่มี ≥ 2 สีเส้นหลัก (stroke-width ≥ 2) ต้องมี legend หรือป้ายสีในภาพ
ใช้:  python3 tools/svg_qa.py            → รายงาน (exit 1 ถ้ามี ❌)
      python3 tools/svg_qa.py <ชื่อบท>   → เฉพาะไฟล์
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
INK = {"#374151", "#6b7280", "#9ca3af", "#cbd5e1", "#e5e7eb", "#f3f4f6", "#111827", "#4b5563", "#fff", "#ffffff", "none", "#d1d5db", "#e2e8f0"}


def check_svg(svg):
    issues = []
    head = svg[:svg.find(">") + 1]
    if 'role="img"' not in head: issues.append("ไม่มี role=\"img\"")
    if "aria-label=" not in head: issues.append("ไม่มี aria-label")
    if "viewBox=" not in head: issues.append("ไม่มี viewBox")
    if re.search(r'\s(width|height)="\d+(px)?"', head): issues.append("hardcode width/height")
    texts = re.findall(r"<text\b[^>]*>", svg)
    inherit = bool(re.search(r"<g\b[^>]*font-family=\"[^\"]*Sarabun", svg)) or "font-family:Sarabun" in svg
    bad_font = [t for t in texts if "Sarabun" not in t] if not inherit else []
    if texts and bad_font and len(bad_font) == len(texts): issues.append(f"<text> {len(bad_font)} ตัวไม่ระบุฟอนต์ Sarabun")
    # ซีรีส์: เส้นหลักหนา ≥ 2 สีต่างกัน → ต้องมี legend (เส้นสั้น + ข้อความ) หรือป้ายสีเดียวกับเส้น
    series = set()
    for m in re.finditer(r"<(?:path|polyline|line)\b[^>]*>", svg):
        tag = m.group(0)
        sw = re.search(r'stroke-width="([\d.]+)"', tag); st = re.search(r'stroke="([^"]+)"', tag)
        if sw and st and float(sw.group(1)) >= 2 and st.group(1).lower() not in INK and "dasharray" not in tag:
            series.add(st.group(1).lower())
    if len(series) >= 2 and 'data-legend="per-panel"' not in head:
        fills = {m.group(1).lower() for m in re.finditer(r'<text\b[^>]*fill="([^"]+)"', svg)}
        # legend swatch = เส้นสั้น (≤ 30px) หรือ rect เล็กสีเดียวกับซีรีส์
        for m in re.finditer(r'<line\b[^>]*>', svg):
            tag = m.group(0); c = re.search(r'stroke="([^"]+)"', tag)
            xs = re.findall(r'x[12]="([\d.]+)"', tag)
            if c and len(xs) == 2 and abs(float(xs[0]) - float(xs[1])) <= 30: fills.add(c.group(1).lower())
        for m in re.finditer(r'<rect\b[^>]*>', svg):
            tag = m.group(0); c = re.search(r'fill="([^"]+)"', tag); wd = re.search(r'width="([\d.]+)"', tag)
            if c and wd and float(wd.group(1)) <= 30: fills.add(c.group(1).lower())
        def hue(hx):
            hx = hx.lstrip("#")
            if len(hx) == 3: hx = "".join(ch * 2 for ch in hx)
            try: r, g, b = (int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4))
            except ValueError: return None
            mx, mn = max(r, g, b), min(r, g, b)
            if mx - mn < 0.15: return None          # เทา/หมึก ไม่นับเป็นสีซีรีส์
            d = mx - mn
            h = (60 * ((g - b) / d) % 360) if mx == r else (60 * ((b - r) / d) + 120) if mx == g else (60 * ((r - g) / d) + 240)
            return h
        def same_family(c1, c2):
            h1, h2 = hue(c1), hue(c2)
            return h1 is not None and h2 is not None and min(abs(h1 - h2), 360 - abs(h1 - h2)) <= 22
        labelled = sum(1 for c in series if any(same_family(c, fcol) for fcol in fills))
        # เส้นเดียวที่ระบายสีตามเครื่องหมาย (เขียว = กำไร · แดง = ขาดทุน) ไม่ใช่สองซีรีส์
        if series <= {"#16a34a", "#dc2626", "#15803d", "#b91c1c"} and re.search(r"Payoff|P/L|P&amp;L|กำไร|ขาดทุน|Profit", svg):
            labelled = len(series)
        if labelled < len(series):
            issues.append(f"มี {len(series)} สีเส้นหลัก แต่ป้ายสีตรงกันแค่ {labelled} — ต้องมี legend/ป้ายทุกซีรีส์")
    return issues


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    files = [os.path.join(DOCS, f + ".html") for f in only] if only else sorted(glob.glob(os.path.join(DOCS, "*.html")))
    n_svg = bad = 0
    for f in files:
        s = open(f, encoding="utf-8").read()
        for i, m in enumerate(re.finditer(r"<svg\b.*?</svg>", s, re.S), 1):
            if len(m.group(0)) < 200: continue   # ไอคอนตกแต่ง
            n_svg += 1
            iss = check_svg(m.group(0))
            if iss:
                bad += 1
                lab = re.search(r'aria-label="([^"]{0,50})', m.group(0))
                print(f"❌ {os.path.basename(f)} · svg #{i} ({lab.group(1) if lab else '?'}…): " + " · ".join(iss))
    print(f"\nตรวจ SVG {n_svg} ชิ้นใน {len(files)} ไฟล์ · มีปัญหา {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
