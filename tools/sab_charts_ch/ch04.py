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
              ("บัญชีหลักประกัน", [r["หลักประกัน"] for r in rows], C["amber"]),
              ("เงินสดอิสระ", [r["เงินสดอิสระ"] for r in rows], C["blue"])]
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
                    f" → โอนจากเงินสดอิสระ {B.fmt(c4['ต้องโอน'])}", 11, C["purple"], "start", 700))
    lx = f.L
    for name, _, col in series:
        out.append(f'<rect x="{lx}" y="{f.T - 44}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, f.T - 34, name, 11.5, C["muted"]))
        lx += 34 + 8 * len(name)
    out.append(text(f.L, f.T - 62, "กำไรเกิดในเหรียญ แต่เงินถูกเรียกจากบัญชีหลักประกัน — ที่โอนไปช่วยได้มีแค่เงินสดอิสระ",
                    13, C["ink"], weight=700))
    alt = (f"กราฟแท่งสี่ช่วงเวลา แต่ละช่วงมีสามแท่ง กำไรที่ค้างในเหรียญ บัญชีหลักประกัน และเงินสดอิสระ "
           f"สิ้นวันที่ 9 เหรียญมีกำไร {B.fmt(series[0][1][1])} แต่บัญชีหลักประกันเหลือ {B.fmt(c4['หลักประกันหลังชำระ'])} "
           f"จึงต้องโอนเงินสดอิสระ {B.fmt(c4['ต้องโอน'])} เงินสดอิสระลดจาก {B.fmt(rows[0]['เงินสดอิสระ'])} เหลือ "
           f"{B.fmt(c4['เงินสดอิสระหลังโอน'])}")
    cap = (f"แท่งไม่รวมเงิน {B.fmt(s0)} ที่ซื้อเหรียญ · equity = {B.fmt(s0)} + สามแท่ง · ราคาขึ้น 10% วันที่ 9 "
           f"equity เปลี่ยนแค่ {B.fmt(c4['equity_เปลี่ยน'])} แต่เงินย้ายกระเป๋า {B.fmt(c4['ต้องโอน'])}")
    return wrap(W, H, alt, out, cap, "สอน")
