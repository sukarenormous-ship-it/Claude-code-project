"""เล่ม 2 บท 7 — เข้าเมื่อไร ออกเมื่อไร · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json คีย์ ch07 เท่านั้น)

sab2-entry-path   : เส้นทาง X 40 วัน (มือ) · เส้นเข้า 1 / 1.5 / 2 / 2.5 ทั้งสองฝั่ง · แถบออก ±0.5
sab2-entry-ou     : 🎲 โลก OU φ 0.9 · เงินต่อปีของแต่ละเส้นเข้า ที่ต้นทุนต่อไม้ 2 / 6 / 10
sab2-entry-ltcdot : 📡 Z ของ LTC บน DOT (ไม้บรรทัดช่วงเลือก) ช่วงเลือก → ช่วงตรวจ · เส้นเข้า ±1 / ±2 / ±2.5 · แถบออก ±0.5
sab2-entry-thr    : แนวคิด · แรงดึงกลับที่คาดต่อวันของโลกที่มีกรอบ ±2 (ศูนย์ในกรอบ · 20% นอกกรอบ) กับแฝด OU φ 0.96
"""

from sab_charts import B, C, chart, grouped_bars, text, wrap

L, R = 64, 24


def _legend(out, items, x, y):
    """items = [(ชื่อ, สี)] เส้นประตามสีของเส้นเข้า"""
    for name, col in items:
        out.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 18}" y2="{y - 4}" stroke="{col}" stroke-width="2" stroke-dasharray="6 3"/>')
        out.append(text(x + 24, y, name, 11, col, weight=700))
        x += 36 + 6.6 * len(name)
    return x


@chart("sab2-entry-path")
def _path(fig):
    m = fig["ch07"]["มือ"]
    X = m["X"]
    W, H = 760, 350
    top, bm = 84, 278
    lo, hi = -3, 3
    y = lambda v: bm - (v - lo) / (hi - lo) * (bm - top)  # noqa: E731
    out = []
    for g in (-3, -2, -1, 0, 1, 2, 3):
        out.append(f'<line x1="{L}" y1="{y(g):.1f}" x2="{W - R}" y2="{y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    half = m["ออก"]
    out.append(f'<rect x="{L}" y="{y(half):.1f}" width="{W - L - R}" height="{y(-half) - y(half):.1f}" '
               f'fill="{C["grey"]}" fill-opacity="0.15"/>')
    cols = [C["amber"], C["green"], C["purple"], C["red"]]
    for ln, col in zip(m["เส้น"], cols):
        for v in (ln["เส้น"], -ln["เส้น"]):
            out.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{W - R}" y2="{y(v):.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="6 4"/>')
    n = len(X)
    xp = lambda i: L + i / (n - 1) * (W - L - R)  # noqa: E731
    pts = " ".join(f"{xp(i):.1f},{y(v):.1f}" for i, v in enumerate(X))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="1.6" stroke-opacity="0.6"/>')
    for i, v in enumerate(X):
        out.append(f'<circle cx="{xp(i):.1f}" cy="{y(v):.1f}" r="3.2" fill="{C["blue"]}"/>')
    # จุดที่ควรเห็น: วัน 3 แตะเส้น 1 กับ 1.5 ฝั่งบวก · วัน 16 แตะเส้น 2.5
    i3, i16 = 2, 15
    out.append(f'<circle cx="{xp(i3):.1f}" cy="{y(X[i3]):.1f}" r="6.5" fill="none" stroke="{C["ink"]}" stroke-width="1.4"/>')
    out.append(f'<line x1="{xp(i3) + 5:.1f}" y1="{y(X[i3]) - 5:.1f}" x2="{xp(i3) + 22:.1f}" y2="{y(2.75) + 3:.1f}" stroke="{C["ink"]}" stroke-width="1"/>')
    out.append(text(xp(i3) + 25, y(2.75) + 4, f"วัน 3: X {B.fmt(X[i3])} แตะเส้น 1 กับ 1.5 ฝั่งบวก (short X)", 10.5, C["ink"], "start", 700))
    out.append(f'<circle cx="{xp(i16):.1f}" cy="{y(X[i16]):.1f}" r="6.5" fill="none" stroke="{C["ink"]}" stroke-width="1.4"/>')
    out.append(text(xp(i16) - 10, y(X[i16]) + 4, f"วัน 16: X {B.fmt(X[i16])} ครั้งเดียวที่ถึงเส้น 2.5", 10.5, C["ink"], "end", 700))
    for d in (1, 10, 20, 30, 40):
        out.append(text(xp(d - 1), bm + 16, f"วัน {d}", 10.5, C["grey"], "middle"))
    out.append(text(L, top - 58, f"X ของคู่จำลอง {m['วัน']} วัน (Mean 0 · SD 1 จึงเท่ากับ Z) กับเส้นเข้าสี่เส้นทั้งสองฝั่ง", 13, C["ink"], weight=700))
    _legend(out, [(f"เส้นเข้า {B.fmt(ln['เส้น'])} ({ln['ไม้']} ไม้)", col) for ln, col in zip(m["เส้น"], cols)], L, top - 36)
    out.append(text(L, top - 14, f"แถบเทา = ช่วง ±{B.fmt(m['ออก'])} ที่การ์ดออก · เส้นประฝั่งบวกกับฝั่งลบสีเดียวกัน", 11, C["muted"]))
    alt = (f"X {m['วัน']} วัน ต่ำสุด {B.fmt(m['ต่ำสุด'])} สูงสุด {B.fmt(m['สูงสุด'])} เส้นเข้า 1 1.5 2 2.5 ทั้งสองฝั่ง ได้ "
           f"{', '.join(str(x['ไม้']) for x in m['เส้น'])} ไม้ วันที่ 3 X แตะเส้น 1 และ 1.5 ฝั่งบวก")
    cap = f"โลกเชือก φ {B.fmt(m['phi'])} หนึ่งเส้นทาง ปัดทศนิยมหนึ่งตำแหน่ง · เส้นเข้าแสดงทั้งฝั่งบวกและฝั่งลบ"
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
    W, H = 760, 350
    top, bm = 84, 278
    lo, hi = -3, 7
    y = lambda v: bm - (v - lo) / (hi - lo) * (bm - top)  # noqa: E731
    out = []
    for t in (-2, 0, 2, 4, 6):
        out.append(f'<line x1="{L}" y1="{y(t):.1f}" x2="{W - R}" y2="{y(t):.1f}" stroke="{C["axis"] if t == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if t == 0 else 1}"/>')
        out.append(text(L - 8, y(t) + 4, B.fmt(t), 11, C["grey"], "end"))
    out.append(f'<rect x="{L}" y="{y(0.5):.1f}" width="{W - L - R}" height="{y(-0.5) - y(0.5):.1f}" fill="{C["grey"]}" fill-opacity="0.15"/>')
    lines_ = ((1, C["amber"]), (2, C["purple"]), (2.5, C["red"]))
    for v, col in lines_:
        for s_ in (v, -v):
            out.append(f'<line x1="{L}" y1="{y(s_):.1f}" x2="{W - R}" y2="{y(s_):.1f}" stroke="{col}" stroke-width="1.4" stroke-dasharray="6 4"/>')
    n = g["รวม"] - 1
    xp = lambda i: L + i / n * (W - L - R)  # noqa: E731
    pts = " ".join(f"{xp(i):.1f},{y(v):.1f}" for i, v in zip(g["i"], g["z"]))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["blue"]}" stroke-width="2" stroke-linejoin="round"/>')
    xb = xp(g["แบ่ง"])
    out.append(f'<line x1="{xb:.1f}" y1="{top}" x2="{xb:.1f}" y2="{bm}" stroke="{C["ink"]}" stroke-dasharray="5 4" stroke-width="1.3"/>')
    out.append(text(xb - 6, top + 14, "ช่วงเลือก", 11, C["ink"], "end", 700))
    out.append(text(xb + 6, top + 14, "ช่วงตรวจ", 11, C["ink"], "start", 700))
    out.append(text(L, top - 58, "Z ของ LTC บน DOT วัดด้วยไม้บรรทัดของช่วงเลือก", 13, C["ink"], weight=700))
    _legend(out, [(f"เส้นเข้า {B.fmt(v)}", col) for v, col in lines_], L, top - 36)
    out.append(text(L, top - 14, "แถบเทา = ช่วง ±0.5 ที่การ์ดออก · เส้นประฝั่งบวกกับฝั่งลบสีเดียวกัน", 11, C["muted"]))
    out.append(text(L, bm + 16, r["ช่วงเลือก"]["เริ่ม"], 10.5, C["grey"], "start"))
    out.append(text(xb, bm + 16, r["ช่วงตรวจ"]["เริ่ม"], 10.5, C["grey"], "middle"))
    out.append(text(W - R, bm + 16, r["ช่วงตรวจ"]["จบ"], 10.5, C["grey"], "end"))
    ld = r["LTC-DOT"]
    alt = (f"Z ของ LTC บน DOT ช่วงเลือกแกว่ง {B.fmt(ld['Zเลือกต่ำสุด'])} ถึง {B.fmt(ld['Zเลือกสูงสุด'])} รอบศูนย์ "
           f"ช่วงตรวจขึ้นไปแกว่ง {B.fmt(ld['Zตรวจต่ำสุด'])} ถึง {B.fmt(ld['Zตรวจสูงสุด'])} เฉลี่ย {B.fmt(ld['Zตรวจเฉลี่ย'])}")
    cap = (f"Binance ราคาปิดรายวัน · h {B.fmt(ld['h'])} · Mean {B.fmt(ld['Mean'])} · SD {B.fmt(ld['SD'])} จากช่วงเลือก · "
           "แสดงทุก 7 วัน · ช่วงทดสอบสุดท้ายไม่ได้แตะ")
    return wrap(W, H, alt, out, cap, "จริง")


@chart("sab2-entry-thr")
def _thr(fig):
    c = fig["ch07"]
    t, k = c["มีกรอบ"], c["แรงดึงกรอบ"]
    W, H = 760, 340
    top, bm = 80, 270
    xs = k["X"]
    x0, x1 = min(k["แกนx"]), max(k["แกนx"])
    ylo, yhi = min(k["แกนy"]), max(k["แกนy"])
    xp = lambda v: L + (v - x0) / (x1 - x0) * (W - L - R)  # noqa: E731
    y = lambda v: bm - (v - ylo) / (yhi - ylo) * (bm - top)  # noqa: E731
    out = []
    for g in k["แกนy"]:
        out.append(f'<line x1="{L}" y1="{y(g):.1f}" x2="{W - R}" y2="{y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}" '
                   f'stroke-width="{1.5 if g == 0 else 1}"/>')
        out.append(text(L - 8, y(g) + 4, B.fmt(g), 11, C["grey"], "end"))
    band = t["กรอบ"]
    out.append(f'<rect x="{xp(-band):.1f}" y="{top}" width="{xp(band) - xp(-band):.1f}" height="{bm - top}" fill="{C["grey"]}" fill-opacity="0.13"/>')
    for g in k["แกนx"]:
        out.append(text(xp(g), bm + 16, B.fmt(g), 10.5, C["grey"], "middle"))
    out.append(text((L + W - R) / 2, bm + 34, "X วันนี้ (ห่างจากค่ากลาง)", 11.5, C["muted"], "middle"))
    # แฝด OU: เส้นเดียวต่อเนื่อง
    pts = " ".join(f"{xp(x):.1f},{y(v):.1f}" for x, v in zip(xs, k["แฝด"]))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{C["grey"]}" stroke-width="2.4" stroke-dasharray="7 4"/>')
    # โลกที่มีกรอบ: สามท่อน (นอกซ้าย · ในกรอบ · นอกขวา) ไม่ลากเส้นตั้งที่ขอบกรอบ
    segs = [[(x, v) for x, v in zip(xs, k["มีกรอบ"]) if x < -band], [(x, v) for x, v in zip(xs, k["มีกรอบ"]) if -band <= x <= band],
            [(x, v) for x, v in zip(xs, k["มีกรอบ"]) if x > band]]
    for sg in segs:
        pts = " ".join(f"{xp(x):.1f},{y(v):.1f}" for x, v in sg)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{C["purple"]}" stroke-width="2.8" stroke-linejoin="round"/>')
    for e in k["เส้นเข้าX"]:
        xx = xp(e["X"])
        out.append(f'<line x1="{xx:.1f}" y1="{top + 22}" x2="{xx:.1f}" y2="{bm}" stroke="{C["ink"]}" stroke-width="1.1" stroke-dasharray="3 3"/>')
        out.append(text(xx, top + 16, f"เส้น {B.fmt(e['เส้น'])}", 10.5, C["ink"], "middle", 700))
    out.append(text(xp(0), y(0) - 30, f"ในกรอบ ±{B.fmt(int(band))}: ไม่มีแรงดึง", 11.5, C["purple"], "middle", 700))
    out.append(text(xp(0), y(0) - 14, "X เดินสุ่ม ต้องรอโชคพากลับ", 11, C["purple"], "middle"))
    out.append(text(xp(-3.1), y(0.42), f"นอกกรอบ: ดึงกลับ {B.fmt(k['ดึงนอกเปอร์เซ็นต์'])}%", 11.5, C["purple"], "middle", 700))
    out.append(text(xp(-3.1), y(0.42) + 15, f"ของระยะทุกวัน (φ {B.fmt(t['phiนอก'])})", 11, C["purple"], "middle"))
    out.append(text(L, top - 54, "X ถูกดึงกลับเข้าหาค่ากลางวันละเท่าไร (ค่าที่คาด) ในสองโลกที่วัด φ ได้เท่ากัน", 13, C["ink"], weight=700))
    lx = L
    for name, col, dash, wd in ((f"โลกที่มีกรอบ (ดึงเฉพาะนอกกรอบ)", C["purple"], None, 2.8),
                                (f"แฝด OU φ {B.fmt(t['phiประมาณ'])} (ดึง {B.fmt(k['ดึงแฝดเปอร์เซ็นต์'])}% ของระยะทุกที่)", C["grey"], "7 4", 2.4)):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{lx}" y1="{top - 34}" x2="{lx + 20}" y2="{top - 34}" stroke="{col}" stroke-width="{wd}"{da}/>')
        out.append(text(lx + 26, top - 30, name, 11.5, C["muted"]))
        lx += 44 + 7 * len(name)
    out.append(text(L, top - 10, "แถบเทา = กรอบ · เส้นประตั้ง = เส้นเข้า 2 กับ 2.5 แปลงเป็นระยะของ X (× SD ระยะยาว "
                    + B.fmt(t["sdยาว"]) + ")", 11, C["muted"]))
    alt = (f"แกนนอน X จาก −4 ถึง 4 แกนตั้งแรงดึงกลับต่อวัน เส้นม่วงของโลกที่มีกรอบเป็นศูนย์ในกรอบ ±{B.fmt(int(band))} แล้วกระโดดเป็น "
           f"{B.fmt(k['ดึงนอกเปอร์เซ็นต์'])}% ของระยะนอกกรอบ เส้นประเทาของแฝด OU φ {B.fmt(t['phiประมาณ'])} ค่อย ๆ ชันขึ้นทุกระยะ")
    cap = (f"threshold_pair กรอบ ±{B.fmt(int(band))} · ในกรอบ φ 1 · นอกกรอบ φ {B.fmt(t['phiนอก'])} · แฝด OU φ {B.fmt(t['phiประมาณ'])} "
           f"SD {B.fmt(t['sdยาว'])} · แรงดึงที่คาด = (1 − φ) × ระยะ")
    return wrap(W, H, alt, out, cap, "แนวคิด")
