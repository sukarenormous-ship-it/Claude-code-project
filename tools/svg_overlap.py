#!/usr/bin/env python3
"""หาข้อความที่ซ้อนทับกันในภาพ SVG ทุกชิ้นของคลัง — สาเหตุอันดับหนึ่งที่ทำให้กราฟ "อ่านไม่ออก"

คำนวณกรอบของข้อความแต่ละชิ้นจาก x, y, font-size, text-anchor และความกว้างต่ออักษร
(ค่าคงที่ชุดเดียวกับ tools/make_figures.py:text_width ซึ่ง fit จากการวัดจริงในเบราว์เซอร์)
แล้วรายงานคู่ที่กรอบทับกัน กับข้อความที่ล้นออกนอกกรอบภาพ

    python3 tools/svg_overlap.py            → ตรวจทั้งคลัง (exit 1 ถ้าพบ)
    python3 tools/svg_overlap.py pm-part3   → ตรวจเฉพาะไฟล์ที่ชื่อมีคำนี้
"""
import glob
import html as _html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")

_COMBINING = set("ัิีึืฺุู็่้๊๋์ํ๎")
_NARROW = set("ijltfrI.,:;!|'’ ")
_W_THAI, _W_NARROW, _W_LATIN, _W_SYM = 0.601, 0.293, 0.530, 0.404
PAD = 1.5          # ยอมให้ชิดกันได้เล็กน้อยก่อนนับว่าทับ (px)
MIN_OVERLAP = 6.0  # พื้นที่ทับซ้อนที่เล็กกว่านี้ถือว่าไม่กระทบการอ่าน (px²)
GRID_COL = "#e5e7eb"   # เส้นกริดจาง — ข้อความวางทับได้ ไม่กระทบการอ่าน
MIN_STROKE = 1.2       # เส้นที่บางกว่านี้ถือว่าไม่บังข้อความ
SHRINK = 2.0           # หดกรอบข้อความก่อนเทียบกับเส้น เพื่อให้เส้นที่แค่เฉียดขอบไม่ถูกนับ


def text_width(text, size):
    w = 0.0
    for ch in text:
        if ch in _COMBINING: continue
        if ch in _NARROW: w += _W_NARROW
        elif "฀" <= ch <= "๿": w += _W_THAI
        elif ch.isdigit() or ("a" <= ch <= "z") or ("A" <= ch <= "Z"): w += _W_LATIN
        else: w += _W_SYM
    return w * size


def _attr(tag, name, default=None):
    m = re.search(name + r'="([^"]*)"', tag)
    return m.group(1) if m else default


def texts_of(svg):
    """คืนรายการ (ข้อความ, x0, y0, x1, y1) ของ <text> ทุกชิ้น (ข้ามชิ้นที่หมุนหรือว่างเปล่า)"""
    out = []
    for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
        tag, body = m.group(1), m.group(2)
        if "transform" in tag: continue                      # ป้ายแกนที่หมุน 90° — ไม่ตรวจ
        txt = _html.unescape(re.sub(r"<[^>]+>", "", body)).strip()
        if not txt: continue
        try:
            x = float(_attr(tag, "x", "0")); y = float(_attr(tag, "y", "0"))
        except ValueError:
            continue
        size = float(_attr(tag, "font-size", "10"))
        anc = _attr(tag, "text-anchor", "start")
        w = text_width(txt, size)
        x0 = x - w if anc == "end" else (x - w / 2 if anc == "middle" else x)
        out.append((txt, x0, y - size * 0.78, x0 + w, y + size * 0.22, size))
    return out


def segments_of(svg):
    """คืนรายการเส้นตรง (x1, y1, x2, y2) ของเส้นข้อมูลทุกเส้น — ข้ามเส้นกริดจางและเส้นบางมาก"""
    segs = []
    for m in re.finditer(r"<(polyline|line|polygon)\b([^>]*)>", svg):
        kind, tag = m.group(1), m.group(2)
        col = (_attr(tag, "stroke") or "").lower()
        if col in ("", "none") or col == GRID_COL: continue
        try:
            if float(_attr(tag, "stroke-width", "1")) < MIN_STROKE: continue
        except ValueError:
            continue
        if kind == "line":
            try: segs.append(tuple(float(_attr(tag, k, "0")) for k in ("x1", "y1", "x2", "y2")))
            except ValueError: pass
            continue
        pts = []
        for pair in (_attr(tag, "points") or "").split():
            try:
                a, b = pair.split(","); pts.append((float(a), float(b)))
            except ValueError:
                pass
        segs += [(p[0], p[1], q[0], q[1]) for p, q in zip(pts[:-1], pts[1:])]
    return segs


def _seg_hits_box(seg, box):
    """เส้นตรงพาดผ่านกรอบข้อความไหม (Liang-Barsky)"""
    x1, y1, x2, y2 = seg
    x0, y0, x3, y3 = box[1] + SHRINK, box[2] + SHRINK, box[3] - SHRINK, box[4] - SHRINK
    if x3 <= x0 or y3 <= y0: return False
    dx, dy = x2 - x1, y2 - y1
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x1 - x0), (dx, x3 - x1), (-dy, y1 - y0), (dy, y3 - y1)):
        if p == 0:
            if q < 0: return False
        else:
            r = q / p
            if p < 0:
                if r > t1: return False
                t0 = max(t0, r)
            else:
                if r < t0: return False
                t1 = min(t1, r)
    return t0 <= t1


def overlaps(a, b):
    ox = min(a[3], b[3]) - max(a[1], b[1]) - PAD
    oy = min(a[4], b[4]) - max(a[2], b[2]) - PAD
    return ox * oy if ox > 0 and oy > 0 else 0.0


def check_svg(svg):
    """คืน (คู่ที่ทับกัน, ข้อความที่ล้นกรอบ)"""
    vb = _attr(svg[:400], "viewBox")
    W, H = (float(v) for v in vb.split()[2:4]) if vb else (0, 0)
    ts = texts_of(svg)
    hits = []
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            area = overlaps(ts[i], ts[j])
            if area >= MIN_OVERLAP: hits.append((area, ts[i][0], ts[j][0]))
    segs = segments_of(svg)
    on_line = [t[0] for t in ts if any(_seg_hits_box(sg, t) for sg in segs)]
    out_of = [t for t in ts if W and (t[1] < -1 or t[3] > W + 1 or t[2] < -1 or t[4] > H + 1)]
    return sorted(hits, reverse=True), out_of, on_line, (W, H)


def main():
    pat = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else ""
    verbose = "-v" in sys.argv          # แสดงเส้นที่พาดทับข้อความด้วย (ไม่นับเป็นข้อผิดพลาด เพราะมีขอบขาวรอง)
    bad = warn = n_svg = 0
    for path in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
        name = os.path.basename(path)
        if pat and pat not in name: continue
        s = open(path, encoding="utf-8").read()
        for m in re.finditer(r"<svg\b.*?</svg>", s, re.S):
            svg = m.group(0)
            if len(svg) < 200: continue
            n_svg += 1
            lab = (_attr(svg[:600], "aria-label") or "")[:46]
            hits, out_of, on_line, (W, H) = check_svg(svg)
            for area, a, b in hits[:4]:
                print(f"❌ {name} · {lab}…\n     ทับกัน {area:.0f}px²: \"{a[:46]}\"  ×  \"{b[:46]}\""); bad += 1
            for t in out_of[:3]:
                print(f"❌ {name} · {lab}…\n     ล้นกรอบ: \"{t[0][:52]}\" (x {t[1]:.0f}–{t[3]:.0f} · y {t[2]:.0f}–{t[4]:.0f} · กรอบ {W:.0f}×{H:.0f})"); bad += 1
            warn += len(on_line)
            if verbose:
                for t in on_line[:4]:
                    print(f"⚠️  {name} · {lab}…\n     เส้นพาดทับข้อความ (มีขอบขาวรองแล้ว): \"{t[:52]}\"")
    print(f"\nตรวจ SVG {n_svg} ชิ้น · ข้อความทับกันหรือล้นกรอบ {bad} จุด · เส้นพาดทับข้อความ {warn} จุด (ดูด้วย -v)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
