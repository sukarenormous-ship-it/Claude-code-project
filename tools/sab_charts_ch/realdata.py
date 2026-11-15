"""ภาคผนวก K — กราฟข้อมูลจริง (ปลั๊กอินของ tools/sab_charts.py · ตัวเลขทุกตัวอ่านจาก fig["realdata"])

sab-real-x       : X = BTC − 19 × ETH รายวัน 2025-01-01..2026-11-14 · ไม้บรรทัดทั้งปีของช่วงเลือก (ม่วง) · ไม้บรรทัด 90 วัน (ส้ม) · จุดสัญญาณ
sab-real-equity  : มูลค่าบัญชีรายวันในช่วงทดสอบ · การ์ดที่ตรึงไว้ (ไม่มีไม้ เส้นแบน) กับการดูครั้งที่สอง (ไม้บรรทัด 90 วัน)
"""

from sab_charts import chart, wrap, text, C, B

INK, MUTED = C["ink"], C["muted"]
XCOL, FULL, W90 = C["blue"], C["purple"], C["amber"]


def _poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


@chart("sab-real-x")
def _real_x(fig):
    r = fig["realdata"]
    g, ru, ex, h = r["ชุดกราฟ"], r["ไม้บรรทัด"], r["สำรวจ90"], r["h"]["เลือก"]
    xs = g["X"]
    n = len(xs)
    W, H, L, R, T, Bm = 760, 400, 70, 24, 70, 340
    ticks = g["แกนX"]
    lo, hi = ticks[0], ticks[-1]
    X = lambda i: L + i / (n - 1) * (W - L - R)          # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)    # noqa: E731
    t0, w0 = g["iทดสอบเริ่ม"], g["iหน้าต่างเริ่ม"]
    p = [text(L, 22, f"X = BTC − {h} × ETH รายวัน: ช่วงทดสอบไม่เคยแตะเส้น ±2 SD ของทั้งปี", 13, INK, weight=700)]
    p.append(f'<rect x="{L}" y="{T}" width="{X(t0) - L:.1f}" height="{Bm - T}" fill="#f5f3ff"/>')
    p.append(text(L + 6, T + 14, "ช่วงเลือก (วัดไม้บรรทัด)", 11, FULL, weight=700))
    p.append(text(X(t0) + 6, T + 14, "ช่วงทดสอบ (ตรึงไม้บรรทัด)", 11, MUTED, weight=700))
    for t in ticks:
        p.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{W - R}" y2="{Y(t):.1f}" stroke="{C["grid"]}" stroke-width="1"/>')
        p.append(text(L - 8, Y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
    for m in g["เดือน"]:
        p.append(text(X(m["i"]), Bm + 16, m["ป้าย"], 10.5, C["grey"], "middle"))
    # ไม้บรรทัดทั้งปี (ม่วง): Mean เส้นทึบ · ±2 SD เส้นประ ลากทั้งกราฟ
    for v, dash in ((ru["Mean"], None), (ru["เส้นบน"], "6 4"), (ru["เส้นล่าง"], "6 4")):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="{FULL}" stroke-width="1.6"{da}/>')
    p.append(text(W - R - 4, Y(ru["เส้นบน"]) - 6, f"+2 SD {B.fmt(ru['เส้นบน'])}", 11, FULL, "end", 700))
    p.append(text(W - R - 4, Y(ru["Mean"]) - 6, f"Mean {B.fmt(ru['Mean'])}", 11, FULL, "end", 700))
    p.append(text(W - R - 4, Y(ru["เส้นล่าง"]) + 15, f"−2 SD {B.fmt(ru['เส้นล่าง'])}", 11, FULL, "end", 700))
    # ไม้บรรทัด 90 วัน (ส้ม): ±2 SD จากต้นหน้าต่างถึงท้ายกราฟ
    for v in (ex["เส้นบน"], ex["เส้นล่าง"]):
        p.append(f'<line x1="{X(w0):.1f}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="{W90}" '
                 f'stroke-width="1.6" stroke-dasharray="3 3"/>')
    p.append(f'<polyline points="{_poly([(X(i), Y(v)) for i, v in enumerate(xs)])}" fill="none" stroke="{XCOL}" '
             f'stroke-width="2" stroke-linejoin="round"/>')
    for k, s in enumerate(ex["สัญญาณ"], 1):
        i = _idx(fig, s["วัน"])
        p.append(f'<circle cx="{X(i):.1f}" cy="{Y(s["X"]):.1f}" r="5" fill="{W90}" stroke="#fff" stroke-width="1.5"/>')
        p.append(text(X(i) + (-8 if k == 1 else 8), Y(s["X"]) + 20, f"สัญญาณไม้ {k}", 11, W90, "end" if k == 1 else "start", 700))
    lx = L
    for name, col, dash in (("X ของชุด", XCOL, None), ("ไม้บรรทัดทั้งปี", FULL, "6 4"), ("ไม้บรรทัด 90 วัน (ดูครั้งที่สอง)", W90, "3 3")):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        p.append(f'<line x1="{lx}" y1="44" x2="{lx + 22}" y2="44" stroke="{col}" stroke-width="2.4"{da}/>')
        p.append(text(lx + 28, 48, name, 11.5, MUTED))
        lx += 44 + 9 * len(name)
    alt = (f"กราฟเส้น X ของชุด BTC หนึ่งเหรียญคู่กับ ETH {h} เหรียญ รายวันจาก {r['แหล่ง']['แถว']} วัน "
           f"ไม้บรรทัดจากช่วงเลือกมี Mean {B.fmt(ru['Mean'])} และกรอบ ±2 SD {B.fmt(ru['เส้นล่าง'])} ถึง {B.fmt(ru['เส้นบน'])} "
           f"ตลอดช่วงทดสอบ X อยู่ในกรอบนี้ทุกวัน ส่วนไม้บรรทัด 90 วันแคบกว่าและให้สัญญาณ {ex['จำนวนสัญญาณ']} ครั้ง")
    cap = f"ราคาปิดรายวัน Binance spot (UTC) ดึงเมื่อ {r['แหล่ง']['ดึงเมื่อ'][:10]} · หน่วยดอลลาร์ (USDT) ต่อหนึ่งชุด"
    return wrap(W, H, alt, p, cap, "จริง")


def _idx(fig, day):
    """ลำดับวันในชุด X จากวันที่ (วันแรก = 2025-01-01 · ทุกวันมีครบ)"""
    import datetime as _dt
    return (_dt.date.fromisoformat(day) - _dt.date.fromisoformat(fig["realdata"]["แหล่ง"]["แถวแรก"]["วัน"])).days


@chart("sab-real-equity")
def _real_equity(fig):
    r = fig["realdata"]
    g, ex = r["ชุดกราฟ"], r["สำรวจ90"]
    t0 = g["iทดสอบเริ่ม"]
    eq90, eq = g["equity90"], g["equity"]
    n = len(eq90)
    W, H, L, R, T, Bm = 760, 340, 70, 24, 70, 290
    ticks = g["แกนequity"]
    lo, hi = ticks[0], ticks[-1]
    X = lambda i: L + i / (n - 1) * (W - L - R)          # noqa: E731
    Y = lambda v: Bm - (v - lo) / (hi - lo) * (Bm - T)    # noqa: E731
    p = [text(L, 22, "มูลค่าบัญชีรายวัน ทุน 1,000: ไม่มีไม้เลย กับสองไม้ที่เสียทั้งคู่", 13, INK, weight=700)]
    for t in ticks:
        p.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{W - R}" y2="{Y(t):.1f}" stroke="{C["axis"] if t == 1000 else C["grid"]}" stroke-width="1"/>')
        p.append(text(L - 8, Y(t) + 4, B.fmt(t), 10.5, C["grey"], "end"))
    for m in g["เดือน"]:
        if m["i"] >= t0:
            p.append(text(X(m["i"] - t0), Bm + 16, m["ป้าย"], 10.5, C["grey"], "middle"))
    for ser, col, wd in ((eq, C["grey"], 2.4), (eq90, W90, 2.2)):
        p.append(f'<polyline points="{_poly([(X(i), Y(v)) for i, v in enumerate(ser)])}" fill="none" stroke="{col}" '
                 f'stroke-width="{wd}" stroke-linejoin="round"/>')
    for k, t in enumerate(ex["ไม้"], 1):
        i = _idx(fig, t["วันออก"]) - t0
        p.append(f'<circle cx="{X(i):.1f}" cy="{Y(eq90[i]):.1f}" r="4.5" fill="{C["purple"]}"/>')
        p.append(text(X(i) + 8, Y(eq90[i]) + 18 + (k - 1) * 4, f"ไม้ {k} ออก ({t['เหตุ']}) {B.fmt(t['สุทธิ'])}", 11, C["purple"], "start", 700))
    i_lo = _idx(fig, ex["ddถึง"]) - t0
    p.append(text(X(i_lo) - 6, Y(ex["ddก้น"]) + 4, f"ก้น {B.fmt(ex['ddก้น'])}", 10.5, MUTED, "end"))
    p.append(text(W - R, Y(ex["equityจบ"]) - 8, f"จบ {B.fmt(ex['equityจบ'])}", 11, W90, "end", 700))
    lx = L
    for name, col in (("การ์ดที่ตรึงไว้ (ไม่มีไม้)", C["grey"]), ("ไม้บรรทัด 90 วัน (ดูครั้งที่สอง)", W90)):
        p.append(f'<line x1="{lx}" y1="44" x2="{lx + 22}" y2="44" stroke="{col}" stroke-width="2.4"/>')
        p.append(text(lx + 28, 48, name, 11.5, MUTED))
        lx += 44 + 9 * len(name)
    alt = (f"กราฟเส้นมูลค่าบัญชีรายวันตลอดช่วงทดสอบ {r['แหล่ง']['วันช่วงทดสอบ']} วัน เส้นเทาคือการ์ดที่ตรึงไว้ซึ่งไม่มีไม้เลย "
           f"จึงแบนที่ 1,000 เส้นส้มคือการดูครั้งที่สองด้วยไม้บรรทัด 90 วัน มีสองไม้ จบที่ {B.fmt(ex['equityจบ'])} "
           f"ลึกสุดจากยอด {B.fmt(ex['drawdown'])}")
    cap = "มูลค่าบัญชี = เงินสด + มูลค่าขาที่ถือ − ภาระซื้อคืน ตีราคาที่ราคาปิดทุกวัน หักค่าธรรมเนียมแล้ว"
    return wrap(W, H, alt, p, cap, "จริง")
