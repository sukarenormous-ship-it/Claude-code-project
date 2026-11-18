"""บท 13 เล่ม 2 — เครื่อง backtest ของตัวเอง · สเปกกราฟของบท (อ่านตัวเลขจาก docs/sab2-figures.json เท่านั้น)

sab2-hand-loop    : X ของคู่ A–B สิบวัน · เส้นเข้า 2 กับเส้นออก 0.5 · จุดสัญญาณ (วันที่ 3 · 7) กับจุดได้ราคา (วันที่ 4 · 8)
sab2-ton-fixes    : ผลของสเปรดชีตต้นหลังแก้ทีละจุด · โลกตัวอย่าง เทียบมัธยฐาน 30 โลก (โลกที่ไม่มีเชือกให้เก็บ)
sab2-survivors    : 🎲 100 เหรียญเดินสุ่ม · ราคาปลาย ÷ ราคาเริ่ม เป็นจุดซ้อน · รอด (ทึบ) / ถูกถอด (กลวง) · มัธยฐานสองแบบ
sab2-real-equity  : Equity รายสัปดาห์บน BTC–ETH ช่วงตรวจ · เครื่องซื่อ เทียบชีตแบบต้น (ค่าจากทั้งสองช่วง + ได้ราคาวันสัญญาณ)
"""

from sab_charts import B, C, chart, grouped_bars, text, wrap

INK, MUTED, GREY = C["ink"], C["muted"], C["grey"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


@chart("sab2-hand-loop")
def _hand_loop(fig):
    c = fig["ch13"]["v2"]["มือ"]
    days = c["วัน"]
    xs = [d["X"] for d in days]
    W, H, L, R, T, Bm = 760, 340, 64, 30, 60, 290
    lo, hi = -1.5, 2.6
    X = lambda i: L + i / (len(days) - 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "สัญญาณเกิดหลังราคาปิด ราคาที่ได้คือราคาปิดวันถัดไป", 13, INK, weight=700)]
    for g in (-1, 0, 1, 2):
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 0 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    enter, leave = 2, 0.5
    out.append(f'<line x1="{L}" y1="{Y(enter):.1f}" x2="{W - R}" y2="{Y(enter):.1f}" stroke="{C["red"]}" stroke-dasharray="5 4"/>')
    out.append(text(W - R, Y(enter) - 6, "เส้นเข้า Z 2", 11, C["red"], "end", 700))
    out.append(f'<line x1="{L}" y1="{Y(leave):.1f}" x2="{W - R}" y2="{Y(leave):.1f}" stroke="{C["green"]}" stroke-dasharray="5 4"/>')
    out.append(text(W - R, Y(leave) + 15, "เส้นออก Z 0.5", 11, C["green"], "end", 700))
    for i, d in enumerate(days):
        out.append(text(X(i), Bm + 20, f"วัน {d['วัน']}", 10.5, GREY, "middle"))
    pts = [(X(i), Y(v)) for i, v in enumerate(xs)]
    out.append(f'<polyline points="{_poly(pts)}" fill="none" stroke="{C["blue"]}" stroke-width="2.4" stroke-linejoin="round"/>')
    for x, y in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{C["blue"]}"/>')
    marks = [(c["สัญญาณเข้า"]["วัน"], "สัญญาณ short", C["purple"], -12),
             (c["fillเข้า"]["วัน"], "ได้ราคา", C["amber"], 22),
             (c["สัญญาณออก"]["วัน"], "สัญญาณปิด", C["purple"], 22),
             (c["fillออก"]["วัน"], "ได้ราคา", C["amber"], -12)]
    for day, lab, col, dy in marks:
        i = day - 1
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(xs[i]):.1f}" r="6.5" fill="none" stroke="{col}" stroke-width="2.4"/>')
        out.append(text(X(i), Y(xs[i]) + dy, f"{lab} {B.fmt(xs[i])}", 11, col, "middle", 700))
    alt = ("เส้น X ของคู่ A–B สิบวัน ขึ้นจาก 0.6 ถึง 2.3 ในวันที่ 3 ซึ่งเป็นวันสัญญาณ แล้วได้ราคาวันที่ 4 ที่ 2.0 "
           "ลงถึง 0.4 ในวันที่ 7 ซึ่งเป็นสัญญาณปิด และได้ราคาวันที่ 8 ที่ 0.7")
    return wrap(W, H, alt, out, "คู่ A–B ของเล่ม 1 · ไม้บรรทัด Mean 0 SD 1 จึงอ่าน X เป็น Z ได้ตรง · short X 10 ชุด", "สอน")


@chart("sab2-ton-fixes")
def _ton_fixes(fig):
    t = fig["ch13"]["v2"]["ต้น"]
    keys = ["ต้นเดิม", "แก้fill", "แก้ไม้บรรทัด", "แก้h"]
    cats = ["ชีตเดิมของต้น", "แก้ราคาที่ได้", "แก้ไม้บรรทัด", "แก้ h (ซื่อครบ)"]
    one = [t["ผล"][k]["ผล"] for k in keys]
    med = [t["สามสิบโลก"][k]["มัธยฐาน"] for k in keys]
    parts = grouped_bars(cats, [("โลกตัวอย่างในชีตของต้น", one, C["blue"]), ("มัธยฐานของ 30 โลกแบบเดียวกัน", med, C["purple"])],
                         "ผลทั้งปีหลังแก้ Look-ahead ทีละจุด (ทุนเริ่ม 1,000)")
    alt = ("แท่งผลทั้งปีสี่แบบ ชีตเดิมของต้นบวกมาก แก้ราคาที่ได้แล้วเหลือบวกเล็กน้อย แก้ไม้บรรทัดและ h แล้วติดลบราวค่าธรรมเนียม "
           "ทั้งในโลกตัวอย่างและในมัธยฐานของ 30 โลก")
    return wrap(760, 330, alt, parts, "โลกที่ไม่มีเชือกให้เก็บ (เดินสุ่มช้า + แรงสะบัดที่หายในวันเดียว) · 5 ชุด · ค่าธรรมเนียม 0.05% ต่อ fill",
                "จำลอง")


@chart("sab2-real-equity")
def _real_equity(fig):
    r = fig["ch13"]["v2"]["จริง"]
    ln = r["เส้นมูลค่า"]
    a, b, days = ln["ซื่อ"], ln["ต้นเดิม"], ln["วัน"]
    ticks = r["แกนกราฟ"]
    W, H, L, R, T, Bm = 760, 340, 70, 30, 66, 290
    lo, hi = ticks[0] - 40, ticks[-1] + 60      # เผื่อใต้ 600 ให้ป้ายจุดต่ำสุดไม่ชนป้ายวันที่
    X = lambda i: L + i / (len(a) - 1) * (W - L - R)  # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)  # noqa: E731
    out = [text(16, 26, "Equity รายสัปดาห์ของคู่ BTC–ETH ในช่วงตรวจ (ทุนเริ่ม 1,000)", 13, INK, weight=700)]
    for g in ticks:
        out.append(f'<line x1="{L}" y1="{Y(g):.1f}" x2="{W - R}" y2="{Y(g):.1f}" stroke="{C["axis"] if g == 1000 else C["grid"]}"/>')
        out.append(text(L - 8, Y(g) + 4, B.fmt(g), 11, GREY, "end"))
    for i in r["ป้ายวันกราฟ"]:
        out.append(text(X(i), Bm + 20, days[i], 10.5, GREY, "middle"))
    for s, col in ((b, C["amber"]), (a, C["blue"])):
        out.append(f'<polyline points="{_poly([(X(i), Y(v)) for i, v in enumerate(s)])}" fill="none" stroke="{col}" '
                   f'stroke-width="2.4" stroke-linejoin="round"/>')
    lx = L
    for name, col in (("เครื่องซื่อ (ค่าจากช่วงเลือก · ได้ราคาวันถัดไป)", C["blue"]), ("ชีตแบบต้น (โกงครบสามจุด)", C["amber"])):
        out.append(f'<rect x="{lx}" y="{T - 22}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(text(lx + 16, T - 12, name, 11.5, MUTED))
        lx += 34 + 7.2 * len(name)
    i_min = a.index(min(a))
    out.append(f'<circle cx="{X(i_min):.1f}" cy="{Y(a[i_min]):.1f}" r="5" fill="{C["purple"]}"/>')
    out.append(text(X(i_min) + 8, Y(a[i_min]) + 16, f"ต่ำสุดรายสัปดาห์ {B.fmt(a[i_min])}", 11, C["purple"], "start", 700))
    out.append(text(W - R, Y(a[-1]) + 16, f"จบ {B.fmt(a[-1])}", 11, C["blue"], "end", 700))
    out.append(text(W - R, Y(b[-1]) - 8, f"จบ {B.fmt(b[-1])}", 11, C["amber"], "end", 700))
    alt = ("เส้น Equity สองเส้นตลอดช่วงตรวจ เส้นน้ำเงินของเครื่องซื่อลงไปต่ำกว่า 650 กลางปีแล้วกลับขึ้นมาจบต่ำกว่า 1,000 "
           "เส้นส้มของชีตแบบต้นแกว่งน้อยกว่าและจบเหนือ 1,000")
    return wrap(W, H, alt, out, "ราคาปิดรายวัน Binance spot (UTC) ช่วงตรวจ 2024-11-15 ถึง 2025-11-14 · 0.01 BTC คู่ ETH 0.24 · "
                "จุดรายสัปดาห์ (ทุก 7 วัน + วันสุดท้าย)", "จริง")


@chart("sab2-survivors")
def _survivors(fig):
    s = fig["ch13"]["v2"]["ผู้รอด"]
    g = s["กราฟ"]
    ratios, alive = g["ราคาปลาย"], g["รอด"]
    W, H, L, R, T, Bm = 760, 360, 40, 30, 96, 316
    step, top = 0.25, 6.75                       # ช่องละ 0.25 เท่าของราคาเริ่ม
    X = lambda v: L + v / top * (W - L - R)  # noqa: E731
    dy = 11.5
    out = [text(16, 24, f"{s['เหรียญ']} เหรียญที่ไม่มีใครเก่งกว่าใคร: ราคาปลาย ÷ ราคาเริ่ม (จุดละหนึ่งเหรียญ)", 13.5, INK, weight=700)]
    out.append(f'<line x1="{L}" y1="{Bm}" x2="{W - R}" y2="{Bm}" stroke="{C["axis"]}" stroke-width="1.4"/>')
    for k in range(0, 7):
        out.append(f'<line x1="{X(k):.1f}" y1="{Bm}" x2="{X(k):.1f}" y2="{Bm + 5}" stroke="{C["axis"]}"/>')
        out.append(text(X(k), Bm + 18, f"{k} เท่า", 10.5, GREY, "middle"))
    out.append(text((L + W - R) / 2, Bm + 36, "ราคาปลาย ÷ ราคาเริ่ม (1 เท่า = ราคาเท่าเดิม)", 11, MUTED, "middle", 700))
    for v, col, lab, yy, anc in ((s["มัธยฐานทุกเหรียญ"], INK, f"มัธยฐานทุก {s['เหรียญ']} เหรียญ {B.fmt(s['มัธยฐานทุกเหรียญ'])}", T - 20, "start"),
                                 (s["มัธยฐานเฉพาะที่รอด"], C["blue"], f"มัธยฐานเฉพาะ {s['รอด']} เหรียญที่รอด {B.fmt(s['มัธยฐานเฉพาะที่รอด'])}", T - 2, "start")):
        out.append(f'<line x1="{X(v):.1f}" y1="{yy + 6}" x2="{X(v):.1f}" y2="{Bm}" stroke="{col}" stroke-dasharray="5 4" stroke-width="1.8"/>')
        out.append(text(X(v) + (-6 if anc == "end" else 6), yy, lab, 11, col, anc, 700))
    bins = {}
    for r, a in sorted(zip(ratios, alive), key=lambda t: (not t[1], t[0])):   # ที่รอดซ้อนล่าง ที่ถูกถอดซ้อนบน
        bins.setdefault(int(r / step), []).append(a)
    for b, col in bins.items():
        cx = X((b + 0.5) * step)
        for k, a in enumerate(col):
            cy = Bm - 7 - k * dy
            if a:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.6" fill="{C["blue"]}"/>')
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#fff" stroke="{C["red"]}" stroke-width="1.8"/>')
    lx = L
    for name, filled in ((f"รอดอยู่ในรายชื่อ ณ วันจบ ({s['รอด']} เหรียญ)", True),
                         (f"ถูกถอด เพราะราคาเคยลงต่ำกว่า {s['เกณฑ์ถอดเปอร์เซ็นต์']}% ของราคาเริ่ม ({s['ถูกถอด']} เหรียญ)", False)):
        if filled:
            out.append(f'<circle cx="{lx + 5}" cy="48" r="4.6" fill="{C["blue"]}"/>')
        else:
            out.append(f'<circle cx="{lx + 5}" cy="48" r="4" fill="#fff" stroke="{C["red"]}" stroke-width="1.8"/>')
        out.append(text(lx + 16, 52, name, 11.5, MUTED))
        lx += 40 + 7.0 * len(name)
    alt = (f"จุดของ {s['เหรียญ']} เหรียญเรียงตามราคาปลายเทียบราคาเริ่ม จุดกลวงสีแดงของเหรียญที่ถูกถอดกองอยู่ทางซ้ายใต้ 1 เท่าเกือบทั้งหมด "
           f"เมื่อตัดทิ้ง มัธยฐานขยับจาก {B.fmt(s['มัธยฐานทุกเหรียญ'])} เป็น {B.fmt(s['มัธยฐานเฉพาะที่รอด'])}")
    cap = (f"{s['เหรียญ']} เหรียญจำลอง เดินสุ่มราว 3% ต่อวัน {B.fmt(s['วัน'])} วัน · เริ่มราคาเดียวกัน · "
           f"ช่องละ {B.fmt(step)} เท่า · ถูกถอดตัดสินจากราคาระหว่างทาง ไม่ใช่ราคาปลาย")
    return wrap(W, H, alt, out, cap, "จำลอง")
