"""บท 6 — วันที่ 30: ปิดหรือถือ · สเปกกราฟของบท

sab-hold-or-close : ถือต่ออีก 60 วันได้เพิ่ม 550.75 (basis 500 + ไม่ต้องจ่ายค่าปิดวันนี้ − ค่าขาย spot วันหมดอายุ)
                    เทียบเส้นค่าเสียโอกาส 821.92 (hurdle 4%) และ 410.96 (hurdle 2%)
sab-carry-strip   : รอบชดเชย — ยอดสะสมของกำไรสุทธิ 2,846 ต่อรอบ 90 วัน ต้องกี่รอบจึงเท่าความเสียหายครั้งเดียว
                    125,000 (44 รอบ) หรือ 25,000 ถ้าวาง spot นอก exchange (8.8 รอบ)
"""
from sab_charts import chart, wrap, text, Frame, C, B


@chart("sab-hold-or-close")
def _hold_or_close(fig):
    d = fig["ch06"]["วันที่30"]
    W, H = 760, 340
    steps = [("basis ที่เหลือ", d["basis"]), ("ไม่ต้องจ่ายค่าปิดวันนี้", d["ค่าธรรมเนียมปิดตอนนี้"]),
             ("ค่าขาย spot วันหมดอายุ", -d["ค่าธรรมเนียมspotถ้าถือ"])]
    total, opp, opp2 = d["ถือได้เพิ่ม"], d["เสียโอกาส60วัน"], d["เสียโอกาสที่hurdle2"]
    f = Frame(0, opp, W, H, L=64, R=200, T=60, Bm=270, pad=0.14)
    out = f.grid([0, 200, 400, 600, 800])
    n = len(steps) + 1
    gw = (W - f.L - f.R) / n
    bw = min(70, gw * 0.6)
    run, prev = 0, None
    for i, (name, v) in enumerate(steps):
        cx = f.L + gw * i + gw / 2
        a, b = run, run + v
        col = C["green"] if v >= 0 else C["red"]
        ya, yb = f.y(a), f.y(b)
        out.append(f'<rect x="{cx - bw / 2:.1f}" y="{min(ya, yb):.1f}" width="{bw:.1f}" height="{max(1, abs(yb - ya)):.1f}" rx="2" fill="{col}"/>')
        out.append(text(cx, min(ya, yb) - 7, ("+" if v > 0 else "−") + B.fmt(abs(v)), 12, col, "middle", 700))
        out.append(text(cx, f.Bm + 18, name, 10.5, C["muted"], "middle"))
        if prev is not None:
            out.append(f'<line x1="{prev:.1f}" y1="{ya:.1f}" x2="{cx - bw / 2:.1f}" y2="{ya:.1f}" stroke="{C["axis"]}" stroke-dasharray="3 3"/>')
        prev = cx + bw / 2
        run = b
    cx = f.L + gw * (n - 1) + gw / 2
    yt = f.y(total)
    out.append(f'<line x1="{prev:.1f}" y1="{yt:.1f}" x2="{cx - bw / 2:.1f}" y2="{yt:.1f}" stroke="{C["axis"]}" stroke-dasharray="3 3"/>')
    out.append(f'<rect x="{cx - bw / 2:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{f.y(0) - yt:.1f}" rx="2" fill="{C["blue"]}"/>')
    out.append(text(cx, yt + 18, B.fmt(total), 12, "#ffffff", "middle", 700))
    out.append(text(cx, f.Bm + 18, "ถือได้เพิ่ม", 10.5, C["muted"], "middle"))
    # เส้นค่าเสียโอกาสสองระดับ
    x_end = W - f.R + 8
    for val, lab, col, dash in ((opp, f"ค่าเสียโอกาส 60 วัน · hurdle 4%: {B.fmt(opp)}", C["purple"], "6 4"),
                                (opp2, f"ถ้า hurdle 2%: {B.fmt(opp2)}", C["grey"], "3 3")):
        yy = f.y(val)
        out.append(f'<line x1="{f.L}" y1="{yy:.1f}" x2="{x_end:.1f}" y2="{yy:.1f}" stroke="{col}" stroke-dasharray="{dash}" stroke-width="1.6"/>')
        out.append(text(x_end + 4, yy + 4, lab, 11, col, "start", 700))
    # ช่องว่างที่ขาด
    gx = cx + bw / 2 + 12
    out.append(f'<line x1="{gx:.1f}" y1="{f.y(opp):.1f}" x2="{gx:.1f}" y2="{yt:.1f}" stroke="{C["red"]}" stroke-width="1.6"/>')
    for yy in (f.y(opp), yt):
        out.append(f'<line x1="{gx - 4:.1f}" y1="{yy:.1f}" x2="{gx + 4:.1f}" y2="{yy:.1f}" stroke="{C["red"]}" stroke-width="1.6"/>')
    out.append(text(gx + 8, (f.y(opp) + yt) / 2 + 4, f"ขาด {B.fmt(d['ปิดดีกว่า'][0])} → ปิดดีกว่า", 11.5, C["red"], "start", 700))
    out.append(text(f.L, f.T - 30, "วันที่ 30 ถือต่ออีก 60 วันได้เงินเพิ่มเท่าไร เทียบกับที่เงิน 125,000 หาได้จากทางอื่น",
                    13, C["ink"], weight=700))
    alt = (f"กราฟแท่งลอย ถือต่อได้ basis ที่เหลือ {B.fmt(d['basis'])} บวกค่าปิดวันนี้ที่ไม่ต้องจ่าย {B.fmt(d['ค่าธรรมเนียมปิดตอนนี้'])} "
           f"ลบค่าขาย spot วันหมดอายุ {B.fmt(d['ค่าธรรมเนียมspotถ้าถือ'])} รวม {B.fmt(total)} ต่ำกว่าเส้นค่าเสียโอกาส {B.fmt(opp)} "
           f"ที่ hurdle 4% อยู่ {B.fmt(d['ปิดดีกว่า'][0])} แต่สูงกว่าเส้น {B.fmt(opp2)} ที่ hurdle 2%")
    cap = (f"คิดที่ 1 BTC · วันที่ 30 spot {B.fmt(d['spot'])} futures {B.fmt(d['futures'])} · taker 0.05% · ค่าธรรมเนียมตอนเปิดจ่ายไปแล้ว "
           f"จึงไม่อยู่ในภาพ (เท่ากันทั้งสองทาง) · ค่าเสียโอกาสคิดบนทุนตั้งต้น {B.fmt(fig['บัญชีมิน']['ทุนภาค1']['รวม'])} "
           f"(บนเงินที่ปลดได้จริงราว {B.fmt(d['เสียโอกาสบนเงินที่ปลดได้'])} คำตอบไม่เปลี่ยน) · ยังไม่รวมส่วนต่างราคาซื้อ-ขาย")
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-carry-strip")
def _carry_strip(fig):
    r = fig["ch06"]["รอบชดเชย"]
    gain, n_all, n_small = r["กำไรต่อรอบ"], r["เสียทั้ง125000"], r["เสียเฉพาะ25000"]
    big = fig["บัญชีมิน"]["ทุนภาค1"]["รวม"]
    small = fig["ch06"]["เงินบนexchangeถ้าspotอยู่นอก"]
    W, H = 760, 340
    L, R, T, Bm = 74, 40, 64, 280
    top = gain * (n_all + 1)
    Y = lambda v: Bm - v / top * (Bm - T)                         # noqa: E731
    X = lambda k: L + k / (n_all + 2) * (W - L - R)               # noqa: E731
    out = []
    for g in (0, small, 50000, 75000, 100000, big):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    # ยอดสะสมแบบขั้นบันได รอบละ +2,846
    d = f"M{X(0):.1f},{Y(0):.1f}"
    for k in range(1, n_all + 1):
        d += f" H{X(k):.1f} V{Y(gain * k):.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="{C["green"]}" stroke-width="2.2"/>')
    # ความเสียหายครั้งเดียวสองขนาด
    for val, n, lab, col in ((big, n_all, f"เสียทั้งก้อน {B.fmt(big)} = {B.fmt(n_all)} รอบ (ราว {B.fmt(r['ปี'])} ปี)", C["red"]),
                             (small, n_small, f"เสียแค่เงินบน exchange {B.fmt(small)} = {B.fmt(n_small)} รอบ (ราว {B.fmt(r['ปี25000'])} ปี)", C["amber"])):
        yy = Y(val)
        out.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W - R}" y2="{yy:.1f}" stroke="{col}" stroke-dasharray="6 4" stroke-width="1.5"/>')
        out.append(f'<circle cx="{X(n):.1f}" cy="{yy:.1f}" r="5" fill="{C["purple"]}"/>')
        right = X(n) > W * 0.6
        out.append(text(X(n) + (-10 if right else 10), yy - 9, lab, 11.5, C["purple"], "end" if right else "start", 700))
    # หนึ่งครั้งที่ลบทุกอย่าง
    xe = X(n_all + 1)
    out.append(f'<line x1="{xe:.1f}" y1="{Y(gain * n_all):.1f}" x2="{xe:.1f}" y2="{Y(0) - 6:.1f}" stroke="{C["red"]}" stroke-width="2.4"/>')
    out.append(f'<polygon points="{xe - 6:.1f},{Y(0) - 12:.1f} {xe + 6:.1f},{Y(0) - 12:.1f} {xe:.1f},{Y(0):.1f}" fill="{C["red"]}"/>')
    out.append(text(xe - 8, Y(gain * n_all * 0.45), "ครั้งเดียว", 11.5, C["red"], "end", 700))
    out.append(text(L, Bm + 22, "รอบที่ 0", 10.5, C["grey"], "middle"))
    out.append(text(X(n_all), Bm + 22, f"รอบที่ {B.fmt(n_all)}", 10.5, C["grey"], "middle"))
    out.append(text((L + W - R) / 2, Bm + 42, f"จำนวนรอบ 90 วัน (กำไรสุทธิรอบละ {B.fmt(gain)})", 12, C["muted"], "middle"))
    out.append(text(L, T - 34, "ต้องเก็บกี่รอบ จึงเท่าความเสียหายครั้งเดียว", 13, C["ink"], weight=700))
    alt = (f"เส้นขั้นบันไดยอดสะสมกำไรสุทธิรอบละ {B.fmt(gain)} ต้อง {B.fmt(n_all)} รอบ ราว {B.fmt(r['ปี'])} ปี จึงถึง {B.fmt(big)} "
           f"ถ้าเงินที่เสี่ยงมีแค่ {B.fmt(small)} ต้อง {B.fmt(n_small)} รอบ แล้วความเสียหายครั้งเดียวลบยอดทั้งหมดกลับเป็นศูนย์")
    cap = (f"ยอดสะสมของ cash-and-carry ถ้าทุกรอบได้เท่าไม้ของมิน · รอบชดเชย = ความเสียหายครั้งเดียว ÷ กำไรต่อรอบ · "
           f"{B.fmt(small)} = หลักประกัน {B.fmt(fig['บัญชีมิน']['ทุนภาค1']['หลักประกัน'])} + เงินสดอิสระ "
           f"{B.fmt(fig['บัญชีมิน']['ทุนภาค1']['เงินสดอิสระ'])} เมื่อเก็บ spot ไว้นอก exchange · ไม่ใช่การพยากรณ์ว่า exchange จะล้ม — คือการถามว่าเสียครั้งเดียวต้องทำงานกี่ปีชดเชย")
    return wrap(W, H, alt, out, cap, "สอน")
