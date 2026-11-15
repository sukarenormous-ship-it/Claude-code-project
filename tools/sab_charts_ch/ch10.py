"""บท 10 — คู่ที่สวยที่สุดจาก 200 คู่ · สเปกกราฟของบท

sab-two-humps  : (v2) คู่ไม่มีเชือก 200 คู่กับคู่มีเชือก 200 คู่ (ชุดบท 9) แบ่งตามสัดส่วนวันในกรอบช่วงทดสอบ
                 คู่ปลอมกองสองหัว (หลุดไกล / โชคดีเกือบเต็ม) · คู่จริงกองที่ 85–100% → ทำไมยกเกณฑ์แล้วคู่ปลอมแทบไม่ลด
(sab-selection-bias และ sab-seed-spread อยู่ใน tools/sab_charts.py กลาง)
"""

from sab_charts import chart, wrap, text, nice_ticks, C, B

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
