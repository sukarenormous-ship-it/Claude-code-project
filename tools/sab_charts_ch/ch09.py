"""บท 9 — สองเหรียญที่เดินด้วยกัน · สเปกกราฟของบท

sab-corr-vs-rope    : คู่ตัวอย่างสองแบบ ระยะห่าง (% ของ A เทียบ B) ตลอด 500 วัน + ป้าย correlation สองชั้น
                      (คู่ตัวอย่าง 0.91 / 0.74 · เฉลี่ย 200 คู่ 0.90 / 0.72 — แผน errata 18 · 8.2 แถว 7.1)
sab-formation-test  : คู่ไม่มีเชือกตัวอย่างในหน่วยระยะแกว่ง (z) · ไม้บรรทัดวัดจากช่วงเลือกแล้วตรึงไปวัดช่วงทดสอบ
sab-rope-types      : ผังเชือก 4 ชนิด (ภาพแนวคิด · ไม่มีตัวเลข) · ต่อจาก sab-rope-types0 ของบท 0
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
    p = [text(L, 26, "correlation สูงกว่า แต่ระยะห่างเดินออกไปไม่กลับ", 13, INK, weight=700)]
    panels = [("ไม่มีเชือก", "คู่ไม่มีเชือก", NOROPE, 52), ("มีเชือก", "คู่มีเชือก", ROPE, 262)]
    for key, name, col, top in panels:
        y0, y1 = top + 34, top + 180
        ex, avg = c9["คู่ตัวอย่าง"][key], c9[key]
        p.append(f'<rect x="8" y="{top}" width="{W - 16}" height="196" rx="10" fill="#fafafa" stroke="{C["grid"]}"/>')
        p.append(text(24, top + 22, f"{name} · correlation คู่ตัวอย่าง {B.fmt(ex['corr'])} · เฉลี่ย 200 คู่ {B.fmt(avg['corr'])}",
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
        p.append(text(W - R - 6, y0 + 8, f"ช่วงทดสอบอยู่ในกรอบ {B.fmt(ex['ในกรอบ'])}%", 11.5, C["purple"], "end", 700))
    p.append(text((L + W - R) / 2 - 150, H - 14, "← ช่วงเลือก 250 วัน", 11, MUTED, "middle"))
    p.append(text((L + W - R) / 2 + 150, H - 14, "ช่วงทดสอบ 250 วัน →", 11, MUTED, "middle"))
    alt = (f"กราฟสองแผง ระยะห่างของ A เทียบ B ตลอด {ndays} วัน คู่ไม่มีเชือก correlation {B.fmt(c9['คู่ตัวอย่าง']['ไม่มีเชือก']['corr'])} "
           f"ระยะห่างเดินขึ้นไปเรื่อย ๆ ช่วงทดสอบอยู่ในกรอบ {B.fmt(c9['คู่ตัวอย่าง']['ไม่มีเชือก']['ในกรอบ'])}% "
           f"คู่มีเชือก correlation {B.fmt(c9['คู่ตัวอย่าง']['มีเชือก']['corr'])} แกว่งแรงกว่าแต่กลับมารอบศูนย์ "
           f"อยู่ในกรอบ {B.fmt(c9['คู่ตัวอย่าง']['มีเชือก']['ในกรอบ'])}%")
    cap = ("แกนตั้ง = A ห่างจากราคาเทียบกับ B กี่ % (นับจากวันแรก) · คู่ตัวอย่างหนึ่งคู่ต่อแบบที่มีค่าใกล้ค่าเฉลี่ยของแบบตัวเอง · "
           "เส้นประ = รอยต่อช่วงเลือกกับช่วงทดสอบ · ราคาทั้งหมดสร้างขึ้น ไม่ใช่เหรียญจริง")
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
    p = [text(L, 22, "ไม้บรรทัดวัดจากช่วงเลือก แล้วตรึงไว้ไปวัดช่วงทดสอบ", 13, INK, weight=700),
         f'<rect x="{L}" y="{y0}" width="{xd - L:.1f}" height="{y1 - y0}" fill="{C["purple"]}" fill-opacity=".05"/>']
    for k in (-2, -1, 0, 1, 2):
        col = C["axis"] if k == 0 else (C["purple"] if abs(k) == 2 else C["grey"])
        dash = "" if k == 0 else ' stroke-dasharray="5 4"'
        p.append(f'<line x1="{L}" y1="{Y(k):.1f}" x2="{W - R}" y2="{Y(k):.1f}" stroke="{col}" stroke-width="1.3"{dash}/>')
        p.append(text(L - 8, Y(k) + 4, ("+" if k > 0 else "") + B.fmt(k), 10.5, col, "end"))
    p.append(text(W - R - 4, Y(2) - 6, "+2 ระยะแกว่ง", 10.5, C["purple"], "end", 700))
    p.append(text(W - R - 4, Y(-2) + 14, "−2 ระยะแกว่ง", 10.5, C["purple"], "end", 700))
    p.append(text(W - R - 4, Y(0) - 6, "ค่ากลาง", 10.5, MUTED, "end"))
    pts = [(X(i), Y(v)) for i, v in enumerate(z)]
    p.append(f'<polyline points="{_poly(pts[:nf])}" fill="none" stroke="{NOROPE}" stroke-width="1.8"/>')
    p.append(f'<polyline points="{_poly(pts[nf - 1:])}" fill="none" stroke="{NOROPE}" stroke-width="1.8" stroke-opacity=".55"/>')
    for i in range(nf, len(z)):
        if abs(z[i]) > 2:
            p.append(f'<circle cx="{pts[i][0]:.1f}" cy="{pts[i][1]:.1f}" r="1.9" fill="{C["red"]}"/>')
    p.append(f'<line x1="{xd:.1f}" y1="{y0 - 8}" x2="{xd:.1f}" y2="{y1}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    p.append(text(L + 8, y0 + 16, f"ช่วงเลือก: ใน ±1 {B.fmt(st['ช่วงเลือกในหนึ่งระยะ'])}% · ใน ±2 {B.fmt(st['ช่วงเลือกในสองระยะ'])}%",
                  11.5, C["purple"], weight=700))
    p.append(text(xd + 10, y0 + 16, f"ช่วงทดสอบ: ใน ±2 แค่ {B.fmt(st['ช่วงทดสอบในสองระยะ'])}% · จุดแดง = วันที่หลุดกรอบ",
                  11.5, C["red"], weight=700))
    p.append(text(L, y1 + 22, "วันที่ 1", 10.5, C["grey"], "middle"))
    p.append(text(xd, y1 + 22, f"วันที่ {B.fmt(nf)}", 10.5, C["grey"], "middle"))
    p.append(text(W - R, y1 + 22, f"วันที่ {B.fmt(c9['จำลอง']['วัน'])}", 10.5, C["grey"], "end"))
    p.append(text(L - 44, y0 - 10, "z", 11, MUTED))
    alt = (f"กราฟเส้นระยะห่างของคู่ไม่มีเชือกในหน่วยระยะแกว่ง ช่วงเลือกอยู่ในกรอบ ±2 ราว {B.fmt(st['ช่วงเลือกในสองระยะ'])}% "
           f"แต่ในช่วงทดสอบอยู่ในกรอบเดิมแค่ {B.fmt(st['ช่วงทดสอบในสองระยะ'])}% และหลุดกรอบเป็นช่วงยาว")
    cap = (f"คู่ไม่มีเชือกตัวอย่างเดียวกับภาพบน · ค่ากลางและระยะแกว่งวัดจาก {B.fmt(nf)} วันแรกเท่านั้น · "
           f"ในช่วงเลือกแถบ ±1 มีวันราว 2 ใน 3 ({B.fmt(st['ช่วงเลือกในหนึ่งระยะ'])}%) ตามนิยาม · ช่วงทดสอบใช้ไม้บรรทัดเดิม ไม่วัดใหม่")
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
                f'<line x1="{mid:.1f}" y1="{y + 11}" x2="{mid:.1f}" y2="{y - 16}" stroke="{C["green"]}" stroke-width="2"/>',
                f'<path d="M{mid - 5:.1f},{y - 10} l5,-8 l5,8 z" fill="{C["green"]}"/>',
                f'<circle cx="{mid:.1f}" cy="{y - 24}" r="5" fill="none" stroke="{C["green"]}" stroke-width="2"/>', a, b]
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
    rows = [("chain", "โซ่ที่มีวันล็อก", "spot กับ dated futures", "สัญญาชำระราคาวันหมดอายุ", "เงินสดหมดระหว่างทาง (บท 4)"),
            ("pull", "เชือกที่มีคนคอยดึง", "โทเคนที่แลกคืนเป็นเหรียญแม่ได้", "คนที่แลกคืนได้ซื้อขายจนระยะหด",
             "คิวแลกคืนยาว · การแลกถูกระงับ"),
            ("spring", "ยางยืด", "เหรียญที่แข่งในกลุ่มเดียวกัน", "ปัจจัยร่วมกระทบทั้งคู่ ไม่มีใครบังคับ",
             "ข่าวเฉพาะตัว · ตลาดเปลี่ยนมุมมองถาวร"),
            ("dash", "เส้นที่วาดเอง", "คู่ที่เจอจากการค้นข้อมูลย้อนหลัง", "ไม่มีเหตุผลที่อธิบายได้",
             "ความบังเอิญจากการค้นมาก (บท 10)")]
    W, rh, top = 760, 88, 58
    H = top + rh * len(rows) + 18
    p = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>',
         text(250, 30, "อะไรดึงกลับ", 12, MUTED, weight=700), text(520, 30, "พังเมื่อ", 12, MUTED, weight=700)]
    # ลูกศรด้านซ้าย: บนผูกแน่น → ล่างต้องพึ่งข้อมูล
    p.append(f'<line x1="20" y1="{top + 8}" x2="20" y2="{H - 26}" stroke="{C["grey"]}" stroke-width="2"/>')
    p.append(f'<path d="M14,{H - 30} l6,12 l6,-12 z" fill="{C["grey"]}"/>')
    p.append(text(30, top + 2, "ผูกแน่น", 10.5, C["grey"]))
    p.append(text(30, H - 8, "ต้องพึ่งหลักฐานจากข้อมูล", 10.5, C["grey"]))
    for i, (kind, name, ex, pull, fail) in enumerate(rows):
        y = top + i * rh
        hi = kind == "spring"
        p.append(f'<rect x="36" y="{y}" width="{W - 46}" height="{rh - 10}" rx="9" fill="{"#f5f3ff" if hi else "#fafafa"}" '
                 f'stroke="{C["purple"] if hi else C["grid"]}" stroke-width="{1.6 if hi else 1}"/>')
        p.append(text(50, y + 24, name, 13, INK, weight=700))
        p.append(text(50, y + 44, ex, 11, MUTED))
        p += _icon(kind, 60, 210, y + 62)
        p.append(text(250, y + 34, pull, 11.5, INK))
        p.append(text(520, y + 34, fail, 11.5, C["red"]))
        if hi:
            p.append(text(W - 22, y + 64, "A–B ของมินอยู่ขั้นนี้", 11.5, C["purple"], "end", 700))
    alt = ("ผังบันไดเชือกสี่ขั้นจากผูกแน่นลงไปหลวม โซ่ที่มีวันล็อก เชือกที่มีคนคอยดึง ยางยืด และเส้นที่วาดเอง "
           "แต่ละขั้นบอกว่าอะไรดึงสองราคากลับ และพังเมื่อไร คู่ A–B ของมินอยู่ขั้นยางยืด")
    cap = ("ยิ่งลงล่าง กลไกที่บังคับให้สองราคากลับมาหากันยิ่งอ่อน และหลักฐานต้องมาจากข้อมูลที่ไม่ได้ใช้เลือกคู่ · "
           "perp (บท 7) คือเชือกไม่มีวันล็อกที่มีค่าดึงทุกรอบ")
    return wrap(W, H, alt, p, cap, "แนวคิด", narrow=True)
