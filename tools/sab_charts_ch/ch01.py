"""บท 1 — ค่าผ่านทางสองขา และนิ้วที่จับเชือก · สเปกกราฟของบท

sab-cost-roundtrip (★): ค่าผ่านทางไปกลับสองขา (สี่ครั้ง) ที่สามระดับค่าธรรมเนียม (taker 0.05% · maker 0.02% ถ้าได้ครบ · 0.1% อัตราสองเท่า)
แท่งแนวนอนซ้อนสองส่วน (ส่วนต่างราคาซื้อ-ขาย + ค่าธรรมเนียม) · แกนเป็นค่าผ่านทางล้วน (ไม่วาด basis 3,000 ทั้งก้อน
เพราะ 240 จะเหลือแค่ 8% ของแกน — กฎ "หนึ่งกราฟหนึ่งประเด็น") · ส่วนที่เหลือจาก 3,000 เขียนเป็นป้ายท้ายแท่ง
sab-orderbook (★ v2): ภาพแนวคิดหน้าคำสั่งที่รออยู่ — กดซื้อทันทีได้ ask · กดขายทันทีได้ bid · ราคาบนกราฟอยู่กึ่งกลาง (ยังไม่พูดถึงคำสั่งตั้งรอ เพราะบทสอนในตอนหลัง)
"""
from sab_charts import chart, wrap, text, nice_ticks, C, B


@chart("sab-cost-roundtrip")
def _cost_roundtrip(fig):
    lv = fig["ch01"]["สามระดับ"]
    fee = fig["บัญชีมิน"]["ค่าธรรมเนียม"]
    basis = fig["บัญชีมิน"]["BTC"]["basis"]
    rows = [("taker", f"taker {B.fmt(fee['taker'])}%", "cash-and-carry"),
            ("maker", f"maker {B.fmt(fee['maker'])}%", "ถ้าได้ครบทุกขา"),
            ("มินในnq", f"{B.fmt(fee['มินในnq'])}%", "อัตราสองเท่า")]
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
    f4 = fig["ch01"]["v2"]["สี่ครั้ง"]["taker"]
    out.append(text(X(0), T - 12,
                    f"สี่ครั้ง × (ครึ่งช่องว่าง {B.fmt(f4['ครึ่งช่องว่าง'])} + ค่าธรรมเนียม {B.fmt(f4['ค่าธรรมเนียมต่อครั้ง'])}) "
                    f"= {B.fmt(f4['รวม'])}", 11, C["purple"], "start", 700))
    lx = L
    for name, col in (("ช่องว่างที่ข้าม", C["amber"]), ("ค่าธรรมเนียม", C["red"])):
        out.append(f'<rect x="{lx}" y="{T - 46}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 36, name, 11.5, C["muted"]))
        lx += 40 + 6.5 * len(name)
    out.append(text(24, 26, "ค่าผ่านทางไปกลับครบสองขา (1 BTC)", 13, C["ink"], weight=700))
    alt = (f"แท่งแนวนอนสามแถว ค่าผ่านทางไปกลับสองขา taker {B.fmt(-t0['สองขา'])} เหลือจาก basis "
           f"{B.fmt(t0['3000ลบสองขา'])} · maker ถ้าได้ครบ {B.fmt(-lv['maker']['สองขา'])} · 0.1% ต่อข้าง "
           f"{B.fmt(-lv['มินในnq']['สองขา'])} เหลือ {B.fmt(lv['มินในnq']['3000ลบสองขา'])}")
    cap = ("1 BTC · แกนคือค่าผ่านทางล้วน ไม่ใช่ basis ทั้งก้อน · "
           "maker นับช่องว่างเป็นศูนย์เฉพาะเมื่อได้ราคาที่ตั้งรอครบทั้งสี่ครั้ง")
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
    out = [text(24, 26, "หน้าคำสั่งที่รออยู่: กราฟโชว์ราคาเดียว แต่ซื้อขายจริงมีสองราคา", 13, C["ink"], weight=700)]
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
    out.append(f'<line x1="{cx - 200}" y1="{ym + 18}" x2="{cx + 90}" y2="{ym + 18}" stroke="{C["purple"]}" stroke-dasharray="5 4"/>')
    out.append(text(cx - 120, ym + 12, B.fmt(mid), 12, C["purple"], "end", 700))
    out.append(text(cx - 100, ym + 12, "ราคาบนกราฟ (กึ่งกลาง)", 11, C["purple"]))
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
    out.append(text(rx, ya - 4, f"ask {B.fmt(ask)}: กดซื้อทันที ได้ราคานี้", 11.5, C["ink"], weight=700))
    out.append(text(rx, ya + 13, "ราคาต่ำสุดที่มีคนรอขาย", 10.5, C["muted"]))
    out.append(f'<line x1="{rx - 6}" y1="{yb}" x2="{cx + 60}" y2="{yb}" stroke="{C["ink"]}" stroke-width="1.2"/>')
    out.append(text(rx, yb - 4, f"bid {B.fmt(bid)}: กดขายทันที ได้ราคานี้", 11.5, C["ink"], weight=700))
    out.append(text(rx, yb + 13, "ราคาสูงสุดที่มีคนรอซื้อ", 10.5, C["muted"]))
    out.append(text(rx, ym + 19, f"ช่องว่าง {B.fmt(ask)} − {B.fmt(bid)} = {B.fmt(ask - bid)}", 12, C["purple"], weight=700))
    alt = (f"ภาพแนวคิดหน้าคำสั่งที่รออยู่ ด้านบนคือคนที่รอขาย ราคาต่ำสุด ask {B.fmt(ask)} ด้านล่างคือคนที่รอซื้อ ราคาสูงสุด bid "
           f"{B.fmt(bid)} ราคาบนกราฟ {B.fmt(mid)} อยู่ตรงกลางและไม่มีใครซื้อขายได้ที่ราคานั้น")
    cap = "1 BTC · ความยาวแถบแทนปริมาณที่รออยู่ ไม่ใช่ตัวเลขจริง"
    return wrap(W, H, alt, out, cap, "แนวคิด")


@chart("sab-leverage-lines")
def _leverage_lines(fig):
    """v2: Margin ที่เหลือ (% ของที่วาง) เมื่อราคาสวน x% · เส้นละหนึ่งระดับ Leverage · ตกถึงศูนย์ที่ 100% ÷ เท่า
    เน้น 10 เท่า (หน้าจอของมิน) · spot 1 เท่าเป็นเส้นอ้างอิง (เสียเท่ากันเป็นเงิน แต่ยังเหลือเงินส่วนใหญ่)"""
    tab = fig["ch01"]["leverageตาราง"]
    lv = fig["ch01"]["leverage"]
    walk = fig["ch01"]["v2"]["หลักประกันเดิน"]["แถว"]
    levels = sorted(tab.values(), key=lambda r: r["เท่า"])
    xmax = max(r["สวนแล้วหมดเปอร์เซ็นต์"] for r in levels)
    W, H = 760, 340
    L, R, T, Bm = 70, 730, 84, 270
    X = lambda p: L + p / xmax * (R - L)                      # noqa: E731
    Y = lambda v: Bm - v / 100 * (Bm - T)                     # noqa: E731
    out = [text(16, 26, f"ยิ่งหลายเท่า ระยะก่อน Margin หมดยิ่งสั้น: {lv['เท่า']} เท่าหมดเมื่อราคาสวน "
                        f"{tab[str(lv['เท่า'])]['สวนแล้วหมดเปอร์เซ็นต์']}%", 13.5, C["ink"], weight=700)]
    for g in (0, 50, 100):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, Y(g) + 4, f"{g}%", 11, C["grey"], "end"))
    out.append(text(L - 56, T - 16, "Margin ที่เหลือ เทียบกับที่วาง", 11, C["muted"]))
    # spot 1 เท่า: จ่ายเต็ม · เส้นอ้างอิง
    out.append(f'<line x1="{X(0):.1f}" y1="{Y(100):.1f}" x2="{X(xmax):.1f}" y2="{Y(100 - xmax):.1f}" stroke="{C["blue"]}" '
               f'stroke-width="2" stroke-dasharray="6 4"/>')
    out.append(text(X(xmax) - 4, Y(100 - xmax) + 20, f"spot {fig['ch01']['v2']['spotเท่า']} เท่า (จ่ายเต็ม)", 11.5, C["blue"], "end", 700))
    for r in levels:
        k, z = r["เท่า"], r["สวนแล้วหมดเปอร์เซ็นต์"]
        hot = k == lv["เท่า"]
        col = C["purple"] if hot else C["muted"]
        out.append(f'<line x1="{X(0):.1f}" y1="{Y(100):.1f}" x2="{X(z):.1f}" y2="{Y(0):.1f}" stroke="{col}" '
                   f'stroke-width="{3 if hot else 1.8}" stroke-linecap="round"/>')
        out.append(f'<circle cx="{X(z):.1f}" cy="{Y(0):.1f}" r="4.5" fill="#fff" stroke="{col}" stroke-width="2"/>')
        last = z == xmax
        if last:                                               # ขวาสุดไม่มีที่ และซ้ายมีเส้นพาด: ป้ายไว้ใต้ตัวเลขแกน
            out.append(text(X(z), Bm + 33, f"{k} เท่า", 11.5, col, "middle", 700))
        else:
            out.append(text(X(z) + 7, Y(0) - 7, f"{k} เท่า", 11.5, col, "start", 700))
        out.append(text(X(z), Bm + 18, f"{z}%", 11, C["grey"], "middle"))
    # จุดจากตารางเดินเงิน: 10 เท่า ราคาสวน 5% เหลือ 500 (50%)
    r5 = walk["5"]
    px, py = X(r5["ราคาเปลี่ยนเปอร์เซ็นต์"]), Y(r5["เหลือเปอร์เซ็นต์"])
    out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{C["purple"]}"/>')
    lx, ly = X(xmax * .42), Y(24)                              # ช่องว่างระหว่างเส้น 5 เท่ากับ 2 เท่า
    out.append(f'<path d="M{px + 5:.1f},{py + 3:.1f} C{px + 60:.1f},{py + 20:.1f} {lx - 60:.1f},{ly - 4:.1f} {lx - 6:.1f},{ly - 4:.1f}" '
               f'fill="none" stroke="{C["purple"]}" stroke-width="1"/>')
    out.append(text(lx, ly, f"10 เท่า สวน {r5['ราคาเปลี่ยนเปอร์เซ็นต์']}%: เหลือ {B.fmt(r5['เหลือ'])} จาก {B.fmt(lv['หลักประกัน'])}",
                    11.5, C["purple"], "start", 700))
    out.append(text(X(0), Bm + 18, "0%", 11, C["grey"], "middle"))
    out.append(text((L + R) / 2, Bm + 40, "ราคาเดินสวนทางสถานะ (%)", 12, C["muted"], "middle"))
    alt = ("กราฟเส้นลาดลง Margin ที่เหลือเทียบกับที่วาง เมื่อราคาสวน " + " ".join(
        f"{r['เท่า']} เท่าหมดที่ {r['สวนแล้วหมดเปอร์เซ็นต์']}%" for r in levels) +
        f" ส่วน spot ที่จ่ายเต็มยังเหลือครึ่งหนึ่งเมื่อราคาสวน {xmax}%")
    cap = f"สถานะมูลค่า {B.fmt(lv['ถือ'])} · กติกาสอน: Margin หมดเมื่อขาดทุนเท่าที่วาง · ยังไม่นับการบังคับปิดก่อนถึงศูนย์"
    return wrap(W, H, alt, out, cap, "สอน")
