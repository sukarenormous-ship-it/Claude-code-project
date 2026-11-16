"""บท 15 เล่ม 2 — ต้นทุน ขนาด และการเสื่อมของกลยุทธ์ · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-capacity-curve  : กำไรสุทธิต่อไม้ตามขนาดขา (ตัวอย่างสอน 1% ต่อไม้ · สามก้อน) เทียบเส้นตรงจากขาละ 1,000 · ยอด · จุดคุ้มทุน
sab2-funding-years   : funding carry เฉลี่ยต่อเดือน ปีที่ 1 / 2 / 3 ของ BTC และ ETH เทียบค่าคาดจากช่วงเลือก
sab2-tracking-funnel : แผนภูมิควบคุมของ ETH ช่วงตรวจ · ผลสะสมเทียบที่คาด เส้นเตือน 1 SD × √n เส้นลงมือ 2 SD × √n
"""

from sab_charts import B, C, chart, text, wrap

INK, GREY = C["ink"], C["grey"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


@chart("sab2-capacity-curve")
def _capacity(fig):
    c = fig["ch15"]["มือ"]
    rows = {r["ขา"]: r for r in c["แถว"]}
    W, H, L, R, T, Bm = 760, 360, 64, 30, 60, 300
    xmax, lo, hi = 20000, -50, 120
    X = lambda s: L + s / xmax * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    a, b = c["a"] * 10, c["สี่κต่อล้าน"]                       # ต่อพัน: 6 · 0.4
    out = [text(16, 26, "กำไรสุทธิต่อไม้ขึ้นแล้วลง ยอดอยู่ครึ่งทางไปจุดคุ้มทุน", 13, INK, weight=700)]
    for g in (-40, 0, 40, 80):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for s in (0, 5000, 10000, 15000, 20000):
        out.append(text(X(s), Bm + 20, B.fmt(s), 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 40, "ขนาดต่อขา (ดอลลาร์)", 11, GREY, "middle"))
    lin = [(X(0), Y(0)), (X(xmax), Y(rows[20000]["ถ้าเส้นตรง"]))]
    out.append(f'<polyline points="{_poly(lin)}" fill="none" stroke="{GREY}" stroke-width="2" stroke-dasharray="6 5"/>')
    out.append(text(X(xmax) - 4, Y(rows[20000]["ถ้าเส้นตรง"]) - 8, f"ถ้าขยายเป็นเส้นตรง {B.fmt(int(rows[20000]['ถ้าเส้นตรง']))}", 11, GREY, "end", 700))
    pts = []
    for i in range(0, 41):
        k = i * 0.5
        pts.append((X(k * 1000), Y(a * k - b * k * k)))
    out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{C["blue"]}" stroke-width="2.6" stroke-linejoin="round"/>')
    marks = [(1000, rows[1000]["สุทธิ"], "ขาละ 1,000", C["blue"], 22, "start"),
             (c["จุดสูงสุด"], c["สุทธิสูงสุด"], "ยอด 7,500", C["purple"], 24, "middle"),
             (c["คุ้มทุน"], 0, "คุ้มทุน 15,000", C["amber"], -12, "middle"),
             (20000, int(rows[20000]["สุทธิ"]), "ขาละ 20,000", C["red"], 22, "end")]
    for s, v, lab, col, dy, anc in marks:
        out.append(f'<circle cx="{X(s):.1f}" cy="{Y(v):.1f}" r="5" fill="{col}"/>')
        out.append(text(X(s), Y(v) + dy, f"{lab}: {B.fmt(v)}", 11, col, anc, 700))
    alt = ("เส้นกำไรสุทธิต่อไม้ตามขนาดขา ขาละ 1,000 ได้ 5.6 ขึ้นไปสูงสุด 22.5 ที่ 7,500 ลดลงเป็นศูนย์ที่ 15,000 "
           "และติดลบ 40 ที่ 20,000 ขณะที่เส้นตรงจากขาละ 1,000 ขึ้นไปถึง 112")
    return wrap(W, H, alt, out, "กำไรก่อนต้นทุน 1% ของขาต่อไม้ · ค่าธรรมเนียม 0.05% ครึ่ง spread 0.05% ราคาเลื่อน 0.02% ต่อ 1,000 · สี่ fill ต่อไม้", "สอน")


@chart("sab2-funding-years")
def _funding_years(fig):
    d = fig["ch15"]["เสื่อมจริง"]
    W, H, L, R, T, Bm = 760, 340, 64, 30, 60, 280
    lo, hi = 0, 1.0
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "funding carry เฉลี่ยต่อเดือน (% ของมูลค่าที่ถือ)", 13, INK, weight=700)]
    for g in (0, 0.4, 0.8):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    years = [("ปี1", "ปีที่ 1 (ช่วงเลือก)"), ("ปี2", "ปีที่ 2 (ช่วงเลือก)"), ("ปี3", "ปีที่ 3 (ช่วงตรวจ)")]
    cols = {"BTC": C["blue"], "ETH": C["amber"]}
    gw = (W - L - R) / 3
    bw = 56
    for i, (k, lab) in enumerate(years):
        cx = L + gw * (i + 0.5)
        for j, coin in enumerate(("BTC", "ETH")):
            v = d[coin][k]["Mean"]
            x0 = cx + (j - 1) * (bw + 8) + 4
            out.append(f'<rect x="{x0:.1f}" y="{Y(v):.1f}" width="{bw}" height="{Y(0) - Y(v):.1f}" fill="{cols[coin]}" opacity="0.85"/>')
            out.append(text(x0 + bw / 2, Y(v) - 6, f"{coin} {B.fmt(v)}", 11, cols[coin], "middle", 700))
        out.append(text(cx, Bm + 20, lab, 11, GREY, "middle"))
    for coin, dy, anc in (("BTC", 14, "start"), ("ETH", -8, "start")):
        v = d[coin]["ช่วงเลือก"]["Mean"]
        out.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="{cols[coin]}" stroke-dasharray="5 4"/>')
        x = L + 4 if anc == "start" else W - R - 4
        out.append(text(x, Y(v) + dy, f"คาดจากช่วงเลือก {coin} {B.fmt(v)}", 10.5, cols[coin], anc, 700))
    alt = ("แท่ง funding carry ต่อเดือนสามปี BTC 0.31 0.82 0.61 ETH 0.35 0.8 0.22 เส้นประค่าคาดจากช่วงเลือก BTC 0.57 ETH 0.58 "
           "ปีที่ 3 ของ ETH ต่ำกว่าเส้นมาก")
    return wrap(W, H, alt, out, "Deribit BTC-PERPETUAL และ ETH-PERPETUAL · เดือนละ 30 วัน · ปีที่ 3 คือช่วงตรวจ", "จริง")


@chart("sab2-tracking-funnel")
def _funnel(fig):
    e = fig["ch15"]["ติดตามจริง"]["ETH"]
    rows = e["แถว"]
    W, H, L, R, T, Bm = 760, 360, 64, 30, 60, 300
    lo, hi = -1.5, 8
    n = len(rows)
    X = lambda m: L + (m - 1) / (n - 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "funding carry ETH ช่วงตรวจ: ผลสะสมเทียบที่คาดจากช่วงเลือก", 13, INK, weight=700)]
    for g in (0, 2, 4, 6):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for r in rows:
        out.append(text(X(r["เดือน"]), Bm + 20, f"{r['เดือน']}", 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 40, "เดือนของช่วงตรวจ", 11, GREY, "middle"))

    def line(key, col, dash, width=2.2):
        pts = [(X(r["เดือน"]), Y(r[key])) for r in rows]
        d_ = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<polyline points="{_poly(pts)}" fill="none" stroke="{col}" stroke-width="{width}"{d_} stroke-linejoin="round"/>'
    out.append(line("คาด", GREY, None))
    out.append(line("เตือน", C["amber"], "6 4"))
    out.append(line("ลงมือ", C["red"], "6 4"))
    out.append(line("สะสม", C["blue"], None, 2.8))
    last = rows[-1]
    out.append(text(X(n) - 4, Y(last["คาด"]) - 8, f"ที่คาด {B.fmt(last['คาด'])}", 11, GREY, "end", 700))
    out.append(text(X(n) - 4, Y(last["เตือน"]) - 8, f"เส้นเตือน {B.fmt(last['เตือน'])}", 11, C["amber"], "end", 700))
    out.append(text(X(n - 2), Y(rows[n - 3]["ลงมือ"]) + 20, f"เส้นลงมือ {B.fmt(last['ลงมือ'])}", 11, C["red"], "middle", 700))
    out.append(text(X(n) - 4, Y(last["สะสม"]) - 8, f"ผลจริง {B.fmt(last['สะสม'])}", 11, C["blue"], "end", 700))
    w = rows[e["เตือนเดือน"] - 1]
    out.append(f'<circle cx="{X(w["เดือน"]):.1f}" cy="{Y(w["สะสม"]):.1f}" r="6.5" fill="none" stroke="{C["purple"]}" stroke-width="2.4"/>')
    out.append(text(X(w["เดือน"]), Y(w["สะสม"]) + 22, f"เดือนที่ {w['เดือน']} หลุดเส้นเตือน", 11, C["purple"], "middle", 700))
    alt = ("ผลสะสมของ funding carry ETH ช่วงตรวจ เริ่ม 1.64 แล้วแบนราบราว 2 ขณะที่ที่คาดขึ้นถึง 6.96 "
           "ผลจริงหลุดใต้เส้นเตือนเดือนที่ 6 และจบที่ 2.62 เหนือเส้นลงมือ 1.98")
    return wrap(W, H, alt, out, "ค่าคาด Mean 0.58 และ SD 0.72 ต่อเดือนจากช่วงเลือก 24 เดือน · เส้นเตือน 1 SD × √n · เส้นลงมือ 2 SD × √n", "จริง")
