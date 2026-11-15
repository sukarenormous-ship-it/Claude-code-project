"""บท 4 — คืนที่ราคาขึ้น 10% · สเปกกราฟของบท

sab-two-pockets: แทนสเปกเดิมใน tools/sab_charts.py (แท่งซ้อนทั้งบัญชี) ซึ่งทำให้เงินสดอิสระ 14,700 → 3,480 และ
หลักประกันที่เหลือ 100 เล็กจนมองไม่เห็นข้างมูลค่า spot 100,000 · ฉบับนี้ตัดราคาที่ซื้อเหรียญออก แล้ววางสามกระเป๋า
(กำไรที่ค้างในเหรียญ · บัญชีหลักประกัน · เงินสดอิสระ) บนสเกลเดียวกัน — equity = ราคาที่ซื้อเหรียญ + สามแท่ง
"""
from sab_charts import chart, wrap, text, Frame, nice_ticks, C, B


@chart("sab-two-pockets")
def _two_pockets(fig):
    c4 = fig["ch04"]
    rows = c4["ตารางบัญชี"][2:]                      # เปิดครบสองขา → ชำระวันที่ 9 → โอนเติม → วันหมดอายุ
    s0 = fig["บัญชีมิน"]["BTC"]["spot"]
    names = {"shortfuturesวางหลักประกัน": "เปิดครบสองขา", "ชำระวันที่9": "ชำระสิ้นวันที่ 9",
             "หลังโอนเติม": "โอนเติมแล้ว", "ชำระวันหมดอายุ": "วันหมดอายุ"}
    series = [("กำไรที่ค้างในเหรียญ", [r["มูลค่าspot"] - s0 for r in rows], C["green"]),
              ("บัญชี Margin", [r["หลักประกัน"] for r in rows], C["amber"]),
              ("Free Cash", [r["เงินสดอิสระ"] for r in rows], C["blue"])]
    W, H = 760, 326
    vals = [v for _, s, _ in series for v in s]
    f = Frame(0, max(vals), W, H, T=84, Bm=276, pad=0.14)
    out = f.grid(nice_ticks(0, max(vals)))
    gw = (W - f.L - f.R) / len(rows)
    bw = 40
    pos = {}
    for i, r in enumerate(rows):
        cx = f.L + gw * i + gw / 2
        for j, (_, s, col) in enumerate(series):
            v = s[i]
            x = cx - 3 * (bw + 6) / 2 + j * (bw + 6)
            y0, y1 = f.y(0), f.y(v)
            out.append(f'<rect x="{x:.1f}" y="{y1:.1f}" width="{bw}" height="{max(1.5, y0 - y1):.1f}" rx="2" fill="{col}"/>')
            out.append(text(x + bw / 2, min(y1, y0 - 1.5) - 6, B.fmt(v), 10.5, C["ink"], "middle", 700))
            pos[(i, j)] = (x + bw / 2, y1)
        out.append(text(cx, f.Bm + 18, names.get(r["เหตุการณ์"], r["เหตุการณ์"]), 11.5, C["ink"], "middle", 700))
        out.append(text(cx, f.Bm + 34, f"equity {B.fmt(r['equity'])}", 11, C["muted"], "middle"))
    # callout: หลักประกันเหลือ 100 ทั้งที่ต้องมี 11,320
    mx, my = pos[(1, 1)]
    out.append(f'<line x1="{mx:.1f}" y1="{my - 22:.1f}" x2="{mx + 10:.1f}" y2="{f.T - 2:.1f}" stroke="{C["purple"]}" stroke-width="1.4"/>')
    out.append(text(mx + 14, f.T - 6, f"เหลือ {B.fmt(c4['หลักประกันหลังชำระ'])} · กติกาต้องมี {B.fmt(c4['หลักประกันที่ต้องมี'])}"
                    f" → โอนจาก Free Cash {B.fmt(c4['ต้องโอน'])}", 11, C["purple"], "start", 700))
    lx = f.L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{f.T - 44}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 34, name, 11.5, C["muted"]))
        lx += 34 + 8 * len(name)
    out.append(text(f.L, f.T - 62, "กำไรเกิดในเหรียญ แต่เงินถูกเรียกจากบัญชี Margin — ที่โอนไปช่วยได้มีแค่ Free Cash",
                    13, C["ink"], weight=700))
    alt = (f"กราฟแท่งสี่ช่วงเวลา แต่ละช่วงมีสามแท่ง กำไรที่ค้างในเหรียญ บัญชีหลักประกัน และเงินสดอิสระ "
           f"สิ้นวันที่ 9 เหรียญมีกำไร {B.fmt(series[0][1][1])} แต่บัญชีหลักประกันเหลือ {B.fmt(c4['หลักประกันหลังชำระ'])} "
           f"จึงต้องโอนเงินสดอิสระ {B.fmt(c4['ต้องโอน'])} เงินสดอิสระลดจาก {B.fmt(rows[0]['เงินสดอิสระ'])} เหลือ "
           f"{B.fmt(c4['เงินสดอิสระหลังโอน'])}")
    cap = f"ถือ spot 1 BTC กับ short futures 1 BTC · ทุน 125,000 · แท่งไม่รวม {B.fmt(s0)} ที่จ่ายซื้อเหรียญ"
    return wrap(W, H, alt, out, cap, "สอน")


@chart("sab-buffer-gauge")
def _buffer_gauge(fig):
    """กับดักกันชนสะสม: เงินสดอิสระที่เหลือหลังโอนเติมทุกคืน เทียบราคา futures ที่ขึ้นสะสมจากราคาเปิด
    เส้นตรงเพราะทุก 1 ที่ราคาขึ้นต้องโอน 1.1 (กติกาสอน 10%) · ต่ำกว่า 0 = เงินสดไม่พอโอน"""
    c4, v2 = fig["ch04"], fig["ch04"]["v2"]
    f0 = fig["บัญชีมิน"]["BTC"]["futures"]
    mult = c4["ตัวคูณหลักประกัน"]
    f9 = c4["คืนวันที่9"]["futures"]
    f10 = v2["หลังคืนวันที่9"]["futuresคืนถัดไป"]
    f15 = c4["dist"][2]["futures"]
    who = [("ทุน 125,000 (มิน)", fig["เรื่อง"]["part3"]["close"]["เงินสดอิสระ"], C["green"], v2["กันชน"]["ราคาหมด125000"],
            c4["กันชน"]["125000"]),
           ("ทุน 120,000 (ต้น)", c4["ต้นเงินสดอิสระ"], C["red"], v2["กันชน"]["ราคาหมด120000"], c4["กันชน"]["120000"])]
    left = lambda cash, F: cash - mult * (F - f0)  # noqa: E731
    lo, hi = left(who[1][1], f15), who[0][1]
    W, H = 760, 360
    f = Frame(lo, hi, W, H, T=86, Bm=290, pad=0.1)
    out = f.grid(nice_ticks(lo, hi))
    X = lambda F: f.L + (F - f0) / (f15 - f0) * (W - f.L - f.R)  # noqa: E731
    # พื้นใต้ศูนย์ = เงินสดไม่พอ
    out.append(f'<rect x="{f.L}" y="{f.y(0):.1f}" width="{W - f.L - f.R}" height="{f.Bm - f.y(0):.1f}" fill="#fef2f2"/>')
    out.append(text(f.L + 6, f.y(0) + 16, "ต่ำกว่าศูนย์ = เงินสดไม่พอโอน → ถูกบังคับปิด", 11, C["red"], "start", 700))
    for F in (f9, f10):
        out.append(f'<line x1="{X(F):.1f}" y1="{f.T}" x2="{X(F):.1f}" y2="{f.Bm}" stroke="{C["grey"]}" stroke-dasharray="4 4"/>')
    out.append(text(X(f9) - 6, f.T + 12, "คืนวันที่ 9", 11, C["muted"], "end", 700))
    out.append(text(X(f10) + 6, f.T + 12, "คืนถัดไป +3%", 11, C["muted"], "start", 700))
    for name, cash, col, zero_at, pct in who:
        out.append(f'<line x1="{X(f0):.1f}" y1="{f.y(cash):.1f}" x2="{X(f15):.1f}" y2="{f.y(left(cash, f15)):.1f}" '
                   f'stroke="{col}" stroke-width="2.4"/>')
        out.append(f'<circle cx="{X(zero_at):.1f}" cy="{f.y(0):.1f}" r="4" fill="#fff" stroke="{col}" stroke-width="2"/>')
        out.append(text(X(f0) + 6, f.y(cash) - 8, f"เริ่ม {B.fmt(cash)}", 11, col, "start", 700))
    # จุดที่เส้นข้ามศูนย์ (วงกลมขาว) อธิบายรวมที่มุมล่างซ้าย ซึ่งว่างเพราะสองเส้นยังอยู่เหนือศูนย์
    out.append(text(f.L + 6, f.Bm - 8, f"○ เงินสดหมด: ต้นที่ {B.fmt(who[1][3])} ({B.fmt(who[1][4])}%) · "
                    f"มินที่ {B.fmt(who[0][3])} ({B.fmt(who[0][4])}%)", 11, C["ink"], "start", 700))
    for v, F in ((c4["เงินสดอิสระหลังโอน"], f9), (-c4["ต้นขาด"], f9), (-v2["หลังคืนวันที่9"]["ขาด"], f10)):
        y = f.y(v)
        out.append(f'<circle cx="{X(F):.1f}" cy="{y:.1f}" r="4.5" fill="{C["purple"]}"/>')
        out.append(text(X(F) + 8, y + 4, B.fmt(v), 11.5, C["purple"], "start", 700))
    for F, lab in ((f0, B.fmt(f0)), (f9, B.fmt(f9)), (f15, B.fmt(f15))):
        out.append(text(X(F), f.Bm + 16, lab, 10.5, C["grey"], "middle"))
    out.append(text((f.L + W - f.R) / 2, f.Bm + 36, "ราคา futures (ขึ้นสะสมจากราคาเปิด)", 12, C["muted"], "middle"))
    lx = f.L
    for name, _, col, _, _ in who:
        out.append(f'<rect x="{lx}" y="{f.T - 40}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 30, name, 11.5, C["muted"]))
        lx += 34 + 8 * len(name)
    out.append(text(f.L, f.T - 58, "Free Cash ที่เหลือหลังโอนเติม เมื่อราคา futures ขึ้นสะสม", 13, C["ink"], weight=700))
    alt = (f"กราฟเส้นสองเส้นลาดลง เงินสดอิสระที่เหลือของทุน 125,000 เริ่ม {B.fmt(who[0][1])} และของทุน 120,000 เริ่ม "
           f"{B.fmt(who[1][1])} เส้นของต้นแตะศูนย์ที่ราคา futures {B.fmt(who[1][3])} ก่อนคืนวันที่ 9 ส่วนของมินเหลือ "
           f"{B.fmt(c4['เงินสดอิสระหลังโอน'])} ที่คืนวันที่ 9 แล้วแตะศูนย์ที่ {B.fmt(who[0][3])}")
    cap = f"ถือ spot 1 BTC กับ short futures 1 BTC ที่ {B.fmt(f0)} · กติกาหลักประกัน 10% ชำระสิ้นวัน"
    return wrap(W, H, alt, out, cap, "สอน")
