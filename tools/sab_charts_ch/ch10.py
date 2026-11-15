"""บท 10 — คู่ที่สวยที่สุดจาก 200 คู่ · สเปกกราฟของบท

sab-two-humps  : (v2) คู่ไม่มีเชือก 200 คู่กับคู่มีเชือก 200 คู่ (ชุดบท 9) แบ่งตามสัดส่วนวันในกรอบช่วงทดสอบ
                 คู่ปลอมกองสองหัว (หลุดไกล / โชคดีเกือบเต็ม) · คู่จริงกองที่ 85–100% → ทำไมยกเกณฑ์แล้วคู่ปลอมแทบไม่ลด
sab-false-pass : (v2 ตอน ค · 2) โอกาสเจออย่างน้อยหนึ่งคู่ที่ดูผ่าน ลอง 0–60 คู่ ที่ 5% (สมมติ ตอน ข) vs 30.5% (วัดได้ที่เกณฑ์ 85)
                 (คีย์ไม่ใช่ sab-tries-luck เพื่อไม่ชนกับ ☆ ของบท 15)
(sab-selection-bias และ sab-seed-spread อยู่ใน tools/sab_charts.py กลาง)
"""

from sab_charts import chart, wrap, text, lines, nice_ticks, Frame, C, B

NOROPE, ROPE = C["blue"], C["amber"]          # สีเดียวกับบท 9 (คู่ไม่มีเชือก น้ำเงิน · คู่มีเชือก ส้ม)


@chart("sab-two-humps")
def _two_humps(fig):
    rows = fig["ch10"]["v2"]["กองคู่"]
    cats = [f"ต่ำกว่า {r['ต่ำกว่า']}%" if r["ตั้งแต่"] == 0 else
            (f"{r['ตั้งแต่']}% ขึ้นไป" if r["ต่ำกว่า"] > 100 else f"{r['ตั้งแต่']}–{r['ต่ำกว่า']}%") for r in rows]
    fake = [r["ไม่มีเชือก"] for r in rows]
    real = [r["มีเชือก"] for r in rows]
    W, H = 760, 340
    L, R, T, Bm = 56, 24, 84, 280
    top = max(fake + real)
    ticks = [t for t in nice_ticks(0, top, 4) if t >= 0]
    hi = max(ticks[-1], top) * 1.08
    Y = lambda v: Bm - v / hi * (Bm - T)  # noqa: E731
    p = [text(L, 26, "คู่ปลอมกองสองหัว คู่จริงกองช่วง 85–100%", 13, C["ink"], weight=700)]
    for i, (name, col) in enumerate((("คู่ไม่มีเชือก 200 คู่", NOROPE), ("คู่มีเชือก 200 คู่", ROPE))):
        x = L + i * 190
        p.append(f'<rect x="{x}" y="44" width="11" height="11" rx="2" fill="{col}"/>')
        p.append(text(x + 16, 54, name, 11.5, C["muted"]))
    for t in ticks:
        p.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{W - R}" y2="{Y(t):.1f}" '
                 f'stroke="{C["axis"] if t == 0 else C["grid"]}" stroke-width="{1.4 if t == 0 else 1}"/>')
        p.append(text(L - 8, Y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
    gw = (W - L - R) / len(cats)
    bw = min(40, (gw - 20) / 2)
    for i, c in enumerate(cats):
        cx = L + gw * i + gw / 2
        for j, (v, col) in enumerate(((fake[i], NOROPE), (real[i], ROPE))):
            x = cx - (bw + 4) + j * (bw + 4)
            p.append(f'<rect x="{x:.1f}" y="{Y(v):.1f}" width="{bw:.1f}" height="{max(1, Bm - Y(v)):.1f}" rx="2" fill="{col}"/>')
            p.append(text(x + bw / 2, Y(v) - 6, B.fmt(v), 10.5, col, "middle", 700))
        p.append(text(cx, Bm + 18, c, 11.5, C["muted"], "middle"))
    p.append(text((L + W - R) / 2, H - 14, "Test Period อยู่ในกรอบ ±2 กี่ % ของวัน", 11.5, C["muted"], "middle"))
    alt = ("กราฟแท่งคู่ แบ่งคู่ตามสัดส่วนวันในกรอบช่วงทดสอบหกช่วง คู่ไม่มีเชือก "
           + " ".join(f"{c} {v} คู่" for c, v in zip(cats, fake))
           + " คู่มีเชือก " + " ".join(f"{c} {v} คู่" for c, v in zip(cats, real)))
    cap = "ชุดทดลองเดียวกับบท 9 · แบบละ 200 คู่ · ตัวเลขบนแท่งคือจำนวนคู่"
    return wrap(W, H, alt, p, cap, "จำลอง")


@chart("sab-false-pass")
def _false_pass(fig):
    c10 = fig["ch10"]
    cv = c10["v2"]["เส้นลองหลายครั้ง"]
    tries, many = c10["v2"]["ลองหลายครั้ง"], c10["ลองหลายครั้ง"]
    rate = c10["เกณฑ์ในกรอบ85"]["ปล่อยคู่ปลอม"]
    xs = cv["คู่"]
    series = [("สมมติ 5% ต่อคู่ (ตอน ข)", cv["ที่5"], C["blue"]),
              (f"วัดได้ {B.fmt(rate)}% ต่อคู่ ที่เกณฑ์ 85%", cv["ที่305"], C["red"])]
    marks = [(2, tries["สองคู่ที่305"], f"2 คู่: {B.fmt(tries['สองคู่ที่305'])}%"),
             (20, many["20"], f"20 คู่: {B.fmt(many['20'])}%"),
             (50, many["50"], f"50 คู่: {B.fmt(many['50'])}%")]
    xt = [(k, str(k)) for k in xs if k % 10 == 0]
    parts = lines(xs, series, "ยิ่งลองหลายคู่ ยิ่งแทบแน่นอนว่าเจอคู่ปลอมที่ดูผ่าน", unit="%",
                  xlabel="จำนวนคู่ไม่มีเชือกที่ลอง", W=760, H=320, xticks=xt)
    allv = cv["ที่5"] + cv["ที่305"]
    f = Frame(min(allv), max(allv), 760, 320)
    X = lambda k: f.L + (k - xs[0]) / (xs[-1] - xs[0]) * (760 - f.L - f.R)   # noqa: E731
    for (k, v, lab), (dx, dy, anc) in zip(marks, ((10, 4, "start"), (8, 20, "start"), (0, 22, "middle"))):
        parts.append(f'<circle cx="{X(k):.1f}" cy="{f.y(v):.1f}" r="4.5" fill="{C["purple"]}"/>')
        parts.append(text(X(k) + dx, f.y(v) + dy, lab, 11.5, C["purple"], anc, 700))
    alt = (f"เส้นสองเส้น โอกาสเจออย่างน้อยหนึ่งคู่ที่ดูผ่านเมื่อลอง 0 ถึง {xs[-1]} คู่ เส้นน้ำเงินที่ 5% ต่อคู่ถึง {B.fmt(many['20'])}% "
           f"ที่ 20 คู่และ {B.fmt(many['50'])}% ที่ 50 คู่ เส้นแดงที่ {B.fmt(rate)}% ต่อคู่ถึง {B.fmt(tries['สองคู่ที่305'])}% ตั้งแต่ 2 คู่")
    cap = "ชุดทดลองของบท 9 ให้ค่า 30.5% · โอกาสต่อคู่ถือว่าเท่ากันและไม่ขึ้นต่อกัน · 100% − (1 − โอกาสต่อคู่) คูณกันเท่าจำนวนคู่"
    return wrap(760, 320, alt, parts, cap, "สอน")
