"""เล่ม 2 บท 7 — เข้าเมื่อไร ออกเมื่อไร · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch07 เท่านั้น)

sab2-entry-path   : เส้นทาง X 40 วัน (มือ) · เส้นเข้า 1 / 1.5 / 2 / 2.5 ฝั่งลบ · แถบออก ±0.5
sab2-entry-ou     : 🎲 โลก OU φ 0.9 · เงินต่อปีของแต่ละเส้นเข้า ที่ต้นทุนต่อไม้ 2 / 6 / 10
sab2-entry-ltcdot : 📡 Z ของ LTC บน DOT (ไม้บรรทัดช่วงเลือก) ช่วงเลือก → ช่วงตรวจ · เส้นเข้า 1 / 2 / 2.5 · แถบออก ±0.5
"""

from sab_charts import B, C, chart, grouped_bars, text, wrap

L, R, T, BM = 64, 24, 56, 250


def _frame(lo, hi, W, ticks):
    y = lambda v: BM - (v - lo) / (hi - lo) * (BM - T)  # noqa: E731
    out = []
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{y(g):.1f}" x2="{W - R}" y2="{y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    return out, y


def _band(y, W, half):
    return (f'<rect x="{L}" y="{y(half):.1f}" width="{W - L - R}" height="{y(-half) - y(half):.1f}" '
            f'fill="{C["grey"]}" fill-opacity="0.15"/>')


def _hline(y, W, v, col, lab, right=True, dy=-5):
    out = [f'<line x1="{L}" y1="{y(v):.1f}" x2="{W - R}" y2="{y(v):.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="6 4"/>']
    out.append(text(W - R - 4 if right else L + 4, y(v) + dy, lab, 10.5, col, "end" if right else "start", 700))
    return out


@chart("sab2-entry-path")
def _path(fig):
    m = fig["ch07"]["มือ"]
    X = m["X"]
    W, H = 760, 320
    out, y = _frame(-3, 2, W, [-3, -2, -1, 0, 1, 2])
    out.append(_band(y, W, m["ออก"]))
    cols = [C["amber"], C["green"], C["purple"], C["red"]]
    for ln, col in zip(m["เส้น"], cols):
        out += _hline(y, W, -ln["เส้น"], col, f"เส้นเข้า {B.fmt(ln['เส้น'])} ({ln['ไม้']} ไม้)", right=False)
    n = len(X)
    xp = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
    pts = " ".join(f"{xp(i):.1f},{y(v):.1f}" for i, v in enumerate(X))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="1.6" stroke-opacity="0.6"/>')
    for i, v in enumerate(X):
        out.append(f'<circle cx="{xp(i):.1f}" cy="{y(v):.1f}" r="3.2" fill="{C["blue"]}"/>')
    for d in (1, 10, 20, 30, 40):
        out.append(text(xp(d - 1), BM + 16, f"วัน {d}", 10.5, C["grey"], "middle"))
    out.append(text(L, T - 30, f"X ของคู่จำลอง {m['วัน']} วัน (Mean 0 · SD 1 จึงเท่ากับ Z) กับเส้นเข้าสี่เส้น", 13, C["ink"], weight=700))
    out.append(text(L, T - 12, f"แถบเทา = ช่วง ±{B.fmt(m['ออก'])} ที่การ์ดออก", 11, C["muted"]))
    alt = (f"X {m['วัน']} วัน ต่ำสุด {B.fmt(m['ต่ำสุด'])} สูงสุด {B.fmt(m['สูงสุด'])} เส้นเข้า 1 1.5 2 2.5 ได้ "
           f"{', '.join(str(x['ไม้']) for x in m['เส้น'])} ไม้")
    cap = f"โลกเชือก φ {B.fmt(m['phi'])} หนึ่งเส้นทาง ปัดทศนิยมหนึ่งตำแหน่ง · เส้นเข้าแสดงเฉพาะฝั่งลบซึ่งเป็นฝั่งที่ X ไปถึง"
    return wrap(W, H, alt, out, cap, "จำลอง")


@chart("sab2-entry-ou")
def _ou(fig):
    o = fig["ch07"]["ou"]["phi09"]
    rows = list(o["แถว"].values())
    cats = [f"เส้น {B.fmt(r['เส้น'])}" for r in rows]
    costs = fig["ch07"]["ค่า"]["ต้นทุนสามระดับ"]
    series = [(f"ต้นทุนต่อไม้ {costs[0]}", [r["ปัดx1"] for r in rows], C["green"]),
              (f"ต้นทุน {costs[1]}", [r["ปัดx3"] for r in rows], C["amber"]),
              (f"ต้นทุน {costs[2]}", [r["ปัดx5"] for r in rows], C["red"])]
    out = grouped_bars(cats, series, f"โลก φ {B.fmt(o['phi'])}: เงินต่อปี (ดอลลาร์ · 10 ชุด) ของแต่ละเส้นเข้า")
    alt = (f"เงินต่อปี ต้นทุน 2: {', '.join(B.fmt(r['ปัดx1']) for r in rows)} · ต้นทุน 6: "
           f"{', '.join(B.fmt(r['ปัดx3']) for r in rows)} · ต้นทุน 10: {', '.join(B.fmt(r['ปัดx5']) for r in rows)}")
    cap = (f"price_pair φ {B.fmt(o['phi'])} · {fig['ch07']['ค่า']['โลก']} โลก × {fig['ch07']['ค่า']['ปีต่อโลก']} ปี · "
           "ออก 0.5 · ถือไม่เกิน 30 วัน · คิดจากเลขปัดในตาราง")
    return wrap(760, 330, alt, out, cap, "จำลอง")


@chart("sab2-entry-ltcdot")
def _ltc(fig):
    r = fig["ch07"]["จริง"]
    g = r["LTC-DOT"]["กราฟ"]
    W, H = 760, 330
    out, y = _frame(-3, 7, W, [-2, 0, 2, 4, 6])
    out.append(_band(y, W, 0.5))
    for v, col, dy, right in ((1, C["amber"], 14, False), (2, C["purple"], 14, False), (2.5, C["red"], -5, False)):
        out += _hline(y, W, v, col, f"เส้นเข้า {B.fmt(v)}", right=right, dy=dy)
    n = g["รวม"] - 1
    xp = lambda i: L + i / n * (W - L - R)  # noqa: E731
    pts = " ".join(f"{xp(i):.1f},{y(v):.1f}" for i, v in zip(g["i"], g["z"]))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2" stroke-linejoin="round"/>')
    xb = xp(g["แบ่ง"])
    out.append(f'<line x1="{xb:.1f}" y1="{T}" x2="{xb:.1f}" y2="{BM}" stroke="{C["ink"]}" stroke-dasharray="5 4" stroke-width="1.3"/>')
    out.append(text(xb - 6, T + 14, "ช่วงเลือก", 11, C["ink"], "end", 700))
    out.append(text(xb + 6, T + 14, "ช่วงตรวจ", 11, C["ink"], "start", 700))
    out.append(text(L, T - 30, "Z ของ LTC บน DOT วัดด้วยไม้บรรทัดของช่วงเลือก", 13, C["ink"], weight=700))
    out.append(text(L, T - 12, "แถบเทา = ช่วง ±0.5 ที่การ์ดออก", 11, C["muted"]))
    out.append(text(L, BM + 16, r["ช่วงเลือก"]["เริ่ม"], 10.5, C["grey"], "start"))
    out.append(text(xb, BM + 16, r["ช่วงตรวจ"]["เริ่ม"], 10.5, C["grey"], "middle"))
    out.append(text(W - R, BM + 16, r["ช่วงตรวจ"]["จบ"], 10.5, C["grey"], "end"))
    ld = r["LTC-DOT"]
    alt = (f"Z ของ LTC บน DOT ช่วงเลือกแกว่ง {B.fmt(ld['Zเลือกต่ำสุด'])} ถึง {B.fmt(ld['Zเลือกสูงสุด'])} รอบศูนย์ "
           f"ช่วงตรวจขึ้นไปแกว่ง {B.fmt(ld['Zตรวจต่ำสุด'])} ถึง {B.fmt(ld['Zตรวจสูงสุด'])} เฉลี่ย {B.fmt(ld['Zตรวจเฉลี่ย'])}")
    cap = (f"Binance ราคาปิดรายวัน · h {B.fmt(ld['h'])} · Mean {B.fmt(ld['Mean'])} · SD {B.fmt(ld['SD'])} จากช่วงเลือก · "
           "แสดงทุก 7 วัน · ช่วงทดสอบสุดท้ายไม่ได้แตะ")
    return wrap(W, H, alt, out, cap, "จริง")
