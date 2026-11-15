"""บท 9 — สองเหรียญที่เดินด้วยกัน · สเปกกราฟของบท

sab-corr-vs-rope    : คู่ตัวอย่างสองแบบ ระยะห่าง (% ของ A เทียบ B) ตลอด 500 วัน + ป้าย correlation สองชั้น
                      (คู่ตัวอย่าง 0.91 / 0.74 · เฉลี่ย 200 คู่ 0.90 / 0.72 — แผน errata 18 · 8.2 แถว 7.1)
sab-formation-test  : คู่ไม่มีเชือกตัวอย่างในหน่วยระยะแกว่ง (z) · ไม้บรรทัดวัดจากช่วงเลือกแล้วตรึงไปวัดช่วงทดสอบ
sab-rope-types      : ผังเชือก 4 ชนิด (ภาพแนวคิด · ไม่มีตัวเลข) · ต่อจาก sab-rope-types0 ของบท 0 (v2: อยู่ในแฟ้มท้ายบท)
sab-ruler20         : (v2) X ของ A–B 20 วัน กับเส้น Mean และแถบ ±1 / ±2 Standard Deviation — ตอน ก
sab-test10          : (v2) ไม้บรรทัดจากวันที่ 1–20 ตรึงไว้ แล้ววัดวันทดสอบ 21–30 — ตอน ข
"""

import math

from sab_charts import chart, wrap, text, nice_ticks, C, B

INK, MUTED = C["ink"], C["muted"]
NOROPE, ROPE = C["blue"], C["amber"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def _panel(series, x0, x1, y0, y1, lo, hi, col, every=2):
    """เส้นหนึ่งเส้นในกรอบ (x0..x1, y0 บน .. y1 ล่าง) ช่วงค่า lo..hi → (svg, ฟังก์ชัน X, Y)"""
    n = len(series)
    X = lambda i: x0 + i / (n - 1) * (x1 - x0)  # noqa: E731
    Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)  # noqa: E731
    pts = [(X(i), Y(v)) for i, v in enumerate(series) if i % every == 0 or i == n - 1]
    return (f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="1.8" '
            f'stroke-linejoin="round"/>'), X, Y


@chart("sab-corr-vs-rope")
def _corr_vs_rope(fig):
    c9 = fig["ch09"]
    nf, ndays = c9["จำลอง"]["ช่วงเลือก"], c9["จำลอง"]["วัน"]
    pctd = {k: [(math.exp(v) - 1) * 100 for v in c9["กราฟ"][k]] for k in ("ไม่มีเชือก", "มีเชือก")}
    allv = pctd["ไม่มีเชือก"] + pctd["มีเชือก"]
    ticks = [t for t in nice_ticks(min(allv), max(allv), 4)]
    lo, hi = min(ticks[0], min(allv)), max(ticks[-1], max(allv))
    W, H = 760, 470
    L, R = 64, 24
    p = [text(L, 26, "Correlation สูงกว่า แต่ระยะห่างเดินออกไปไม่กลับ", 13, INK, weight=700)]
    panels = [("ไม่มีเชือก", "คู่ไม่มีเชือก", NOROPE, 52), ("มีเชือก", "คู่มีเชือก", ROPE, 262)]
    for key, name, col, top in panels:
        y0, y1 = top + 34, top + 180
        ex, avg = c9["คู่ตัวอย่าง"][key], c9[key]
        p.append(f'<rect x="8" y="{top}" width="{W - 16}" height="196" rx="10" fill="#fafafa" stroke="{C["grid"]}"/>')
        p.append(text(24, top + 22, f"{name} · Correlation คู่ตัวอย่าง {ex['corr']:.2f} · เฉลี่ย 200 คู่ {avg['corr']:.2f}",
                      12.5, col, weight=700))
        Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)  # noqa: E731
        for t in ticks:
            if lo <= t <= hi:
                p.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{W - R}" y2="{Y(t):.1f}" '
                         f'stroke="{C["axis"] if t == 0 else C["grid"]}" stroke-width="{1.4 if t == 0 else 1}"/>')
                p.append(text(L - 8, Y(t) + 4, f"{B.fmt(t)}%", 10.5, C["grey"], "end"))
        xd = L + (nf - 1) / (ndays - 1) * (W - R - L)
        p.append(f'<line x1="{xd:.1f}" y1="{y0 - 6}" x2="{xd:.1f}" y2="{y1}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
        line, _, _ = _panel(pctd[key], L, W - R, y0, y1, lo, hi, col)
        p.append(line)
        p.append(text(W - R - 6, y0 + 8, f"ครึ่งหลังอยู่ในกรอบ {B.fmt(ex['ในกรอบ'])}%", 11.5, C["purple"], "end", 700))
    p.append(text((L + W - R) / 2 - 150, H - 14, "← ครึ่งแรก 250 วัน (ใช้วัดกรอบ)", 11, MUTED, "middle"))
    p.append(text((L + W - R) / 2 + 150, H - 14, "ครึ่งหลัง 250 วัน →", 11, MUTED, "middle"))
    alt = (f"กราฟสองแผง ระยะห่างของ A เทียบ B ตลอด {ndays} วัน คู่ไม่มีเชือก Correlation {B.fmt(c9['คู่ตัวอย่าง']['ไม่มีเชือก']['corr'])} "
           f"ระยะห่างเดินขึ้นไปเรื่อย ๆ ครึ่งหลังอยู่ในกรอบ {B.fmt(c9['คู่ตัวอย่าง']['ไม่มีเชือก']['ในกรอบ'])}% "
           f"คู่มีเชือก Correlation {B.fmt(c9['คู่ตัวอย่าง']['มีเชือก']['corr'])} แกว่งแรงกว่าแต่กลับมารอบศูนย์ "
           f"อยู่ในกรอบ {B.fmt(c9['คู่ตัวอย่าง']['มีเชือก']['ในกรอบ'])}%")
    cap = "แกนตั้ง = A ห่างจาก B กี่ % นับจากวันแรก · คู่ตัวอย่างที่ใกล้ค่าเฉลี่ยของแบบ"
    return wrap(W, H, alt, p, cap, "จำลอง")


@chart("sab-formation-test")
def _formation_test(fig):
    c9 = fig["ch09"]
    nf = c9["จำลอง"]["ช่วงเลือก"]
    s = c9["กราฟ"]["ไม่มีเชือก"]
    st = c9["ตัวอย่างสองแบบ"]["ไม่มีเชือก"]
    f = s[:nf]
    m = sum(f) / nf
    sd = math.sqrt(sum((x - m) ** 2 for x in f) / (nf - 1))
    z = [(x - m) / sd for x in s]
    W, H = 760, 360
    L, R, y0, y1 = 64, 24, 64, 316
    lo, hi = min(-3.0, min(z) - 0.3), max(3.0, max(z) + 0.3)
    X = lambda i: L + i / (len(z) - 1) * (W - R - L)  # noqa: E731
    Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)  # noqa: E731
    xd = X(nf - 1)
    p = [text(L, 22, "ไม้บรรทัดจาก Formation Period ตรึงไว้วัด Test Period", 13, INK, weight=700),
         f'<rect x="{L}" y="{y0}" width="{xd - L:.1f}" height="{y1 - y0}" fill="{C["purple"]}" fill-opacity=".05"/>']
    for k in (-2, -1, 0, 1, 2):
        col = C["axis"] if k == 0 else (C["purple"] if abs(k) == 2 else C["grey"])
        dash = "" if k == 0 else ' stroke-dasharray="5 4"'
        p.append(f'<line x1="{L}" y1="{Y(k):.1f}" x2="{W - R}" y2="{Y(k):.1f}" stroke="{col}" stroke-width="1.3"{dash}/>')
        p.append(text(L - 8, Y(k) + 4, ("+" if k > 0 else "") + B.fmt(k), 10.5, col, "end"))
    p.append(text(L + 6, Y(2) - 6, "+2 Standard Deviation", 10.5, C["purple"], "start", 700))
    p.append(text(W - R - 4, Y(0) - 6, "Mean", 10.5, MUTED, "end"))
    pts = [(X(i), Y(v)) for i, v in enumerate(z)]
    p.append(f'<polyline points="{_poly(pts[:nf])}" fill="none" stroke="{NOROPE}" stroke-width="1.8"/>')
    p.append(f'<polyline points="{_poly(pts[nf - 1:])}" fill="none" stroke="{NOROPE}" stroke-width="1.8" stroke-opacity=".55"/>')
    for i in range(nf, len(z)):
        if abs(z[i]) > 2:
            p.append(f'<circle cx="{pts[i][0]:.1f}" cy="{pts[i][1]:.1f}" r="1.9" fill="{C["red"]}"/>')
    p.append(f'<line x1="{xd:.1f}" y1="{y0 - 8}" x2="{xd:.1f}" y2="{y1}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    p.append(text(L + 8, Y(-2.55), f"Formation Period: ใน ±1 {B.fmt(st['ช่วงเลือกในหนึ่งระยะ'])}% · ±2 {B.fmt(st['ช่วงเลือกในสองระยะ'])}%",
                  11.5, C["purple"], weight=700))
    p.append(text(xd + 10, Y(-2.55), f"Test Period: ใน ±2 แค่ {B.fmt(st['ช่วงทดสอบในสองระยะ'])}% · จุดแดง = หลุดกรอบ",
                  11.5, C["red"], weight=700))
    p.append(text(xd, y1 + 22, f"วันที่ {B.fmt(nf)}", 10.5, C["grey"], "middle"))
    p.append(text(W - R, y1 + 22, f"วันที่ {B.fmt(c9['จำลอง']['วัน'])}", 10.5, C["grey"], "end"))
    p.append(text(L - 44, y0 - 10, "Z-score", 11, MUTED))
    alt = (f"กราฟเส้นระยะห่างของคู่ไม่มีเชือกในหน่วย Standard Deviation ช่วง Formation Period อยู่ในกรอบ ±2 ราว {B.fmt(st['ช่วงเลือกในสองระยะ'])}% "
           f"แต่ใน Test Period อยู่ในกรอบเดิมแค่ {B.fmt(st['ช่วงทดสอบในสองระยะ'])}% และหลุดกรอบเป็นช่วงยาว")
    cap = "คู่ไม่มีเชือกตัวอย่างเดียวกับภาพบน"
    return wrap(W, H, alt, p, cap, "จำลอง")


# ── ผังเชือก 4 ชนิด ──

def _chain_h(x0, x1, y):
    out, link, x = [], 13.0, x0
    k = 0
    while x + link <= x1:
        if k % 2 == 0:
            out.append(f'<ellipse cx="{x + link / 2:.1f}" cy="{y}" rx="{link * 0.62:.1f}" ry="4.6" fill="none" '
                       f'stroke="{MUTED}" stroke-width="2.2"/>')
        else:
            out.append(f'<line x1="{x + 1:.1f}" y1="{y}" x2="{x + link - 1:.1f}" y2="{y}" stroke="{MUTED}" stroke-width="3" '
                       f'stroke-linecap="round"/>')
        x += link
        k += 1
    return out


def _icon(kind, x0, x1, y):
    a, b = (f'<circle cx="{x0:.1f}" cy="{y}" r="6" fill="{C["blue"]}"/>',
            f'<circle cx="{x1:.1f}" cy="{y}" r="6" fill="{C["amber"]}"/>')
    if kind == "chain":
        col = C["purple"]
        lock = [f'<path d="M{x1 - 26:.1f},{y - 14} v-5 a5,5 0 0 1 10,0 v5" fill="none" stroke="{col}" stroke-width="2"/>',
                f'<rect x="{x1 - 29:.1f}" y="{y - 15}" width="16" height="12" rx="2.5" fill="{col}"/>']
        return _chain_h(x0 + 8, x1 - 8, y) + lock + [a, b]
    if kind == "pull":
        mid = (x0 + x1) / 2
        return [f'<path d="M{x0 + 6:.1f},{y} Q{mid:.1f},{y + 22} {x1 - 6:.1f},{y}" fill="none" stroke="{MUTED}" stroke-width="2.6"/>',
                f'<line x1="{mid:.1f}" y1="{y + 10}" x2="{mid:.1f}" y2="{y - 2}" stroke="{C["green"]}" stroke-width="2"/>',
                f'<path d="M{mid - 5:.1f},{y - 1} l5,-8 l5,8 z" fill="{C["green"]}"/>', a, b]
    if kind == "spring":
        n, pts = 14, []
        for i in range(n + 1):
            xx = x0 + 8 + i * (x1 - x0 - 16) / n
            pts.append((xx, y + (0 if i in (0, n) else (-7 if i % 2 else 7))))
        return [f'<polyline points="{_poly(pts)}" fill="none" stroke="{MUTED}" stroke-width="2.2" stroke-linejoin="round"/>', a, b]
    return [f'<line x1="{x0 + 8:.1f}" y1="{y}" x2="{x1 - 8:.1f}" y2="{y}" stroke="{MUTED}" stroke-width="2.2" '
            f'stroke-dasharray="3 6" stroke-linecap="round"/>', a, b]


@chart("sab-rope-types")
def _rope_types(fig):  # noqa: ARG001 — ภาพแนวคิด ไม่อ่านตัวเลข
    # ผังแคบ (W 560 · narrow) ให้อ่านได้บนจอ 420 px: ซ้าย = ชื่อขั้น + ตัวอย่าง + ไอคอน · ขวา = อะไรดึงกลับ (ดำ) / พังเมื่อ (แดง)
    # ไม่ไฮไลต์ขั้นของ A–B — 🛑 ถัดจากภาพให้ผู้อ่านเลือกขั้นเอง
    rows = [("chain", "โซ่ที่มีวันล็อก", "spot กับ dated futures", "สัญญาชำระราคาวันหมดอายุ", "เงินสดหมดระหว่างทาง"),
            ("pull", "เชือกที่มีคนคอยดึง", "โทเคนที่แลกคืนเป็นเหรียญแม่ได้", "คนแลกคืนซื้อขายจนระยะหด", "คิวยาว · แลกคืนถูกระงับ"),
            ("spring", "ยางยืด", "เหรียญที่แข่งกลุ่มเดียวกัน", "ข่าวร่วม ไม่มีใครบังคับ", "ข่าวเฉพาะตัว · มุมมองเปลี่ยนถาวร"),
            ("dash", "เส้นที่วาดเอง", "คู่ที่เจอจากการค้นย้อนหลัง", "ไม่มีเหตุผลอธิบาย", "บังเอิญจากการค้นมาก")]
    W, rh, top = 560, 100, 50
    H = top + rh * len(rows) + 8
    xr = 262
    p = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>',
         text(xr, 30, "อะไรดึงกลับ", 13, INK, weight=700), text(xr + 90, 30, "· พังเมื่อ", 13, C["red"], weight=700)]
    # ลูกศรด้านซ้าย: บนผูกแน่น → ล่างต้องพึ่งข้อมูล
    p.append(f'<line x1="16" y1="{top + 8}" x2="16" y2="{H - 22}" stroke="{C["grey"]}" stroke-width="2"/>')
    p.append(f'<path d="M10,{H - 26} l6,12 l6,-12 z" fill="{C["grey"]}"/>')
    for i, (kind, name, ex, pull, fail) in enumerate(rows):
        y = top + i * rh
        p.append(f'<rect x="30" y="{y}" width="{W - 38}" height="{rh - 10}" rx="9" fill="#fafafa" stroke="{C["grid"]}"/>')
        p.append(text(44, y + 25, name, 15, INK, weight=700))
        p.append(text(44, y + 46, ex, 12.5, MUTED))
        p += _icon(kind, 54, 214, y + 70)
        p.append(text(xr, y + 36, pull, 14.5, INK))
        p.append(text(xr, y + 64, fail, 14.5, C["red"]))
    alt = ("ผังบันไดเชือกสี่ขั้นจากผูกแน่นลงไปหลวม โซ่ที่มีวันล็อก เชือกที่มีคนคอยดึง ยางยืด และเส้นที่วาดเอง "
           "แต่ละขั้นบอกว่าอะไรดึงสองราคากลับ และพังเมื่อไร")
    cap = "บนผูกแน่น ล่างต้องพึ่งข้อมูลที่ไม่ได้ใช้เลือกคู่"
    return wrap(W, H, alt, p, cap, "แนวคิด", narrow=True)


# ── v2: ไม้บรรทัดของ A–B ──

def _f(v):
    """ตัวเลขบนกราฟ: 2.0 → 2 · 2.2 → 2.2"""
    return B.fmt(int(v)) if float(v).is_integer() else B.fmt(v)


def _ruler_frame(W, L, R, y0, y1, n, lo=-3.0, hi=3.0):
    X = lambda d: L + (d - 1) / (n - 1) * (W - R - L)  # noqa: E731
    Y = lambda v: y1 - (v - lo) / (hi - lo) * (y1 - y0)  # noqa: E731
    return X, Y


def _bands(p, X, Y, x0, x1, mean, sd, labels=True):
    p.append(f'<rect x="{x0:.1f}" y="{Y(mean + sd):.1f}" width="{x1 - x0:.1f}" height="{Y(mean - sd) - Y(mean + sd):.1f}" '
             f'fill="{C["purple"]}" fill-opacity=".09"/>')
    for k in (-2, -1, 0, 1, 2):
        v = mean + k * sd
        col = C["axis"] if k == 0 else (C["purple"] if abs(k) == 2 else C["grey"])
        dash = "" if k == 0 else ' stroke-dasharray="5 4"'
        p.append(f'<line x1="{x0:.1f}" y1="{Y(v):.1f}" x2="{x1:.1f}" y2="{Y(v):.1f}" stroke="{col}" stroke-width="1.3"{dash}/>')
        if labels:
            p.append(text(x0 - 8, Y(v) + 4, ("+" if v > 0 else "") + _f(v), 10.5, col, "end"))


@chart("sab-ruler20")
def _ruler20(fig):
    c = fig["ch09"]["นับมือ20วัน"]
    xs, mean, sd = c["X"], c["ค่ากลาง"], c["ระยะแกว่งนับมือ"]
    n = len(xs)
    W, H, L, R, y0, y1 = 760, 380, 64, 150, 60, 320
    X, Y = _ruler_frame(W, L, R, y0, y1, n)
    p = [text(L, 24, f"X ของ A–B {n} วัน กับไม้บรรทัด Mean {_f(mean)} · SD {_f(sd)}", 13, INK, weight=700)]
    _bands(p, X, Y, L, W - R, mean, sd)
    xr = W - R + 8
    p.append(text(xr, Y(mean) + 4, f"Mean {_f(mean)}", 11, MUTED))
    p.append(text(xr, Y(mean + sd) - 4, "ขอบ ±1 SD", 11, C["grey"]))
    p.append(text(xr, Y(mean + sd) + 12, f"แถบนี้มี {c['ในหนึ่งระยะ']} วัน", 11, C["purple"], weight=700))
    p.append(text(xr, Y(mean + 2 * sd) - 4, "ขอบ ±2 SD", 11, C["purple"], weight=700))
    p.append(text(xr, Y(mean + 2 * sd) + 12, f"ข้างในมี {c['ในสองระยะ']} วัน", 11, C["purple"]))
    pts = [(X(i + 1), Y(v)) for i, v in enumerate(xs)]
    p.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{NOROPE}" stroke-width="1.4" stroke-opacity=".5"/>')
    far = c["วันไกลสุด"]
    for i, (x, y) in enumerate(pts):
        d = abs(xs[i] - mean)
        col = C["purple"] if d > 2 * sd else (NOROPE if d <= sd else C["ink"])
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if i + 1 == far else 3.6}" fill="{col}"/>')
    fx, fy = pts[far - 1]
    p.append(text(fx + 8, fy - 6, f"วันที่ {far}: X = {B.fmt(c['Xไกลสุด'])}", 11.5, C["purple"], weight=700))
    for d in (1, 5, 10, 15, 20):
        p.append(text(X(d), y1 + 20, f"วันที่ {d}", 10.5, C["grey"], "middle"))
    p.append(text(L - 50, y0 - 12, "X (ดอลลาร์ต่อชุด)", 11, MUTED))
    alt = (f"จุด X ของคู่ A–B {n} วัน รอบเส้น Mean {_f(mean)} แถบ ±1 Standard Deviation มี {c['ในหนึ่งระยะ']} วัน "
           f"แถบ ±2 มี {c['ในสองระยะ']} วัน วันที่ {far} อยู่นอกแถบ ±2 ที่ X {B.fmt(c['Xไกลสุด'])}")
    cap = "จุดสีน้ำเงิน = อยู่ในแถบ ±1 · จุดเทาเข้ม = นอก ±1 แต่ใน ±2 · จุดม่วง = นอก ±2"
    return wrap(W, H, alt, p, cap, "สอน")


@chart("sab-test10")
def _test10(fig):
    c9 = fig["ch09"]
    c, t = c9["นับมือ20วัน"], c9["v2"]["วันทดสอบ"]
    mean, sd = c["ค่ากลาง"], c["ระยะแกว่งนับมือ"]
    xs = c["X"] + t["X"]
    nf, n = len(c["X"]), len(c["X"]) + len(t["X"])
    W, H, L, R, y0, y1 = 760, 380, 64, 24, 60, 320
    X, Y = _ruler_frame(W, L, R, y0, y1, n)
    xd = (X(nf) + X(nf + 1)) / 2
    p = [text(L, 24, f"ไม้บรรทัดจากวันที่ 1–{nf} ตรึงไว้ แล้ววัดวันที่ {nf + 1}–{n}", 13, INK, weight=700),
         f'<rect x="{L}" y="{y0}" width="{xd - L:.1f}" height="{y1 - y0}" fill="{C["grey"]}" fill-opacity=".07"/>']
    _bands(p, X, Y, L, W - R, mean, sd)
    p.append(f'<line x1="{xd:.1f}" y1="{y0 - 6}" x2="{xd:.1f}" y2="{y1}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    pts = [(X(i + 1), Y(v)) for i, v in enumerate(xs)]
    p.append(f'<polyline points="{_poly(pts[:nf])}" fill="none" stroke="{NOROPE}" stroke-width="1.4" stroke-opacity=".45"/>')
    p.append(f'<polyline points="{_poly(pts[nf - 1:])}" fill="none" stroke="{ROPE}" stroke-width="1.6"/>')
    for i, (x, y) in enumerate(pts):
        out = abs(xs[i] - mean) > 2 * sd
        col = C["red"] if (out and i >= nf) else (NOROPE if i < nf else ROPE)
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.6 if out and i >= nf else 3.3}" fill="{col}"/>')
    d1, d2 = t["วันหลุด"][0], t["วันหลุด"][-1]
    p.append(text(X(d2) + 10, Y(t["Xสูงสุด"]) - 4, f"วันที่ {d1}–{d2} หลุด +2", 11.5, C["red"], weight=700))
    p.append(text(L + 8, y1 - 10, f"ช่วงที่ใช้วัด {nf} วัน", 11.5, MUTED, weight=700))
    p.append(text(W - R - 6, y1 - 10, f"ช่วงทดสอบ: ใน ±2 = {t['วันในกรอบ']} จาก {t['วัน']} วัน", 11.5, ROPE, "end", 700))
    for d in (1, 10, 20, 30):
        p.append(text(X(d), y1 + 20, f"วันที่ {d}", 10.5, C["grey"], "middle"))
    p.append(text(L - 50, y0 - 12, "X (ดอลลาร์ต่อชุด)", 11, MUTED))
    alt = (f"X ของคู่ A–B วันที่ 1 ถึง {n} เส้น Mean และแถบ ±1 ±2 Standard Deviation วัดจาก {nf} วันแรกแล้วลากต่อโดยไม่แก้ "
           f"วันที่ {nf + 1}–{n} อยู่ในแถบ ±2 {t['วันในกรอบ']} วัน หลุดวันที่ {d1} และ {d2}")
    cap = f"เส้นน้ำเงิน = {nf} วันที่ใช้วัดไม้บรรทัด · เส้นส้ม = {t['วัน']} วันที่จดหลังตรึงไม้บรรทัด · จุดแดง = หลุดกรอบ ±2"
    return wrap(W, H, alt, p, cap, "สอน")
