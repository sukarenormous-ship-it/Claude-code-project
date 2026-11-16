"""เล่ม 2 บท 5 — ไม้บรรทัดที่เลื่อนได้ · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch05 เท่านั้น)

sab2-hand-split : ไม้มือ short X 10 ชุด · วันที่ 6 · วันที่ 7 · รวม — "กำไร" บนจอ (X วาดด้วย h ของแต่ละวัน) เทียบเงินจริง
                  และผลต่างที่มาจากการนิยามใหม่
sab2-sim-hpath  : 🎲 โลก h ไหล 2 → 2.2 (seed ตัวอย่าง) · h จริง · h ตรึงจาก 250 วันแรก · หน้าต่าง 60 / 120 วัน
sab2-btc-rollh  : 📡 BTC–ETH h หน้าต่าง 60 / 120 วัน ตลอดช่วงเลือก + ช่วงตรวจ เทียบ h ของทั้งช่วงเลือก
"""

from sab_charts import B, C, chart, grouped_bars, lines, text, wrap

GREY = C["grey"]


@chart("sab2-hand-split")
def _hand_split(fig):
    c = fig["ch05"]["บัญชี"]
    cats = ["วันที่ 5 → 6", "วันที่ 6 → 7", "รวมสองวัน"]
    jo = c["จอ"] + [c["รวมจอ"]]
    money = c["เงินจากราคา"] + [c["รวมเงิน"]]
    red = c["นิยามใหม่"] + [c["รวมนิยามใหม่"]]
    series = [("บนจอ: ชุด × X ที่วาดด้วย h ของวันนั้น", jo, C["amber"]),
              ("เงินจริงจากราคา", money, C["blue"]),
              ("ผลต่าง = ผลจากการนิยามใหม่", red, GREY)]
    parts = grouped_bars(cats, series, f"short X {c['ชุด']} ชุด เมื่อ h เปลี่ยนจาก {B.fmt(c['h0'])} เป็น {B.fmt(c['h1'])} ระหว่างถือ")
    alt = (f"แท่งสามกลุ่ม วันที่ 5 ถึง 6 บนจอ +{B.fmt(c['จอ'][0])} เงินจริง {B.fmt(c['เงินจากราคา'][0])} "
           f"วันที่ 6 ถึง 7 บนจอ +{B.fmt(c['จอ'][1])} เงินจริง +{B.fmt(c['เงินจากราคา'][1])} "
           f"รวมบนจอ +{B.fmt(c['รวมจอ'])} เงินจริง {B.fmt(c['รวมเงิน'])} ผลต่าง {B.fmt(c['รวมนิยามใหม่'])} มาจากการนิยามใหม่")
    cap = f"short X {c['ชุด']} ชุดตั้งแต่ราคาปิดวันที่ 5 · ยังไม่หักค่าธรรมเนียม"
    return wrap(760, 330, alt, parts, cap, "สอน")


def _band_lines(xs, series, title, lo, hi, ticks, W=760, L=64, R=24, T=56, Bm=250):
    """เส้นหลายเส้นบนแกน y ที่กำหนดช่วงเอง (lines() กลางเริ่มแกนที่ศูนย์ ซึ่งบีบ h ราว 2 จนอ่านไม่ออก)"""
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    X = lambda x: L + (x - xs[0]) / (xs[-1] - xs[0]) * (W - L - R)  # noqa: E731
    out = [text(L, T - 30, title, 13, C["ink"], weight=700)]
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for name, ys, col, dash in series:
        pts = " ".join(f"{X(x):.1f},{Y(v):.1f}" for x, v in zip(xs, ys) if v is not None)
        extra = ' stroke-dasharray="6 4"' if dash else ""
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.2"{extra} stroke-linejoin="round"/>')
    lx = L
    for name, _, col, _ in series:
        out.append(f'<rect x="{lx}" y="{T - 16}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 6, name, 11.5, C["muted"]))
        lx += 24 + 7.5 * len(name)
    return out, X, Y


@chart("sab2-sim-hpath")
def _sim_hpath(fig):
    g = fig["ch05"]["จำลอง"]["กราฟ"]
    n = len(g["จริง"])
    xs = [k * 5 for k in range(n)]
    series = [("h จริง", g["จริง"], C["green"], False),
              ("ตรึงจาก 250 วันแรก", [g["ตรึง"]] * n, GREY, True),
              ("หน้าต่าง 60 วัน", g["60"], C["amber"], False),
              ("หน้าต่าง 120 วัน", g["120"], C["blue"], False)]
    split = g["วันแบ่ง"]
    parts, X, Y = _band_lines(xs, series, "โลกที่ h ไหลจาก 2 ไป 2.2: ใครตามทัน", 1.8, 2.3, [1.8, 1.9, 2, 2.1, 2.2, 2.3])
    sx = X(split)
    parts.append(f'<line x1="{sx:.1f}" y1="56" x2="{sx:.1f}" y2="250" stroke="{C["purple"]}" stroke-dasharray="5 4" stroke-width="1.5"/>')
    parts.append(text(sx + 6, 242, "เริ่มช่วงเทรด →", 11, C["purple"], weight=700))
    parts.append(text(X(0), 266, "วันแรก", 10.5, GREY, "start"))
    parts.append(text(sx, 266, f"วัน {split}", 10.5, GREY, "middle"))
    parts.append(text(X(xs[-1]), 266, "วันสุดท้าย", 10.5, GREY, "end"))
    alt = (f"กราฟเส้นสี่เส้นของโลกจำลองหนึ่งชุด เส้นเขียวคือ h จริงที่ไหลจาก 2 ไป 2.2 "
           f"เส้นเทาประคือ h ตรึง {B.fmt(g['ตรึง'])} จาก 250 วันแรก เส้นส้มคือหน้าต่าง 60 วันซึ่งแกว่งมากกว่า "
           "เส้นน้ำเงินคือหน้าต่าง 120 วันซึ่งเรียบกว่าแต่ตามหลัง")
    cap = f"โลก h ไหล 2 → 2.2 · seed {g['seed']} · จุดทุก 5 วัน · เส้นประม่วงคือจุดเริ่มช่วงเทรด"
    return wrap(760, 290, alt, parts, cap, "จำลอง")


@chart("sab2-btc-rollh")
def _btc_rollh(fig):
    g = fig["ch05"]["จริง"]["BTC-ETH"]["กราฟ"]
    xs = g["วัน"]
    series = [("หน้าต่าง 60 วัน", g["60"], C["amber"]),
              ("หน้าต่าง 120 วัน", g["120"], C["blue"]),
              (f"ทั้งช่วงเลือก {B.fmt(g['ตรึง'])}", [g["ตรึง"]] * len(xs), GREY)]
    split = g["แบ่ง"]
    parts = lines(xs, series, "BTC บน ETH: h จาก 60 และ 120 วันล่าสุด", xticks=[(xs[0], "เริ่มช่วงเลือก"),
                                                                                  (split, "เริ่มช่วงตรวจ")])
    W, L, R, T, Bm = 760, 64, 24, 56, 250
    sx = L + (split - xs[0]) / (xs[-1] - xs[0]) * (W - L - R)
    parts.append(f'<line x1="{sx:.1f}" y1="{T}" x2="{sx:.1f}" y2="{Bm}" stroke="{C["purple"]}" stroke-dasharray="5 4" stroke-width="1.5"/>')
    parts.append(text(W - R, Bm + 16, "จบช่วงตรวจ", 10.5, GREY, "end"))
    alt = ("กราฟเส้น h ของ BTC บน ETH จากหน้าต่าง 60 วัน (ส้ม) และ 120 วัน (น้ำเงิน) ตลอดช่วงเลือกและช่วงตรวจ "
           f"เทียบเส้นเทาที่ {B.fmt(g['ตรึง'])} เส้นส้มแกว่งตั้งแต่ต่ำกว่าศูนย์จนเกิน 30 เส้นน้ำเงินแกว่งน้อยกว่าแต่ยังกว้าง")
    cap = f"ราคาปิดรายวัน Binance · h บนราคา · จุดทุก 5 วัน · {g['วันรวม']} วัน (ไม่แตะช่วงทดสอบสุดท้าย)"
    return wrap(760, 320, alt, parts, cap, "จริง")
