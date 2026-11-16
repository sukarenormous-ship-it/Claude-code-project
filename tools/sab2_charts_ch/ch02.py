"""บท 2 เล่ม 2 — ราคาหรือ log ราคา · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json → ch02 เท่านั้น)

sab2-ruler2  : 📡 Z-score ทุกวันของช่วงเลือก เมื่อไม้บรรทัด (h · Mean · SD) วัดจากปีแรกเท่านั้น สองแผง: X แบบราคา · X แบบ log
               เส้น ±2 · เส้นแบ่งปีแรก/ปีหลัง · ตัดที่ 8 และเขียนค่าสูงสุดของปีหลัง
sab2-coins   : 📡 จำนวน ETH ต่อ BTC หนึ่งเหรียญ ถ้าถือตาม h แบบ log (h × ราคา BTC ÷ ราคา ETH) ทุกวันของช่วงเลือก
               เทียบเส้นคงที่ของ h แบบราคา (23.69)
sab2-zmax    : 🎲 Z สูงสุดของปีหลังใน 30 โลกที่เชือกอยู่บนเปอร์เซ็นต์ (ราคา เทียบ log) + 📡 ค่าของ BTC–ETH · แกนนอนแบบ log
"""

import math

from sab_charts import chart, wrap, text, C, B

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


@chart("sab2-ruler2")
def _ruler2(fig):
    r = fig["ch02"]["จริง"]
    g = r["ชุดกราฟ"]
    mp, ml = r["ไม้ปีแรก"]["ราคา"], r["ไม้ปีแรก"]["log"]
    panels = [("X แบบราคา (ดอลลาร์ต่อชุด)", g["zราคา"], C["amber"], mp),
              ("X แบบ log (เปอร์เซ็นต์)", g["zlog"], C["blue"], ml)]
    half = g["iครึ่ง"]
    W, L, R = 760, 64, 200
    ph, gap, top = 130, 48, 56
    H = top + len(panels) * (ph + gap) + 16
    lo, hi = -3, 8
    out = [text(16, 26, "ไม้บรรทัดวัดจากปีแรก แล้วใช้วัดปีหลัง: แบบราคายืดหลุดกรอบ แบบ log หลุดน้อยกว่า", 13.5, INK, weight=700)]
    for k, (name, zs, col, m) in enumerate(panels):
        t0 = top + k * (ph + gap)
        n = len(zs)
        X = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
        Y = lambda v, t0=t0: t0 + (hi - max(lo, min(hi, v))) / (hi - lo) * ph  # noqa: E731
        out.append(text(L, t0 - 8, name, 11.5, INK, weight=700))
        out.append(f'<rect x="{X(half):.1f}" y="{t0}" width="{X(n - 1) - X(half):.1f}" height="{ph}" fill="{C["grid"]}" fill-opacity=".45"/>')
        for gv in (-2, 0, 2, 4, 6, 8):
            stroke = C["axis"] if gv == 0 else (C["red"] if abs(gv) == 2 else C["grid"])
            dash = ' stroke-dasharray="4 4"' if abs(gv) == 2 else ""
            out.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W - R}" y2="{Y(gv):.1f}" stroke="{stroke}"{dash}/>')
            out.append(text(L - 8, Y(gv) + 4, B.fmt(gv), 10, GREY, "end"))
        pts = [(X(i), Y(v)) for i, v in enumerate(zs)]
        out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="1.4" stroke-linejoin="round"/>')
        out.append(text(X(half / 2), t0 + ph + 15, "ปีแรก (วัดไม้บรรทัด)", 10.5, MUTED, "middle"))
        out.append(text((X(half) + X(n - 1)) / 2, t0 + ph + 15, "ปีหลัง (ใช้ไม้เดิม)", 10.5, MUTED, "middle"))
        lx = W - R + 14
        out.append(text(lx, t0 + 22, f"ปีหลัง Z สูงสุด {B.fmt(m['Zสูงสุด'])}", 11.5, col, weight=700))
        out.append(text(lx, t0 + 42, f"นอก ±2 อยู่ {B.fmt(m['นอกสองเปอร์เซ็นต์'])}% ของวัน", 11, INK))
        out.append(text(lx, t0 + 62, f"h ปีแรก {B.fmt(m['h'])}", 11, MUTED))
        out.append(text(lx, t0 + 80, f"h ปีหลัง {B.fmt(m['hปีหลัง'])}", 11, MUTED))
        if m["Zสูงสุด"] > hi:
            out.append(text(lx, t0 + 100, f"(ภาพตัดที่ {hi})", 10.5, col))
    out.append(text(L, H - 6, f"แกนนอน = {B.fmt(r['วัน'])} วันของช่วงเลือก · แกนตั้ง = Z-score · เส้นประแดง = ±2", 10.5, MUTED))
    alt = (f"สองแผงเส้น Z-score {r['วัน']} วัน ไม้บรรทัดวัดจากปีแรก แผงบน X แบบราคา ปีหลังพุ่งขึ้นถึง {mp['Zสูงสุด']} "
           f"อยู่นอก ±2 {mp['นอกสองเปอร์เซ็นต์']}% ของวัน แผงล่าง X แบบ log ปีหลังขึ้นถึง {ml['Zสูงสุด']} "
           f"อยู่นอก ±2 {ml['นอกสองเปอร์เซ็นต์']}% ของวัน")
    cap = (f"ราคาปิดรายวัน Binance ช่วงเลือก {r['เริ่ม']} ถึง {r['จบ']} · ไม้บรรทัดจาก {B.fmt(r['ครึ่ง'])} วันแรก "
           f"ใช้วัด {B.fmt(r['ครึ่งหลังวัน'])} วันหลัง · ตัดแกนที่ −3 ถึง 8")
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-coins")
def _coins(fig):
    r = fig["ch02"]["จริง"]
    c = r["เหรียญ"]
    ys = r["ชุดกราฟ"]["เหรียญ"]
    n = len(ys)
    W, H, L, R, T, Bm = 760, 340, 64, 200, 56, 290
    lo, hi = 10, 45
    X = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "h แบบ log คงที่ แต่จำนวน ETH ที่ต้องถือต่อ BTC เปลี่ยนทุกวัน", 13.5, INK, weight=700)]
    for gv in (10, 20, 30, 40):
        out.append(f'<line x1="{L}" y1="{Y(gv):.1f}" x2="{W - R}" y2="{Y(gv):.1f}" stroke="{C["grid"]}"/>')
        out.append(text(L - 8, Y(gv) + 4, B.fmt(gv), 11, GREY, "end"))
    out.append(text(L - 8, T - 14, "ETH ต่อ BTC 1 เหรียญ", 11.5, MUTED, "start", 700))
    pts = [(X(i), Y(v)) for i, v in enumerate(ys)]
    out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{C["blue"]}" stroke-width="1.8" stroke-linejoin="round"/>')
    hp = c["hราคา"]
    out.append(f'<line x1="{L}" y1="{Y(hp):.1f}" x2="{W - R}" y2="{Y(hp):.1f}" stroke="{C["amber"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    out.append(f'<circle cx="{X(0):.1f}" cy="{Y(ys[0]):.1f}" r="4.5" fill="{C["blue"]}"/>')
    out.append(f'<circle cx="{X(n - 1):.1f}" cy="{Y(ys[-1]):.1f}" r="4.5" fill="{C["blue"]}"/>')
    out.append(text(X(0) + 8, Y(ys[0]) + 18, f"วันแรก ราว {B.fmt(c['วันแรก'])}", 11, C["blue"], "start", 700))
    out.append(text(X(n - 1) - 8, Y(ys[-1]) - 10, f"วันสุดท้าย ราว {B.fmt(c['วันสุดท้าย'])}", 11, C["blue"], "end", 700))
    lx = W - R + 14
    out.append(f'<line x1="{lx}" y1="{T + 16}" x2="{lx + 26}" y2="{T + 16}" stroke="{C["blue"]}" stroke-width="2.4"/>')
    out.append(text(lx + 32, T + 20, f"ตาม h แบบ log {B.fmt(r['h'])}", 11, C["blue"], weight=700))
    out.append(text(lx + 32, T + 36, "(h × BTC ÷ ETH)", 10.5, MUTED))
    out.append(f'<line x1="{lx}" y1="{T + 62}" x2="{lx + 26}" y2="{T + 62}" stroke="{C["amber"]}" stroke-width="2.4" stroke-dasharray="6 4"/>')
    out.append(text(lx + 32, T + 66, f"h แบบราคา {B.fmt(hp)}", 11, C["amber"], weight=700))
    out.append(text(lx + 32, T + 82, "(จำนวนคงที่)", 10.5, MUTED))
    out.append(text(L, H - 10, f"แกนนอน = {B.fmt(r['วัน'])} วันของช่วงเลือก {r['เริ่ม']} ถึง {r['จบ']}", 10.5, MUTED))
    alt = (f"เส้นจำนวน ETH ต่อ BTC หนึ่งเหรียญตาม h แบบ log {r['h']} เริ่มราว {c['วันแรก']} ไต่ขึ้นเป็นขั้นจนจบราว {c['วันสุดท้าย']} "
           f"เส้นประคงที่ที่ {hp} คือ h แบบราคา")
    cap = f"ราคาปิดรายวัน Binance ช่วงเลือก · h แบบ log {B.fmt(r['h'])} จากทั้ง {B.fmt(r['วัน'])} วัน · หนึ่งจุดต่อวัน"
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-zmax")
def _zmax(fig):
    s = fig["ch02"]["จำลอง"]
    r = fig["ch02"]["จริง"]["ไม้ปีแรก"]
    zp, zl = s["ชุดกราฟ"]["Zราคา"], s["ชุดกราฟ"]["Zlog"]
    W, L, R = 760, 190, 40
    H = 330
    lo, hi = 0.5, 100
    X = lambda v: L + (math.log10(max(lo, v)) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (W - L - R)  # noqa: E731
    out = [text(16, 26, f"Z สูงสุดของปีหลังใน {B.fmt(s['ชุด'])} โลกที่เชือกอยู่บนเปอร์เซ็นต์ เทียบกับ BTC–ETH", 13.5, INK, weight=700)]
    top, bot = 56, 250
    for gv in (0.5, 1, 2, 5, 10, 20, 50, 100):
        dash = ' stroke-dasharray="4 4"' if gv == 2 else ""
        out.append(f'<line x1="{X(gv):.1f}" y1="{top}" x2="{X(gv):.1f}" y2="{bot}" stroke="{C["red"] if gv == 2 else C["grid"]}"{dash}/>')
        out.append(text(X(gv), bot + 18, B.fmt(gv), 11, GREY, "middle"))
    out.append(text((L + W - R) / 2, bot + 38, "Z สูงสุดในปีหลัง (แกนแบบ log: แต่ละช่องคูณ 2 ถึง 2.5 เท่า)", 11.5, MUTED, "middle", 700))
    rows = [("🎲 วัดด้วยราคา", zp, C["amber"], s["สุ่มซ้ำ"]["Zสูงสุดราคา"]["มัธยฐาน"]),
            ("🎲 วัดด้วย log", zl, C["blue"], s["สุ่มซ้ำ"]["Zสูงสุดlog"]["มัธยฐาน"])]
    for j, (lab, vals, col, med) in enumerate(rows):
        y = top + 40 + 60 * j
        out.append(text(16, y + 4, lab, 12, INK, weight=700))
        for k, v in enumerate(sorted(vals)):
            out.append(f'<circle cx="{X(v):.1f}" cy="{y + (k % 3 - 1) * 6:.1f}" r="3.6" fill="{col}" fill-opacity=".6"/>')
        out.append(f'<line x1="{X(med):.1f}" y1="{y - 14}" x2="{X(med):.1f}" y2="{y + 14}" stroke="{col}" stroke-width="3"/>')
        out.append(text(X(med), y - 18, f"มัธยฐาน {B.fmt(med)}", 10.5, col, "middle", 700))
    y = top + 40 + 120
    out.append(text(16, y + 4, "📡 BTC–ETH", 12, INK, weight=700))
    for v, col, lab, dy in ((r["ราคา"]["Zสูงสุด"], C["amber"], "ราคา", -12), (r["log"]["Zสูงสุด"], C["blue"], "log", -12)):
        out.append(f'<rect x="{X(v) - 5:.1f}" y="{y - 5}" width="10" height="10" fill="{col}"/>')
        out.append(text(X(v), y + dy, f"{lab} {B.fmt(v)}", 10.5, col, "middle", 700))
    out.append(text(X(2) + 4, top - 4, "เส้น 2", 10.5, C["red"], "start", 700))
    alt = (f"จุด {s['ชุด']} จุดต่อแถว แกนนอนแบบ log จาก 0.5 ถึง 100 โลกที่วัดด้วยราคามี Z สูงสุดกระจายตั้งแต่ "
           f"{s['สุ่มซ้ำ']['Zสูงสุดราคา']['ต่ำสุด']} ถึง {s['สุ่มซ้ำ']['Zสูงสุดราคา']['สูงสุด']} มัธยฐาน {s['สุ่มซ้ำ']['Zสูงสุดราคา']['มัธยฐาน']} "
           f"วัดด้วย log กระจาย {s['สุ่มซ้ำ']['Zสูงสุดlog']['ต่ำสุด']} ถึง {s['สุ่มซ้ำ']['Zสูงสุดlog']['สูงสุด']} มัธยฐาน "
           f"{s['สุ่มซ้ำ']['Zสูงสุดlog']['มัธยฐาน']} BTC–ETH ได้ {r['ราคา']['Zสูงสุด']} แบบราคา และ {r['log']['Zสูงสุด']} แบบ log")
    cap = (f"โลกเชือกบนเปอร์เซ็นต์ h {B.fmt(s['h'])} บน log ราคา φ {B.fmt(s['phi'])} · {B.fmt(s['วัน'])} วัน · "
           f"สุ่มซ้ำ {B.fmt(s['ชุด'])} ชุด · ไม้บรรทัดจากปีแรก · สี่เหลี่ยมคือข้อมูลจริงช่วงเลือก")
    return wrap(W, H, alt, out, cap, "จำลอง")
