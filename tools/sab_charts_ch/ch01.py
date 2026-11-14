"""บท 1 — ค่าผ่านทางสองขา และนิ้วที่จับเชือก · สเปกกราฟของบท

sab-cost-roundtrip (★): ค่าผ่านทางไปกลับสองขาที่สามระดับค่าธรรมเนียม (taker 0.05% · maker 0.02% ถ้าได้ครบ · 0.1% ของมินใน nq)
แท่งแนวนอนซ้อนสองส่วน (ส่วนต่างราคาซื้อ-ขาย + ค่าธรรมเนียม) · แกนเป็นค่าผ่านทางล้วน (ไม่วาด basis 3,000 ทั้งก้อน
เพราะ 240 จะเหลือแค่ 8% ของแกน — กฎ "หนึ่งกราฟหนึ่งประเด็น") · ส่วนที่เหลือจาก 3,000 เขียนเป็นป้ายท้ายแท่ง
sab-orderbook (☆): ภาพแนวคิดสมุดคำสั่ง — คำสั่งซื้อทันทีข้ามส่วนต่าง · คำสั่งตั้งรอรอในแถว
"""
from sab_charts import chart, wrap, text, nice_ticks, C, B


@chart("sab-cost-roundtrip")
def _cost_roundtrip(fig):
    lv = fig["ch01"]["สามระดับ"]
    fee = fig["บัญชีมิน"]["ค่าธรรมเนียม"]
    basis = fig["บัญชีมิน"]["BTC"]["basis"]
    rows = [("taker", f"taker {B.fmt(fee['taker'])}%", "cash-and-carry"),
            ("maker", f"maker {B.fmt(fee['maker'])}%", "ถ้าได้ครบทุกขา"),
            ("มินในnq", f"{B.fmt(fee['มินในnq'])}%", "ของมินใน nq")]
    W, H = 760, 300
    L, R, T = 196, 210, 92
    rh, gap = 34, 30
    top = max(-lv[k]["สองขา"] for k, _, _ in rows)
    ticks = [t for t in nice_ticks(0, top) if t >= 0]
    hi = max(ticks[-1], top)
    X = lambda v: L + v / hi * (W - L - R)  # noqa: E731
    out = []
    ybot = T + len(rows) * (rh + gap) - gap
    for t in ticks:
        out.append(f'<line x1="{X(t):.1f}" y1="{T - 8}" x2="{X(t):.1f}" y2="{ybot + 6}" '
                   f'stroke="{C["axis"] if t == 0 else C["grid"]}" stroke-width="{1.5 if t == 0 else 1}"/>')
        out.append(text(X(t), ybot + 22, B.fmt(t), 11, C["grey"], "middle"))
    for i, (k, name, sub) in enumerate(rows):
        d = lv[k]
        y = T + i * (rh + gap)
        sp, fe = -d["ส่วนต่างสองขา"], -d["ค่าธรรมเนียมสองขา"]
        out.append(text(L - 12, y + 15, name, 12.5, C["ink"], "end", 700))
        out.append(text(L - 12, y + 31, sub, 10.5, C["muted"], "end"))
        x = X(0)
        if sp:
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{X(sp) - X(0):.1f}" height="{rh}" fill="{C["amber"]}"/>')
            x = X(sp)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{X(sp + fe) - x:.1f}" height="{rh}" fill="{C["red"]}"/>')
        out.append(text(X(sp + fe) + 8, y + 15, f"−{B.fmt(sp + fe)}", 12.5, C["red"], "start", 700))
        out.append(text(X(sp + fe) + 8, y + 31,
                        f"basis เหลือ {B.fmt(d['3000ลบสองขา'])}",
                        10.5, C["muted"]))
    # callout ม่วงที่แถว taker (ตัวเลขที่ร้อยแก้วพูดถึง)
    t0 = lv["taker"]
    cx = X(-t0["สองขา"]) - 4
    out.append(f'<rect x="{X(0) - 3:.1f}" y="{T - 4}" width="{cx - X(0) + 7:.1f}" height="{rh + 8}" rx="4" fill="none" '
               f'stroke="{C["purple"]}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    out.append(text(X(0), T - 12,
                    f"สองขา × (ส่วนต่าง {B.fmt(-t0['ส่วนต่าง'])} + ค่าธรรมเนียม {B.fmt(-t0['ค่าธรรมเนียมไปกลับ'])}) "
                    f"= {B.fmt(-t0['สองขา'])}", 11, C["purple"], "start", 700))
    lx = L
    for name, col in (("Bid-Ask Spread", C["amber"]), ("ค่าธรรมเนียม", C["red"])):
        out.append(f'<rect x="{lx}" y="{T - 46}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 36, name, 11.5, C["muted"]))
        lx += 36 + 6.5 * len(name)
    out.append(text(24, 26, "ค่าผ่านทางไปกลับครบสองขา (1 BTC)", 13, C["ink"], weight=700))
    alt = (f"แท่งแนวนอนสามแถว ค่าผ่านทางไปกลับสองขา taker {B.fmt(-t0['สองขา'])} เหลือจาก basis "
           f"{B.fmt(t0['3000ลบสองขา'])} · maker ถ้าได้ครบ {B.fmt(-lv['maker']['สองขา'])} · 0.1% ต่อข้าง "
           f"{B.fmt(-lv['มินในnq']['สองขา'])} เหลือ {B.fmt(lv['มินในnq']['3000ลบสองขา'])}")
    cap = ("แกนคือค่าผ่านทางล้วน ไม่ใช่ basis ทั้งก้อน · "
           "maker นับส่วนต่างเป็นศูนย์เฉพาะเมื่อได้ราคาที่ตั้งรอครบทุกขา")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-orderbook")
def _orderbook(fig):
    bt = fig["บัญชีมิน"]["BTC"]
    bid, ask, mid = bt["bid"], bt["ask"], bt["spot"]
    step = ask - mid                                   # 10 ต่อชั้นในภาพ (ภาพแนวคิด)
    W, H = 760, 330
    cx, rowh = 300, 30
    asks = [ask + step * 2 * i for i in (2, 1, 0)]
    bids = [bid - step * 2 * i for i in (0, 1, 2)]
    sizes_a, sizes_b = [70, 110, 150], [140, 100, 60]   # ความยาวแถบ = ปริมาณที่รอ (แนวคิด ไม่ใช่ตัวเลข)
    out = [text(24, 26, "สมุดคำสั่ง (order book): สองราคาตอนซื้อขาย", 13, C["ink"], weight=700)]
    y = 56
    out.append(text(cx - 120, y - 6, "ราคา", 11, C["muted"], "end"))
    out.append(text(cx - 100, y - 6, "คนที่รอขาย / รอซื้อ", 11, C["muted"]))
    for i, p in enumerate(asks):
        yy = y + i * rowh
        out.append(text(cx - 120, yy + 19, B.fmt(p) if p == ask else "สูงกว่า", 12 if p == ask else 10.5,
                        C["red"], "end", 700 if p == ask else None))
        out.append(f'<rect x="{cx - 100}" y="{yy + 5}" width="{sizes_a[i]}" height="{rowh - 10}" rx="3" fill="{C["red"]}" '
                   f'fill-opacity="{0.9 if p == ask else 0.35}"/>')
    ym = y + 3 * rowh
    out.append(f'<line x1="{cx - 200}" y1="{ym + 14}" x2="{cx + 90}" y2="{ym + 14}" stroke="{C["purple"]}" stroke-dasharray="5 4"/>')
    out.append(text(cx - 120, ym + 19, B.fmt(mid), 12, C["purple"], "end", 700))
    out.append(text(cx - 100, ym + 19, "ราคากลาง (mid) — ราคาที่กราฟโชว์ ไม่มีใครซื้อขายได้ที่นี่", 11, C["purple"]))
    for i, p in enumerate(bids):
        yy = ym + rowh + i * rowh
        out.append(text(cx - 120, yy + 19, B.fmt(p) if p == bid else "ต่ำกว่า", 12 if p == bid else 10.5,
                        C["green"], "end", 700 if p == bid else None))
        out.append(f'<rect x="{cx - 100}" y="{yy + 5}" width="{sizes_b[i]}" height="{rowh - 10}" rx="3" fill="{C["green"]}" '
                   f'fill-opacity="{0.9 if p == bid else 0.35}"/>')
    # คำอธิบายด้านขวา
    rx = cx + 120
    ya = y + 2 * rowh + 15
    yb = ym + rowh + 15
    out.append(f'<line x1="{rx - 6}" y1="{ya}" x2="{cx + 60}" y2="{ya}" stroke="{C["ink"]}" stroke-width="1.2"/>')
    out.append(text(rx, ya - 4, f"ask {B.fmt(ask)}: คำสั่งซื้อทันทีได้ของที่ราคานี้", 11.5, C["ink"], weight=700))
    out.append(text(rx, ya + 13, "(taker ข้ามส่วนต่างขึ้นไปหาคนที่รอขาย)", 10.5, C["muted"]))
    out.append(f'<line x1="{rx - 6}" y1="{yb}" x2="{cx + 60}" y2="{yb}" stroke="{C["ink"]}" stroke-width="1.2"/>')
    out.append(text(rx, yb - 4, f"bid {B.fmt(bid)}: คำสั่งขายทันทีได้ราคานี้", 11.5, C["ink"], weight=700))
    out.append(text(rx, yb + 13, "คำสั่งตั้งรอ (maker) ไปต่อแถวตรงนี้ แล้วรอคนมาชน", 10.5, C["muted"]))
    out.append(text(rx, ym + 19, f"ส่วนต่างราคาซื้อ-ขาย = {B.fmt(ask - bid)}", 12, C["purple"], weight=700))
    alt = (f"ภาพแนวคิดสมุดคำสั่ง ด้านบนคือคนที่รอขาย ราคาต่ำสุด ask {B.fmt(ask)} ด้านล่างคือคนที่รอซื้อ ราคาสูงสุด bid "
           f"{B.fmt(bid)} ราคากลาง {B.fmt(mid)} อยู่ตรงกลางและไม่มีใครซื้อขายได้ที่ราคานั้น")
    cap = "ความยาวแถบแทนปริมาณที่รออยู่ ไม่ใช่ตัวเลขจริง · ซื้อทันทีได้ ask ขายทันทีได้ bid ช่องว่างตรงกลางคือค่าผ่านทางที่ไม่มีบรรทัดไหนบอก"
    return wrap(W, H, alt, out, cap, "แนวคิด")
