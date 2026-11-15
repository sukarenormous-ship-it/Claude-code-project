"""บท 7 — Perp: เชือกที่ไม่มีวันล็อก · สเปกกราฟของบท

sab-funding-paths  (★): funding สะสม 90 รอบของสถานะเดียวกันภายใต้สี่เส้นทาง (ราบ · พุ่งแล้วแผ่ว · กลับขั้ว · สลับ)
                        + เส้นค่าธรรมเนียม maker 80 + จุดที่กฎ "ติดลบ 3 รอบติดแล้วออก" ทำงาน (กลับขั้ว +340 · สลับ −45)
sab-funding-breakeven (v2 ตอน ข): ค่าธรรมเนียม 80 จ่ายตั้งแต่ต้น · รอบละ 10 ต้อง 8 รอบ · เทียบสมุดจริง 3 รอบของมิน (+20.50 แล้วออก)
(☆ sab-funding-rounds ยังไม่ทำ — บทชนเพดานคำ)
"""

from sab_charts import chart, wrap, text, Frame, C, B


def _m2(v):
    """เงินในป้าย: จำนวนเต็มไม่มีทศนิยม · ไม่ลงตัวพิมพ์สองตำแหน่งให้ตรงกับร้อยแก้ว (40.30 ไม่ใช่ 40.3)"""
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"


def _sgn(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-funding-paths")
def _funding_paths(fig):
    c7 = fig["ch07"]
    g, p, rule = c7["กราฟ"], c7["สี่เส้นทาง"], c7["กฎออก"]
    fee = c7["ค่าธรรมเนียมเปิดปิด"]["maker"]
    n = c7["รอบ"]["ใน30วัน"]
    W, H = 760, 370
    f = Frame(0, max(max(v) for v in g.values()), W, H, L=64, R=128, T=64, Bm=290, pad=0.06)
    xs = list(range(1, n + 1))
    X = lambda x: f.L + (x - 1) / (n - 1) * (W - f.L - f.R)  # noqa: E731
    out = f.grid([0, fee, p["สลับ"]["fundingรวม"], p["ราบ"]["fundingรวม"], p["พุ่งแล้วแผ่ว"]["fundingรวม"]])
    # เส้นค่าธรรมเนียม
    yf = f.y(fee)
    out.append(f'<line x1="{f.L}" y1="{yf:.1f}" x2="{W - f.R}" y2="{yf:.1f}" stroke="{C["muted"]}" '
               f'stroke-dasharray="4 4" stroke-width="1.3"/>')
    out.append(text(X(62), yf - 6, f"ค่าธรรมเนียม {B.fmt(fee)} (maker)", 10.5, C["muted"], "middle"))
    # ราบกับกลับขั้วทับกัน 45 รอบแรก: วาดราบเส้นหนาไว้ใต้ ให้เห็นเป็นขอบน้ำเงินรอบเส้นแดง
    series = [("ราบ", C["blue"], "", 5.5), ("พุ่งแล้วแผ่ว", C["green"], "", 2.5), ("กลับขั้ว", C["red"], "", 2.2),
              ("สลับ", C["amber"], ' stroke-dasharray="7 4"', 2.5)]
    for name, col, dash, sw in series:
        pts = " ".join(f"{X(x):.1f},{f.y(v):.1f}" for x, v in zip(xs, g[name]))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}" '
                   f'stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        last = g[name][-1]
        out.append(text(X(n) + 8, f.y(last) + 4, f"{name} {B.fmt(p[name]['fundingรวม'])}", 11.5, col, "start", 700))
    # จุดที่กฎออกทำงาน: ① กลับขั้ว ② สลับ
    pts = [(rule["รอบที่ออกกลับขั้ว"], g["กลับขั้ว"][rule["รอบที่ออกกลับขั้ว"] - 1], "1"),
           (rule["รอบที่ออกสลับ"], g["สลับ"][rule["รอบที่ออกสลับ"] - 1], "2")]
    for x, y, lab in pts:
        out.append(f'<circle cx="{X(x):.1f}" cy="{f.y(y):.1f}" r="8" fill="#fff" stroke="{C["purple"]}" stroke-width="2.2"/>')
        out.append(text(X(x), f.y(y) + 4, lab, 10.5, C["purple"], "middle", 700))
    # ป้ายแกน x (จำนวนรอบ < 100 · ไม่ใช่เลขลอย)
    for x in (1, 30, 45, 60, n):
        out.append(text(X(x), f.Bm + 16, str(x), 10.5, C["grey"], "middle"))
    out.append(text((f.L + W - f.R) / 2, f.Bm + 34, "รอบ funding (90 รอบ = 30 วันในตัวอย่างนี้)", 11.5, C["muted"], "middle"))
    fl, al = p["กลับขั้ว"], p["สลับ"]
    out.append(text(f.L, f.Bm + 64, f"① กลับขั้ว: กฎออกรอบที่ {rule['รอบที่ออกกลับขั้ว']} → สุทธิ "
                    f"{_sgn(fl['กฎmaker'])} (ถือต่อ {_sgn(fl['สุทธิmaker'])})", 11.5, C["purple"], "start", 700))
    out.append(text(f.L + (W - f.L - f.R) / 2 + 20, f.Bm + 64, f"② สลับ: กฎออกรอบที่ {rule['รอบที่ออกสลับ']} → สุทธิ "
                    f"{_sgn(al['กฎmaker'])} (ถือต่อ {_sgn(al['สุทธิmaker'])})", 11.5, C["purple"], "start", 700))
    out.append(text(f.L, f.T - 36, "funding สะสม 90 รอบ ของสถานะเดียวกัน (1 BTC)", 13, C["ink"], weight=700))
    alt = (f"กราฟเส้นสี่เส้น funding สะสม 90 รอบ เส้นทางราบจบที่ {B.fmt(p['ราบ']['fundingรวม'])} "
           f"พุ่งแล้วแผ่วจบที่ {B.fmt(p['พุ่งแล้วแผ่ว']['fundingรวม'])} กลับขั้วขึ้นไปแล้วคืนจนเหลือ 0 "
           f"สลับขึ้นช้า ๆ จบที่ {B.fmt(p['สลับ']['fundingรวม'])} เส้นประค่าธรรมเนียม {B.fmt(fee)} "
           f"กฎออกเมื่อติดลบสามรอบติดช่วยเส้นทางกลับขั้วจาก {B.fmt(fl['สุทธิmaker'])} เป็น {_sgn(fl['กฎmaker'])} "
           f"แต่ทำให้เส้นทางสลับจาก {_sgn(al['สุทธิmaker'])} เหลือ {B.fmt(al['กฎmaker'])}")
    cap = "Mark Price ตรึง 100,000 จึงยังไม่รวมกำไรจากราคาสองขา"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-funding-breakeven")
def _funding_breakeven(fig):
    """ตอน ข: ค่าธรรมเนียมเปิดปิด 80 จ่ายครบตั้งแต่ต้น · funding รอบละ 10 ต้อง 8 รอบ (64 ชั่วโมง) จึงพอ
    เทียบสมุดจริงของมิน 10 → 40.30 → 20.50 แล้วออกที่รอบ 3"""
    c7 = fig["ch07"]
    v2 = c7["v2"]
    fee = c7["ค่าธรรมเนียมเปิดปิด"]["maker"]
    per = c7["รอบ"]["fundingต่อรอบ"]
    need = v2["สามรอบ"]["รอบพอค่าธรรมเนียม"]
    hrs = v2["สามรอบ"]["ชั่วโมงพอค่าธรรมเนียม"]
    real = [0] + [r["สะสม"] for r in v2["สมุด"]]
    n = need + 2
    W, H = 760, 330
    L, R, T, Bm = 64, 24, 64, 270
    top = per * n
    X = lambda k: L + k / n * (W - L - R)                        # noqa: E731
    Y = lambda v: Bm - v / top * (Bm - T)                        # noqa: E731
    out = [text(L, 24, "ค่าธรรมเนียมจ่ายครบตั้งแต่ต้น ส่วน funding ค่อย ๆ เข้าทีละรอบ", 13, C["ink"], weight=700)]
    for g in range(0, top + 1, 20):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" '
                   f'stroke="{C["axis"] if g == 0 else C["grid"]}" stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    for k in range(0, n + 1):
        out.append(text(X(k), Bm + 18, str(k), 10.5, C["grey"], "middle"))
    out.append(text((L + W - R) / 2, Bm + 38, f"รอบ funding (รอบละ {c7['รอบ']['ชั่วโมงต่อรอบ']} ชั่วโมงในตัวอย่างนี้)",
                    11.5, C["muted"], "middle"))
    # เส้นค่าธรรมเนียม
    out.append(f'<line x1="{L}" y1="{Y(fee):.1f}" x2="{W - R}" y2="{Y(fee):.1f}" stroke="{C["red"]}" '
               f'stroke-dasharray="6 4" stroke-width="1.6"/>')
    out.append(text(L + 6, Y(fee) - 7, f"ค่าธรรมเนียมเปิดปิด maker {B.fmt(fee)} (จ่ายแน่ทั้งก้อน)", 11.5, C["red"], weight=700))
    # ถ้าได้รอบละ 10 ทุกรอบ: ขั้นบันได
    d = f"M{X(0):.1f},{Y(0):.1f}"
    for k in range(1, n + 1):
        d += f" H{X(k):.1f} V{Y(per * k):.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="{C["green"]}" stroke-width="2.4"/>')
    out.append(text(X(need - 2), Y(per * (need - 4)), f"ถ้าได้รอบละ {B.fmt(per)} ทุกรอบ", 11.5, C["green"], "start", 700))
    out.append(f'<circle cx="{X(need):.1f}" cy="{Y(fee):.1f}" r="5.5" fill="{C["purple"]}"/>')
    out.append(text(X(need) - 10, Y(fee) - 26, f"รอบ {need} ({hrs} ชั่วโมง) จึงพอค่าธรรมเนียม", 11.5, C["purple"], "end", 700))
    # สมุดจริงของมิน 3 รอบ
    pts = " ".join(f"{X(k):.1f},{Y(v):.1f}" for k, v in enumerate(real))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2.4" stroke-linejoin="round"/>')
    for k, v in enumerate(real[1:], 1):
        out.append(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="3.6" fill="{C["blue"]}"/>')
    k3 = len(real) - 1
    out.append(f'<circle cx="{X(k3):.1f}" cy="{Y(real[-1]):.1f}" r="6" fill="#fff" stroke="{C["blue"]}" stroke-width="2.4"/>')
    out.append(text(X(k3) + 10, Y(real[-1]) + 16, f"สมุดจริงของมิน: ออกรอบ {k3} ที่ +{_m2(real[-1])}", 11.5, C["blue"], weight=700))
    out.append(text(X(1) + 6, Y(real[2]) - 8, f"+{_m2(real[1])} → +{_m2(real[2])} → +{_m2(real[3])}", 10.5, C["blue"]))
    alt = (f"เส้นประแดงค่าธรรมเนียม {B.fmt(fee)} อยู่ตั้งแต่รอบแรก ขั้นบันไดสีเขียวรอบละ {B.fmt(per)} ถึงเส้นที่รอบ {need} "
           f"ส่วนเส้นน้ำเงินของมินขึ้นเป็น {B.fmt(real[2])} แล้วลงเหลือ {B.fmt(real[3])} และออกที่รอบ {k3} ซึ่งยังต่ำกว่าเส้นค่าธรรมเนียมมาก")
    cap = "ชุด spot 1 BTC + short perp 1 BTC · ยังไม่รวมกำไรจากราคาสองขา (+30 ของมิน)"
    return wrap(W, H, alt, out, cap, "สอน")
