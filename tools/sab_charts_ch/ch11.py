"""บท 11 — สมุดบัญชีของคู่ · สเปกกราฟของบท

sab-pair-legs (★): สองวิธีนับเงินก้อนเดียวกัน — ซ้าย: กำไรรายขา (A +20 · B −10 · รวม +10)
ขวา: X = A − 2B ขยับ 0 → 1 คูณ 10 ชุด = +10 (แทนภาพ 3.2 fixed_holdings ที่มีสี่ช่อง)
sab-cost-steps (★): น้ำตก +20 −10 = 10 แล้วหักต้นทุน 4 / 3 / 5 → −2 (ภาพ 3.5 costs)
"""
from sab_charts import chart, wrap, waterfall, text, Frame, C, B


def sg(v):
    return ("+" if v > 0 else "") + B.fmt(v)


@chart("sab-pair-legs")
def _pair_legs(fig):
    c = fig["ch11"]
    a, b = c["ขา"]["A"], c["ขา"]["B"]
    tot = c["กำไรจากราคา"]
    x0, x1 = c["Xก่อนหลัง"]
    sets = c["เปิด"]["ชุด"]
    nA, nB = c["เปิด"]["A"]["จำนวน"], c["เปิด"]["B"]["จำนวน"]
    pA0, pB0 = c["เปิด"]["A"]["ราคา"], c["เปิด"]["B"]["ราคา"]
    pA1, pB1 = c["ราคาใหม่"]["A"], c["ราคาใหม่"]["B"]
    W, H = 760, 340
    out = []
    # ── ซ้าย: แท่งรายขา ──
    f = Frame(min(b, 0), max(a, tot), W=400, H=H, L=56, R=20, T=78, Bm=270)
    for g in (-10, 0, 10, 20):
        yy = f.y(g)
        out.append(f'<line x1="{f.L}" y1="{yy:.1f}" x2="{f.W - f.R}" y2="{yy:.1f}" '
                   f'stroke="{C["axis"] if g == 0 else C["grid"]}" stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(f.L - 8, yy + 4, B.fmt(g), 11, C["grey"], "end"))
    cols = [(f"ขา A {sg(nA)} × (+{B.fmt(pA1 - pA0)})", a, C["green"]),
            (f"ขา B {sg(nB)} × (+{B.fmt(pB1 - pB0)})", b, C["red"]),
            ("รวมสองขา", tot, C["purple"])]
    gw = (f.W - f.L - f.R) / 3
    for i, (name, v, col) in enumerate(cols):
        cx = f.L + gw * i + gw / 2
        y0, y1 = f.y(0), f.y(v)
        out.append(f'<rect x="{cx - 30:.1f}" y="{min(y0, y1):.1f}" width="60" height="{abs(y1 - y0):.1f}" rx="3" fill="{col}"/>')
        out.append(text(cx, (y1 - 8) if v >= 0 else (y1 + 18), sg(v), 13, col, "middle", 700))
        out.append(text(cx, f.Bm + 20, name, 11, C["muted"], "middle"))
    out.append(text(f.L - 40, 40, "วิธีที่ 1: คิดทีละขา", 12.5, C["ink"], weight=700))
    # ── ขวา: X ขยับ 0 → 1 ──
    L2, R2 = 470, W - 30
    lo, hi = -0.5, 1.6
    Y = lambda v: 270 - (v - lo) / (hi - lo) * (270 - 78)  # noqa: E731
    for g in (0, 1):
        out.append(f'<line x1="{L2}" y1="{Y(g):.1f}" x2="{R2}" y2="{Y(g):.1f}" '
                   f'stroke="{C["axis"] if g == 0 else C["grid"]}" stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L2 - 8, Y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    xa, xb = L2 + 40, R2 - 130
    out.append(f'<line x1="{xa}" y1="{Y(x0):.1f}" x2="{xb}" y2="{Y(x1):.1f}" stroke="{C["blue"]}" '
               f'stroke-width="2.5" stroke-dasharray="6 4" stroke-linecap="round"/>')
    for xx, v, lab in ((xa, x0, f"X = {B.fmt(pA0)} − 2 × {B.fmt(pB0)} = {B.fmt(x0)}"),
                       (xb, x1, f"X = {B.fmt(pA1)} − 2 × {B.fmt(pB1)} = {B.fmt(x1)}")):
        out.append(f'<circle cx="{xx}" cy="{Y(v):.1f}" r="5.5" fill="{C["blue"]}"/>')
        if v == x0:
            out.append(text(xx, Y(v) + 20, lab, 11, C["ink"], "middle"))
        else:
            out.append(text(xx + 10, Y(v) - 10, lab, 11, C["ink"], "start"))
    out.append(text(xa, 290, "ก่อน", 11, C["muted"], "middle"))
    out.append(text(xb, 290, "หลัง", 11, C["muted"], "middle"))
    out.append(f'<rect x="{R2 - 150}" y="{Y(0.42):.1f}" width="150" height="30" rx="6" fill="#f5f3ff" stroke="{C["purple"]}"/>')
    out.append(text(R2 - 75, Y(0.42) + 20, f"{B.fmt(sets)} ชุด × {B.fmt(x1 - x0)} = {sg(tot)}", 13,
                    C["purple"], "middle", 700))
    out.append(text(L2 - 20, 40, "วิธีที่ 2: จำนวนชุด × X ที่ขยับ", 12.5, C["ink"], weight=700))
    out.append(f'<line x1="440" y1="30" x2="440" y2="300" stroke="{C["axis"]}" stroke-dasharray="3 4"/>')
    alt = (f"สองแผง แผงซ้ายเป็นแท่งกำไรรายขา ขา A {sg(a)} ขา B {sg(b)} รวม {sg(tot)} "
           f"แผงขวาเป็น X จาก {B.fmt(x0)} ขึ้นเป็น {B.fmt(x1)} คูณ {B.fmt(sets)} ชุด ได้ {sg(tot)} เท่ากัน")
    cap = "ถือคงที่ตลอดช่วง ยังไม่หักต้นทุน · เส้นประช่วยอ่าน ไม่ใช่เส้นทางราคา"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-cost-steps")
def _cost_steps(fig):
    c = fig["ch11"]
    t = c["ต้นทุน"]
    steps = [("ขา A", c["ขา"]["A"], "delta"), ("ขา B", c["ขา"]["B"], "delta"),
             ("กำไรจากราคา", c["กำไรจากราคา"], "total"),
             ("ต้นทุนเข้า", -t["เข้า"], "delta"), ("ระหว่างถือ", -t["ระหว่างถือ"], "delta"),
             ("ต้นทุนออก", -t["ออก"], "delta"), ("กำไรสุทธิ", c["สุทธิ"], "total")]
    parts = waterfall(steps, f"ราคาให้ {sg(c['กำไรจากราคา'])} แต่ค่าผ่านทางรวม {B.fmt(t['รวม'])} — จบที่ "
                             f"{B.fmt(c['สุทธิ'])}", W=760, H=320)
    alt = (f"กราฟน้ำตก ขา A {sg(c['ขา']['A'])} ขา B {sg(c['ขา']['B'])} ได้กำไรจากราคา "
           f"{B.fmt(c['กำไรจากราคา'])} หักต้นทุนเข้า {B.fmt(t['เข้า'])} ระหว่างถือ {B.fmt(t['ระหว่างถือ'])} "
           f"ออก {B.fmt(t['ออก'])} เหลือกำไรสุทธิ {B.fmt(c['สุทธิ'])}")
    cap = "ไม่ใช่อัตราค่าธรรมเนียมของตลาดใด"
    return wrap(760, 320, alt, parts, cap, "สอน")
